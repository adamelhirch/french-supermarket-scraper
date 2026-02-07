"""Manual cookie extraction helper for E.Leclerc store selection.

This script helps you manually select your store on Leclerc, then extracts the cookies
for future automated scraping.

Steps:
1. Run this script
2. A browser window will open
3. Navigate to E.Leclerc and select your store (Toulouse-Rangueil)
4. Press Enter in the terminal
5. Cookies will be saved to leclerc_cookies.json
"""

import asyncio
from playwright.async_api import async_playwright
import json

async def extract_cookies():
    print("🍪 Cookie Extraction Helper for E.Leclerc\n")
    print("=" * 60)
    
    async with async_playwright() as p:
        # Launch visible browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("\n📍 Step 1: Opening E.Leclerc...")
        await page.goto('https://www.e-leclerc.com')
        
        print("\n✋ MANUAL ACTION REQUIRED:")
        print("   1. Click 'Choisir mon magasin'")
        print("   2. Search for 'Toulouse' or your location")
        print("   3. Select your preferred store (e.g., Toulouse-Rangueil)")
        print("   4. Wait for the page to reload with your store selected")
        print("\n   Then press ENTER here to continue...")
        
        input()
        
        print("\n🍪 Extracting cookies...")
        cookies = await context.cookies()
        
        # Save cookies
        cookie_file = '/home/ubuntu/.openclaw/workspace/supermarket-scraper/leclerc_cookies.json'
        with open(cookie_file, 'w') as f:
            json.dump(cookies, f, indent=2)
        
        print(f"✅ Cookies saved to: {cookie_file}")
        print(f"   Found {len(cookies)} cookies")
        
        # Also save as a simple dict for easier use
        cookie_dict = {c['name']: c['value'] for c in cookies}
        dict_file = '/home/ubuntu/.openclaw/workspace/supermarket-scraper/leclerc_cookies_simple.json'
        with open(dict_file, 'w') as f:
            json.dump(cookie_dict, f, indent=2)
        
        print(f"✅ Simple cookie dict saved to: {dict_file}\n")
        
        # Show important cookies
        store_cookies = [c for c in cookies if 'store' in c['name'].lower() or 'magasin' in c['name'].lower()]
        if store_cookies:
            print("📍 Store-related cookies found:")
            for c in store_cookies:
                print(f"   - {c['name']}: {c['value'][:50]}...")
        else:
            print("⚠️  No obvious store cookies found. All cookies saved anyway.")
        
        print("\n🧪 Testing cookies...")
        await page.goto('https://www.e-leclerc.com/recherche?text=poulet')
        await asyncio.sleep(3)
        
        # Check if store is still selected
        page_text = await page.evaluate('() => document.body.innerText')
        if 'Choisir mon magasin' in page_text:
            print("⚠️  Store selection may not persist in cookies")
        else:
            print("✅ Store selection seems to persist!")
        
        input("\nPress ENTER to close browser...")
        await browser.close()

if __name__ == '__main__':
    asyncio.run(extract_cookies())
