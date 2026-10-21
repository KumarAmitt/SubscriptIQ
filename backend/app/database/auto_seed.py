import psycopg2
from app.config import settings
from app.database.seed_db import run_seed

def ensure_database_seeded():
    """
    Checks if PostgreSQL has been initialized with schema and seed data.
    If tables are missing, automatically executes the DDL and seeds >1,000 enterprise rows.
    Ensures seamless one-command setup via Docker or local dev.
    """
    try:
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            dbname=settings.DB_NAME
        )
        cur = conn.cursor()
        cur.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'organizations');")
        table_exists = cur.fetchone()[0]

        if not table_exists:
            print("[Auto-Seed] Database schema missing. Initializing schema and seed data now...")
            conn.close()
            run_seed()
            print("[Auto-Seed] Database successfully initialized and seeded.")
        else:
            cur.execute("SELECT count(*) FROM organizations;")
            count = cur.fetchone()[0]
            if count == 0:
                print("[Auto-Seed] Organizations table empty. Seeding database now...")
                conn.close()
                run_seed()
                print("[Auto-Seed] Database successfully seeded.")
            else:
                print(f"[Auto-Seed] PostgreSQL database already seeded with {count} organizations.")
            conn.close()
    except Exception as e:
        print(f"[Auto-Seed] Notice: Could not auto-seed database: {e}")
