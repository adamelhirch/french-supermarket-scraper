"""HTTP API server for price comparison."""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional
import logging
import asyncio
from price_comparator import PriceComparator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="French Supermarket Price API",
    description="Compare prices across Leclerc, Carrefour, and Intermarché",
    version="1.0.0"
)

# Initialize comparator (will be created on startup)
comparator = None


@app.on_event("startup")
async def startup_event():
    """Initialize the price comparator on startup."""
    global comparator
    # TODO: Add Redis client here if needed
    comparator = PriceComparator(cache_client=None)
    logger.info("Price comparator initialized")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "French Supermarket Price API",
        "version": "1.0.0",
        "endpoints": {
            "/search": "Search for products",
            "/compare": "Compare prices across stores",
            "/health": "Health check"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/search")
async def search(
    q: str = Query(..., description="Search query"),
    max_results: int = Query(10, ge=1, le=50, description="Max results per store")
):
    """
    Search for products across all stores.
    
    Args:
        q: Search query
        max_results: Maximum results per store (1-50)
        
    Returns:
        List of products from all stores
    """
    if not comparator:
        raise HTTPException(status_code=503, detail="Comparator not initialized")
    
    try:
        logger.info(f"Search request: q={q}, max_results={max_results}")
        products = await comparator.search_all(q, max_results)
        
        return {
            "query": q,
            "total_results": len(products),
            "products": [p.to_dict() for p in products]
        }
    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/compare")
async def compare(
    q: str = Query(..., description="Search query"),
    max_per_store: int = Query(5, ge=1, le=20, description="Max results per store")
):
    """
    Compare prices for a product across stores.
    
    Args:
        q: Search query
        max_per_store: Maximum results per store (1-20)
        
    Returns:
        Price comparison with best deals
    """
    if not comparator:
        raise HTTPException(status_code=503, detail="Comparator not initialized")
    
    try:
        logger.info(f"Compare request: q={q}, max_per_store={max_per_store}")
        results = await comparator.compare_prices(q, max_per_store)
        
        return results
    except Exception as e:
        logger.error(f"Compare error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9998,
        log_level="info"
    )
