# Roadmap

## Phase 1: MVP Foundation (Weeks 1-2)

**Goal:** Core infrastructure and basic audience research working end-to-end.

### Backend Foundation
- [ ] Project setup (FastAPI scaffold, folder structure)
- [ ] Database models + SQLAlchemy setup
- [ ] Alembic migrations
- [ ] Basic auth (Clerk integration)
- [ ] API structure (v1 routes)

### AI Infrastructure
- [ ] Claude API wrapper (services/ai/claude.py)
- [ ] Tiered model routing (cheap vs expensive models)
- [ ] DeepSeek/Haiku integration for bulk processing
- [ ] Prompt templates system

### Audience Research (Marketing Scout - Acquisition Hook)
- [ ] Reddit API integration
- [ ] AI-powered keyword discovery from product description
- [ ] Subreddit discovery + relevance scoring
- [ ] HN Algolia integration
- [ ] Audience research endpoint
- [ ] Basic frontend (product input → results)

---

## Phase 2: Content & Tracking (Weeks 3-4)

**Goal:** Users can generate content and track what converts.

### Content Generation
- [ ] Content generation prompts (helpful, story, question styles)
- [ ] Subreddit rule analyzer (read rules before generating)
- [ ] Content generation endpoint
- [ ] Post preview UI

### Link Tracking
- [ ] UTM link generation
- [ ] Short URL service (aos.link redirect)
- [ ] Click tracking
- [ ] Conversion tracking (JS snippet)
- [ ] Webhook receiver for external conversions (Stripe, etc.)

### Campaign Dashboard
- [ ] Campaign CRUD
- [ ] Stats display (clicks, conversions, rates)
- [ ] Per-post performance breakdown

---

## Phase 3: Feedback Aggregator (Weeks 5-6)

**Goal:** The retention engine is live. Users have ongoing value.

### Mention Monitoring
- [ ] Reddit mention monitoring (background jobs via Celery)
- [ ] Keyword-based monitoring (not just brand name)
- [ ] Historical backfill on signup (90 days for Pro, 2 weeks for Indie)
- [ ] Twitter/X mention monitoring (if API accessible)
- [ ] HN mention monitoring

### Feedback Collection
- [ ] Embeddable feedback widget
- [ ] Email feedback ingestion
- [ ] Manual CSV import
- [ ] Webhook receiver for support tools

### Sentiment & Analysis
- [ ] Tiered sentiment analysis (cheap model filters → expensive model analyzes)
- [ ] Category detection (bug, feature, complaint, praise, churn risk)
- [ ] Key phrase extraction
- [ ] Urgency scoring

### Feedback Dashboard
- [ ] Real-time feed view
- [ ] Filters (source, sentiment, category, date)
- [ ] Search within feedback
- [ ] Mark as actioned

---

## Phase 4: Insights & Intelligence (Weeks 7-8)

**Goal:** AI makes sense of the data and tells users what to do.

### Theme Clustering
- [ ] Auto-cluster feedback into themes
- [ ] Theme dashboard ("Onboarding Issues" - 47 mentions)
- [ ] Sentiment breakdown per theme

### Weekly Reports
- [ ] Automated report generation (every Monday)
- [ ] Email delivery (Resend)
- [ ] Dashboard report view
- [ ] Marketing performance summary
- [ ] Feedback sentiment summary
- [ ] AI-generated recommendations

### Deep Analysis (Pro+ Feature)
- [ ] Agent-based analysis system
- [ ] "Deep Churn Analysis" agent
- [ ] "Competitor Intelligence Report" agent
- [ ] "Content Strategy Recommendation" agent
- [ ] Credit system for Pro tier

---

## Phase 5: Polish & Launch (Weeks 9-10)

**Goal:** Production-ready, payments working, launched.

### Payments & Tiers
- [ ] Stripe integration
- [ ] Tier enforcement (keyword limits, backfill depth, features)
- [ ] Upgrade/downgrade flows
- [ ] Usage tracking & limits

### Production Readiness
- [ ] Error tracking (Sentry)
- [ ] Logging & monitoring
- [ ] Rate limiting
- [ ] Caching layer (Redis)
- [ ] Graceful degradation (API failures don't crash app)

### Launch
- [ ] Landing page
- [ ] Documentation / help center
- [ ] Onboarding flow
- [ ] Deploy to production (Vercel + Railway/Render)
- [ ] Dogfood: Use AudienceOS to market AudienceOS

---

## Post-MVP Roadmap

### Phase 6: Marketing Scout Enhancements

- [ ] Post timing optimizer (best times to post per subreddit)
- [ ] Post performance feedback loop (learn what works)
- [ ] Competitor content tracking
- [ ] Multi-platform campaign sync (Reddit → Twitter → LinkedIn)
- [ ] A/B title suggestions

### Phase 7: Feedback Aggregator Enhancements

- [ ] Reddit insider scoring (weight by account credibility)
- [ ] Competitive intelligence loop (track competitor mentions)
- [ ] Churn early warning system (combine signals)
- [ ] Reply suggestions (AI drafts responses to mentions)
- [ ] App Store / Play Store review monitoring
- [ ] G2 / Capterra / Trustpilot integration

### Phase 8: Advanced Intelligence

- [ ] AI chat interface ("What should I post this week?")
- [ ] Unified "Signal Score" (brand health metric)
- [ ] Smart alerts system (spike detection, trending posts)
- [ ] ROI calculator dashboard
- [ ] "What Should I Do Today?" daily action list
- [ ] Audience evolution tracking (quarterly reports)

### Phase 9: Scale & Enterprise

- [ ] White-label for agencies
- [ ] Team collaboration (comments, assignments)
- [ ] Slack/Discord notifications
- [ ] Zapier/Make integrations
- [ ] Custom API for integrations
- [ ] Multi-language support
- [ ] Custom AI training on brand voice

---

## Build Order (Quick Reference)

For those who want the linear checklist:

### MVP (Weeks 1-10)
1. [ ] FastAPI + Next.js scaffold
2. [ ] Database models + migrations
3. [ ] Auth (Clerk)
4. [ ] AI infrastructure (Claude + DeepSeek tiering)
5. [ ] Reddit API integration
6. [ ] AI keyword discovery
7. [ ] Audience research endpoint + UI
8. [ ] Content generation
9. [ ] Link tracking + conversions
10. [ ] Campaign dashboard
11. [ ] Reddit mention monitoring
12. [ ] Historical backfill
13. [ ] Feedback widget
14. [ ] Sentiment analysis pipeline
15. [ ] Feedback dashboard
16. [ ] Theme clustering
17. [ ] Weekly reports
18. [ ] Deep analysis agents (Pro+)
19. [ ] Stripe + tier enforcement
20. [ ] Landing page + deploy
