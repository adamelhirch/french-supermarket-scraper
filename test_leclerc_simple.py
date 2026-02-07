"""Quick test for Leclerc scraping with real selectors."""

import asyncio
from playwright.async_api import async_playwright
import re

async def test_leclerc():
    print('🔍 Testing E.Leclerc scraper...\n')
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Navigate to search
            await page.goto('https://www.e-leclerc.com/recherche?text=poulet', 
                          wait_until='networkidle', timeout=45000)
            
            # Wait for content to render (Angular SPA)
            print('⏳ Waiting for dynamic content...')
            await asyncio.sleep(8)
            
            # Get page text to verify products loaded
            page_text = await page.evaluate('() => document.body.innerText')
            
            if '€' in page_text and ('poulet' in page_text.lower() or 'filet' in page_text.lower()):
                print('✅ Products detected on page\n')
                
                # Try to extract visible text with prices
                lines = page_text.split('\n')
                products_found = 0
                
                for i, line in enumerate(lines):
                    if re.search(r'\d+[,\.]\d+\s*€', line):
                        products_found += 1
                        if products_found <= 3:
                            # Look at surrounding lines for product name
                            context = lines[max(0, i-2):i+1]
                            print(f'Product {products_found}:')
                            print(f'  {" / ".join([l.strip() for l in context if l.strip()])}')
                            print()
                
                print(f'\n✅ Found {products_found} items with prices')
            else:
                print('❌ No products detected')
                print(f'Page text sample:\n{page_text[:500]}')
        
        except Exception as e:
            print(f'❌ Error: {e}')
        
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(test_leclerc())
