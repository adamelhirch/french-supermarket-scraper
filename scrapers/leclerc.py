"""E.Leclerc scraper implementation."""

from typing import List, Optional
from playwright.async_api import async_playwright, Browser, Page
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
        """
        Search for products on E.Leclerc.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of Product objects
        """
        # Load cookies
        if not self.cookie_file.exists():
            self.logger.error(f"Cookie file not found: {self.cookie_file}")
            self.logger.error("Run extract_leclerc_cookies.py first to save cookies")
            return []
        
        with open(self.cookie_file) as f:
            cookies = json.load(f)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            await context.add_cookies(cookies)
            page = await context.new_page()
            
            try:
                products = await self._scrape_search_page(page, query, max_results)
                return products
            finally:
                await browser.close()
    
    async def _scrape_search_page(
        self, page: Page, query: str, max_results: int
    ) -> List[Product]:
        """Scrape search results page."""
        try:
            # Use correct URL format: /recherche?q=QUERY
            search_url = f"{self.SEARCH_URL}?q={query}"
            self.logger.info(f"Navigating to: {search_url}")
            
            await page.goto(search_url, wait_until="networkidle", timeout=40000)
            
            # Wait for dynamic content to load (Angular SPA)
            import asyncio
            await asyncio.sleep(10)
            
            # Get page text
            page_text = await page.evaluate('() => document.body.innerText')
            
            # Extract products
            products = []
            lines = page_text.split('\n')
            
            for i, line in enumerate(lines):
                if len(products) >= max_results:
                    break
                
                # Look for price pattern
                price_match = re.search(r'(\d+)[€,.](\d+)\s*€', line)
                if not price_match:
                    continue
                
                # Extract price
                try:
                    price = float(f"{price_match.group(1)}.{price_match.group(2)}")
                except:
                    continue
                
                # Get context for product name
                context_start = max(0, i - 3)
                context_end = min(len(lines), i + 2)
                context_lines = [l.strip() for l in lines[context_start:context_end] if l.strip()]
                
                # Try to find product name (usually before price)
                product_name = None
                for ctx_line in context_lines:
                    # Skip if it's just a price or category
                    if re.search(r'^\d+[€,.]', ctx_line):
                        continue
                    if ctx_line in ['Vérifier la disponibilité', 'Vendu par', 'Autre offre']:
                        continue
                    if len(ctx_line) > 10 and len(ctx_line) < 150:
                        product_name = ctx_line
                        break
                
                if not product_name:
                    product_name = f"Produit {len(products) + 1}"
                
                # Extract unit price if available
                unit_price = None
                unit_label = None
                for ctx_line in context_lines:
                    unit_match = re.search(r'(\d+[,.]?\d*)\s*€\s*/\s*(Kg|kg|L|l)', ctx_line)
                    if unit_match:
                        try:
                            unit_price = float(unit_match.group(1).replace(',', '.'))
                            unit_label = f"€/{unit_match.group(2)}"
                        except:
                            pass
                        break
                
                # Create product
                product = Product(
                    name=product_name,
                    price=price,
                    unit="pièce",
                    store=self.store_name,
                    url=search_url,
                    unit_price=unit_price,
                    unit_label=unit_label,
                )
                
                products.append(product)
                self.logger.debug(f"Extracted: {product_name} - {price}€")
            
            self.logger.info(f"Found {len(products)} products")
            return products
            
        except Exception as e:
            self.logger.error(f"Error scraping search page: {e}")
            return []
    
    async def _extract_product(self, element, page: Page) -> Optional[Product]:
        """Extract product data from a product element."""
        try:
            # Extract name
            name_selectors = [
                '.product-name',
                '.product-title',
                '[data-product-name]',
                'h3',
                '.productName'
            ]
            name = None
            for selector in name_selectors:
                name_elem = await element.query_selector(selector)
                if name_elem:
                    name = (await name_elem.inner_text()).strip()
                    break
            
            if not name:
                return None
            
            # Extract price
            price_selectors = [
                '.product-price',
                '.price',
                '[data-product-price]',
                '.productPrice-price'
            ]
            price_text = None
            for selector in price_selectors:
                price_elem = await element.query_selector(selector)
                if price_elem:
                    price_text = (await price_elem.inner_text()).strip()
                    break
            
            if not price_text:
                return None
            
            # Parse price (handle formats like "2,50 €", "2.50€", etc.)
            price_match = re.search(r'(\d+)[,.](\d+)', price_text)
            if not price_match:
                return None
            
            price = float(f"{price_match.group(1)}.{price_match.group(2)}")
            
            # Extract unit (pièce, kg, etc.)
            unit = "pièce"  # Default
            unit_elem = await element.query_selector('.product-unit, .unit, [data-product-unit]')
            if unit_elem:
                unit = (await unit_elem.inner_text()).strip()
            
            # Extract URL
            link_elem = await element.query_selector('a[href]')
            url = self.BASE_URL
            if link_elem:
                href = await link_elem.get_attribute('href')
                if href:
                    url = href if href.startswith('http') else f"{self.BASE_URL}{href}"
            
            # Extract image
            image_url = None
            img_elem = await element.query_selector('img')
            if img_elem:
                image_url = await img_elem.get_attribute('src')
                if image_url and not image_url.startswith('http'):
                    image_url = f"{self.BASE_URL}{image_url}"
            
            # Extract brand
            brand = None
            brand_elem = await element.query_selector('.product-brand, .brand, [data-product-brand]')
            if brand_elem:
                brand = (await brand_elem.inner_text()).strip()
            
            # Extract unit price (€/kg, €/L, etc.)
            unit_price = None
            unit_label = None
            unit_price_elem = await element.query_selector('.unit-price, .product-unit-price, [data-unit-price]')
            if unit_price_elem:
                unit_price_text = (await unit_price_elem.inner_text()).strip()
                unit_match = re.search(r'(\d+)[,.](\d+)\s*€\s*/\s*(\w+)', unit_price_text)
                if unit_match:
                    unit_price = float(f"{unit_match.group(1)}.{unit_match.group(2)}")
                    unit_label = f"€/{unit_match.group(3)}"
            
            return Product(
                name=name,
                price=price,
                unit=unit,
                store=self.store_name,
                url=url,
                image_url=image_url,
                brand=brand,
                unit_price=unit_price,
                unit_label=unit_label,
            )
            
        except Exception as e:
            self.logger.error(f"Error extracting product: {e}")
            return None
