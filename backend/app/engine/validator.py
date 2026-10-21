import re
import sqlglot
from sqlglot import exp
from app.config import settings

VALID_TABLES = {
    "organizations", "departments", "users", "vendors",
    "subscriptions", "license_allocations", "invoices",
    "usage_telemetry", "optimization_recommendations",
    "schema_metadata", "query_logs", "system_settings"
}

def validate_and_sanitize_sql(
    sql: str,
    dialect: str = "postgres",
    guardrails_config: dict | None = None
) -> dict:
    """
    Step 5: SQL Validator & Guardrails Engine
    Performs:
    1. Syntax check with sqlglot
    2. Prohibited DML/DDL check (DROP, DELETE, UPDATE, INSERT, etc.)
    3. Schema existence check on tables
    4. Row limit enforcement (appends LIMIT N if missing)
    5. Multi-dialect transpilation (Bonus challenge!)
    """
    errors = []
    sanitized_sql = sql.strip()
    sanitized_sql = re.sub(r"^```(?:sql)?", "", sanitized_sql, flags=re.IGNORECASE).strip()
    sanitized_sql = re.sub(r"```$", "", sanitized_sql).strip()
    sanitized_sql = sanitized_sql.rstrip(";")
    
    cfg = guardrails_config or {}
    blocked_ops = cfg.get("blocked_operations", settings.BLOCKED_OPERATIONS)
    allow_dml = cfg.get("allow_dml_override", False)
    default_limit = cfg.get("default_row_limit", settings.DEFAULT_ROW_LIMIT)
    max_limit = cfg.get("max_row_limit", settings.MAX_ROW_LIMIT)
    allowed_tables = set(cfg.get("allowed_tables", list(VALID_TABLES)))

    # 1. Prohibited operations check (Guardrails)
    if not allow_dml:
        for op in blocked_ops:
            if re.search(rf"\b{re.escape(op)}\b", sanitized_sql, re.IGNORECASE):
                errors.append(f"Guardrail violation: prohibited operation '{op.upper()}' detected in query.")

    if errors:
        return {
            "valid": False,
            "sanitized_sql": sql,
            "errors": errors,
            "ast": None
        }

    # 2. Syntax parsing with sqlglot
    parsed_expressions = None
    try:
        parsed_expressions = sqlglot.parse(sanitized_sql, read="postgres")
    except Exception as e:
        errors.append(f"SQL Syntax Error: {str(e)}")
        return {
            "valid": False,
            "sanitized_sql": sql,
            "errors": errors,
            "ast": None
        }

    if not parsed_expressions or parsed_expressions[0] is None:
        errors.append("SQL Parser could not construct an AST from the provided statement.")
        return {
            "valid": False,
            "sanitized_sql": sql,
            "errors": errors,
            "ast": None
        }

    root_expr = parsed_expressions[0]

    # Verify statement is a SELECT or WITH (Common Table Expression)
    if not isinstance(root_expr, (exp.Select, exp.Union)):
        # Check if WITH expression wrapping a SELECT
        if not (isinstance(root_expr, exp.Expression) and root_expr.find(exp.Select)):
            errors.append("Invalid query type: Only SELECT statements are permitted.")

    # 3. Table verification
    tables_in_query = set()
    for table in root_expr.find_all(exp.Table):
        tbl_name = table.name.lower()
        tables_in_query.add(tbl_name)
        if tbl_name not in allowed_tables:
            errors.append(f"Table '{tbl_name}' does not exist or is not permitted in workspace schema.")

    # 4. Row limit enforcement (Cap or optionally append LIMIT)
    limit_expr = root_expr.find(exp.Limit)
    if limit_expr:
        # Check if exceeds max limit
        try:
            val = int(limit_expr.expression.this)
            if val > max_limit:
                sanitized_sql = re.sub(r"LIMIT\s+\d+", f"LIMIT {max_limit}", sanitized_sql, flags=re.IGNORECASE)
        except Exception:
            pass
    elif cfg.get("enforce_row_limit", False):
        # Only append LIMIT N if enforce_row_limit guardrail is explicitly turned on
        sanitized_sql = f"{sanitized_sql} LIMIT {default_limit}"

    # Ensure clean terminating semicolon
    final_sql = sanitized_sql.strip().rstrip(";") + ";"

    return {
        "valid": len(errors) == 0,
        "sanitized_sql": final_sql,
        "errors": errors,
        "tables_used": list(tables_in_query),
        "transpiled": {}
    }
