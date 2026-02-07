"""Improved E.Leclerc scraper with accurate product name extraction."""

from typing import List
from playwright.async_api import async_playwright
import re
import json
from pathlib import Path
from .base import BaseScraper, Product


class LeclercScraper(BaseScraper):
    """Scraper for E.Leclerc online store."""
    
    BASE_URL = "https://www.e.leclerc"
    SEARCH_URL = "https://www.e.leclerc/recherche"
    
    def __init__(self, cache_client=None, cache_ttl: int = 3600):
        """Initialize Leclerc scraper with cookies."""
        super().__init__(cache_client, cache_ttl)
        self.cookie_file = Path(__file__).parent.parent / "leclerc_cookies.json"
    
    @property
    def store_name(self) -> str:
        return "Leclerc"
    
    async def search(self, query: str, max_results: int = 10) -> List[Product]:
        """Search for products on E.Leclerc."""
        if not self.cookie_file.exists():
            self.logger.error(f"Cookie file not found: {self.cookie_file}")
            return []
        
        with open(self.cookie_file) as f:
            cookies = json.load(f)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            await context.add_cookies(cookies)
            page = await context.new_page()
            
            try:
                products = await self._scrape_products(page, query, max_results)
                return products
            finally:
                await browser.close()
    
    async def _scrape_products(self, page, query: str, max_results: int) -> List[Product]:
        """Scrape products from page."""
        search_url = f"{self.SEARCH_URL}?q={query}"
        self.logger.info(f"Navigating to: {search_url}")
        
        await page.goto(search_url, wait_until="networkidle", timeout=40000)
        
        # Wait for content
        import asyncio
        await asyncio.sleep(10)
        
        # Extract product blocks
        product_texts = await page.evaluate('''() => {
            const elements = document.querySelectorAll('[class*="product"]');
            const results = [];
            elements.forEach(el => {
                const text = el.textContent.trim();
                if (text.length > 20 && text.includes('€')) {
                    results.push(text);
                }
            });
            return results;
        }''')
        
        products = []
        seen_products = set()
        
        for text in product_texts:
            if len(products) >= max_results:
                break
            
            # Pattern: "Product Name  Brand  XX € ,YY ZZ,ZZ € / Unit Vendu par ..."
            # Extract price first
            price_match = re.search(r'(\d+)\s*€\s*,(\d+)', text)
            if not price_match:
                continue
            
            price = float(f"{price_match.group(1)}.{price_match.group(2)}")
            
            # Extract product name (before brand and price)
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            if not lines:
                continue
            
            # First line is usually the product name
            name = lines[0] if lines else f"Product {len(products) + 1}"
            
            # Avoid duplicates
            product_key = f"{name}_{price}"
            if product_key in seen_products:
                continue
            seen_products.add(product_key)
            
            # Extract brand (second line if exists and short)
            brand = None
            if len(lines) > 1 and len(lines[1]) < 30 and not re.search(r'\d+.*€', lines[1]):
                brand = lines[1]
            
            # Extract unit price
            unit_price = None
            unit_label = None
            unit_match = re.search(r'(\d+[,.]?\d*)\s*€\s*/\s*(Kg|kg|L|l|Kilo)', text)
            if unit_match:
                unit_price = float(unit_match.group(1).replace(',', '.'))
                unit_str = unit_match.group(2)
                if unit_str == 'Kilo':
                    unit_str = 'kg'
                unit_label = f"€/{unit_str}"
            
            product = Product(
                name=name,
                price=price,
                unit="pièce",
                store=self.store_name,
                url=search_url,
                brand=brand,
                unit_price=unit_price,
                unit_label=unit_label,
            )
            
            products.append(product)
            self.logger.debug(f"Extracted: {name} - {price}€")
        
        self.logger.info(f"Found {len(products)} products")
        return products
