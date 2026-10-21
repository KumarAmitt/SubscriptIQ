import random
import datetime
import json
from pathlib import Path
import psycopg2
import psycopg2.extras
from app.config import settings

def run_seed():
    print(f"Connecting to PostgreSQL at {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}...")
    conn = psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        dbname=settings.DB_NAME
    )
    conn.autocommit = False
    cur = conn.cursor()

    # 1. Execute DDL script
    ddl_file = Path(__file__).parent / "schema_ddl.sql"
    print(f"Applying schema DDL from {ddl_file}...")
    with open(ddl_file, "r") as f:
        ddl_sql = f.read()
    cur.execute(ddl_sql)
    conn.commit()
    print("Schema DDL applied successfully.")

    random.seed(42)

    # 2. Seed Organizations
    print("Seeding organizations...")
    orgs_data = [
        ("SubscriptIQ Global Corp", "subscriptiq.ai", "Enterprise Technology", 1450, "Enterprise"),
        ("Acme Cloud Systems", "acmecloud.io", "Cloud Infrastructure", 620, "Enterprise"),
        ("FinFlow Capital", "finflow.com", "Financial Services", 890, "Enterprise"),
        ("NovaHealth Medical", "novahealth.org", "Healthcare Logistics", 1120, "Enterprise"),
    ]
    cur.executemany(
        """
        INSERT INTO organizations (name, domain, industry, employee_count, tier)
        VALUES (%s, %s, %s, %s, %s)
        """,
        orgs_data
    )
    conn.commit()

    # 3. Seed Departments
    print("Seeding departments...")
    depts = [
        (1, "Engineering", 1250000.00, "CC-ENG-101", 380),
        (1, "Product & Design", 450000.00, "CC-PRD-102", 120),
        (1, "Data Science & AI", 680000.00, "CC-DAT-103", 95),
        (1, "Sales & Growth", 750000.00, "CC-SLS-104", 240),
        (1, "Marketing", 320000.00, "CC-MKT-105", 85),
        (1, "Operations & Security", 540000.00, "CC-OPS-106", 110),
        (1, "Finance & Legal", 280000.00, "CC-FIN-107", 50),
        (1, "Customer Experience", 390000.00, "CC-CSX-108", 150),
    ]
    cur.executemany(
        """
        INSERT INTO departments (org_id, name, budget_annual, cost_center_code, head_count)
        VALUES (%s, %s, %s, %s, %s)
        """,
        depts
    )
    conn.commit()

    # 4. Seed Vendors
    print("Seeding vendors...")
    vendors_data = [
        ("GitHub", "https://github.com", "Enterprise 24/7 Gold", "SOC2 Type II, ISO27001, FedRAMP"),
        ("Figma", "https://figma.com", "Enterprise Dedicated", "SOC2 Type II, ISO27001"),
        ("Slack Technologies", "https://slack.com", "Enterprise Grid Support", "SOC2 Type II, HIPAA, ISO27001"),
        ("Notion Labs", "https://notion.so", "Priority Support", "SOC2 Type II, GDPR"),
        ("Datadog", "https://datadoghq.com", "Premier Technical Account Manager", "SOC2 Type II, FedRAMP"),
        ("Amazon Web Services", "https://aws.amazon.com", "Enterprise Support", "SOC2, ISO27001, FedRAMP High"),
        ("Zoom Video Communications", "https://zoom.us", "Business Premier", "SOC2 Type II, HIPAA"),
        ("Salesforce", "https://salesforce.com", "Signature Success", "SOC2 Type II, ISO27001"),
        ("Atlassian", "https://atlassian.com", "Enterprise Advisory", "SOC2 Type II, ISO27001"),
        ("HubSpot", "https://hubspot.com", "Enterprise Tier", "SOC2 Type II"),
        ("Linear", "https://linear.app", "Standard Team", "SOC2 Type II"),
        ("OpenAI Enterprise", "https://openai.com", "Enterprise Advisory Support", "SOC2 Type II, HIPAA"),
        ("Snowflake", "https://snowflake.com", "Mission Critical Support", "SOC2 Type II, HIPAA, FedRAMP"),
        ("Workday", "https://workday.com", "Platinum Support", "SOC2 Type II, ISO27001"),
    ]
    cur.executemany(
        """
        INSERT INTO vendors (name, website, support_tier, security_compliance)
        VALUES (%s, %s, %s, %s)
        """,
        vendors_data
    )
    conn.commit()

    # 5. Seed Subscriptions (Master Contracts)
    print("Seeding subscriptions...")
    # Reference date is early 2026/current
    today = datetime.date(2026, 10, 20)
    subs_info = [
        (1, 1, "GitHub Enterprise Cloud", "Engineering", "annual", 4200.00, 50400.00, 200, today - datetime.timedelta(days=320), today + datetime.timedelta(days=45), True, "active"),
        (1, 2, "Figma Organization Tier", "Design", "annual", 2400.00, 28800.00, 80, today - datetime.timedelta(days=340), today + datetime.timedelta(days=25), True, "under_review"),
        (1, 3, "Slack Enterprise Grid", "Communication", "annual", 5100.00, 61200.00, 350, today - datetime.timedelta(days=200), today + datetime.timedelta(days=165), True, "active"),
        (1, 4, "Notion Business & AI", "Productivity", "monthly", 1850.00, 22200.00, 180, today - datetime.timedelta(days=150), today + datetime.timedelta(days=12), True, "active"),
        (1, 5, "Datadog Infrastructure & APM", "DevOps", "monthly", 8400.00, 100800.00, 50, today - datetime.timedelta(days=400), today + datetime.timedelta(days=8), True, "under_review"),
        (1, 6, "AWS Compute & RDS Suite", "Cloud Infrastructure", "monthly", 18500.00, 222000.00, 120, today - datetime.timedelta(days=700), today + datetime.timedelta(days=30), True, "active"),
        (1, 7, "Zoom One Enterprise", "Communication", "annual", 1950.00, 23400.00, 150, today - datetime.timedelta(days=310), today + datetime.timedelta(days=55), True, "active"),
        (1, 8, "Salesforce Sales Cloud Unlimited", "Sales", "annual", 12400.00, 148800.00, 80, today - datetime.timedelta(days=180), today + datetime.timedelta(days=185), True, "active"),
        (1, 9, "Atlassian Jira & Confluence Cloud", "Engineering", "annual", 3900.00, 46800.00, 250, today - datetime.timedelta(days=300), today + datetime.timedelta(days=65), True, "active"),
        (1, 10, "HubSpot Marketing Hub Enterprise", "Marketing", "annual", 3200.00, 38400.00, 40, today - datetime.timedelta(days=250), today + datetime.timedelta(days=115), True, "active"),
        (1, 11, "Linear Team Premium", "Engineering", "monthly", 950.00, 11400.00, 100, today - datetime.timedelta(days=120), today + datetime.timedelta(days=18), True, "active"),
        (1, 12, "OpenAI API Enterprise Tier", "Data Science & AI", "monthly", 6800.00, 81600.00, 60, today - datetime.timedelta(days=90), today + datetime.timedelta(days=22), True, "active"),
        (1, 13, "Snowflake Enterprise Data Warehouse", "Data Science & AI", "annual", 9500.00, 114000.00, 75, today - datetime.timedelta(days=290), today + datetime.timedelta(days=75), True, "active"),
        (1, 14, "Workday Human Capital Management", "Operations & Security", "annual", 7200.00, 86400.00, 1200, today - datetime.timedelta(days=350), today + datetime.timedelta(days=15), True, "active"),
    ]
    cur.executemany(
        """
        INSERT INTO subscriptions (
            org_id, vendor_id, product_name, category, billing_cycle,
            monthly_cost, annual_contract_value, total_seats_licensed,
            start_date, renewal_date, auto_renew, status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        subs_info
    )
    conn.commit()

    # 6. Seed Users (>= 1,000 rows requirement)
    print("Seeding 1,200 users...")
    first_names = [
        "Alex", "Sarah", "Michael", "Emily", "David", "Jessica", "James", "Emma",
        "Daniel", "Olivia", "Matthew", "Sophia", "Andrew", "Isabella", "Joshua",
        "Ava", "Christopher", "Mia", "Joseph", "Charlotte", "Ethan", "Amelia",
        "Liam", "Harper", "Noah", "Evelyn", "Lucas", "Abigail", "Mason", "Elena",
        "Marcus", "Priya", "Chen", "Kenji", "Fatima", "Carlos", "Aisha", "Mateo"
    ]
    last_names = [
        "Rivera", "Chen", "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller",
        "Davis", "Wilson", "Anderson", "Taylor", "Thomas", "Moore", "Jackson", "Martin",
        "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez",
        "Lewis", "Robinson", "Walker", "Young", "Allen", "King", "Wright", "Scott"
    ]
    roles = ["Software Engineer", "Senior Architect", "Product Manager", "Data Analyst",
             "UX Designer", "DevOps Specialist", "Account Executive", "Marketing Lead",
             "Security Analyst", "Financial Analyst", "Support Specialist"]

    users_batch = []
    for i in range(1, 1201):
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        email = f"{fn.lower()}.{ln.lower()}{i}@subscriptiq.ai"
        full_name = f"{fn} {ln}"
        dept_id = random.randint(1, 8)
        role = random.choice(roles)
        is_active = random.random() > 0.05
        users_batch.append((1, dept_id, email, full_name, role, is_active))

    cur.executemany(
        """
        INSERT INTO users (org_id, dept_id, email, full_name, role, is_active)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        users_batch
    )
    conn.commit()

    # 7. Seed License Allocations (>= 1,000 rows requirement)
    print("Seeding license allocations (aligned with subscription seat capacity)...")
    allocations_batch = []
    seat_types = ["Full License", "Admin", "Viewer", "Guest"]
    
    # Target allocations per subscription (HubSpot has exactly 40 seats matching licensed capacity)
    sub_alloc_targets = {
        1: 185,   # GitHub Enterprise Cloud: 200 licensed
        2: 75,    # Figma Organization Tier: 80 licensed
        3: 320,   # Slack Enterprise Grid: 350 licensed
        4: 165,   # Notion Business & AI: 180 licensed
        5: 45,    # Datadog Infrastructure & APM: 50 licensed
        6: 110,   # AWS Compute & RDS Suite: 120 licensed
        7: 135,   # Zoom One Enterprise: 150 licensed
        8: 80,    # Salesforce Sales Cloud Unlimited: 80 licensed
        9: 220,   # Atlassian Jira & Confluence Cloud: 250 licensed
        10: 40,   # HubSpot Marketing Hub Enterprise: exactly 40 licensed!
        11: 90,   # Linear Team Premium: 100 licensed
        12: 55,   # OpenAI API Enterprise Tier: 60 licensed
        13: 70,   # Snowflake Enterprise Data Warehouse: 75 licensed
        14: 390,  # Workday Human Capital Management: 1200 licensed
    }
    
    for sub_id, count in sub_alloc_targets.items():
        sub_users = random.sample(range(1, 1201), count)
        for user_id in sub_users:
            seat_type = random.choice(seat_types)
            assigned_offset = random.randint(30, 360)
            assigned_date = today - datetime.timedelta(days=assigned_offset)
            
            # ~18% dormant seats (inactive > 30 days)
            is_dormant = random.random() < 0.18
            if is_dormant:
                inactivity_days = random.randint(35, 180)
            else:
                inactivity_days = random.randint(1, 20)
            last_activity_date = today - datetime.timedelta(days=inactivity_days)
            
            allocations_batch.append((sub_id, user_id, seat_type, assigned_date, last_activity_date, is_dormant))

    cur.executemany(
        """
        INSERT INTO license_allocations (
            subscription_id, user_id, seat_type, assigned_date, last_activity_date, is_dormant
        ) VALUES (%s, %s, %s, %s, %s, %s)
        """,
        allocations_batch
    )
    conn.commit()

    # 8. Seed Invoices (>= 1,000 rows requirement)
    print("Seeding 1,200 invoices...")
    invoices_batch = []
    payment_methods = ["Amex Corporate 8921", "Brex Virtual 4102", "Stripe ACH Transfer", "Silicon Valley Bank Wire"]
    payment_statuses = ["paid", "paid", "paid", "paid", "pending", "overdue"]

    for i in range(1, 1201):
        sub_id = random.randint(1, 14)
        inv_num = f"INV-2026-{10000 + i}"
        days_ago = random.randint(5, 720)
        inv_date = today - datetime.timedelta(days=days_ago)
        due_date = inv_date + datetime.timedelta(days=30)
        
        base_amount = random.choice([950.00, 1850.00, 2400.00, 3200.00, 4200.00, 5100.00, 6800.00, 8400.00, 12400.00, 18500.00])
        variance = round(random.uniform(-50.0, 120.0), 2)
        amount = round(base_amount + variance, 2)
        tax_amount = round(amount * 0.0825, 2)
        status = random.choice(payment_statuses) if days_ago < 45 else "paid"
        method = random.choice(payment_methods)
        
        invoices_batch.append((sub_id, inv_num, inv_date, due_date, amount, tax_amount, status, method))

    cur.executemany(
        """
        INSERT INTO invoices (
            subscription_id, invoice_number, invoice_date, due_date,
            amount, tax_amount, payment_status, payment_method
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        invoices_batch
    )
    conn.commit()

    # 9. Seed Usage Telemetry (>= 1,000 rows requirement)
    print("Seeding 1,000 usage telemetry data points...")
    telemetry_batch = []
    for i in range(1, 1001):
        sub_id = random.randint(1, 14)
        days_ago = random.randint(1, 365)
        rec_date = today - datetime.timedelta(days=days_ago)
        active_users = random.randint(15, 280)
        util_rate = round(random.uniform(42.0, 98.5), 2)
        storage_gb = round(random.uniform(20.0, 4500.0), 2)
        api_calls = random.randint(1200, 850000)
        
        telemetry_batch.append((sub_id, rec_date, active_users, util_rate, storage_gb, api_calls))

    cur.executemany(
        """
        INSERT INTO usage_telemetry (
            subscription_id, record_date, active_users_day,
            utilization_rate, storage_used_gb, api_calls_count
        ) VALUES (%s, %s, %s, %s, %s, %s)
        """,
        telemetry_batch
    )
    conn.commit()

    # 10. Seed Optimization Recommendations
    print("Seeding optimization recommendations...")
    recs = [
        (2, "dormant_seats_removal", "12 Figma seats have zero activity in 45 days. Reclaiming inactive seats saves ₹28,000/month.", 28000.00, 0.96, "detected"),
        (4, "dormant_seats_removal", "18 Notion Business seats unused for over 60 days. Downgrade seats to Viewer tier.", 15000.00, 0.92, "detected"),
        (5, "tier_downgrade", "Datadog log retention can be adjusted from 60 days to 30 days without violating audit compliance.", 70000.00, 0.88, "reviewing"),
        (3, "annual_switch_discount", "Slack contract renewal in 165 days qualifies for a 15% multi-year enterprise discount.", 62000.00, 0.91, "detected"),
        (6, "overlap_consolidation", "Consolidate unused dev cluster EC2 instances on AWS to Graviton savings plans.", 115000.00, 0.95, "detected"),
        (1, "dormant_seats_removal", "6 GitHub Enterprise seats unassigned since offboarding. Reallocate to incoming cohort.", 10500.00, 0.98, "applied"),
    ]
    cur.executemany(
        """
        INSERT INTO optimization_recommendations (
            subscription_id, recommendation_type, description,
            estimated_monthly_savings, confidence_score, status
        ) VALUES (%s, %s, %s, %s, %s, %s)
        """,
        recs
    )
    conn.commit()

    # 11. Seed Schema Metadata (for Schema Manager in Admin UI)
    print("Seeding schema metadata dictionary...")
    schema_dict = [
        # organizations
        ("organizations", "id", "INTEGER", "Unique identifier for corporate organization", False, "org_id, company_id"),
        ("organizations", "name", "VARCHAR", "Legal name of the enterprise company", False, "company_name, org_name"),
        ("organizations", "tier", "VARCHAR", "Corporate support and licensing tier", False, "plan_level, account_type"),
        
        # departments
        ("departments", "name", "VARCHAR", "Department name (Engineering, Design, Sales, etc.)", False, "dept, division, team"),
        ("departments", "budget_annual", "NUMERIC", "Annual allocated budget in INR (₹) for this department", False, "budget, allocated_spend"),
        
        # users
        ("users", "full_name", "VARCHAR", "Employee first and last name", False, "name, employee_name"),
        ("users", "email", "VARCHAR", "Corporate work email address (confidential PII)", True, "work_email, login"),
        ("users", "role", "VARCHAR", "Job title and organizational role", False, "title, job_function"),
        ("users", "is_active", "BOOLEAN", "Whether the employee account is active or departed", False, "status, enabled"),
        
        # vendors
        ("vendors", "name", "VARCHAR", "Name of the software vendor or provider", False, "vendor, supplier, provider"),
        ("vendors", "website", "VARCHAR", "Official URL of the vendor", False, "url, domain"),
        
        # subscriptions
        ("subscriptions", "product_name", "VARCHAR", "Name of the SaaS subscription or application", False, "tool, software, service, app"),
        ("subscriptions", "category", "VARCHAR", "Software category (Engineering, Communication, etc.)", False, "type, group, domain"),
        ("subscriptions", "monthly_cost", "NUMERIC", "Standard recurring monthly cost in INR (₹). (Note: for annual contracts, check annual_contract_value)", False, "monthly_spend, monthly_price, cost_per_month"),
        ("subscriptions", "annual_contract_value", "NUMERIC", "Total committed annual contract value (ACV) in INR (₹)", False, "acv, annual_spend, yearly_cost, total_contract_value"),
        ("subscriptions", "total_seats_licensed", "INTEGER", "Total number of purchased license seats", False, "seat_count, total_licenses, capacity"),
        ("subscriptions", "renewal_date", "DATE", "Upcoming contract renewal date", False, "renew_date, expiration_date, contract_end"),
        ("subscriptions", "status", "VARCHAR", "Contract status: active, under_review, pending_downgrade, canceled", False, "state, contract_status"),
        
        # license_allocations
        ("license_allocations", "seat_type", "VARCHAR", "Type of seat allocated: Full License, Admin, Viewer, Guest", False, "tier, license_type"),
        ("license_allocations", "last_activity_date", "DATE", "Date of user's most recent login or activity in the software", False, "last_login, last_used, recent_activity"),
        ("license_allocations", "is_dormant", "BOOLEAN", "True if user has not logged in for over 45 days", False, "inactive, unused, idle"),
        
        # invoices
        ("invoices", "amount", "NUMERIC", "Total invoiced charge in INR (₹). (Note: may include taxes or one-off setup fees)", False, "invoice_total, billed_amount, payment"),
        ("invoices", "payment_status", "VARCHAR", "Status of invoice: paid, pending, overdue, disputed", False, "status, paid_flag"),
        ("invoices", "invoice_date", "DATE", "Date invoice was issued by vendor", False, "bill_date, charge_date"),
        ("invoices", "payment_method", "VARCHAR", "Corporate credit card or payment channel used", True, "credit_card, billing_method"),
        
        # usage_telemetry
        ("usage_telemetry", "utilization_rate", "NUMERIC", "Percentage of licensed seats actively used (0.0 to 100.0%)", False, "utilization, seat_usage_pct, adoption_rate"),
        ("usage_telemetry", "active_users_day", "INTEGER", "Number of unique daily active users", False, "dau, active_users"),
        
        # optimization_recommendations
        ("optimization_recommendations", "estimated_monthly_savings", "NUMERIC", "Projected monthly savings in INR (₹) from optimization", False, "savings, reclaim_amount, cost_reduction"),
        ("optimization_recommendations", "confidence_score", "NUMERIC", "AI confidence score from 0.00 to 1.00", False, "confidence, certainty")
    ]
    cur.executemany(
        """
        INSERT INTO schema_metadata (table_name, column_name, data_type, description, is_sensitive, synonyms)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (table_name, column_name) DO UPDATE SET
            description = EXCLUDED.description,
            is_sensitive = EXCLUDED.is_sensitive,
            synonyms = EXCLUDED.synonyms,
            updated_at = CURRENT_TIMESTAMP
        """,
        schema_dict
    )
    conn.commit()

    # 12. Seed Default System Settings
    print("Seeding initial system settings...")
    initial_settings = [
        ("model_config", {
            "default_model": "openai/gpt-oss-120b",
            "allowed_models_for_users": [
                "openai/gpt-oss-120b",
                "openai/gpt-oss-20b",
                "gemini-3.1-flash-lite",
                "gemma-4-26b-a4b-it"
            ],
            "admin_enforced_model": None, # If set, overrides user choice
            "temperature": 0.1,
            "database": "postgresql",
            "max_tokens": 1024,
            "enable_semantic_cache": True,
            "groq_api_key_set": bool(settings.GROQ_API_KEY),
            "gemini_api_key_set": bool(settings.GEMINI_API_KEY),
        }),
        ("guardrails_config", {
            "blocked_operations": ["DROP", "DELETE", "UPDATE", "INSERT", "TRUNCATE", "ALTER", "GRANT", "REVOKE", "CREATE"],
            "allow_dml_override": False,
            "default_row_limit": 1000,
            "max_row_limit": 2000,
            "enforce_row_limit": False,
            "allowed_tables": [
                "organizations", "departments", "users", "vendors",
                "subscriptions", "license_allocations", "invoices",
                "usage_telemetry", "optimization_recommendations"
            ]
        })
    ]
    for key, val in initial_settings:
        cur.execute(
            """
            INSERT INTO system_settings (key, value)
            VALUES (%s, %s)
            ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = CURRENT_TIMESTAMP
            """,
            (key, psycopg2.extras.Json(val))
        )
    conn.commit()

    # 13. Seed Initial Query Logs
    print("Seeding sample query logs...")
    sample_logs = [
        ("What are the top 5 subscriptions by monthly spend?",
         "SELECT product_name, category, monthly_cost FROM subscriptions ORDER BY monthly_cost DESC LIMIT 5;",
         "SELECT_SIMPLE", "success", None, 14.2, 5, "openai/gpt-oss-120b"),
        ("Which subscriptions renew in the next 30 days?",
         "SELECT product_name, monthly_cost, renewal_date FROM subscriptions WHERE renewal_date <= CURRENT_DATE + INTERVAL '30 days' ORDER BY renewal_date ASC LIMIT 50;",
         "SELECT_TEMPORAL", "success", None, 18.5, 4, "gemini-3.1-flash-lite"),
        ("Show total monthly cost grouped by category",
         "SELECT category, COUNT(*) as tool_count, SUM(monthly_cost) as total_monthly_spend FROM subscriptions GROUP BY category ORDER BY total_monthly_spend DESC LIMIT 50;",
         "SELECT_AGGREGATE", "success", None, 22.1, 7, "openai/gpt-oss-120b"),
        ("DELETE FROM subscriptions WHERE id = 1;",
         None, "UNSUPPORTED", "blocked", "Guardrail blocked prohibited operation 'DELETE'. SELECT queries only.", 1.2, 0, "openai/gpt-oss-120b")
    ]
    cur.executemany(
        """
        INSERT INTO query_logs (
            query_text, generated_sql, query_type, status, error_message,
            latency_ms, row_count, model_used
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        sample_logs
    )
    conn.commit()

    # Verify counts
    print("\n--- Seeding Complete: Verifying Row Counts ---")
    tables = [
        "organizations", "departments", "users", "vendors", "subscriptions",
        "license_allocations", "invoices", "usage_telemetry",
        "optimization_recommendations", "schema_metadata", "query_logs", "system_settings"
    ]
    for t in tables:
        cur.execute(f"SELECT COUNT(*) FROM {t};")
        count = cur.fetchone()[0]
        print(f"Table '{t}': {count} rows")

    cur.close()
    conn.close()
    print("\nDatabase seeded successfully!")

if __name__ == "__main__":
    run_seed()
