"""
LangGraph Nodes for the SubscriptIQ Text-to-SQL Workflow.
Implements the 7 core stages as modular LangGraph nodes.
"""
import re
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.ai_services.state import SQLAgentState
from app.ai_services.models import get_langchain_model
from app.ai_services.mcp_tools import mcp_postgres_query
from app.engine.classifier import classify_query
from app.engine.schema_linker import link_schema
from app.engine.retriever import retrieve_examples
from app.engine.validator import validate_and_sanitize_sql
from app.engine.formatter import format_result
from app.engine.generator import clean_generated_sql, synthesize_fallback_sql

async def classifier_node(state: SQLAgentState) -> Dict[str, Any]:
    """Stage 1: Intent Classification and Security Guardrail Routing."""
    query = state["query"]
    classification = classify_query(query)
    
    return {
        "query_type": classification["query_type"],
        "is_supported": classification["is_supported"],
        "rejection_reason": classification.get("reason"),
        "retry_count": state.get("retry_count", 0)
    }

async def schema_linker_node(state: SQLAgentState) -> Dict[str, Any]:
    """Stage 2: Schema Linking, Synonym Resolution, and PII Masking."""
    if not state.get("is_supported", True) or state.get("query_type") == "CONVERSATIONAL":
        return {}

    query = state["query"]
    classification = {
        "query_type": state["query_type"],
        "is_supported": state["is_supported"]
    }
    
    linker_out = link_schema(query, classification)
    return {
        "resolved_tables": linker_out["resolved_tables"],
        "schema_prompt": linker_out["schema_context_prompt"]
    }

async def qdrant_retriever_node(state: SQLAgentState) -> Dict[str, Any]:
    """Stage 3: Vector Semantic Retrieval of Curated SQL Few-Shots from Qdrant."""
    if not state.get("is_supported", True) or state.get("query_type") == "CONVERSATIONAL":
        return {}

    query = state["query"]
    query_type = state["query_type"]
    examples = retrieve_examples(query, query_type=query_type, limit=4)
    return {
        "few_shot_examples": examples
    }

async def sql_generator_node(state: SQLAgentState) -> Dict[str, Any]:
    """Stage 4: LangChain Model Generation (ChatGroq / ChatGoogleGenerativeAI)."""
    if not state.get("is_supported", True):
        return {}

    query = state["query"]
    query_type = state.get("query_type", "SELECT_SIMPLE")
    selected_model = state.get("selected_model", "openai/gpt-oss-120b")
    temperature = state.get("temperature", 0.1)

    # Handle Conversational / Capabilities / Greetings / Out-of-Scope without running database queries
    if query_type == "CONVERSATIONAL":
        lower_q = query.lower().strip()
        is_greeting = bool(re.search(r"^(hi|hello|hey|greetings|good\s+(morning|afternoon|evening)|howdy|sup|how\s+are\s+you|thanks|thank\s+you|bye|goodbye)\b", lower_q))
        is_capability = bool(re.search(r"\b(what\s+can\s+you\s+do|how\s+can\s+you\s+help|what\s+do\s+you\s+do|who\s+are\s+you|what\s+is\s+this|help\s*me|help$|capabilities|sample\s+queries|sample\s+questions)\b", lower_q))

        if is_greeting:
            system_prompt = (
                "You are SubscriptIQ AI, a professional enterprise assistant specialized in SaaS subscription analytics and software license optimization.\n"
                "The user is sending a greeting or polite conversational pleasantry.\n"
                "Respond warmly, naturally, and concisely in 1 to 2 sentences (e.g. 'Hello! How can I assist you with your organization\'s software subscriptions, spend analysis, or license tracking today?').\n"
                "Do NOT output a long repetitive list of features, bullet points, or sample queries, as the user already has the welcome guide in the chat interface. Do NOT output SQL."
            )
            fallback_text = "👋 Hello! How can I assist you with your organization's software subscriptions, spend analytics, or license optimizations today?"
        elif is_capability:
            system_prompt = (
                "You are SubscriptIQ AI, an enterprise assistant specialized in SaaS subscription and spend intelligence.\n"
                "The user is asking about your capabilities or how you can help.\n"
                "Provide a brief, well-structured summary of what you can analyze (subscription spending, upcoming contract renewals, dormant license seats, and vendor invoices) with 2-3 sample questions.\n"
                "Keep it concise, clear, and professional. Do NOT output SQL."
            )
            fallback_text = (
                "👋 **I am SubscriptIQ AI**, your assistant for SaaS subscription and spend intelligence.\n\n"
                "I can help you analyze:\n"
                "- 💳 **Subscription Spend**: Monthly & annual costs across departments and vendors.\n"
                "- 📅 **Contract Renewals**: Upcoming renewals in the next 14, 30, or 60 days.\n"
                "- 👥 **License Optimization**: Dormant and unassigned licenses to reclaim waste.\n"
                "- 📄 **Invoices & Billing**: Payment statuses, overdue bills, and invoice breakdowns.\n\n"
                "Try asking questions like:\n"
                "- *'Show top 5 subscriptions by monthly spend'*\n"
                "- *'Which subscriptions renew in the next 30 days?'*\n"
                "- *'Find all dormant license seats'*"
            )
        else:
            # Out-of-scope query (e.g. weather, jokes, recipes, general coding, sports, world trivia, etc.)
            system_prompt = (
                "You are SubscriptIQ AI, an enterprise analytics assistant specialized EXCLUSIVELY in corporate SaaS subscription management, "
                "software licenses, IT expenditure, vendor contracts, and license allocation analytics.\n"
                "The user's query is OUT OF SCOPE for SubscriptIQ.\n"
                "Politely decline to answer their specific question. Specifically acknowledge what they asked about (e.g. jokes, weather, general programming, geography, recipes, etc.), "
                "explain that SubscriptIQ is dedicated solely to corporate software subscriptions, SaaS spend, and license tracking, "
                "and invite them to ask about their organization's software subscriptions, renewals, licenses, or billing invoices.\n"
                "Keep your response polite, professional, concise (2 to 3 sentences), and uniquely tailored to what was asked.\n"
                "Do NOT answer the out-of-scope question itself. Do NOT output SQL code blocks."
            )
            clean_q = query.strip().rstrip("?").rstrip(".")
            clean_display = clean_q[:55] + ("..." if len(clean_q) > 55 else "")
            fallback_text = (
                f"I apologize, but answering questions regarding '{clean_display}' is outside my scope. "
                "As SubscriptIQ AI, I specialize strictly in corporate SaaS subscription management, software spend analysis, vendor contracts, and license optimization. "
                "Please feel free to ask about your company's software tools, upcoming renewals, or billing invoices!"
            )

        llm = get_langchain_model(selected_model, temperature=temperature)
        if llm is not None:
            conv_messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=query)
            ]
            try:
                ai_msg = await llm.ainvoke(conv_messages)
                return {
                    "generated_sql": None,
                    "explanation": ai_msg.content.strip(),
                    "messages": conv_messages + [AIMessage(content=ai_msg.content.strip())]
                }
            except Exception as e:
                print(f"[LangChain Conversational Notice] {e}")

        return {
            "generated_sql": None,
            "explanation": fallback_text,
            "messages": [HumanMessage(content=query), AIMessage(content=fallback_text)]
        }

    resolved_tables = state.get("resolved_tables", [])
    schema_prompt = state.get("schema_prompt", "")
    few_shot_examples = state.get("few_shot_examples", [])
    retry_error = state.get("retry_error")

    # Format Few-Shot examples
    few_shot_text = ""
    for i, ex in enumerate(few_shot_examples, 1):
        few_shot_text += f"\nExample {i}:\nQuestion: {ex['question']}\nSQL: {ex['sql']}\n"

    system_prompt = f"""You are SubscriptIQ AI, a senior PostgreSQL database engineer and natural language analytics engine.
Your mission is to generate clean, performant, and safe SELECT queries for PostgreSQL based on user questions.

RULES:
1. ONLY generate SELECT queries. DO NOT generate DROP, DELETE, UPDATE, INSERT, TRUNCATE, or ALTER under any circumstances.
2. Dialect: PostgreSQL. Use PostgreSQL functions (e.g. CURRENT_DATE, INTERVAL '30 days', ILIKE, EXTRACT, ROUND, NULLIF).
   - Date differences: In PostgreSQL, (CURRENT_DATE - date_column) returns an integer (number of days). To check older than 30 days, compare with integer: (CURRENT_DATE - date_column) > 30, OR compare timestamps: date_column < CURRENT_DATE - INTERVAL '30 days'. NEVER compare (date - date) > INTERVAL.
   - For dormant license seats: license_allocations.is_dormant = TRUE OR (CURRENT_DATE - license_allocations.last_activity_date) > 30.
   - For aggregate counts with multiple joins, use COUNT(DISTINCT table.id) to avoid cartesian inflation.
3. Always format your output with a markdown ```sql code block containing the SQL query, followed by a 1-sentence plain English explanation.
4. If the question asks for spend or cost, check whether monthly or annual spend is desired. Default to `monthly_cost` for monthly figures and `annual_contract_value` for annual figures.
5. Do NOT append arbitrary LIMIT clauses if the user asks for 'all' records or an unconstrained list (such as 'List all users...', 'Show all subscriptions'). Return the full matching dataset. Only use LIMIT when the user explicitly asks for top/bottom or a specific count (e.g., 'top 5', 'first 10').
6. User Name & Subscription Allocation Schema Rules:
   - In the `users` table, employee names are stored in column `full_name` (e.g. `u.full_name ILIKE '%Elena Wilson%'`).
   - The `users` table does NOT have `first_name` or `last_name` columns. NEVER reference `u.first_name` or `u.last_name`.
   - To find what subscriptions an employee has, JOIN subscriptions with license_allocations and users:
     SELECT DISTINCT s.id, s.product_name, s.category, s.monthly_cost, s.status, u.full_name
     FROM subscriptions s
     JOIN license_allocations la ON la.subscription_id = s.id
     JOIN users u ON u.id = la.user_id
     WHERE u.full_name ILIKE '%<name>%';
7. Subscription Audit & Utilization Queries:
   When asked to "audit" or "analyze metrics and contract terms" or check assigned users, cost per user, unallocated seats, or dormant waste for a subscription/tool:
   Generate SQL following this exact structure:
   SELECT
       s.product_name,
       s.category,
       s.billing_cycle,
       s.monthly_cost,
       s.annual_contract_value,
       s.total_seats_licensed,
       COUNT(DISTINCT la.user_id) AS assigned_users_count,
       ROUND(s.monthly_cost / NULLIF(COUNT(DISTINCT la.user_id), 0), 2) AS cost_per_user,
       (s.total_seats_licensed - COUNT(DISTINCT la.id)) AS unallocated_seats,
       ROUND((s.total_seats_licensed - COUNT(DISTINCT la.id)) * (s.monthly_cost / NULLIF(s.total_seats_licensed, 0)), 2) AS unallocated_waste,
       COUNT(CASE WHEN la.is_dormant = TRUE OR (CURRENT_DATE - la.last_activity_date) > 30 THEN 1 END) AS dormant_seats,
       ROUND(COUNT(CASE WHEN la.is_dormant = TRUE OR (CURRENT_DATE - la.last_activity_date) > 30 THEN 1 END) * (s.monthly_cost / NULLIF(s.total_seats_licensed, 0)), 2) AS dormant_waste,
       s.renewal_date,
       s.status
   FROM subscriptions s
   LEFT JOIN license_allocations la ON la.subscription_id = s.id
   WHERE s.product_name ILIKE '%<tool_name>%'
   GROUP BY s.id, s.product_name, s.category, s.billing_cycle, s.monthly_cost, s.annual_contract_value, s.total_seats_licensed, s.renewal_date, s.status;

{schema_prompt}

{few_shot_text}
"""

    user_prompt = f"User Question: {query}\nQuery Type: {query_type}\nRelevant Tables: {', '.join(resolved_tables)}"
    if retry_error:
        user_prompt += f"\n\nPREVIOUS GENERATION ERROR: {retry_error}\nPlease correct the SQL query to resolve this error."

    # Construct LangChain messages
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]

    llm = get_langchain_model(selected_model, temperature=temperature)
    raw_response = None

    if llm is not None:
        try:
            ai_msg = await llm.ainvoke(messages)
            raw_response = ai_msg.content
        except Exception as e:
            print(f"[LangChain LLM Notice] {e}. Falling back to internal engine.")

    if raw_response:
        sql, explanation = clean_generated_sql(raw_response)
    else:
        sql, explanation = synthesize_fallback_sql(
            query=query,
            query_type=query_type,
            resolved_tables=resolved_tables,
            few_shot_examples=few_shot_examples
        )

    return {
        "generated_sql": sql,
        "explanation": explanation,
        "messages": messages + [AIMessage(content=f"```sql\n{sql}\n```\n{explanation}")]
    }

async def validator_node(state: SQLAgentState) -> Dict[str, Any]:
    """Stage 5: AST Parsing & SQL Validator Guardrails."""
    if not state.get("is_supported", True):
        return {}

    if state.get("query_type") == "CONVERSATIONAL":
        return {
            "is_valid": True,
            "validation_errors": [],
            "generated_sql": None,
            "retry_error": None,
            "retry_count": 0
        }

    sql = state.get("generated_sql", "")
    val_out = validate_and_sanitize_sql(sql)
    
    is_valid = val_out["valid"]
    errors = val_out.get("errors", [])
    retry_count = state.get("retry_count", 0)

    # If invalid and we haven't retried yet, prepare feedback
    retry_error = "; ".join(errors) if not is_valid else None
    if not is_valid:
        retry_count += 1

    return {
        "is_valid": is_valid,
        "validation_errors": errors,
        "generated_sql": val_out.get("sanitized_sql", sql),
        "retry_error": retry_error,
        "retry_count": retry_count
    }

async def executor_node(state: SQLAgentState) -> Dict[str, Any]:
    """Stage 6: Read-Only Database Execution via MCP Postgres Tool."""
    if not state.get("is_supported", True):
        return {
            "success": False,
            "columns": [],
            "rows": [],
            "row_count": 0,
            "error": state.get("rejection_reason")
        }

    if state.get("query_type") == "CONVERSATIONAL":
        return {
            "success": True,
            "columns": [],
            "rows": [],
            "row_count": 0,
            "error": None
        }

    sql = state.get("generated_sql", "")
    
    # Execute via MCP Tool
    mcp_result = mcp_postgres_query.invoke({"sql_query": sql})

    error = mcp_result.get("error")
    retry_count = state.get("retry_count", 0)
    retry_error = state.get("retry_error")

    # If execution failed and we have retries remaining, trigger self-healing retry
    if error and retry_count <= 1:
        retry_count += 1
        retry_error = f"Database execution error: {error}. Please correct the PostgreSQL query syntax, data types, or operators."

    # If execution failed after self-healing retry, recover using synthesized engine SQL
    if error and retry_count > 1:
        fb_sql, fb_exp = synthesize_fallback_sql(
            query=state["query"],
            query_type=state.get("query_type", "SELECT_AGGREGATE"),
            resolved_tables=state.get("resolved_tables", []),
            few_shot_examples=state.get("few_shot_examples", [])
        )
        if fb_sql:
            fb_res = mcp_postgres_query.invoke({"sql_query": fb_sql})
            if fb_res.get("success"):
                return {
                    "success": True,
                    "columns": fb_res.get("columns", []),
                    "rows": fb_res.get("rows", []),
                    "row_count": fb_res.get("row_count", 0),
                    "error": None,
                    "generated_sql": fb_sql,
                    "explanation": fb_exp,
                    "retry_count": retry_count,
                    "retry_error": None
                }

    return {
        "success": mcp_result.get("success", False),
        "columns": mcp_result.get("columns", []),
        "rows": mcp_result.get("rows", []),
        "row_count": mcp_result.get("row_count", 0),
        "error": error,
        "retry_count": retry_count,
        "retry_error": retry_error
    }

async def formatter_node(state: SQLAgentState) -> Dict[str, Any]:
    """Stage 7: Format Results, Derive Auto-Charts, and Natural Language Summary."""
    query = state["query"]
    query_type = state.get("query_type", "SELECT_SIMPLE")
    sql = state.get("generated_sql")
    explanation = state.get("explanation")
    columns = state.get("columns", [])
    rows = state.get("rows", [])
    error = state.get("error")
    is_supported = state.get("is_supported", True)

    if not is_supported:
        reason = state.get("rejection_reason", "Unsupported query type.")
        return {
            "success": False,
            "query": query,
            "query_type": "UNSUPPORTED",
            "model_used": state.get("selected_model"),
            "sql": None,
            "explanation": reason,
            "nl_summary": f"Query blocked: {reason}",
            "columns": [],
            "rows": [],
            "row_count": 0,
            "chart": None,
            "error": reason
        }

    if query_type == "CONVERSATIONAL":
        return {
            "success": True,
            "chart": None,
            "nl_summary": explanation or "👋 Hello! How can I assist you with your organization's subscriptions?",
            "columns": [],
            "rows": [],
            "row_count": 0,
            "error": None
        }

    exec_dict = {
        "columns": columns,
        "rows": rows,
        "row_count": len(rows),
        "error": error
    }
    formatted = format_result(query, sql or "", exec_dict, explanation)

    return {
        "success": formatted["success"],
        "chart": formatted.get("chart"),
        "nl_summary": formatted.get("nl_summary"),
        "error": formatted.get("error")
    }
