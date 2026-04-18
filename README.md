# FairGig: A Platform for Pakistan's Gig Workers

FairGig is a comprehensive platform designed to empower gig workers in Pakistan—including ride-hailing drivers, delivery riders, freelancers, and domestic workers—with the tools to track earnings, prove income to financial institutions and landlords, and collectively identify systemic unfairness in their work.

## The Problem

Pakistan's gig workers operate in a fragmented ecosystem with no unified way to log income, no verifiable proof of earnings for banks or landlords, and no protection when platforms cut rates silently or deactivate accounts without notice. Workers lack transparency into their own earning trends, and advocates have no data-driven way to spot and respond to exploitative practices at scale.

## The Solution

FairGig solves this by creating a transparent, worker-centric ecosystem with three core functions:

- **For Gig Workers**: Log every shift, understand earnings trends, generate verified income certificates, and access community insights about platform practices.
- **For Verifiers**: Review worker-submitted evidence and stamp approval onto their earnings record, creating trust for third parties.
- **For Advocates and Analysts**: Access aggregated, anonymised data to spot commission cuts, identify vulnerable workers, and detect platform-wide unfairness patterns.

---

## Core User Roles

### Gig Worker (Primary User)

The gig worker is the platform's core user. They:

- Log shift data manually through an intuitive form (platform name, date, hours, gross earned, deductions, net received) or bulk import via CSV
- Upload screenshots from their platform apps for independent verification
- View personalized analytics including weekly/monthly trends, effective hourly rates, commission changes, and how their earnings compare to the anonymised city-wide median for their job category
- Generate and download a shareable income certificate to present to landlords or banks
- Post and read updates on the community grievance board to stay informed about rate changes and platform practices

The platform must be usable by workers who are not highly tech-savvy. Clear feedback, simple navigation, Urdu/English bilingual support, and mobile-friendly design are essential.

### Verifier

Verifiers are trusted reviewers (NGO staff, labour advocates, or certified auditors) who:

- Review worker-submitted screenshots in a verification queue
- Make one of three decisions for each submission:
  - **Approve**: The screenshot matches the logged numbers
  - **Flag Discrepancy**: The screenshot contradicts the logged numbers
  - **Mark Unverifiable**: The screenshot is too blurry, cropped, or unclear to judge
- Have their decision permanently stamped onto the worker's profile and certificate

### Advocate/Analyst

Labour rights professionals and researchers who:

- Access an aggregate analytics dashboard showing no individual worker data
- Monitor commission trends across platforms month-to-month
- Analyze income distribution by city zone and job category
- Track top complaint categories and emerging worker vulnerabilities
- Identify workers whose income dropped more than 20% month-on-month for outreach and support
- Use these insights to build cases for policy change or platform accountability

### Worker Community

An anonymous bulletin board where:

- Workers post rate intelligence ("Careem dropped per-km rate in Gulberg on 15 March") and complaints
- Advocates can tag posts, group similar ones into clusters, and escalate systemic issues
- Workers find solidarity and real-time information about platform changes

---

## Core Features

### 1. Earnings Logger

A flexible entry system where workers record shift data with full transparency into what they earn and what platforms take.

**Manual Entry**: A form captures platform name, date, hours worked, gross earnings, platform deductions, and net received. Form validation ensures data quality; users get clear feedback on every entry.

**Bulk CSV Import**: Tech-savvy workers can upload a CSV file with the same fields. The system validates the file, shows preview with any errors flagged, and lets the worker confirm before importing all entries at once.

**Data Storage**: All entries are stored with a reference link to any associated screenshots and a verification status (pending, approved, flagged, unverifiable). Workers can edit or delete their own entries before they're verified.

### 2. Screenshot Verification Flow

Workers upload evidence from their platform app. The verification process ensures data credibility.

**Upload**: Worker selects and uploads a screenshot. The system validates file format and size, assigns a unique reference, and queues it for verification.

**Verifier Review**: A dedicated verifier queue shows pending screenshots one at a time. The verifier sees:
- The screenshot image
- The associated logged earnings data (platform, date, hours, amounts)
- A simple decision form with radio buttons: Approve / Flag Discrepancy / Mark Unverifiable

**Decision Recording**: Once decided, the outcome is locked onto that entry's record. Workers see their verification status on their profile and can include approved/flagged entries in their income certificate.

**Optional OCR Enhancement**: To speed up verification, the system can use OCR (Tesseract.js or Python) to auto-read numbers from screenshots and pre-populate the verification form, keeping a human reviewer in the loop for final approval.

### 3. Income Analytics Dashboard (Worker View)

Workers gain visibility into their own income patterns and how they compare to their peers.

**Time-Series Charts**:
- Weekly earnings trend (line chart over the past 12 weeks)
- Monthly earnings comparison (bar chart showing gross vs. net)
- Effective hourly rate over time (rolling 4-week average)

**Commission Tracking**: A line chart showing how the platform's deduction percentage has changed over the worker's history. Workers can spot when a platform cut its rates.

**Peer Comparison**: A critical feature—how does this worker's earnings compare to the anonymised city-wide median for their job category and platform? This must be computed from real seeded data in the database, not hardcoded. For example: "Your average hourly rate as a Careem driver in Karachi is PKR 450. The median for your zone is PKR 475."

**Data Recency**: The dashboard updates as new entries are logged. Workers see "Last updated: 2 hours ago" so they know the data is current.

### 4. Shareable Income Certificate

A clean, printable document that workers can generate for any date range and share with landlords, banks, or employers.

**Content**:
- Worker name and verified status (e.g., "50 entries verified by labour advocate")
- Date range of earnings covered
- Summary table: date, platform, hours, gross, deductions, net
- Total summary: total hours, total gross, total deductions, total net, effective hourly rate
- Verification stamp: How many entries were approved vs. flagged vs. unverifiable; date of most recent verification
- Issuer note: "This certificate is issued by FairGig, an independent earnings verification platform."

**Print-Ready Design**: Built with `@media print` CSS so it renders cleanly with Ctrl+P or Print → Save as PDF. No navigation bars, no clutter—just the certificate content.

**Optional PDF Download**: Server-side PDF generation using WeasyPrint allows one-click download without relying on browser print dialog.

### 5. Grievance Board (Community Insights)

An anonymous message board where workers share rate intelligence and complaints; advocates moderate and escalate.

**Worker Posting**:
- Platform name (required dropdown)
- Category: Rate Cut / Wrongful Deactivation / Technical Issue / Other
- Description (required, text area)
- Anonymous by default; optional verified worker badge if they allow it

**Post Visibility**: All posts are public to workers and advocates. No login required to read (read-only access for guests).

**Advocate Moderation**:
- View all posts with metadata (creation date, category, vote count)
- Add tags to a post (e.g., "Careem", "Urgent", "Duplicate")
- Mark posts as Escalated or Resolved
- Manually group similar posts or use keyword clustering to auto-suggest duplicates

**Community Engagement**: Workers can upvote helpful posts. The top posts (by votes and recency) are featured at the top of the board.

### 6. Advocate Analytics Panel

A restricted dashboard (advocates only) that shows aggregated, anonymised trends. Individual worker PII never leaves the earnings service.

**Commission Trends**: Line chart showing the average platform deduction percentage over time for each major platform (Careem, Uber, Shopee, etc.). Advocates spot rate cuts and market shifts.

**Income Distribution**: Box plot or histogram showing income distribution by city zone (Karachi, Lahore, Islamabad, etc.) and job category (ride-hailing, delivery, freelance). Reveals inequality and regional variation.

**Top Complaint Categories This Week**: A bar chart showing which grievance categories (rate cut, deactivation, etc.) are most common right now. Helps advocates prioritize response.

**Vulnerability List**: Workers whose income dropped more than 20% month-on-month, sorted by severity. Advocates can export this list for outreach campaigns.

**Data Anonymity**: All data is aggregated (counts, averages, medians, percentiles). No individual worker records are visible. Advocates never see personally identifiable information—only aggregated statistics.

### 7. Anomaly Detection Service

A dedicated microservice that workers and judges can call to get intelligent feedback on suspicious earnings patterns.

**Input**: Worker ID and recent earnings history (last 30-90 days of shift logs).

**Output**: A JSON response flagging anomalies with plain-English explanations:

```json
{
  "anomalies": [
    {
      "date": "2026-04-12",
      "type": "deduction_outlier",
      "explanation": "Your platform deduction on 12 April was 3.2 standard deviations above your 30-day average (34% vs. your normal 22%). This may indicate a platform surge charge or subscription fee."
    },
    {
      "date": "2026-04-18",
      "type": "income_drop",
      "explanation": "Your earnings dropped 35% from last month (PKR 28,000 → PKR 18,200). This could signal reduced order volume, fewer working hours, or a platform rate cut."
    }
  ]
}
```

**Algorithm**:
- Z-score analysis on deductions (flag if > 2.5 standard deviations from 30-day mean)
- Month-on-month income percentage change (flag if > 20% drop)
- Optional: working hours anomaly detection (sudden reduction may signal platform throttling)
- Optional: cross-worker clustering to surface platform-wide patterns

**Use Case**: Judges will call this endpoint directly during evaluation with a test payload. The endpoint must have clean input/output schema documentation and handle edge cases (new worker with <7 days of history, worker with no deductions, etc.).

---

## System Architecture

FairGig is built as a set of independent microservices communicating over REST APIs. Each service is independently executable and has a single start command.

### Service Breakdown

#### 1. Auth Service (FastAPI)

**Responsibility**: JWT-based authentication, role assignment, and token refresh.

**Endpoints**:
- `POST /auth/register`: Create a new account (worker, verifier, or advocate)
- `POST /auth/login`: Issue JWT token on successful login
- `POST /auth/refresh`: Refresh an expired token
- `GET /auth/verify`: Validate and decode a JWT token
- `POST /auth/otp/send`: Send OTP to email via MailHog (development)
- `POST /auth/otp/verify`: Verify OTP and issue token

**Database**: Stores user credentials (hashed), roles, email, and OTP state.

**Security**: Passwords are hashed with bcrypt. JWTs are signed with a secret key and include role information. OTP is stored with a short expiry (5 minutes).

**MailHog Integration**: In development, OTP emails are sent to MailHog (no external SMTP). MailHog runs on `localhost:1025` (SMTP) and `localhost:8025` (web UI).

#### 2. Earnings Service (FastAPI or your choice)

**Responsibility**: All CRUD operations for shift logs, CSV upload processing, and verification status tracking.

**Endpoints**:
- `POST /earnings/entry`: Create a new shift entry
- `GET /earnings/entry/{id}`: Retrieve a single entry
- `PUT /earnings/entry/{id}`: Update an entry (before verification)
- `DELETE /earnings/entry/{id}`: Delete an entry (before verification)
- `GET /earnings/worker/{worker_id}`: List all entries for a worker
- `POST /earnings/bulk-import`: Upload and process CSV file
- `GET /earnings/analytics/worker/{worker_id}`: Get worker's personal analytics (trends, medians)

**Data Model**:
```
Entry {
  id: UUID,
  worker_id: UUID,
  platform: String (Careem, Uber, Shopee, etc.),
  date: Date,
  hours: Float,
  gross_earned: Decimal,
  deductions: Decimal,
  net_received: Decimal,
  screenshot_ref: String (nullable, reference to verification service),
  verification_status: Enum (pending, approved, flagged, unverifiable),
  created_at: DateTime,
  updated_at: DateTime
}
```

**CSV Import**: Validates file structure, previews data, detects duplicates, and bulk-inserts approved entries. Errors are reported line-by-line.

**Analytics Query**: Computes aggregates from real seeded data—weekly totals, hourly rates, platform deduction trends, and peer comparisons (anonymised median for the same zone + platform + job category).

#### 3. Anomaly Service (Python FastAPI)

**Responsibility**: Statistical anomaly detection on individual worker earnings.

**Endpoint**:
- `POST /anomalies/detect`: Accept worker earnings history, return flagged anomalies

**Input Schema**:
```json
{
  "worker_id": "uuid",
  "entries": [
    {
      "date": "2026-04-10",
      "hours": 8,
      "gross": 2500,
      "deductions": 550,
      "net": 1950
    }
  ]
}
```

**Output Schema**:
```json
{
  "worker_id": "uuid",
  "anomalies": [
    {
      "date": "2026-04-12",
      "type": "deduction_outlier",
      "severity": "medium",
      "explanation": "Your platform deduction on 12 April was 3.2 standard deviations above your 30-day average (34% vs. your normal 22%)."
    }
  ]
}
```

**Algorithm**:
- Deduction Z-score: Calculate mean and std dev of deduction % over the past 30 days. Flag entries where z-score > 2.5.
- Income Drop: Compare this month's total earnings to last month's. Flag if drop > 20%.
- Hours Anomaly: Check if recent working hours are significantly lower than historical average (platform may be throttling orders).

**Edge Cases**: Handle workers with < 7 days of history, zero deductions, missing data gracefully. Return empty anomalies list if data is insufficient.

#### 4. Grievance Service (Node.js)

**Responsibility**: Complaint CRUD, tagging, clustering, and escalation state management.

**Endpoints**:
- `POST /grievance/post`: Create a new complaint
- `GET /grievance/post/{id}`: Retrieve a single complaint
- `PUT /grievance/post/{id}`: Update a complaint (author only)
- `DELETE /grievance/post/{id}`: Delete a complaint (author or advocate)
- `GET /grievance/posts`: List all posts with pagination and filtering
- `POST /grievance/post/{id}/upvote`: Upvote a post
- `PUT /grievance/post/{id}/tags`: Add/remove tags (advocate only)
- `PUT /grievance/post/{id}/escalate`: Mark as escalated (advocate only)
- `POST /grievance/clustering`: Auto-suggest similar posts based on keyword similarity
- `GET /grievance/analytics`: Top categories, top posts, escalation stats (advocate only)

**Data Model**:
```
Post {
  id: UUID,
  worker_id: UUID (nullable for anonymous),
  platform: String,
  category: Enum (rate_cut, deactivation, technical_issue, other),
  description: String,
  tags: Array<String>,
  escalation_state: Enum (open, escalated, resolved),
  upvote_count: Integer,
  created_at: DateTime,
  updated_at: DateTime
}
```

**Clustering**: Simple TF-IDF on complaint descriptions; suggest posts with cosine similarity > 0.75 as potential duplicates.

**Moderation Workflow**: Advocates can read all posts, add tags, and transition escalation state. Workers see public posts only.

#### 5. Analytics Service

**Responsibility**: Aggregate queries for the advocate dashboard. Queries only anonymised, aggregate data from earnings and grievance services.

**Endpoints**:
- `GET /analytics/commissions/trends`: Commission % trends by platform over time
- `GET /analytics/income/distribution`: Income distribution by zone + category
- `GET /analytics/grievance/categories`: Top complaint categories this week
- `GET /analytics/vulnerable-workers`: Workers with >20% month-on-month income drop

**Data Fetch Pattern**: The analytics service does not store data. On each request, it queries the Earnings Service for individual records, computes aggregates in-memory, and returns only the summary statistics to the advocate. Individual worker records never appear in the response.

**Anonymisation**: Results are returned as:
- Commission trends: `{"platform": "Careem", "date": "2026-04", "avg_deduction_pct": 24.5}`
- Income distribution: `{"zone": "Karachi", "category": "delivery", "median": 18000, "p25": 12000, "p75": 28000}`
- Vulnerable workers: `{"count": 47}` (only counts, no names or IDs)

#### 6. Certificate Renderer Service

**Responsibility**: Generate printable income certificates for workers.

**Endpoint**:
- `GET /certificate/generate/{worker_id}?from=2026-01-01&to=2026-04-30`: Return HTML certificate

**Response**: Clean HTML page with `@media print` CSS. Browser can print or save as PDF directly. Optional server-side PDF generation with WeasyPrint.

**Content**: Worker name, verified entry count, date range, earnings table, totals, verification stamp.

#### 7. Frontend (React or Angular)

**Responsibility**: User-facing web application for workers, verifiers, and advocates.

**Routes (Worker)**:
- `/login`: Login page
- `/register`: Sign-up page
- `/dashboard`: Personal earnings summary and charts
- `/log-entry`: Manual entry form
- `/bulk-import`: CSV upload
- `/verify-status`: View verification queue status
- `/certificate`: Generate and download income certificate
- `/grievance-board`: Read and post community complaints

**Routes (Verifier)**:
- `/verify-queue`: Queue of pending screenshots
- `/verify/{entry_id}`: Individual screenshot verification
- `/stats`: Verification stats (submissions reviewed, accuracy)

**Routes (Advocate)**:
- `/analytics`: Aggregate dashboard (commissions, income, complaints, vulnerabilities)
- `/grievance-moderation`: Tag and escalate posts
- `/export`: Export data for analysis

**Technology Stack**:
- React or Angular
- Tailwind CSS for responsive design (mobile, tablet, desktop)
- Urdu/English bilingual UI where feasible
- Form validation and error handling
- Charts (Chart.js or Recharts for React; ng-charts for Angular)
- HTTP client to call backend services

---

## Technical Constraints

### Mandatory Requirements

**Anomaly Service**: Must be Python FastAPI. This is non-negotiable and will be tested by judges.

**Grievance Service**: Must be Node.js. This is non-negotiable and will be tested by judges.

**Second FastAPI Service**: At least one other backend service (recommended: Auth or Earnings) must also be FastAPI.

**Frontend**: Must be React or Angular. No WordPress, Webflow, or no-code builders.

**No Docker**: Every service must be independently executable with a single start command. Each service has its own README with setup and run instructions.

**Database**: PostgreSQL is used for this project. It provides SQL views for anonymisation, row-level security, strong ACID guarantees, and jsonb support for flexible metadata storage.

**Seeded Data**: The city-wide median comparison on the worker dashboard must be computed from real seeded records in the database (at least a few hundred entries across multiple zones, platforms, and categories), not hardcoded constants.

**API Documentation**: All inter-service endpoints must be documented. A Postman collection, OpenAPI/Swagger spec, or even a markdown table is acceptable. Include endpoint URL, HTTP method, required headers (Auth token), request shape, response shape, and possible error codes.

**Income Certificate Print**: Must work with browser print (Ctrl+P). Use `@media print` CSS to hide navigation and format for paper. Tested by printing to PDF.

### Development Tools

**MailHog**: Used for OTP testing in development. Auth service sends OTP emails to MailHog's SMTP endpoint. No real email sending during development.

**Tailwind CSS**: Use for responsive design. All UI components must be mobile-friendly (tests will include mobile and desktop viewports).

**Seeding Script**: Provide a standalone script (Python or Node) that populates the database with realistic test data:
- 500+ earnings entries across multiple workers, platforms (Careem, Uber, Shopee, InDrive), zones (Karachi, Lahore, Islamabad, Peshawar), and categories (ride-hailing, delivery, freelance)
- 100+ grievance posts with realistic content
- Verification statuses mixed (approved, flagged, unverifiable, pending)

---

## Project Structure

```
fastgig/
├── auth-service/
│   ├── main.py
│   ├── requirements.txt
│   ├── README.md
│   ├── config.py
│   └── ...
├── earnings-service/
│   ├── main.py
│   ├── requirements.txt
│   ├── README.md
│   └── ...
├── anomaly-service/
│   ├── main.py
│   ├── requirements.txt
│   ├── README.md
│   └── ...
├── grievance-service/
│   ├── package.json
│   ├── README.md
│   ├── server.js
│   └── ...
├── analytics-service/
│   ├── main.py (or index.js)
│   ├── requirements.txt (or package.json)
│   ├── README.md
│   └── ...
├── certificate-renderer/
│   ├── main.py (or index.js)
│   ├── requirements.txt (or package.json)
│   ├── README.md
│   └── ...
├── frontend/
│   ├── package.json
│   ├── README.md
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── ...
│   └── ...
├── database/
│   ├── seed.py (or seed.js)
│   ├── schema.sql
│   └── README.md
├── docs/
│   ├── API.md (all endpoints documented)
│   ├── ARCHITECTURE.md
│   └── SETUP.md
└── README.md (this file)
```

---

## Getting Started

### Prerequisites

- Python 3.9+ (for Python services)
- Node.js 16+ (for Grievance Service and Frontend)
- PostgreSQL (see database section)
- MailHog (for OTP testing in development)
- Git

### Setup Overview

1. Clone the repository
2. Set up the database and run seeding script
3. Start MailHog for email testing
4. Start each backend service in separate terminals
5. Start the frontend in another terminal
6. Access the application at `http://localhost:3000` (frontend default)

### Detailed Setup

#### Step 1: Clone and Install Dependencies

```bash
git clone <repository-url>
cd fastgig

# Auth Service
cd auth-service
pip install -r requirements.txt
cd ..

# Earnings Service
cd earnings-service
pip install -r requirements.txt
cd ..

# Anomaly Service
cd anomaly-service
pip install -r requirements.txt
cd ..

# Grievance Service
cd grievance-service
npm install
cd ..

# Frontend
cd frontend
npm install
cd ..
```

#### Step 2: Database Setup

Choose one of the following:

**PostgreSQL Setup**

```bash
# Create database
createdb fairgig_db

# Run schema
psql fairgig_db < database/schema.sql

# Run seeding script
cd database
python seed.py --platform postgresql
cd ..
```

Create a `.env` file in each service with your database URL:

```
DATABASE_URL=postgresql://user:password@localhost/fairgig_db
```

#### Step 3: Start MailHog

```bash
# Download MailHog from https://github.com/mailhog/MailHog/releases
# Or install via Homebrew: brew install mailhog

mailhog
# SMTP server runs on localhost:1025
# Web UI runs on http://localhost:8025
```

#### Step 4: Start Backend Services

Open a terminal for each service:

**Terminal 1: Auth Service**
```bash
cd auth-service
python main.py
# Runs on http://localhost:8001
```

**Terminal 2: Earnings Service**
```bash
cd earnings-service
python main.py
# Runs on http://localhost:8002
```

**Terminal 3: Anomaly Service**
```bash
cd anomaly-service
python main.py
# Runs on http://localhost:8003
```

**Terminal 4: Grievance Service**
```bash
cd grievance-service
npm start
# Runs on http://localhost:8004
```

**Terminal 5: Analytics Service**
```bash
cd analytics-service
python main.py
# Runs on http://localhost:8005
```

**Terminal 6: Certificate Renderer**
```bash
cd certificate-renderer
python main.py
# Runs on http://localhost:8006
```

#### Step 5: Start Frontend

```bash
cd frontend
npm start
# Runs on http://localhost:3000
```

#### Step 6: Access the Application

- **Frontend**: http://localhost:3000
- **Auth Service Docs**: http://localhost:8001/docs (Swagger)
- **Earnings Service Docs**: http://localhost:8002/docs
- **Anomaly Service Docs**: http://localhost:8003/docs
- **Grievance Service Docs**: http://localhost:8004/docs
- **MailHog Web UI**: http://localhost:8025 (view OTP emails)

### Test Credentials

After seeding, use these to log in:

```
Worker:
  Email: worker1@example.com
  Password: password123

Verifier:
  Email: verifier@example.com
  Password: password123

Advocate:
  Email: advocate@example.com
  Password: password123
```

---

## API Documentation

Full inter-service API contracts are documented in docs/API.md.

### Quick Reference

**Auth Service**
- `POST /auth/register` - Create account
- `POST /auth/login` - Issue token
- `POST /auth/otp/send` - Send OTP
- `POST /auth/otp/verify` - Verify OTP
- `POST /auth/refresh` - Refresh token
- `GET /auth/verify` - Validate token

**Earnings Service**
- `POST /earnings/entry` - Create entry
- `GET /earnings/worker/{worker_id}` - List entries
- `PUT /earnings/entry/{id}` - Update entry
- `DELETE /earnings/entry/{id}` - Delete entry
- `POST /earnings/bulk-import` - CSV upload
- `GET /earnings/analytics/worker/{worker_id}` - Personal analytics

**Anomaly Service**
- `POST /anomalies/detect` - Detect anomalies in earnings history

**Grievance Service**
- `POST /grievance/post` - Create post
- `GET /grievance/posts` - List posts
- `PUT /grievance/post/{id}` - Update post
- `PUT /grievance/post/{id}/tags` - Add tags (advocate only)
- `PUT /grievance/post/{id}/escalate` - Escalate (advocate only)
- `POST /grievance/clustering` - Suggest similar posts

**Analytics Service**
- `GET /analytics/commissions/trends` - Commission trends (advocate only)
- `GET /analytics/income/distribution` - Income distribution (advocate only)
- `GET /analytics/grievance/categories` - Top complaint categories (advocate only)
- `GET /analytics/vulnerable-workers` - At-risk workers (advocate only)

**Certificate Renderer**
- `GET /certificate/generate/{worker_id}` - Generate certificate (worker only)

---

## Database Choice Justification

### PostgreSQL (Recommended for Privacy)

PostgreSQL is the database of choice because:

1. **SQL Views for Anonymisation**: The analytics service can use SQL views to compute aggregates without ever selecting individual worker records. Example:

```sql
CREATE VIEW commission_trends AS
SELECT 
  platform,
  DATE_TRUNC('month', date) as month,
  AVG(deductions / NULLIF(gross_earned, 0)) as avg_deduction_pct,
  COUNT(*) as entry_count
FROM earnings
GROUP BY platform, DATE_TRUNC('month', date)
ORDER BY month DESC;
```

The analytics service queries only this view and never touches the raw earnings table, ensuring no PII leaks.

2. **Row-Level Security (RLS)**: PostgreSQL supports row-level security policies, so a worker can never see another worker's data even if they gain direct database access.

3. **Strong ACID Guarantees**: Earnings data is financial information; ACID compliance is critical.

4. **Jsonb for Flexible Metadata**: Platform-specific metadata (e.g., Careem bonus structure) can be stored as jsonb with fast querying.

---

## Beyond the Requirements: Optional Enhancements

While the core platform meets all SOFTEC 2026 requirements, several enhancements would strengthen the platform and impress evaluators.

### 1. OCR for Screenshot Verification

Add Tesseract.js (JavaScript) or pytesseract (Python) to pre-fill verification forms from screenshots. The system reads numbers from uploaded images and populates the earnings data fields, letting verifiers confirm in seconds instead of manually re-entering data. Keeps humans in the loop for the final decision.

### 2. PDF Export for Income Certificates

Extend the certificate renderer to support one-click PDF download using WeasyPrint (Python) or Puppeteer (Node.js). Workers can email the certificate directly without relying on browser print dialog.

### 3. Advanced Anomaly Detection

Go beyond simple z-scores. Implement rolling averages, seasonal adjustment, cross-worker clustering, or machine learning techniques like isolation forests for non-linear anomaly detection.

### 4. Keyword Clustering for Complaints

Automatically group similar grievance posts using TF-IDF + Cosine Similarity, LDA Topic Modeling, or other NLP techniques.

### 5. Differential Privacy for Analytics

Add statistical noise to aggregate results so no individual worker's data can be reverse-engineered.

### 6. Urdu/English Bilingual UI

Add bilingual support for worker-facing views using i18n frameworks (react-i18next for React; ngx-translate for Angular).

### 7. SMS Notifications

For workers without reliable email, add SMS notifications via Twilio API or similar, with MailHog SMS mock for development.

### 8. Mobile App

Build a React Native or Flutter mobile app sharing API calls with the web frontend.

### 9. Real-Time Collaboration for Advocates

WebSocket-based real-time updates so multiple advocates see changes as they happen.

### 10. Export to Power BI / Tableau

Allow advocates to export anonymised analytics data in formats compatible with BI tools.

---

## Data Privacy & Security

### PII Protection

- Worker names, email addresses, and phone numbers are stored in the Auth Service only
- Earnings Service stores only `worker_id` (UUID), not names or contact info
- Grievance Service stores `worker_id` optionally (posts can be anonymous)
- Analytics Service computes aggregates and returns only statistics
- No analytics query result includes individual worker records or PII

### Encryption

- Passwords: Bcrypt hashing (12 rounds)
- Data in transit: HTTPS/TLS (enforce in production)
- Sensitive config: Environment variables, never hardcoded

### JWT Security

- Tokens signed with a strong secret key
- Short expiry (15 minutes); refresh tokens for long sessions
- Role information embedded in token (worker, verifier, advocate)
- Tokens validated on every protected endpoint

### Rate Limiting

- Auth endpoints rate-limited to prevent brute-force attacks (5 attempts per minute per IP)
- API endpoints rate-limited per user (100 requests per minute for workers, 1000 for advocates)

---

## Testing Strategy

### Unit Tests

Each service includes unit tests for business logic, input validation, and error handling.

Run with: `pytest` (Python) or `npm test` (Node.js)

### Integration Tests

Test inter-service communication (Auth → Earnings token validation, Earnings → Analytics aggregate correctness, Frontend → Backend workflows).

### Load Testing

Simulate advocate dashboard query load with 500+ workers' data. Analytics endpoint must respond in < 2 seconds.

---

## Deployment Notes

### For Production

1. Use managed databases (AWS RDS PostgreSQL, Google Cloud SQL, Azure Database for PostgreSQL)
2. Deploy services to cloud (AWS Lambda, Google Cloud Run, Heroku, DigitalOcean, etc.)
3. Enable HTTPS everywhere; redirect HTTP to HTTPS
4. Use environment-specific config (.env for dev, secrets manager for prod)
5. Set up logging and monitoring (CloudWatch, DataDog, Sentry for error tracking)
6. Implement database backups and disaster recovery plan
7. Use a reverse proxy (Nginx) to manage CORS and rate limiting centrally

### For Development

Services run on localhost on different ports. No Docker needed; each service is independently executable with straightforward setup.

---

## Contributing

Developers should:

1. Clone the repository
2. Follow setup instructions above
3. Create a feature branch: `git checkout -b feature/your-feature`
4. Write unit tests for new logic
5. Ensure all tests pass: `pytest` or `npm test`
6. Submit a pull request with a clear description

---

## License

FairGig is built for the SOFTEC 2026 competition as part of a broader mission to empower gig workers in Pakistan.

---

## Contact & Support

For questions about the platform architecture, features, or deployment, refer to the detailed READMEs in each service folder and the comprehensive API documentation in docs/API.md.

---

**Last Updated**: April 2026  
**Version**: 1.0.0  
**Platform**: Gig Economy Fairness & Transparency
