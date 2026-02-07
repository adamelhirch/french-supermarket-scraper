# Cookie-Based Scraping Setup for E.Leclerc

## 🎯 Strategy

Since E.Leclerc blocks automated store selection, we use **manual cookie extraction**:
1. You manually select your store once in a real browser
2. We extract and save the cookies
3. Future scraping sessions reuse those cookies

## 📋 Steps

### 1. Extract Cookies (One-Time Setup)

**Important:** Run this on a machine with a display (your Mac or via VNC on VPS).

```bash
cd /home/ubuntu/.openclaw/workspace/supermarket-scraper
source venv/bin/activate

# On Mac with display:
python3 extract_leclerc_cookies.py

# On VPS with X11 forwarding:
DISPLAY=:0 python3 extract_leclerc_cookies.py
```

**What happens:**
1. A Chrome window opens
2. You manually select "Toulouse-Rangueil" (or your preferred store)
3. Press ENTER in terminal
4. Cookies are saved to `leclerc_cookies.json`

### 2. Test Cookies

```bash
python3 test_leclerc_cookies.py
```

If successful, you'll see product results for "poulet" with your store's prices.

### 3. Use in Production

Update `scrapers/leclerc.py` to load cookies before scraping:

```python
async def search(self, query: str, max_results: int = 10):
    # Load cookies
    cookie_file = Path(__file__).parent.parent / "leclerc_cookies.json"
    with open(cookie_file) as f:
        cookies = json.load(f)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        await context.add_cookies(cookies)
        page = await context.new_page()
        
        # ... rest of scraping code
```

## ⚠️ Limitations

- **Cookies expire** after some time (weeks/months)
- **Re-run extraction** when cookies expire
- **Store-specific**: Cookies tied to your selected store

## 🔄 Refresh Cookies

When cookies stop working:
1. Run `extract_leclerc_cookies.py` again
2. Select store manually
3. Cookies refreshed

## 📁 Files

- `extract_leclerc_cookies.py` - Cookie extraction helper
- `test_leclerc_cookies.py` - Test saved cookies
- `leclerc_cookies.json` - Saved cookies (gitignored)
- `leclerc_cookies_simple.json` - Simple name:value dict

## 🚀 Next Steps

After successful cookie test:
1. Update main Leclerc scraper to use cookies
2. Update Carrefour scraper (if cookies work there too)
3. Test Intermarché with same approach
