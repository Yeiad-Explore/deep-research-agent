"""
General Web Scraper for extracting content from webpages
"""
import httpx
import logging
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re

logger = logging.getLogger(__name__)


class WebScraper:
    """
    General purpose web scraper for extracting main content from webpages
    """

    def __init__(self, timeout: int = 10, max_content_length: int = 50000):
        """
        Initialize web scraper

        Args:
            timeout: Request timeout in seconds
            max_content_length: Maximum content length to extract
        """
        self.timeout = timeout
        self.max_content_length = max_content_length
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    async def scrape_url(self, url: str) -> Dict[str, Any]:
        """
        Scrape content from a URL

        Args:
            url: URL to scrape

        Returns:
            Dictionary with scraped content and metadata
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()

                # Check content type
                content_type = response.headers.get("content-type", "")
                if "text/html" not in content_type:
                    logger.warning(f"Non-HTML content type for {url}: {content_type}")
                    return self._empty_result(url, "Non-HTML content")

                # Parse HTML
                soup = BeautifulSoup(response.text, "lxml")

                # Extract metadata
                title = self._extract_title(soup)
                author = self._extract_author(soup)
                published_date = self._extract_date(soup)
                domain = urlparse(url).netloc

                # Extract main content
                main_content = self._extract_main_content(soup)

                # Clean and truncate content
                cleaned_content = self._clean_text(main_content)
                if len(cleaned_content) > self.max_content_length:
                    cleaned_content = cleaned_content[:self.max_content_length] + "..."

                result = {
                    "url": url,
                    "title": title,
                    "author": author,
                    "published_date": published_date,
                    "domain": domain,
                    "content": cleaned_content,
                    "content_length": len(cleaned_content),
                    "success": True,
                    "error": None
                }

                logger.info(f"Successfully scraped: {url} ({len(cleaned_content)} chars)")
                return result

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error scraping {url}: {e.response.status_code}")
            return self._empty_result(url, f"HTTP {e.response.status_code}")

        except httpx.TimeoutException:
            logger.error(f"Timeout scraping {url}")
            return self._empty_result(url, "Timeout")

        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return self._empty_result(url, str(e))

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        # Try og:title first
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"]

        # Try title tag
        title_tag = soup.find("title")
        if title_tag:
            return title_tag.get_text().strip()

        # Try h1
        h1 = soup.find("h1")
        if h1:
            return h1.get_text().strip()

        return "Unknown Title"

    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract author name"""
        # Try meta author tag
        author_meta = soup.find("meta", attrs={"name": "author"})
        if author_meta and author_meta.get("content"):
            return author_meta["content"]

        # Try article:author
        article_author = soup.find("meta", property="article:author")
        if article_author and article_author.get("content"):
            return article_author["content"]

        return None

    def _extract_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract publication date"""
        # Try article:published_time
        published_time = soup.find("meta", property="article:published_time")
        if published_time and published_time.get("content"):
            return published_time["content"]

        # Try datePublished schema.org
        date_published = soup.find("meta", attrs={"itemprop": "datePublished"})
        if date_published and date_published.get("content"):
            return date_published["content"]

        # Try time tag
        time_tag = soup.find("time")
        if time_tag and time_tag.get("datetime"):
            return time_tag["datetime"]

        return None

    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from page"""
        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "header", "footer", "aside", "iframe", "noscript"]):
            element.decompose()

        # Try to find main content area
        content_candidates = [
            soup.find("article"),
            soup.find("main"),
            soup.find("div", class_=re.compile(r"(content|article|post|entry)", re.I)),
            soup.find("div", id=re.compile(r"(content|article|post|entry)", re.I)),
        ]

        for candidate in content_candidates:
            if candidate:
                text = candidate.get_text(separator="\n", strip=True)
                if len(text) > 200:  # Ensure it has substantial content
                    return text

        # Fallback to body
        body = soup.find("body")
        if body:
            return body.get_text(separator="\n", strip=True)

        return soup.get_text(separator="\n", strip=True)

    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove extra whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)

        # Remove common boilerplate patterns
        text = re.sub(r'(Accept|Reject) Cookies.*?\n', '', text, flags=re.I)
        text = re.sub(r'Subscribe to.*?newsletter.*?\n', '', text, flags=re.I)

        return text.strip()

    def _empty_result(self, url: str, error: str) -> Dict[str, Any]:
        """Return empty result with error"""
        return {
            "url": url,
            "title": "",
            "author": None,
            "published_date": None,
            "domain": urlparse(url).netloc,
            "content": "",
            "content_length": 0,
            "success": False,
            "error": error
        }

    async def scrape_multiple(self, urls: list[str]) -> list[Dict[str, Any]]:
        """
        Scrape multiple URLs concurrently

        Args:
            urls: List of URLs to scrape

        Returns:
            List of scrape results
        """
        import asyncio

        tasks = [self.scrape_url(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        formatted_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                formatted_results.append(self._empty_result(urls[i], str(result)))
            else:
                formatted_results.append(result)

        return formatted_results
