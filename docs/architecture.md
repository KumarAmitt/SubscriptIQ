# SubscriptIQ — Architecture Overview

This document provides a comprehensive technical overview of the **SubscriptIQ** Text-to-SQL architecture, the 7-stage LangGraph workflow, data models, and vector retrieval subsystem.

---

## 1. System Architecture

SubscriptIQ decouples the presentation layer, the AI orchestration pipeline, the relational analytics database, and the vector retrieval engine:

```
                            ┌─────────────────────────────────┐
                            │    Vue 3 Single Page App        │
                            │ (Tailored SaaS Analytics UI)    │
                            └───────────────┬─────────────────┘
                                            │ HTTP / JSON
                                            ▼
                            ┌─────────────────────────────────┐
                            │   Nginx Reverse Proxy (:5173)   │
                            │  Route /api ➔ backend:8000      │
                            └───────────────┬─────────────────┘
                                            │
                                            ▼
                      ┌─────────────────────────────────────────────┐
                      │            FastAPI REST Server              │
                      │  - Auth & RBAC (HMAC-SHA256 JWT)            │
                      │  - Administration REST APIs                 │
                      │  - Natural Language Query Orchestrator      │
                      └─────────────────────┬───────────────────────┘
                                            │
               ┌────────────────────────────┼────────────────────────────┐
               ▼                            ▼                            ▼
   ┌───────────────────────┐   ┌───────────────────────────┐   ┌──────────────────────┐
   │ LangGraph StateGraph  │   │  Qdrant Vector DB Engine  │   │ PostgreSQL 16 DB     │
   │ (7-Stage Pipeline     │   │ (Embedded In-Memory Store │   │ (9 Domain Tables,    │
   │ + Self-Healing Loops) │   │  35 Curated Few-Shots)    │   │  >1,000 Seed Rows)   │
   └───────────────────────┘   └───────────────────────────┘   └──────────────────────┘
```

---

## 2. The 7-Stage LangGraph AI Pipeline

The core query processing pipeline is constructed as a cyclic state machine (`StateGraph(SQLAgentState)`) in [`backend/app/ai_services/graph.py`](file:///home/galaxy/CODE/AI/capApp/SubscriptIQ/backend/app/ai_services/graph.py):

```
                   [ START ]
                       │
                       ▼
               ┌───────────────┐
               │ 1. Classifier │
               └───────┬───────┘
                       │
      Is Supported?   / \   Unsupported / Malicious
       ───────────────   ──────────────────────────────────┐
      │                                                    │
      ▼                                                    │
┌──────────────────┐                                       │
│ 2. Schema Linker │                                       │
└─────┬────────────┘                                       │
      │                                                    │
      ▼                                                    │
┌──────────────────────┐                                   │
│ 3. Qdrant Retriever  │                                   │
└─────┬────────────────┘                                   │
      │                                                    │
      ▼                                                    │
┌──────────────────────┐  ◀───────────┐                    │
│   4. SQL Generator   │              │ (Retry ≤ 1)        │
└─────┬────────────────┘              │ Feedback           │
      │                               │                    │
      ▼                               │                    │
┌──────────────────────┐              │                    │
│   5. SQL Validator   │ ──── Valid? ─┘                    │
└─────┬────────────────┘      No                           │
      │                                                    │
      ▼ Yes                                                │
┌──────────────────────┐              │                    │
│    6. SQL Executor   │ ── Error? ───┘                    │
└─────┬────────────────┘    (DB Syntax/Runtime Retry)      │
      │                                                    │
      ▼ Success                                            │
┌──────────────────────┐                                   │
│  7. Result Formatter │ ◀─────────────────────────────────┘
└─────┬────────────────┘
      │
      ▼
   [ END ]
```

### Stage Breakdown

| Stage | Module | Responsibility |
|---|---|---|
| **1. Classifier** | [`classifier.py`](file:///home/galaxy/CODE/AI/capApp/SubscriptIQ/backend/app/engine/classifier.py) | Analyzes intent into `SELECT_SIMPLE`, `SELECT_AGGREGATE`, `SELECT_JOIN`, `SELECT_TEMPORAL`, or `UNSUPPORTED`. Destructive queries (`DROP`, `DELETE`, `TRUNCATE`) are blocked immediately without invoking the LLM. |
| **2. Schema Linker** | [`schema_linker.py`](file:///home/galaxy/CODE/AI/capApp/SubscriptIQ/backend/app/engine/schema_linker.py) | Maps user phrasing to database tables and columns, matches business synonyms ("annual spend" ➔ `annual_contract_value`), and resolves documented schema ambiguities. |
| **3. Vector Retriever** | [`retriever.py`](file:///home/galaxy/CODE/AI/capApp/SubscriptIQ/backend/app/engine/retriever.py) | Queries the embedded Qdrant vector database using cosine distance to retrieve the top 3–5 most relevant (Question ➔ SQL) examples. |
| **4. SQL Generator** | [`generator.py`](file:///home/galaxy/CODE/AI/capApp/SubscriptIQ/backend/app/engine/generator.py) | Combines PostgreSQL DDL schema context, column descriptions, and retrieved few-shot examples into an enriched prompt for the LLM (Groq / Gemini). |
| **5. SQL Validator** | [`validator.py`](file:///home/galaxy/CODE/AI/capApp/SubscriptIQ/backend/app/engine/validator.py) | Performs Abstract Syntax Tree (AST) parsing with `sqlglot`. Validates table names, rejects prohibited keywords, checks row limits, and emits error feedback if a retry is required. |
| **6. SQL Executor** | [`executor.py`](file:///home/galaxy/CODE/AI/capApp/SubscriptIQ/backend/app/engine/executor.py) | Executes the validated query against PostgreSQL using read-only transaction semantics (`READ ONLY`), capturing latency and row counts. |
| **7. Result Formatter** | [`formatter.py`](file:///home/galaxy/CODE/AI/capApp/SubscriptIQ/backend/app/engine/formatter.py) | Formats tabular JSON data, generates a 1–2 sentence executive summary with Indian Rupee (₹) formatting, and auto-detects chart configurations (doughnut/bar) for numeric columns. |

---

## 3. Relational Schema Architecture

The database model is defined in [`backend/app/database/schema_ddl.sql`](file:///home/galaxy/CODE/AI/capApp/SubscriptIQ/backend/app/database/schema_ddl.sql) across 12 tables:

### Domain Tables (SaaS Analytics)
1. **`organizations`**: Enterprise tenant details, industry, and employee size.
2. **`departments`**: Cost centers, headcounts, and annual department budgets.
3. **`users`**: Enterprise employees assigned to cost centers and departments (1,200 rows).
4. **`vendors`**: SaaS vendors, security compliance (SOC2, FedRAMP), and support SLAs.
5. **`subscriptions`**: Active SaaS contracts, billing cycles, monthly costs, and renewal dates.
6. **`license_allocations`**: Per-user seat assignments, seat types, and last active dates for dormant seat detection (1,500 rows).
7. **`invoices`**: Billing history, tax, payment status, and due dates (1,200 rows).
8. **`usage_telemetry`**: Daily active users (DAU), storage consumption, and API call volumes (1,000 rows).
9. **`optimization_recommendations`**: Cost-saving opportunities generated from dormant licenses and unutilized seats.

### System & Administration Tables
10. **`schema_metadata`**: Dynamic dictionary of table/column descriptions and sensitive (PII) column masking flags.
11. **`query_logs`**: Comprehensive audit trail of all natural language questions, generated SQL, status, and execution timings.
12. **`system_settings`**: Persisted configuration for active guardrails, row limits, and model parameters.

---

## 4. Qdrant Vector Store Integration

- **Storage:** Local persistent vector storage (`backend/database/qdrant_storage`).
- **Dataset:** 35 curated few-shot query pairs spanning all query classes (`SELECT_SIMPLE`, `SELECT_AGGREGATE`, `SELECT_JOIN`, `SELECT_TEMPORAL`).
- **Admin Control:** The **Examples Manager** panel supports full CRUD and live semantic testing directly against the collection.

---

## 5. Security & Guardrails Architecture

1. **Pre-LLM Gate:** The classifier catches raw destructive strings before the prompt is sent to the LLM.
2. **AST Guardrail Engine:** `sqlglot` parses queries into syntax trees to identify and block write operations (`DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `TRUNCATE`).
3. **Safe Database Execution:** All user queries execute in a read-only PostgreSQL transaction session.
4. **Row Clamping:** Enforces default and maximum query row limits (`LIMIT 50`) to protect memory and network bandwidth.
5. **Role-Based Access Control (RBAC):** Admin features (schema editing, guardrails configuration, model switching, evaluation harness) require HMAC-SHA256 JWT tokens with the `admin` role.
