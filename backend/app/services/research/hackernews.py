"""Hacker News API client using Algolia search (no auth required)."""

import logging
from datetime import datetime
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Algolia HN Search API
HN_ALGOLIA_URL = "https://hn.algolia.com/api/v1"


class HackerNewsClient:
    """
    Hacker News client using Algolia's free search API.

    Algolia provides a fast, free API for searching Hacker News content.
    No authentication required.

    Docs: https://hn.algolia.com/api
    """

    def __init__(self):
        """Initialize the Hacker News client."""
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=HN_ALGOLIA_URL,
                timeout=30.0,
                headers={"User-Agent": "AudienceOS/1.0"},
            )
        return self._client

    async def search(
        self,
        query: str,
        tags: str | None = None,
        num_results: int = 25,
        page: int = 0,
    ) -> list[dict[str, Any]]:
        """
        Search Hacker News using Algolia API.

        Args:
            query: Search query
            tags: Filter by tags (e.g., "story", "comment", "author_pg")
                  Use AND: "story,author_pg"
                  Use OR: "(story,comment)"
            num_results: Number of results per page (max 1000)
            page: Page number (0-indexed)

        Returns:
            List of search results (stories/comments)

        Example tags:
            - "story" - only stories
            - "comment" - only comments
            - "(story,comment)" - stories OR comments
            - "author_USERNAME" - posts by specific user
            - "story,author_pg" - stories by pg (AND)
        """
        client = await self._get_client()

        params = {
            "query": query,
            "hitsPerPage": min(num_results, 1000),
            "page": page,
        }

        if tags:
            params["tags"] = tags

        try:
            response = await client.get("/search", params=params)
            response.raise_for_status()

            data = response.json()
            hits = data.get("hits", [])

            # Normalize the response format
            results = []
            for hit in hits:
                result = {
                    "objectID": hit.get("objectID"),
                    "title": hit.get("title") or hit.get("story_title") or "",
                    "text": hit.get("comment_text") or hit.get("story_text") or "",
                    "url": hit.get("url") or hit.get("story_url"),
                    "author": hit.get("author"),
                    "by": hit.get("author"),  # Alias for consistency
                    "points": hit.get("points", 0),
                    "num_comments": hit.get("num_comments", 0),
                    "created_at": hit.get("created_at"),
                    "created_at_i": hit.get("created_at_i"),
                    "type": "story" if hit.get("title") else "comment",
                    "story_id": hit.get("story_id"),
                    "parent_id": hit.get("parent_id"),
                }

                # Build HN URL
                if result["objectID"]:
                    result["hn_url"] = f"https://news.ycombinator.com/item?id={result['objectID']}"

                results.append(result)

            return results

        except httpx.HTTPError as e:
            logger.error(f"HN Algolia API error: {e}")
            raise

    async def search_by_date(
        self,
        query: str,
        tags: str | None = None,
        num_results: int = 25,
        page: int = 0,
    ) -> list[dict[str, Any]]:
        """
        Search Hacker News sorted by date (most recent first).

        Same parameters as search(), but results are sorted by date
        instead of relevance.
        """
        client = await self._get_client()

        params = {
            "query": query,
            "hitsPerPage": min(num_results, 1000),
            "page": page,
        }

        if tags:
            params["tags"] = tags

        try:
            response = await client.get("/search_by_date", params=params)
            response.raise_for_status()

            data = response.json()
            hits = data.get("hits", [])

            results = []
            for hit in hits:
                result = {
                    "objectID": hit.get("objectID"),
                    "title": hit.get("title") or hit.get("story_title") or "",
                    "text": hit.get("comment_text") or hit.get("story_text") or "",
                    "url": hit.get("url") or hit.get("story_url"),
                    "author": hit.get("author"),
                    "by": hit.get("author"),
                    "points": hit.get("points", 0),
                    "num_comments": hit.get("num_comments", 0),
                    "created_at": hit.get("created_at"),
                    "created_at_i": hit.get("created_at_i"),
                    "type": "story" if hit.get("title") else "comment",
                    "story_id": hit.get("story_id"),
                    "parent_id": hit.get("parent_id"),
                }

                if result["objectID"]:
                    result["hn_url"] = f"https://news.ycombinator.com/item?id={result['objectID']}"

                results.append(result)

            return results

        except httpx.HTTPError as e:
            logger.error(f"HN Algolia API error: {e}")
            raise

    async def get_item(self, item_id: str | int) -> dict[str, Any] | None:
        """
        Get a specific item (story or comment) by ID.

        Args:
            item_id: The Hacker News item ID

        Returns:
            Item data or None if not found
        """
        client = await self._get_client()

        try:
            response = await client.get(f"/items/{item_id}")

            if response.status_code == 404:
                return None

            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"HN Algolia API error getting item {item_id}: {e}")
            return None

    async def get_user(self, username: str) -> dict[str, Any] | None:
        """
        Get user information.

        Args:
            username: The Hacker News username

        Returns:
            User data or None if not found
        """
        client = await self._get_client()

        try:
            response = await client.get(f"/users/{username}")

            if response.status_code == 404:
                return None

            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"HN Algolia API error getting user {username}: {e}")
            return None

    async def get_front_page(self, num_results: int = 30) -> list[dict[str, Any]]:
        """
        Get current front page stories.

        Args:
            num_results: Number of stories to return

        Returns:
            List of front page stories
        """
        # Search for stories with high points from the last day
        return await self.search(
            query="",
            tags="front_page",
            num_results=num_results,
        )

    async def search_stories(
        self,
        query: str,
        num_results: int = 25,
    ) -> list[dict[str, Any]]:
        """
        Search only stories (not comments).

        Args:
            query: Search query
            num_results: Number of results

        Returns:
            List of matching stories
        """
        return await self.search(
            query=query,
            tags="story",
            num_results=num_results,
        )

    async def search_comments(
        self,
        query: str,
        num_results: int = 25,
    ) -> list[dict[str, Any]]:
        """
        Search only comments (not stories).

        Args:
            query: Search query
            num_results: Number of results

        Returns:
            List of matching comments
        """
        return await self.search(
            query=query,
            tags="comment",
            num_results=num_results,
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
