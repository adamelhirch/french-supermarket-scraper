#!/bin/bash
# Test script for quick scraper validation

cd "$(dirname "$0")"
source venv/bin/activate

echo "🧪 Testing Price Scraper..."
echo ""

# Test 1: Search for a common product
echo "Test 1: Searching for 'poulet'..."
python3 compare.py "poulet" -n 3

echo ""
echo "Test 2: Searching for 'lait'..."
python3 compare.py "lait" -n 3

echo ""
echo "✅ Tests complete"
