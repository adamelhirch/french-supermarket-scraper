#!/usr/bin/env python3
"""CLI tool for quick price comparison."""

import asyncio
import sys
import argparse
from price_comparator import PriceComparator
import logging


def print_results(results):
    """Pretty print comparison results."""
    print(f"\n🛒 Price Comparison: '{results['query']}'")
    print(f"━" * 60)
    print(f"Found {results['total_products']} products from {len(results['stores_searched'])} stores")
    print(f"Stores: {', '.join(results['stores_searched'])}\n")
    
    if not results['best_deals']:
        print("❌ No products found")
        return
    
    for i, deal in enumerate(results['best_deals'][:10], 1):
        print(f"{i}. {deal['name']}")
        print(f"   💰 Best: {deal['best_price']:.2f}€ @ {deal['best_store']}")
        
        if deal['savings'] > 0:
            print(f"   💸 Save {deal['savings']:.2f}€ ({deal['price_difference_percent']}%)")
        
        if len(deal['all_prices']) > 1:
            print(f"   📊 Prices:")
            for price_info in deal['all_prices']:
                indicator = "✅" if price_info['store'] == deal['best_store'] else "  "
                print(f"      {indicator} {price_info['store']}: {price_info['price']:.2f}€")
        
        print(f"   🔗 {deal['url']}")
        print()


async def main():
    """Run CLI price comparison."""
    parser = argparse.ArgumentParser(
        description="Compare prices across French supermarkets"
    )
    parser.add_argument(
        "query",
        help="Product to search for (e.g., 'poulet', 'lait', 'pain')"
    )
    parser.add_argument(
        "-n", "--max-per-store",
        type=int,
        default=5,
        help="Maximum results per store (default: 5)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(level=log_level)
    
    # Run comparison
    comparator = PriceComparator()
    results = await comparator.compare_prices(args.query, args.max_per_store)
    
    # Print results
    print_results(results)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
