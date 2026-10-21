# SubscriptIQ — Key Design Decisions

This document outlines the core architectural and engineering decisions made during the design and development of **SubscriptIQ**.

---

## 1. Why LangGraph Instead of Simple Linear Chains?

Traditional LLM pipelines execute sequentially (`Step A ➔ Step B ➔ Step C`). In Text-to-SQL systems, this approach fails as soon as a generated query contains a syntax error, unknown column reference, or fails AST validation.

**Our Decision:**
We built the workflow using **LangGraph `StateGraph`** with a typed state schema (`SQLAgentState`):
- **Conditional Routing:** Malicious or destructive requests (`DROP`, `DELETE`) are routed immediately from the Classifier to the Formatter, bypassing the LLM completely.
- **Self-Healing AST Loop (`router_after_validator`):** If `sqlglot` detects syntax errors or missing tables, the system feeds the validator error back to `sql_generator` for a single automated correction attempt.
- **Self-Healing Runtime Loop (`router_after_executor`):** If PostgreSQL returns a runtime error (e.g., type casting discrepancy), the exact database error is fed back to the generator to heal the query before returning results to the user.

---

## 2. Why PostgreSQL 16 Over SQLite?

While SQLite was the default minimum requirement for the assignment, SubscriptIQ chose **PostgreSQL 16**:
- **Realistic Enterprise Dialect:** SaaS subscription analytics requires robust temporal math (`DATE_TRUNC`, interval arithmetic, date subtraction for churn/dormancy) and complex relational joins across 9+ tables.
- **True Read-Only Transaction Security:** PostgreSQL allows native session-level enforcement (`SET TRANSACTION READ ONLY`), providing a defense-in-depth guarantee against accidental writes.
- **Production Parity:** Using PostgreSQL in Docker mirrors real-world corporate analytics warehouses rather than single-file demo databases.

---

## 3. Why Embedded Qdrant for Few-Shot Vector Retrieval?

Rather than hardcoding static few-shot examples into LLM prompts or relying on heavy cloud vector databases:
- **Embedded Local Persistence:** Qdrant runs embedded directly inside the backend container (`backend/database/qdrant_storage`), eliminating external cloud dependencies, API costs, or network latency.
- **Semantic Generalization:** Few-shot matching uses cosine similarity over query semantics rather than keyword string matching, ensuring queries like *"How much are we paying Figma monthly?"* match relevant cost-retrieval examples.
- **Live CRUD via Admin UI:** Administrators can add, inspect, and delete examples directly through the **Examples Manager** panel without restarting the backend or rebuilding containers.

---

## 4. Why AST Parsing (`sqlglot`) Over Regex Guardrails?

Many SQL security implementations attempt to detect dangerous queries using regex pattern matching (e.g. `re.search(r"DROP|DELETE")`), which is notoriously vulnerable to SQL injection, comments (`/* ... */`), string literals, and subquery tricks.

**Our Decision:**
We use **`sqlglot`** to parse the generated query into an Abstract Syntax Tree (AST):
- **Dialect-Aware Syntax Verification:** Confirms that the query is strictly valid PostgreSQL SQL.
- **AST Node Traversal:** Directly inspects expression types to guarantee the root statement is a `Select` expression.
- **Safe Limit Injection:** Automatically verifies whether a `LIMIT` clause exists and clamps it to configured thresholds without breaking existing `ORDER BY` or nested clauses.
- **Semantic Transpilation:** Enables multi-dialect equivalence checks and semantic diffing during the evaluation benchmark.

---

## 5. Why Vue 3 + Pinia + Nginx Reverse Proxy?

- **Vue 3 Composition API & Pinia:** Enables responsive, component-driven UI panels (live table accordions, dynamic charts, toggle switches) with structured state management for authentication, chat sessions, and configuration settings.
- **Unified Reverse Proxy Architecture:** The Vue production container uses **Nginx** to serve optimized static frontend assets and reverse-proxy `/api` requests to the FastAPI backend. This avoids Cross-Origin Resource Sharing (CORS) complications and simplifies production deployment to a single external port (`5173`).

---

## 6. Currency and Localization (`en-IN` / INR ₹)

To model real-world localization:
- **Currency Standard:** All monetary figures across tables (`monthly_cost`, `annual_contract_value`, `invoices.amount`, `budget_annual`) are modeled in **Indian Rupees (₹)**.
- **Indian Number Formatting:** Telemetry tables and summaries format numbers according to the Indian system (`en-IN`, e.g., `₹62,85,500`), demonstrating how enterprise analytics tools adapt to specific regional financial standards.
