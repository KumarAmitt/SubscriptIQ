# SubscriptIQ Backend — AI Services & API Engine

The SubscriptIQ backend is built with **FastAPI**, **LangGraph**, **LangChain**, and **PostgreSQL**, package-managed via Astral's **`uv`**.

---

## 🧠 AI Architecture: LangGraph + LangChain + MCP

All AI features are implemented in the dedicated `app/ai_services/` directory:

```
backend/app/ai_services/
├── __init__.py          # Exports pipeline entrypoint and state schemas
├── state.py             # SQLAgentState TypedDict for LangGraph state machine
├── models.py            # LangChain model factory (ChatGroq, ChatGoogleGenerativeAI)
├── mcp_tools.py         # Model Context Protocol (MCP) @tool definitions for PostgreSQL
├── nodes.py             # 7 pipeline nodes implemented as LangGraph step functions
└── graph.py             # StateGraph definition, conditional edges, retry loops & compilation
```

### Reference Concepts from `notebooks/`
The implementation draws inspiration and architectural patterns directly from the reference notebooks:
1. **`2_react_langgraph.ipynb` & `ai_orchestration_langgraph.ipynb`**:
   - `StateGraph(SQLAgentState)` structure with typed state management.
   - Message passing via `BaseMessage` and `AIMessage`.
   - Dynamic routing and conditional edges.
2. **`routing_with_guardrails.ipynb` & `agentic_ai_langchain_with_sem_router_updated.ipynb`**:
   - Pre-LLM intent classification and safety guardrails.
   - Guardrail conditional edge: routes `UNSUPPORTED` destructive intents (`DROP`, `DELETE`, `TRUNCATE`) immediately to an early exit, never allowing harmful queries to reach LLMs or the database.
   - Schema linking and ambiguous term resolution.
3. **`qdrant_filterops.ipynb`**:
   - Cosine similarity vector search and payload filtering for few-shot SQL retrieval.

---

## 🛠️ MCP (Model Context Protocol) Database Connection

Database operations within the LangGraph nodes are encapsulated using Model Context Protocol (MCP) compliant `@tool` decorators defined in `app/ai_services/mcp_tools.py`:

- **`mcp_postgres_query`**: Executes read-only queries with strict session boundaries (`SET TRANSACTION READ ONLY;`) and timeout limits.
- **`mcp_get_table_schema`**: Retrieves column schemas, primary/foreign keys, and data types for dynamic LLM context.
- **`mcp_explain_query`**: Analyzes SQL query execution plans (`EXPLAIN (ANALYZE, BUFFERS)`) safely.

---

## 🔄 Self-Healing Graph Workflow

```
[START]
   │
   ▼
classifier_node ──► (destructive?) ──► [END with Guardrail Rejection]
   │ (safe)
   ▼
schema_linker_node
   │
   ▼
qdrant_retriever_node
   │
   ▼
sql_generator_node ◄──┐ (Self-Healing Retry on Syntax/Safety Error)
   │                  │
   ▼                  │
validator_node ───────┘ (up to 1 retry attempt)
   │ (valid)
   ▼
executor_node (MCP PostgreSQL)
   │
   ▼
formatter_node
   │
   ▼
[END]
```

---

## 📦 Package Management with `uv`

All dependencies are tracked in `pyproject.toml` and locked in `uv.lock`. Do **not** use `requirements.txt`.

### Development Commands
```bash
# Install dependencies
uv sync

# Run development server
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run test suite
uv run pytest tests/
```

---

## 🧪 Evaluation Benchmark

SubscriptIQ includes an automated 25-query evaluation harness running against the LangGraph pipeline:

```bash
# Login to get admin token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@subscriptiq.ai","password":"admin123"}' \
  | jq -r .access_token)

# Run benchmark
curl -X POST http://localhost:8000/api/eval \
  -H "Authorization: Bearer $TOKEN"
```
