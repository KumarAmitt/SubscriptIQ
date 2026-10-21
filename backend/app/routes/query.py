from fastapi import APIRouter, HTTPException
from app.config import settings
from app.models.schemas import QueryRequest, QueryResponse
from app.engine.pipeline import process_natural_language_query, get_current_model_config
from app.database.connection import fetch_all, fetch_one

router = APIRouter(prefix="", tags=["Query & Dashboard"])

@router.post("/query", response_model=QueryResponse)
async def handle_query(payload: QueryRequest):
    """
    Executes the 7-stage Text-to-SQL Pipeline:
    NL Query -> Classifier -> Schema Linker -> Examples Retriever ->
    SQL Generator -> Validator -> Executor -> Formatter.
    """
    try:
        result = await process_natural_language_query(
            query=payload.query,
            selected_model=payload.model_id,
            user_role=payload.user_role,
            user_email=payload.user_email
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
async def get_models(user_role: str = "user"):
    """
    Returns available AI models.
    Supports user role filtering and indicates admin-enforced models.
    Only models permitted by the administrator are returned so clients cannot select unallowed models.
    """
    cfg = get_current_model_config()
    default_model = cfg.get("default_model", settings.DEFAULT_MODEL)
    admin_enforced = cfg.get("admin_enforced_model")
    allowed_for_users = cfg.get("allowed_models_for_users")

    if allowed_for_users is None or len(allowed_for_users) == 0:
        allowed_for_users = [m["id"] for m in settings.SUPPORTED_MODELS]

    # If admin enforced a specific model, only that model is permitted
    if admin_enforced:
        effective_allowed = [admin_enforced]
    else:
        effective_allowed = allowed_for_users

    all_models = settings.SUPPORTED_MODELS
    result_models = []

    for m in all_models:
        if m["id"] in effective_allowed:
            item = dict(m)
            item["is_default"] = (m["id"] == default_model)
            item["is_enforced"] = bool(admin_enforced or len(effective_allowed) == 1)
            item["disabled"] = False
            result_models.append(item)

    # Ensure default_model is among the allowed models; if not, pick the first allowed
    if result_models and not any(m["id"] == default_model for m in result_models):
        default_model = result_models[0]["id"]
        result_models[0]["is_default"] = True

    agent_connected = bool(settings.GROQ_API_KEY or settings.GEMINI_API_KEY)
    return {
        "models": result_models,
        "default_model": default_model,
        "admin_enforced_model": admin_enforced,
        "is_enforced_for_users": bool(admin_enforced or len(effective_allowed) == 1),
        "agent_connected": agent_connected,
        "connection_status": "connected" if agent_connected else "disconnected"
    }

@router.get("/dashboard/stats")
async def get_dashboard_stats():
    """
    Provides dynamic KPI metrics, live subscription list, and AI recommendations
    for the frontend Dashboard view.
    """
    try:
        # 1. Total monthly spend & subscription count
        spend_row = fetch_one(
            "SELECT COALESCE(SUM(monthly_cost), 0) AS total_spend, COUNT(*) AS active_count FROM subscriptions WHERE status = 'active';"
        )
        total_monthly_spend = float(spend_row["total_spend"])
        active_subs_count = int(spend_row["active_count"])

        # 2. Dormant seats count
        dormant_row = fetch_one(
            "SELECT COUNT(*) AS dormant_count FROM license_allocations WHERE is_dormant = TRUE;"
        )
        dormant_seats_count = int(dormant_row["dormant_count"])

        # 3. Renewals in next 14 days
        renewals_row = fetch_one(
            """
            SELECT COUNT(*) AS upcoming_count
            FROM subscriptions
            WHERE renewal_date >= CURRENT_DATE AND renewal_date <= CURRENT_DATE + INTERVAL '14 days';
            """
        )
        renewals_soon_count = int(renewals_row["upcoming_count"])

        # 4. Total optimization savings potential
        savings_row = fetch_one(
            "SELECT COALESCE(SUM(estimated_monthly_savings), 0) AS total_savings FROM optimization_recommendations WHERE status = 'detected';"
        )
        potential_savings = float(savings_row["total_savings"])

        # 5. Live subscriptions list
        subs = fetch_all(
            """
            SELECT 
                s.id, s.product_name AS name, s.category, s.billing_cycle,
                s.monthly_cost, s.annual_contract_value, s.total_seats_licensed AS "totalSeats",
                s.renewal_date, s.status, s.auto_renew,
                v.name AS vendor_name,
                COALESCE((SELECT COUNT(*) FROM license_allocations l WHERE l.subscription_id = s.id), 0) AS "activeSeats"
            FROM subscriptions s
            JOIN vendors v ON s.vendor_id = v.id
            ORDER BY s.monthly_cost DESC;
            """
        )

        formatted_subs = []
        for s in subs:
            total_seats = s["totalSeats"] or 1
            active_seats = min(s["activeSeats"], total_seats)
            utilization = round((active_seats / total_seats) * 100)
            
            # Abbreviation & color
            name_parts = s["name"].split()
            abbr = "".join(p[0] for p in name_parts[:2]).upper()
            colors = ["#6366f1", "#10b981", "#f59e0b", "#ec4899", "#38bdf8", "#8b5cf6"]
            color = colors[s["id"] % len(colors)]

            formatted_subs.append({
                "id": s["id"],
                "name": s["name"],
                "abbr": abbr,
                "color": color,
                "tier": f"{s['billing_cycle'].capitalize()} Contract",
                "category": s["category"],
                "activeSeats": active_seats,
                "totalSeats": total_seats,
                "utilization": utilization,
                "spend": f"{settings.CURRENCY_SYMBOL}{float(s['monthly_cost']):,.0f}/mo",
                "monthly_cost": float(s["monthly_cost"]),
                "annual_spend": float(s["annual_contract_value"]),
                "renewal": str(s["renewal_date"]),
                "status": s["status"]
            })

        # 6. Active optimization recommendations
        recs = fetch_all(
            """
            SELECT r.id, s.product_name, r.recommendation_type, r.description,
                   r.estimated_monthly_savings, r.confidence_score, r.status
            FROM optimization_recommendations r
            JOIN subscriptions s ON r.subscription_id = s.id
            WHERE r.status = 'detected'
            ORDER BY r.estimated_monthly_savings DESC
            LIMIT 5;
            """
        )

        return {
            "currency": settings.CURRENCY_CODE,
            "currency_symbol": settings.CURRENCY_SYMBOL,
            "metrics": {
                "total_monthly_spend": total_monthly_spend,
                "active_subscriptions": active_subs_count,
                "dormant_seats": dormant_seats_count,
                "renewals_in_14_days": renewals_soon_count,
                "projected_monthly_savings": potential_savings
            },
            "subscriptions": formatted_subs,
            "recommendations": recs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
