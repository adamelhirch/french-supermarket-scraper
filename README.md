# 🛒 French Supermarket Price Scraper

Web scraping system for French supermarkets (Leclerc, Carrefour, Intermarché) with intelligent price comparison.

## Features
- 🔍 **Real-time price comparison** across 3 major French supermarkets
- 💰 **Best price detection** with savings calculation
- 🛒 **Grocy integration** for smart shopping lists
- ⚡ **Redis caching** to avoid rate limiting (optional)
- 🎯 **Robust error handling** with automatic retries
- 🌐 **FastAPI HTTP server** for programmatic access
- 🖥️ **CLI tool** for quick terminal queries

## Supported Stores
- E.Leclerc (https://www.e-leclerc.com)
- Carrefour (https://www.carrefour.fr)
- Intermarché (https://www.intermarche.com)

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/adamelhirch/french-supermarket-scraper.git
cd french-supermarket-scraper
```

### 2. Create virtual environment and install dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

## Usage

### CLI Tool (Quick Comparison)
```bash
# Search for a product
./compare.py "poulet"

# Limit results per store
./compare.py "lait" -n 3

# Verbose mode
./compare.py "pain" -v
```

### Python API
```python
from price_comparator import PriceComparator
import asyncio

async def main():
    comparator = PriceComparator()
    results = await comparator.compare_prices("poulet", max_per_store=5)
    
    for deal in results['best_deals']:
        print(f"{deal['name']}: {deal['best_price']}€ @ {deal['best_store']}")

asyncio.run(main())
```

### HTTP API Server
```bash
# Start server
source venv/bin/activate
python api_server.py

# Server runs on http://localhost:9998
# Endpoints:
#   GET /search?q=poulet&max_results=10
#   GET /compare?q=lait&max_per_store=5
```

### Grocy Integration
```bash
# Generate smart shopping report from Grocy list
source venv/bin/activate
python grocy_integration.py
```

## Architecture

```
supermarket-scraper/
├── scrapers/
│   ├── base.py           # Base scraper class with caching
│   ├── leclerc.py        # E.Leclerc scraper
│   ├── carrefour.py      # Carrefour scraper
│   └── intermarche.py    # Intermarché scraper
├── price_comparator.py   # Price comparison engine
├── api_server.py         # FastAPI HTTP server
├── compare.py            # CLI tool
├── grocy_integration.py  # Grocy shopping list integration
└── requirements.txt      # Python dependencies
```

## How It Works

1. **Query**: User provides a product name (e.g., "poulet")
2. **Parallel Scraping**: All store scrapers run simultaneously using Playwright
3. **Data Extraction**: Product name, price, unit, brand, image, URL extracted
4. **Caching**: Results cached (optional Redis) to reduce load
5. **Comparison**: Best prices found, savings calculated
6. **Output**: Results formatted and returned (CLI/API/Grocy)

## Configuration

### Redis Caching (Optional)
```python
import redis
from price_comparator import PriceComparator

redis_client = redis.Redis(host='localhost', port=6379, db=0)
comparator = PriceComparator(cache_client=redis_client)
```

### Grocy API
Store your Grocy API key in:
```
~/.openclaw/secrets/grocy_api_key.txt
```

## Testing
```bash
./test.sh
```

## Example Output
```
🛒 Price Comparison: 'poulet'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Found 15 products from 3 stores
Stores: Leclerc, Carrefour, Intermarché

1. Poulet fermier entier
   💰 Best: 6.99€ @ Leclerc
   💸 Save 2.00€ (22.2%)
   📊 Prices:
      ✅ Leclerc: 6.99€
         Carrefour: 8.49€
         Intermarché: 8.99€
   🔗 https://www.e-leclerc.com/...
```

## Known Limitations
- **Dynamic websites**: Supermarket sites change frequently, scrapers may need updates
- **Rate limiting**: Use caching and reasonable delays to avoid blocks
- **Accuracy**: Product matching is approximate (name-based), may have false positives
- **Regional pricing**: Prices vary by location, scrapers use default stores

## Future Improvements
- [ ] Location-based store selection
- [ ] Better product matching (fuzzy search, images)
- [ ] Price history tracking
- [ ] Mobile app integration
- [ ] Automated scraper health checks
- [ ] Multi-language support

## Contributing
Pull requests welcome! Please ensure:
- Code follows existing style
- Tests pass (`./test.sh`)
- Commit messages are clear

## License
MIT License - see LICENSE file

## Author
**Adam El Hirch** - [GitHub](https://github.com/adamelhirch)

## Disclaimer
This tool is for educational and personal use only. Respect robots.txt and terms of service of scraped websites. Use responsibly and ethically.
