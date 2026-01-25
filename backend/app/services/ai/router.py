"""AI model router for tiered model selection."""

import logging
from enum import Enum
from typing import Any

from app.core.config import Settings
from app.services.ai.base import AIProvider
from app.services.ai.claude import ClaudeProvider
from app.services.ai.deepseek import DeepSeekProvider
from app.services.ai.openai import OpenAIProvider
from app.services.ai.prompts import get_prompt

logger = logging.getLogger(__name__)


class ModelTier(str, Enum):
    """Model tier for cost/quality tradeoff."""

    CHEAP = "cheap"  # GPT-4o-mini/DeepSeek - for filtering, classification, bulk processing
    EXPENSIVE = "expensive"  # Claude - for analysis, generation, nuanced tasks


class AIRouter:
    """
    Routes AI requests to appropriate model based on task tier.

    Cost optimization strategy:
    - CHEAP tier: High volume, simple tasks (filtering, classification, sentiment)
    - EXPENSIVE tier: Low volume, complex tasks (insights, generation, deep analysis)

    Provider priority:
    - CHEAP: GPT-4o-mini > DeepSeek > Claude Haiku
    - EXPENSIVE: Claude Sonnet
    """

    def __init__(self, settings: Settings):
        """
        Initialize the AI router with providers.

        Args:
            settings: Application settings with API keys
        """
        self.settings = settings

        # Initialize providers (lazy initialization)
        self._cheap: AIProvider | None = None
        self._expensive: AIProvider | None = None

    @property
    def cheap(self) -> AIProvider:
        """
        Get the cheap model provider.

        Priority: DeepSeek V3 > GPT-4o-mini > Claude Haiku

        DeepSeek is preferred because:
        - Better quality: 88.5% MMLU vs 82% for GPT-4o-mini
        - Cheaper with caching: $0.028/M vs $0.15/M input
        - Latency doesn't matter for background batch processing
        """
        if self._cheap is None:
            if self.settings.DEEPSEEK_API_KEY:
                logger.info("Using DeepSeek V3 for cheap tier")
                self._cheap = DeepSeekProvider(api_key=self.settings.DEEPSEEK_API_KEY)
            elif self.settings.OPENAI_API_KEY:
                logger.info("Using GPT-4o-mini for cheap tier (DeepSeek not configured)")
                self._cheap = OpenAIProvider(
                    api_key=self.settings.OPENAI_API_KEY,
                    model="gpt-4o-mini",
                )
            else:
                logger.warning("No cheap tier API key set, falling back to Claude Haiku")
                self._cheap = ClaudeProvider(
                    api_key=self.settings.ANTHROPIC_API_KEY,
                    model="claude-3-5-haiku-20241022",
                )
        return self._cheap

    @property
    def expensive(self) -> AIProvider:
        """Get the expensive model provider (Claude)."""
        if self._expensive is None:
            self._expensive = ClaudeProvider(api_key=self.settings.ANTHROPIC_API_KEY)
        return self._expensive

    def get_provider(self, tier: ModelTier) -> AIProvider:
        """
        Get the provider for the specified tier.

        Args:
            tier: The model tier to use

        Returns:
            The appropriate AI provider
        """
        return self.cheap if tier == ModelTier.CHEAP else self.expensive

    # =========================================================================
    # CHEAP TIER - High volume operations
    # =========================================================================

    async def filter_relevance(
        self,
        texts: list[str],
        product_name: str,
        keywords: list[str],
    ) -> list[dict[str, Any]]:
        """
        Filter texts for relevance to a product (CHEAP tier).

        Args:
            texts: List of texts to filter
            product_name: Name of the product
            keywords: Keywords to match against

        Returns:
            List of relevance results with is_relevant, confidence, matched_keywords
        """
        results = []
        for text in texts:
            prompt = get_prompt(
                "relevance_filter",
                product_name=product_name,
                keywords=", ".join(keywords),
                text=text,
            )
            result = await self.cheap.complete_json(prompt)
            results.append(result)
        return results

    async def classify_feedback(self, text: str) -> dict[str, Any]:
        """
        Classify feedback into a category (CHEAP tier).

        Args:
            text: The feedback text to classify

        Returns:
            Classification result with category and confidence
        """
        prompt = get_prompt("basic_classify", text=text)
        return await self.cheap.complete_json(prompt)

    async def analyze_feedback_bulk(
        self,
        text: str,
        product_description: str,
    ) -> dict[str, Any]:
        """
        Analyze feedback for sentiment, category, and basic signals (CHEAP tier).

        This is the PRIMARY method for processing feedback items.
        Uses cheap model for cost efficiency on bulk processing.

        Args:
            text: The text to analyze
            product_description: Context about the product

        Returns:
            Analysis result with sentiment, category, urgency, churn_risk
        """
        prompt = get_prompt(
            "bulk_feedback_analysis",
            text=text,
            product_description=product_description,
        )
        return await self.cheap.complete_json(prompt)

    # =========================================================================
    # EXPENSIVE TIER - Low volume, high-value operations
    # =========================================================================

    async def analyze_sentiment_deep(
        self,
        text: str,
        product_description: str,
    ) -> dict[str, Any]:
        """
        Perform DEEP nuanced sentiment analysis (EXPENSIVE tier).

        Only use this for flagged items requiring nuanced understanding,
        NOT for bulk processing. For bulk, use analyze_feedback_bulk().

        Args:
            text: The text to analyze
            product_description: Context about the product

        Returns:
            Detailed sentiment analysis result
        """
        prompt = get_prompt(
            "sentiment_analysis",
            text=text,
            product_description=product_description,
        )
        return await self.expensive.complete_json(prompt)

    async def discover_keywords(
        self,
        product_name: str,
        product_description: str,
        product_url: str | None = None,
    ) -> dict[str, Any]:
        """
        Discover keywords for monitoring (EXPENSIVE tier).

        Args:
            product_name: Name of the product
            product_description: Description of the product
            product_url: Optional URL of the product

        Returns:
            Keyword suggestions organized by category
        """
        prompt = get_prompt(
            "keyword_discovery",
            name=product_name,
            description=product_description,
            url=product_url or "Not provided",
        )
        return await self.expensive.complete_json(prompt)

    async def research_audience(
        self,
        product_description: str,
    ) -> dict[str, Any]:
        """
        Research where the target audience hangs out (EXPENSIVE tier).

        Args:
            product_description: Description of the product

        Returns:
            Audience research results with platforms, keywords, competitors
        """
        prompt = get_prompt(
            "audience_research",
            description=product_description,
        )
        return await self.expensive.complete_json(prompt)

    async def generate_content(
        self,
        subreddit: str,
        rules: str,
        topic: str,
        product_context: str,
    ) -> dict[str, Any]:
        """
        Generate content posts (EXPENSIVE tier).

        Args:
            subreddit: Target subreddit name
            rules: Subreddit rules
            topic: Topic to write about
            product_context: Context about the product (not mentioned directly)

        Returns:
            Generated posts in different styles
        """
        prompt = get_prompt(
            "content_generation",
            subreddit=subreddit,
            rules=rules,
            topic=topic,
            product=product_context,
        )
        return await self.expensive.complete_json(prompt)

    async def cluster_themes(
        self,
        product_name: str,
        product_description: str,
        feedback_items: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Cluster feedback into themes (EXPENSIVE tier).

        Args:
            product_name: Name of the product
            product_description: Description of the product
            feedback_items: List of feedback items to cluster

        Returns:
            Clustered themes with indices and metadata
        """
        # Format feedback items for the prompt
        formatted_items = "\n".join(
            f"[{i}] ({item.get('sentiment', 'unknown')}, churn_risk={item.get('churn_risk', 0):.2f}): {item.get('text', '')[:500]}"
            for i, item in enumerate(feedback_items)
        )

        prompt = get_prompt(
            "theme_clustering",
            product_name=product_name,
            product_description=product_description,
            feedback_count=len(feedback_items),
            feedback_items=formatted_items,
        )
        return await self.expensive.complete_json(prompt)

    async def generate_weekly_report(
        self,
        product_name: str,
        start_date: str,
        end_date: str,
        marketing_stats: str,
        feedback_summary: str,
        mention_stats: str,
    ) -> dict[str, Any]:
        """
        Generate a weekly report (EXPENSIVE tier).

        Args:
            product_name: Name of the product
            start_date: Start date of the reporting period
            end_date: End date of the reporting period
            marketing_stats: Formatted marketing statistics
            feedback_summary: Formatted feedback summary
            mention_stats: Formatted mention statistics

        Returns:
            Weekly report content
        """
        prompt = get_prompt(
            "weekly_report",
            product_name=product_name,
            start_date=start_date,
            end_date=end_date,
            marketing_stats=marketing_stats,
            feedback_summary=feedback_summary,
            mention_stats=mention_stats,
        )
        return await self.expensive.complete_json(prompt)

    async def deep_analysis_churn(
        self,
        product_name: str,
        product_description: str,
        high_risk_feedback: str,
        negative_feedback: str,
        competitor_mentions: str,
    ) -> dict[str, Any]:
        """
        Perform deep churn analysis (EXPENSIVE tier - Pro+).

        Args:
            product_name: Name of the product
            product_description: Description of the product
            high_risk_feedback: Formatted high churn risk feedback
            negative_feedback: Formatted negative feedback
            competitor_mentions: Formatted competitor mentions

        Returns:
            Comprehensive churn analysis results
        """
        prompt = get_prompt(
            "deep_analysis_churn",
            product_name=product_name,
            product_description=product_description,
            high_risk_feedback=high_risk_feedback,
            negative_feedback=negative_feedback,
            competitor_mentions=competitor_mentions,
        )
        return await self.expensive.complete_json(prompt, max_tokens=4000)

    async def deep_analysis_competitor(
        self,
        product_name: str,
        product_description: str,
        competitor_feedback: str,
        comparison_requests: str,
        competitor_feature_requests: str,
    ) -> dict[str, Any]:
        """
        Perform deep competitor analysis (EXPENSIVE tier - Pro+).

        Args:
            product_name: Name of the product
            product_description: Description of the product
            competitor_feedback: Formatted feedback mentioning competitors
            comparison_requests: Formatted comparison requests
            competitor_feature_requests: Formatted feature requests mentioning competitors

        Returns:
            Comprehensive competitor intelligence
        """
        prompt = get_prompt(
            "deep_analysis_competitor",
            product_name=product_name,
            product_description=product_description,
            competitor_feedback=competitor_feedback,
            comparison_requests=comparison_requests,
            competitor_feature_requests=competitor_feature_requests,
        )
        return await self.expensive.complete_json(prompt, max_tokens=4000)

    async def deep_analysis_content(
        self,
        product_name: str,
        product_description: str,
        audience_sources: str,
        top_content: str,
        user_questions: str,
        pain_points: str,
        praise_feedback: str,
    ) -> dict[str, Any]:
        """
        Perform deep content strategy analysis (EXPENSIVE tier - Pro+).

        Args:
            product_name: Name of the product
            product_description: Description of the product
            audience_sources: Formatted audience sources
            top_content: Formatted top performing content
            user_questions: Formatted user questions
            pain_points: Formatted pain points
            praise_feedback: Formatted praise feedback

        Returns:
            Comprehensive content strategy recommendations
        """
        prompt = get_prompt(
            "deep_analysis_content",
            product_name=product_name,
            product_description=product_description,
            audience_sources=audience_sources,
            top_content=top_content,
            user_questions=user_questions,
            pain_points=pain_points,
            praise_feedback=praise_feedback,
        )
        return await self.expensive.complete_json(prompt, max_tokens=4000)

    async def generate_insights(
        self,
        product_name: str,
        analysis_type: str,
        analysis_results: str,
    ) -> dict[str, Any]:
        """
        Generate actionable insights from analysis (EXPENSIVE tier).

        Args:
            product_name: Name of the product
            analysis_type: Type of analysis performed
            analysis_results: Formatted analysis results

        Returns:
            Generated insights with actions and evidence
        """
        prompt = get_prompt(
            "generate_insights",
            product_name=product_name,
            analysis_type=analysis_type,
            analysis_results=analysis_results,
        )
        return await self.expensive.complete_json(prompt)

    # =========================================================================
    # DEPRECATED - Use analyze_feedback_bulk() instead
    # =========================================================================

    async def analyze_sentiment(
        self,
        text: str,
        product_description: str,
    ) -> dict[str, Any]:
        """
        DEPRECATED: Use analyze_feedback_bulk() for bulk processing.

        This method uses the EXPENSIVE tier and should only be used for
        special cases requiring deep analysis. For normal feedback processing,
        use analyze_feedback_bulk() which uses the cheap tier.
        """
        logger.warning(
            "analyze_sentiment() uses expensive tier - consider analyze_feedback_bulk() for bulk processing"
        )
        return await self.analyze_sentiment_deep(text, product_description)
