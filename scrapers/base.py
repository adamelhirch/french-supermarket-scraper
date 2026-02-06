"""Base scraper class for all supermarket scrapers."""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import asyncio
import logging
from datetime import datetime, timedelta
import hashlib
import json

logger = logging.getLogger(__name__)


class Product:
    """Product data model."""
    
    def __init__(
        self,
        name: str,
        price: float,
        unit: str,
        store: str,
        url: str,
        image_url: Optional[str] = None,
        brand: Optional[str] = None,
        category: Optional[str] = None,
        unit_price: Optional[float] = None,
        unit_label: Optional[str] = None,
    ):
        self.name = name
        self.price = price
        self.unit = unit
        self.store = store
        self.url = url
        self.image_url = image_url
        self.brand = brand
        self.category = category
        self.unit_price = unit_price  # Prix au kg/L
        self.unit_label = unit_label  # "€/kg", "€/L", etc.
        self.scraped_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "price": self.price,
            "unit": self.unit,
            "store": self.store,
            "url": self.url,
            "image_url": self.image_url,
            "brand": self.brand,
            "category": self.category,
            "unit_price": self.unit_price,
            "unit_label": self.unit_label,
            "scraped_at": self.scraped_at,
        }
    
    def cache_key(self, query: str) -> str:
        """Generate cache key for this product."""
        key = f"{self.store}:{query}:{self.name}:{self.price}"
        return hashlib.md5(key.encode()).hexdigest()


class BaseScraper(ABC):
    """Base class for all supermarket scrapers."""
    
    def __init__(self, cache_client=None, cache_ttl: int = 3600):
        """
        Initialize scraper.
        
        Args:
            cache_client: Redis client or similar (optional)
            cache_ttl: Cache time-to-live in seconds (default 1 hour)
        """
        self.cache = cache_client
        self.cache_ttl = cache_ttl
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @property
    @abstractmethod
    def store_name(self) -> str:
        """Return the store name (e.g., 'Leclerc', 'Carrefour')."""
        pass
    
    @abstractmethod
    async def search(self, query: str, max_results: int = 10) -> List[Product]:
        """
        Search for products.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of Product objects
        """
        pass
    
    def _get_cache_key(self, query: str) -> str:
        """Generate cache key for a search query."""
        return f"scraper:{self.store_name.lower()}:{hashlib.md5(query.encode()).hexdigest()}"
    
    async def _get_cached(self, query: str) -> Optional[List[Product]]:
        """Get cached results if available."""
        if not self.cache:
            return None
        
        try:
            cache_key = self._get_cache_key(query)
            cached = await asyncio.to_thread(self.cache.get, cache_key)
            
            if cached:
                self.logger.info(f"Cache HIT for query: {query}")
                data = json.loads(cached)
                return [
                    Product(
                        name=p["name"],
                        price=p["price"],
                        unit=p["unit"],
                        store=p["store"],
                        url=p["url"],
                        image_url=p.get("image_url"),
                        brand=p.get("brand"),
                        category=p.get("category"),
                        unit_price=p.get("unit_price"),
                        unit_label=p.get("unit_label"),
                    )
                    for p in data
                ]
        except Exception as e:
            self.logger.warning(f"Cache read error: {e}")
        
        return None
    
    async def _set_cached(self, query: str, products: List[Product]) -> None:
        """Cache search results."""
        if not self.cache:
            return
        
        try:
            cache_key = self._get_cache_key(query)
            data = json.dumps([p.to_dict() for p in products])
            await asyncio.to_thread(self.cache.setex, cache_key, self.cache_ttl, data)
            self.logger.info(f"Cached {len(products)} results for query: {query}")
        except Exception as e:
            self.logger.warning(f"Cache write error: {e}")
    
    async def search_with_cache(self, query: str, max_results: int = 10) -> List[Product]:
        """
        Search with automatic caching.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of Product objects
        """
        # Try cache first
        cached = await self._get_cached(query)
        if cached:
            return cached[:max_results]
        
        # Perform actual search
        self.logger.info(f"Cache MISS for query: {query} - scraping...")
        products = await self.search(query, max_results)
        
        # Cache results
        await self._set_cached(query, products)
        
        return products
    
    async def retry_on_failure(self, coro, max_retries: int = 3, delay: float = 2.0):
        """
        Retry a coroutine on failure.
        
        Args:
            coro: Coroutine to execute
            max_retries: Maximum number of retries
            delay: Delay between retries in seconds
            
        Returns:
            Result of the coroutine
            
        Raises:
            Last exception if all retries fail
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                return await coro
            except Exception as e:
                last_error = e
                self.logger.warning(
                    f"Attempt {attempt + 1}/{max_retries} failed: {e}"
                )
                if attempt < max_retries - 1:
                    await asyncio.sleep(delay * (attempt + 1))
        
        raise last_error
