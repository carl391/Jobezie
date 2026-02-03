# CLAUDE.md - Jobezie AI Career Assistant

## Quick Start
```bash
# Backend (Python 3.9+, PostgreSQL, Redis)
pip install -r requirements.txt
flask db upgrade
python run.py  # http://localhost:5000

# Frontend (Node 18+)
cd frontend && npm install && npm run dev  # http://localhost:5173
```

## Tech Stack
- **Backend**: Flask 3.0, SQLAlchemy, JWT auth, PostgreSQL, Redis caching
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS, React Router 7
- **AI**: Claude API (primary), OpenAI GPT-4 (fallback)
- **Payments**: Stripe | **Email**: SendGrid (configured, not wired)

## Project Structure
```
/app/
  __init__.py          # Flask factory, blueprints, error handlers
  config.py            # Environment configs (dev/test/prod)
  models/              # SQLAlchemy models (User, Resume, Recruiter, Message, Activity)
  routes/              # API blueprints (auth, resume, recruiter, message, activity, dashboard, ai)
  services/            # Business logic (ai_service, resume_service, recruiter_service, etc.)
  utils/               # Validators, decorators

/frontend/src/
  App.tsx              # Router, protected routes
  contexts/AuthContext.tsx  # JWT auth state
  lib/api.ts           # Axios client with interceptors
  pages/               # Route components
  components/          # Shared UI components
  types/index.ts       # TypeScript interfaces
```

## Implementation Status

### Complete
- **Auth**: Register, login, logout, JWT refresh, password reset
- **Resumes**: CRUD, ATS scoring (7-component, 100-point scale), tailoring, versioning
- **Recruiters**: Kanban CRM, engagement/fit scoring, notes, research data
- **Messages**: Compose, AI generation, quality scoring (5-component)
- **Activities**: Logging, timeline, pipeline management
- **Dashboard**: Career readiness score, stats, follow-up recommendations
- **Frontend Pages**: Dashboard, Login, Register, Resumes, Recruiters (Kanban board)

### TODO (Stubs/Incomplete)
- **Frontend Pages**: Messages, Activity, AI Coach, Settings (show "coming soon")
- **LinkedIn OAuth**: Routes defined, implementation incomplete
- **Resume Parsing**: Model structure exists, actual PDF/DOCX parsing not implemented
- **Email Notifications**: SendGrid configured but not integrated
- **Interview Prep**: AI service skeleton only
- **Token Blocklist**: Uses in-memory set, needs Redis for production

## Key Models

**User**: UUID PK, subscription tiers (BASIC/PRO/EXPERT/CAREER_KEEPER), usage limits
**Resume**: ATS scoring (compatibility, keywords, achievements, formatting, progression, completeness, fit)
**Recruiter**: Engagement score (response/open/recency), Fit score (industry/location/specialty/tier)
**Message**: Quality score (word count, personalization, metrics, CTA, tone)
**Activity**: Pipeline stages (NEW→RESEARCHING→CONTACTED→RESPONDED→INTERVIEWING→OFFER→ACCEPTED/DECLINED)

## API Endpoints (Base: /api)
- `/auth/*` - Authentication flows
- `/resumes/*` - Resume CRUD + ATS analysis
- `/recruiters/*` - CRM operations + notes
- `/messages/*` - Outreach + AI generation
- `/activities/*` - Timeline + pipeline
- `/dashboard/*` - Stats + readiness score
- `/ai/*` - Generate message, optimize resume, career coach

## Environment Variables
```
DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY
ANTHROPIC_API_KEY, OPENAI_API_KEY
STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET
SENDGRID_API_KEY, REDIS_URL
CORS_ORIGINS, FLASK_ENV
VITE_API_URL (frontend)
```

## Notes
- Subscription tier limits: BASIC (5 recruiters, 2 resumes), PRO (50/10), EXPERT (unlimited)
- AI fallback: Claude → OpenAI if Claude fails
- Deployment configs ready: Railway, Render, Heroku
- Single initial commit (Feb 2026) - this is baseline state
