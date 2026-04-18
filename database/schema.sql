-- FairGig PostgreSQL Database Schema

-- This schema defines all tables required for user management, earnings tracking,
-- verification workflows, and community grievances.

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable Row-Level Security
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- ============================================================================
-- USERS TABLE - Core authentication and role management
-- ============================================================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('worker', 'verifier', 'advocate')),
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_created_at ON users(created_at);

-- ============================================================================
-- WORKERS TABLE - Extended profile for gig workers
-- ============================================================================
CREATE TABLE workers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    full_name VARCHAR(255) NOT NULL,
    city_zone VARCHAR(100) NOT NULL CHECK (city_zone IN (
        'Karachi', 'Lahore', 'Islamabad', 'Peshawar', 'Quetta', 'Multan', 'Faisalabad', 'Other'
    )),
    primary_platform VARCHAR(100) NOT NULL CHECK (primary_platform IN (
        'Careem', 'Uber', 'Shopee', 'InDrive', 'Freelance', 'Domestic Work', 'Other'
    )),
    category VARCHAR(100) NOT NULL CHECK (category IN (
        'ride-hailing', 'delivery', 'freelance', 'domestic-work', 'other'
    )),
    verified_entries_count INTEGER DEFAULT 0,
    profile_image_url VARCHAR(500),
    bio TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_workers_user_id ON workers(user_id);
CREATE INDEX idx_workers_city_zone ON workers(city_zone);
CREATE INDEX idx_workers_primary_platform ON workers(primary_platform);
CREATE INDEX idx_workers_category ON workers(category);

-- ============================================================================
-- EARNINGS_ENTRIES TABLE - Core earnings data for workers
-- ============================================================================
CREATE TABLE earnings_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    worker_id UUID NOT NULL REFERENCES workers(user_id) ON DELETE CASCADE,
    platform VARCHAR(100) NOT NULL CHECK (platform IN (
        'Careem', 'Uber', 'Shopee', 'InDrive', 'Freelance', 'Domestic Work', 'Other'
    )),
    entry_date DATE NOT NULL,
    hours_worked NUMERIC(5, 2) NOT NULL CHECK (hours_worked > 0 AND hours_worked <= 24),
    gross_earned NUMERIC(10, 2) NOT NULL CHECK (gross_earned >= 0),
    platform_deductions NUMERIC(10, 2) NOT NULL CHECK (platform_deductions >= 0),
    net_received NUMERIC(10, 2) NOT NULL CHECK (net_received >= 0),
    deduction_percentage NUMERIC(5, 2) GENERATED ALWAYS AS (
        CASE 
            WHEN gross_earned = 0 THEN 0
            ELSE (platform_deductions / gross_earned) * 100
        END
    ) STORED,
    hourly_rate NUMERIC(10, 2) GENERATED ALWAYS AS (
        CASE 
            WHEN hours_worked = 0 THEN 0
            ELSE net_received / hours_worked
        END
    ) STORED,
    verification_status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (verification_status IN (
        'pending', 'approved', 'flagged', 'unverifiable'
    )),
    screenshot_id UUID,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_earnings_worker_id ON earnings_entries(worker_id);
CREATE INDEX idx_earnings_entry_date ON earnings_entries(entry_date);
CREATE INDEX idx_earnings_platform ON earnings_entries(platform);
CREATE INDEX idx_earnings_verification_status ON earnings_entries(verification_status);
CREATE INDEX idx_earnings_worker_date ON earnings_entries(worker_id, entry_date);
CREATE INDEX idx_earnings_worker_platform ON earnings_entries(worker_id, platform);

-- ============================================================================
-- SCREENSHOTS TABLE - Evidence for earnings verification
-- ============================================================================
CREATE TABLE screenshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entry_id UUID NOT NULL REFERENCES earnings_entries(id) ON DELETE CASCADE,
    file_path VARCHAR(500) NOT NULL,
    file_size_bytes INTEGER,
    file_format VARCHAR(20) CHECK (file_format IN ('jpg', 'jpeg', 'png', 'gif', 'webp')),
    uploaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    verification_decision VARCHAR(50) CHECK (verification_decision IN (
        'approved', 'flagged', 'unverifiable'
    )),
    verified_by_verifier_id UUID REFERENCES users(id),
    verification_notes TEXT,
    verified_at TIMESTAMP
);

CREATE INDEX idx_screenshots_entry_id ON screenshots(entry_id);
CREATE INDEX idx_screenshots_verification_decision ON screenshots(verification_decision);
CREATE INDEX idx_screenshots_verified_by ON screenshots(verified_by_verifier_id);
CREATE INDEX idx_screenshots_uploaded_at ON screenshots(uploaded_at);

-- ============================================================================
-- GRIEVANCE_POSTS TABLE - Community complaints and platform intelligence
-- ============================================================================
CREATE TABLE grievance_posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    worker_id UUID REFERENCES workers(user_id) ON DELETE SET NULL,
    platform VARCHAR(100) NOT NULL CHECK (platform IN (
        'Careem', 'Uber', 'Shopee', 'InDrive', 'Freelance', 'Domestic Work', 'Other'
    )),
    category VARCHAR(100) NOT NULL CHECK (category IN (
        'rate_cut', 'wrongful_deactivation', 'technical_issue', 'payment_issue', 'other'
    )),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    is_anonymous BOOLEAN DEFAULT TRUE,
    tags TEXT[], -- Array of tags added by advocates (e.g., ['urgent', 'duplicate'])
    escalation_state VARCHAR(50) NOT NULL DEFAULT 'open' CHECK (escalation_state IN (
        'open', 'escalated', 'resolved'
    )),
    upvote_count INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_grievance_worker_id ON grievance_posts(worker_id);
CREATE INDEX idx_grievance_platform ON grievance_posts(platform);
CREATE INDEX idx_grievance_category ON grievance_posts(category);
CREATE INDEX idx_grievance_escalation_state ON grievance_posts(escalation_state);
CREATE INDEX idx_grievance_created_at ON grievance_posts(created_at);
CREATE INDEX idx_grievance_tags ON grievance_posts USING GIN(tags);

-- ============================================================================
-- GRIEVANCE_COMMENTS TABLE - Discussion thread for grievance posts
-- ============================================================================
CREATE TABLE grievance_comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    post_id UUID NOT NULL REFERENCES grievance_posts(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL,
    comment_text TEXT NOT NULL,
    is_from_advocate BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_grievance_comments_post_id ON grievance_comments(post_id);
CREATE INDEX idx_grievance_comments_user_id ON grievance_comments(user_id);
CREATE INDEX idx_grievance_comments_created_at ON grievance_comments(created_at);

-- ============================================================================
-- OTP_TOKENS TABLE - One-time passwords for email verification
-- ============================================================================
CREATE TABLE otp_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL,
    token VARCHAR(10) NOT NULL,
    purpose VARCHAR(50) NOT NULL CHECK (purpose IN ('email_verification', 'password_reset')),
    expiry TIMESTAMP NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_otp_tokens_email ON otp_tokens(email);
CREATE INDEX idx_otp_tokens_token ON otp_tokens(token);
CREATE INDEX idx_otp_tokens_expiry ON otp_tokens(expiry);

-- ============================================================================
-- PASSWORD_RESET_TOKENS TABLE - Password reset tokens
-- ============================================================================
CREATE TABLE password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) NOT NULL UNIQUE,
    expiry TIMESTAMP NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_password_reset_tokens_user_id ON password_reset_tokens(user_id);
CREATE INDEX idx_password_reset_tokens_token ON password_reset_tokens(token);
CREATE INDEX idx_password_reset_tokens_expiry ON password_reset_tokens(expiry);

-- ============================================================================
-- ANONYMIZED VIEWS FOR ANALYTICS (No PII exposure)
-- ============================================================================

-- View for Commission Trends (No individual worker data exposed)
CREATE VIEW commission_trends AS
SELECT 
    platform,
    DATE_TRUNC('month', entry_date)::DATE AS month,
    COUNT(*) AS entry_count,
    ROUND(AVG(deduction_percentage)::NUMERIC, 2) AS avg_deduction_pct,
    ROUND(MIN(deduction_percentage)::NUMERIC, 2) AS min_deduction_pct,
    ROUND(MAX(deduction_percentage)::NUMERIC, 2) AS max_deduction_pct,
    ROUND(STDDEV(deduction_percentage)::NUMERIC, 2) AS stddev_deduction_pct
FROM earnings_entries
WHERE verification_status = 'approved'
GROUP BY platform, DATE_TRUNC('month', entry_date)
ORDER BY month DESC, platform;

-- View for Income Distribution by Zone (No individual worker data exposed)
CREATE VIEW income_distribution_by_zone AS
SELECT 
    w.city_zone,
    w.category,
    COUNT(ee.id) AS entry_count,
    ROUND(AVG(ee.net_received)::NUMERIC, 2) AS avg_net_earnings,
    ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY ee.net_received)::NUMERIC, 2) AS p25_earnings,
    ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY ee.net_received)::NUMERIC, 2) AS median_earnings,
    ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY ee.net_received)::NUMERIC, 2) AS p75_earnings,
    ROUND(AVG(ee.hourly_rate)::NUMERIC, 2) AS avg_hourly_rate,
    ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY ee.hourly_rate)::NUMERIC, 2) AS median_hourly_rate
FROM earnings_entries ee
JOIN workers w ON ee.worker_id = w.user_id
WHERE ee.verification_status = 'approved'
GROUP BY w.city_zone, w.category
ORDER BY w.city_zone, w.category;

-- View for Verification Statistics (Aggregated, no PII)
CREATE VIEW verification_stats AS
SELECT 
    ee.platform,
    ee.verification_status,
    COUNT(*) AS count,
    ROUND((COUNT(*)::FLOAT / (SELECT COUNT(*) FROM earnings_entries) * 100)::NUMERIC, 2) AS percentage
FROM earnings_entries ee
GROUP BY ee.platform, ee.verification_status
ORDER BY ee.platform, ee.verification_status;

-- ============================================================================
-- ROW-LEVEL SECURITY POLICIES (Disabled - enable after Auth Service is running)
-- ============================================================================
-- NOTE: RLS requires the Auth Service to set the session variable
-- `app.current_user_id` on each DB connection before queries run.
-- Uncomment and apply these policies once the Auth Service is deployed.
--
-- Example session setup in Auth Service:
--   db.execute("SET LOCAL app.current_user_id = :uid", {"uid": str(user_id)})
--
-- ALTER TABLE workers ENABLE ROW LEVEL SECURITY;
--
-- CREATE POLICY workers_select_own ON workers
--     FOR SELECT USING (user_id = current_setting('app.current_user_id', true)::uuid);
--
-- CREATE POLICY workers_update_own ON workers
--     FOR UPDATE USING (user_id = current_setting('app.current_user_id', true)::uuid);
--
-- ALTER TABLE earnings_entries ENABLE ROW LEVEL SECURITY;
--
-- CREATE POLICY earnings_select_own ON earnings_entries
--     FOR SELECT USING (worker_id = current_setting('app.current_user_id', true)::uuid);
--
-- CREATE POLICY earnings_insert_own ON earnings_entries
--     FOR INSERT WITH CHECK (worker_id = current_setting('app.current_user_id', true)::uuid);
--
-- CREATE POLICY earnings_update_own ON earnings_entries
--     FOR UPDATE USING (
--         worker_id = current_setting('app.current_user_id', true)::uuid
--         AND verification_status = 'pending'
--     );

-- ============================================================================
-- UTILITY FUNCTIONS
-- ============================================================================

-- Function to update earnings_entries.updated_at timestamp
CREATE OR REPLACE FUNCTION update_earnings_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for earnings_entries
CREATE TRIGGER earnings_entries_update_trigger
BEFORE UPDATE ON earnings_entries
FOR EACH ROW
EXECUTE FUNCTION update_earnings_updated_at();

-- Function to update workers.updated_at timestamp
CREATE OR REPLACE FUNCTION update_workers_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for workers
CREATE TRIGGER workers_update_trigger
BEFORE UPDATE ON workers
FOR EACH ROW
EXECUTE FUNCTION update_workers_updated_at();

-- Function to update users.updated_at timestamp
CREATE OR REPLACE FUNCTION update_users_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for users
CREATE TRIGGER users_update_trigger
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_users_updated_at();

-- Function to update grievance_posts.updated_at timestamp
CREATE OR REPLACE FUNCTION update_grievance_posts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for grievance_posts
CREATE TRIGGER grievance_posts_update_trigger
BEFORE UPDATE ON grievance_posts
FOR EACH ROW
EXECUTE FUNCTION update_grievance_posts_updated_at();

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
