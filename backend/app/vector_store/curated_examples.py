"""
Curated Library of 35 Few-Shot (Question -> SQL) pairs for SubscriptIQ
Covering SELECT_SIMPLE, SELECT_AGGREGATE, SELECT_JOIN, SELECT_TEMPORAL, and Ambiguity cases.
"""

CURATED_EXAMPLES: list[dict] = [
    # --- SELECT_SIMPLE (6 examples) ---
    {
        "id": 1,
        "question": "Show all active SaaS subscriptions",
        "sql": "SELECT id, product_name, category, monthly_cost, annual_contract_value, status FROM subscriptions WHERE status = 'active' ORDER BY monthly_cost DESC;",
        "query_type": "SELECT_SIMPLE",
        "explanation": "Filters the subscriptions table for rows where status is 'active' and orders by monthly cost."
    },
    {
        "id": 2,
        "question": "Which subscriptions have auto-renewal enabled?",
        "sql": "SELECT product_name, renewal_date, monthly_cost, billing_cycle FROM subscriptions WHERE auto_renew = TRUE ORDER BY renewal_date ASC;",
        "query_type": "SELECT_SIMPLE",
        "explanation": "Selects products where auto_renew is true, sorted by upcoming renewal date."
    },
    {
        "id": 3,
        "question": "List all engineering software tools with monthly cost greater than 2000",
        "sql": "SELECT product_name, monthly_cost, total_seats_licensed FROM subscriptions WHERE category = 'Engineering' AND monthly_cost > 2000 ORDER BY monthly_cost DESC;",
        "query_type": "SELECT_SIMPLE",
        "explanation": "Filters subscriptions by Engineering category and monthly cost threshold."
    },
    {
        "id": 4,
        "question": "Show all pending or overdue invoices",
        "sql": "SELECT invoice_number, invoice_date, due_date, amount, payment_status FROM invoices WHERE payment_status IN ('pending', 'overdue') ORDER BY due_date ASC;",
        "query_type": "SELECT_SIMPLE",
        "explanation": "Filters invoices table for pending and overdue payment statuses."
    },
    {
        "id": 5,
        "question": "List all vendors that comply with FedRAMP",
        "sql": "SELECT name, website, support_tier, security_compliance FROM vendors WHERE security_compliance ILIKE '%FedRAMP%' ORDER BY name ASC;",
        "query_type": "SELECT_SIMPLE",
        "explanation": "Filters vendors where security_compliance string includes FedRAMP."
    },
    {
        "id": 6,
        "question": "Find all dormant license seats",
        "sql": "SELECT id, subscription_id, user_id, seat_type, last_activity_date FROM license_allocations WHERE is_dormant = TRUE ORDER BY last_activity_date ASC;",
        "query_type": "SELECT_SIMPLE",
        "explanation": "Filters license allocations flagged as dormant."
    },

    # --- SELECT_AGGREGATE (8 examples) ---
    {
        "id": 7,
        "question": "What is the total monthly spend across all subscriptions?",
        "sql": "SELECT SUM(monthly_cost) AS total_monthly_spend, COUNT(*) AS active_subscriptions_count FROM subscriptions WHERE status = 'active';",
        "query_type": "SELECT_AGGREGATE",
        "explanation": "Calculates the sum of monthly costs across active subscriptions."
    },
    {
        "id": 8,
        "question": "Show total monthly spend grouped by subscription category",
        "sql": "SELECT category, COUNT(*) AS tools_count, SUM(monthly_cost) AS total_monthly_cost, SUM(annual_contract_value) AS total_acv FROM subscriptions GROUP BY category ORDER BY total_monthly_cost DESC;",
        "query_type": "SELECT_AGGREGATE",
        "explanation": "Groups subscriptions by category and aggregates count and total cost."
    },
    {
        "id": 9,
        "question": "What is the average license utilization rate for each subscription?",
        "sql": "SELECT s.product_name, ROUND(AVG(t.utilization_rate), 2) AS avg_utilization_pct, MAX(t.active_users_day) AS peak_dau FROM subscriptions s JOIN usage_telemetry t ON s.id = t.subscription_id GROUP BY s.product_name ORDER BY avg_utilization_pct ASC;",
        "query_type": "SELECT_AGGREGATE",
        "explanation": "Joins usage telemetry with subscriptions to compute average utilization."
    },
    {
        "id": 10,
        "question": "How many dormant license seats are there per tool?",
        "sql": "SELECT s.product_name, COUNT(l.id) AS dormant_seats_count, s.monthly_cost / NULLIF(s.total_seats_licensed, 0) AS estimated_cost_per_seat FROM subscriptions s JOIN license_allocations l ON s.id = l.subscription_id WHERE l.is_dormant = TRUE GROUP BY s.product_name, s.monthly_cost, s.total_seats_licensed ORDER BY dormant_seats_count DESC;",
        "query_type": "SELECT_AGGREGATE",
        "explanation": "Counts dormant license allocations grouped by subscription."
    },
    {
        "id": 11,
        "question": "What is the total potential savings from all detected optimization recommendations?",
        "sql": "SELECT recommendation_type, COUNT(*) AS opportunities_count, SUM(estimated_monthly_savings) AS total_monthly_savings FROM optimization_recommendations WHERE status = 'detected' GROUP BY recommendation_type ORDER BY total_monthly_savings DESC;",
        "query_type": "SELECT_AGGREGATE",
        "explanation": "Sums potential monthly savings grouped by recommendation type."
    },
    {
        "id": 12,
        "question": "Calculate total annual budget and employee count per department",
        "sql": "SELECT name AS department_name, head_count, budget_annual, cost_center_code FROM departments ORDER BY budget_annual DESC;",
        "query_type": "SELECT_AGGREGATE",
        "explanation": "Retrieves department budgets and head counts."
    },
    {
        "id": 13,
        "question": "What is the maximum and average invoice amount paid per vendor?",
        "sql": "SELECT v.name AS vendor_name, COUNT(i.id) AS invoices_count, ROUND(AVG(i.amount), 2) AS avg_invoice_amount, MAX(i.amount) AS max_invoice_amount FROM vendors v JOIN subscriptions s ON v.id = s.vendor_id JOIN invoices i ON s.id = i.subscription_id WHERE i.payment_status = 'paid' GROUP BY v.name ORDER BY avg_invoice_amount DESC;",
        "query_type": "SELECT_AGGREGATE",
        "explanation": "Calculates average and maximum paid invoice amounts per vendor."
    },
    {
        "id": 14,
        "question": "Count of users by role in the organization",
        "sql": "SELECT role, COUNT(*) AS user_count FROM users WHERE is_active = TRUE GROUP BY role ORDER BY user_count DESC;",
        "query_type": "SELECT_AGGREGATE",
        "explanation": "Groups active users by role with count."
    },

    # --- SELECT_JOIN (10 examples) ---
    {
        "id": 15,
        "question": "List all subscriptions along with their vendor name and support tier",
        "sql": "SELECT s.product_name, v.name AS vendor_name, v.support_tier, s.monthly_cost, s.renewal_date FROM subscriptions s JOIN vendors v ON s.vendor_id = v.id ORDER BY s.monthly_cost DESC;",
        "query_type": "SELECT_JOIN",
        "explanation": "Joins subscriptions with vendors table to fetch vendor support metadata."
    },
    {
        "id": 16,
        "question": "Show employees who have full licenses for Figma",
        "sql": "SELECT u.full_name, u.email, d.name AS department, l.assigned_date, l.last_activity_date FROM users u JOIN license_allocations l ON u.id = l.user_id JOIN subscriptions s ON l.subscription_id = s.id LEFT JOIN departments d ON u.dept_id = d.id WHERE s.product_name ILIKE '%Figma%' AND l.seat_type = 'Full License' ORDER BY l.last_activity_date DESC;",
        "query_type": "SELECT_JOIN",
        "explanation": "Joins users, license_allocations, subscriptions, and departments for Figma full license seats."
    },
    {
        "id": 17,
        "question": "Show all dormant seats with user name, tool name, and last activity date",
        "sql": "SELECT u.full_name, s.product_name, l.seat_type, l.last_activity_date, CURRENT_DATE - l.last_activity_date AS days_inactive FROM license_allocations l JOIN users u ON l.user_id = u.id JOIN subscriptions s ON l.subscription_id = s.id WHERE l.is_dormant = TRUE ORDER BY days_inactive DESC;",
        "query_type": "SELECT_JOIN",
        "explanation": "Joins allocations with users and subscriptions, calculating inactive days."
    },
    {
        "id": 18,
        "question": "List all invoices for Datadog including due date and payment status",
        "sql": "SELECT i.invoice_number, s.product_name, i.invoice_date, i.due_date, i.amount, i.payment_status FROM invoices i JOIN subscriptions s ON i.subscription_id = s.id WHERE s.product_name ILIKE '%Datadog%' ORDER BY i.invoice_date DESC;",
        "query_type": "SELECT_JOIN",
        "explanation": "Joins invoices and subscriptions filtered by Datadog."
    },
    {
        "id": 19,
        "question": "Which department has the most software licenses assigned?",
        "sql": "SELECT d.name AS department_name, COUNT(l.id) AS total_assigned_licenses FROM departments d JOIN users u ON d.id = u.dept_id JOIN license_allocations l ON u.id = l.user_id GROUP BY d.name ORDER BY total_assigned_licenses DESC;",
        "query_type": "SELECT_JOIN",
        "explanation": "Three-table join between departments, users, and license allocations to rank by assigned seats."
    },
    {
        "id": 20,
        "question": "Show AI recommendations with subscription details and vendor website",
        "sql": "SELECT r.description, r.estimated_monthly_savings, r.confidence_score, s.product_name, v.name AS vendor_name, v.website FROM optimization_recommendations r JOIN subscriptions s ON r.subscription_id = s.id JOIN vendors v ON s.vendor_id = v.id WHERE r.status = 'detected' ORDER BY r.estimated_monthly_savings DESC;",
        "query_type": "SELECT_JOIN",
        "explanation": "Joins optimization recommendations with subscriptions and vendors."
    },
    {
        "id": 21,
        "question": "Find users with access to more than 3 distinct subscriptions",
        "sql": "SELECT u.full_name, u.email, COUNT(DISTINCT l.subscription_id) AS distinct_tools_count FROM users u JOIN license_allocations l ON u.id = l.user_id GROUP BY u.id, u.full_name, u.email HAVING COUNT(DISTINCT l.subscription_id) > 3 ORDER BY distinct_tools_count DESC;",
        "query_type": "SELECT_JOIN",
        "explanation": "Joins users and licenses, grouping by user with HAVING filter on distinct subscriptions."
    },
    {
        "id": 22,
        "question": "List corporate payment cards and total spend billed to each method",
        "sql": "SELECT payment_method, COUNT(*) AS invoice_count, SUM(amount) AS total_billed_amount FROM invoices WHERE payment_status = 'paid' GROUP BY payment_method ORDER BY total_billed_amount DESC;",
        "query_type": "SELECT_AGGREGATE",
        "explanation": "Aggregates paid invoices by corporate payment method."
    },
    {
        "id": 23,
        "question": "Show subscriptions and their lowest recorded daily utilization rate",
        "sql": "SELECT s.product_name, MIN(t.utilization_rate) AS lowest_utilization_pct, AVG(t.utilization_rate) AS avg_utilization_pct FROM subscriptions s JOIN usage_telemetry t ON s.id = t.subscription_id GROUP BY s.product_name ORDER BY lowest_utilization_pct ASC;",
        "query_type": "SELECT_JOIN",
        "explanation": "Joins subscriptions and telemetry to identify lowest recorded utilization."
    },
    {
        "id": 24,
        "question": "Show users in Engineering who have unassigned or dormant licenses",
        "sql": "SELECT u.full_name, d.name AS department, s.product_name, l.seat_type, l.last_activity_date FROM users u JOIN departments d ON u.dept_id = d.id JOIN license_allocations l ON u.id = l.user_id JOIN subscriptions s ON l.subscription_id = s.id WHERE d.name = 'Engineering' AND l.is_dormant = TRUE ORDER BY l.last_activity_date ASC;",
        "query_type": "SELECT_JOIN",
        "explanation": "Joins users, departments, licenses, and subscriptions filtered by Engineering and dormancy."
    },

    # --- SELECT_TEMPORAL (7 examples) ---
    {
        "id": 25,
        "question": "Which subscriptions renew in the next 30 days?",
        "sql": "SELECT product_name, category, monthly_cost, renewal_date, (renewal_date - CURRENT_DATE) AS days_until_renewal FROM subscriptions WHERE renewal_date >= CURRENT_DATE AND renewal_date <= CURRENT_DATE + INTERVAL '30 days' ORDER BY renewal_date ASC;",
        "query_type": "SELECT_TEMPORAL",
        "explanation": "Performs temporal date math filtering renewal_date within the next 30 days."
    },
    {
        "id": 26,
        "question": "Find all subscriptions renewing within 14 days with their monthly cost",
        "sql": "SELECT product_name, monthly_cost, renewal_date, (renewal_date - CURRENT_DATE) AS days_remaining FROM subscriptions WHERE renewal_date >= CURRENT_DATE AND renewal_date <= CURRENT_DATE + INTERVAL '14 days' ORDER BY days_remaining ASC;",
        "query_type": "SELECT_TEMPORAL",
        "explanation": "Calculates days remaining until renewal within a 14-day window."
    },
    {
        "id": 27,
        "question": "Show users who have not logged in for more than 45 days",
        "sql": "SELECT u.full_name, s.product_name, l.last_activity_date, (CURRENT_DATE - l.last_activity_date) AS days_inactive FROM license_allocations l JOIN users u ON l.user_id = u.id JOIN subscriptions s ON l.subscription_id = s.id WHERE l.last_activity_date < CURRENT_DATE - INTERVAL '45 days' ORDER BY days_inactive DESC;",
        "query_type": "SELECT_TEMPORAL",
        "explanation": "Compares last_activity_date against a 45-day threshold."
    },
    {
        "id": 28,
        "question": "What is the total invoice spend in the last 90 days?",
        "sql": "SELECT SUM(amount) AS total_spend_last_90_days, COUNT(*) AS invoices_count FROM invoices WHERE invoice_date >= CURRENT_DATE - INTERVAL '90 days' AND payment_status = 'paid';",
        "query_type": "SELECT_TEMPORAL",
        "explanation": "Aggregates invoice amounts issued within the last 90 days."
    },
    {
        "id": 29,
        "question": "Show telemetry trends over the past 30 days for AWS",
        "sql": "SELECT t.record_date, t.active_users_day, t.utilization_rate, t.storage_used_gb FROM usage_telemetry t JOIN subscriptions s ON t.subscription_id = s.id WHERE s.product_name ILIKE '%AWS%' AND t.record_date >= CURRENT_DATE - INTERVAL '30 days' ORDER BY t.record_date DESC;",
        "query_type": "SELECT_TEMPORAL",
        "explanation": "Filters daily telemetry for AWS over the past 30 days."
    },
    {
        "id": 30,
        "question": "List subscriptions that started in the last 6 months",
        "sql": "SELECT product_name, category, start_date, monthly_cost FROM subscriptions WHERE start_date >= CURRENT_DATE - INTERVAL '6 months' ORDER BY start_date DESC;",
        "query_type": "SELECT_TEMPORAL",
        "explanation": "Selects subscriptions initiated within the past 6 months."
    },
    {
        "id": 31,
        "question": "Find overdue invoices where due date was more than 15 days ago",
        "sql": "SELECT i.invoice_number, s.product_name, i.due_date, (CURRENT_DATE - i.due_date) AS days_overdue, i.amount FROM invoices i JOIN subscriptions s ON i.subscription_id = s.id WHERE i.payment_status = 'overdue' AND i.due_date < CURRENT_DATE - INTERVAL '15 days' ORDER BY days_overdue DESC;",
        "query_type": "SELECT_TEMPORAL",
        "explanation": "Identifies overdue invoices overdue by more than 15 days."
    },

    # --- AMBIGUITY RESOLUTION & ADVANCED CASES (4 examples) ---
    {
        "id": 32,
        "question": "What is our spend on Figma?",
        "sql": "SELECT product_name, monthly_cost AS monthly_recurring_spend, annual_contract_value AS total_acv, billing_cycle FROM subscriptions WHERE product_name ILIKE '%Figma%';",
        "query_type": "SELECT_SIMPLE",
        "explanation": "Resolves ambiguity between monthly_cost and annual_contract_value by presenting both clearly."
    },
    {
        "id": 33,
        "question": "Show total revenue or invoice payments for all tools this year",
        "sql": "SELECT s.product_name, SUM(i.amount) AS total_invoiced_paid FROM subscriptions s JOIN invoices i ON s.id = i.subscription_id WHERE i.payment_status = 'paid' AND EXTRACT(YEAR FROM i.invoice_date) = EXTRACT(YEAR FROM CURRENT_DATE) GROUP BY s.product_name ORDER BY total_invoiced_paid DESC;",
        "query_type": "SELECT_AGGREGATE",
        "explanation": "Resolves spend/revenue ambiguity by summing actual paid invoice amounts for the current year."
    },
    {
        "id": 34,
        "question": "Top 10 highest cost software licenses per seat",
        "sql": "SELECT product_name, category, monthly_cost, total_seats_licensed, ROUND(monthly_cost / NULLIF(total_seats_licensed, 0), 2) AS cost_per_seat FROM subscriptions WHERE total_seats_licensed > 0 ORDER BY cost_per_seat DESC LIMIT 10;",
        "query_type": "SELECT_AGGREGATE",
        "explanation": "Calculates unit economics: monthly cost per licensed seat."
    },
    {
        "id": 35,
        "question": "Rank subscriptions by potential monthly savings detected by AI",
        "sql": "SELECT s.product_name, s.monthly_cost, r.recommendation_type, r.estimated_monthly_savings, ROUND((r.estimated_monthly_savings / NULLIF(s.monthly_cost, 0)) * 100, 1) AS savings_pct FROM subscriptions s JOIN optimization_recommendations r ON s.id = r.subscription_id WHERE r.status = 'detected' ORDER BY r.estimated_monthly_savings DESC;",
        "query_type": "SELECT_JOIN",
        "explanation": "Calculates percentage savings relative to monthly cost for detected optimizations."
    }
]
