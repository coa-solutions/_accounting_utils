"""
Accounting Period Utilities

Utilities for parsing accounting/fiscal periods and generating date ranges.
Used across integrations and accounting modules.

Supports: all, ytd, q1-q4, YYYY, YYYY-MM, YYYY-qN
"""

from typing import List, Optional, Tuple
from datetime import datetime, timedelta


def add_months(dt: datetime, months: int) -> datetime:
    """Add (or subtract) months to a datetime."""
    month = dt.month - 1 + months
    year = dt.year + month // 12
    month = month % 12 + 1

    day = dt.day
    while True:
        try:
            return dt.replace(year=year, month=month, day=day)
        except ValueError:
            day -= 1
            if day < 1:
                raise


# ============================================================================
# Constants
# ============================================================================

# Start date for 'all' period queries
DATA_START_DATE = '2022-01-01'


def parse_period(period: str) -> Tuple[str, Optional[str]]:
    """
    Parse accounting period to date range

    Supports: all, ytd, q1-q4, YYYY, YYYY-MM, YYYY-q1

    Args:
        period: Period string (all, ytd, q1-q4, YYYY, YYYY-MM, YYYY-qN)

    Returns:
        Tuple of (start_date, end_date) as ISO strings. end_date is None for open-ended periods.

    Examples:
        >>> parse_period('all')
        ('2022-01-01', None)

        >>> parse_period('ytd')
        ('2025-01-01', None)

        >>> parse_period('q1')
        ('2025-01-01', '2025-03-31')

        >>> parse_period('2024')
        ('2024-01-01', '2024-12-31')

        >>> parse_period('2025-03')
        ('2025-03-01', '2025-03-31')

        >>> parse_period('2024-q2')
        ('2024-04-01', '2024-06-30')
    """
    today = datetime.now()
    current_year = today.year

    period = period.lower().strip()

    # All available data
    if period == 'all':
        return (DATA_START_DATE, None)

    # Year-to-date
    if period == 'ytd':
        return (f'{current_year}-01-01', None)

    # Quarters (current year)
    quarters = {
        'q1': ('01-01', '03-31'),
        'q2': ('04-01', '06-30'),
        'q3': ('07-01', '09-30'),
        'q4': ('10-01', '12-31')
    }
    if period in quarters:
        start_mm_dd, end_mm_dd = quarters[period]
        return (f'{current_year}-{start_mm_dd}', f'{current_year}-{end_mm_dd}')

    # Specific year (YYYY)
    if period.isdigit() and len(period) == 4:
        year = int(period)
        if year == current_year:
            return (f'{year}-01-01', None)
        return (f'{year}-01-01', f'{year}-12-31')

    # Specific month (YYYY-MM)
    if '-' in period and len(period) == 7:
        year, month = period.split('-')
        if month.isdigit():
            # Last day of month
            if int(month) == 12:
                end_date = f'{year}-12-31'
            else:
                next_month = datetime(int(year), int(month) + 1, 1)
                last_day = (next_month - timedelta(days=1)).day
                end_date = f'{year}-{month}-{last_day:02d}'
            return (f'{year}-{month}-01', end_date)

        # Quarter (YYYY-qN)
        if month.startswith('q') and month[1:].isdigit():
            quarter_mm = quarters.get(month)
            if quarter_mm:
                start_mm_dd, end_mm_dd = quarter_mm
                return (f'{year}-{start_mm_dd}', f'{year}-{end_mm_dd}')

    raise ValueError(f"Invalid period format: {period}")


def generate_months(start_date: str, end_date: Optional[str]) -> List[str]:
    """
    Generate list of month strings from date range

    Args:
        start_date: ISO date string (YYYY-MM-DD)
        end_date: ISO date string (YYYY-MM-DD) or None for current month

    Returns:
        List of month strings ['2025-01', '2025-02', ...]

    Examples:
        >>> generate_months('2025-01-15', '2025-03-20')
        ['2025-01', '2025-02', '2025-03']

        >>> generate_months('2024-11-01', '2025-02-15')
        ['2024-11', '2024-12', '2025-01', '2025-02']
    """
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d') if end_date else datetime.now()

    months = []
    current = start
    while current <= end:
        months.append(current.strftime('%Y-%m'))
        current = add_months(current, 1)

    return months


__all__ = [
    'add_months',
    'parse_period',
    'generate_months',
    'DATA_START_DATE',
]
