# AI Prompts

## Audience Research Prompt

```
You are an audience research expert. Given a product description, identify where the target audience spends time online.

PRODUCT DESCRIPTION:
{description}

Analyze this product and identify:

1. TARGET PERSONAS: Who would use this? (e.g., "indie SaaS founders", "DevOps engineers")

2. SUBREDDITS (Top 10): Rank by relevance. For each:
   - Name (e.g., r/SaaS)
   - Relevance score (0-1)
   - Why this subreddit fits
   - Sample topics/posts that would resonate

3. KEYWORDS: What terms does this audience search for?

4. COMPETITOR PRODUCTS: What else might they be using?

5. PAIN POINTS: What problems drive them to seek solutions?

Return as structured JSON matching this schema:
{schema}
```

---

## Keyword Discovery Prompt

```
You are a keyword research expert. Given a product, generate comprehensive keywords for monitoring mentions across social platforms.

PRODUCT NAME: {name}
PRODUCT DESCRIPTION: {description}
PRODUCT URL: {url}

Generate keywords in these categories:

1. BRAND VARIATIONS:
   - Exact name
   - Common misspellings
   - Abbreviations
   - With/without spaces

2. FOUNDER/TEAM (if detectable):
   - Names mentioned on the site
   - Twitter handles
   - "that thing [name] built"

3. COMPETITORS:
   - Direct competitors
   - "[product] alternative"
   - "[product] vs [competitor]"

4. PROBLEM PHRASES:
   - Questions people ask when they need this
   - Pain points described without naming a solution
   - "how do I [problem]"

5. SOLUTION PHRASES:
   - Category terms
   - Feature-specific terms
   - Industry jargon

Return as JSON with confidence scores for each keyword.
```

---

## Sentiment Analysis Prompt

```
Analyze this customer feedback for sentiment and actionability.

FEEDBACK TEXT:
"{text}"

SOURCE: {source}
PRODUCT CONTEXT: {product_description}

Analyze and return:
1. SENTIMENT: positive, negative, neutral, or mixed
2. EMOTION: frustrated, happy, confused, requesting, comparing, etc.
3. CATEGORY: bug, feature_request, praise, complaint, question, churn_risk
4. URGENCY: low, medium, high, critical
5. PRODUCT_AREA: which part of the product (if detectable)
6. KEY_PHRASES: important quotes/phrases
7. CHURN_RISK: 0-1 probability this user might leave
8. SUGGESTED_ACTION: one concrete thing the team could do

Return as structured JSON.
```

---

## Content Generation Prompt

```
Generate a Reddit post for the following context. The post should be HELPFUL and NON-PROMOTIONAL. Do not mention the product directly. Instead, share insights, solve problems, or spark discussion.

TARGET SUBREDDIT: {subreddit}
SUBREDDIT RULES: {rules}
SUBREDDIT CULTURE: {culture_notes}
TOPIC AREA: {topic}
PRODUCT CONTEXT (for your understanding, don't mention): {product}

Generate 3 post variations:
1. HELPFUL: Share a tip, insight, or solution
2. STORY: Share a relatable experience or lesson learned
3. QUESTION: Ask a thought-provoking question that sparks discussion

For each post include:
- Title (compelling, follows subreddit norms)
- Body (appropriate length for subreddit)
- Subtle CTA (optional - only if natural, like "happy to share my approach")

The goal is genuine engagement, not promotion. Posts that feel like ads get removed and damage reputation.

Return as structured JSON.
```

---

## Relevance Filtering Prompt (Cheap Model)

```
Determine if this post/comment mentions or is relevant to the product.

PRODUCT: {product_name}
KEYWORDS: {keywords}
TEXT: "{text}"

Return JSON:
{
  "is_relevant": true/false,
  "confidence": 0-1,
  "matched_keywords": ["keyword1", "keyword2"],
  "reason": "brief explanation"
}

Be inclusive - if there's reasonable chance it's relevant, mark true.
```

---

## Basic Classification Prompt (Cheap Model)

```
Classify this feedback into a category.

TEXT: "{text}"

Categories:
- bug: Something is broken
- feature_request: Asking for new functionality
- complaint: Expressing frustration
- praise: Positive feedback
- question: Asking for help
- churn_risk: Considering leaving/switching
- competitor_mention: Mentioning a competitor

Return JSON:
{
  "category": "category_name",
  "confidence": 0-1
}
```

---

## Weekly Report Prompt

```
Generate a weekly report for this product based on the collected data.

PRODUCT: {product_name}
TIME PERIOD: {start_date} to {end_date}

MARKETING DATA:
{marketing_stats}

FEEDBACK DATA:
{feedback_summary}

MENTION DATA:
{mention_stats}

Generate a report with:

1. EXECUTIVE SUMMARY (2-3 sentences)

2. MARKETING PERFORMANCE
   - Key metrics
   - Best/worst performing content
   - Conversion insights

3. AUDIENCE SENTIMENT
   - Overall trend
   - Top complaints (with counts)
   - Top praise (with counts)
   - Notable changes from last week

4. RECOMMENDED ACTIONS (prioritized)
   - High priority items
   - Opportunities spotted
   - Risks to address

5. NEXT WEEK FOCUS
   - Suggested topics/subreddits
   - Trending conversations to join

Write in a direct, actionable style. No fluff.
```

---

## Deep Analysis: Churn Risk Prompt

```
Analyze churn risk signals for this product.

PRODUCT: {product_name}

NEGATIVE FEEDBACK (last 30 days):
{negative_feedback}

SUPPORT TICKETS:
{support_data}

COMPETITOR MENTIONS:
{competitor_mentions}

USER BEHAVIOR (if available):
{behavior_data}

Identify:

1. HIGH-RISK USERS
   - Who is showing churn signals?
   - What specific signals?
   - Confidence level

2. COMMON CHURN TRIGGERS
   - What issues are pushing people away?
   - Frequency of each trigger

3. COMPETITIVE THREATS
   - Which competitors are being considered?
   - What's attracting users to them?

4. RECOMMENDED INTERVENTIONS
   - Specific actions to reduce churn
   - Priority order
   - Expected impact

Be specific. Name names. Provide evidence.
```
