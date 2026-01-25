# Features

## MVP Features

### Marketing Scout (Acquisition Hook)

#### Audience Research
**Input:** Product description (paste README or describe in 2-3 sentences)

**Output:**
- Top 10 subreddits where audience hangs out (ranked by relevance)
- Top 5 Twitter/X accounts to follow/engage
- Top 3 HN topics/keywords to monitor
- Competitor mentions and sentiment

**How It Works:**
```
User Input → Claude extracts keywords/personas →
  Parallel search (Reddit + HN + Twitter) →
  Claude ranks by relevance + activity →
  Return sorted results with reasoning
```

#### AI-Powered Keyword Discovery
Users shouldn't have to guess what keywords to monitor. The AI generates:
- Brand name variations and common misspellings
- Founder/team names (if detectable from site)
- Competitor names (for comparison tracking)
- Problem phrases ("how do I track API costs")
- Solution phrases ("API billing dashboard")
- Industry jargon and abbreviations

#### Content Generation
**Input:** Target platform + audience + product info
**Output:** 3 post variations (helpful, story, question)

Posts are NON-PROMOTIONAL. They solve problems, share insights, or ask questions. No "check out my product" spam.

#### Link Tracking
- UTM link generation
- Short URL service (aos.link)
- Click tracking
- Conversion tracking (JS snippet + webhooks)

---

### Feedback Aggregator (Retention Hook)

**This is the core retention engine.** See CLAUDE.md for why this matters.

#### Multi-Source Feedback Collection

**Sources (MVP):**
1. Reddit Mentions - Monitor subreddits + keywords
2. Twitter/X Mentions - Track @mentions + keywords
3. Embedded Widget - Simple form for email/website
4. Manual Import - CSV upload

**Sources (Post-MVP):**
- App Store / Play Store reviews
- G2, Capterra, Trustpilot
- Discord/Slack integrations
- Intercom/Zendesk integrations

#### The Feedback Bucket
This is NOT about analyzing one post's comments. The system:
1. Monitors for product/brand mentions across ALL sources
2. Collects every mention into a unified bucket
3. Analyzes the bucket as a corpus - patterns, trends, recurring issues
4. Generates actionable insights

#### Historical Backfill
On signup, backfill historical mentions so users see immediate value:
- Indie: 2 weeks
- Pro: 90 days
- Agency: 6 months+

#### Sentiment Analysis
Each piece of feedback gets:
- **Sentiment:** positive / negative / neutral / mixed
- **Emotion:** frustrated, happy, confused, requesting, comparing
- **Category:** bug, feature request, praise, complaint, question, churn risk
- **Urgency:** low / medium / high / critical
- **Product Area:** auto-detected

#### Feedback Dashboard
- Real-time feed view
- Filters (source, sentiment, category, date)
- Theme clustering ("Onboarding Issues" - 47 mentions)
- Trends over time

---

### Unified Insights

#### Weekly Report (Automated)
Every Monday, users get:
- Marketing performance summary
- Best/worst performing content
- Sentiment trends
- Top complaints and praise
- AI-generated action recommendations
- Next week focus areas

#### Deep Analysis (Pro+ Only)
Agent-based analysis that spends more compute on thorough insights:
- Deep Churn Analysis
- Competitor Intelligence Report
- Content Strategy Recommendation
- Weekly Executive Summary

---

## Post-MVP Features

### Marketing Scout Enhancements

#### Post Timing Optimizer
Analyze when target subreddits are most active:
- "Best time to post in r/SaaS: Tuesday 10am EST"
- "Avoid weekends in r/webdev - 60% less engagement"

#### Subreddit Rule Analyzer
Before generating content, AI reads subreddit rules:
- Auto-flag posts that might violate rules
- Adjust tone/format based on community norms

#### Post Performance Feedback Loop
Track what worked and feed back into generation:
- "Your 'story' posts convert 3x better than 'helpful'"
- AI learns your winning patterns

#### Competitor Content Tracking
See what competitors post and how it performs:
- "CompetitorX posted in r/SaaS, got 200 upvotes"
- Gaps in their strategy you could fill

#### Multi-Platform Campaign Sync
Same message adapted for Reddit/Twitter/HN/LinkedIn

---

### Feedback Aggregator Enhancements

#### Reddit Insider Scoring
Weight feedback by user credibility:
- Account age
- Karma in relevant subreddits
- Post history quality

#### Competitive Intelligence Loop
Track what people say about competitors:
- "X is too expensive" → pricing opportunity
- "X lacks feature Y" → roadmap signal

#### Churn Early Warning System
Combine signals:
- Negative feedback from known customer
- Support ticket escalation
- Social complaint pattern

#### Reply Suggestions
When someone mentions your product:
- AI drafts a helpful response
- Flags high-priority mentions

---

### Advanced Intelligence

#### AI Chat Interface
Natural language queries:
- "What are people complaining about most?"
- "What subreddits should I post in this week?"

#### Unified "Signal Score"
One health metric combining marketing + sentiment:
- "Signal Score: 73 (up from 68)"
- Breaks down: Reach, Engagement, Sentiment, Conversion

#### Smart Alerts
Proactive notifications:
- "Spike in negative mentions (5x normal)"
- "Your r/SaaS post is trending"

#### ROI Calculator
Show clear dollar value:
- "Time saved: ~15 hours"
- "Leads generated: 47"
- "Churns prevented: 3"

#### "What Should I Do Today?"
AI-prioritized daily action list

---

## Pricing & Tier Limits

### Indie - $39/mo
- 1 product
- Audience research (10/month)
- Content generation (50 posts/month)
- Basic feedback monitoring (Reddit only)
- Weekly email reports
- 500 feedback items/month
- **AI Keyword Discovery:** Basic (5-8 suggestions)
- **Keyword Limit:** 10 keywords
- **Backfill Depth:** 2 weeks
- **Deep Analysis:** Not included

### Pro - $99/mo
- 3 products
- Unlimited audience research
- Unlimited content generation
- Full feedback monitoring (Reddit + Twitter + widget)
- Advanced sentiment analysis
- 5,000 feedback items/month
- API access
- Priority support
- **AI Keyword Discovery:** Full (20+ suggestions) + ongoing
- **Keyword Limit:** 50 keywords
- **Backfill Depth:** 90 days
- **Deep Analysis:** 4 credits/month

### Agency - $299/mo
- Unlimited products
- Everything in Pro
- White-label reports
- Client management dashboard
- Unlimited feedback items
- Team seats (up to 10)
- Dedicated support
- Custom integrations
- **AI Keyword Discovery:** Full + per-client custom
- **Keyword Limit:** Unlimited
- **Backfill Depth:** 6 months+
- **Deep Analysis:** Unlimited
