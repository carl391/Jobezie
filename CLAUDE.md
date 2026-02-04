# CLAUDE.md - Jobezie AI Career Assistant

## Quick Start
```bash
# Backend (Python 3.11+, PostgreSQL, Redis)
pip install -r requirements.txt
flask db upgrade
python run.py  # http://localhost:5000

# Frontend (Node 18+)
cd frontend && npm install && npm run dev  # http://localhost:5173
```

## Tech Stack
- **Backend**: Flask 3.0, SQLAlchemy 2.0, JWT auth, PostgreSQL, Redis, Celery
- **Frontend**: React 19, TypeScript 5.9, Vite 7, Tailwind CSS 4, React Router 7
- **AI**: Claude API (primary), OpenAI GPT-4 (fallback)
- **Payments**: Stripe | **Email**: SendGrid (configured, not wired)

## Project Structure

### Backend (`/app/`)
```
__init__.py              # Flask factory, blueprints, rate limiting, API docs endpoint
config.py                # Environment configs (dev/test/prod), JWT settings
extensions.py            # SQLAlchemy, JWT, Redis, CORS, rate limiter init

models/
  user.py                # User with subscription tiers, usage tracking, career data
  resume.py              # Resume + ResumeVersion, ATS scoring, parsed content
  recruiter.py           # Recruiter + RecruiterNote, pipeline stages, engagement/fit
  message.py             # Message types, quality scoring, generation context
  activity.py            # Activity + PipelineItem, Kanban tracking

routes/
  auth.py                # Register, login, logout, refresh, password reset
  resume.py              # CRUD, scoring, tailoring, analysis, suggestions
  recruiter.py           # CRUD, stages, notes, recommendations, stats
  message.py             # CRUD, AI generation, quality scoring
  activity.py            # Log, timeline, pipeline
  dashboard.py           # Stats, readiness score, recommendations
  ai.py                  # Generate message, optimize resume, career coach, interview prep
  linkedin.py            # Profile analysis, headline/summary generation, visibility
  labor_market.py        # Shortage scores, salary benchmarks, opportunity analysis
  subscription.py        # Stripe checkout, portal, webhooks, tier management

services/
  ai_service.py          # Claude/OpenAI integration, system prompts
  resume_service.py      # File upload, parsing, ATS analysis
  recruiter_service.py   # CRM logic, engagement/fit calculation
  message_service.py     # Quality scoring, templates
  activity_service.py    # Timeline, pipeline tracking
  linkedin_service.py    # Profile optimization, keyword database
  labor_market_service.py # Market data, salary benchmarks
  stripe_service.py      # Subscription management, webhooks
  scoring/               # ats.py, message.py, engagement.py, readiness.py

utils/
  validators.py          # Input validation, XSS/SQLi protection, sanitization
  decorators.py          # @admin_required, @subscription_required, @feature_limit
```

### Frontend (`/frontend/src/`)
```
App.tsx                  # Router setup, QueryClient, protected routes
contexts/AuthContext.tsx # JWT auth state, login/register/logout
lib/api.ts               # Axios client, 7 API service groups, 40+ endpoints
types/index.ts           # 16 TypeScript interfaces (User, Resume, Recruiter, etc.)

components/
  Layout.tsx             # Sidebar nav, top bar, mobile menu, user dropdown
  ProtectedRoute.tsx     # Auth check wrapper
  ui/                    # Modal, ScoreCircle, ScoreBar, Tabs, Badge, EmptyState
  messages/              # ComposeMessageModal, MessageCard
  resumes/               # ViewResumeModal, ATSScoreModal
  recruiters/            # AddRecruiterModal, RecruiterDetailsModal
  onboarding/            # 7-step onboarding flow components

pages/
  Login.tsx              # ✅ Complete - form, validation, password toggle
  Register.tsx           # ✅ Complete - form, password requirements
  Dashboard.tsx          # ✅ Complete - stats, pipeline, activities, recommendations
  Resumes.tsx            # ✅ Complete - upload, list, view, ATS scoring, AI optimize
  Recruiters.tsx         # ✅ Complete - list, search, filter, add, view details
  Messages.tsx           # ✅ Complete - CRUD, quality scoring, AI generation
  Activity.tsx           # ✅ Complete - timeline and Kanban views
  AICoach.tsx            # ✅ Complete - chat interface with AI coaching
  Settings.tsx           # ✅ Complete - profile, security, subscription tabs
  Onboarding.tsx         # ✅ Complete - 7-step onboarding flow
```

## Implementation Status

### Backend - Complete ✅
- **Auth**: Full JWT flow with refresh, password reset
- **Resumes**: Upload, parse, ATS scoring (7 components), tailoring, versioning
- **Recruiters**: Kanban CRM, engagement/fit scoring, notes
- **Messages**: Quality scoring (5 components), AI generation
- **Activities**: Timeline, pipeline management
- **Dashboard**: Career readiness, stats, recommendations
- **LinkedIn Tools**: Profile analysis, headline/summary generation, visibility scoring
- **Labor Market**: Shortage scores, salary benchmarks, opportunity analysis
- **Subscriptions**: Stripe integration, tier management, webhooks

### Frontend - Complete ✅
| Page | Status | Notes |
|------|--------|-------|
| Login/Register | ✅ 100% | Full validation, password requirements |
| Dashboard | ✅ 100% | Stats, pipeline, activities, recommendations |
| Resumes | ✅ 100% | Upload, list, view, ATS scoring, AI optimize |
| Recruiters | ✅ 100% | List, search, filter, add, view details, create message |
| Messages | ✅ 100% | CRUD, quality scoring, AI generation |
| Activity | ✅ 100% | Timeline and Kanban views |
| AI Coach | ✅ 100% | Chat interface with AI coaching |
| Settings | ✅ 100% | Profile, security, subscription tabs |
| Onboarding | ✅ 100% | 7-step flow with backend integration |

### TODO
- **Token Blocklist**: Migrate from in-memory set to Redis
- **Scheduled Jobs**: Add Celery tasks for weekly summaries and follow-up reminders

## API Endpoints (Base: /api)
- `/auth/*` - Authentication flows
- `/resumes/*` - Resume CRUD + ATS analysis
- `/recruiters/*` - CRM operations + notes
- `/messages/*` - Outreach + AI generation
- `/activities/*` - Timeline + pipeline
- `/dashboard/*` - Stats + readiness score
- `/ai/*` - Generate message, optimize resume, career coach
- `/linkedin/*` - Profile analysis, headline/summary generation
- `/labor-market/*` - Shortage, salary, opportunity scores
- `/subscription/*` - Stripe checkout, portal, webhooks

## Key Models
- **User**: UUID PK, tiers (BASIC/PRO/EXPERT/CAREER_KEEPER), usage limits, career data
- **Resume**: ATS scoring (7 components: compatibility, keywords, achievements, formatting, progression, completeness, fit)
- **Recruiter**: Pipeline (8 stages), engagement score (response/open/recency), fit score
- **Message**: Types (initial/follow-up/thank-you/check-in), quality score (5 components)
- **Activity**: 13 activity types, pipeline stages, priority scoring

## Recent Changes (Feb 2026)
- `c1d2c2f` - Rate limiting (100 req/min), env-aware API docs
- `e252db1` - Root endpoint with API documentation
- `205b926` - Python 3.13 fix: psycopg2-binary 2.9.10
- `366a936` - Python 3.13 fix: SQLAlchemy 2.0.36, Alembic 1.14.0

## Environment Variables
```
DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY
ANTHROPIC_API_KEY, OPENAI_API_KEY
STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET
SENDGRID_API_KEY, REDIS_URL
CORS_ORIGINS, FLASK_ENV, FRONTEND_URL
VITE_API_URL (frontend)
```

## Notes
- Subscription limits: BASIC (5 recruiters, 2 resumes), PRO (50/10), EXPERT (unlimited)
- AI fallback: Claude → OpenAI if Claude fails
- Rate limiting: 100 req/min default, 10/min for docs endpoint
- Deployment ready: Render (primary), Railway, Heroku
- Health check: `/health` endpoint
