"""
OpenAlex API client for social science/management literature collection.
Specialized for Chinese and English management journals.
"""

import requests
import time
import json
from typing import Optional


BASE_URL = "https://api.openalex.org"

# Social science / management concept IDs in OpenAlex
SOCIAL_SCIENCE_CONCEPTS = {
    "management": "https://openalex.org/C144024400",
    "business": "https://openalex.org/C15744967",
    "economics": "https://openalex.org/C162324750",
    "sociology": "https://openalex.org/C144133560",
    "public_administration": "https://openalex.org/C17746579",
    "organizational_studies": "https://openalex.org/C186755401",
    "marketing": "https://openalex.org/C537208841",
    "finance": "https://openalex.org/C153968042",
}


def search_papers(
    query: str,
    year_start: int = 2021,
    year_end: int = 2026,
    language: Optional[str] = None,
    journal_issns: Optional[list] = None,
    max_results: int = 200,
    per_page: int = 50,
    email: Optional[str] = None,
) -> list:
    """Search papers on OpenAlex with social science filters.

    Args:
        query: Search terms (supports Chinese)
        year_start: Start year filter
        year_end: End year filter
        language: 'zh' for Chinese, 'en' for English, None for both
        journal_issns: List of journal ISSNs to filter
        max_results: Maximum number of results
        per_page: Results per page (max 200)
        email: Polite pool email for faster rate limits

    Returns:
        List of paper dictionaries
    """
    papers = []
    cursor = "*"

    headers = {}
    if email:
        headers["mailto"] = email

    filters = [f"from_publication_date:{year_start}-01-01",
               f"to_publication_date:{year_end}-12-31",
               "type:article"]

    if language:
        filters.append(f"language:{language}")

    if journal_issns:
        issn_filter = "|".join(journal_issns)
        filters.append(f"primary_location.source.issn:{issn_filter}")

    filter_str = ",".join(filters)

    while len(papers) < max_results:
        params = {
            "search": query,
            "filter": filter_str,
            "per_page": min(per_page, max_results - len(papers)),
            "cursor": cursor,
            "sort": "cited_by_count:desc",
        }

        try:
            resp = requests.get(
                f"{BASE_URL}/works",
                params=params,
                headers=headers,
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
        except (requests.RequestException, json.JSONDecodeError) as e:
            print(f"OpenAlex API error: {e}")
            break

        results = data.get("results", [])
        if not results:
            break

        for work in results:
            paper = _parse_work(work)
            if paper:
                papers.append(paper)

        cursor = data.get("meta", {}).get("next_cursor")
        if not cursor:
            break

        time.sleep(0.1)  # Rate limiting

    return papers[:max_results]


def search_by_concept(
    concept_id: str,
    query: str,
    year_start: int = 2021,
    year_end: int = 2026,
    language: Optional[str] = None,
    max_results: int = 100,
) -> list:
    """Search papers filtered by OpenAlex concept ID."""
    filters = [
        f"from_publication_date:{year_start}-01-01",
        f"to_publication_date:{year_end}-12-31",
        f"concepts.id:{concept_id}",
        "type:article",
    ]
    if language:
        filters.append(f"language:{language}")

    filter_str = ",".join(filters)

    papers = []
    cursor = "*"

    while len(papers) < max_results:
        params = {
            "search": query,
            "filter": filter_str,
            "per_page": min(50, max_results - len(papers)),
            "cursor": cursor,
            "sort": "cited_by_count:desc",
        }

        try:
            resp = requests.get(f"{BASE_URL}/works", params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except (requests.RequestException, json.JSONDecodeError):
            break

        results = data.get("results", [])
        if not results:
            break

        for work in results:
            paper = _parse_work(work)
            if paper:
                papers.append(paper)

        cursor = data.get("meta", {}).get("next_cursor")
        if not cursor:
            break

        time.sleep(0.1)

    return papers[:max_results]


def get_references(work_id: str) -> list:
    """Get referenced works (backward citations) for a paper."""
    try:
        resp = requests.get(
            f"{BASE_URL}/works/{work_id}",
            params={"select": "referenced_works"},
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json().get("referenced_works", [])
    except (requests.RequestException, json.JSONDecodeError):
        return []


def _parse_work(work: dict) -> Optional[dict]:
    """Parse an OpenAlex work result into standardized paper dict."""
    if not work:
        return None

    # Extract DOI
    doi = work.get("doi", "")
    if doi and doi.startswith("https://doi.org/"):
        doi = doi.replace("https://doi.org/", "")

    # Extract journal info
    primary_location = work.get("primary_location") or {}
    source = primary_location.get("source") or {}
    journal = source.get("display_name", "")
    issn = source.get("issn", [])
    issn_l = source.get("issn_l", "")

    # Extract year
    pub_date = work.get("publication_date", "")
    year = int(pub_date[:4]) if pub_date else None

    # Extract abstract (OpenAlex returns inverted index)
    abstract_inverted = work.get("abstract_inverted_index")
    abstract = _reconstruct_abstract(abstract_inverted)

    # Extract keywords/concepts
    concepts = work.get("concepts", [])
    keywords = [c.get("display_name", "") for c in concepts[:10]
                if c.get("score", 0) > 0.3]

    # Extract authors
    authorships = work.get("authorships", [])
    authors = []
    for a in authorships[:10]:
        author_name = a.get("author", {}).get("display_name", "")
        if author_name:
            authors.append(author_name)

    # Detect language
    language = work.get("language", "en")

    return {
        "id": work.get("id", ""),
        "title": work.get("title", ""),
        "authors": authors,
        "journal": journal,
        "journal_issn": issn,
        "journal_issn_l": issn_l,
        "year": year,
        "doi": doi,
        "abstract": abstract,
        "citations": work.get("cited_by_count", 0),
        "keywords": keywords,
        "language": language,
        "source_db": "openalex",
        "url": work.get("doi") or work.get("id", ""),
        "references_count": work.get("referenced_works_count", 0),
        "referenced_works": work.get("referenced_works", [])[:50],
    }


def _reconstruct_abstract(inverted_index: Optional[dict]) -> str:
    """Reconstruct abstract from OpenAlex inverted index format."""
    if not inverted_index:
        return ""

    word_positions = []
    for word, positions in inverted_index.items():
        for pos in positions:
            word_positions.append((pos, word))

    word_positions.sort()
    return " ".join(w for _, w in word_positions)
