from datetime import datetime
from typing import Tuple, Optional


def get_year_range(years: int) -> Tuple[int, int]:
    end_year = datetime.now().year
    start_year = end_year - years
    return start_year, end_year


def validate_years(years: int) -> bool:
    return 1 <= years <= 5


def parse_year(year_value: any) -> Optional[int]:
    if isinstance(year_value, int):
        return year_value

    if isinstance(year_value, str):
        year_str = year_value.strip()
        if year_str.isdigit():
            try:
                return int(year_str)
            except ValueError:
                pass

    return None


def is_year_in_range(year: int, start_year: int, end_year: int) -> bool:
    return start_year <= year <= end_year


def format_year_range(start_year: int, end_year: int) -> str:
    return f"{start_year}-{end_year}"


def get_current_year() -> int:
    return datetime.now().year
