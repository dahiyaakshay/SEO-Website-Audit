# Package initialization for utils module

# Import utility classes for easier access
from .scraper import WebScraper
from .report_generator import ReportGenerator
from .ai_integration import TogetherAIClient

# Package metadata
__all__ = [
    'WebScraper',
    'ReportGenerator',
    'TogetherAIClient'
]

__version__ = '0.1.0'
