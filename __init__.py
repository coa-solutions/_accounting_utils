"""
Shared Accounting Utilities

Utilities for accounting periods and date ranges.
Used by Mercury, ops/ledger, and other financial integrations.
"""

from .periods import add_months, parse_period, generate_months, DATA_START_DATE

__all__ = [
    'add_months',
    'parse_period',
    'generate_months',
    'DATA_START_DATE',
]
