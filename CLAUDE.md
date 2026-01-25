# AudienceOS

B2B SaaS that helps founders find their audience, reach them with content, and listen to feedback. Replaces SparkToro + Canny + Brand24.

## Critical Context

**READ THIS FIRST - it affects all implementation decisions.**

### Business Model

AudienceOS has TWO features that serve different purposes:

1. **Marketing Scout (Acquisition Hook)** - Find where your audience hangs out, generate content, track conversions. Valuable but potentially one-time - once you know your subreddits, you know them.

2. **Feedback Aggregator (RETENTION HOOK)** - This is the real product. Monitors mentions across Reddit/Twitter/HN/email/widgets, collects them into a unified "bucket", analyzes patterns over time. Users keep paying because:
   - Mentions never stop (inherently ongoing)
   - The bucket gets smarter over time (6 months of data > 1 week)
   - Multi-source aggregation is the moat
   - Analytics create dependency ("r/SaaS converts 12%, r/webdev 3%")

**The feedback aggregator is NOT about analyzing comments on a single post.** It's about collecting EVERY mention of the product across ALL sources into one bucket, then analyzing that corpus for patterns and actionable insights.

### Cold Start Solution

New users have an empty bucket. Solve with **historical backfill**:
- On signup, search last 2-90 days of Reddit/HN/Twitter mentions
- Dashboard is immediately populated
- "We found 47 mentions in the last 90 days. Here's what people are saying."

### AI Cost Management

Use **tiered models** to keep costs sustainable:
- **Cheap models** (DeepSeek, Haiku): relevance filtering, basic classification, keyword extraction
- **Expensive models** (Claude): nuanced sentiment, insight generation, content creation

Flow: 1000 raw mentions → cheap model filters to 150 relevant → expensive model analyzes batch → 1 insight report

### AI Keyword Discovery

Users shouldn't guess keywords. AI generates:
- Brand variations + misspellings
- Founder names
- Competitor names
- Problem phrases ("how do I track API costs")
- Solution phrases

Tiered: Indie gets 10 keywords, Pro gets 50, Agency unlimited.

## Docs

Detailed documentation split into focused files:

| File | Contents |
|------|----------|
| `docs/ARCHITECTURE.md` | Tech stack, AI tiering, project structure, data models |
| `docs/ROADMAP.md` | Full roadmap, build order, phases |
| `docs/API.md` | Endpoints, auth, CLI commands |
| `docs/PROMPTS.md` | AI prompt templates |
| `docs/FEATURES.md` | Detailed feature specs, pricing tiers, improvement ideas |
| `docs/SETUP.md` | Dev workflow, env vars, deployment |
| `docs/SECURITY.md` | Security checklist, audit prompts, common vulnerabilities |

## Security (Non-Negotiable)

**Read `docs/SECURITY.md` before writing any auth, API, or payment code.**

Key rules:
1. **Gatekeep every action** - Check authorization on EVERY endpoint, not just authentication
2. **Don't hide, withhold** - Premium features aren't hidden client-side, they're not sent at all
3. **Secrets off browser** - No API keys in client code (check for NEXT_PUBLIC_ prefixed secrets)
4. **Server does math** - All pricing, scoring, sensitive logic on backend only
5. **Sanitize everything** - Never trust user input
6. **Rate limit buttons** - Prevent bots from spamming expensive operations
7. **Don't log secrets** - No passwords, tokens, or keys in logs
8. **Audit with rival AI** - Before launch, have Gemini/GPT audit code Claude wrote
9. **Update dependencies** - Run `npm audit` / `pip-audit` weekly
10. **Vague errors to users** - Log details privately, show generic messages publicly

## Quick Reference

**Tech:** Python/FastAPI backend, Next.js frontend, PostgreSQL, Redis/Celery, Claude + DeepSeek

**Tiers:**
- Indie $39/mo: 1 product, 10 keywords, 2-week backfill
- Pro $99/mo: 3 products, 50 keywords, 90-day backfill, 4 deep analysis credits
- Agency $299/mo: Unlimited everything

**Key Risk:** Scope creep. This is 2 products in one. Phase the build carefully.

**Start with:** Reddit only. Twitter/X API is expensive and restrictive.
