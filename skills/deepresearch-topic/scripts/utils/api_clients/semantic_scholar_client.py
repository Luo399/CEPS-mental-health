"""
Semantic Scholar API client for citation graph enrichment.
"""

import requests
import time
import json
from typing import Optional


BASE_URL = "https://api.semanticscholar.org/graph/v1"

PAPER_FIELDS = "paperId,title,year,abstract,citationCount,referenceCount,authors,venue,externalIds,fieldsOfStudy,citations,references"


def search_papers(
    query: str,
    year_start: int = 2021,
    year_end: int = 2026,
    fields_of_study: Optional[list] = None,
    max_results: int = 100,
    api_key: Optional[str] = None,
) -> list:
    """Search papers on Semantic Scholar.

    Args:
        query: Search terms
        year_start: Start year
        year_end: End year
        fields_of_study: e.g. ["Business", "Economics", "Sociology"]
        max_results: Maximum results
        api_key: Optional API key for higher rate limits

    Returns:
        List of paper dictionaries
    """
    papers = []
    offset = 0
    limit = min(100, max_results)

    headers = {}
    if api_key:
        headers["x-api-key"] = api_key

    while len(papers) < max_results:
        params = {
            "query": query,
            "limit": limit,
            "offset": offset,
            "fields": "paperId,title,year,abstract,citationCount,referenceCount,authors,venue,externalIds,fieldsOfStudy",
            "year": f"{year_start}-{year_end}",
        }

        if fields_of_study:
            params["fieldsOfStudy"] = ",".join(fields_of_study)

        try:
            resp = requests.get(
                f"{BASE_URL}/paper/search",
                params=params,
                headers=headers,
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
        except (requests.RequestException, json.JSONDecodeError) as e:
            print(f"Semantic Scholar API error: {e}")
            break

        results = data.get("data", [])
        if not results:
            break

        for paper_data in results:
            paper = _parse_paper(paper_data)
            if paper:
                papers.append(paper)

        if data.get("next"):
            offset = data["next"]
        else:
            break

        time.sleep(1.0)  # Rate limiting: 1 req/sec without key

    return papers[:max_results]


def get_citations(
    paper_id: str,
    api_key: Optional[str] = None,
) -> list:
    """Get papers that cite this paper (forward citations).

    Args:
        paper_id: Semantic Scholar paper ID or DOI
        api_key: Optional API key

    Returns:
        List of citing paper IDs
    """
    headers = {}
    if api_key:
        headers["x-api-key"] = api_key

    citing_ids = []
    offset = 0

    while True:
        params = {
            "fields": "paperId,title,year,citationCount",
            "limit": 100,
            "offset": offset,
        }

        try:
            resp = requests.get(
                f"{BASE_URL}/paper/{paper_id}/citations",
                params=params,
                headers=headers,
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
        except (requests.RequestException, json.JSONDecodeError):
            break

        citations = data.get("data", [])
        if not citations:
            break

        for cit in citations:
            citing_paper = cit.get("citingPaper", {})
            if citing_paper.get("paperId"):
                citing_ids.append(citing_paper["paperId"])

        if data.get("next"):
            offset = data["next"]
        else:
            break

        time.sleep(1.0)

    return citing_ids


def get_references(
    paper_id: str,
    api_key: Optional[str] = None,
) -> list:
    """Get this paper's references (backward citations).

    Args:
        paper_id: Semantic Scholar paper ID or DOI
        api_key: Optional API key

    Returns:
        List of referenced paper IDs
    """
    headers = {}
    if api_key:
        headers["x-api-key"] = api_key

    ref_ids = []
    offset = 0

    while True:
        params = {
            "fields": "paperId",
            "limit": 100,
            "offset": offset,
        }

        try:
            resp = requests.get(
                f"{BASE_URL}/paper/{paper_id}/references",
                params=params,
                headers=headers,
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
        except (requests.RequestException, json.JSONDecodeError):
            break

        refs = data.get("data", [])
        if not refs:
            break

        for ref in refs:
            cited_paper = ref.get("citedPaper", {})
            if cited_paper.get("paperId"):
                ref_ids.append(cited_paper["paperId"])

        if data.get("next"):
            offset = data["next"]
        else:
            break

        time.sleep(1.0)

    return ref_ids


def get_paper_batch(
    paper_ids: list,
    api_key: Optional[str] = None,
) -> list:
    """Batch retrieval of paper details.

    Args:
        paper_ids: List of Semantic Scholar paper IDs (max 500)
        api_key: Optional API key

    Returns:
        List of paper dictionaries
    """
    if not paper_ids:
        return []

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["x-api-key"] = api_key

    batch = paper_ids[:500]
    papers = []

    try:
        resp = requests.post(
            f"{BASE_URL}/paper/batch",
            params={"fields": "paperId,title,year,citationCount,authors,venue,externalIds"},
            headers=headers,
            json={"ids": batch},
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()

        for paper_data in data:
            if paper_data:
                paper = _parse_paper(paper_data)
                if paper:
                    papers.append(paper)

    except (requests.RequestException, json.JSONDecodeError) as e:
        print(f"Semantic Scholar batch API error: {e}")

    return papers


def _parse_paper(paper_data: dict) -> Optional[dict]:
    """Parse a Semantic Scholar paper result."""
    if not paper_data or not paper_data.get("paperId"):
        return None

    # Extract DOI
    ext_ids = paper_data.get("externalIds", {})
    doi = ext_ids.get("DOI", "")

    # Extract authors
    authors = []
    for a in (paper_data.get("authors") or [])[:10]:
        name = a.get("name", "")
        if name:
            authors.append(name)

    return {
        "id": paper_data.get("paperId", ""),
        "title": paper_data.get("title", ""),
        "authors": authors,
        "journal": paper_data.get("venue", ""),
        "year": paper_data.get("year"),
        "doi": doi,
        "abstract": paper_data.get("abstract", "") or "",
        "citations": paper_data.get("citationCount", 0) or 0,
        "keywords": [],
        "language": "en",  # Semantic Scholar is predominantly English
        "source_db": "semantic_scholar",
        "url": f"https://www.semanticscholar.org/paper/{paper_data['paperId']}",
        "references_count": paper_data.get("referenceCount", 0) or 0,
        "fields_of_study": paper_data.get("fieldsOfStudy", []),
    }
