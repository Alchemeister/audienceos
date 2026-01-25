# Setup & Development

## Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...          # Claude API
DEEPSEEK_API_KEY=...                  # DeepSeek for bulk processing
DATABASE_URL=postgresql://...          # Postgres connection
REDIS_URL=redis://...                  # Redis for queues

# Reddit API (required for audience research)
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
REDDIT_USER_AGENT=audienceos/1.0

# Twitter/X API (optional, enables Twitter features)
TWITTER_BEARER_TOKEN=...

# Optional but recommended
GITHUB_TOKEN=...                       # Higher rate limits
SENTRY_DSN=...                        # Error tracking
RESEND_API_KEY=...                    # Email delivery

# Stripe (for payments)
STRIPE_SECRET_KEY=...
STRIPE_WEBHOOK_SECRET=...
STRIPE_PRICE_INDIE=price_...
STRIPE_PRICE_PRO=price_...
STRIPE_PRICE_AGENCY=price_...

# App config
APP_ENV=development                    # development, staging, production
APP_URL=http://localhost:3000
API_URL=http://localhost:8000
SECRET_KEY=...                        # For JWT signing

# Feature flags
ENABLE_TWITTER=false                  # Enable Twitter features
ENABLE_GITHUB=false                   # Enable GitHub features
```

---

## Local Setup

```bash
# Clone and setup
git clone <repo>
cd audienceos

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys

# Run migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

---

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

---

## Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Running Background Workers

```bash
# Start Celery worker
celery -A app.tasks worker --loglevel=info

# Start Celery beat (for scheduled tasks)
celery -A app.tasks beat --loglevel=info
```

---

## Deployment

### Backend (Railway/Render)

1. Connect your repo
2. Set environment variables
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel)

1. Connect your repo
2. Set `NEXT_PUBLIC_API_URL` to backend URL
3. Deploy

### Workers (Railway/Render)

Separate service for Celery workers:
- Start command: `celery -A app.tasks worker --loglevel=info`

---

## Development Notes

- **Start with Reddit only.** Twitter/X API is expensive and restrictive.
- **Don't over-engineer auth.** Use Clerk. Focus on core features.
- **Cache aggressively.** Reddit/HN data doesn't change every minute. 1-hour cache minimum.
- **Graceful degradation.** If Reddit API fails, show cached data. Never crash.
- **Mobile-friendly dashboard.** Founders check metrics on phones.
- **Dogfood immediately.** Use AudienceOS to market AudienceOS.
