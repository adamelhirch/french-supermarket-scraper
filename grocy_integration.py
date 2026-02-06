"""Integration with Grocy for smart shopping lists."""

import asyncio
import json
import subprocess
import os
from typing import List, Dict
from price_comparator import PriceComparator


def get_grocy_shopping_list() -> List[Dict]:
    """Get shopping list from Grocy."""
    api_key_file = os.path.expanduser("~/.openclaw/secrets/grocy_api_key.txt")
    
    if not os.path.exists(api_key_file):
        raise FileNotFoundError("Grocy API key not found")
    
    with open(api_key_file) as f:
        api_key = f.read().strip()
    
    # Use Grocy API to get shopping list
    result = subprocess.run([
        "curl", "-s",
        "-H", f"GROCY-API-KEY: {api_key}",
        "https://grocy.adamelhirch.com/api/objects/shopping_list"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Failed to fetch Grocy shopping list: {result.stderr}")
    
    items = json.loads(result.stdout)
    return items


async def price_compare_shopping_list(items: List[Dict]) -> Dict:
    """
    Compare prices for all items in shopping list.
    
    Args:
        items: Grocy shopping list items
        
    Returns:
        Dictionary with price comparisons for each item
    """
    comparator = PriceComparator()
    results = {}
    
    for item in items:
        product_name = item.get("product", {}).get("name", item.get("note", ""))
        if not product_name:
            continue
        
        print(f"🔍 Comparing prices for: {product_name}")
        
        try:
            comparison = await comparator.compare_prices(product_name, max_per_store=3)
            results[product_name] = comparison
        except Exception as e:
            print(f"❌ Error comparing {product_name}: {e}")
            results[product_name] = {"error": str(e)}
    
    return results


def format_shopping_report(results: Dict) -> str:
    """Format shopping comparison results as a readable report."""
    report = "🛒 **Smart Shopping Report**\n\n"
    
    total_best_price = 0
    total_savings = 0
    
    for product_name, data in results.items():
        if "error" in data:
            report += f"❌ {product_name}: {data['error']}\n\n"
            continue
        
        if not data.get("best_deals"):
            report += f"🔍 {product_name}: No results found\n\n"
            continue
        
        best_deal = data["best_deals"][0]
        
        report += f"**{product_name}**\n"
        report += f"  💰 Best: {best_deal['best_price']:.2f}€ @ {best_deal['best_store']}\n"
        
        if best_deal['savings'] > 0:
            report += f"  💸 Save {best_deal['savings']:.2f}€ ({best_deal['price_difference_percent']}%)\n"
            total_savings += best_deal['savings']
        
        total_best_price += best_deal['best_price']
        
        if len(best_deal['all_prices']) > 1:
            report += "  📊 Other stores:\n"
            for price in best_deal['all_prices'][1:]:
                report += f"    • {price['store']}: {price['price']:.2f}€\n"
        
        report += "\n"
    
    report += "---\n"
    report += f"**Total (best prices): {total_best_price:.2f}€**\n"
    if total_savings > 0:
        report += f"**Total savings: {total_savings:.2f}€**\n"
    
    return report


async def main():
    """Generate smart shopping report."""
    print("🛒 Fetching Grocy shopping list...")
    items = get_grocy_shopping_list()
    
    if not items:
        print("✅ Shopping list is empty")
        return
    
    print(f"📝 Found {len(items)} items\n")
    
    print("🔍 Comparing prices across supermarkets...")
    results = await price_compare_shopping_list(items)
    
    print("\n" + "="*60)
    report = format_shopping_report(results)
    print(report)
    
    # Save report
    output_file = "/home/ubuntu/.openclaw/workspace/shopping_report.txt"
    with open(output_file, "w") as f:
        f.write(report)
    
    print(f"\n💾 Report saved to: {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
