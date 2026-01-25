# AudienceOS

**Full-stack audience intelligence for founders, product teams, and agencies.**

Find where your audience hangs out → Reach them with great content → Listen to what they're saying → Adapt based on real feedback.

## The Problem

Founders and product teams waste hours:
- **Guessing** where to market (posting in wrong places)
- **Missing** what customers actually say (feedback scattered across 10+ sources)
- **Not knowing** what marketing actually converts (vanity metrics, no attribution)

Current tools are either:
- **Too expensive:** Brandwatch, Meltwater ($10K-100K/yr)
- **Too narrow:** SparkToro (audience only), Canny (feedback only), Brand24 (monitoring only)
- **Dead:** GummySearch shut down Nov 2025, leaving 135K users stranded

## The Solution

One platform that closes the loop:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    FIND     │ ──▶ │    REACH    │ ──▶ │   LISTEN    │ ──▶ │    ADAPT    │
│  audiences  │     │   content   │     │  feedback   │     │  insights   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

1. **FIND:** Paste your product description → Get top subreddits, Twitter accounts, HN topics
2. **REACH:** AI generates non-spammy content + tracks clicks/conversions
3. **LISTEN:** Auto-monitors Reddit, Twitter, collects widget feedback, analyzes sentiment
4. **ADAPT:** Weekly reports with actionable insights ("47 complaints about onboarding this week")

---

## Viability Score: 7.7/10 - BUILD

| Factor | Score | Notes |
|--------|-------|-------|
| Problem Severity | 9/10 | 90% of founders say marketing is hardest; 80% of feedback never acted on |
| Market Size | 8/10 | Audience intel ($8B→$34B), Feedback ($2.3B→$5.1B), Sentiment ($6B+) |
| Willingness to Pay | 8/10 | Replaces 3-4 tools; agencies pay $100-500/mo for this |
| Competition | 6/10 | NO affordable combined solution exists |
| Feasibility | 6/10 | Complex but APIs available; scope managed via phasing |
| Timing | 8/10 | Only 17% use AI for feedback; GummySearch dead; gap open |

### Why This Wins

- **Gap in market:** Enterprise tools exist ($10K+/yr) but nothing for SMBs at $39-299/mo
- **Full loop:** Competitors do one piece; this connects find → reach → listen → adapt
- **AI timing:** Claude makes sentiment analysis + content gen accessible now
- **GummySearch opportunity:** 135K users actively seeking alternatives

### Key Risks

- Scope creep (mitigate: strict phasing)
- API dependencies (mitigate: graceful degradation)
- Indie hackers are cheap (mitigate: agency tier focus)

---

## Pricing

| Tier | Price | Products | Key Features |
|------|-------|----------|--------------|
| **Indie** | $39/mo | 1 | Audience research, content gen, basic monitoring |
| **Pro** | $99/mo | 3 | Full monitoring, advanced sentiment, API access |
| **Agency** | $299/mo | Unlimited | White-label, team seats, custom integrations |

---

## Quick Start

```bash
# Clone
git clone <repo>
cd audienceos

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your ANTHROPIC_API_KEY, REDDIT_* credentials

# Run backend
uvicorn app.main:app --reload

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

---

## Tech Stack

- **Backend:** Python 3.11+, FastAPI, PostgreSQL, Redis, Celery
- **Frontend:** Next.js 14, TypeScript, Tailwind, shadcn/ui
- **AI:** Anthropic Claude API
- **Data:** Reddit API, Twitter/X API, HN Algolia
- **Payments:** Stripe
- **Auth:** Clerk

---

## Features

### Marketing Scout
- Audience research from product description
- Reddit subreddit discovery + ranking
- HN topic/keyword discovery
- AI content generation (3 styles: helpful, story, question)
- UTM link tracking
- Click → signup → conversion attribution

### Feedback Aggregator
- Reddit mention monitoring
- Twitter/X mention monitoring
- Embeddable feedback widget
- Sentiment analysis (positive/negative/neutral + emotions)
- Category detection (bug, feature request, complaint, praise)
- Theme clustering ("Onboarding issues" - 47 mentions)

### Unified Insights
- Single dashboard for marketing + feedback
- Weekly automated email reports
- AI chat interface ("What are people complaining about?")
- Churn risk detection
- Recommended actions

---

## Roadmap

### MVP (Weeks 1-4)
- [x] Audience research (Reddit + HN)
- [x] Content generation
- [x] Link tracking + conversions
- [x] Feedback monitoring (Reddit)
- [x] Sentiment analysis
- [x] Weekly reports

### Phase 2 (Weeks 5-8)
- [ ] Twitter/X integration
- [ ] GitHub monitoring (for dev tools)
- [ ] Team collaboration
- [ ] Slack notifications
- [ ] Competitor tracking

### Phase 3 (Future)
- [ ] AI chat interface
- [ ] White-label for agencies
- [ ] App store review monitoring
- [ ] Auto-posting (with approval)
- [ ] Predictive insights

---

## Competitors Comparison

| Feature | AudienceOS | SparkToro | Canny | Brand24 | Brandwatch |
|---------|------------|-----------|-------|---------|------------|
| Audience research | ✅ | ✅ | ❌ | ❌ | ✅ |
| Content generation | ✅ | ❌ | ❌ | ❌ | ❌ |
| Conversion tracking | ✅ | ❌ | ❌ | ❌ | ❌ |
| Feedback collection | ✅ | ❌ | ✅ | ❌ | ❌ |
| Social listening | ✅ | ❌ | ❌ | ✅ | ✅ |
| Sentiment analysis | ✅ | ❌ | ❌ | ✅ | ✅ |
| AI insights | ✅ | ❌ | ❌ | ❌ | ✅ |
| SMB pricing | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Price** | $39-299/mo | $50-300/mo | $79-359/mo | $49-149/mo | $10K+/yr |

---

## Documentation

See [CLAUDE.md](./CLAUDE.md) for:
- Full technical specification
- Data models (Pydantic)
- API endpoints
- Claude prompts
- Build order
- Improvement ideas

---

## License

MIT

---

## Contributing

This is a personal project, but PRs welcome. Please read CLAUDE.md first to understand the architecture.
