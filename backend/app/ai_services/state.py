from typing import TypedDict, Optional, List, Dict, Any
from langchain_core.messages import BaseMessage

class SQLAgentState(TypedDict, total=False):
    """
    LangGraph State Schema for the Text-to-SQL Analytics Agent.
    Tracks state through classification, schema linking, Qdrant retrieval,
    LangChain model generation, AST validation, MCP tool execution, and formatting.
    """
    # User Inputs
    query: str
    selected_model: str
    user_role: str
    user_email: str
    temperature: float

    # Pipeline Metadata & Classification
    query_type: str
    is_supported: bool
    rejection_reason: Optional[str]

    # Schema Linking & Vector Retrieval
    resolved_tables: List[str]
    schema_prompt: str
    few_shot_examples: List[Dict[str, Any]]

    # LLM Generation & LangChain Messages
    messages: List[BaseMessage]
    generated_sql: Optional[str]
    explanation: Optional[str]
    retry_error: Optional[str]
    retry_count: int

    # AST Guardrails Validation
    is_valid: bool
    validation_errors: List[str]

    # Execution & Formatting
    success: bool
    columns: List[str]
    rows: List[Dict[str, Any]]
    row_count: int
    chart: Optional[Dict[str, Any]]
    nl_summary: Optional[str]
    latency_ms: float
    error: Optional[str]
