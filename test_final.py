import asyncio
from playwright.async_api import async_playwright
import json
import re

async def test_various_queries():
    """Test different product queries to see what works."""
    
    with open('leclerc_cookies.json') as f:
        cookies = json.load(f)
    
    queries = ['lait', 'pain', 'tomate', 'riz', 'pates']
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        await context.add_cookies(cookies)
        page = await context.new_page()
        
        print("🧪 Testing multiple food queries\n")
        print("=" * 60)
        
        for query in queries:
            print(f"\n🔍 Query: '{query}'")
            print("-" * 40)
            
            url = f'https://www.e.leclerc/recherche?q={query}'
            await page.goto(url, wait_until='networkidle', timeout=40000)
            await asyncio.sleep(8)
            
            page_text = await page.evaluate('() => document.body.innerText')
            prices = re.findall(r'(\d+[,\.]\d+)\s*€', page_text)
            
            print(f"💰 Prices found: {len(prices)}")
            
            # Check if alimentary products
            has_food_keywords = any(word in page_text.lower() for word in [
                'bio', 'fermier', 'frais', 'laitier', 'boulang', 'kg', 'litre'
            ])
            
            if has_food_keywords:
                print("✅ Food keywords detected")
                
                # Show first product
                lines = page_text.split('\n')
                for i, line in enumerate(lines):
                    if re.search(r'\d+[,\.]\d+\s*€', line):
                        context = lines[max(0,i-2):i+2]
                        print(f"   Sample: {' | '.join([l.strip() for l in context if l.strip()][:3])}")
                        break
            else:
                print("⚠️  No obvious food keywords")
        
        await browser.close()

asyncio.run(test_various_queries())
