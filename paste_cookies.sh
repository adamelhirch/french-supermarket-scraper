#!/bin/bash
# Quick cookie paste helper

cd "$(dirname "$0")"

echo "🍪 Cookie Paste Helper"
echo "====================="
echo ""
echo "Paste your cookies JSON here (press Ctrl+D when done):"
echo ""

# Read multiline input
COOKIES=$(cat)

# Save to file
echo "$COOKIES" > leclerc_cookies.json

echo ""
echo "✅ Cookies saved to leclerc_cookies.json"
echo ""
echo "🧪 Testing cookies..."
source venv/bin/activate
python3 test_leclerc_cookies.py
