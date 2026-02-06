"""Scrapers package initialization."""

from .base import BaseScraper, Product
from .leclerc import LeclercScraper
from .carrefour import CarrefourScraper
from .intermarche import IntermarcheScraper

__all__ = [
    "BaseScraper",
    "Product",
    "LeclercScraper",
    "CarrefourScraper",
    "IntermarcheScraper",
]
