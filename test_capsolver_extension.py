"""
Test CapSolver extension with Leclerc Drive DataDome CAPTCHA.

This script needs to run on a machine with:
1. Display (GUI) - not headless
2. CapSolver Chrome extension installed
3. Chrome browser

For VPS: This won't work directly. Need to either:
- Use CapSolver API instead
- Run on Adam's local machine
"""

import asyncio
from playwright.async_api import async_playwright
import json
from pathlib import Path

async def test_capsolver_extension():
    print("🧪 Testing CapSolver Extension with DataDome\n")
    print("⚠️  NOTE: This requires NON-headless Chrome with CapSolver extension\n")
    
    # Load cookies
    cookie_file = Path(__file__).parent / "leclerc_drive_cookies_updated.json"
    with open(cookie_file) as f:
        cookies = json.load(f)
    
    print(f"🍪 Loaded {len(cookies)} cookies\n")
    
    async with async_playwright() as p:
        # Launch Chrome in NON-headless mode
        # You need to specify the extension path
        print("🚀 Launching Chrome (non-headless)...")
        print("⚠️  You need to provide the CapSolver extension path!\n")
        
        # Extension path example (adapt to your system):
        # For Linux: ~/.config/google-chrome/Default/Extensions/...
        # For Windows: %LOCALAPPDATA%\Google\Chrome\User Data\Default\Extensions\...
        # For macOS: ~/Library/Application Support/Google/Chrome/Default/Extensions/...
        
        # TEMPORARY: Launch without extension to show the workflow
        browser = await p.chromium.launch(
            headless=False,  # MUST be False for CapSolver extension
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                # To load extension, add:
                # f'--disable-extensions-except={extension_path}',
                # f'--load-extension={extension_path}'
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        )
        
        await context.add_cookies(cookies)
        page = await context.new_page()
        
        url = 'https://fd7-courses.leclercdrive.fr/magasin-123111-123111-Montaudran/recherche.aspx?TexteRecherche=riz'
        
        print(f"🔗 Navigating to: {url}")
        await page.goto(url, wait_until='domcontentloaded', timeout=60000)
        
        print("\n⏳ Waiting for CapSolver to detect and solve CAPTCHA...")
        print("   (This should take 10-30 seconds if extension is loaded)\n")
        
        # Wait longer for CAPTCHA to be solved
        await asyncio.sleep(30)
        
        # Check if we passed the CAPTCHA
        page_text = await page.evaluate('() => document.body.innerText')
        title = await page.title()
        
        print(f"📄 Title: {title}")
        
        has_captcha = 'access is temporarily restricted' in page_text.lower() or 'datadome' in page_text.lower()
        has_products = len(page_text) > 1000
        
        if has_captcha:
            print("\n❌ Still blocked by DataDome CAPTCHA")
            print("   → CapSolver extension not loaded or didn't solve it")
        elif has_products:
            print("\n✅ SUCCESS! Page loaded with content!")
            print(f"   Page text length: {len(page_text)} chars")
            print(f"\n   First 500 chars:\n{page_text[:500]}")
        else:
            print("\n⚠️  Unclear status")
            print(f"   Page text: {page_text[:300]}")
        
        await page.screenshot(path='/tmp/capsolver_test.png')
        print("\n📸 Screenshot: /tmp/capsolver_test.png")
        
        print("\n⏸️  Browser will stay open for 30s for manual inspection...")
        await asyncio.sleep(30)
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(test_capsolver_extension())
