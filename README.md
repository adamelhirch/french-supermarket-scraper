# 🛒 French Supermarket Price Scraper

Web scraping system for French supermarkets (Leclerc, Carrefour, Intermarché).

## Features
- Real-time price comparison
- Product search across multiple stores
- Grocy integration for smart shopping lists
- Redis caching to avoid rate limiting
- Robust error handling with retries

## Architecture
- **Scrapers:** Store-specific implementations
- **Cache:** Redis for performance
- **API:** HTTP server for queries
- **Integration:** Grocy + Firefly III sync

## Setup
```bash
pip install playwright redis beautifulsoup4 aiohttp
playwright install chromium
```

## Usage
See individual scraper files for details.
