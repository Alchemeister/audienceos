"""AI prompt templates for AudienceOS."""

PROMPTS = {
    # =========================================================================
    # CHEAP MODEL PROMPTS (DeepSeek, Haiku)
    # Used for high-volume, simple tasks
    # =========================================================================
    "relevance_filter": """Determine if this post/comment mentions or is relevant to the product.

PRODUCT: {product_name}
KEYWORDS: {keywords}
TEXT: "{text}"

Return JSON:
{{
  "is_relevant": true/false,
  "confidence": 0-1,
  "matched_keywords": ["keyword1", "keyword2"],
  "reason": "brief explanation"
}}

Be inclusive - if there's reasonable chance it's relevant, mark true.""",
    "basic_classify": """Classify this feedback into a category.

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
{{
  "category": "category_name",
  "confidence": 0-1
}}""",
    "bulk_feedback_analysis": """Analyze this customer feedback efficiently.

TEXT: "{text}"

PRODUCT CONTEXT: {product_description}

Return JSON with:
{{
  "sentiment": "positive/negative/neutral/mixed",
  "category": "bug/feature_request/praise/complaint/question/churn_risk/competitor_mention",
  "urgency": "low/medium/high/critical",
  "churn_risk": 0.0-1.0,
  "key_phrases": ["phrase1", "phrase2"],
  "product_area": "string or null"
}}

Be concise. Focus on accuracy over detail.""",
    # =========================================================================
    # EXPENSIVE MODEL PROMPTS (Claude Sonnet/Opus)
    # Used for complex reasoning, nuanced analysis, content generation
    # =========================================================================
    "sentiment_analysis": """Analyze this customer feedback for sentiment and actionability.

FEEDBACK TEXT:
"{text}"

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

Return as JSON:
{{
  "sentiment": "string",
  "emotion": "string",
  "category": "string",
  "urgency": "string",
  "product_area": "string or null",
  "key_phrases": ["phrase1", "phrase2"],
  "churn_risk": 0.0,
  "suggested_action": "string"
}}""",
    "keyword_discovery": """You are a keyword research expert. Given a product, generate comprehensive keywords for monitoring mentions across social platforms.

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

Return as JSON:
{{
  "brand_variations": [{{"keyword": "string", "confidence": 0.0}}],
  "founder_team": [{{"keyword": "string", "confidence": 0.0}}],
  "competitors": [{{"keyword": "string", "confidence": 0.0}}],
  "problem_phrases": [{{"keyword": "string", "confidence": 0.0}}],
  "solution_phrases": [{{"keyword": "string", "confidence": 0.0}}]
}}""",
    "audience_research": """You are an audience research expert. Given a product description, identify where the target audience spends time online.

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

Return as JSON:
{{
  "personas": ["persona1", "persona2"],
  "subreddits": [
    {{
      "name": "r/SaaS",
      "relevance_score": 0.95,
      "reasoning": "why this fits",
      "sample_topics": ["topic1", "topic2"]
    }}
  ],
  "keywords": ["keyword1", "keyword2"],
  "competitors": ["competitor1", "competitor2"],
  "pain_points": ["pain1", "pain2"]
}}""",
    "content_generation": """Generate a Reddit post for the following context. The post should be HELPFUL and NON-PROMOTIONAL. Do not mention the product directly. Instead, share insights, solve problems, or spark discussion.

TARGET SUBREDDIT: {subreddit}
SUBREDDIT RULES: {rules}
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

Return as JSON:
{{
  "posts": [
    {{
      "style": "helpful",
      "title": "string",
      "body": "string",
      "cta_subtle": "string or null",
      "estimated_engagement": "low/medium/high"
    }}
  ]
}}""",
    "weekly_report": """Generate a weekly report for this product based on the collected data.

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

Return as JSON:
{{
  "executive_summary": "string",
  "marketing_performance": {{
    "key_metrics": {{}},
    "best_content": "string",
    "worst_content": "string",
    "conversion_insights": "string"
  }},
  "sentiment": {{
    "trend": "improving/declining/stable",
    "top_complaints": [{{"issue": "string", "count": 0}}],
    "top_praise": [{{"topic": "string", "count": 0}}],
    "notable_changes": "string"
  }},
  "recommended_actions": [
    {{"priority": "high/medium/low", "action": "string", "reason": "string"}}
  ],
  "next_week_focus": {{
    "topics": ["string"],
    "subreddits": ["string"],
    "trending": "string"
  }}
}}""",
    # =========================================================================
    # THEME CLUSTERING (EXPENSIVE)
    # Used for grouping feedback into actionable themes
    # =========================================================================
    "theme_clustering": """You are an expert at analyzing customer feedback and identifying patterns.

PRODUCT: {product_name}
PRODUCT DESCRIPTION: {product_description}

FEEDBACK ITEMS (total: {feedback_count}):
{feedback_items}

Analyze all feedback and cluster into 3-7 distinct themes. Each theme should represent a meaningful pattern that the product team can act on.

For each theme, identify:
1. A clear, actionable name (e.g., "Onboarding Friction", "API Performance Issues")
2. A description explaining the theme and why it matters
3. The urgency level based on sentiment and frequency
4. Key phrases/keywords that define this theme
5. Overall sentiment breakdown

Return as JSON:
{{
  "themes": [
    {{
      "name": "Theme Name",
      "description": "What this theme is about and why it matters",
      "feedback_indices": [0, 2, 5],
      "urgency": "low/medium/high/critical",
      "keywords": ["keyword1", "keyword2"],
      "sentiment_breakdown": {{
        "positive": 0,
        "negative": 5,
        "neutral": 2,
        "mixed": 1
      }}
    }}
  ],
  "unclustered_indices": [],
  "summary": "Brief overall summary of the feedback landscape"
}}

Guidelines:
- Themes should be specific and actionable, not generic
- Don't create themes with fewer than 2 feedback items
- Urgency is based on: negative sentiment + frequency + churn_risk signals
- Keywords should help identify similar future feedback""",
    # =========================================================================
    # DEEP ANALYSIS PROMPTS (EXPENSIVE - Pro+ only)
    # Agent-based analysis that spends more compute for thorough analysis
    # =========================================================================
    "deep_analysis_churn": """You are a churn analysis expert. Perform a deep analysis of churn signals in the feedback.

PRODUCT: {product_name}
PRODUCT DESCRIPTION: {product_description}

HIGH-RISK FEEDBACK (churn_risk > 0.5):
{high_risk_feedback}

ALL NEGATIVE FEEDBACK:
{negative_feedback}

COMPETITOR MENTIONS:
{competitor_mentions}

Perform a comprehensive churn analysis:

1. CHURN RISK ASSESSMENT
   - Overall churn risk level for the product
   - Key drivers of churn
   - User segments most at risk

2. PATTERN ANALYSIS
   - Common complaints leading to churn signals
   - Feature gaps mentioned
   - Competitor advantages cited

3. EARLY WARNING SIGNS
   - Phrases/patterns that predict churn
   - User behaviors to monitor
   - Timeline patterns (how long before users churn)

4. RETENTION OPPORTUNITIES
   - Quick wins to address
   - High-impact improvements
   - Communication strategies

5. COMPETITIVE POSITIONING
   - Where competitors are winning
   - Differentiation opportunities
   - Win-back strategies

Return as JSON:
{{
  "summary": "Executive summary of churn analysis",
  "risk_level": "low/medium/high/critical",
  "risk_score": 0.0,
  "key_drivers": [
    {{"driver": "string", "impact": "high/medium/low", "frequency": 0}}
  ],
  "at_risk_segments": [
    {{"segment": "string", "risk_level": "string", "count": 0}}
  ],
  "early_warning_signs": ["string"],
  "retention_opportunities": [
    {{"opportunity": "string", "impact": "string", "effort": "string"}}
  ],
  "competitive_gaps": [
    {{"competitor": "string", "advantage": "string", "response": "string"}}
  ],
  "recommendations": [
    {{"priority": "high/medium/low", "action": "string", "expected_impact": "string"}}
  ]
}}""",
    "deep_analysis_competitor": """You are a competitive intelligence expert. Analyze competitor mentions and market positioning.

PRODUCT: {product_name}
PRODUCT DESCRIPTION: {product_description}

COMPETITOR MENTIONS IN FEEDBACK:
{competitor_feedback}

COMPARISON REQUESTS:
{comparison_requests}

FEATURE REQUESTS MENTIONING COMPETITORS:
{competitor_feature_requests}

Perform comprehensive competitive intelligence:

1. COMPETITOR LANDSCAPE
   - Who are the main competitors mentioned
   - How often each is mentioned
   - Context of mentions (positive/negative/neutral)

2. COMPETITIVE POSITIONING
   - Where your product wins
   - Where competitors win
   - Perception gaps

3. FEATURE GAP ANALYSIS
   - Features users want that competitors have
   - Unique features users love
   - Parity features needed

4. MARKET OPPORTUNITIES
   - Underserved segments
   - Differentiation opportunities
   - Potential partnerships

5. STRATEGIC RECOMMENDATIONS
   - Positioning adjustments
   - Feature prioritization
   - Marketing messages

Return as JSON:
{{
  "summary": "Executive summary of competitive landscape",
  "competitors": [
    {{
      "name": "string",
      "mention_count": 0,
      "sentiment": "positive/negative/neutral/mixed",
      "strengths": ["string"],
      "weaknesses": ["string"]
    }}
  ],
  "your_strengths": ["string"],
  "your_weaknesses": ["string"],
  "feature_gaps": [
    {{"feature": "string", "competitor": "string", "user_demand": "high/medium/low"}}
  ],
  "opportunities": [
    {{"opportunity": "string", "segment": "string", "potential": "string"}}
  ],
  "recommendations": [
    {{"priority": "high/medium/low", "action": "string", "rationale": "string"}}
  ]
}}""",
    "deep_analysis_content": """You are a content strategy expert. Analyze feedback to develop a content strategy.

PRODUCT: {product_name}
PRODUCT DESCRIPTION: {product_description}

AUDIENCE SOURCES (where users hang out):
{audience_sources}

TOP PERFORMING CONTENT:
{top_content}

QUESTIONS USERS ASK:
{user_questions}

PAIN POINTS FROM FEEDBACK:
{pain_points}

PRAISE FROM FEEDBACK:
{praise_feedback}

Develop a comprehensive content strategy:

1. CONTENT THEMES
   - Topics that resonate with the audience
   - Pain points to address
   - Success stories to highlight

2. CHANNEL STRATEGY
   - Best platforms for each content type
   - Posting frequency recommendations
   - Community engagement tactics

3. CONTENT CALENDAR SUGGESTIONS
   - Weekly themes
   - Seasonal opportunities
   - Trending topics to leverage

4. CONTENT TYPES
   - Educational content opportunities
   - Story-based content ideas
   - Thought leadership angles

5. ENGAGEMENT OPTIMIZATION
   - Best performing formats
   - Call-to-action strategies
   - Community building tactics

Return as JSON:
{{
  "summary": "Executive summary of content strategy",
  "content_themes": [
    {{
      "theme": "string",
      "rationale": "string",
      "content_ideas": ["string"],
      "priority": "high/medium/low"
    }}
  ],
  "channel_recommendations": [
    {{
      "channel": "string",
      "content_types": ["string"],
      "frequency": "string",
      "engagement_tactics": ["string"]
    }}
  ],
  "calendar_suggestions": [
    {{
      "week": 1,
      "theme": "string",
      "content_pieces": ["string"]
    }}
  ],
  "content_formats": [
    {{"format": "string", "effectiveness": "string", "examples": ["string"]}}
  ],
  "recommendations": [
    {{"priority": "high/medium/low", "action": "string", "expected_impact": "string"}}
  ]
}}""",
    # =========================================================================
    # INSIGHT GENERATION (EXPENSIVE)
    # Generate actionable insights from analysis
    # =========================================================================
    "generate_insights": """Based on the analysis, generate specific actionable insights.

PRODUCT: {product_name}
ANALYSIS TYPE: {analysis_type}
ANALYSIS RESULTS: {analysis_results}

Generate 3-5 specific, actionable insights. Each insight should:
- Have a clear, attention-grabbing title
- Describe what was found and why it matters
- Suggest a concrete action to take
- Include supporting evidence

Return as JSON:
{{
  "insights": [
    {{
      "type": "marketing_opportunity/churn_risk/feature_demand/competitor_insight/sentiment_shift/trending_topic/action_required",
      "title": "Clear, specific title",
      "description": "What this insight means and why it matters",
      "priority": "low/medium/high/critical",
      "suggested_action": "Specific action to take",
      "evidence": ["Supporting data point 1", "Supporting data point 2"],
      "confidence": 0.8
    }}
  ]
}}""",
}


def get_prompt(name: str, **kwargs) -> str:
    """
    Get a prompt template and fill in variables.

    Args:
        name: Name of the prompt template
        **kwargs: Variables to substitute into the template

    Returns:
        The formatted prompt string

    Raises:
        KeyError: If prompt name not found
    """
    if name not in PROMPTS:
        raise KeyError(f"Prompt '{name}' not found. Available: {list(PROMPTS.keys())}")

    return PROMPTS[name].format(**kwargs)
