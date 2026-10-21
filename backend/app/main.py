from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database.connection import get_connection_pool
from app.vector_store.qdrant_store import init_vector_store
from app.routes.query import router as query_router
from app.routes.admin_schema import router as admin_schema_router
from app.routes.admin_examples import router as admin_examples_router
from app.routes.admin_logs import router as admin_logs_router
from app.routes.admin_guardrails import router as admin_guardrails_router
from app.routes.admin_config import router as admin_config_router
from app.routes.eval import router as eval_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB pool & Qdrant vector store
    print("Initializing SubscriptIQ Backend...")
    try:
        pool = get_connection_pool()
        print(f"Connected to PostgreSQL ({settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME})")
        from app.database.auto_seed import ensure_database_seeded
        ensure_database_seeded()
        from app.engine.pipeline import get_current_model_config
        get_current_model_config()
    except Exception as e:
        print(f"PostgreSQL connection warning: {e}")

    try:
        init_vector_store()
        print("Qdrant vector store initialized.")
    except Exception as e:
        print(f"Qdrant init warning: {e}")

    yield

    # Shutdown
    print("Shutting down SubscriptIQ Backend...")
    try:
        p = get_connection_pool()
        p.closeall()
    except Exception:
        pass

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Text-to-SQL Analytics Engine with Admin UI and Qdrant Vector Retrieval",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In development allow all or localhost:5173
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import Depends
from app.auth import require_admin
from app.routes.auth_routes import router as auth_router

# Register API Routers under /api
app.include_router(auth_router, prefix="/api")
app.include_router(query_router, prefix="/api")

# Admin Routers Protected with require_admin
app.include_router(admin_schema_router, prefix="/api", dependencies=[Depends(require_admin)])
app.include_router(admin_examples_router, prefix="/api", dependencies=[Depends(require_admin)])
app.include_router(admin_logs_router, prefix="/api", dependencies=[Depends(require_admin)])
app.include_router(admin_guardrails_router, prefix="/api", dependencies=[Depends(require_admin)])
app.include_router(admin_config_router, prefix="/api", dependencies=[Depends(require_admin)])
app.include_router(eval_router, prefix="/api", dependencies=[Depends(require_admin)])

@app.get("/api/health")
async def healthcheck():
    return {
        "status": "healthy",
        "service": "SubscriptIQ Text-to-SQL Engine",
        "database": f"PostgreSQL ({settings.DB_HOST}:{settings.DB_PORT})",
        "vector_store": "Qdrant",
        "models_supported": [m["name"] for m in settings.SUPPORTED_MODELS]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
