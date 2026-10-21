"""
LangGraph Workflow Orchestrator for SubscriptIQ Text-to-SQL Analytics.
Constructs, wires, and compiles the multi-stage StateGraph with conditional retry loops.
"""
import time
from typing import Literal, Dict, Any
from langgraph.graph import StateGraph, START, END

from app.ai_services.state import SQLAgentState
from app.ai_services.nodes import (
    classifier_node,
    schema_linker_node,
    qdrant_retriever_node,
    sql_generator_node,
    validator_node,
    executor_node,
    formatter_node
)

def router_after_classifier(state: SQLAgentState) -> Literal["schema_linker", "formatter"]:
    """Conditional Edge: Route malicious or unsupported queries directly to formatter to block."""
    if not state.get("is_supported", True):
        return "formatter"
    return "schema_linker"

def router_after_validator(state: SQLAgentState) -> Literal["sql_generator", "executor"]:
    """
    Conditional Edge: Self-Healing Retry Loop.
    If AST validation failed and retry count is under 1, loop back to generator with feedback.
    Otherwise, proceed to database executor.
    """
    if not state.get("is_valid", False) and state.get("retry_count", 0) <= 1:
        return "sql_generator"
    return "executor"

def router_after_executor(state: SQLAgentState) -> Literal["sql_generator", "formatter"]:
    """
    Conditional Edge: Self-Healing SQL Execution Retry Loop (Assignment Bonus Requirement).
    If database execution against PostgreSQL produced a runtime or syntax error and
    retry count is under 1, loop back to sql_generator with the database error feedback.
    Otherwise, proceed to result formatter.
    """
    if state.get("error") and state.get("retry_count", 0) <= 1:
        return "sql_generator"
    return "formatter"

def build_sql_agent_graph():
    """Builds and compiles the LangGraph StateGraph workflow."""
    builder = StateGraph(SQLAgentState)

    # 1. Register Nodes
    builder.add_node("classifier", classifier_node)
    builder.add_node("schema_linker", schema_linker_node)
    builder.add_node("qdrant_retriever", qdrant_retriever_node)
    builder.add_node("sql_generator", sql_generator_node)
    builder.add_node("validator", validator_node)
    builder.add_node("executor", executor_node)
    builder.add_node("formatter", formatter_node)

    # 2. Wire Edges
    builder.add_edge(START, "classifier")
    
    # Branching after classifier
    builder.add_conditional_edges(
        "classifier",
        router_after_classifier,
        {
            "schema_linker": "schema_linker",
            "formatter": "formatter"
        }
    )

    builder.add_edge("schema_linker", "qdrant_retriever")
    builder.add_edge("qdrant_retriever", "sql_generator")
    builder.add_edge("sql_generator", "validator")

    # Branching after validator (Self-Healing Syntax & Guardrails Retry Loop)
    builder.add_conditional_edges(
        "validator",
        router_after_validator,
        {
            "sql_generator": "sql_generator",
            "executor": "executor"
        }
    )

    # Branching after executor (Self-Healing Runtime Execution Retry Loop)
    builder.add_conditional_edges(
        "executor",
        router_after_executor,
        {
            "sql_generator": "sql_generator",
            "formatter": "formatter"
        }
    )
    builder.add_edge("formatter", END)

    # 3. Compile Graph
    return builder.compile()

# Singleton compiled LangGraph agent
sql_agent_graph = build_sql_agent_graph()

async def run_langgraph_pipeline(
    query: str,
    selected_model: str,
    user_role: str = "user",
    user_email: str = "alex.rivera@subscriptiq.ai",
    temperature: float = 0.1
) -> Dict[str, Any]:
    """
    Executes the compiled LangGraph pipeline asynchronously for a given natural language query.
    """
    start_time = time.perf_counter()

    initial_state: SQLAgentState = {
        "query": query,
        "selected_model": selected_model,
        "user_role": user_role,
        "user_email": user_email,
        "temperature": temperature,
        "retry_count": 0,
        "is_supported": True,
        "messages": []
    }

    final_state = await sql_agent_graph.ainvoke(initial_state)
    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

    return {
        "success": final_state.get("success", False),
        "query": query,
        "query_type": final_state.get("query_type", "SELECT_SIMPLE"),
        "model_used": selected_model,
        "sql": final_state.get("generated_sql"),
        "explanation": final_state.get("explanation"),
        "nl_summary": final_state.get("nl_summary"),
        "columns": final_state.get("columns", []),
        "rows": final_state.get("rows", []),
        "row_count": final_state.get("row_count", 0),
        "latency_ms": elapsed_ms,
        "chart": final_state.get("chart"),
        "pipeline_steps": {
            "classifier": {"query_type": final_state.get("query_type"), "is_supported": final_state.get("is_supported")},
            "schema_linker": {"resolved_tables": final_state.get("resolved_tables", [])},
            "retriever": {"examples_count": len(final_state.get("few_shot_examples", []))},
            "validator": {"valid": final_state.get("is_valid", True), "errors": final_state.get("validation_errors", [])}
        },
        "error": final_state.get("error")
    }
