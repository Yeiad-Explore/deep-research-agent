"""
YARS (Yet Another Reddit Scraper) Client
Reddit scraper using simple JSON requests - NO API KEYS REQUIRED
Based on YARS approach: uses requests module for Reddit's public JSON API
"""
import requests
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import time

logger = logging.getLogger(__name__)


class YARSRedditClient:
    """
    Reddit scraper using simple JSON requests (YARS approach)
    No Reddit API keys required - uses public JSON endpoints
    """

    def __init__(self, user_agent: str = "DeepResearchAgent/1.0", request_delay: float = 0.5):
        """
        Initialize YARS Reddit client

        Args:
            user_agent: User agent string
            request_delay: Delay between requests in seconds (default: 0.5)
        """
        self.headers = {
            "User-Agent": user_agent
        }
        self.base_url = "https://www.reddit.com"
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.request_delay = request_delay

    def _make_request(self, url: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make request to Reddit JSON API with error handling

        Args:
            url: URL to request
            params: Query parameters

        Returns:
            JSON response data or None
        """
        try:
            # Add .json to get JSON response
            if not url.endswith('.json'):
                url = url.rstrip('/') + '.json'

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            # Rate limiting - be respectful to Reddit
            time.sleep(self.request_delay)

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to {url}: {e}")
            return None

    def search_reddit(self, query: str, limit: int = 50, time_filter: str = "month") -> List[Dict[str, Any]]:
        """
        Search Reddit for posts using a keyword query

        Args:
            query: Search query
            limit: Maximum number of results
            time_filter: Time filter (hour/day/week/month/year/all)

        Returns:
            List of post dictionaries
        """
        try:
            url = f"{self.base_url}/search.json"
            params = {
                "q": query,
                "limit": min(limit, 100),
                "sort": "relevance",
                "t": time_filter
            }

            data = self._make_request(url, params)
            if not data:
                return []

            posts = []
            for child in data.get("data", {}).get("children", []):
                post_data = child.get("data", {})
                posts.append(self._format_post(post_data))

            logger.info(f"Found {len(posts)} posts for query: '{query}'")
            return posts

        except Exception as e:
            logger.error(f"Error searching Reddit: {e}")
            return []

    async def search_posts(
        self,
        query: str,
        subreddits: Optional[List[str]] = None,
        limit: int = 50,
        time_filter: str = "month"
    ) -> List[Dict[str, Any]]:
        """
        Search across Reddit posts (async wrapper for compatibility)

        Args:
            query: Search query
            subreddits: List of subreddits to search
            limit: Maximum number of posts
            time_filter: Time filter

        Returns:
            List of post dictionaries
        """
        if subreddits:
            # Search specific subreddits
            all_posts = []
            for subreddit in subreddits:
                posts = self.fetch_subreddit_posts(
                    subreddit,
                    limit=limit // len(subreddits),
                    category="search",
                    time_filter=time_filter,
                    search_query=query
                )
                all_posts.extend(posts)
            return all_posts
        else:
            return self.search_reddit(query, limit, time_filter)

    async def search_comments(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search comments (extracts from post comments)

        Args:
            query: Search query
            limit: Maximum comments

        Returns:
            List of comment dictionaries
        """
        posts = self.search_reddit(query, limit=10)
        all_comments = []

        for post in posts[:5]:  # Get comments from top 5 posts
            post_url = post.get("url", "")
            if post_url:
                thread_data = await self.get_post_with_comments(post_url, comment_limit=10)
                comments = thread_data.get("comments", [])
                all_comments.extend(comments[:limit // 5])

        return all_comments[:limit]

    def fetch_subreddit_posts(
        self,
        subreddit: str,
        limit: int = 25,
        category: str = "hot",
        time_filter: str = "week",
        search_query: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch posts from a specific subreddit

        Args:
            subreddit: Subreddit name (without r/)
            limit: Maximum posts
            category: Post category (hot/new/top/rising/controversial)
            time_filter: Time filter for top/controversial
            search_query: Optional search query within subreddit

        Returns:
            List of post dictionaries
        """
        try:
            if search_query:
                # Search within subreddit
                url = f"{self.base_url}/r/{subreddit}/search.json"
                params = {
                    "q": search_query,
                    "restrict_sr": "on",
                    "limit": min(limit, 100),
                    "sort": "relevance",
                    "t": time_filter
                }
            else:
                # Get posts by category
                url = f"{self.base_url}/r/{subreddit}/{category}.json"
                params = {
                    "limit": min(limit, 100),
                    "t": time_filter if category in ["top", "controversial"] else None
                }

            data = self._make_request(url, params)
            if not data:
                return []

            posts = []
            for child in data.get("data", {}).get("children", []):
                post_data = child.get("data", {})
                posts.append(self._format_post(post_data))

            logger.info(f"Fetched {len(posts)} posts from r/{subreddit}")
            return posts

        except Exception as e:
            logger.error(f"Error fetching subreddit posts: {e}")
            return []

    async def get_hot_discussions(self, subreddit: str, limit: int = 25) -> List[Dict[str, Any]]:
        """
        Get hot discussions from subreddit

        Args:
            subreddit: Subreddit name
            limit: Maximum posts

        Returns:
            List of post dictionaries
        """
        return self.fetch_subreddit_posts(subreddit, limit, category="hot")

    def scrape_post_details(self, permalink: str) -> Optional[Dict[str, Any]]:
        """
        Scrape details of a specific post

        Args:
            permalink: Post permalink (e.g., /r/subreddit/comments/id/title/)

        Returns:
            Post details or None
        """
        try:
            url = f"{self.base_url}{permalink}"
            data = self._make_request(url)

            if not data or len(data) < 2:
                return None

            # First element is the post, second is comments
            post_data = data[0].get("data", {}).get("children", [{}])[0].get("data", {})

            return self._format_post(post_data)

        except Exception as e:
            logger.error(f"Error scraping post details: {e}")
            return None

    async def get_post_with_comments(
        self,
        post_url: str,
        comment_limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get post with comments

        Args:
            post_url: Reddit post URL
            comment_limit: Maximum comments

        Returns:
            Dictionary with post and comments
        """
        try:
            # Extract permalink from URL
            if "reddit.com" in post_url:
                permalink = post_url.split("reddit.com")[1].split("?")[0]
            else:
                permalink = post_url

            url = f"{self.base_url}{permalink}"
            data = self._make_request(url)

            if not data or len(data) < 2:
                return {"post": {}, "comments": [], "total_comments": 0}

            # Parse post
            post_data = data[0].get("data", {}).get("children", [{}])[0].get("data", {})
            post = self._format_post(post_data)

            # Parse comments
            comments = []
            comment_data = data[1].get("data", {}).get("children", [])

            def extract_comments(comment_list, depth=0):
                """Recursively extract comments"""
                for item in comment_list:
                    if item.get("kind") == "t1":  # Comment
                        comment = item.get("data", {})
                        if comment.get("body"):
                            comments.append({
                                "body": comment.get("body", ""),
                                "score": comment.get("score", 0),
                                "author": comment.get("author", "[deleted]"),
                                "created_utc": datetime.fromtimestamp(
                                    comment.get("created_utc", 0)
                                ).isoformat(),
                                "is_submitter": comment.get("is_submitter", False)
                            })

                        # Get replies
                        replies = comment.get("replies")
                        if isinstance(replies, dict):
                            reply_children = replies.get("data", {}).get("children", [])
                            extract_comments(reply_children, depth + 1)

            extract_comments(comment_data)

            logger.info(f"Retrieved post with {len(comments)} comments")
            return {
                "post": post,
                "comments": comments[:comment_limit],
                "total_comments": len(comments)
            }

        except Exception as e:
            logger.error(f"Error getting post with comments: {e}")
            return {"post": {}, "comments": [], "total_comments": 0}

    async def get_subreddit_recommendations(
        self,
        topic: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find relevant subreddits for a topic

        Args:
            topic: Topic to search
            limit: Maximum subreddits

        Returns:
            List of subreddit information
        """
        try:
            url = f"{self.base_url}/subreddits/search.json"
            params = {
                "q": topic,
                "limit": limit
            }

            data = self._make_request(url, params)
            if not data:
                return []

            subreddits = []
            for child in data.get("data", {}).get("children", []):
                sub_data = child.get("data", {})
                subreddits.append({
                    "name": sub_data.get("display_name", ""),
                    "title": sub_data.get("title", ""),
                    "description": sub_data.get("public_description", ""),
                    "subscribers": sub_data.get("subscribers", 0),
                    "active_users": sub_data.get("active_user_count", 0),
                    "url": f"https://reddit.com/r/{sub_data.get('display_name', '')}"
                })

            logger.info(f"Found {len(subreddits)} subreddits for topic: '{topic}'")
            return sorted(subreddits, key=lambda x: x['subscribers'], reverse=True)

        except Exception as e:
            logger.error(f"Error finding subreddits: {e}")
            return []

    async def analyze_thread_sentiment(self, post_url: str) -> Dict[str, Any]:
        """
        Analyze sentiment of a thread

        Args:
            post_url: Reddit post URL

        Returns:
            Sentiment analysis
        """
        thread_data = await self.get_post_with_comments(post_url, comment_limit=50)
        comments = thread_data.get("comments", [])

        if not comments:
            return {"sentiment": "neutral", "confidence": 0.0}

        total_score = sum(c.get("score", 0) for c in comments)
        avg_score = total_score / len(comments) if comments else 0

        positive_count = sum(1 for c in comments if c.get("score", 0) > 5)
        negative_count = sum(1 for c in comments if c.get("score", 0) < 0)

        sentiment = "neutral"
        if avg_score > 10:
            sentiment = "positive"
        elif avg_score < -5:
            sentiment = "negative"

        return {
            "sentiment": sentiment,
            "average_score": avg_score,
            "positive_comments": positive_count,
            "negative_comments": negative_count,
            "total_comments": len(comments),
            "engagement_level": "high" if len(comments) > 30 else "medium" if len(comments) > 10 else "low"
        }

    def _format_post(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format Reddit post data into standardized dictionary

        Args:
            post_data: Raw post data from Reddit API

        Returns:
            Formatted post dictionary
        """
        return {
            "id": post_data.get("id", ""),
            "title": post_data.get("title", ""),
            "body": post_data.get("selftext", ""),
            "url": f"https://reddit.com{post_data.get('permalink', '')}" if post_data.get("permalink") else "",
            "external_url": post_data.get("url") if not post_data.get("is_self") else None,
            "score": post_data.get("score", 0),
            "upvote_ratio": post_data.get("upvote_ratio", 0.5),
            "num_comments": post_data.get("num_comments", 0),
            "author": post_data.get("author", "[deleted]"),
            "subreddit": post_data.get("subreddit", ""),
            "created_utc": datetime.fromtimestamp(
                post_data.get("created_utc", 0)
            ).isoformat() if post_data.get("created_utc") else "",
            "is_self": post_data.get("is_self", False),
            "link_flair_text": post_data.get("link_flair_text"),
            "thumbnail_url": post_data.get("thumbnail") if post_data.get("thumbnail") != "self" else None,
            "image_url": post_data.get("url") if post_data.get("post_hint") == "image" else None
        }

    async def close(self):
        """Close the session"""
        self.session.close()
