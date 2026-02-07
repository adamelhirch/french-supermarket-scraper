"""Test undetected-chromedriver with Carrefour."""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_carrefour():
    print("🚀 Starting undetected-chromedriver test...")
    
    options = uc.ChromeOptions()
    # Remove headless for now - Cloudflare detects it
    # options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    driver = None
    try:
        # Let undetected-chromedriver handle everything
        driver = uc.Chrome(
            options=options,
            version_main=144  # Match Chrome version
        )
        
        print("🔍 Navigating to Carrefour search page...")
        driver.get("https://www.carrefour.fr/s?q=poulet")
        
        # Wait for Cloudflare challenge to resolve
        print("⏳ Waiting for page load (15s)...")
        time.sleep(15)
        
        # Check title
        title = driver.title
        print(f"📄 Page title: {title}")
        
        if "Un instant" in title or "Just a moment" in title:
            print("⚠️  Still on Cloudflare challenge page")
            print("⏳ Waiting additional 10s...")
            time.sleep(10)
            title = driver.title
            print(f"📄 New title: {title}")
        
        # Check current URL
        current_url = driver.current_url
        print(f"🔗 Current URL: {current_url}")
        
        # Try to find products
        print("\n🔍 Looking for product elements...")
        
        selectors_to_try = [
            '[data-testid="product-card"]',
            '.product-card',
            '.product-item',
            '[data-product]',
            'article',
            '.product',
        ]
        
        found_products = False
        for selector in selectors_to_try:
            try:
                products = driver.find_elements(By.CSS_SELECTOR, selector)
                if products:
                    print(f"✅ Found {len(products)} elements with selector: {selector}")
                    found_products = True
                    
                    # Extract first product info
                    if products:
                        first_product = products[0]
                        print(f"\n📦 First product HTML preview:")
                        html = first_product.get_attribute('outerHTML')
                        print(html[:500] + "...")
                    break
            except Exception as e:
                continue
        
        if not found_products:
            print("❌ No products found with any selector")
            print("\n📄 Page source preview (first 2000 chars):")
            print(driver.page_source[:2000])
        
        # Take screenshot
        screenshot_path = "/tmp/carrefour_uc.png"
        driver.save_screenshot(screenshot_path)
        print(f"\n📸 Screenshot saved: {screenshot_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            driver.quit()
            print("\n✅ Browser closed")

if __name__ == "__main__":
    test_carrefour()
