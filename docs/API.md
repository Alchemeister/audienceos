# API Reference

## Authentication

All API requests require Bearer token:
```
Authorization: Bearer <api_key>
```

API keys are scoped to organization. Rate limits:
- Indie: 100 req/min
- Pro: 500 req/min
- Agency: 2000 req/min

---

## Endpoints Overview

```
# Audience Research
POST   /api/v1/audiences/research     # Start research
GET    /api/v1/audiences/{id}         # Get research results
GET    /api/v1/audiences              # List all audiences

# Campaigns
POST   /api/v1/campaigns              # Create campaign
GET    /api/v1/campaigns/{id}         # Get campaign
POST   /api/v1/campaigns/{id}/generate  # Generate posts
GET    /api/v1/campaigns/{id}/stats   # Get stats

# Tracking
POST   /api/v1/tracking/links         # Create tracked link
POST   /api/v1/tracking/convert       # Record conversion
GET    /api/v1/tracking/stats         # Get tracking stats

# Feedback
GET    /api/v1/feedback               # List feedback
POST   /api/v1/feedback/analyze       # Analyze text
GET    /api/v1/feedback/themes        # Get clustered themes
POST   /api/v1/feedback/webhook       # Incoming webhook

# Insights
GET    /api/v1/insights               # List insights
GET    /api/v1/insights/report        # Get weekly report
POST   /api/v1/insights/chat          # AI chat

# Products
POST   /api/v1/products               # Create product
GET    /api/v1/products/{id}          # Get product
PUT    /api/v1/products/{id}          # Update product
```

---

## Audience Research

### Start Research

```
POST /api/v1/audiences/research
{
  "product_description": "An API cost tracker for dev teams...",
  "product_url": "https://example.com",  // optional, will scrape
  "focus": "b2b" | "b2c" | "developer"   // optional hint
}

Response:
{
  "audiences": [
    {
      "platform": "reddit",
      "name": "r/SaaS",
      "relevance_score": 0.92,
      "monthly_active": 125000,
      "recent_relevant_posts": 23,
      "reasoning": "High concentration of SaaS founders discussing costs...",
      "sample_posts": [...]
    },
    ...
  ],
  "keywords": ["api costs", "usage tracking", "billing alerts"],
  "competitors_mentioned": ["AWS Cost Explorer", "Cloudability"],
  "confidence": "high"
}
```

---

## Content Generation

```
POST /api/v1/campaigns/generate
{
  "audience_id": "aud_123",
  "platform": "reddit",
  "subreddit": "r/SaaS",
  "style": "helpful",  // helpful, story, question, insight
  "topic_hint": "api costs"  // optional
}

Response:
{
  "posts": [
    {
      "style": "helpful",
      "title": "How I cut our API costs by 40% with a simple dashboard",
      "body": "...",
      "cta_subtle": "Happy to share the spreadsheet template I used...",
      "estimated_engagement": "medium-high"
    },
    ...
  ]
}
```

---

## Link Tracking

```
POST /api/v1/tracking/links
{
  "destination_url": "https://myapp.com",
  "campaign_id": "camp_123",
  "source": "reddit",
  "medium": "organic",
  "content": "r_saas_api_costs"
}

Response:
{
  "tracked_url": "https://aos.link/a1b2c3",
  "utm_url": "https://myapp.com?utm_source=reddit&utm_medium=organic&...",
  "tracking_pixel": "<script>...</script>"  // optional embed
}
```

---

## Feedback Analysis

```
POST /api/v1/feedback/analyze
{
  "text": "Your onboarding is confusing. I spent 20 minutes trying to connect my Stripe account.",
  "source": "twitter",
  "author": "@johndoe",
  "context": {}  // optional metadata
}

Response:
{
  "sentiment": "negative",
  "emotion": "frustrated",
  "category": "complaint",
  "subcategory": "onboarding",
  "urgency": "medium",
  "product_area": "integrations",
  "key_phrases": ["onboarding confusing", "connect Stripe", "20 minutes"],
  "suggested_action": "Review Stripe integration onboarding flow",
  "churn_risk": 0.65
}
```

---

## CLI Commands

```bash
# Install
pip install -r requirements.txt

# === Audience Research ===

# Research where your audience hangs out
python -m app.cli research "An API cost tracker for dev teams that alerts on budget overruns"

# Research from a URL (scrapes the page)
python -m app.cli research --url https://myapp.com

# Quick mode (Reddit + HN only, faster)
python -m app.cli research "API cost tracker" --quick

# === Content Generation ===

# Generate posts for a discovered audience
python -m app.cli generate --audience aud_123 --platform reddit --subreddit "r/SaaS"

# Generate with specific style
python -m app.cli generate --audience aud_123 --style story

# === Tracking ===

# Create tracked link
python -m app.cli track https://myapp.com --source reddit --campaign launch-week

# View campaign stats
python -m app.cli stats --campaign camp_123

# === Feedback ===

# Start monitoring for a product
python -m app.cli monitor --product prod_123

# Analyze a specific piece of text
python -m app.cli analyze "Your onboarding is confusing and I almost gave up"

# View feedback dashboard (terminal UI)
python -m app.cli feedback --product prod_123

# === Insights ===

# Generate weekly report
python -m app.cli report --product prod_123

# Chat with AI about your data
python -m app.cli chat --product prod_123
> "What are people complaining about most?"

# === Admin ===

# Run background workers
python -m app.cli worker

# Sync all data sources
python -m app.cli sync --product prod_123
```
