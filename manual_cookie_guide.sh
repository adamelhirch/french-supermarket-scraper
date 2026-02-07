#!/bin/bash
# Manual cookie extraction guide for E.Leclerc
# You'll extract cookies manually from your browser

echo "🍪 Manual Cookie Extraction for E.Leclerc"
echo "=========================================="
echo ""
echo "📋 Steps to extract cookies manually:"
echo ""
echo "1. Open Chrome/Firefox and go to: https://www.e-leclerc.com"
echo ""
echo "2. Select your store (Toulouse-Rangueil):"
echo "   - Click 'Choisir mon magasin'"
echo "   - Search for 'Toulouse'"
echo "   - Select your store"
echo ""
echo "3. Open DevTools:"
echo "   - Press F12 (or Cmd+Option+I on Mac)"
echo "   - Go to 'Application' tab (Chrome) or 'Storage' tab (Firefox)"
echo "   - Click 'Cookies' → 'https://www.e-leclerc.com'"
echo ""
echo "4. Copy ALL cookies:"
echo "   - Right-click in the cookies list"
echo "   - Select 'Copy all' or manually copy each cookie"
echo ""
echo "5. Paste the cookies in the terminal when prompted below"
echo ""
echo "================================================================"
echo ""
echo "🔍 Alternative method - Export as JSON:"
echo ""
echo "In Chrome DevTools Console (tab 'Console'), run this JavaScript:"
echo ""
cat << 'JAVASCRIPT'
copy(JSON.stringify(document.cookie.split('; ').map(c => {
  const [name, value] = c.split('=');
  return {
    name: name,
    value: value,
    domain: '.e-leclerc.com',
    path: '/',
    secure: true,
    httpOnly: false,
    sameSite: 'Lax'
  };
}), null, 2));
JAVASCRIPT
echo ""
echo ""
echo "This will copy cookies as JSON to your clipboard."
echo "Then paste them into leclerc_cookies.json"
echo ""
echo "================================================================"
echo ""
echo "📂 Save location:"
echo "   /home/ubuntu/.openclaw/workspace/supermarket-scraper/leclerc_cookies.json"
echo ""
echo "✅ Once saved, run: python3 test_leclerc_cookies.py"
