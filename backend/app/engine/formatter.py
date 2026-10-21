from app.config import settings

def generate_natural_language_summary(
    query: str,
    columns: list[str],
    rows: list[dict],
    row_count: int,
    explanation: str | None = None
) -> str:
    """
    Step 7a: Natural Language Summary Synthesizer
    Produces a crisp, 1-2 sentence executive summary of the query results.
    """
    if row_count == 0:
        return f"No records found matching your query: '{query}'."

    first_row = rows[0]
    sym = settings.CURRENCY_SYMBOL
    
    # 1. Single aggregate value (e.g. SUM or COUNT)
    if row_count == 1:
        metrics = []
        for col, raw_val in first_row.items():
            if raw_val is not None:
                try:
                    num_val = float(raw_val)
                    if "spend" in col.lower() or "cost" in col.lower() or "amount" in col.lower() or "savings" in col.lower() or "acv" in col.lower() or "budget" in col.lower():
                        metrics.append(f"{col.replace('_', ' ')} is {sym}{num_val:,.2f}")
                    elif num_val.is_integer():
                        metrics.append(f"{col.replace('_', ' ')} is {int(num_val):,}")
                    else:
                        metrics.append(f"{col.replace('_', ' ')} is {num_val:,.2f}")
                except (ValueError, TypeError):
                    metrics.append(f"{col.replace('_', ' ')} is '{raw_val}'")
        return f"Query returned 1 summary record: " + ", ".join(metrics) + "."

    # 2. Ranking or top list
    if "top" in query.lower() or "order by" in str(explanation).lower() or "highest" in query.lower():
        name_key = next((k for k in ["product_name", "category", "name", "full_name", "vendor_name"] if k in first_row), None)
        val_key = next((k for k in ["monthly_cost", "total_monthly_spend", "amount", "budget_annual", "annual_contract_value", "total_acv"] if k in first_row), None)
        
        if name_key and val_key:
            lead_item = first_row.get(name_key)
            raw_lead_val = first_row.get(val_key)
            try:
                num_lead = float(raw_lead_val)
                lead_val_str = f"{sym}{num_lead:,.2f}"
            except (ValueError, TypeError):
                lead_val_str = str(raw_lead_val)
            return f"Found {row_count} records. Top ranked is **{lead_item}** with {val_key.replace('_', ' ')} of **{lead_val_str}**."

    # 3. Renewals / temporal queries
    if any(w in query.lower() for w in ["renew", "renewal", "upcoming"]):
        tool_names = [r.get("product_name") for r in rows[:3] if r.get("product_name")]
        tools_str = ", ".join(tool_names) if tool_names else f"{row_count} tools"
        return f"Identified **{row_count} subscriptions** approaching renewal within the designated window (including {tools_str})."

    # 4. Inactive or dormant seats
    if any(w in query.lower() for w in ["dormant", "inactive", "unused"]):
        return f"Detected **{row_count} dormant seat allocations** with no recorded login activity in the designated monitoring timeframe."

    # General multi-row summary
    return f"Retrieved **{row_count} records** answering your query. Results are displayed in the interactive table below."

def is_identifier_column(col: str) -> bool:
    """Returns True if column represents a database ID or key rather than a business metric."""
    c = col.lower().strip()
    return c == "id" or c.endswith("_id") or c.startswith("id_") or c.endswith("_code") or c in {"pk", "fk"}

def detect_chart_data(columns: list[str], rows: list[dict]) -> dict | None:
    """
    Step 7b: Meaningful Business Chart Auto-generation.
    Prioritizes real financial metrics (spend, cost, savings) and operational metrics (seats, utilization).
    STRICTLY ignores database primary/foreign keys (id, user_id, etc.).
    """
    if not rows or len(rows) > 20 or len(columns) < 2:
        return None

    # Special Handler for Single-Subscription Queries (Recommendations & Cost Impact or Seat Breakdown)
    if len(rows) == 1:
        r = rows[0]
        prod_name = r.get("product_name") or "Subscription"

        # 1. Cost Optimization & Recommendation Impact (Doughnut / Pie Chart)
        if "estimated_monthly_savings" in r or "estimated_annual_savings" in r:
            monthly_cost = float(r.get("monthly_cost") or 0)
            annual_cost = float(r.get("annual_contract_value") or (monthly_cost * 12))
            monthly_savings = float(r.get("estimated_monthly_savings") or 0)
            annual_savings = float(r.get("estimated_annual_savings") or (monthly_savings * 12))

            # If cost fields were omitted from query columns, enrich from subscriptions table
            if (monthly_cost == 0 or annual_cost == 0) and prod_name and prod_name != "Subscription":
                try:
                    from app.database.connection import execute_readonly_sql
                    sub_res = execute_readonly_sql(
                        "SELECT monthly_cost, annual_contract_value FROM subscriptions WHERE product_name ILIKE %s LIMIT 1",
                        (f"%{prod_name}%",)
                    )
                    if sub_res.get("rows"):
                        s_row = sub_res["rows"][0]
                        if monthly_cost == 0:
                            monthly_cost = float(s_row.get("monthly_cost") or 0)
                        if annual_cost == 0:
                            annual_cost = float(s_row.get("annual_contract_value") or (monthly_cost * 12))
                except Exception:
                    pass

            if annual_savings > 0 and annual_cost > 0:
                return {
                    "type": "doughnut",
                    "title": f"Annual Cost Impact & Optimization Savings ({prod_name})",
                    "label_column": "financial_metric",
                    "value_column": "amount",
                    "labels": ["Current Annual Contract", "Projected Annual Savings"],
                    "values": [round(annual_cost, 2), round(annual_savings, 2)]
                }
            elif monthly_savings > 0:
                cost_val = monthly_cost if monthly_cost > 0 else monthly_savings
                return {
                    "type": "doughnut",
                    "title": f"Monthly Cost vs. Projected Savings ({prod_name})",
                    "label_column": "financial_metric",
                    "value_column": "amount",
                    "labels": ["Current Monthly Cost", "Projected Monthly Savings"],
                    "values": [round(cost_val, 2), round(monthly_savings, 2)]
                }

        # 2. Seat Allocation & Optimization Breakdown
        if "total_seats_licensed" in r and ("assigned_users_count" in r or "dormant_seats" in r):
            total_seats = int(r.get("total_seats_licensed") or 0)
            assigned_users = int(r.get("assigned_users_count") or 0)
            dormant = int(r.get("dormant_seats") or 0)
            unallocated = int(r.get("unallocated_seats") if r.get("unallocated_seats") is not None else max(0, total_seats - assigned_users))
            active_users = max(0, assigned_users - dormant)
            
            return {
                "type": "doughnut",
                "title": f"Seat Allocation & Optimization Breakdown ({prod_name})",
                "label_column": "allocation_type",
                "value_column": "seat_count",
                "labels": ["Active In-Use Seats", "Dormant Inactive Seats", "Unallocated Idle Seats"],
                "values": [float(active_users), float(dormant), float(unallocated)]
            }
        return None

    # 1. Select the most descriptive label column (product_name, category, department, vendor, etc.)
    label_candidates = [
        "product_name", "category", "department", "department_name", "vendor", "vendor_name",
        "name", "full_name", "role", "payment_method", "seat_type", "status"
    ]
    label_col = None
    for cand in label_candidates:
        if cand in columns:
            label_col = cand
            break

    if not label_col:
        for col in columns:
            if is_identifier_column(col) or col.endswith("_date") or "date" in col.lower():
                continue
            sample_val = rows[0].get(col)
            if isinstance(sample_val, str):
                label_col = col
                break

    # 2. Select the most meaningful numeric metric
    # Priority A: Financial / Spend Metrics
    financial_candidates = [
        "monthly_cost", "annual_contract_value", "amount", "budget_annual",
        "estimated_monthly_savings", "total_monthly_spend", "total_acv", "total_billed_amount"
    ]
    value_col = None
    for cand in financial_candidates:
        if cand in columns and not is_identifier_column(cand):
            value_col = cand
            break

    # Priority B: Operational / Utilization Metrics
    if not value_col:
        operational_candidates = [
            "total_seats_licensed", "active_users_day", "utilization_rate",
            "total_assigned_licenses", "tools_count", "user_count", "head_count",
            "days_inactive", "days_overdue", "storage_used_gb", "api_calls_count"
        ]
        for cand in operational_candidates:
            if cand in columns and not is_identifier_column(cand):
                value_col = cand
                break

    # Priority C: Fallback to any numeric column that is NOT an ID or date
    if not value_col:
        for col in columns:
            if col == label_col or is_identifier_column(col) or "date" in col.lower():
                continue
            sample = rows[0].get(col)
            try:
                if sample is not None and not isinstance(sample, bool):
                    float(sample)
                    value_col = col
                    break
            except (ValueError, TypeError):
                continue

    # If no meaningful metric exists, do NOT generate a chart based on IDs or arbitrary columns
    if not label_col or not value_col:
        return None

    labels = [str(r.get(label_col, "")) for r in rows]
    try:
        values = [float(r.get(value_col, 0) or 0) for r in rows]
    except (ValueError, TypeError):
        return None

    chart_type = "doughnut" if len(labels) <= 6 else "bar"
    if any("trend" in c or "date" in c for c in columns):
        chart_type = "line"

    return {
        "type": chart_type,
        "title": f"{value_col.replace('_', ' ').title()} by {label_col.replace('_', ' ').title()}",
        "label_column": label_col,
        "value_column": value_col,
        "labels": labels,
        "values": values
    }

def format_result(
    query: str,
    sql: str,
    exec_result: dict,
    explanation: str | None = None
) -> dict:
    """
    Step 7: Result Formatter
    Combines tabular data, executive summary, and auto-generated chart data.
    """
    columns = exec_result.get("columns", [])
    rows = exec_result.get("rows", [])
    row_count = exec_result.get("row_count", 0)
    latency_ms = exec_result.get("latency_ms", 0.0)
    error = exec_result.get("error")

    if error:
        return {
            "success": False,
            "columns": [],
            "rows": [],
            "row_count": 0,
            "latency_ms": latency_ms,
            "nl_summary": f"Query execution failed: {error}",
            "chart": None,
            "error": error
        }

    nl_summary = generate_natural_language_summary(query, columns, rows, row_count, explanation)
    chart = detect_chart_data(columns, rows)

    return {
        "success": True,
        "columns": columns,
        "rows": rows,
        "row_count": row_count,
        "latency_ms": latency_ms,
        "nl_summary": nl_summary,
        "chart": chart,
        "error": None
    }
