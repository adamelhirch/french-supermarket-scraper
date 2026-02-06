"""Price comparison engine."""

from typing import List, Dict
import asyncio
import logging
from scrapers import LeclercScraper, CarrefourScraper, IntermarcheScraper, Product

logger = logging.getLogger(__name__)


class PriceComparator:
    """Compare prices across multiple supermarkets."""
    
    def __init__(self, cache_client=None):
        """
        Initialize price comparator.
        
        Args:
            cache_client: Redis client (optional)
        """
        self.scrapers = [
            LeclercScraper(cache_client),
            CarrefourScraper(cache_client),
            IntermarcheScraper(cache_client),
        ]
    
    async def search_all(self, query: str, max_per_store: int = 10) -> List[Product]:
        """
        Search all stores in parallel.
        
        Args:
            query: Search query
            max_per_store: Maximum results per store
            
        Returns:
            List of all products from all stores
        """
        logger.info(f"Searching '{query}' across {len(self.scrapers)} stores...")
        
        # Run all scrapers in parallel
        tasks = [
            scraper.search_with_cache(query, max_per_store)
            for scraper in self.scrapers
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results and filter errors
        all_products = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Scraper {self.scrapers[i].store_name} failed: {result}")
            else:
                all_products.extend(result)
        
        logger.info(f"Found {len(all_products)} total products")
        return all_products
    
    def find_best_price(self, products: List[Product]) -> Dict:
        """
        Find the best price among products.
        
        Args:
            products: List of products to compare
            
        Returns:
            Dictionary with best price info
        """
        if not products:
            return None
        
        # Group by approximate name (case-insensitive, stripped)
        by_name = {}
        for p in products:
            key = p.name.lower().strip()
            if key not in by_name:
                by_name[key] = []
            by_name[key].append(p)
        
        # Find best price for each group
        best_deals = []
        for name, group in by_name.items():
            sorted_group = sorted(group, key=lambda x: x.price)
            cheapest = sorted_group[0]
            
            # Calculate savings vs most expensive
            most_expensive = sorted_group[-1]
            savings = most_expensive.price - cheapest.price if len(sorted_group) > 1 else 0
            
            best_deals.append({
                "name": cheapest.name,
                "best_price": cheapest.price,
                "best_store": cheapest.store,
                "url": cheapest.url,
                "all_prices": [
                    {
                        "store": p.store,
                        "price": p.price,
                        "unit": p.unit,
                        "url": p.url,
                    }
                    for p in sorted_group
                ],
                "savings": round(savings, 2),
                "price_difference_percent": round(
                    (savings / most_expensive.price * 100) if most_expensive.price > 0 else 0,
                    1
                ),
            })
        
        # Sort by best savings
        best_deals.sort(key=lambda x: x["savings"], reverse=True)
        
        return best_deals
    
    async def compare_prices(self, query: str, max_per_store: int = 5) -> Dict:
        """
        Compare prices for a query across all stores.
        
        Args:
            query: Search query
            max_per_store: Maximum results per store
            
        Returns:
            Comparison results with best deals
        """
        # Search all stores
        products = await self.search_all(query, max_per_store)
        
        if not products:
            return {
                "query": query,
                "total_products": 0,
                "best_deals": [],
            }
        
        # Find best prices
        best_deals = self.find_best_price(products)
        
        return {
            "query": query,
            "total_products": len(products),
            "stores_searched": list(set(p.store for p in products)),
            "best_deals": best_deals,
        }


async def main():
    """Test the price comparator."""
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    query = sys.argv[1] if len(sys.argv) > 1 else "poulet"
    
    comparator = PriceComparator()
    results = await comparator.compare_prices(query, max_per_store=5)
    
    print(f"\n🛒 Price Comparison: '{query}'")
    print(f"Found {results['total_products']} products from {len(results['stores_searched'])} stores")
    print(f"Stores: {', '.join(results['stores_searched'])}\n")
    
    for i, deal in enumerate(results['best_deals'][:5], 1):
        print(f"{i}. {deal['name']}")
        print(f"   💰 Best: {deal['best_price']:.2f}€ @ {deal['best_store']}")
        if deal['savings'] > 0:
            print(f"   💸 Save {deal['savings']:.2f}€ ({deal['price_difference_percent']}%)")
        print(f"   🔗 {deal['url']}")
        
        if len(deal['all_prices']) > 1:
            print(f"   📊 Other prices:")
            for price in deal['all_prices'][1:]:
                print(f"      • {price['store']}: {price['price']:.2f}€")
        print()


if __name__ == "__main__":
    asyncio.run(main())
