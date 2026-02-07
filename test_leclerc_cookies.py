"""Test Leclerc scraping with saved cookies."""

import asyncio
from playwright.async_api import async_playwright
import json
import re
from pathlib import Path

async def test_with_cookies():
    print("🧪 Testing E.Leclerc with saved cookies\n")
    
    cookie_file = Path('/home/ubuntu/.openclaw/workspace/supermarket-scraper/leclerc_cookies.json')
    
    if not cookie_file.exists():
        print("❌ Cookie file not found!")
        print(f"   Expected: {cookie_file}")
        print("\n   Run extract_leclerc_cookies.py first to save cookies.")
        return
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
        # Load cookies
        print("🍪 Loading cookies...")
        with open(cookie_file) as f:
            cookies = json.load(f)
        
        await context.add_cookies(cookies)
        print(f"✅ Loaded {len(cookies)} cookies\n")
        
        page = await context.new_page()
        
        try:
            print("🔍 Searching for 'poulet' with cookies...")
            await page.goto('https://www.e-leclerc.com/recherche?text=poulet', 
                          wait_until='networkidle', timeout=40000)
            
            # Wait for content
            await asyncio.sleep(8)
            
            # Check results
            page_text = await page.evaluate('() => document.body.innerText')
            
            # Count prices
            prices = re.findall(r'(\d+[,\.]\d+)\s*€', page_text)
            
            print(f"💰 Found {len(prices)} prices on page\n")
            
            if len(prices) > 5:
                print("✅ Products loaded successfully!\n")
                
                # Extract first products
                lines = page_text.split('\n')
                products_found = 0
                
                for i, line in enumerate(lines):
                    if re.search(r'\d+[,\.]\d+\s*€', line) and 'poulet' in line.lower():
                        products_found += 1
                        if products_found <= 5:
                            context_start = max(0, i-1)
                            context_end = min(len(lines), i+2)
                            context = [l.strip() for l in lines[context_start:context_end] if l.strip()]
                            
                            print(f"Product {products_found}:")
                            print(f"  {' | '.join(context[:3])}")
                            print()
                
                if products_found == 0:
                    print("⚠️  Prices found but no 'poulet' products")
                    print("   Showing any 5 products with prices:\n")
                    
                    shown = 0
                    for i, line in enumerate(lines):
                        if re.search(r'\d+[,\.]\d+\s*€', line) and shown < 5:
                            shown += 1
                            context = lines[max(0,i-1):i+2]
                            print(f"  {' | '.join([l.strip() for l in context if l.strip()])}")
                            print()
            else:
                print("❌ Not enough products found")
                print(f"\nPage text sample:\n{page_text[:600]}")
            
            # Save screenshot
            await page.screenshot(path='/tmp/leclerc_with_cookies.png')
            print("📸 Screenshot: /tmp/leclerc_with_cookies.png")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(test_with_cookies())
