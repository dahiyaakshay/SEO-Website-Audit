# Package initialization for analyzers module

# Import analyzers for easier access
from .seo_analyzer import SEOAnalyzer
from .performance_analyzer import PerformanceAnalyzer
from .content_analyzer import ContentAnalyzer
from .accessibility_analyzer import AccessibilityAnalyzer
from .security_analyzer import SecurityAnalyzer
from .design_analyzer import DesignAnalyzer

# Package metadata
__all__ = [
    'SEOAnalyzer',
    'PerformanceAnalyzer',
    'ContentAnalyzer',
    'AccessibilityAnalyzer',
    'SecurityAnalyzer',
    'DesignAnalyzer'
]

__version__ = '0.1.0'
