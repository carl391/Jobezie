# Jobezie Platform - Comprehensive Technical Overview

**Generated:** February 5, 2026
**Version:** 2.0.0 (Full Build)
**Repository:** Jobezie AI Career Assistant

---

## Table of Contents
1. [Project Structure](#1-project-structure)
2. [Technical Architecture](#2-technical-architecture)
3. [API Endpoints Inventory](#3-api-endpoints-inventory)
4. [Algorithm Implementations](#4-algorithm-implementations)
5. [Database Schema](#5-database-schema)
6. [Frontend Status](#6-frontend-status)
7. [Configuration & Environment](#7-configuration--environment)
8. [Dependencies](#8-dependencies)
9. [Testing](#9-testing)
10. [Production Readiness Assessment](#10-production-readiness-assessment)
11. [Recommended Next Steps](#11-recommended-next-steps)

---

## 1. Project Structure

```
Jobezie/
├── app/                              # Backend Flask Application
│   ├── __init__.py                   # Flask app factory, blueprints, error handlers
│   ├── config.py                     # Environment configurations (dev/test/prod)
│   ├── extensions.py                 # Flask extensions initialization
│   │
│   ├── models/                       # SQLAlchemy Models (5 files)
│   │   ├── __init__.py
│   │   ├── user.py                   # User model (lines: 334) - auth, subscriptions, usage
│   │   ├── resume.py                 # Resume, ResumeVersion models (lines: 214)
│   │   ├── recruiter.py              # Recruiter, RecruiterNote models
│   │   ├── message.py                # Message model with quality scoring
│   │   └── activity.py               # Activity, PipelineItem models
│   │
│   ├── routes/                       # API Route Blueprints (10 files)
│   │   ├── __init__.py
│   │   ├── auth.py                   # 12 endpoints - authentication
│   │   ├── resume.py                 # 9 endpoints - resume management
│   │   ├── recruiter.py              # 17 endpoints - CRM operations
│   │   ├── message.py                # 14 endpoints - message management
│   │   ├── activity.py               # 11 endpoints - activity tracking
│   │   ├── dashboard.py              # 3 endpoints - stats & readiness
│   │   ├── ai.py                     # 5 endpoints - AI operations
│   │   ├── linkedin.py               # 7 endpoints - LinkedIn tools
│   │   ├── labor_market.py           # 6 endpoints - market intelligence
│   │   └── subscription.py           # 7 endpoints - Stripe integration
│   │
│   ├── services/                     # Business Logic Services
│   │   ├── __init__.py
│   │   ├── ai_service.py             # Claude/OpenAI integration (lines: 609)
│   │   ├── resume_service.py         # Upload, parse, score (lines: 529)
│   │   ├── recruiter_service.py      # CRM logic, engagement calculation
│   │   ├── message_service.py        # Quality scoring, templates
│   │   ├── activity_service.py       # Timeline, pipeline tracking
│   │   ├── linkedin_service.py       # Profile optimization
│   │   ├── labor_market_service.py   # Market data, salary benchmarks
│   │   ├── stripe_service.py         # Subscription management (lines: 509)
│   │   ├── email_service.py          # SendGrid templates (lines: 409)
│   │   │
│   │   └── scoring/                  # Scoring Algorithm Modules
│   │       ├── __init__.py
│   │       ├── ats.py                # ATS scoring (lines: 503)
│   │       ├── message.py            # Message quality scoring (lines: 380)
│   │       ├── engagement.py         # Engagement & fit scoring
│   │       └── readiness.py          # Career readiness (lines: 333)
│   │
│   └── utils/                        # Utility Modules
│       ├── __init__.py
│       ├── validators.py             # Input validation, XSS/SQLi protection
│       └── decorators.py             # @admin_required, @subscription_required
│
├── frontend/                         # React Frontend Application
│   ├── src/
│   │   ├── App.tsx                   # Router, QueryClient, protected routes
│   │   ├── main.tsx                  # Application entry point
│   │   │
│   │   ├── contexts/                 # React Context Providers
│   │   │   ├── AuthContext.tsx       # JWT auth state management
│   │   │   └── TourContext.tsx       # Interactive tour state
│   │   │
│   │   ├── lib/
│   │   │   └── api.ts                # Axios client, 10 API service groups (lines: 273)
│   │   │
│   │   ├── types/
│   │   │   └── index.ts              # 25+ TypeScript interfaces (lines: 254)
│   │   │
│   │   ├── pages/                    # Page Components (11 files)
│   │   │   ├── Login.tsx             # ✅ Complete
│   │   │   ├── Register.tsx          # ✅ Complete
│   │   │   ├── Dashboard.tsx         # ✅ Complete
│   │   │   ├── Resumes.tsx           # ✅ Complete
│   │   │   ├── Recruiters.tsx        # ✅ Complete (lines: 235)
│   │   │   ├── Messages.tsx          # ✅ Complete
│   │   │   ├── Activity.tsx          # ✅ Complete
│   │   │   ├── AICoach.tsx           # ✅ Complete
│   │   │   ├── Settings.tsx          # ✅ Complete
│   │   │   ├── Onboarding.tsx        # ✅ Complete
│   │   │   └── Learn.tsx             # ✅ Complete - Interactive tours
│   │   │
│   │   ├── components/               # Reusable Components
│   │   │   ├── Layout.tsx            # App shell, sidebar, navigation
│   │   │   ├── ProtectedRoute.tsx    # Auth wrapper
│   │   │   ├── ui/                   # Modal, ScoreCircle, ScoreBar, Tabs, Badge
│   │   │   ├── messages/             # ComposeMessageModal, MessageCard
│   │   │   ├── resumes/              # ViewResumeModal, ATSScoreModal
│   │   │   ├── recruiters/           # AddRecruiterModal, RecruiterDetailsModal
│   │   │   └── onboarding/           # 7-step onboarding flow
│   │   │
│   │   ├── config/
│   │   │   └── tours.ts              # Tour definitions for each feature
│   │   │
│   │   └── styles/
│   │       ├── index.css             # Global styles, Tailwind directives
│   │       └── tour.css              # Tour-specific styling
│   │
│   ├── package.json                  # Frontend dependencies
│   ├── vite.config.ts                # Vite configuration
│   ├── tailwind.config.js            # Tailwind CSS configuration
│   └── tsconfig.json                 # TypeScript configuration
│
├── tests/                            # Test Suite
│   ├── __init__.py
│   ├── conftest.py                   # Pytest fixtures
│   ├── test_scoring.py               # Scoring algorithm tests
│   ├── test_routes_phase2.py         # Route integration tests
│   ├── test_models_phase2.py         # Model tests
│   └── unit/
│       ├── __init__.py
│       ├── test_auth.py              # Auth flow tests
│       ├── test_user_model.py        # User model tests
│       └── test_validators.py        # Validator tests
│
├── migrations/                       # Alembic Database Migrations
│   ├── versions/                     # Migration files
│   ├── env.py
│   └── alembic.ini
│
├── docker-compose.yml                # Docker development setup (lines: 159)
├── Dockerfile                        # Backend container
├── render.yaml                       # Render.com deployment blueprint (lines: 83)
├── requirements.txt                  # Python dependencies (lines: 72)
├── run.py                            # Development server entry
├── celery_app.py                     # Celery worker configuration
├── CLAUDE.md                         # AI assistant instructions
└── .env.example                      # Environment variable template
```

---

## 2. Technical Architecture

### 2.1 Backend Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Framework** | Flask | 3.0.0 | Web application framework |
| **ORM** | SQLAlchemy | 2.0.36 | Database abstraction |
| **Database** | PostgreSQL | 15 | Primary data store |
| **Cache** | Redis | 7.x | Caching, rate limiting, sessions |
| **Authentication** | Flask-JWT-Extended | 4.6.0 | JWT token management |
| **Task Queue** | Celery | 5.3.6 | Background job processing |
| **Rate Limiting** | Flask-Limiter | 3.5.0 | API rate limiting |
| **CORS** | Flask-CORS | 4.0.0 | Cross-origin resource sharing |
| **Migrations** | Alembic | 1.14.0 | Database schema migrations |

### 2.2 Frontend Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Framework** | React | 19.2.0 | UI library |
| **Language** | TypeScript | 5.9.3 | Type-safe JavaScript |
| **Build Tool** | Vite | 7.2.4 | Fast development/build |
| **Styling** | Tailwind CSS | 4.1.18 | Utility-first CSS |
| **Routing** | React Router | 7.13.0 | Client-side routing |
| **HTTP Client** | Axios | 1.13.4 | API communication |
| **State** | TanStack Query | 5.90.20 | Server state management |
| **Forms** | React Hook Form | 7.71.1 | Form handling |
| **Validation** | Zod | 4.3.6 | Schema validation |
| **Charts** | Recharts | 3.7.0 | Data visualization |
| **Icons** | Lucide React | 0.563.0 | Icon library |
| **Tours** | Driver.js | 1.4.0 | Interactive feature tours |

### 2.3 AI Integration

| Provider | Model | Purpose |
|----------|-------|---------|
| **Anthropic (Primary)** | claude-sonnet-4-20250514 | Message generation, resume optimization, career coaching |
| **OpenAI (Fallback)** | gpt-4-turbo-preview | Backup AI provider |

**AI Service Capabilities** (`app/services/ai_service.py:14-61`):
- Message Generator: Outreach messages with personalization
- Resume Optimizer: ATS-focused suggestions
- Career Coach: Interview prep, job search strategy
- Interview Prep: Practice questions, STAR method guidance

### 2.4 Payment Integration

| Service | Purpose | Price IDs |
|---------|---------|-----------|
| **Stripe** | Subscription management | STRIPE_PRICE_PRO, STRIPE_PRICE_EXPERT, STRIPE_PRICE_CAREER_KEEPER |

**Tier Pricing** (`app/services/stripe_service.py:35-40`):
- Basic: Free ($0)
- Pro: $19.99/month
- Expert: $49.99/month
- Career Keeper: $9.99/month

### 2.5 Email Service

| Service | Purpose |
|---------|---------|
| **SendGrid** | Transactional emails |

**Email Templates** (`app/services/email_service.py:33-173`):
- `welcome` - New user onboarding
- `password_reset` - Password recovery
- `email_verification` - Email confirmation
- `subscription_confirmed` - Tier activation
- `subscription_cancelled` - Cancellation notice
- `payment_failed` - Payment failure alert
- `weekly_summary` - Activity summary
- `follow_up_reminder` - Recruiter follow-up

---

## 3. API Endpoints Inventory

### 3.1 Authentication (`/api/auth/`) - 12 Endpoints

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/register` | No | User registration |
| POST | `/login` | No | User login, returns JWT tokens |
| POST | `/logout` | Yes | Invalidate tokens |
| POST | `/refresh` | Refresh Token | Refresh access token |
| POST | `/verify-email` | No | Verify email with token |
| POST | `/resend-verification` | No | Resend verification email |
| PUT | `/password` | Yes | Change password |
| POST | `/forgot-password` | No | Request password reset |
| POST | `/reset-password` | No | Reset password with token |
| GET | `/me` | Yes | Get current user |
| PUT | `/profile` | Yes | Update user profile |
| GET | `/tour/status` | Yes | Get tour completion status |
| POST | `/tour/complete` | Yes | Mark tour as complete |

### 3.2 Resumes (`/api/resumes/`) - 9 Endpoints

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/` | Yes | List all user resumes |
| POST | `/` | Yes | Upload new resume |
| GET | `/master` | Yes | Get master resume |
| GET | `/<id>` | Yes | Get resume by ID |
| DELETE | `/<id>` | Yes | Delete resume (soft delete) |
| PUT | `/<id>/master` | Yes | Set as master resume |
| POST | `/<id>/score` | Yes | Calculate ATS score with keywords |
| POST | `/<id>/tailor` | Yes | Create tailored version |
| GET | `/<id>/suggestions` | Yes | Get optimization suggestions |
| GET | `/<id>/analysis` | Yes | Get full ATS analysis |

### 3.3 Recruiters (`/api/recruiters/`) - 17 Endpoints

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/` | Yes | List recruiters (filterable) |
| POST | `/` | Yes | Add new recruiter |
| GET | `/stats` | Yes | Get pipeline statistics |
| GET | `/stages` | Yes | Get pipeline stages |
| GET | `/recommendations` | Yes | Get action recommendations |
| GET | `/<id>` | Yes | Get recruiter by ID |
| PUT | `/<id>` | Yes | Update recruiter |
| DELETE | `/<id>` | Yes | Delete recruiter |
| PUT | `/<id>/stage` | Yes | Update pipeline stage |
| POST | `/<id>/message-sent` | Yes | Track message sent |
| POST | `/<id>/message-opened` | Yes | Track message opened |
| POST | `/<id>/response` | Yes | Track response received |
| GET | `/<id>/fit-score` | Yes | Get fit score calculation |
| GET | `/<id>/notes` | Yes | Get recruiter notes |
| POST | `/<id>/notes` | Yes | Add note |
| PUT | `/<id>/notes/<note_id>` | Yes | Update note |
| DELETE | `/<id>/notes/<note_id>` | Yes | Delete note |

### 3.4 Messages (`/api/messages/`) - 14 Endpoints

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/` | Yes | List messages |
| POST | `/` | Yes | Create message |
| GET | `/stats` | Yes | Get message statistics |
| GET | `/tips/<type>` | Yes | Get writing tips by type |
| POST | `/validate` | Yes | Validate message quality |
| POST | `/context` | Yes | Get generation context |
| GET | `/<id>` | Yes | Get message by ID |
| PUT | `/<id>` | Yes | Update message |
| DELETE | `/<id>` | Yes | Delete message |
| POST | `/<id>/send` | Yes | Mark as sent |
| POST | `/<id>/open` | Yes | Mark as opened |
| POST | `/<id>/respond` | Yes | Mark as responded |
| GET | `/<id>/score` | Yes | Get quality score |
| POST | `/<id>/regenerate` | Yes | Regenerate with AI |

### 3.5 Activities (`/api/activities/`) - 11 Endpoints

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/` | Yes | List activities |
| POST | `/` | Yes | Log activity |
| GET | `/recent` | Yes | Get recent activities |
| GET | `/counts` | Yes | Get activity counts by type |
| GET | `/timeline` | Yes | Get timeline view |
| GET | `/weekly-summary` | Yes | Get weekly summary |
| GET | `/pipeline` | Yes | Get pipeline items |
| GET | `/pipeline/stats` | Yes | Get pipeline statistics |
| POST | `/pipeline` | Yes | Add to pipeline |
| PUT | `/pipeline/<id>/move` | Yes | Move pipeline item |
| DELETE | `/pipeline/<id>` | Yes | Remove from pipeline |

### 3.6 Dashboard (`/api/dashboard/`) - 3 Endpoints

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/` | Yes | Get aggregated dashboard data |
| GET | `/readiness` | Yes | Get career readiness score |
| GET | `/stats/weekly` | Yes | Get weekly statistics |

### 3.7 AI (`/api/ai/`) - 5 Endpoints

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/status` | Yes | Check AI service availability |
| POST | `/generate-message` | Yes | Generate outreach message |
| POST | `/optimize-resume` | Yes | Get resume suggestions |
| POST | `/career-coach` | Yes | Career coaching chat |
| POST | `/interview-prep` | Yes | Interview preparation |
| POST | `/improve-message` | Yes | Improve existing message |

### 3.8 LinkedIn (`/api/linkedin/`) - 7 Endpoints

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/analyze` | Yes | Analyze profile |
| POST | `/headline/generate` | Yes | Generate headline options |
| POST | `/summary/generate` | Yes | Generate summary |
| POST | `/experience/optimize` | Yes | Optimize experience entries |
| POST | `/visibility` | Yes | Calculate visibility score |
| GET | `/keywords/<industry>` | Yes | Get industry keywords |
| GET | `/tips` | Yes | Get optimization tips |

### 3.9 Labor Market (`/api/labor-market/`) - 6 Endpoints

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/overview` | Yes | Market overview stats |
| GET | `/shortage` | Yes | Skill shortage scores |
| GET | `/salary` | Yes | Salary benchmarks |
| GET | `/outlook/<role>` | Yes | Role-specific outlook |
| POST | `/opportunity` | Yes | Calculate opportunity score |
| GET | `/industries/trending` | Yes | Trending industries |
| GET | `/roles/high-demand` | Yes | High-demand roles |

### 3.10 Subscriptions (`/api/subscription/`) - 7 Endpoints

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/tiers` | No | Get available tiers |
| GET | `/status` | Yes | Get subscription status |
| POST | `/checkout` | Yes | Create Stripe checkout session |
| POST | `/portal` | Yes | Get customer portal URL |
| POST | `/cancel` | Yes | Cancel subscription |
| POST | `/reactivate` | Yes | Reactivate cancelled sub |
| POST | `/webhook` | No (Stripe sig) | Handle Stripe webhooks |

### 3.11 System Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API documentation & available endpoints |
| GET | `/health` | Health check for monitoring |

---

## 4. Algorithm Implementations

### 4.1 ATS Score Algorithm

**File:** `app/services/scoring/ats.py:14-23`

**Formula:**
```
ATS_SCORE = compatibility(15%) + keywords(15%) + achievements(25%) +
            formatting(15%) + progression(15%) + completeness(10%) + fit(5%)
```

**Weights:**
```python
ATS_WEIGHTS = {
    "compatibility": 15,  # File format, parsing success
    "keywords": 15,       # Industry/role keyword density
    "achievements": 25,   # Quantified accomplishments
    "formatting": 15,     # Structure, readability
    "progression": 15,    # Career advancement pattern
    "completeness": 10,   # All sections present
    "fit": 5,             # Match to target role
}
```

**Component Scoring Details:**

| Component | Max Score | Key Factors |
|-----------|-----------|-------------|
| Compatibility | 100 | DOCX (100), PDF (90), TXT (85), Other (60) |
| Keywords | 100 | Percentage of target keywords found |
| Achievements | 100 | Action verbs (20pts), Metrics (30pts), STAR format (10pts) |
| Formatting | 100 | Word count 400-800 (+15), Headers (+15), Bullets (+10) |
| Progression | 100 | Date patterns (+15), Title progression (+15) |
| Completeness | 100 | Contact, Summary, Experience, Education, Skills |
| Fit | 100 | Target role keywords in resume |

**Action Verbs List** (`ats.py:35-93`): 62 verbs including "achieved", "led", "improved", "generated"

**Metric Patterns** (`ats.py:96-103`):
- Dollar amounts: `\$[\d,]+[KMB]?`
- Percentages: `\d+%`
- Multipliers: `\d+x`
- Team sizes: `\d+\s*(?:people|employees|team members)`

---

### 4.2 Career Readiness Score Algorithm

**File:** `app/services/scoring/readiness.py:13-19`

**Formula:**
```
READINESS = profile(20%) + resume(25%) + network(20%) + activity(15%) + response(20%)
```

**Weights:**
```python
READINESS_WEIGHTS = {
    "profile": 20,    # Profile completeness
    "resume": 25,     # Resume ATS score
    "network": 20,    # Active recruiter pipeline
    "activity": 15,   # Weekly outreach activity
    "response": 20,   # Response rate vs benchmark
}
```

**Benchmarks** (`readiness.py:44-49`):
- Optimal recruiter count: 10
- Minimum recruiter count: 3
- Weekly message target: 5

**Response Rate Benchmarks by Career Stage** (`readiness.py:183-189`):
```python
benchmarks = {
    "entry_level": 0.10,    # 10%
    "early_career": 0.18,   # 18%
    "mid_level": 0.25,      # 25%
    "senior": 0.20,         # 20%
    "executive": 0.15,      # 15%
}
```

---

### 4.3 Message Quality Score Algorithm

**File:** `app/services/scoring/message.py:18-25`

**Formula:**
```
QUALITY = words(25%) + personalization(25%) + metrics(25%) + cta(20%) + tone(5%)
```

**Research Backing:**
- < 150 words = 22% higher response rate
- Name + company personalization = 15% higher response
- Quantified achievements = 40% more interviews

**Optimal Message Lengths** (`message.py:28-33`):
```python
OPTIMAL_LENGTHS = {
    "initial_outreach": (100, 150),
    "follow_up": (50, 75),
    "thank_you": (100, 125),
    "check_in": (50, 100),
}
```

**Call-to-Action Patterns** (`message.py:36-45`):
- "would you be open/available/interested"
- "could we schedule/set up"
- "i'd love/like to discuss"
- "let me know if"

**Personalization Types** (`message.py:59-67`):
- Name greeting
- Company mention
- Role reference
- Recent work reference
- Mutual connection
- Specific detail

---

### 4.4 Engagement Score Algorithm

**File:** `app/services/scoring/engagement.py`

**Formula:**
```
ENGAGEMENT = response_rate(40%) + open_rate(30%) + recency(30%)
```

**Weights:**
```python
ENGAGEMENT_WEIGHTS = {
    "response_rate": 40,  # Responses / messages sent
    "open_rate": 30,      # Opens / messages sent
    "recency": 30,        # Days since last contact (inverse)
}
```

---

### 4.5 Fit Score Algorithm

**File:** `app/services/scoring/engagement.py`

**Formula:**
```
FIT = industry(30%) + location(20%) + specialty(25%) + tier(15%) + depth(10%)
```

**Weights:**
```python
FIT_WEIGHTS = {
    "industry": 30,    # Industry match to user targets
    "location": 20,    # Location match
    "specialty": 25,   # Recruiter specialty match
    "tier": 15,        # Company tier match
    "depth": 10,       # Relationship depth
}
```

---

### 4.6 Opportunity Score Algorithm

**File:** `app/services/labor_market_service.py`

**Formula:**
```
OPPORTUNITY = shortage(40%) + skill_match(35%) + growth(25%)
```

**Shortage Score Formula:**
```
SHORTAGE = demand(40%) + growth(30%) + supply_gap(30%)
```

---

## 5. Database Schema

### 5.1 Users Table

**Model:** `app/models/user.py:96-172`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, default uuid4 | Unique identifier |
| email | String(255) | UNIQUE, NOT NULL, INDEX | User email |
| password_hash | String(255) | NOT NULL | Bcrypt hash |
| email_verified | Boolean | default False | Email verification status |
| verification_token | String(255) | nullable | Email verification token |
| first_name | String(100) | nullable | First name |
| last_name | String(100) | nullable | Last name |
| phone | String(20) | nullable | Phone number |
| location | String(200) | nullable | Location |
| linkedin_url | String(500) | nullable | LinkedIn profile URL |
| years_experience | Integer | nullable | Years of experience |
| career_stage | String(50) | nullable | Career stage enum |
| current_role | String(200) | nullable | Current job title |
| target_roles | JSONB | default [] | Target job titles |
| target_industries | JSONB | default [] | Target industries |
| target_companies | JSONB | default [] | Target companies |
| technical_skills | JSONB | default [] | Technical skills |
| soft_skills | JSONB | default [] | Soft skills |
| languages | JSONB | default [] | Languages spoken |
| certifications | JSONB | default [] | Certifications |
| salary_expectation | Integer | nullable | Target salary |
| remote_preference | String(50) | nullable | remote/hybrid/onsite |
| relocation_willing | Boolean | default False | Relocation preference |
| communication_style | String(50) | default 'balanced' | formal/casual/balanced |
| subscription_tier | String(50) | default 'basic' | Subscription tier |
| stripe_customer_id | String(255) | nullable | Stripe customer ID |
| stripe_subscription_id | String(255) | nullable | Stripe subscription ID |
| subscription_expires_at | DateTime | nullable | Subscription expiry |
| monthly_recruiter_count | Integer | default 0 | Monthly usage |
| monthly_research_count | Integer | default 0 | Monthly usage |
| monthly_message_count | Integer | default 0 | Monthly usage |
| monthly_resume_count | Integer | default 0 | Monthly usage |
| monthly_tailoring_count | Integer | default 0 | Monthly usage |
| daily_coach_count | Integer | default 0 | Daily usage |
| monthly_interview_prep_count | Integer | default 0 | Monthly usage |
| usage_reset_date | DateTime | nullable | Usage reset date |
| onboarding_completed | Boolean | default False | Onboarding status |
| onboarding_step | Integer | default 1 | Current step |
| tour_completed | Boolean | default False | Tour completion |
| completed_tours | JSONB | default [] | Completed tour IDs |
| is_active | Boolean | default True | Account status |
| last_login_at | DateTime | nullable | Last login |
| created_at | DateTime | default utcnow | Creation timestamp |
| updated_at | DateTime | auto-update | Update timestamp |

**Subscription Tiers** (`user.py:77-84`):
```python
class SubscriptionTier(str, Enum):
    BASIC = "basic"           # Free
    PRO = "pro"               # $19.99/month
    EXPERT = "expert"         # $49.99/month
    CAREER_KEEPER = "career_keeper"  # $9.99/month
```

**Tier Limits** (`user.py:193-232`):
| Feature | BASIC | PRO | EXPERT | CAREER_KEEPER |
|---------|-------|-----|--------|---------------|
| Recruiters | 5 | 50 | Unlimited | 5 |
| Tailored Resumes | 2 | 10 | Unlimited | 1 |
| AI Messages | 10 | 100 | Unlimited | 10 |
| Research | 5 | 25 | Unlimited | 2 |
| Daily Coach | 10 | 50 | Unlimited | 10 |
| Interview Prep | 0 | 3 | Unlimited | 1 |
| Skills Gap | 1 | 5 | Unlimited | 1 |

---

### 5.2 Resumes Table

**Model:** `app/models/resume.py:14-88`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| user_id | UUID | FK(users.id), NOT NULL, INDEX | Owner |
| title | String(255) | nullable | Display title |
| file_name | String(255) | nullable | Original filename |
| file_type | String(50) | nullable | pdf/docx/txt |
| file_size | Integer | nullable | Size in bytes |
| file_path | String(500) | nullable | Storage path |
| raw_text | Text | nullable | Extracted text |
| parsed_sections | JSONB | default {} | Structured sections |
| contact_info | JSONB | default {} | Extracted contact |
| work_experience | JSONB | default [] | Experience entries |
| education | JSONB | default [] | Education entries |
| skills | JSONB | default [] | Skills list |
| certifications | JSONB | default [] | Certifications |
| summary | Text | nullable | Resume summary |
| ats_total_score | Integer | nullable | Weighted total |
| ats_compatibility_score | Integer | nullable | 15% weight |
| ats_keywords_score | Integer | nullable | 15% weight |
| ats_achievements_score | Integer | nullable | 25% weight |
| ats_formatting_score | Integer | nullable | 15% weight |
| ats_progression_score | Integer | nullable | 15% weight |
| ats_completeness_score | Integer | nullable | 10% weight |
| ats_fit_score | Integer | nullable | 5% weight |
| ats_recommendations | JSONB | default [] | Improvement tips |
| missing_keywords | JSONB | default [] | Missing keywords |
| weak_sections | JSONB | default [] | Weak sections |
| is_tailored | Boolean | default False | Is tailored version |
| target_job_title | String(255) | nullable | Target role |
| target_company | String(255) | nullable | Target company |
| source_resume_id | UUID | FK(resumes.id), nullable | Parent resume |
| is_master | Boolean | default False | Master resume flag |
| is_deleted | Boolean | default False | Soft delete |
| deleted_at | DateTime | nullable | Deletion time |
| parse_status | String(50) | default 'pending' | Parse status |
| analyzed_at | DateTime | nullable | Analysis time |
| created_at | DateTime | default utcnow | Creation |
| updated_at | DateTime | auto-update | Update |

---

### 5.3 Resume Versions Table

**Model:** `app/models/resume.py:172-203`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| resume_id | UUID | FK(resumes.id), NOT NULL, INDEX | Parent resume |
| version_number | Integer | default 1 | Version number |
| change_summary | String(500) | nullable | Change description |
| raw_text | Text | nullable | Content snapshot |
| parsed_sections | JSONB | default {} | Sections snapshot |
| ats_score | Integer | nullable | Score at version |
| created_at | DateTime | default utcnow | Creation |

---

### 5.4 Recruiters Table

**Model:** `app/models/recruiter.py`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| user_id | UUID | FK(users.id), NOT NULL, INDEX | Owner |
| first_name | String(100) | NOT NULL | First name |
| last_name | String(100) | NOT NULL | Last name |
| email | String(255) | nullable | Email |
| phone | String(50) | nullable | Phone |
| company | String(255) | nullable | Company name |
| title | String(200) | nullable | Job title |
| linkedin_url | String(500) | nullable | LinkedIn URL |
| status | String(50) | default 'new' | Pipeline stage |
| priority_score | Integer | default 50 | Priority |
| engagement_score | Integer | nullable | Engagement score |
| fit_score | Integer | nullable | Fit score |
| messages_sent | Integer | default 0 | Messages sent |
| messages_opened | Integer | default 0 | Messages opened |
| responses_received | Integer | default 0 | Responses |
| last_contact_date | DateTime | nullable | Last contact |
| next_action | String(255) | nullable | Next action |
| next_action_date | DateTime | nullable | Action due date |
| source | String(100) | nullable | Lead source |
| specialty | String(255) | nullable | Specialty areas |
| industries | JSONB | default [] | Industries |
| locations | JSONB | default [] | Locations |
| notes_text | Text | nullable | Notes text |
| tags | JSONB | default [] | Tags |
| is_deleted | Boolean | default False | Soft delete |
| created_at | DateTime | default utcnow | Creation |
| updated_at | DateTime | auto-update | Update |

**Pipeline Stages:**
```python
PIPELINE_STAGES = [
    'new', 'researching', 'contacted', 'responded',
    'interviewing', 'offer', 'accepted', 'declined'
]
```

---

### 5.5 Recruiter Notes Table

**Model:** `app/models/recruiter.py`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| recruiter_id | UUID | FK(recruiters.id), NOT NULL, INDEX | Parent |
| content | Text | NOT NULL | Note content |
| created_by | UUID | FK(users.id), nullable | Creator |
| created_at | DateTime | default utcnow | Creation |
| updated_at | DateTime | auto-update | Update |

---

### 5.6 Messages Table

**Model:** `app/models/message.py`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| user_id | UUID | FK(users.id), NOT NULL, INDEX | Owner |
| recruiter_id | UUID | FK(recruiters.id), NOT NULL, INDEX | Recipient |
| subject | String(255) | nullable | Email subject |
| body | Text | NOT NULL | Message content |
| message_type | String(50) | default 'initial_outreach' | Message type |
| status | String(50) | default 'draft' | Message status |
| quality_score | Integer | nullable | Quality score |
| word_count | Integer | nullable | Word count |
| personalization_elements | JSONB | default [] | Personalization used |
| generated_by_ai | Boolean | default False | AI generated |
| ai_model | String(100) | nullable | AI model used |
| sent_at | DateTime | nullable | Send time |
| opened_at | DateTime | nullable | Open time |
| responded_at | DateTime | nullable | Response time |
| created_at | DateTime | default utcnow | Creation |
| updated_at | DateTime | auto-update | Update |

**Message Types:**
```python
class MessageType(str, Enum):
    INITIAL_OUTREACH = "initial_outreach"
    FOLLOW_UP = "follow_up"
    THANK_YOU = "thank_you"
    CHECK_IN = "check_in"
```

---

### 5.7 Activities Table

**Model:** `app/models/activity.py`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| user_id | UUID | FK(users.id), NOT NULL, INDEX | Owner |
| activity_type | String(50) | NOT NULL | Activity type |
| description | String(500) | nullable | Description |
| recruiter_id | UUID | FK(recruiters.id), nullable | Related recruiter |
| resume_id | UUID | FK(resumes.id), nullable | Related resume |
| message_id | UUID | FK(messages.id), nullable | Related message |
| metadata | JSONB | default {} | Additional data |
| created_at | DateTime | default utcnow, INDEX | Creation |

**Activity Types:**
```python
ACTIVITY_TYPES = [
    'recruiter_added', 'recruiter_updated', 'recruiter_stage_changed',
    'message_created', 'message_sent', 'message_opened', 'message_responded',
    'resume_uploaded', 'resume_scored', 'resume_tailored',
    'profile_updated', 'coach_session', 'interview_prep',
    'login', 'subscription_changed'
]
```

---

### 5.8 Pipeline Items Table

**Model:** `app/models/activity.py`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Unique identifier |
| user_id | UUID | FK(users.id), NOT NULL, INDEX | Owner |
| recruiter_id | UUID | FK(recruiters.id), nullable | Related recruiter |
| stage | String(50) | NOT NULL | Pipeline stage |
| position | Integer | default 0 | Sort order |
| priority | String(20) | default 'medium' | Priority level |
| last_activity | DateTime | nullable | Last activity |
| notes | Text | nullable | Notes |
| created_at | DateTime | default utcnow | Creation |
| updated_at | DateTime | auto-update | Update |

---

## 6. Frontend Status

### 6.1 Page Completion Status

| Page | File | Status | Lines | Features |
|------|------|--------|-------|----------|
| Login | `pages/Login.tsx` | ✅ 100% | ~150 | Form validation, password toggle, error handling |
| Register | `pages/Register.tsx` | ✅ 100% | ~180 | Password requirements, validation |
| Dashboard | `pages/Dashboard.tsx` | ✅ 100% | ~350 | Stats, pipeline, activities, recommendations, charts |
| Resumes | `pages/Resumes.tsx` | ✅ 100% | ~400 | Upload, list, view, ATS scoring, AI optimize |
| Recruiters | `pages/Recruiters.tsx` | ✅ 100% | 235 | List, search, filter, add, Kanban pipeline |
| Messages | `pages/Messages.tsx` | ✅ 100% | ~350 | CRUD, quality scoring, AI generation |
| Activity | `pages/Activity.tsx` | ✅ 100% | ~300 | Timeline and Kanban views |
| AI Coach | `pages/AICoach.tsx` | ✅ 100% | ~250 | Chat interface with AI |
| Settings | `pages/Settings.tsx` | ✅ 100% | ~400 | Profile, security, subscription tabs |
| Onboarding | `pages/Onboarding.tsx` | ✅ 100% | ~500 | 7-step flow with backend integration |
| Learn | `pages/Learn.tsx` | ✅ 100% | ~200 | Interactive feature tours |

### 6.2 API Client Coverage

**File:** `frontend/src/lib/api.ts`

| API Group | Methods | Coverage |
|-----------|---------|----------|
| authApi | 8 methods | ✅ Complete |
| dashboardApi | 3 methods | ✅ Complete |
| resumeApi | 9 methods | ✅ Complete |
| recruiterApi | 11 methods | ✅ Complete |
| messageApi | 11 methods | ✅ Complete |
| activityApi | 10 methods | ✅ Complete |
| aiApi | 6 methods | ✅ Complete |
| subscriptionApi | 6 methods | ✅ Complete |
| linkedinApi | 6 methods | ✅ Complete |
| laborMarketApi | 5 methods | ✅ Complete |

### 6.3 TypeScript Interfaces

**File:** `frontend/src/types/index.ts`

| Interface | Purpose |
|-----------|---------|
| User | User profile and settings |
| OnboardingData | Onboarding form data |
| ProfileUpdateData | Profile update payload |
| AuthTokens | JWT token pair |
| Resume | Resume metadata and scores |
| ATSBreakdown | ATS score components |
| Recruiter | Recruiter CRM data |
| RecruiterNote | Recruiter notes |
| Message | Outreach message |
| MessageQualityScore | Quality scoring details |
| Activity | Activity log entry |
| PipelineItem | Kanban pipeline item |
| DashboardData | Dashboard aggregation |
| CareerReadiness | Readiness scores |
| PipelineSummary | Pipeline statistics |
| UsageStats | Tier usage tracking |
| FollowUpRecommendation | Follow-up suggestions |
| LoginFormData | Login form |
| RegisterFormData | Registration form |
| ApiError | Error response format |

---

## 7. Configuration & Environment

### 7.1 Environment Variables

**Backend (`app/config.py`):**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | None | Flask secret key |
| `JWT_SECRET_KEY` | Yes | None | JWT signing key |
| `DATABASE_URL` | Yes | sqlite (dev) | PostgreSQL connection |
| `REDIS_URL` | No | None | Redis connection |
| `ANTHROPIC_API_KEY` | No | None | Claude API key |
| `OPENAI_API_KEY` | No | None | OpenAI API key |
| `STRIPE_SECRET_KEY` | No | None | Stripe secret key |
| `STRIPE_WEBHOOK_SECRET` | No | None | Stripe webhook secret |
| `STRIPE_PRICE_PRO` | No | None | Pro tier price ID |
| `STRIPE_PRICE_EXPERT` | No | None | Expert tier price ID |
| `STRIPE_PRICE_CAREER_KEEPER` | No | None | Career Keeper price ID |
| `SENDGRID_API_KEY` | No | None | SendGrid API key |
| `SENDGRID_FROM_EMAIL` | No | noreply@jobezie.com | Sender email |
| `SENDGRID_FROM_NAME` | No | Jobezie | Sender name |
| `FLASK_ENV` | No | development | Environment mode |
| `CORS_ORIGINS` | No | localhost | Allowed origins |
| `FRONTEND_URL` | No | http://localhost:5173 | Frontend URL |

**Frontend:**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_URL` | No | http://localhost:5000/api | Backend API URL |

### 7.2 Flask Configuration Classes

**File:** `app/config.py`

```python
class Config:
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///jobezie_dev.db"

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
```

### 7.3 Rate Limiting

**File:** `app/__init__.py`

| Endpoint | Limit | Description |
|----------|-------|-------------|
| Default | 100/minute | All API endpoints |
| `/` (docs) | 10/minute | API documentation |

---

## 8. Dependencies

### 8.1 Python Dependencies (`requirements.txt`)

**Core Framework:**
- Flask==3.0.0
- Werkzeug==3.0.1

**Database:**
- Flask-SQLAlchemy==3.1.1
- SQLAlchemy==2.0.36
- psycopg2-binary==2.9.10
- alembic==1.14.0
- Flask-Migrate==4.0.5

**Authentication:**
- Flask-JWT-Extended==4.6.0
- PyJWT==2.8.0
- bcrypt==4.1.2

**Validation & Security:**
- email-validator==2.1.0
- python-dotenv==1.0.0

**Caching:**
- redis==5.0.1
- Flask-Caching==2.1.0

**API:**
- marshmallow==3.20.1
- Flask-CORS==4.0.0
- Flask-Limiter==3.5.0

**HTTP:**
- requests==2.31.0
- httpx==0.26.0

**AI:**
- anthropic==0.18.1
- openai==1.12.0

**Payments:**
- stripe==8.0.0

**Email:**
- sendgrid==6.11.0

**Document Parsing:**
- python-docx==1.1.0
- PyPDF2==3.0.1

**Background Tasks:**
- celery==5.3.6

**Testing:**
- pytest==7.4.4
- pytest-cov==4.1.0
- pytest-flask==1.3.0
- factory-boy==3.3.0
- Faker==22.0.0

**Development:**
- black==23.12.1
- isort==5.13.2
- flake8==7.0.0
- bandit==1.7.7
- safety==3.2.0

**Production:**
- gunicorn==21.2.0

### 8.2 Node Dependencies (`frontend/package.json`)

**Runtime:**
- react: ^19.2.0
- react-dom: ^19.2.0
- react-router-dom: ^7.13.0
- @tanstack/react-query: ^5.90.20
- axios: ^1.13.4
- react-hook-form: ^7.71.1
- @hookform/resolvers: ^5.2.2
- zod: ^4.3.6
- recharts: ^3.7.0
- lucide-react: ^0.563.0
- clsx: ^2.1.1
- driver.js: ^1.4.0
- @tailwindcss/postcss: ^4.1.18

**Development:**
- typescript: ~5.9.3
- vite: ^7.2.4
- @vitejs/plugin-react: ^5.1.1
- tailwindcss: ^4.1.18
- postcss: ^8.5.6
- autoprefixer: ^10.4.24
- eslint: ^9.39.1
- @testing-library/react: ^16.2.0
- @testing-library/jest-dom: ^6.6.0
- @testing-library/user-event: ^14.6.0
- vitest: ^2.1.0
- @vitest/coverage-v8: ^2.1.0
- jsdom: ^24.0.0

---

## 9. Testing

### 9.1 Test Files

| File | Purpose | Coverage |
|------|---------|----------|
| `tests/conftest.py` | Pytest fixtures, test app factory | Setup |
| `tests/test_scoring.py` | Scoring algorithm tests | ✅ Complete |
| `tests/test_routes_phase2.py` | Route integration tests | Partial |
| `tests/test_models_phase2.py` | Model tests | Partial |
| `tests/unit/__init__.py` | Unit test package | Setup |
| `tests/unit/test_auth.py` | Authentication flow tests | ✅ Complete |
| `tests/unit/test_user_model.py` | User model tests | ✅ Complete |
| `tests/unit/test_validators.py` | Input validation tests | ✅ Complete |
| `tests/integration/__init__.py` | Integration test package | Empty |

### 9.2 Test Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_scoring.py

# Run unit tests only
pytest tests/unit/

# Frontend tests
cd frontend && npm run test

# Frontend coverage
cd frontend && npm run test:coverage
```

### 9.3 Coverage Gaps

**Backend:**
- [ ] Resume upload/parsing tests
- [ ] Recruiter CRM tests
- [ ] Message generation tests
- [ ] Activity tracking tests
- [ ] Dashboard aggregation tests
- [ ] AI service tests (with mocks)
- [ ] LinkedIn service tests
- [ ] Labor market service tests
- [ ] Stripe webhook tests
- [ ] Email service tests
- [ ] Integration tests for all routes

**Frontend:**
- [ ] Component unit tests
- [ ] Page integration tests
- [ ] API mock tests
- [ ] Form validation tests
- [ ] Tour flow tests

---

## 10. Production Readiness Assessment

### 10.1 Ready for Production ✅

| Component | Status | Notes |
|-----------|--------|-------|
| Core API | ✅ Ready | All routes implemented, rate limited |
| Authentication | ✅ Ready | JWT with refresh, password reset |
| Database Models | ✅ Ready | Migrations ready, indexes defined |
| User Management | ✅ Ready | Registration, profiles, subscriptions |
| Resume Management | ✅ Ready | Upload, parse, score, tailor |
| Recruiter CRM | ✅ Ready | Full pipeline management |
| Message System | ✅ Ready | Quality scoring, AI generation |
| Activity Tracking | ✅ Ready | Timeline, Kanban views |
| Dashboard | ✅ Ready | Stats, readiness score |
| AI Integration | ✅ Ready | Claude primary, OpenAI fallback |
| Stripe Payments | ✅ Ready | Checkout, portal, webhooks |
| Email Templates | ✅ Ready | All transactional emails |
| Frontend UI | ✅ Ready | All pages complete |
| Interactive Tours | ✅ Ready | Feature onboarding |
| Deployment Config | ✅ Ready | Render, Docker, Railway |

### 10.2 Partial Implementation ⚠️

| Component | Status | Missing |
|-----------|--------|---------|
| Token Blocklist | ⚠️ Partial | Uses in-memory set, needs Redis migration |
| Test Coverage | ⚠️ Partial | ~40% backend, minimal frontend |
| Celery Tasks | ⚠️ Partial | Worker configured, tasks not implemented |
| Error Tracking | ⚠️ Partial | Logging present, no Sentry/external |

### 10.3 Not Implemented ❌

| Component | Priority | Description |
|-----------|----------|-------------|
| Weekly Email Summaries | Medium | Scheduled Celery task |
| Follow-up Reminders | Medium | Automated email notifications |
| Real-time Notifications | Low | WebSocket/SSE for live updates |
| Admin Dashboard | Low | Internal admin interface |
| API Versioning | Low | /api/v1/ prefix |
| OpenAPI/Swagger Docs | Low | Auto-generated API docs |

---

## 11. Recommended Next Steps

### 11.1 High Priority (Before Production Launch)

1. **Migrate Token Blocklist to Redis**
   - Current: In-memory set (`app/extensions.py:35-54`)
   - Issue: Tokens lost on restart, not shared across instances
   - Solution: Use Redis set with TTL matching token expiry

2. **Increase Test Coverage to 80%**
   - Add unit tests for all services
   - Add integration tests for critical flows
   - Add frontend component tests

3. **Add Error Tracking**
   - Integrate Sentry or similar
   - Configure error alerting
   - Add performance monitoring

4. **Security Audit**
   - Run `bandit` and `safety` checks
   - Review all user inputs for injection
   - Audit file upload handling

### 11.2 Medium Priority (Post-Launch)

5. **Implement Scheduled Tasks**
   ```python
   # celery_app.py - Add scheduled tasks
   @celery.task
   def send_weekly_summaries():
       # Send weekly email to all users
       pass

   @celery.task
   def send_followup_reminders():
       # Check for stale contacts, send reminders
       pass
   ```

6. **Add Database Connection Pooling**
   - Configure SQLAlchemy pool settings
   - Add connection health checks

7. **Implement Caching Strategy**
   - Cache dashboard aggregations
   - Cache labor market data
   - Cache user tier limits

8. **Add API Rate Limiting per User**
   - Current: Global rate limits
   - Needed: Per-user limits based on tier

### 11.3 Low Priority (Future Enhancements)

9. **Real-time Features**
   - WebSocket for live pipeline updates
   - Server-sent events for notifications

10. **Advanced Analytics**
    - User engagement metrics
    - AI usage analytics
    - Conversion funnels

11. **Mobile Optimization**
    - PWA configuration
    - Mobile-specific layouts

12. **Internationalization**
    - Multi-language support
    - Currency localization

---

## Appendix: Quick Reference

### A.1 Common Commands

```bash
# Backend
pip install -r requirements.txt
flask db upgrade
python run.py

# Frontend
cd frontend && npm install
npm run dev

# Docker
docker-compose up -d

# Tests
pytest --cov=app
cd frontend && npm run test

# Linting
black app/
isort app/
flake8 app/
```

### A.2 Key File Locations

| Purpose | Location |
|---------|----------|
| App Factory | `app/__init__.py:16` |
| Config Classes | `app/config.py:10` |
| User Model | `app/models/user.py:96` |
| ATS Scoring | `app/services/scoring/ats.py:106` |
| AI Service | `app/services/ai_service.py:14` |
| API Client | `frontend/src/lib/api.ts:1` |
| Type Definitions | `frontend/src/types/index.ts:1` |
| Tour Config | `frontend/src/config/tours.ts:1` |

### A.3 API Base URL

- Development: `http://localhost:5000/api`
- Production: `https://jobezie-api.onrender.com/api`

---

*Document generated by comprehensive codebase analysis. Last updated: February 5, 2026.*
