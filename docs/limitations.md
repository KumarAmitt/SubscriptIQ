# SubscriptIQ — Known Limitations & Future Roadmap

This document outlines the known boundaries, engineering trade-offs, and operational limitations of the current **SubscriptIQ** release, along with suggested future enhancements.

---

## 1. Cloud LLM Free-Tier Rate Limits (TPD / RPM)

- **Symptom:** When executing high-volume queries or running the full 25-query evaluation benchmark rapidly, free-tier cloud endpoints (particularly Groq's `openai/gpt-oss-120b`) can encounter HTTP 429 errors (`Tokens-Per-Day (TPD)` or `Requests-Per-Minute (RPM)` limit exceeded).
- **Current Mitigation:** The system logs an explicit warning and falls back to deterministic local schema heuristics when rate limits are triggered.
- **Production Recommendation:** For production deployments, configure dedicated tier API keys with higher concurrency limits or switch to high-throughput endpoints like `gemini-3.1-flash-lite`.

---

## 2. Read-Only SQL Scope by Design

- **Constraint:** SubscriptIQ is strictly an **analytics and intelligence** platform. It rejects all data manipulation statements (`INSERT`, `UPDATE`, `DELETE`, `MERGE`) and schema alterations (`DROP`, `ALTER`, `TRUNCATE`).
- **Rationale:** Prevents accidental modification or malicious destruction of enterprise financial, contract, and telemetry records by natural language users.
- **Limitation:** Users cannot use natural language to perform operational tasks like *"Update Sarah's seat allocation to Admin"* or *"Mark invoice #1045 as paid"*.

---

## 3. Single-Turn Query Context (Stateless SQL)

- **Current Behavior:** Each natural language query is currently evaluated independently against the schema and vector store.
- **Limitation:** Conversational follow-ups (e.g., Question 1: *"Show all engineering tools"* followed by Question 2: *"Now filter those where cost exceeds ₹50,000"*) treat Question 2 as an isolated prompt rather than refining the previously generated SQL AST.
- **Future Roadmap:** Maintain session-level conversation memory within the LangGraph state to support progressive query refinement and conversational SQL drill-downs.

---

## 4. Cross-Dialect Transpilation Edge Cases

- **Current Behavior:** While the core queries use standardized SQL supported by `sqlglot`, certain PostgreSQL-specific functions (e.g., `ILIKE`, advanced date intervals, `ROUND(numeric, 2)`) may require manual adjustments when transpiling to dialects with distinct casting requirements (such as SQLite).
- **Target Engine:** SubscriptIQ is natively calibrated for PostgreSQL 16.

---

## 5. Synchronous Batch Benchmark Timeout (Nginx Proxy)

- **Current Behavior:** The 25-query evaluation benchmark runs end-to-end within a single synchronous HTTP `POST /api/eval` request.
- **Limitation:** When using external LLMs with varying network latency or retry loops, evaluating 25 queries sequentially can take 60–90 seconds. Standard reverse proxy configurations with default 60-second timeouts (`proxy_read_timeout 60s`) may return a `504 Gateway Time-out` to the browser even though the backend process continues.
- **Recommended Solution:** Adjust Nginx's proxy timeout to 300s (`proxy_read_timeout 300s;`) or execute the evaluation benchmark directly via the backend API (`http://localhost:8000/api/eval`) or background job queue (e.g., Celery / Redis).
