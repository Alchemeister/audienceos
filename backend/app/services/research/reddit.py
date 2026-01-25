"""Reddit API client for audience research and mention monitoring."""

import logging
from typing import Any

import httpx

from app.core.config import Settings
from app.core.exceptions import ExternalAPIError, RateLimitError

logger = logging.getLogger(__name__)

REDDIT_API_URL = "https://oauth.reddit.com"
REDDIT_AUTH_URL = "https://www.reddit.com/api/v1/access_token"


class RedditClient:
    """
    Reddit API client for searching and monitoring.

    Uses Reddit's OAuth2 for authentication.
    """

    def __init__(self, settings: Settings):
        """
        Initialize the Reddit client.

        Args:
            settings: Application settings with Reddit credentials
        """
        self.client_id = settings.REDDIT_CLIENT_ID
        self.client_secret = settings.REDDIT_CLIENT_SECRET
        self.user_agent = settings.REDDIT_USER_AGENT
        self._access_token: str | None = None
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create authenticated HTTP client."""
        if self._client is None or self._client.is_closed:
            # Get access token if needed
            if not self._access_token:
                await self._authenticate()

            self._client = httpx.AsyncClient(
                base_url=REDDIT_API_URL,
                headers={
                    "Authorization": f"Bearer {self._access_token}",
                    "User-Agent": self.user_agent,
                },
                timeout=30.0,
            )
        return self._client

    async def _authenticate(self) -> None:
        """Authenticate with Reddit and get access token."""
        if not self.client_id or not self.client_secret:
            raise ExternalAPIError(
                message="Reddit API credentials not configured",
                service="reddit",
            )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                REDDIT_AUTH_URL,
                auth=(self.client_id, self.client_secret),
                data={"grant_type": "client_credentials"},
                headers={"User-Agent": self.user_agent},
            )

            if response.status_code != 200:
                raise ExternalAPIError(
                    message=f"Reddit authentication failed: {response.status_code}",
                    service="reddit",
                    status_code=response.status_code,
                )

            data = response.json()
            self._access_token = data["access_token"]

    async def search_subreddits(
        self,
        query: str,
        limit: int = 25,
    ) -> list[dict[str, Any]]:
        """
        Search for subreddits matching a query.

        Args:
            query: Search term
            limit: Maximum results to return

        Returns:
            List of subreddit data
        """
        client = await self._get_client()

        try:
            response = await client.get(
                "/subreddits/search",
                params={
                    "q": query,
                    "limit": limit,
                    "sort": "relevance",
                },
            )

            if response.status_code == 429:
                raise RateLimitError(service="reddit")

            if response.status_code != 200:
                raise ExternalAPIError(
                    message=f"Reddit API error: {response.status_code}",
                    service="reddit",
                    status_code=response.status_code,
                )

            data = response.json()
            subreddits = []

            for child in data.get("data", {}).get("children", []):
                sr = child.get("data", {})
                subreddits.append({
                    "name": sr.get("display_name_prefixed", ""),
                    "title": sr.get("title", ""),
                    "description": sr.get("public_description", ""),
                    "subscribers": sr.get("subscribers", 0),
                    "active_users": sr.get("accounts_active", 0),
                    "url": f"https://reddit.com{sr.get('url', '')}",
                    "over18": sr.get("over18", False),
                })

            return subreddits

        except httpx.HTTPError as e:
            logger.error(f"Reddit HTTP error: {e}")
            raise ExternalAPIError(
                message=str(e),
                service="reddit",
            )

    async def search_posts(
        self,
        subreddit: str,
        query: str,
        time_filter: str = "month",
        limit: int = 25,
    ) -> list[dict[str, Any]]:
        """
        Search for posts in a subreddit.

        Args:
            subreddit: Subreddit name (without r/)
            query: Search term
            time_filter: one of hour, day, week, month, year, all
            limit: Maximum results to return

        Returns:
            List of post data
        """
        client = await self._get_client()

        try:
            response = await client.get(
                f"/r/{subreddit}/search",
                params={
                    "q": query,
                    "restrict_sr": "true",
                    "sort": "relevance",
                    "t": time_filter,
                    "limit": limit,
                },
            )

            if response.status_code == 429:
                raise RateLimitError(service="reddit")

            if response.status_code != 200:
                raise ExternalAPIError(
                    message=f"Reddit API error: {response.status_code}",
                    service="reddit",
                    status_code=response.status_code,
                )

            data = response.json()
            posts = []

            for child in data.get("data", {}).get("children", []):
                post = child.get("data", {})
                posts.append({
                    "id": post.get("id"),
                    "title": post.get("title", ""),
                    "selftext": post.get("selftext", ""),
                    "author": post.get("author", ""),
                    "subreddit": post.get("subreddit_name_prefixed", ""),
                    "score": post.get("score", 0),
                    "num_comments": post.get("num_comments", 0),
                    "url": f"https://reddit.com{post.get('permalink', '')}",
                    "created_utc": post.get("created_utc"),
                })

            return posts

        except httpx.HTTPError as e:
            logger.error(f"Reddit HTTP error: {e}")
            raise ExternalAPIError(
                message=str(e),
                service="reddit",
            )

    async def get_subreddit_info(self, subreddit: str) -> dict[str, Any]:
        """
        Get information about a subreddit.

        Args:
            subreddit: Subreddit name (without r/)

        Returns:
            Subreddit information
        """
        client = await self._get_client()

        try:
            response = await client.get(f"/r/{subreddit}/about")

            if response.status_code == 429:
                raise RateLimitError(service="reddit")

            if response.status_code == 404:
                raise ExternalAPIError(
                    message=f"Subreddit not found: {subreddit}",
                    service="reddit",
                    status_code=404,
                )

            if response.status_code != 200:
                raise ExternalAPIError(
                    message=f"Reddit API error: {response.status_code}",
                    service="reddit",
                    status_code=response.status_code,
                )

            sr = response.json().get("data", {})
            return {
                "name": sr.get("display_name_prefixed", ""),
                "title": sr.get("title", ""),
                "description": sr.get("public_description", ""),
                "subscribers": sr.get("subscribers", 0),
                "active_users": sr.get("accounts_active", 0),
                "url": f"https://reddit.com{sr.get('url', '')}",
                "rules_url": f"https://reddit.com/r/{subreddit}/about/rules",
                "created_utc": sr.get("created_utc"),
            }

        except httpx.HTTPError as e:
            logger.error(f"Reddit HTTP error: {e}")
            raise ExternalAPIError(
                message=str(e),
                service="reddit",
            )

    async def get_subreddit_rules(self, subreddit: str) -> list[dict[str, Any]]:
        """
        Get the rules for a subreddit.

        Args:
            subreddit: Subreddit name (without r/)

        Returns:
            List of subreddit rules with descriptions
        """
        client = await self._get_client()

        try:
            response = await client.get(f"/r/{subreddit}/about/rules")

            if response.status_code == 429:
                raise RateLimitError(service="reddit")

            if response.status_code == 404:
                # Some subreddits don't have rules defined
                return []

            if response.status_code != 200:
                raise ExternalAPIError(
                    message=f"Reddit API error: {response.status_code}",
                    service="reddit",
                    status_code=response.status_code,
                )

            data = response.json()
            rules = []

            for rule in data.get("rules", []):
                rules.append({
                    "short_name": rule.get("short_name", ""),
                    "description": rule.get("description", ""),
                    "kind": rule.get("kind", "all"),  # "link", "comment", or "all"
                    "violation_reason": rule.get("violation_reason", ""),
                })

            return rules

        except httpx.HTTPError as e:
            logger.error(f"Reddit HTTP error fetching rules: {e}")
            # Don't fail content generation if rules can't be fetched
            return []

    async def get_subreddit_rules_text(self, subreddit: str) -> str:
        """
        Get subreddit rules as a formatted text string for AI prompts.

        Args:
            subreddit: Subreddit name (without r/)

        Returns:
            Formatted rules text or message if no rules found
        """
        rules = await self.get_subreddit_rules(subreddit)

        if not rules:
            return "No specific rules found for this subreddit. Follow general Reddit etiquette."

        formatted = []
        for i, rule in enumerate(rules, 1):
            name = rule.get("short_name", f"Rule {i}")
            desc = rule.get("description", "")
            if desc:
                formatted.append(f"{i}. {name}: {desc}")
            else:
                formatted.append(f"{i}. {name}")

        return "\n".join(formatted)

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
