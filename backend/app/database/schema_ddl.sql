-- ============================================================================
-- SubscriptIQ PostgreSQL Schema DDL
-- Enterprise SaaS Subscription Analytics & Optimization Engine
-- ============================================================================

-- Drop tables if needed in reverse dependency order
DROP TABLE IF EXISTS optimization_recommendations CASCADE;
DROP TABLE IF EXISTS usage_telemetry CASCADE;
DROP TABLE IF EXISTS invoices CASCADE;
DROP TABLE IF EXISTS license_allocations CASCADE;
DROP TABLE IF EXISTS subscriptions CASCADE;
DROP TABLE IF EXISTS vendors CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS departments CASCADE;
DROP TABLE IF EXISTS organizations CASCADE;
DROP TABLE IF EXISTS schema_metadata CASCADE;
DROP TABLE IF EXISTS query_logs CASCADE;
DROP TABLE IF EXISTS system_settings CASCADE;

-- 1. Organizations
CREATE TABLE organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    domain VARCHAR(120) NOT NULL UNIQUE,
    industry VARCHAR(60) NOT NULL,
    employee_count INT NOT NULL DEFAULT 100,
    tier VARCHAR(30) NOT NULL DEFAULT 'Enterprise',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Departments
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    org_id INT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(80) NOT NULL,
    budget_annual NUMERIC(14, 2) NOT NULL DEFAULT 500000.00,
    cost_center_code VARCHAR(40) NOT NULL,
    head_count INT NOT NULL DEFAULT 20
);

-- 3. Users (Workspace employees)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    org_id INT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    dept_id INT REFERENCES departments(id) ON DELETE SET NULL,
    email VARCHAR(160) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'Member',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Vendors (SaaS Tool Providers)
CREATE TABLE vendors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    website VARCHAR(160),
    support_tier VARCHAR(50) DEFAULT 'Enterprise 24/7',
    security_compliance VARCHAR(80) DEFAULT 'SOC2 Type II, ISO27001'
);

-- 5. Subscriptions (Master SaaS contracts)
-- Ambiguity case 1: 'monthly_cost' vs 'annual_contract_value / 12'
-- Ambiguity case 2: 'annual_contract_value' vs SUM(invoices.amount)
CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    org_id INT NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    vendor_id INT NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
    product_name VARCHAR(120) NOT NULL,
    category VARCHAR(60) NOT NULL,
    billing_cycle VARCHAR(30) NOT NULL DEFAULT 'monthly', -- 'monthly', 'annual', 'quarterly'
    monthly_cost NUMERIC(10, 2) NOT NULL,
    annual_contract_value NUMERIC(14, 2) NOT NULL,
    total_seats_licensed INT NOT NULL DEFAULT 10,
    start_date DATE NOT NULL,
    renewal_date DATE NOT NULL,
    auto_renew BOOLEAN NOT NULL DEFAULT TRUE,
    status VARCHAR(30) NOT NULL DEFAULT 'active', -- 'active', 'under_review', 'pending_downgrade', 'canceled'
    payment_terms VARCHAR(40) DEFAULT 'Net 30'
);

-- 6. License Allocations (Seat usage per user)
-- Temporal arithmetic: last_activity_date comparison for dormant seat detection
CREATE TABLE license_allocations (
    id SERIAL PRIMARY KEY,
    subscription_id INT NOT NULL REFERENCES subscriptions(id) ON DELETE CASCADE,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    seat_type VARCHAR(40) NOT NULL DEFAULT 'Full License', -- 'Full License', 'Admin', 'Viewer', 'Guest'
    assigned_date DATE NOT NULL,
    last_activity_date DATE NOT NULL,
    is_dormant BOOLEAN NOT NULL DEFAULT FALSE
);

-- 7. Invoices (Billing history)
-- Ambiguity case: 'amount' in invoices vs 'monthly_cost' in subscriptions
CREATE TABLE invoices (
    id SERIAL PRIMARY KEY,
    subscription_id INT NOT NULL REFERENCES subscriptions(id) ON DELETE CASCADE,
    invoice_number VARCHAR(60) NOT NULL UNIQUE,
    invoice_date DATE NOT NULL,
    due_date DATE NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    tax_amount NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    payment_status VARCHAR(30) NOT NULL DEFAULT 'paid', -- 'paid', 'pending', 'overdue', 'disputed'
    payment_method VARCHAR(60) NOT NULL DEFAULT 'Amex Corporate'
);

-- 8. Usage Telemetry (Daily/Weekly utilization metrics)
CREATE TABLE usage_telemetry (
    id SERIAL PRIMARY KEY,
    subscription_id INT NOT NULL REFERENCES subscriptions(id) ON DELETE CASCADE,
    record_date DATE NOT NULL,
    active_users_day INT NOT NULL,
    utilization_rate NUMERIC(5, 2) NOT NULL, -- e.g. 78.50%
    storage_used_gb NUMERIC(10, 2) DEFAULT 0.00,
    api_calls_count INT DEFAULT 0
);

-- 9. Optimization Recommendations (AI cost saving opportunities)
CREATE TABLE optimization_recommendations (
    id SERIAL PRIMARY KEY,
    subscription_id INT NOT NULL REFERENCES subscriptions(id) ON DELETE CASCADE,
    recommendation_type VARCHAR(60) NOT NULL, -- 'dormant_seats_removal', 'tier_downgrade', 'annual_switch_discount', 'overlap_consolidation'
    description TEXT NOT NULL,
    estimated_monthly_savings NUMERIC(10, 2) NOT NULL,
    confidence_score NUMERIC(4, 2) NOT NULL DEFAULT 0.90,
    status VARCHAR(30) NOT NULL DEFAULT 'detected', -- 'detected', 'reviewing', 'applied', 'dismissed'
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 10. Schema Metadata (For Schema Manager in Admin UI)
CREATE TABLE schema_metadata (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(80) NOT NULL,
    column_name VARCHAR(80) NOT NULL,
    data_type VARCHAR(60) NOT NULL,
    description TEXT,
    is_sensitive BOOLEAN NOT NULL DEFAULT FALSE,
    synonyms TEXT DEFAULT '',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_table_col UNIQUE (table_name, column_name)
);

-- 11. Query Logs (For Query Logs panel in Admin UI)
CREATE TABLE query_logs (
    id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    generated_sql TEXT,
    query_type VARCHAR(40),
    status VARCHAR(20) NOT NULL, -- 'success', 'error', 'blocked'
    error_message TEXT,
    latency_ms NUMERIC(10, 2) NOT NULL DEFAULT 0.0,
    row_count INT NOT NULL DEFAULT 0,
    model_used VARCHAR(80) NOT NULL,
    user_email VARCHAR(160) DEFAULT 'alex.rivera@subscriptiq.ai',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 12. System Settings (For Model Config & Guardrails panels)
CREATE TABLE system_settings (
    key VARCHAR(80) PRIMARY KEY,
    value JSONB NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create helpful indexes for performance
CREATE INDEX idx_subscriptions_org ON subscriptions(org_id);
CREATE INDEX idx_subscriptions_vendor ON subscriptions(vendor_id);
CREATE INDEX idx_subscriptions_renewal ON subscriptions(renewal_date);
CREATE INDEX idx_licenses_sub ON license_allocations(subscription_id);
CREATE INDEX idx_licenses_user ON license_allocations(user_id);
CREATE INDEX idx_licenses_dormant ON license_allocations(is_dormant);
CREATE INDEX idx_invoices_sub ON invoices(subscription_id);
CREATE INDEX idx_invoices_date ON invoices(invoice_date);
CREATE INDEX idx_telemetry_sub_date ON usage_telemetry(subscription_id, record_date);
