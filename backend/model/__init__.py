
"""
ScreenGuard Model Package

This package contains the core image authenticity detection functionality
with specialized transaction fraud analysis capabilities.
"""

from .detector import ImageAuthenticityDetector
from .transaction_analyzer import TransactionAnalyzer

__all__ = ['ImageAuthenticityDetector', 'TransactionAnalyzer']
__version__ = '2.0.0'
