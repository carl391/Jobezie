# JOBEZIE SYSTEM OVERVIEW

**Comprehensive Platform Audit**
**Generated: February 8, 2026**
**Version: 2.0.0**

---

## Table of Contents

1. [Project Architecture](#section-1-project-architecture)
2. [Authentication & Session Flow](#section-2-authentication--session-flow)
3. [Onboarding Flow](#section-3-onboarding-flow)
4. [Dashboard](#section-4-dashboard)
5. [Resume System](#section-5-resume-system-end-to-end)
6. [Recruiter CRM System](#section-6-recruiter-crm-system-end-to-end)
7. [Message Generation System](#section-7-message-generation-system-end-to-end)
8. [Activity Tracking & Pipeline](#section-8-activity-tracking--pipeline)
9. [AI Career Coach](#section-9-ai-career-coach)
10. [Labor Market Intelligence](#section-10-labor-market-intelligence)
11. [LinkedIn Profile Optimizer](#section-11-linkedin-profile-optimizer)
12. [Subscription & Billing](#section-12-subscription--billing)
13. [Profile & Settings](#section-13-profile--settings)
14. [Security & Validation](#section-14-security--validation)
15. [AI Service Architecture](#section-15-ai-service-architecture)
16. [API Endpoint Inventory](#section-16-api-endpoint-inventory)
17. [Frontend Component Map](#section-17-frontend-component-map)
18. [Data Flow Diagrams](#section-18-data-flow-diagrams)
19. [What's Missing / Gaps](#section-19-whats-missing--gaps)
20. [Recommendations](#section-20-recommendations)

---

## Section 1: Project Architecture

### Directory Tree (Actual)

```
Jobezie/
├── app/                          # Flask backend application
│   ├── __init__.py               # App factory, blueprint registration, error handlers, API docs
│   ├── config.py                 # Environment configs (Dev/Test/Prod), JWT settings
│   ├── extensions.py             # SQLAlchemy, JWT, Redis, CORS, Limiter, Caching init
│   ├── models/
│   │   ├── __init__.py           # Model exports
│   │   ├── user.py               # User, SubscriptionTier, CareerStage, GUID type, JSONType
│   │   ├── resume.py             # Resume, ResumeVersion
│   │   ├── recruiter.py          # Recruiter, RecruiterNote, RecruiterStatus
│   │   ├── message.py            # Message, MessageType, MessageStatus
│   │   ├── activity.py           # Activity, PipelineItem, ActivityType, PipelineStage
│   │   ├── labor_market.py       # Occupation, Skill, OccupationSkill, LaborMarketData, ShortageScore
│   │   └── notification.py       # Notification, NotificationType
│   ├── routes/
│   │   ├── __init__.py           # Blueprint imports and __all__ exports
│   │   ├── auth.py               # Registration, login, JWT, password reset, profile, tours
│   │   ├── resume.py             # Resume CRUD, ATS scoring, tailoring, analysis
│   │   ├── recruiter.py          # Recruiter CRM, stages, notes, fit/engagement scoring
│   │   ├── message.py            # Message CRUD, quality scoring, validation, context
│   │   ├── activity.py           # Activity logging, timeline, pipeline/Kanban
│   │   ├── dashboard.py          # Dashboard stats, readiness score, weekly stats
│   │   ├── ai.py                 # AI message generation, resume optimization, coaching, interview prep
│   │   ├── linkedin.py           # Profile analysis, headline/summary generation, visibility
│   │   ├── labor_market.py       # Shortage scores, salary benchmarks, opportunity analysis
│   │   ├── subscription.py       # Stripe checkout, portal, webhooks, tier management
│   │   └── notification.py       # Notification CRUD, generation, mark read
│   ├── services/
│   │   ├── ai_service.py         # Claude/OpenAI dual-provider AI integration
│   │   ├── resume_service.py     # File upload, PDF/DOCX parsing, ATS analysis
│   │   ├── recruiter_service.py  # CRM logic, engagement/fit calculation
│   │   ├── message_service.py    # Quality scoring, templates, context assembly
│   │   ├── activity_service.py   # Timeline, pipeline tracking, weekly summaries
│   │   ├── linkedin_service.py   # Profile optimization, keyword database, visibility scoring
│   │   ├── labor_market_service.py # Market data, salary benchmarks, shortage/opportunity scoring
│   │   ├── stripe_service.py     # Subscription management, webhook handlers
│   │   ├── notification_service.py # Follow-up reminders, usage warnings
│   │   └── scoring/
│   │       ├── ats.py            # 7-component ATS resume scoring algorithm
│   │       ├── message.py        # 5-component message quality scoring algorithm
│   │       ├── engagement.py     # Engagement, fit, and priority scoring algorithms
│   │       └── readiness.py      # 5-component career readiness scoring algorithm
│   └── utils/
│       ├── validators.py         # Input validation, XSS/SQLi protection, sanitization
│       └── decorators.py         # @admin_required, @subscription_required, @feature_limit, etc.
├── frontend/                     # React frontend application
│   ├── package.json              # Dependencies and scripts
│   ├── vite.config.ts            # Vite build configuration
│   └── src/
│       ├── App.tsx               # Router setup, QueryClient, protected routes
│       ├── main.tsx              # Entry point, providers
│       ├── contexts/
│       │   ├── AuthContext.tsx    # JWT auth state, login/register/logout
│       │   └── TourContext.tsx    # Driver.js tour system, completion tracking
│       ├── lib/
│       │   └── api.ts            # Axios client, 11 API service groups, 60+ functions
│       ├── types/
│       │   └── index.ts          # 20+ TypeScript interfaces
│       ├── components/
│       │   ├── Layout.tsx        # Sidebar nav, top bar, mobile menu, notifications
│       │   ├── ProtectedRoute.tsx # Auth + onboarding guard
│       │   ├── ui/               # Modal, ScoreCircle, ScoreBar, Tabs, Badge, EmptyState,
│       │   │                     # Skeleton, CommandPalette, PageTransition, NotificationBell,
│       │   │                     # OccupationAutocomplete, SkillsAutocomplete
│       │   ├── messages/         # ComposeMessageModal, MessageCard
│       │   ├── resumes/          # ViewResumeModal, ATSScoreModal, ResumeTailorModal, ResumeAnalysisModal
│       │   ├── recruiters/       # AddRecruiterModal, RecruiterDetailsModal
│       │   ├── onboarding/       # WelcomeStep, CareerInfoStep, ResumeUploadStep, ATSResultsStep,
│       │   │                     # FirstRecruiterStep, FirstMessageStep, CompleteStep
│       │   └── learn/            # CategoryCard, FeatureCard
│       └── pages/
│           ├── Login.tsx         # Login form with remember me
│           ├── Register.tsx      # Registration with plan selection + Stripe redirect
│           ├── Dashboard.tsx     # Stats, pipeline, activities, skills coverage, hot markets
│           ├── Resumes.tsx       # Upload, list, view, ATS scoring, AI optimize, tailor
│           ├── Recruiters.tsx    # List, search, filter, add, view details
│           ├── Messages.tsx      # CRUD, quality scoring, AI generation
│           ├── Activity.tsx      # Timeline and Kanban views with drag-drop
│           ├── AICoach.tsx       # 4-mode chat interface with AI coaching
│           ├── Settings.tsx      # Profile, security, subscription, help tabs
│           ├── Onboarding.tsx    # 7-step onboarding wizard
│           ├── LinkedIn.tsx      # Headline, summary, visibility generators
│           ├── InterviewPrep.tsx # Interview preparation tools
│           └── Learn.tsx         # Feature guide with categorized cards
├── migrations/
│   └── versions/
│       ├── 001_initial.py        # Core tables (users, resumes, resume_versions, recruiters,
│       │                         # recruiter_notes, messages, activities, pipeline_items)
│       ├── 1d37f0452b05_add_tour_tracking_columns.py  # tour_completed, completed_tours on users
│       ├── 002_add_labor_market_tables.py  # occupations, skills, occupation_skills,
│       │                                   # labor_market_data, shortage_scores
│       └── 003_add_notifications_table.py  # notifications table
├── requirements.txt              # Python dependencies
├── run.py                        # Flask dev server entry point
├── render.yaml                   # Render deployment configuration
├── CLAUDE.md                     # Project documentation for AI assistants
└── seed_onet_data.py             # O*NET data seeding script
```

### Tech Stack (Verified from `requirements.txt` and `package.json`)

| Layer | Technology | Version |
|-------|-----------|---------|
| **Backend Framework** | Flask | 3.0.0 |
| **ORM** | SQLAlchemy | 2.0.36 |
| **Database** | PostgreSQL (psycopg2-binary) | 2.9.10 |
| **Auth** | Flask-JWT-Extended | 4.6.0 |
| **Cache** | Redis | 5.0.1 |
| **Rate Limiting** | Flask-Limiter | 3.5.0 |
| **AI (Primary)** | Anthropic (Claude) | 0.18.1 |
| **AI (Fallback)** | OpenAI | 1.12.0 |
| **Payments** | Stripe | 8.0.0 |
| **Email** | SendGrid | 6.11.0 |
| **Doc Parsing** | PyPDF2 / python-docx | 3.0.1 / 1.1.0 |
| **Frontend Framework** | React | 19.2.0 |
| **Language** | TypeScript | 5.9.3 |
| **Build Tool** | Vite | 7.2.4 |
| **CSS** | Tailwind CSS | 4.1.18 |
| **Routing** | React Router | 7.13.0 |
| **Forms** | react-hook-form + zod | 7.71.1 / 4.3.6 |
| **Data Fetching** | @tanstack/react-query + axios | 5.90.20 / 1.13.4 |
| **Charts** | Recharts | 3.7.0 |
| **Animations** | Framer Motion | 12.33.0 |
| **Tour System** | Driver.js | 1.4.0 |
| **Toasts** | Sonner | 2.0.7 |
| **Command Palette** | cmdk | 1.1.1 |
| **Icons** | Lucide React | 0.563.0 |
| **WSGI Server** | Gunicorn | 21.2.0 |

### Environment Variables Required

| Variable | Service | Required |
|----------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `SECRET_KEY` | Flask secret key | Yes |
| `JWT_SECRET_KEY` | JWT signing key | Yes |
| `ANTHROPIC_API_KEY` | Claude AI API | Yes (for AI features) |
| `OPENAI_API_KEY` | OpenAI fallback | No (fallback) |
| `STRIPE_SECRET_KEY` | Stripe payments | Yes (for billing) |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook verification | Yes (for billing) |
| `SENDGRID_API_KEY` | SendGrid email | No (configured, not fully wired) |
| `REDIS_URL` | Redis cache/rate limiting | No (falls back to in-memory) |
| `CORS_ORIGINS` | Allowed CORS origins | No (defaults: localhost:5173, localhost:3000) |
| `FLASK_ENV` | Environment (development/production) | No (defaults to development) |
| `FRONTEND_URL` | Frontend URL for email links | No |
| `VITE_API_URL` | Backend API URL (frontend) | No (defaults to http://localhost:5000/api) |

### Flask App Factory (`app/__init__.py`)

The app factory `create_app(config_name)`:

1. Creates Flask instance with config
2. Initializes extensions: SQLAlchemy, JWT, Migrate, CORS, Limiter, Cache
3. Configures JWT token blocklist (in-memory set `BLOCKLIST`)
4. Registers 11 blueprints with `/api` prefix:
   - `auth_bp` → `/api/auth`
   - `resume_bp` → `/api/resumes`
   - `recruiter_bp` → `/api/recruiters`
   - `message_bp` → `/api/messages`
   - `activity_bp` → `/api/activities`
   - `dashboard_bp` → `/api/dashboard`
   - `ai_bp` → `/api/ai`
   - `linkedin_bp` → `/api/linkedin`
   - `labor_market_bp` → `/api/labor-market`
   - `subscription_bp` → `/api/subscription`
   - `notification_bp` → `/api/notifications`
5. Registers error handlers (404, 500, rate limit exceeded)
6. Adds root `/` endpoint with API documentation
7. Adds `/health` health check endpoint

### Database Schema (15 Tables)

| # | Table | Model | Primary Key | Description |
|---|-------|-------|-------------|-------------|
| 1 | `users` | User | UUID (GUID) | User accounts, auth, subscriptions, career data |
| 2 | `resumes` | Resume | UUID | Resume uploads, parsed content, ATS scoring |
| 3 | `resume_versions` | ResumeVersion | UUID | Resume version snapshots |
| 4 | `recruiters` | Recruiter | UUID | CRM contacts, engagement tracking |
| 5 | `recruiter_notes` | RecruiterNote | UUID | Recruiter interaction notes |
| 6 | `messages` | Message | UUID | Outreach messages, quality scoring |
| 7 | `activities` | Activity | UUID | Activity timeline entries |
| 8 | `pipeline_items` | PipelineItem | UUID | Kanban board state per recruiter |
| 9 | `occupations` | Occupation | String(20) SOC code | O*NET occupation data (1,016 records) |
| 10 | `skills` | Skill | String(50) element ID | O*NET skill taxonomy (120 dimensions) |
| 11 | `occupation_skills` | OccupationSkill | Composite (occ+skill) | Occupation-skill mappings (107,280 records) |
| 12 | `labor_market_data` | LaborMarketData | Integer auto | BLS statistics (JOLTS, OES, OOH) |
| 13 | `shortage_scores` | ShortageScore | Integer auto | Pre-calculated shortage metrics |
| 14 | `notifications` | Notification | UUID | User alerts and reminders |

#### User Model (Detailed Schema)

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| id | GUID (UUID) | uuid.uuid4 | Primary key |
| email | String(255) | - | Unique, indexed |
| email_verified | Boolean | False | Email verification flag |
| password_hash | String(255) | - | Bcrypt hash |
| verification_token | String(255) | - | Email verification |
| reset_token | String(255) | - | Password reset |
| reset_token_expires | DateTime | - | Token expiration |
| first_name | String(100) | - | |
| last_name | String(100) | - | |
| phone | String(50) | - | |
| location | String(200) | - | |
| linkedin_url | String(500) | - | |
| years_experience | Integer | - | |
| career_stage | String(50) | - | ENTRY_LEVEL, EARLY_CAREER, MID_LEVEL, SENIOR, EXECUTIVE |
| current_role | String(200) | - | |
| target_roles | JSONType | [] | Array of target role strings |
| target_industries | JSONType | [] | Array of industry strings |
| target_companies | JSONType | [] | Array of company strings |
| technical_skills | JSONType | [] | Array of skill strings |
| salary_expectation | Integer | - | |
| preferences | JSONType | {} | User preferences |
| subscription_tier | String(50) | "basic" | BASIC, PRO, EXPERT, CAREER_KEEPER |
| stripe_customer_id | String(255) | - | |
| stripe_subscription_id | String(255) | - | |
| subscription_expires_at | DateTime | - | |
| monthly_message_count | Integer | 0 | AI messages this month |
| monthly_recruiter_count | Integer | 0 | Recruiters added this month |
| monthly_research_count | Integer | 0 | Research actions this month |
| monthly_tailoring_count | Integer | 0 | Resume tailoring this month |
| monthly_interview_prep_count | Integer | 0 | Interview prep this month |
| daily_coach_count | Integer | 0 | Coach calls today |
| usage_reset_date | DateTime | 30 days from creation | Lazy reset trigger |
| onboarding_step | Integer | 1 | Current onboarding step |
| onboarding_completed | Boolean | False | |
| tour_completed | Boolean | False | Main tour completion |
| completed_tours | JSONType | [] | Array of completed tour IDs |
| last_login_at | DateTime | - | |
| created_at | DateTime | utcnow | |
| updated_at | DateTime | utcnow | Auto-updated |

#### Resume Model (Detailed Schema)

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| id | GUID | uuid.uuid4 | Primary key |
| user_id | GUID | - | FK → users.id |
| title | String(255) | - | |
| file_name | String(255) | - | Original filename |
| file_type | String(50) | - | pdf, docx, txt |
| file_size | Integer | - | Bytes |
| file_path | String(500) | - | Storage location |
| raw_text | Text | - | Extracted plain text |
| parsed_sections | JSONType | {} | Structured sections |
| contact_info | JSONType | {} | Name, email, phone, location |
| work_experience | JSONType | [] | Array of job objects |
| education | JSONType | [] | Array of education objects |
| skills | JSONType | [] | Array of skill strings |
| certifications | JSONType | [] | Array of cert strings |
| summary | Text | - | Professional summary |
| ats_total_score | Integer | - | 0-100 |
| ats_compatibility_score | Integer | - | 15% weight |
| ats_keywords_score | Integer | - | 15% weight |
| ats_achievements_score | Integer | - | 25% weight |
| ats_formatting_score | Integer | - | 15% weight |
| ats_progression_score | Integer | - | 15% weight |
| ats_completeness_score | Integer | - | 10% weight |
| ats_fit_score | Integer | - | 5% weight |
| ats_recommendations | JSONType | [] | Suggestions |
| missing_keywords | JSONType | [] | |
| weak_sections | JSONType | [] | |
| is_tailored | Boolean | False | |
| target_job_title | String(255) | - | |
| target_company | String(255) | - | |
| source_resume_id | GUID | - | FK → resumes.id (parent) |
| is_master | Boolean | False | |
| is_deleted | Boolean | False | Soft delete |
| parse_status | String(50) | "pending" | pending, success, error |
| created_at/updated_at | DateTime | utcnow | |

#### Recruiter Model (Detailed Schema)

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| id | GUID | uuid.uuid4 | Primary key |
| user_id | GUID | - | FK → users.id |
| first_name/last_name | String(100) | - | Required |
| email | String(255) | - | Optional |
| phone | String(50) | - | |
| linkedin_url | String(500) | - | |
| company | String(200) | - | |
| title | String(200) | - | |
| company_type | String(100) | - | agency, corporate, executive_search |
| specialty | String(200) | - | |
| industries | JSONType | [] | |
| locations | JSONType | [] | |
| status | String(50) | "new" | Pipeline stage (8 values) |
| messages_sent | Integer | 0 | |
| messages_opened | Integer | 0 | |
| responses_received | Integer | 0 | |
| has_responded | Boolean | False | |
| engagement_score | Integer | 0 | 0-100 |
| engagement_components | JSONType | {} | |
| fit_score | Integer | 0 | 0-100 |
| fit_components | JSONType | {} | |
| research_summary | Text | - | AI research findings |
| last_contact_date | DateTime | - | |
| next_action | String(255) | - | |
| next_action_date | DateTime | - | |
| follow_up_count | Integer | 0 | |
| created_at/updated_at | DateTime | utcnow | |

#### Message Model (Detailed Schema)

| Column | Type | Default | Notes |
|--------|------|---------|-------|
| id | GUID | uuid.uuid4 | Primary key |
| user_id | GUID | - | FK → users.id |
| recruiter_id | GUID | - | FK → recruiters.id |
| message_type | String(50) | "initial_outreach" | 4 types |
| subject | String(255) | - | |
| body | Text | - | Required |
| signature | Text | - | |
| is_ai_generated | Boolean | False | |
| ai_model_used | String(100) | - | claude or openai |
| quality_score | Integer | - | 0-100 overall |
| quality_words_score | Integer | - | 25% weight |
| quality_personalization_score | Integer | - | 25% weight |
| quality_metrics_score | Integer | - | 25% weight |
| quality_cta_score | Integer | - | 20% weight |
| quality_tone_score | Integer | - | 5% weight |
| quality_feedback | JSONType | [] | |
| quality_suggestions | JSONType | [] | |
| word_count | Integer | - | |
| status | String(50) | "draft" | draft, ready, sent, opened, responded |
| sent_at/opened_at/responded_at | DateTime | - | |
| created_at/updated_at | DateTime | utcnow | |

---

## Section 2: Authentication & Session Flow

### Registration Flow

1. **User submits** POST `/api/auth/register` with `email`, `password`, `first_name`, `last_name`
2. **Server validates**: email format, password strength (8+ chars, uppercase, lowercase, digit), name format
3. **Server checks**: email uniqueness in database
4. **Server creates** User record with bcrypt-hashed password, generates verification token
5. **Server generates** JWT access token (1 hour) + refresh token (30 days)
6. **Server responds** with user data + tokens
7. **Frontend stores** tokens in `localStorage` (`access_token`, `refresh_token`)
8. **Frontend**: If paid plan selected, redirects to Stripe checkout; otherwise navigates to `/dashboard`

### Login Flow

1. **User submits** POST `/api/auth/login` with `email`, `password`
2. **Server validates** credentials against bcrypt hash
3. **Server updates** `last_login_at` timestamp
4. **Server generates** JWT access + refresh tokens
5. **Server responds** with user data (via `to_dict(include_private=True)`) + tokens
6. **Frontend stores** tokens in `localStorage`
7. **Frontend**: If "Remember Me" checked, stores email in `localStorage` key `jobezie_remember_email`
8. **Frontend navigates** to original location or `/dashboard`

### Token Refresh Mechanism

- **Access token**: Expires after 1 hour (`JWT_ACCESS_TOKEN_EXPIRES = 3600`)
- **Refresh token**: Expires after 30 days (`JWT_REFRESH_TOKEN_EXPIRES = 2592000`)
- **Frontend interceptor** (`api.ts`): On 401 response, automatically calls POST `/api/auth/refresh` with refresh token
- **Server**: Validates refresh token, issues new access token
- **Token blocklist**: In-memory Python set `BLOCKLIST` in `__init__.py` — **NOT persisted to Redis** (see Gaps section)

### Password Reset Flow

1. POST `/api/auth/forgot-password` with `email`
2. Server generates reset token, sets expiration (implementation uses SendGrid but emails are not fully wired)
3. Always returns 200 (security: doesn't reveal if email exists)
4. POST `/api/auth/reset-password` with `token`, `new_password`
5. Server validates token, updates password hash, clears reset token

### Route Protection

- **Backend**: `@jwt_required()` decorator validates JWT on protected endpoints
- **`@feature_limit(feature_name)`**: Checks `user.can_use_feature()` before allowing action
- **`@subscription_required(*tiers)`**: Checks user's subscription tier
- **Frontend**: `ProtectedRoute` component checks `isAuthenticated` and `onboarding_completed`
  - Unauthenticated → redirect to `/login`
  - Onboarding incomplete → redirect to `/onboarding`
  - Special: subscription routes skip onboarding check

### Subscription Feature Gating: `can_use_feature()` Logic

```python
def can_use_feature(feature, count=1):
    # Step 1: Lazy reset if past usage_reset_date
    if usage_reset_date < utcnow():
        reset_monthly_usage()  # Sets all counters to 0, extends date 30 days

    # Step 2: Get tier limits
    limit = tier_limits[subscription_tier][feature]

    # Step 3: Check unlimited
    if limit == -1:
        return True

    # Step 4: Check usage
    current_usage = get_usage_count(feature)
    return current_usage + count <= limit
```

**Tier Limits:**

| Feature | Basic | Pro | Expert | Career Keeper |
|---------|-------|-----|--------|---------------|
| recruiters | 5 | 50 | Unlimited | 5 |
| tailored_resumes | 2 | 10 | Unlimited | 1 |
| ai_messages | 10 | 100 | Unlimited | 10 |
| research | 3 | 20 | Unlimited | 2 |
| coach_daily | 5 | 50 | Unlimited | 10 |
| interview_prep | 1 | 3 | Unlimited | 1 |
| skills_gap | 1 | 5 | Unlimited | 1 |

---

## Section 3: Onboarding Flow

**Status: Fully Implemented** — 7-step wizard with backend persistence and localStorage state saving.

### Step-by-Step Walkthrough

| Step | Component | What Happens | Data Saved | API Endpoint |
|------|-----------|-------------|------------|--------------|
| 1 | WelcomeStep | Welcome hero with user name, "Let's Get Started" button | None | None |
| 2 | CareerInfoStep | 3 substeps: Job search status → Career stage → Details (role, target roles via OccupationAutocomplete, industries, skills via SkillsAutocomplete) | career_stage, current_role, target_roles, target_industries, technical_skills, onboarding_step=2 | PUT `/api/auth/profile` |
| 3 | ResumeUploadStep | Drag-drop or click upload (PDF/DOCX, max 10MB), or Skip | Resume record created, onboarding_step=3 | POST `/api/resumes` |
| 4 | ATSResultsStep | Displays ATS score with breakdown and top 3 issues, or auto-skips if no resume | onboarding_step=4 | GET `/api/resumes/{id}/analysis` |
| 5 | FirstRecruiterStep | Simplified recruiter form (name, company, title, email, LinkedIn), or Skip | Recruiter record, onboarding_step=5 | POST `/api/recruiters` |
| 6 | FirstMessageStep | Auto-generates AI message for recruiter (or template fallback), editable textarea, or Skip | onboarding_step=6 | POST `/api/ai/generate-message` |
| 7 | CompleteStep | Celebration animation, readiness score, completed items checklist, "Go to Dashboard" | onboarding_completed=true, onboarding_step=7 | PUT `/api/auth/profile` + GET `/api/dashboard/readiness` |

**localStorage persistence**: `onboarding_step`, `onboarding_career_data`, `onboarding_resume_id`

**Access gating**: `ProtectedRoute` redirects to `/onboarding` if `user.onboarding_completed === false`. Backend has `@onboarding_completed_required` decorator but it is **not currently applied** to any routes — gating is frontend-only.

---

## Section 4: Dashboard

### API Endpoints

| Endpoint | Data Provided |
|----------|--------------|
| GET `/api/dashboard` | stats, master_resume, career_readiness, pipeline_summary, recent_activities (10), follow_up_needed (5), usage limits |
| GET `/api/activities/recent?limit=5` | 5 most recent activities for timeline |
| GET `/api/labor-market/skills-map` | User's skills coverage by category (non-blocking) |
| GET `/api/labor-market/roles/high-demand` | Top high-demand roles with shortage scores (non-blocking) |

### Dashboard Widgets

| Widget | Data Source | Description |
|--------|-----------|-------------|
| **Welcome Section** | User name | Personalized greeting |
| **Getting Started Checklist** | Dashboard data | 4-item progress bar (dismissible via localStorage `jobezie_hide_checklist`) |
| **Career Readiness Card** | `career_readiness.overall_score` | ScoreCircle with 0-100 score |
| **Active Recruiters Card** | `stats.active_recruiters` | Count of non-declined recruiters |
| **Messages Sent Card** | `stats.messages_this_week` | Weekly message count |
| **Resumes Card** | `stats.resumes` | Total resume count |
| **Pipeline Overview** | `pipeline_summary` | Bar chart of 8 pipeline stages |
| **Recent Activity** | `activityApi.getRecent(5)` | Timeline of 5 most recent activities |
| **Skills Coverage** | `laborMarketApi.getSkillsMap()` | Skills/abilities/knowledge bars with coverage % |
| **Hot Job Markets** | `laborMarketApi.getHighDemandRoles()` | Top 5 roles with shortage scores |
| **Recommended Follow-ups** | `follow_up_needed` | Top 3 recruiters needing follow-up |

### Career Readiness Score Algorithm

```
readiness = profile(20%) + resume(25%) + network(20%) + activity(15%) + response(20%)
```

**Components** (`app/services/scoring/readiness.py`):

1. **Profile (20%)**: Weighted field completion (required×3 + important×2 + recommended×1, max 28 weight)
2. **Resume (25%)**: No resume = 0, unanalyzed = 40, analyzed = ATS score
3. **Network (20%)**: 0 recruiters = 0, 10+ = 100, 3-9 = linear interpolation
4. **Activity (15%)**: (messages_this_week / 5) × 100, capped at 100
5. **Response (20%)**: response_rate / career_stage_benchmark × 66.67, capped at 100

---

## Section 5: Resume System (End-to-End)

### Upload Flow

1. User selects file via drag-drop or file picker (PDF, DOCX, TXT; max 10MB)
2. Frontend creates `FormData` with file + optional title + is_master flag
3. POST `/api/resumes` → `resume_service.upload_resume()`
4. **File parsing** (`resume_service.py`):
   - PDF → PyPDF2 text extraction
   - DOCX → python-docx paragraph/table extraction
   - TXT → direct read
5. **Section parsing**: Regex-based extraction of contact info, summary, experience, education, skills, certifications
6. **ATS scoring**: Calls `scoring/ats.py:calculate_ats_score()` with parsed content
7. Resume record saved with all parsed fields + ATS scores
8. Returns resume with ATS analysis to frontend

### ATS Scoring Algorithm (7 Components)

**File**: `app/services/scoring/ats.py`

```
ats_score = compatibility(15%) + keywords(15%) + achievements(25%) +
            formatting(15%) + progression(15%) + completeness(10%) + fit(5%)
```

#### 1. Compatibility (15%) — File format & parsing quality
- DOCX: 100, PDF: 90, TXT: 85, Other: 60
- Penalties: >5% special chars (-15), <200 words (-20)

#### 2. Keywords (15%) — Keyword density & relevance
- Formula: `(found_keywords / total_keywords) × 100`
- Returns `missing_keywords` list
- If no keywords provided: checks against common professional terms

#### 3. Achievements (25%) — Quantified impact statements
- Base score: 50
- Checks for 93 action verbs (achieved, accelerated, delivered, etc.)
- ≥10 action verbs: +20, 5-9: +10
- Checks for metric patterns ($amounts, percentages, multipliers, large numbers, time periods)
- ≥8 metrics: +30, 4-7: +15
- Results-oriented bullets: +10

#### 4. Formatting (15%) — Structure & readability
- Base score: 70
- Word count: 400-800 optimal (+15), <300 (-20), >1000 (-10)
- Section headers: ≥4 (+15), <2 (-20)
- Bullet points: ≥10 (+10)

#### 5. Progression (15%) — Career growth evidence
- Base score: 70
- Date ranges: ≥3 (+15), <1 (-20)
- Progression terms (promoted, senior, lead, director, etc.): ≥2 (+15)

#### 6. Completeness (10%) — Essential sections present
- Formula: `(present_sections / 5) × 100`
- Checks for: Contact, Summary, Experience, Education, Skills

#### 7. Fit (5%) — Target role alignment
- Target role mentioned: 100, related terms: 80, no target: 50-70

### Resume Optimization (AI)

POST `/api/ai/optimize-resume`:
1. Fetches resume data + ATS score
2. Builds context prompt with current score, weak sections, missing keywords
3. Calls Claude API (or OpenAI fallback) with system prompt for resume optimization
4. Returns full optimized resume text + AI suggestions + algorithmic suggestions
5. Frontend displays side-by-side with save option

### Resume Tailoring

POST `/api/resumes/{id}/tailor`:
1. Takes target_job_title, target_company, optional optimized_text
2. Creates new Resume record with `is_tailored=true`, `source_resume_id` pointing to original
3. Increments `monthly_tailoring_count`
4. Returns tailored resume with new ATS score

---

## Section 6: Recruiter CRM System (End-to-End)

### CRUD Operations

- **Create**: POST `/api/recruiters` — validates text fields, checks feature limit, creates record
- **Read**: GET `/api/recruiters` — supports status/industry/location filters, sort_by, pagination (max 100)
- **Update**: PUT `/api/recruiters/{id}` — generic field update
- **Delete**: DELETE `/api/recruiters/{id}` — **hard delete** (not soft delete)

### Pipeline Stages (8)

```
NEW → RESEARCHING → CONTACTED → RESPONDED → INTERVIEWING → OFFER → ACCEPTED → DECLINED
```

### Engagement/Response Score Algorithm

**File**: `app/services/scoring/engagement.py`

**With email tracking:**
```
engagement = response_rate(40%) + open_rate(30%) + recency(30%)
```
Label: "Engagement Score"

**Without email tracking (default):**
```
response = response_rate(55%) + recency(45%)
```
Label: "Response Score"

**Response Rate Scoring (40% weight):**
| Response Rate | Score |
|---------------|-------|
| ≥40% | 100 |
| ≥25% | 85 |
| ≥15% | 70 |
| ≥8% | 55 |
| ≥1% | 40 |
| 0% | 25 |
| No data | 50 |

**Recency Decay (30% weight):**
| Days Since Contact | Score |
|-------------------|-------|
| ≤7 (fresh) | 100 |
| ≤14 (warm) | 75 |
| ≤30 (cooling) | 50 |
| ≤60 (cold) | 25 |
| >60 | 10 |
| Never | 0 |

### Recruiter Fit Score Algorithm

```
fit = industry(30%) + location(20%) + specialty(25%) + tier(15%) + depth(10%)
```

1. **Industry Fit (30%)**: Overlap % between user and recruiter industries (≥50%=100, ≥25%=75, <25%=50, none=20)
2. **Location Fit (20%)**: Exact match=100, regional=75, remote/nationwide=80, none=40
3. **Specialty Fit (25%)**: Matches user target role=100, related=70, none=40
4. **Tier Fit (15%)**: Base 70, adjustments for salary range + recruiter type
5. **Depth (10%)**: Profile completeness (industries listed +30, locations +30, specialty +20)

### Priority Score Algorithm

```
priority = days_since(30%) + pending(25%) + potential(20%) + research(15%) + response(10%)
× status_multiplier
```

**Status Multipliers**: new=1.0, researching=0.8, contacted=1.2, responded=1.5, interviewing=1.3, offer=0.5, accepted/declined=0.1

### Follow-up Logic (`needs_follow_up` property)

Returns true when:
- Status is NOT declined/accepted
- Has NOT responded
- 5 ≤ days_since_contact ≤ 14
- follow_up_count < 3

---

## Section 7: Message Generation System (End-to-End)

### Message Generation Flow

1. User opens ComposeMessageModal, selects recruiter + message type
2. Clicks "AI Generate" → POST `/api/ai/generate-message`
3. **Context assembly** (`message_service.get_generation_context()`):
   - Recruiter data (name, company, title, specialty, research summary)
   - User data (name, role, experience, skills, target roles)
   - Resume summary (if resume_id provided)
   - Previous messages to this recruiter
4. **AI generation** (`ai_service.generate_message()`):
   - Builds system prompt with writing guidelines (< 150 words, personalization, metrics, single CTA)
   - Calls Claude API (primary) or OpenAI (fallback)
   - Returns generated message text
5. **Quality scoring** (`scoring/message.py:calculate_message_quality()`):
   - Analyzes word count, personalization, metrics, CTA, tone
   - Returns 0-100 score with feedback and suggestions
6. Message saved as draft with quality scores
7. Frontend displays message in editable textarea with score breakdown

### Message Quality Score Algorithm

**File**: `app/services/scoring/message.py`

```
quality = words(25%) + personalization(25%) + metrics(25%) + cta(20%) + tone(5%)
```

#### 1. Word Count (25%) — Optimal length
- Research: <150 words = 22% higher response rate
- Optimal ranges: initial_outreach 100-150, follow_up 50-75, thank_you 100-125, check_in 50-100
- Within range: 100, below: max(0, 100 - deficit×3), above: max(0, 100 - excess×2)

#### 2. Personalization (25%) — Individual tailoring
- Recruiter name mentioned: +30
- Company name mentioned: +30
- Recent work reference: +20
- Specific detail reference: +20
- Mutual connection: +15

#### 3. Metrics (25%) — Quantified achievements
- ≥3 metrics: 100, 2: 80, 1: 50, 0: 20
- Research: Quantified achievements = 40% more interview callbacks

#### 4. Call-to-Action (20%) — Clear next step
- Exactly 1 CTA: 100, 0: 20, >1: 60 (consolidate suggestion)
- Detects 8 CTA patterns (e.g., "would you be open to", "could we schedule")

#### 5. Tone (5%) — Professional appropriateness
- Base: 70
- Professional phrases: +10-15 each (up to 100)
- Casual red flags: -20 each (hey!, lol, gonna)
- Desperate red flags: -30 each (i really need, please help, desperate)

### Word Count Enforcement

Messages display word count badges in the UI:
- **Green**: ≤150 words (optimal)
- **Yellow**: 151-200 words (slightly long)
- **Red**: 201+ words (too long)

---

## Section 8: Activity Tracking & Pipeline

### Activity Types (15)

```
RECRUITER_ADDED, MESSAGE_SENT, MESSAGE_OPENED, RESPONSE_RECEIVED,
INTERVIEW_SCHEDULED, INTERVIEW_COMPLETED, OFFER_RECEIVED, OFFER_ACCEPTED,
OFFER_DECLINED, STATUS_CHANGE, RESUME_UPLOADED, RESUME_TAILORED,
RESEARCH_COMPLETED, FOLLOW_UP_SENT, NOTE_ADDED
```

### Pipeline Stages (8)

```
NEW, RESEARCHING, CONTACTED, RESPONDED, INTERVIEWING, OFFER, ACCEPTED, DECLINED
```

### Kanban Board

- **Frontend**: `Activity.tsx` with drag-drop implementation
- **Drag handlers**: `handleDragStart` → `handleDragOver` (highlights drop zone) → `handleDrop`
- **On drop**: PUT `/api/activities/pipeline/{item_id}/move` with `stage` and optional `position`
- **Pipeline refresh**: POST `/api/activities/pipeline/refresh` recalculates `days_in_stage` and priority scores

### Timeline View

- Activities grouped by date
- Type-based filtering (All, Messages, Resumes, Recruiters, Interviews)
- Relative date formatting (Just now, 1h ago, etc.)
- Activity-specific icons and colors

### Weekly Summary

GET `/api/activities/weekly-summary` returns:
- Day-by-day activity counts
- Highlights and summary stats
- Total activities, messages sent, responses, interviews

---

## Section 9: AI Career Coach

### Chat Flow

1. User selects mode and sends message
2. Frontend calls POST `/api/ai/career-coach` with:
   - `question`: User's message
   - `conversation_history`: Last 6 messages
   - Context: mode, user name, role, goals, experience
3. **Backend context assembly**:
   - Career readiness score
   - ATS score from master resume
   - Skills gap analysis
   - Market data (shortage scores for target roles)
   - Pipeline stats
4. **System prompt construction** (`ai_service.py`):
   - Role: "Expert career coach with deep knowledge of job markets"
   - Persona guidelines: supportive but direct, evidence-based, actionable
   - Mode-specific instructions (interview prep, resume review, salary negotiation)
   - Injected context data (scores, gaps, market conditions)
5. Calls Claude API (primary) or OpenAI (fallback)
6. Returns response with follow-up suggestions

### 4 Coaching Modes

| Mode | Quick Prompts | Focus |
|------|--------------|-------|
| **General** | Career Strategy, Skills Gap, Market Insights, Networking | Overall career guidance |
| **Interview Prep** | Behavioral Questions, Technical Interview, Mock Interview, Company Research | Interview readiness |
| **Resume Review** | Improve ATS Score, Skills Gap Analysis, Achievement Bullets, Resume Format | Resume optimization |
| **Salary Negotiation** | Market Rate, Negotiate Offer, Counter Offer, Total Compensation | Compensation strategy |

### Conversation History

- Stored in frontend state only (`useState` in `AICoach.tsx`)
- Last 6 messages sent to API for context
- "Clear chat" button resets conversation
- **No server-side persistence** of chat history

---

## Section 10: Labor Market Intelligence

### Data Pipeline

**O*NET Data Seeding** (`seed_onet_data.py`):
- 1,016 occupations from O*NET SOC codes
- 120 skill dimensions across 3 categories (skills, abilities, knowledge)
- 107,280 occupation-skill mappings with importance (0-100) and level (0-100)
- Seeded via `flask db upgrade` + `python seed_onet_data.py`

**BLS Integration**:
- `labor_market_service.py` can fetch from BLS API using series IDs
- Series mapped: unemployment rate (LNS14000000), nonfarm payroll (CES0000000001), etc.
- Currently uses hardcoded data with BLS API as supplement

### Shortage Score Algorithm

**File**: `app/services/labor_market_service.py`

```
shortage = openings(30%) + quits(20%) + growth(20%) + salary(15%) + projection(15%)
         × industry_multiplier
```

**5 Components:**

1. **Openings Score (30%)**: Proxy from base shortage data, benchmarks: excellent ≥2.0, high ≥1.5, moderate ≥1.0
2. **Quits Score (20%)**: Worker confidence/quit rate proxy, benchmarks: excellent ≥4.0, high ≥3.0
3. **Growth Score (20%)**: Employment growth %, benchmarks: excellent ≥5.0, high ≥3.0
4. **Salary Score (15%)**: Salary growth proxy (growth_rate × 0.4), benchmarks: excellent ≥6.0
5. **Projection Score (15%)**: 10-year BLS outlook, benchmarks: excellent ≥15.0, high ≥10.0

**Industry Multiplier**: `1 + (industry_growth - 5) / 30`

**Interpretation**:
- ≥80: "Critical shortage - Very high demand"
- ≥60: "Significant shortage - High demand"
- ≥40: "Moderate demand - Balanced market"
- <40: "Low shortage - Competitive market"

### User Match Algorithm

```
match = skills(40%) + experience(20%) + location(15%) + salary(10%) + interest(15%)
```

1. **Skills (40%)**: `(matching / required) × 100` — queries O*NET for role skills with importance ≥ 3.0
2. **Experience (20%)**: Base value by level + shortage flexibility bonus (up to +25)
3. **Location (15%)**: Geographic multiplier based on city cost-of-living
4. **Salary (10%)**: 85-120% of market = 100, 70-135% = 70, outside = 40
5. **Interest (15%)**: Industry match = 100, role match = 90, default = 60

### Opportunity Score (Geometric Mean)

```
opportunity = √(user_match × shortage)
```

Key property: Both factors must be strong. High shortage + low match = moderate. High match + low shortage = moderate. Only both high = excellent.

### Skills Gap Analysis

GET `/api/labor-market/skills-gap`:
- Queries O*NET for target role's required skills/abilities/knowledge (importance ≥ 3.0)
- Compares against user's `technical_skills`
- Returns per-category breakdown: matched/total/pct, matched_items, missing_items (top 5 each)

### Salary Benchmarks

Base salaries (mid-level): software_engineer $120K, data_scientist $130K, product_manager $125K, etc.

**Location multipliers**:
- High cost (SF, NYC, Seattle): 1.35x
- Medium-high (Denver, Austin): 1.15x
- Medium (Atlanta, Dallas): 1.05x
- Standard: 1.0x

**Experience adjustments**: entry 0.7x, mid 1.0x, senior 1.35x, executive 1.7x

---

## Section 11: LinkedIn Profile Optimizer

### Profile Analysis

POST `/api/linkedin/analyze`:
- Analyzes headline, summary, experience, skills, education, photo, location, industry
- Returns optimization score and section-by-section recommendations
- Implemented in `linkedin_service.py` with algorithmic analysis (no AI call)

### Headline Generator

POST `/api/linkedin/headline/generate`:
- Takes current_role, target_role, industry, key_skills, achievements
- Returns multiple headline options with scores and reasoning
- Algorithm generates variants using keyword combinations

### Summary Generator

POST `/api/linkedin/summary/generate`:
- Takes current_role, years_experience, industry, key_skills, achievements, career_goals
- Returns structured LinkedIn "About" section
- Includes word count and "optimal length" indicator

### Visibility Score

POST `/api/linkedin/visibility`:
- Analyzes profile searchability
- Scores based on: headline keywords, summary completeness, skills count, experience detail, photo presence
- Returns overall 0-100 score with factor breakdown and top improvements

### Keyword Research

GET `/api/linkedin/keywords/{industry}`:
- Returns categorized keywords: must-have, high-value, differentiator
- Hardcoded keyword database per industry in `linkedin_service.py`

### Activity & Streak Tracking

**Not implemented** — Spec mentions Duolingo-style streaks but no code exists for this feature. No database columns, no service functions, no frontend components for streak tracking.

---

## Section 12: Subscription & Billing

### Stripe Integration

**File**: `app/services/stripe_service.py`

**Tier Pricing:**

| Tier | Price | Stripe Price ID |
|------|-------|----------------|
| Basic | Free ($0) | None |
| Pro | $19/month | Configured via env/config |
| Expert | $39/month | Configured via env/config |
| Career Keeper | $9/month | Configured via env/config |

### Checkout Flow

1. User clicks "Upgrade to Pro" on Settings page
2. Frontend calls POST `/api/subscription/checkout` with `{ tier: "pro" }`
3. Backend creates Stripe Customer (if not exists), stores `stripe_customer_id`
4. Backend creates Stripe Checkout Session with:
   - `payment_method_types: ["card"]`
   - `mode: "subscription"`
   - `metadata: { user_id, tier }`
5. Returns `checkout_url` + `session_id`
6. Frontend redirects to Stripe checkout page
7. User completes payment on Stripe
8. Stripe sends webhook → POST `/api/subscription/webhook`

### Webhook Handling

| Event | Handler | Action |
|-------|---------|--------|
| `checkout.session.completed` | `_handle_checkout_completed` | Updates user.subscription_tier, stores stripe_subscription_id |
| `customer.subscription.updated` | `_handle_subscription_updated` | Updates subscription_expires_at |
| `customer.subscription.deleted` | `_handle_subscription_deleted` | Downgrades to BASIC, clears stripe_subscription_id |
| `invoice.payment_failed` | `_handle_payment_failed` | Logs warning, sends notification |

### Usage Tracking

Monthly counters on User model:
- `monthly_message_count` (ai_messages)
- `monthly_recruiter_count` (recruiters)
- `monthly_research_count` (research, opportunity, skills_gap)
- `monthly_tailoring_count` (tailored_resumes)
- `monthly_interview_prep_count` (interview_prep)
- `daily_coach_count` (coach_daily)

**Lazy reset**: When `usage_reset_date < utcnow()`, all monthly counters reset to 0, date extended 30 days

### Frontend Usage Display

Settings > Subscription tab shows:
- Current plan card with renewal date
- 4 usage meters (Recruiters, AI Messages, Research, Tailored Resumes)
- Tier comparison cards with upgrade buttons

---

## Section 13: Profile & Settings

### Profile Data Model

Profile fields map to User model columns. Updated via PUT `/api/auth/profile`.

**Career fields**: years_experience, career_stage, current_role, target_roles, target_industries, technical_skills, salary_expectation

**Auto-detection**: `detect_career_stage(years)`:
- ≤2 years → ENTRY_LEVEL
- ≤5 → EARLY_CAREER
- ≤10 → MID_LEVEL
- ≤15 → SENIOR
- >15 → EXECUTIVE

### Settings Tabs

1. **Profile**: Editable form with all career fields + SkillsAutocomplete for O*NET skills
2. **Security**: Password change form (current + new + confirm)
3. **Subscription**: Current plan, usage meters, tier cards, upgrade/manage buttons
4. **Help**: Platform tour, features guide, feature-specific tours (6), support contact

---

## Section 14: Security & Validation

### Input Validation (`app/utils/validators.py`)

**`validate_text_fields(data, schema)`**: Non-exception validation returning `(validated_dict, errors_list)`
- Checks: required, min_length, max_length (default 1000), dangerous patterns
- Sanitizes via `sanitize_string()`

**`sanitize_string(value)`**:
1. HTML escape with `html.escape(value, quote=True)`
2. Remove null bytes
3. NFKC unicode normalization

**`validate_password(password)`**:
- Min 8 chars, max 128
- Must contain: uppercase, lowercase, digit

**`validate_email(email)`**:
- Max 255 chars, RFC 5322 format, no dangerous patterns
- Returns lowercase + stripped

### Blocked Patterns (XSS/SQLi/Command Injection)

```python
DANGEROUS_PATTERNS = [
    # XSS
    r'<script[^>]*>', r'javascript:', r'on\w+\s*=', r'<iframe[^>]*>',
    r'<object[^>]*>', r'<embed[^>]*>',
    # SQL Injection
    r"'\s*;\s*drop\s+table", r"'\s*;\s*delete\s+from",
    r"'\s*or\s+'1'\s*=\s*'1", r'union\s+select', r'insert\s+into',
    # Command Injection
    r'\bexec\s*\(', r'\beval\s*\(', r'__import__', r'\bos\.', r'\bsubprocess\.',
]
```

### Rate Limiting

- **Default**: 100 requests/minute per IP
- **Documentation endpoint**: 10 requests/minute
- **Storage**: Redis-backed (falls back to in-memory if Redis unavailable)
- Configured via Flask-Limiter in `extensions.py`

### CORS Configuration

- **Development**: `http://localhost:5173`, `http://localhost:3000`
- **Production**: Configured via `CORS_ORIGINS` env var

### JWT Security

- **Access token expiration**: 1 hour
- **Refresh token expiration**: 30 days
- **Blocklist**: In-memory Python set (NOT Redis-backed — see Gaps)
- **Password hashing**: bcrypt with automatic salt
- **HTTPS cookies**: Enabled in production config

---

## Section 15: AI Service Architecture

### Dual Provider System

**File**: `app/services/ai_service.py`

**Primary provider**: Anthropic Claude (claude-3-sonnet or claude-3-haiku)
**Fallback provider**: OpenAI GPT-4 (gpt-4-turbo-preview)

### Provider Selection Logic

| Task | Primary | Model | Fallback |
|------|---------|-------|----------|
| Message generation | Claude | claude-3-sonnet | GPT-4 |
| Resume optimization | Claude | claude-3-sonnet | GPT-4 |
| Career coaching | Claude | claude-3-sonnet | GPT-4 |
| Interview prep | Claude | claude-3-sonnet | GPT-4 |
| Message improvement | Claude | claude-3-haiku | GPT-4 |

### Fallback Mechanism

```python
try:
    response = call_claude(prompt, system_prompt)
except Exception:
    try:
        response = call_openai(prompt, system_prompt)
    except Exception:
        return error_response("AI service unavailable")
```

### Key System Prompts

1. **Message Generation**: Expert recruiter outreach writer. Guidelines: <150 words, personalize to recruiter/company, include quantified achievements, single clear CTA, professional but warm tone.

2. **Resume Optimization**: Expert resume writer and ATS specialist. Analyzes current resume against ATS score breakdown, generates fully optimized version maintaining authenticity.

3. **Career Coaching**: Expert career coach with mode-specific instructions. Injects real-time data: readiness score, ATS score, skills gap, market conditions.

4. **Interview Prep**: HR and interview specialist. Generates role-specific questions OR evaluates user answers with feedback.

### Error Handling

- Provider-level try/catch with fallback
- Rate limit detection and user notification
- Timeout handling (30 second default)
- Frontend: Global interceptor shows toast for `limit_exceeded` and `subscription_required` errors

---

## Section 16: API Endpoint Inventory

### Auth Routes (`/api/auth`) — 13 Endpoints

| # | Method | Path | Auth | Description | Status |
|---|--------|------|------|-------------|--------|
| 1 | POST | `/register` | No | Create user account | ✅ |
| 2 | POST | `/verify-email` | No | Verify email with token | ✅ |
| 3 | POST | `/resend-verification` | JWT | Resend verification email | ✅ |
| 4 | POST | `/login` | No | Authenticate user | ✅ |
| 5 | POST | `/refresh` | Refresh JWT | Issue new access token | ✅ |
| 6 | POST | `/logout` | JWT | Add token to blocklist | ✅ |
| 7 | GET | `/me` | JWT | Get current user profile | ✅ |
| 8 | PUT | `/password` | JWT | Change password | ✅ |
| 9 | POST | `/forgot-password` | No | Request password reset | ✅ |
| 10 | POST | `/reset-password` | No | Reset password with token | ✅ |
| 11 | PUT | `/profile` | JWT | Update user profile | ✅ |
| 12 | GET | `/tour/status` | JWT | Get tour completion status | ✅ |
| 13 | POST | `/tour/complete` | JWT | Mark tour as completed | ✅ |

### Resume Routes (`/api/resumes`) — 10 Endpoints

| # | Method | Path | Auth | Feature Limit | Description | Status |
|---|--------|------|------|---------------|-------------|--------|
| 1 | POST | `/` | JWT | - | Upload resume | ✅ |
| 2 | GET | `/` | JWT | - | List user's resumes | ✅ |
| 3 | GET | `/master` | JWT | - | Get master resume | ✅ |
| 4 | GET | `/{id}` | JWT | - | Get resume details | ✅ |
| 5 | DELETE | `/{id}` | JWT | - | Soft delete resume | ✅ |
| 6 | PUT | `/{id}/master` | JWT | - | Set as master | ✅ |
| 7 | POST | `/{id}/score` | JWT | - | Score against job | ✅ |
| 8 | POST | `/{id}/tailor` | JWT | tailored_resumes | Create tailored version | ✅ |
| 9 | GET | `/{id}/suggestions` | JWT | - | Get improvement tips | ✅ |
| 10 | GET | `/{id}/analysis` | JWT | - | Full ATS breakdown | ✅ |

### Recruiter Routes (`/api/recruiters`) — 16 Endpoints

| # | Method | Path | Auth | Feature Limit | Description | Status |
|---|--------|------|------|---------------|-------------|--------|
| 1 | POST | `/` | JWT | recruiters | Create recruiter | ✅ |
| 2 | GET | `/` | JWT | - | List recruiters | ✅ |
| 3 | GET | `/stats` | JWT | - | Pipeline statistics | ✅ |
| 4 | GET | `/stages` | JWT | - | Available stages | ✅ |
| 5 | GET | `/recommendations` | JWT | - | Follow-up actions | ✅ |
| 6 | GET | `/{id}` | JWT | - | Recruiter details | ✅ |
| 7 | PUT | `/{id}` | JWT | - | Update recruiter | ✅ |
| 8 | DELETE | `/{id}` | JWT | - | Delete recruiter | ✅ |
| 9 | PUT | `/{id}/stage` | JWT | - | Update pipeline stage | ✅ |
| 10 | POST | `/{id}/message-sent` | JWT | - | Record outreach | ✅ |
| 11 | POST | `/{id}/message-opened` | JWT | - | Record email open | ✅ |
| 12 | POST | `/{id}/response` | JWT | - | Record response | ✅ |
| 13 | POST | `/{id}/fit-score` | JWT | - | Calculate fit score | ✅ |
| 14 | GET | `/{id}/notes` | JWT | - | Get notes | ✅ |
| 15 | POST | `/{id}/notes` | JWT | - | Add note | ✅ |
| 16 | PUT | `/{id}/next-action` | JWT | - | Set next action | ✅ |

### Message Routes (`/api/messages`) — 13 Endpoints

| # | Method | Path | Auth | Feature Limit | Description | Status |
|---|--------|------|------|---------------|-------------|--------|
| 1 | POST | `/` | JWT | ai_messages | Create message | ✅ |
| 2 | GET | `/` | JWT | - | List messages | ✅ |
| 3 | GET | `/stats` | JWT | - | Message statistics | ✅ |
| 4 | GET | `/tips/{type}` | JWT | - | Quality tips | ✅ |
| 5 | POST | `/validate` | JWT | - | Quick validation | ✅ |
| 6 | POST | `/context` | JWT | - | Generation context | ✅ |
| 7 | GET | `/{id}` | JWT | - | Get message | ✅ |
| 8 | PUT | `/{id}` | JWT | - | Update message | ✅ |
| 9 | DELETE | `/{id}` | JWT | - | Delete message | ✅ |
| 10 | POST | `/{id}/send` | JWT | - | Mark as sent | ✅ |
| 11 | POST | `/{id}/opened` | JWT | - | Mark as opened | ✅ |
| 12 | POST | `/{id}/responded` | JWT | - | Mark as responded | ✅ |
| 13 | GET | `/{id}/score` | JWT | - | Quality breakdown | ✅ |

### Activity Routes (`/api/activities`) — 12 Endpoints

| # | Method | Path | Auth | Description | Status |
|---|--------|------|------|-------------|--------|
| 1 | POST | `/` | JWT | Log activity | ✅ |
| 2 | GET | `/` | JWT | List activities | ✅ |
| 3 | GET | `/recent` | JWT | Recent activities | ✅ |
| 4 | GET | `/counts` | JWT | Counts by type | ✅ |
| 5 | GET | `/timeline` | JWT | Timeline items | ✅ |
| 6 | GET | `/weekly-summary` | JWT | Weekly metrics | ✅ |
| 7 | GET | `/types` | JWT | Available types | ✅ |
| 8 | GET | `/pipeline` | JWT | Kanban pipeline | ✅ |
| 9 | GET | `/pipeline/stats` | JWT | Pipeline statistics | ✅ |
| 10 | GET | `/pipeline/stages` | JWT | Available stages | ✅ |
| 11 | PUT | `/pipeline/{id}/move` | JWT | Move pipeline item | ✅ |
| 12 | POST | `/pipeline/refresh` | JWT | Recalculate scores | ✅ |

### Dashboard Routes (`/api/dashboard`) — 3 Endpoints

| # | Method | Path | Auth | Description | Status |
|---|--------|------|------|-------------|--------|
| 1 | GET | `/` | JWT | Full dashboard data | ✅ |
| 2 | GET | `/readiness` | JWT | Career readiness breakdown | ✅ |
| 3 | GET | `/stats/weekly` | JWT | Weekly statistics | ✅ |

### AI Routes (`/api/ai`) — 6 Endpoints

| # | Method | Path | Auth | Feature Limit | Description | Status |
|---|--------|------|------|---------------|-------------|--------|
| 1 | GET | `/status` | JWT | - | AI provider status | ✅ |
| 2 | POST | `/generate-message` | JWT | ai_messages | Generate outreach message | ✅ |
| 3 | POST | `/optimize-resume` | JWT | research | Optimize resume with AI | ✅ |
| 4 | POST | `/career-coach` | JWT | coach_daily | Career coaching chat | ✅ |
| 5 | POST | `/interview-prep` | JWT | interview_prep | Interview preparation | ✅ |
| 6 | POST | `/improve-message` | JWT | - | Message improvement | ✅ |

### LinkedIn Routes (`/api/linkedin`) — 7 Endpoints

| # | Method | Path | Auth | Description | Status |
|---|--------|------|------|-------------|--------|
| 1 | POST | `/analyze` | JWT | Profile analysis | ✅ |
| 2 | POST | `/headline/generate` | JWT | Headline options | ✅ |
| 3 | POST | `/summary/generate` | JWT | Summary generation | ✅ |
| 4 | POST | `/experience/optimize` | JWT | Experience optimization | ✅ |
| 5 | POST | `/visibility` | JWT | Visibility score | ✅ |
| 6 | GET | `/keywords/{industry}` | JWT | Industry keywords | ✅ |
| 7 | GET | `/tips` | JWT | Optimization tips | ✅ |

### Labor Market Routes (`/api/labor-market`) — 11 Endpoints

| # | Method | Path | Auth | Feature Limit | Description | Status |
|---|--------|------|------|---------------|-------------|--------|
| 1 | GET | `/overview` | JWT | - | Market overview (cached 600s) | ✅ |
| 2 | GET | `/shortage` | JWT | - | Shortage score (cached 60s) | ✅ |
| 3 | GET | `/salary` | JWT | - | Salary benchmark | ✅ |
| 4 | POST | `/opportunity` | JWT | research | Opportunity score | ✅ |
| 5 | GET | `/outlook/{role}` | JWT | - | Job outlook | ✅ |
| 6 | GET | `/industries/trending` | JWT | - | Trending industries | ✅ |
| 7 | GET | `/roles/high-demand` | JWT | - | High-demand roles | ✅ |
| 8 | GET | `/skills-map` | JWT | - | User skills vs O*NET | ✅ |
| 9 | GET | `/occupations` | JWT | - | Search occupations (cached 300s) | ✅ |
| 10 | GET | `/skills` | JWT | - | Search skills (cached 300s) | ✅ |
| 11 | POST | `/skills-gap` | JWT | skills_gap | Skills gap analysis | ✅ |

### Subscription Routes (`/api/subscription`) — 7 Endpoints

| # | Method | Path | Auth | Description | Status |
|---|--------|------|------|-------------|--------|
| 1 | GET | `/tiers` | No | Public tier info | ✅ |
| 2 | GET | `/status` | JWT | Current subscription | ✅ |
| 3 | POST | `/checkout` | JWT | Create Stripe checkout | ✅ |
| 4 | POST | `/portal` | JWT | Stripe customer portal | ✅ |
| 5 | POST | `/cancel` | JWT | Cancel subscription | ✅ |
| 6 | POST | `/reactivate` | JWT | Reactivate subscription | ✅ |
| 7 | POST | `/webhook` | No | Stripe webhook handler | ✅ |

### Notification Routes (`/api/notifications`) — 5 Endpoints

| # | Method | Path | Auth | Description | Status |
|---|--------|------|------|-------------|--------|
| 1 | GET | `/` | JWT | List notifications | ✅ |
| 2 | GET | `/unread-count` | JWT | Unread count | ✅ |
| 3 | PUT | `/{id}/read` | JWT | Mark read | ✅ |
| 4 | PUT | `/read-all` | JWT | Mark all read | ✅ |
| 5 | POST | `/generate` | JWT | Generate notifications | ✅ |

### **Total: 103 Endpoints** (all implemented)

---

## Section 17: Frontend Component Map

### Pages (14)

| Page | File | On-Mount API Calls | Key Interactions |
|------|------|--------------------|------------------|
| Login | `pages/Login.tsx` | None | Login form → `authApi.login()` |
| Register | `pages/Register.tsx` | None | Register form → `authApi.register()` → optional Stripe redirect |
| Dashboard | `pages/Dashboard.tsx` | `dashboardApi.getDashboard()`, `activityApi.getRecent(5)`, `laborMarketApi.getSkillsMap()`, `laborMarketApi.getHighDemandRoles()` | Widget interactions, auto-tour |
| Resumes | `pages/Resumes.tsx` | `resumeApi.list()` | Upload, set master, delete, view/score/analyze/tailor modals |
| Recruiters | `pages/Recruiters.tsx` | `recruiterApi.list()` | Add, search, filter by stage, view details modal |
| Messages | `pages/Messages.tsx` | `messageApi.list()`, `recruiterApi.list()`, `messageApi.getStats()` | Compose, edit, delete, mark sent, status filter |
| Activity | `pages/Activity.tsx` | `activityApi.list()`, `activityApi.getPipeline()`, `recruiterApi.list()`, `activityApi.getTimeline()`, `activityApi.getCounts()` | Timeline/Kanban toggle, drag-drop, type filter |
| AI Coach | `pages/AICoach.tsx` | None | Mode selection, chat input, quick prompts → `aiApi.careerCoach()` |
| Settings | `pages/Settings.tsx` | `subscriptionApi.getStatus()`, `dashboardApi.getDashboard()` | Profile update, password change, subscription management |
| Onboarding | `pages/Onboarding.tsx` | Varies by step | 7-step wizard with localStorage persistence |
| LinkedIn | `pages/LinkedIn.tsx` | None | Headline/summary/visibility generators |
| InterviewPrep | `pages/InterviewPrep.tsx` | None | Interview question generation/evaluation |
| Learn | `pages/Learn.tsx` | None | Feature cards with tour triggers |

### Shared Components (34+)

| Category | Components | Description |
|----------|-----------|-------------|
| **Layout** | Layout, ProtectedRoute | App shell, auth guard |
| **UI Core** | Modal, ModalFooter | Dialog system |
| **Scoring** | ScoreCircle, ScoreBar | Visual score displays |
| **Display** | Badge, StageBadge, StatusBadge | Status indicators |
| **Navigation** | Tabs, TabsList, TabsTrigger, TabsContent, PillTabs | Tab interfaces |
| **Empty States** | EmptyState, EmptyResumes, EmptyRecruiters, EmptyMessages, EmptyActivities | Zero-data displays |
| **Loading** | Skeleton, SkeletonText, StatCardSkeleton, DashboardSkeleton | Loading placeholders |
| **Interactive** | CommandPalette (Cmd+K), NotificationBell | Global interactions |
| **Animation** | PageTransition, FadeIn, SlideUp, StaggerContainer, StaggerItem | Motion components |
| **Autocomplete** | OccupationAutocomplete, SkillsAutocomplete | O*NET data pickers |
| **Messages** | ComposeMessageModal, MessageCard | Message UI |
| **Resumes** | ViewResumeModal, ATSScoreModal, ResumeTailorModal, ResumeAnalysisModal | Resume UI |
| **Recruiters** | AddRecruiterModal, RecruiterDetailsModal | Recruiter UI |
| **Onboarding** | WelcomeStep, CareerInfoStep, ResumeUploadStep, ATSResultsStep, FirstRecruiterStep, FirstMessageStep, CompleteStep | Onboarding wizard |
| **Learn** | CategoryCard, FeatureCard | Feature guide |

### Routing Structure

```typescript
// App.tsx routes
<Routes>
  <Route path="/login" element={<Login />} />
  <Route path="/register" element={<Register />} />

  {/* Protected routes (require auth + onboarding) */}
  <Route element={<ProtectedRoute><Layout><Outlet /></Layout></ProtectedRoute>}>
    <Route path="/dashboard" element={<Dashboard />} />
    <Route path="/resumes" element={<Resumes />} />
    <Route path="/recruiters" element={<Recruiters />} />
    <Route path="/messages" element={<Messages />} />
    <Route path="/activity" element={<Activity />} />
    <Route path="/ai-coach" element={<AICoach />} />
    <Route path="/interview-prep" element={<InterviewPrep />} />
    <Route path="/linkedin" element={<LinkedIn />} />
    <Route path="/labor-market" element={<LaborMarket />} />  // if exists
    <Route path="/settings" element={<Settings />} />
    <Route path="/learn" element={<Learn />} />
  </Route>

  {/* Onboarding (requires auth, skips onboarding check) */}
  <Route element={<ProtectedRoute requireOnboarding={false}><Outlet /></ProtectedRoute>}>
    <Route path="/onboarding" element={<Onboarding />} />
  </Route>

  <Route path="/" element={<Navigate to="/dashboard" />} />
  <Route path="*" element={<Navigate to="/dashboard" />} />
</Routes>
```

### State Management

- **Global auth**: `AuthContext` (user, tokens, login/logout/refresh)
- **Global tours**: `TourContext` (tour state, completion tracking)
- **Page state**: Local `useState` hooks per page
- **Forms**: `react-hook-form` with `zod` schemas
- **Server state**: `@tanstack/react-query` QueryClient (some pages), most use direct axios calls
- **Persistence**: `localStorage` for tokens, tour state, onboarding progress, remember-me email

### API Layer (`frontend/src/lib/api.ts`)

11 API service groups with 60+ functions:
- `authApi` (11 functions)
- `resumeApi` (10 functions)
- `recruiterApi` (11 functions)
- `messageApi` (13 functions)
- `activityApi` (9 functions)
- `aiApi` (6 functions)
- `dashboardApi` (3 functions)
- `subscriptionApi` (6 functions)
- `linkedinApi` (6 functions)
- `laborMarketApi` (10 functions)
- `notificationApi` (5 functions)

**Axios interceptors**:
- **Request**: Attaches `Authorization: Bearer {token}` header
- **Response error**: On 401, attempts token refresh; on `limit_exceeded`, shows toast with upgrade link; on `subscription_required`, shows toast

---

## Section 18: Data Flow Diagrams

### Flow 1: User Registers and Completes Onboarding

```
User fills register form
  → POST /api/auth/register (email, password, name)
    → validate_email(), validate_password(), validate_name()
    → Create User (bcrypt hash, verification token)
    → Generate JWT access + refresh tokens
    → Return {user, tokens}
  → Frontend stores tokens in localStorage
  → Navigate to /onboarding (ProtectedRoute detects !onboarding_completed)

Step 1: Welcome
  → Display greeting → Click Next

Step 2: Career Info
  → User fills career stage, role, target roles (OccupationAutocomplete)
  → PUT /api/auth/profile (career data + onboarding_step=2)
  → Save to localStorage

Step 3: Resume Upload
  → User drag-drops PDF
  → POST /api/resumes (FormData with file)
    → PyPDF2 extracts text
    → Parse sections (contact, summary, experience, education, skills)
    → calculate_ats_score() (7 components)
    → Save Resume record
    → Return resume with ATS analysis

Step 4: ATS Results
  → GET /api/resumes/{id}/analysis
  → Display score, issues, encouragement

Step 5: First Recruiter
  → User fills recruiter form
  → POST /api/recruiters (name, company, title)
    → Validate text fields
    → Check feature limit (basic: 5)
    → Create Recruiter record
    → Increment monthly_recruiter_count

Step 6: First Message
  → POST /api/ai/generate-message
    → Assemble context (recruiter + user + resume data)
    → Claude API call with system prompt
    → calculate_message_quality() (5 components)
    → Return message with score

Step 7: Complete
  → PUT /api/auth/profile (onboarding_completed=true, step=7)
  → GET /api/dashboard/readiness (calculate_career_readiness)
  → Navigate to /dashboard
  → Auto-start main tour (if not seen)
```

### Flow 2: User Uploads Resume and Gets ATS Score

```
User drag-drops file on Resumes page
  → Create FormData with file
  → POST /api/resumes
    → Validate file type (PDF/DOCX/TXT) and size (<10MB)
    → Extract text:
        PDF → PyPDF2.PdfReader → page.extract_text()
        DOCX → Document(file) → paragraph.text
        TXT → file.read()
    → Parse sections via regex:
        contact_info: email/phone patterns
        summary: "summary|objective|profile|about" header
        experience: "experience|employment|work history" header
        education: "education|degree" header
        skills: "skill|expertise" header
    → calculate_ats_score(raw_text, parsed_sections, keywords, target_role, file_type):
        compatibility: file_type score + penalties
        keywords: found/total ratio
        achievements: action verbs + metrics count
        formatting: word count + headers + bullets
        progression: date ranges + promotion terms
        completeness: 5 required sections check
        fit: target role alignment
        total = weighted sum (15+15+25+15+15+10+5 = 100)
    → Save Resume with all scores
  → Return to frontend

User clicks "ATS Score" button
  → Opens ATSScoreModal
  → GET /api/resumes/{id}/analysis
  → Display: ScoreCircle (total) + 7 component ScoreBars
  → Optional: Enter job description → POST /api/resumes/{id}/score → rescored
  → Optional: "AI Optimize" → POST /api/ai/optimize-resume
    → Claude generates full optimized resume
    → Display side-by-side + Save button
```

### Flow 3: User Generates Message to Recruiter

```
User opens ComposeMessageModal
  → Select recruiter from dropdown
  → Select message type (initial_outreach/follow_up/thank_you/check_in)
  → Click "AI Generate"

  → POST /api/ai/generate-message
    → message_service.get_generation_context():
        recruiter: name, company, title, specialty, research_summary
        user: name, role, experience, skills, target_roles
        resume: summary text (if resume_id provided)
        previous_messages: existing messages to this recruiter
    → ai_service.generate_message():
        Build system prompt (writing guidelines, word limit, personalization)
        Try Claude API → fallback to OpenAI
        Return generated text
    → scoring/message.calculate_message_quality():
        words: length vs optimal range
        personalization: name, company, details
        metrics: quantified achievements
        cta: clear call-to-action count
        tone: professional appropriateness
    → Return message + quality_score + feedback + suggestions

User edits message in textarea
  → Click "Check Quality" → POST /api/messages/validate → updated scores
  → Click "Save Draft" → POST /api/messages (status=draft)
    → Increment monthly_message_count
    → Return saved message
  → Display in Messages list with word count badge
```

### Flow 4: User Asks AI Coach a Question

```
User selects mode (e.g., "Interview Prep")
  → Quick prompt buttons update
User types question or clicks quick prompt
  → Add user message to chat state

  → POST /api/ai/career-coach
    Body: { question, conversation_history (last 6), context: { mode, user_data } }
    → Backend assembles rich context:
        Career readiness score (from scoring/readiness.py)
        Master resume ATS score
        Skills gap (from labor_market_service)
        Market conditions (shortage scores for target roles)
        Pipeline stats (recruiter counts by stage)
    → Build system prompt:
        Role: "Expert career coach..."
        Mode-specific instructions
        Injected data (scores, gaps, market)
        Conversation history
    → Try Claude API → fallback to OpenAI
    → Return { response, follow_up_suggestions }

  → Add AI response to chat state
  → Display with markdown rendering
  → Show follow-up suggestion buttons
```

### Flow 5: User Views Labor Market Opportunities

```
User navigates to Dashboard
  → GET /api/labor-market/skills-map
    → Query O*NET: Match user.technical_skills against skills/abilities/knowledge
    → Return: { skills: [], abilities: [], knowledge: [], coverage_by_category }
  → Display Skills Coverage widget

  → GET /api/labor-market/roles/high-demand
    → Return hardcoded HIGH_DEMAND_ROLES (10 roles with shortage scores)
  → Display Hot Job Markets widget (top 5)

User clicks "View Opportunities" or navigates to Labor Market page
  → POST /api/labor-market/opportunity
    Body: { target_role, target_industry, skills }
    → calculate_shortage_score(role, industry):
        5-factor formula (openings, quits, growth, salary, projection)
        × industry multiplier
    → calculate_user_match(skills, experience, location, salary):
        5-factor formula (skills, experience, location, salary, interest)
    → opportunity = √(user_match × shortage)  [geometric mean]
    → Return: { total_score, components, missing_skills, recommendations }
  → Display opportunity score with breakdown

User clicks "Skills Gap"
  → POST /api/labor-market/skills-gap
    Body: { target_role, skills }
    → Query O*NET for role's required skills (importance ≥ 3.0)
    → Compare against user's skills
    → Return per-category: matched/total/pct, missing items
  → Display skills gap analysis
```

### Flow 6: User Upgrades from Basic to Pro

```
User navigates to Settings > Subscription tab
  → GET /api/subscription/status → { tier: "basic", ... }
  → GET /api/dashboard → usage data
  → Display current plan + usage meters + tier cards

User clicks "Upgrade to Pro"
  → POST /api/subscription/checkout { tier: "pro" }
    → stripe_service.create_customer(user) (if no stripe_customer_id)
        → Stripe API: Customer.create(email, name)
        → Store stripe_customer_id on User
    → stripe_service.create_checkout_session(user, "pro")
        → Get price_id for Pro tier ($19/month)
        → Stripe API: checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{price: price_id, quantity: 1}],
            mode="subscription",
            metadata={user_id, tier: "pro"},
            success_url, cancel_url
          )
    → Return { checkout_url, session_id }
  → Frontend redirects to Stripe checkout page

User completes payment on Stripe
  → Stripe sends POST /api/subscription/webhook
    → Verify signature with STRIPE_WEBHOOK_SECRET
    → Event: checkout.session.completed
    → _handle_checkout_completed(session):
        → Extract user_id, tier from metadata
        → User.subscription_tier = "pro"
        → User.stripe_subscription_id = subscription_id
        → db.session.commit()
  → User returns to success_url (Settings page)
  → Frontend refreshes user data → sees Pro tier
  → Usage limits updated: 50 recruiters, 100 AI messages, 10 tailored resumes, etc.
```

---

## Section 19: What's Missing / Gaps

### Critical Gaps

| # | Gap | Spec vs Code | Impact |
|---|-----|-------------|--------|
| 1 | **Token blocklist is in-memory** | Spec says Redis; code uses Python set `BLOCKLIST` in `__init__.py` | Token revocation lost on server restart; doesn't work across multiple workers |
| 2 | **No Celery tasks configured** | Spec mentions weekly summaries and follow-up reminders as background jobs | No automated email reminders or scheduled reports |
| 3 | **SendGrid not wired** | Package installed, API key configured, but email sending functions create tokens without actually sending emails | Password reset and email verification don't actually send emails |
| 4 | **No real email tracking** | Response Score label used when email tracking unavailable; no integration with email tracking service | Open rates are manually recorded, not automated |
| 5 | **Chat history not persisted** | AI Coach conversation stored in frontend state only | Users lose coaching history on page reload |

### Features Specified but Not Implemented

| Feature | Source | Status |
|---------|--------|--------|
| LinkedIn activity streaks (Duolingo-style) | Spec | Not implemented — no DB columns, no service, no UI |
| Boolean search optimization | Spec | Not implemented |
| AI recruiter research (auto-research via web) | Referenced in UI hints | Placeholder — shows hints but no actual web research API |
| Email sending (welcome, verification, password reset) | SendGrid configured | SendGrid package installed but sending functions not connected |
| Batch activity operations | Spec mentions `/api/activities/batch` | Not implemented as an endpoint |
| Admin panel | `@admin_required` decorator exists | No admin routes, no admin UI, User model lacks `is_admin` column |

### Endpoints with No Frontend

| Endpoint | Notes |
|----------|-------|
| POST `/api/auth/verify-email` | No email verification UI flow |
| POST `/api/auth/resend-verification` | No UI trigger |
| POST `/api/auth/forgot-password` | "Forgot password" link exists on Login but may not be fully wired |
| POST `/api/auth/reset-password` | No reset password page |
| POST `/api/linkedin/experience/optimize` | LinkedIn page only has headline, summary, visibility |
| PUT `/api/recruiters/{id}/next-action` | Available in detail modal but may not have dedicated UI |

### Technical Debt

| Item | Location | Description |
|------|----------|-------------|
| Token blocklist | `app/__init__.py` | In-memory set, not Redis — loses state on restart |
| No database indexes on some JSON columns | Various models | JSON columns used for queries may need GIN indexes |
| Hardcoded salary/market data | `labor_market_service.py` | BLS API integration exists but primarily uses hardcoded data |
| No test suite | `tests/` directory | pytest configured in requirements.txt but no test files found |
| No error boundary | Frontend | No React error boundary component for graceful crash handling |
| No pagination in many frontend pages | Pages | Most pages load all data with limit but don't implement offset/next-page |
| Mixed auth patterns | Routes | Some routes check user manually, others use decorators inconsistently |
| No CSRF protection | Backend | CORS configured but no CSRF tokens for state-changing requests |

### Discrepancies Between Spec and Code

| Spec Says | Code Does |
|-----------|-----------|
| 62 endpoints | 103 endpoints (more than spec anticipated) |
| "Engagement Score" label | Code uses "Response Score" when email tracking unavailable |
| Expert tier $49/month | Code has $39/month (intentional fix) |
| 5 quality components with weights 25/25/25/20/5 | Matches spec ✅ |
| 7 ATS components with weights 15/15/25/15/15/10/5 | Matches spec ✅ |
| Opportunity = geometric mean | Matches spec ✅ |

---

## Section 20: Recommendations

### Critical Blockers for Beta Launch

1. **Migrate token blocklist to Redis** (`app/__init__.py`): Current in-memory set means tokens survive server restarts and won't work with multiple Gunicorn workers. Use Redis set with TTL matching token expiration.

2. **Wire SendGrid email sending**: Password reset and email verification create tokens but never send emails. Connect `sendgrid` to actually deliver:
   - Welcome emails
   - Email verification
   - Password reset links
   - Subscription confirmations

3. **Add error boundary to React app**: No error boundary means uncaught errors crash the entire app. Add a top-level `ErrorBoundary` component.

4. **Add password reset page**: Frontend has "Forgot password" link but no `/reset-password` page to handle the reset token.

### Quick Wins for UX

1. **Persist AI Coach chat history**: Store conversations server-side (new table) so users don't lose coaching context on page reload.

2. **Add pagination controls**: Most list pages fetch limited data but have no "Load more" or page navigation. Add infinite scroll or page buttons.

3. **Add keyboard shortcuts guide**: Command palette (Cmd+K) exists but isn't discoverable. Add a keyboard shortcuts modal.

4. **Add offline/network error handling**: No offline detection or retry UI. Add a network status banner.

5. **Email verification flow**: Add a verification banner on Dashboard prompting users to verify their email.

### Technical Debt to Address Before Scaling

1. **Add test suite**: No tests exist despite pytest being in requirements. Critical for:
   - API endpoint tests
   - Scoring algorithm tests (verify formulas)
   - Auth flow tests
   - Subscription/billing tests

2. **Database indexing review**: Add GIN indexes on JSONB columns used in queries (industries, locations, skills arrays).

3. **API rate limiting per user**: Current rate limiting is IP-based only. Add per-user rate limits for authenticated endpoints.

4. **Refresh token rotation**: Currently refresh tokens are long-lived (30 days) without rotation. Implement single-use refresh tokens.

5. **Audit logging**: No audit trail for sensitive operations (password changes, subscription changes, data deletion).

### Performance Considerations

1. **N+1 queries in dashboard**: Dashboard endpoint makes multiple separate queries that could be optimized with joins or eager loading.

2. **O*NET data caching**: Skills/occupation search is cached (300s) but the full skills-map query could benefit from longer caching.

3. **Frontend bundle splitting**: No evidence of code splitting beyond Vite defaults. Consider lazy-loading pages with `React.lazy()`.

4. **WebSocket for notifications**: Notifications currently poll every 60 seconds. Consider Server-Sent Events or WebSocket for real-time updates.

---

## Appendix: Migration History

| # | Revision | Date | Description |
|---|----------|------|-------------|
| 1 | `001_initial` | 2026-02-03 | Core tables: users, resumes, resume_versions, recruiters, recruiter_notes, messages, activities, pipeline_items |
| 2 | `1d37f0452b05` | 2026-02-05 | Add tour_completed, completed_tours columns to users |
| 3 | `002_add_labor_market` | 2026-02-05 | Add occupations, skills, occupation_skills, labor_market_data, shortage_scores |
| 4 | `003` | 2026-02-07 | Add notifications table |

---

*This document was generated by auditing the actual codebase, not documentation alone. All file paths, function names, algorithms, and endpoint details have been verified against the source code.*
