import re

BLOCKED_INTENT_KEYWORDS = [
    "drop", "delete", "truncate", "alter", "update", "insert",
    "grant", "revoke", "create table", "create database", "drop table",
    "modify", "remove table"
]

TABLE_KEYWORDS = {
    "subscriptions": ["subscription", "subscriptions", "sub", "subs", "contract", "contracts", "plan", "plans", "tool", "tools", "software", "saas", "license", "licenses"],
    "users": ["user", "users", "employee", "employees", "member", "members", "staff", "person", "people", "worker"],
    "departments": ["department", "departments", "dept", "depts", "division", "team", "teams", "budget", "cost center"],
    "vendors": ["vendor", "vendors", "provider", "providers", "supplier", "company", "github", "figma", "slack", "notion", "datadog", "aws", "zoom", "salesforce", "atlassian", "linear", "snowflake", "workday"],
    "license_allocations": ["license", "licenses", "seat", "seats", "allocation", "allocations", "dormant", "idle", "unassigned", "assigned", "inactive"],
    "invoices": ["invoice", "invoices", "bill", "bills", "billing", "payment", "payments", "paid", "due", "card", "amex", "brex", "tax"],
    "usage_telemetry": ["telemetry", "usage", "utilization", "dau", "active users", "storage", "activity", "metrics"],
    "optimization_recommendations": ["recommendation", "recommendations", "saving", "savings", "optimize", "optimization", "waste", "underutilized", "reclaim", "redundant"]
}

COLUMN_KEYWORDS = {
    "monthly_cost": ["monthly cost", "monthly spend", "spend per month", "monthly charge", "monthly price"],
    "annual_contract_value": ["annual spend", "annual contract", "acv", "yearly cost", "total contract value"],
    "renewal_date": ["renewal", "renew", "renews", "expires", "expiration", "renewal date", "renewing"],
    "last_activity_date": ["last active", "last login", "last activity", "dormant", "inactive"],
    "amount": ["invoice amount", "amount paid", "total amount", "charge"],
    "utilization_rate": ["utilization", "utilization rate", "seat usage", "adoption rate"],
    "estimated_monthly_savings": ["savings", "monthly savings", "money saved"]
}

def classify_query(query: str) -> dict:
    """
    Step 1: Query Classifier
    Classifies intent into:
    - SELECT_SIMPLE
    - SELECT_AGGREGATE
    - SELECT_JOIN
    - SELECT_TEMPORAL
    - UNSUPPORTED (e.g. destructive SQL or non-query intents)
    """
    cleaned = query.strip()
    lower = cleaned.lower()

    # 1. Check for unsupported/destructive intents
    for kw in BLOCKED_INTENT_KEYWORDS:
        # Match as whole word or phrase
        if re.search(rf"\b{re.escape(kw)}\b", lower):
            return {
                "query_type": "UNSUPPORTED",
                "tables_mentioned": [],
                "columns_mentioned": [],
                "is_supported": False,
                "reason": f"Prohibited operation '{kw.upper()}' detected. SubscriptIQ is a read-only analytics engine."
            }

    # 2. Check for conversational / greetings / capability queries
    conversational_patterns = [
        r"^(hi|hello|hey|greetings|good\s+(morning|afternoon|evening)|howdy|sup|how\s+are\s+you|thanks|thank\s+you|bye|goodbye)\b",
        r"\b(what\s+can\s+you\s+do|how\s+can\s+you\s+help|what\s+do\s+you\s+do|who\s+are\s+you|what\s+is\s+this|help\s*me|help$)\b",
        r"\b(what\s+can\s+i\s+ask|sample\s+queries|capabilities|sample\s+questions)\b"
    ]
    is_conversational = any(re.search(p, lower) for p in conversational_patterns)

    # 3. Extract tables mentioned
    tables_mentioned = []
    for tbl, kws in TABLE_KEYWORDS.items():
        if any(re.search(rf"\b{re.escape(k)}\b", lower) for k in kws):
            tables_mentioned.append(tbl)

    # 4. Extract columns mentioned
    columns_mentioned = []
    for col, kws in COLUMN_KEYWORDS.items():
        if any(re.search(rf"\b{re.escape(k)}\b", lower) for k in kws):
            columns_mentioned.append(col)

    # If conversational greeting/help without explicit table/column query, route to CONVERSATIONAL
    if is_conversational and not tables_mentioned and not columns_mentioned:
        return {
            "query_type": "CONVERSATIONAL",
            "tables_mentioned": [],
            "columns_mentioned": [],
            "is_supported": True,
            "reason": None
        }

    # Check for domain analytical keywords
    domain_keywords = [
        "subscription", "subscriptions", "sub", "subs", "tool", "tools", "software", "saas", "app", "apps",
        "spend", "spending", "cost", "costs", "price", "pricing", "expense", "expenses", "expenditure",
        "budget", "contract", "contracts", "acv", "mrr", "arr", "renew", "renewal", "renewals",
        "license", "licenses", "seat", "seats", "allocated", "unallocated", "dormant", "idle",
        "invoice", "invoices", "bill", "bills", "billing", "payment", "payments", "paid", "due", "overdue",
        "user", "users", "employee", "employees", "staff", "member", "members", "team", "department", "departments",
        "vendor", "vendors", "provider", "providers", "audit", "optimization", "optimize", "savings", "waste",
        "active", "inactive", "status", "compliance", "tier", "telemetry", "utilization",
        "figma", "github", "slack", "notion", "datadog", "aws", "zoom", "salesforce", "atlassian",
        "linear", "snowflake", "workday", "hubspot", "jira", "confluence", "openai", "google", "microsoft"
    ]
    has_domain_keyword = any(re.search(rf"\b{re.escape(k)}\b", lower) for k in domain_keywords)
    has_person_query = bool(re.search(r"\b(does\s+[a-zA-Z]+\s+[a-zA-Z]+\s+have|has\s+[a-zA-Z]+\s+[a-zA-Z]+|for\s+[a-zA-Z]+\s+[a-zA-Z]+|assigned\s+to\s+[a-zA-Z]+)\b", lower))

    # If the query mentions no database tables, columns, domain concepts, or person entities, it is an out-of-scope query
    if not tables_mentioned and not columns_mentioned and not has_domain_keyword and not has_person_query:
        return {
            "query_type": "CONVERSATIONAL",
            "tables_mentioned": [],
            "columns_mentioned": [],
            "is_supported": True,
            "reason": None
        }

    # 4. Determine Query Type
    # Temporal indicators:
    temporal_patterns = [
        r"\b(renew|renewal|renewing|renews|expir\w+|today|yesterday|tomorrow|days?|months?|years?|quarter|annual|past|last \d+|next \d+|recent|since|before|after|date|between)\b"
    ]
    is_temporal = any(re.search(p, lower) for p in temporal_patterns)

    # Aggregate indicators:
    aggregate_patterns = [
        r"\b(total|sum|average|avg|count|how many|minimum|min|maximum|max|grouped|per|breakdown|by category|by department|by vendor|rank|top \d+|highest|lowest|distribution)\b"
    ]
    is_aggregate = any(re.search(p, lower) for p in aggregate_patterns)

    # Join indicators: multiple distinct entity types, explicit relational requests, or user-ownership questions
    has_person_query = bool(re.search(r"\b(does\s+[a-zA-Z]+\s+[a-zA-Z]+\s+have|has\s+[a-zA-Z]+\s+[a-zA-Z]+|for\s+[a-zA-Z]+\s+[a-zA-Z]+|assigned\s+to\s+[a-zA-Z]+)\b", lower))
    if has_person_query or any(re.search(rf"\b{re.escape(w)}\b", lower) for w in ["have", "has", "holds", "assigned to", "allocated to", "subscribed to"]):
        if any(sub_w in lower for sub_w in ["subscription", "subscriptions", "tool", "tools", "license", "software"]):
            if "users" not in tables_mentioned:
                tables_mentioned.append("users")
            if "license_allocations" not in tables_mentioned:
                tables_mentioned.append("license_allocations")
            if "subscriptions" not in tables_mentioned:
                tables_mentioned.append("subscriptions")

    is_join = len(tables_mentioned) >= 2 or any(
        phrase in lower for phrase in ["with user", "for department", "by vendor", "with vendor", "assigned to", "who have", "which employee", "does", "have"]
    ) or has_person_query

    if is_temporal:
        query_type = "SELECT_TEMPORAL"
    elif is_aggregate:
        query_type = "SELECT_AGGREGATE"
    elif is_join:
        query_type = "SELECT_JOIN"
    else:
        query_type = "SELECT_SIMPLE"

    # Default to subscriptions table if no tables detected
    if not tables_mentioned:
        tables_mentioned = ["subscriptions"]

    return {
        "query_type": query_type,
        "tables_mentioned": tables_mentioned,
        "columns_mentioned": columns_mentioned,
        "is_supported": True,
        "reason": None
    }
