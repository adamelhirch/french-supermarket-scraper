"""Carrefour scraper implementation."""

from typing import List, Optional
from playwright.async_api import async_playwright, Browser, Page
import re
from .base import BaseScraper, Product


class CarrefourScraper(BaseScraper):
    """Scraper for Carrefour online store."""
    
    BASE_URL = "https://www.carrefour.fr"
    SEARCH_URL = "https://www.carrefour.fr/s"
    
    @property
    def store_name(self) -> str:
        return "Carrefour"
    
    async def search(self, query: str, max_results: int = 10) -> List[Product]:
        """
        Search for products on Carrefour.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of Product objects
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            try:
                products = await self._scrape_search_page(browser, query, max_results)
                return products
            finally:
                await browser.close()
    
    async def _scrape_search_page(
        self, browser: Browser, query: str, max_results: int
    ) -> List[Product]:
        """Scrape search results page."""
        page = await browser.new_page()
        
        try:
            # Navigate to search page
            search_url = f"{self.SEARCH_URL}?q={query.replace(' ', '+')}"
            self.logger.info(f"Navigating to: {search_url}")
            
            await page.goto(search_url, wait_until="networkidle", timeout=30000)
            
            # Wait for product grid
            await page.wait_for_selector('[data-testid="product-card"], .product-card, .ds-product-card', timeout=10000)
            
            # Extract products
            products = []
            
            # Carrefour typically uses data-testid attributes
            product_selectors = [
                '[data-testid="product-card"]',
                '.product-card',
                '.ds-product-card',
                '[data-product-id]'
            ]
            
            product_elements = None
            for selector in product_selectors:
                elements = await page.query_selector_all(selector)
                if elements:
                    product_elements = elements
                    self.logger.info(f"Found {len(elements)} products with selector: {selector}")
                    break
            
            if not product_elements:
                self.logger.warning(f"No products found for query: {query}")
                return []
            
            for element in product_elements[:max_results]:
                try:
                    product = await self._extract_product(element, page)
                    if product:
                        products.append(product)
                except Exception as e:
                    self.logger.warning(f"Failed to extract product: {e}")
                    continue
            
            return products
            
        finally:
            await page.close()
    
    async def _extract_product(self, element, page: Page) -> Optional[Product]:
        """Extract product data from a product element."""
        try:
            # Extract name
            name_selectors = [
                '[data-testid="product-title"]',
                '.product-title',
                '.ds-product-title',
                'h3',
                'h2'
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
                '[data-testid="product-price"]',
                '.product-price',
                '.ds-product-price',
                '[data-price]',
                '.price'
            ]
            price_text = None
            for selector in price_selectors:
                price_elem = await element.query_selector(selector)
                if price_elem:
                    price_text = (await price_elem.inner_text()).strip()
                    break
            
            if not price_text:
                return None
            
            # Parse price
            price_match = re.search(r'(\d+)[,.](\d+)', price_text)
            if not price_match:
                return None
            
            price = float(f"{price_match.group(1)}.{price_match.group(2)}")
            
            # Extract unit
            unit = "pièce"
            unit_elem = await element.query_selector('[data-testid="product-unit"], .product-unit, .unit')
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
                # Carrefour often uses lazy loading with data-src
                image_url = await img_elem.get_attribute('src') or await img_elem.get_attribute('data-src')
                if image_url and not image_url.startswith('http'):
                    image_url = f"{self.BASE_URL}{image_url}"
            
            # Extract brand
            brand = None
            brand_elem = await element.query_selector('[data-testid="product-brand"], .product-brand, .brand')
            if brand_elem:
                brand = (await brand_elem.inner_text()).strip()
            
            # Extract unit price
            unit_price = None
            unit_label = None
            unit_price_elem = await element.query_selector('[data-testid="unit-price"], .unit-price')
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
