# FairGig Database Setup Guide

Complete instructions for setting up the FairGig PostgreSQL database and verifying your installation.

---

## Prerequisites

- PostgreSQL 14+ installed and running
- psql command-line tool available
- Database superuser access

**Installation Links**:
- PostgreSQL: https://www.postgresql.org/download/
- macOS (Homebrew): `brew install postgresql`
- Windows: Download from https://www.postgresql.org/download/windows/
- Linux (Ubuntu): `sudo apt-get install postgresql postgresql-contrib`

---

## Step 1: Create the Database

Open a terminal/command prompt and run:

```bash
# Connect to PostgreSQL as superuser
psql -U postgres

# Inside psql shell, create the database
CREATE DATABASE fairgig_db;

# List databases to verify (optional)
\l

# Exit psql
\q
```

**Windows Users**: If psql is not found, add PostgreSQL to your PATH or use the full path:
```bash
"C:\Program Files\PostgreSQL\14\bin\psql" -U postgres
```

---

## Step 2: Run the Schema

Navigate to the fastgig project directory and apply the schema:

```bash
# From project root directory
cd database

# Apply the schema using psql
psql -U postgres -d fairgig_db -f schema.sql
```

**Expected Output**:
```
CREATE EXTENSION
CREATE EXTENSION
CREATE TABLE
CREATE INDEX
...
CREATE TRIGGER
CREATE TRIGGER
```

If you see any errors, ensure PostgreSQL is running and the database was created in Step 1.

---

## Step 3: Verify the Installation

### 3.1 Connect to the Database

```bash
psql -U postgres -d fairgig_db
```

Inside psql, verify all tables exist:

```sql
-- List all tables
\dt

-- Expected output (8 tables):
-- users
-- workers
-- earnings_entries
-- screenshots
-- grievance_posts
-- grievance_comments
-- otp_tokens
-- password_reset_tokens
```

### 3.2 Check Indexes

```sql
-- List all indexes
\di

-- Should show indexes for each table like:
-- idx_users_email
-- idx_workers_city_zone
-- idx_earnings_worker_id
-- etc.
```

### 3.3 Check Views

```sql
-- List all views
\dv

-- Expected output (3 views):
-- commission_trends
-- income_distribution_by_zone
-- verification_stats
```

### 3.4 Check Functions and Triggers

```sql
-- List all functions
\df

-- Expected output (4 functions):
-- update_earnings_updated_at
-- update_workers_updated_at
-- update_users_updated_at
-- update_grievance_posts_updated_at

-- List all triggers
\dy

-- Expected output (4 triggers):
-- earnings_entries_update_trigger
-- workers_update_trigger
-- users_update_trigger
-- grievance_posts_update_trigger
```

### 3.5 Verify Table Structure

```sql
-- Describe the users table
\d users

-- Should show columns:
-- id, email, password_hash, role, email_verified, created_at, updated_at, last_login

-- Describe the earnings_entries table
\d earnings_entries

-- Should show columns and generated columns
```

### 3.6 Test Insert Operations

```sql
-- Insert a test user (password should be bcrypt hashed in real app)
INSERT INTO users (email, password_hash, role, email_verified)
VALUES ('test@example.com', 'hashed_password_here', 'worker', false);

-- Verify insert
SELECT * FROM users WHERE email = 'test@example.com';

-- Clean up test data
DELETE FROM users WHERE email = 'test@example.com';
```

---

## Database Schema Overview

### Core Tables

**1. users**
- Primary authentication table
- Stores email, password hash, and role
- Roles: worker, verifier, advocate

**2. workers**
- Extended profile for gig workers
- Links to users via foreign key
- Stores: full_name, city_zone, primary_platform, category
- Tracks verified_entries_count

**3. earnings_entries**
- Core earnings data for each worker shift
- Fields: platform, entry_date, hours_worked, gross_earned, platform_deductions, net_received
- Verification status: pending, approved, flagged, unverifiable
- Generated columns: deduction_percentage, hourly_rate
- Indexed by: worker_id, entry_date, platform, verification_status

**4. screenshots**
- Evidence for earnings verification
- Links to earnings_entries via foreign key
- Stores: file_path, verification_decision, verified_by_verifier_id
- Tracks: uploaded_at, verified_at

**5. grievance_posts**
- Community complaints about platforms
- Fields: platform, category, title, description
- Tags added by advocates
- Escalation state: open, escalated, resolved
- Tracks upvotes

**6. grievance_comments**
- Discussion thread for grievance posts
- Links to grievance_posts and users

**7. otp_tokens**
- One-time passwords for email verification
- Purpose: email_verification or password_reset
- Auto-expires after 5 minutes

**8. password_reset_tokens**
- Password reset tokens
- Expires after 24 hours

### Anonymized Views (No PII)

**1. commission_trends**
- Shows average deduction % by platform and month
- No individual worker data
- Used for advocate analytics

**2. income_distribution_by_zone**
- Shows earnings distribution by city zone and category
- Includes: median, p25, p75, avg_hourly_rate
- Used for advocate analytics

**3. verification_stats**
- Shows verification status counts
- Aggregated data only

---

## Relationships & Constraints

```
users (1) ──────► (1) workers
         (1) ──────► (many) earnings_entries
         (1) ──────► (many) otp_tokens
         (1) ──────► (many) password_reset_tokens
         (1) ──────► (many) grievance_posts (as commenter)
         (1) ──────► (many) grievance_comments

earnings_entries (many) ──────► (1) workers
                 (1) ──────► (0-1) screenshots

grievance_posts (1) ──────► (0-1) workers
               (1) ──────► (many) grievance_comments

grievance_comments (many) ──────► (1) grievance_posts
                  (many) ──────► (1) users
```

---

## Key Indexes

| Table | Indexes |
|-------|---------|
| **users** | email, role, created_at |
| **workers** | user_id, city_zone, primary_platform, category |
| **earnings_entries** | worker_id, entry_date, platform, verification_status, (worker_id, entry_date), (worker_id, platform) |
| **screenshots** | entry_id, verification_decision, verified_by, uploaded_at |
| **grievance_posts** | worker_id, platform, category, escalation_state, created_at, tags (GIN) |
| **grievance_comments** | post_id, user_id, created_at |
| **otp_tokens** | email, token, expiry |
| **password_reset_tokens** | user_id, token, expiry |

---

## Generated & Computed Columns

**deduction_percentage** (earnings_entries)
- Calculated as: `(platform_deductions / gross_earned) * 100`
- Generated automatically, not stored separately

**hourly_rate** (earnings_entries)
- Calculated as: `net_received / hours_worked`
- Generated automatically, not stored separately

These columns are always up-to-date and don't require manual updates.

---

## Row-Level Security (RLS)

The schema includes RLS policies (currently commented out). When enabled:

- Workers can only see/update their own data
- Verifiers can only verify what they're assigned
- Advocates can only see anonymized aggregates

To enable RLS policies, uncomment the RLS section in schema.sql.

---

## Backup & Recovery

### Create a Backup

```bash
# Full database backup
pg_dump -U postgres -d fairgig_db > fairgig_backup.sql

# Compress backup
pg_dump -U postgres -d fairgig_db | gzip > fairgig_backup.sql.gz
```

### Restore from Backup

```bash
# Full database restore
psql -U postgres -d fairgig_db -f fairgig_backup.sql

# Restore from compressed backup
gunzip -c fairgig_backup.sql.gz | psql -U postgres -d fairgig_db
```

---

## Common Issues & Troubleshooting

### Issue: PostgreSQL not installed or not running

**Solution**:
```bash
# macOS
brew install postgresql
brew services start postgresql

# Ubuntu/Debian
sudo apt-get install postgresql
sudo systemctl start postgresql

# Windows
# Use the PostgreSQL installer from postgresql.org
```

### Issue: "database fairgig_db does not exist"

**Solution**: Create the database first (Step 1)

### Issue: "permission denied"

**Solution**: Make sure you're connecting as a user with superuser privileges
```bash
psql -U postgres -d fairgig_db
```

### Issue: "could not connect to server"

**Solution**: Check if PostgreSQL is running
```bash
# macOS
brew services list

# Ubuntu/Debian
sudo systemctl status postgresql

# Windows
# Check Services in Control Panel or Task Manager for postgresql
```

### Issue: Schema import errors

**Solution**: Ensure the database is empty before importing
```bash
psql -U postgres -d fairgig_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
psql -U postgres -d fairgig_db -f schema.sql
```

---

## Next Steps

Once the database is set up and verified:

1. **Create a .env file** with database connection details
2. **Set up the Auth Service** (Phase 0.2) which will use this database
3. **Run seed scripts** to populate test data (optional)

### Create .env File

```bash
# In project root directory
cat > .env << EOF
DATABASE_URL=postgresql://postgres:password@localhost:5432/fairgig_db
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=fairgig_db
DATABASE_USER=postgres
DATABASE_PASSWORD=password
EOF
```

Replace `password` with your actual PostgreSQL password.

---

## Schema Maintenance

### Update User Password
```sql
UPDATE users
SET password_hash = 'new_hashed_password'
WHERE email = 'user@example.com';
```

### Clean Up Expired OTP Tokens
```sql
DELETE FROM otp_tokens
WHERE expiry < CURRENT_TIMESTAMP;
```

### Get Verification Statistics
```sql
SELECT
    verification_status,
    COUNT(*) as count,
    ROUND((COUNT(*)::FLOAT / (SELECT COUNT(*) FROM earnings_entries) * 100), 2) as percentage
FROM earnings_entries
GROUP BY verification_status;
```

### Get Worker Statistics
```sql
SELECT
    w.city_zone,
    w.category,
    COUNT(DISTINCT w.user_id) as worker_count,
    COUNT(ee.id) as total_entries,
    ROUND(AVG(ee.net_received)::NUMERIC, 2) as avg_earnings
FROM workers w
LEFT JOIN earnings_entries ee ON w.user_id = ee.worker_id
GROUP BY w.city_zone, w.category
ORDER BY w.city_zone;
```

---

## Exit psql

```bash
# From inside psql shell
\q

# Or use Ctrl+D
```

---

## Summary

You now have a fully functional PostgreSQL database for FairGig with:
- ✅ 8 core tables for users, earnings, verification, and grievances
- ✅ Proper indexes for query performance
- ✅ Foreign key constraints for data integrity
- ✅ Automatic timestamp management (created_at, updated_at)
- ✅ 3 anonymized views for advocate analytics (no PII exposure)
- ✅ 4 utility functions and triggers
- ✅ Support for Row-Level Security (optional)

Next: Set up the Auth Service (Phase 0.2) in the IMPLEMENTATION_ROADMAP.
