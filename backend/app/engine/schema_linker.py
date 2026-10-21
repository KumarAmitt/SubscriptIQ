import re
from app.database.connection import fetch_all

SYNONYM_MAP = {
    # Ambiguous concepts
    "spend": ["subscriptions.monthly_cost", "subscriptions.annual_contract_value", "invoices.amount"],
    "cost": ["subscriptions.monthly_cost", "subscriptions.annual_contract_value", "invoices.amount"],
    "revenue": ["subscriptions.annual_contract_value", "invoices.amount"],
    "price": ["subscriptions.monthly_cost", "subscriptions.annual_contract_value"],
    
    # Specific entities
    "tool": "subscriptions.product_name",
    "software": "subscriptions.product_name",
    "application": "subscriptions.product_name",
    "app": "subscriptions.product_name",
    "seats": "subscriptions.total_seats_licensed",
    "license count": "subscriptions.total_seats_licensed",
    "renewal": "subscriptions.renewal_date",
    "expires": "subscriptions.renewal_date",
    "department": "departments.name",
    "team": "departments.name",
    "budget": "departments.budget_annual",
    "employee": "users.full_name",
    "user": "users.full_name",
    "staff": "users.full_name",
    "vendor": "vendors.name",
    "provider": "vendors.name",
    "inactive": "license_allocations.is_dormant",
    "dormant": "license_allocations.is_dormant",
    "last active": "license_allocations.last_activity_date",
    "bill": "invoices.amount",
    "invoice": "invoices.amount",
    "savings": "optimization_recommendations.estimated_monthly_savings",
    "recommendation": "optimization_recommendations.description",
    "utilization": "usage_telemetry.utilization_rate",
    "active users": "usage_telemetry.active_users_day",
}

CANONICAL_SCHEMA = {
    "organizations": [
        ("id", "SERIAL PRIMARY KEY", "Unique organization ID"),
        ("name", "VARCHAR(120)", "Company or entity name"),
        ("domain", "VARCHAR(120)", "Corporate domain"),
        ("industry", "VARCHAR(60)", "Industry sector"),
        ("employee_count", "INT", "Total headcount"),
        ("tier", "VARCHAR(30)", "Account tier (e.g. Enterprise)")
    ],
    "departments": [
        ("id", "SERIAL PRIMARY KEY", "Department ID"),
        ("org_id", "INT REFERENCES organizations(id)", "Parent organization"),
        ("name", "VARCHAR(80)", "Department name (e.g. Engineering, Sales)"),
        ("budget_annual", "NUMERIC(14, 2)", "Annual allocated budget"),
        ("cost_center_code", "VARCHAR(40)", "Accounting cost center code"),
        ("head_count", "INT", "Department employee count")
    ],
    "users": [
        ("id", "SERIAL PRIMARY KEY", "Unique user ID"),
        ("org_id", "INT REFERENCES organizations(id)", "Parent organization"),
        ("dept_id", "INT REFERENCES departments(id)", "Department ID"),
        ("email", "VARCHAR(160)", "Corporate work email"),
        ("full_name", "VARCHAR(100)", "Employee full name (first and last name together; e.g. 'Elena Wilson')"),
        ("role", "VARCHAR(50)", "Job title / role"),
        ("is_active", "BOOLEAN", "Account status flag")
    ],
    "vendors": [
        ("id", "SERIAL PRIMARY KEY", "Vendor ID"),
        ("name", "VARCHAR(100)", "Vendor company name (e.g. Slack, AWS, HubSpot)"),
        ("website", "VARCHAR(160)", "Vendor website"),
        ("support_tier", "VARCHAR(50)", "Contract support level"),
        ("security_compliance", "VARCHAR(80)", "Compliance badges (SOC2, ISO27001, etc.)")
    ],
    "subscriptions": [
        ("id", "SERIAL PRIMARY KEY", "Subscription ID"),
        ("org_id", "INT REFERENCES organizations(id)", "Parent organization"),
        ("vendor_id", "INT REFERENCES vendors(id)", "Vendor ID"),
        ("product_name", "VARCHAR(120)", "Software / product name (e.g. HubSpot Marketing Hub, Slack Enterprise Grid)"),
        ("category", "VARCHAR(60)", "Software category (Sales, Marketing, Communication, etc.)"),
        ("billing_cycle", "VARCHAR(30)", "Billing frequency ('monthly', 'annual', 'quarterly')"),
        ("monthly_cost", "NUMERIC(10, 2)", "Monthly subscription cost"),
        ("annual_contract_value", "NUMERIC(14, 2)", "Total annual contract value (ACV)"),
        ("total_seats_licensed", "INT", "Number of licensed seats purchased"),
        ("start_date", "DATE", "Contract start date"),
        ("renewal_date", "DATE", "Contract renewal / expiration date"),
        ("auto_renew", "BOOLEAN", "Auto renewal flag"),
        ("status", "VARCHAR(30)", "Status ('active', 'under_review', 'canceled')"),
        ("payment_terms", "VARCHAR(40)", "Contract terms ('Net 30', 'Net 60')")
    ],
    "license_allocations": [
        ("id", "SERIAL PRIMARY KEY", "Allocation ID"),
        ("subscription_id", "INT REFERENCES subscriptions(id)", "Subscribed software"),
        ("user_id", "INT REFERENCES users(id)", "Assigned employee"),
        ("seat_type", "VARCHAR(40)", "Seat type ('Full License', 'Admin', 'Viewer', 'Guest')"),
        ("assigned_date", "DATE", "Date seat was assigned"),
        ("last_activity_date", "DATE", "Last login / telemetry activity date"),
        ("is_dormant", "BOOLEAN", "Dormant flag (true if inactive > 30 days)")
    ],
    "invoices": [
        ("id", "SERIAL PRIMARY KEY", "Invoice ID"),
        ("subscription_id", "INT REFERENCES subscriptions(id)", "Associated subscription"),
        ("invoice_number", "VARCHAR(60)", "Unique invoice code"),
        ("invoice_date", "DATE", "Invoice issue date"),
        ("due_date", "DATE", "Payment due date"),
        ("amount", "NUMERIC(12, 2)", "Total invoice charge amount"),
        ("tax_amount", "NUMERIC(10, 2)", "Tax amount"),
        ("payment_status", "VARCHAR(30)", "Status ('paid', 'pending', 'overdue', 'disputed')"),
        ("payment_method", "VARCHAR(60)", "Corporate card or payment method")
    ],
    "usage_telemetry": [
        ("id", "SERIAL PRIMARY KEY", "Telemetry record ID"),
        ("subscription_id", "INT REFERENCES subscriptions(id)", "Associated subscription"),
        ("record_date", "DATE", "Telemetry snapshot date"),
        ("active_users_day", "INT", "Daily active users (DAU)"),
        ("utilization_rate", "NUMERIC(5, 2)", "Seat utilization percentage"),
        ("storage_used_gb", "NUMERIC(10, 2)", "Storage consumed"),
        ("api_calls_count", "INT", "API calls recorded")
    ],
    "optimization_recommendations": [
        ("id", "SERIAL PRIMARY KEY", "Recommendation ID"),
        ("subscription_id", "INT REFERENCES subscriptions(id)", "Associated subscription"),
        ("recommendation_type", "VARCHAR(60)", "Type ('dormant_seats_removal', 'tier_downgrade', etc.)"),
        ("description", "TEXT", "Detailed recommendation insight"),
        ("estimated_monthly_savings", "NUMERIC(10, 2)", "Projected savings per month"),
        ("confidence_score", "NUMERIC(4, 2)", "Confidence level (0.00 to 1.00)"),
        ("status", "VARCHAR(30)", "Status ('detected', 'reviewing', 'applied', 'dismissed')")
    ]
}

def link_schema(query: str, classifier_output: dict) -> dict:
    """
    Step 2: Schema Linker
    Maps entities to exact tables and columns, handles synonyms,
    resolves ambiguities, and queries schema_metadata.
    """
    lower = query.lower()
    resolved_tables = set(classifier_output.get("tables_mentioned", []))
    resolved_columns = set(classifier_output.get("columns_mentioned", []))
    ambiguities = []

    # 1. Match synonyms
    for term, target in SYNONYM_MAP.items():
        if re.search(rf"\b{re.escape(term)}\b", lower):
            if isinstance(target, list):
                # Detected schema ambiguity!
                ambiguities.append({
                    "term": term,
                    "possible_columns": target,
                    "resolution": f"Defaulting to '{target[0]}' for recurring monthly operations unless annual/invoice context is specified."
                })
                # If query mentions 'annual' or 'yearly' or 'acv', select annual_contract_value
                if any(w in lower for w in ["annual", "yearly", "year", "acv"]):
                    resolved_columns.add("subscriptions.annual_contract_value")
                    resolved_tables.add("subscriptions")
                elif any(w in lower for w in ["invoice", "invoices", "billed", "paid", "receipt"]):
                    resolved_columns.add("invoices.amount")
                    resolved_tables.add("invoices")
                else:
                    resolved_columns.add("subscriptions.monthly_cost")
                    resolved_tables.add("subscriptions")
            else:
                tbl, col = target.split(".")
                resolved_tables.add(tbl)
                resolved_columns.add(target)

    # 2. Fetch schema metadata and column descriptions from DB
    meta_rows = []
    try:
        meta_rows = fetch_all(
            "SELECT table_name, column_name, data_type, description, is_sensitive, synonyms FROM schema_metadata ORDER BY table_name, column_name;"
        )
    except Exception as e:
        print(f"Warning: could not fetch schema_metadata from DB ({e})")

    # Group metadata by table
    table_meta_map = {}
    for r in meta_rows:
        tbl = r["table_name"]
        if tbl not in table_meta_map:
            table_meta_map[tbl] = []
        table_meta_map[tbl].append(r)

    # Ensure resolved tables has core tables if still empty
    if not resolved_tables:
        resolved_tables.add("subscriptions")

    # If users is involved, ensure license_allocations and subscriptions are present
    if "users" in resolved_tables:
        resolved_tables.add("license_allocations")
        resolved_tables.add("subscriptions")
    if "license_allocations" in resolved_tables:
        resolved_tables.add("subscriptions")
        resolved_tables.add("users")

    # 3. Construct concise schema context prompt for LLM
    schema_prompt_lines = [
        "### Database Schema (PostgreSQL):",
        "CRITICAL: The `users` table uses column `full_name` for employee names (e.g. `u.full_name ILIKE '%Elena Wilson%'`).",
        "The `users` table does NOT have `first_name` or `last_name` columns. NEVER reference `u.first_name` or `u.last_name`.",
        ""
    ]

    # Render canonical table schema definitions for resolved tables (and core tables)
    tables_to_render = sorted(list(resolved_tables.union({"subscriptions", "license_allocations", "users"})))
    for tbl in tables_to_render:
        if tbl in CANONICAL_SCHEMA:
            col_lines = [f"  - {col} ({dtype}) -- {desc}" for col, dtype, desc in CANONICAL_SCHEMA[tbl]]
            schema_prompt_lines.append(f"Table `{tbl}`:\n" + "\n".join(col_lines))

    # Add foreign key relationship guide
    schema_prompt_lines.append("""
Foreign Key Relationships:
- subscriptions.vendor_id -> vendors.id
- subscriptions.org_id -> organizations.id
- license_allocations.subscription_id -> subscriptions.id
- license_allocations.user_id -> users.id
- users.dept_id -> departments.id
- invoices.subscription_id -> subscriptions.id
- usage_telemetry.subscription_id -> subscriptions.id
- optimization_recommendations.subscription_id -> subscriptions.id
""")

    schema_context_prompt = "\n".join(schema_prompt_lines)

    return {
        "resolved_tables": sorted(list(resolved_tables)),
        "resolved_columns": sorted(list(resolved_columns)),
        "ambiguities": ambiguities,
        "schema_context_prompt": schema_context_prompt
    }
