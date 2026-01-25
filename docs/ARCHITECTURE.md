# Architecture

## Tech Stack

| Component | Choice | Why |
|-----------|--------|-----|
| Language | Python 3.11+ | Type hints, async/await, fast prototyping |
| Web Framework | FastAPI | Async, automatic OpenAPI docs, modern |
| Frontend | Next.js 14 + shadcn/ui | Fast iteration, good DX, modern UI |
| Database | PostgreSQL + SQLite | Postgres for prod, SQLite for local dev |
| ORM | SQLAlchemy 2.0 | Async support, mature |
| Queue | Redis + Celery | Background jobs for data collection |
| AI | Anthropic Claude API | Analysis, content gen, sentiment |
| Auth | Clerk or NextAuth | Fast to implement, handles OAuth |
| Payments | Stripe | Industry standard |
| Deployment | Vercel (frontend) + Railway/Render (backend) | Simple, scalable |
| Validation | Pydantic v2 | Data models, API schemas |

## External APIs

| Service | Purpose | Auth Required |
|---------|---------|---------------|
| Reddit API | Subreddit search, post monitoring | Yes (OAuth) |
| Twitter/X API | Tweet monitoring, audience signals | Yes (Bearer token) |
| Anthropic Claude | AI analysis, content generation | Yes (API key) |
| DeepSeek | Cheap bulk processing | Yes (API key) |
| Google Trends (pytrends) | Interest over time | No (unofficial) |
| GitHub API | Repo/issue signals for dev tools | Optional (higher limits) |
| HN Algolia | Hacker News search | No |

---

## AI Architecture & Cost Optimization

Running AI analysis on thousands of mentions gets expensive fast. The solution is a tiered model approach.

### The Problem

If every mention goes through Claude/GPT-4 for analysis:
- 1000 mentions × $0.01/analysis = $10 per sync
- Multiple syncs per day × many users = thousands in AI costs
- Margins disappear quickly

### The Solution: Model Tiering

Use cheap/fast models for high-volume simple tasks, expensive/smart models for complex reasoning.

**Cheap Models (DeepSeek, Claude Haiku, GPT-4o-mini) for:**
- Initial relevance filtering ("Is this actually about the product?")
- Basic classification (bug / feature request / complaint / praise)
- Keyword extraction from raw text
- Spam and noise filtering
- Bulk processing of raw mentions

**Expensive Models (Claude Sonnet/Opus, GPT-4) for:**
- Nuanced sentiment analysis with context
- Pattern recognition across the entire feedback corpus
- Insight generation ("Here's what this all means")
- Content generation for marketing posts
- Agent-based deep analysis (Pro+ feature)

### The Flow

```
1000 raw mentions from Reddit/Twitter/etc
    ↓ Cheap model filters for relevance
150 actual product mentions
    ↓ Cheap model classifies + extracts key phrases
150 structured feedback items (stored in DB)
    ↓ Expensive model analyzes the batch
1 weekly insight report + actionable recommendations
```

You're paying Claude to analyze 150 structured items, not 1000 raw posts. 85%+ cost reduction.

### Agent-Based Deep Analysis (Pro+ Only)

Higher tiers get access to AI agents that spend more compute cycles on thorough analysis:

- **"Deep Churn Analysis"** - Agent cross-references negative feedback with user behavior patterns
- **"Competitor Intelligence Report"** - Agent researches what people say about competitors across platforms
- **"Content Strategy Recommendation"** - Agent analyzes what's working, why, and suggests next moves
- **"Weekly Executive Summary"** - Agent synthesizes everything into a board-ready report

These are high-value, infrequent tasks (weekly/monthly, not hourly). Cost per user stays reasonable.

**Credit system:** Pro gets 4 Deep Analysis credits/month. Agency gets unlimited.

### Cost Estimates Per Tier

| Tier | Monthly AI Cost/User | Margin |
|------|---------------------|--------|
| Indie ($39) | ~$2-5 | 85%+ |
| Pro ($99) | ~$10-20 | 80%+ |
| Agency ($299) | ~$30-50 | 85%+ |

The tiered model approach keeps AI costs at <20% of revenue even with heavy usage.

---

## Project Structure

```
/audienceos
  /backend
    /app
      /api
        /v1
          audiences.py      # Audience research endpoints
          feedback.py       # Feedback collection endpoints
          insights.py       # AI-generated insights
          campaigns.py      # Content + tracking
          webhooks.py       # Incoming feedback webhooks
      /core
        config.py           # Settings, env vars
        security.py         # Auth, API keys
        exceptions.py       # Custom exceptions
      /models
        user.py             # User, Organization, Subscription
        audience.py         # Audience, Source, Signal
        feedback.py         # Feedback, Mention, Sentiment
        campaign.py         # Campaign, Post, Conversion
        insight.py          # Insight, Report, Action
      /services
        /research
          reddit.py         # Reddit API integration
          twitter.py        # Twitter/X integration
          hackernews.py     # HN Algolia integration
          github.py         # GitHub signals
          trends.py         # Google Trends
        /feedback
          aggregator.py     # Multi-source aggregation
          sentiment.py      # Sentiment analysis
          categorizer.py    # Theme/topic clustering
        /ai
          claude.py         # Claude API wrapper
          deepseek.py       # DeepSeek for bulk processing
          router.py         # Model routing (cheap vs expensive)
          prompts.py        # Prompt templates
          analyzer.py       # Content analysis
          generator.py      # Content generation
        /tracking
          links.py          # UTM link generation
          conversions.py    # Conversion tracking
      /tasks
        research.py         # Background research jobs
        feedback.py         # Feedback collection jobs
        reports.py          # Weekly report generation
      /db
        base.py             # Database setup
        session.py          # Session management
      main.py               # FastAPI app entry
    /migrations             # Alembic migrations
    /tests
    requirements.txt
    Dockerfile
  /frontend
    /src
      /app
        /(dashboard)
          /audiences        # Audience research UI
          /feedback         # Feedback dashboard
          /campaigns        # Content + tracking
          /insights         # AI insights + reports
          /settings         # Account, billing, integrations
        /api                # API routes (Next.js)
      /components
        /ui                 # shadcn components
        /audiences          # Audience-specific components
        /feedback           # Feedback-specific components
        /charts             # Data visualization
      /lib
        api.ts              # Backend API client
        utils.ts            # Utilities
      /hooks                # Custom React hooks
    package.json
    tailwind.config.js
  /shared
    /schemas                # Shared Pydantic/Zod schemas
  /docs                     # Documentation (this folder)
  docker-compose.yml
  .env.example
  README.md
  CLAUDE.md
```

---

## Data Models

```python
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional

# === Enums ===

class Platform(str, Enum):
    REDDIT = "reddit"
    TWITTER = "twitter"
    HACKERNEWS = "hackernews"
    GITHUB = "github"
    EMAIL = "email"
    WIDGET = "widget"
    MANUAL = "manual"

class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"

class FeedbackCategory(str, Enum):
    BUG = "bug"
    FEATURE_REQUEST = "feature_request"
    PRAISE = "praise"
    COMPLAINT = "complaint"
    QUESTION = "question"
    CHURN_RISK = "churn_risk"
    COMPETITOR_MENTION = "competitor_mention"

class Urgency(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class PostStyle(str, Enum):
    HELPFUL = "helpful"
    STORY = "story"
    QUESTION = "question"
    INSIGHT = "insight"

class SubscriptionTier(str, Enum):
    INDIE = "indie"
    PRO = "pro"
    AGENCY = "agency"

# === Core Models ===

class User(BaseModel):
    id: str
    email: str
    name: str
    organization_id: str
    created_at: datetime

class Organization(BaseModel):
    id: str
    name: str
    subscription_tier: SubscriptionTier
    products: list[str]  # product IDs
    created_at: datetime

class Product(BaseModel):
    """A product/project being tracked"""
    id: str
    organization_id: str
    name: str
    description: str
    url: Optional[str]
    keywords: list[str]
    competitors: list[str]
    created_at: datetime

# === Audience Research ===

class AudienceSource(BaseModel):
    """A discovered audience location"""
    id: str
    product_id: str
    platform: Platform
    name: str  # e.g., "r/SaaS", "@indiehackers"
    url: str
    relevance_score: float = Field(ge=0, le=1)
    monthly_active: Optional[int]
    recent_relevant_posts: int
    reasoning: str
    discovered_at: datetime
    last_checked: datetime

class AudienceResearch(BaseModel):
    """Results of an audience research session"""
    id: str
    product_id: str
    sources: list[AudienceSource]
    keywords: list[str]
    competitors_mentioned: list[str]
    confidence: str  # low, medium, high
    created_at: datetime

# === Campaigns & Tracking ===

class GeneratedPost(BaseModel):
    """AI-generated post content"""
    id: str
    campaign_id: str
    platform: Platform
    target_community: str  # e.g., "r/SaaS"
    style: PostStyle
    title: Optional[str]
    body: str
    cta_subtle: Optional[str]
    created_at: datetime

class TrackedLink(BaseModel):
    """A trackable link for conversion attribution"""
    id: str
    campaign_id: str
    destination_url: str
    short_url: str
    utm_source: str
    utm_medium: str
    utm_campaign: str
    utm_content: Optional[str]
    clicks: int = 0
    conversions: int = 0
    created_at: datetime

class Campaign(BaseModel):
    """A marketing campaign (set of posts + tracking)"""
    id: str
    product_id: str
    name: str
    posts: list[GeneratedPost]
    links: list[TrackedLink]
    status: str  # draft, active, completed
    total_clicks: int = 0
    total_conversions: int = 0
    conversion_rate: float = 0
    created_at: datetime

# === Feedback ===

class FeedbackItem(BaseModel):
    """A single piece of feedback from any source"""
    id: str
    product_id: str
    source: Platform
    source_url: Optional[str]
    author: Optional[str]
    author_id: Optional[str]
    text: str
    sentiment: Sentiment
    emotion: Optional[str]
    category: FeedbackCategory
    subcategory: Optional[str]
    urgency: Urgency
    product_area: Optional[str]
    key_phrases: list[str]
    churn_risk: float = Field(ge=0, le=1, default=0)
    suggested_action: Optional[str]
    is_actioned: bool = False
    actioned_at: Optional[datetime]
    raw_data: dict  # Original API response
    created_at: datetime
    collected_at: datetime

class FeedbackTheme(BaseModel):
    """Auto-clustered theme from feedback"""
    id: str
    product_id: str
    name: str  # e.g., "Onboarding Issues"
    description: str
    feedback_count: int
    sentiment_breakdown: dict  # {"positive": 5, "negative": 12, ...}
    urgency: Urgency
    sample_feedback_ids: list[str]
    created_at: datetime
    updated_at: datetime

# === Insights ===

class Insight(BaseModel):
    """An AI-generated insight or recommendation"""
    id: str
    product_id: str
    type: str  # marketing_opportunity, churn_risk, feature_demand, etc.
    title: str
    description: str
    priority: Urgency
    evidence: list[str]  # IDs of supporting feedback/data
    suggested_action: str
    is_actioned: bool = False
    created_at: datetime

class WeeklyReport(BaseModel):
    """Automated weekly summary"""
    id: str
    product_id: str
    week_start: datetime
    week_end: datetime

    # Marketing metrics
    posts_published: int
    total_clicks: int
    total_conversions: int
    conversion_rate: float
    best_performing_post: Optional[str]

    # Feedback metrics
    new_mentions: int
    sentiment_score: float  # -1 to 1
    sentiment_change: float  # vs last week
    top_complaints: list[str]
    top_praise: list[str]

    # Recommendations
    insights: list[Insight]

    created_at: datetime
```
