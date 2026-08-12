"""
Temporal trend detection and momentum scoring for research topics.
"""

from collections import defaultdict
import math


def compute_yearly_frequency(
    items: list,
    year_field: str = "year",
    year_range: tuple = None,
) -> dict:
    """Compute yearly frequency for items (keywords or topics).

    Args:
        items: List of dicts with year_field
        year_field: Key for year value
        year_range: Optional (start_year, end_year) tuple

    Returns:
        Dict mapping year -> count
    """
    freq = defaultdict(int)
    for item in items:
        year = item.get(year_field)
        if year is None:
            continue
        if year_range and (year < year_range[0] or year > year_range[1]):
            continue
        freq[year] += 1

    return dict(freq)


def detect_trend(frequency_series: dict) -> dict:
    """Detect trend using Mann-Kendall test and Sen's slope.

    Args:
        frequency_series: Dict mapping year -> count

    Returns:
        Dict with trend, slope, significance, direction
    """
    if len(frequency_series) < 3:
        return {
            "trend": "insufficient_data",
            "slope": 0,
            "significance": False,
            "direction": "unknown",
        }

    years = sorted(frequency_series.keys())
    values = [frequency_series[y] for y in years]
    n = len(values)

    # Mann-Kendall test
    s = 0
    for i in range(n - 1):
        for j in range(i + 1, n):
            diff = values[j] - values[i]
            if diff > 0:
                s += 1
            elif diff < 0:
                s -= 1

    # Variance of S
    unique_groups = defaultdict(int)
    for v in values:
        unique_groups[v] += 1
    g = len(unique_groups)

    var_s = (n * (n - 1) * (2 * n + 5)) / 18
    for group_size in unique_groups.values():
        var_s -= (group_size * (group_size - 1) * (2 * group_size + 5)) / 18

    # Z statistic
    if var_s > 0:
        if s > 0:
            z = (s - 1) / math.sqrt(var_s)
        elif s < 0:
            z = (s + 1) / math.sqrt(var_s)
        else:
            z = 0
    else:
        z = 0

    # Significance at alpha=0.05 (two-tailed)
    significance = abs(z) > 1.96

    # Sen's slope
    slopes = []
    for i in range(n - 1):
        for j in range(i + 1, n):
            if years[j] != years[i]:
                slopes.append((values[j] - values[i]) / (years[j] - years[i]))

    sen_slope = _median(slopes) if slopes else 0

    # Determine direction
    if significance:
        if sen_slope > 0.5:
            direction = "increasing"
        elif sen_slope < -0.5:
            direction = "decreasing"
        else:
            direction = "stable"
    else:
        direction = "stable"

    return {
        "trend": direction,
        "slope": round(sen_slope, 3),
        "z_statistic": round(z, 3),
        "significance": significance,
        "direction": direction,
        "mann_kendall_s": s,
    }


def classify_momentum(
    keyword: str,
    momentum_score: float,
    total_papers: int,
) -> str:
    """Classify a keyword/topic by momentum.

    Returns: 'emerging', 'rising', 'stable', or 'fading'
    """
    if momentum_score > 0.7 and total_papers < 50:
        return "emerging"
    elif momentum_score > 0.5 and total_papers >= 50:
        return "rising"
    elif 0.2 <= momentum_score <= 0.5:
        return "stable"
    else:
        return "fading"


def compute_momentum_score(
    keyword: str,
    frequency_series: dict,
    citation_data: list = None,
    current_year: int = 2026,
) -> dict:
    """Compute momentum score for a keyword or topic.

    momentum = 0.4 * growth_rate + 0.3 * recent_acceleration + 0.3 * citation_velocity

    Args:
        keyword: The keyword/topic name
        frequency_series: Dict mapping year -> count
        citation_data: Optional list of citation counts for recent papers
        current_year: Current year for calculations

    Returns:
        Dict with momentum_score, components, and classification
    """
    years = sorted(frequency_series.keys())
    values = [frequency_series[y] for y in years]

    if len(years) < 2:
        return {
            "keyword": keyword,
            "momentum_score": 0,
            "growth_rate": 0,
            "recent_acceleration": 0,
            "citation_velocity": 0,
            "classification": "insufficient_data",
            "total_papers": sum(values),
        }

    # Growth rate: Sen's slope / mean frequency
    trend = detect_trend(frequency_series)
    mean_freq = sum(values) / len(values) if values else 1
    normalized_growth = abs(trend["slope"]) / mean_freq if mean_freq > 0 else 0
    # Normalize to 0-1 range
    growth_rate = min(normalized_growth / 2.0, 1.0)

    # Recent acceleration
    recent_years = [y for y in years if y >= current_year - 2]
    prev_years = [y for y in years if current_year - 5 <= y < current_year - 2]

    recent_avg = sum(frequency_series.get(y, 0) for y in recent_years) / max(len(recent_years), 1)
    prev_avg = sum(frequency_series.get(y, 0) for y in prev_years) / max(len(prev_years), 1)

    if prev_avg > 0:
        recent_acceleration = min((recent_avg - prev_avg) / prev_avg, 2.0) / 2.0
    elif recent_avg > 0:
        recent_acceleration = 1.0  # New topic with recent activity
    else:
        recent_acceleration = 0

    # Citation velocity
    if citation_data:
        avg_citations = sum(citation_data) / len(citation_data)
        citation_velocity = min(avg_citations / 20.0, 1.0)  # Normalize
    else:
        citation_velocity = growth_rate * 0.5  # Estimate from growth

    # Composite momentum score
    momentum = 0.4 * growth_rate + 0.3 * recent_acceleration + 0.3 * citation_velocity

    total_papers = sum(values)
    classification = classify_momentum(keyword, momentum, total_papers)

    return {
        "keyword": keyword,
        "momentum_score": round(momentum, 3),
        "growth_rate": round(growth_rate, 3),
        "recent_acceleration": round(recent_acceleration, 3),
        "citation_velocity": round(citation_velocity, 3),
        "classification": classification,
        "total_papers": total_papers,
        "trend": trend["direction"],
        "sen_slope": trend["slope"],
    }


def compute_all_momentum(
    keyword_yearly: dict,
    keyword_citations: dict = None,
    current_year: int = 2026,
) -> list:
    """Compute momentum scores for all keywords.

    Args:
        keyword_yearly: Dict mapping keyword -> {year: count}
        keyword_citations: Dict mapping keyword -> [citation_counts]

    Returns:
        List of momentum score dicts, sorted by momentum descending
    """
    results = []

    for keyword, yearly_freq in keyword_yearly.items():
        cit_data = keyword_citations.get(keyword) if keyword_citations else None
        result = compute_momentum_score(keyword, yearly_freq, cit_data, current_year)
        results.append(result)

    results.sort(key=lambda x: x["momentum_score"], reverse=True)
    return results


def _median(values: list) -> float:
    """Compute median of a list of numbers."""
    if not values:
        return 0
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    if n % 2 == 1:
        return sorted_vals[n // 2]
    return (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2
