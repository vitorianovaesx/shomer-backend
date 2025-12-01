"""URL content fetcher and extractor."""

import re
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup


class ContentFetcher:
    """Fetch and extract content from URLs."""

    def __init__(self, timeout: int = 30):
        """Initialize content fetcher."""
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout, follow_redirects=True)

    async def fetch(self, url: str) -> Dict:
        """Fetch content from URL and extract text, HTML, and images."""
        try:
            response = await self.client.get(url)
            response.raise_for_status()

            html_content = response.text
            soup = BeautifulSoup(html_content, "lxml")

            # Extract text (remove scripts, styles)
            for script in soup(["script", "style", "meta", "link"]):
                script.decompose()

            text_content = soup.get_text(separator="\n", strip=True)

            # Extract images
            images = []
            base_url = response.url
            for img in soup.find_all("img"):
                img_url = img.get("src") or img.get("data-src")
                if img_url:
                    absolute_url = urljoin(str(base_url), img_url)
                    images.append(absolute_url)

            return {
                "url": str(response.url),
                "html": html_content,
                "text": text_content,
                "images": images,
                "status_code": response.status_code,
                "content_type": response.headers.get("content-type", ""),
            }
        except Exception as e:
            raise Exception(f"Failed to fetch {url}: {str(e)}")

    async def fetch_image(self, url: str) -> bytes:
        """Fetch image content."""
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.content
        except Exception as e:
            raise Exception(f"Failed to fetch image {url}: {str(e)}")

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


