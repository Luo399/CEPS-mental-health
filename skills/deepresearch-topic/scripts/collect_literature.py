"""
Phase 1: Literature Collection Engine
Specialized for social science/management literature from Chinese and English top journals.
"""

import json
import argparse
import sys
import os
from datetime import datetime

# Add utils to path
sys.path.insert(0, os.path.dirname(__file__))

from utils.api_clients.openalex_client import search_papers, search_by_concept, SOCIAL_SCIENCE_CONCEPTS
from utils.api_clients.semantic_scholar_client import search_papers as ss_search


# Chinese social science top journal ISSNs
CHINESE_JOURNAL_ISSNS = [
    "1002-5502",  # 管理世界
    "1007-9807",  # 管理科学学报
    "1008-3448",  # 南开管理评论
    "1003-207X",  # 中国管理科学
    "1672-884X",  # 管理学报
    "1006-480X",  # 中国工业经济
    "1001-4950",  # 外国经济与管理
    "1002-5766",  # 经济管理
    "0577-9154",  # 经济研究
    "1002-4921",  # 中国社会科学
    "1002-7246",  # 金融研究
    "1003-2886",  # 会计研究
    "1672-6162",  # 公共管理学报
    "1006-0863",  # 中国行政管理
    "1002-5936",  # 社会学研究
    "1003-2053",  # 科学学研究
    "1000-2995",  # 科研管理
]

# English management top journal ISSNs
ENGLISH_JOURNAL_ISSNS = [
    "0001-4273",  # AMJ
    "0363-7425",  # AMR
    "0143-2095",  # SMJ
    "0001-8392",  # ASQ
    "0022-2380",  # JMS
    "0025-1909",  # Management Science
    "0021-9010",  # JAP
    "0749-5978",  # OBHDP
    "0883-9026",  # JBV
    "0048-7333",  # Research Policy
    "0276-7783",  # MIS Quarterly
    "1047-7047",  # ISR
    "1059-1478",  # POM
    "0022-2429",  # JM
    "0093-5301",  # JCR
]


def collect_from_openalex_zh(domain: str, years: int, max_results: int) -> list:
    """Collect Chinese-language papers from OpenAlex."""
    year_end = datetime.now().year
    year_start = year_end - years

    print(f"[OpenAlex-ZH] Searching: {domain} ({year_start}-{year_end})")
    papers = search_papers(
        query=domain,
        year_start=year_start,
        year_end=year_end,
        language="zh",
        journal_issns=CHINESE_JOURNAL_ISSNS,
        max_results=max_results,
    )
    print(f"[OpenAlex-ZH] Found {len(papers)} Chinese papers")
    return papers


def collect_from_openalex_en(domain: str, years: int, max_results: int) -> list:
    """Collect English-language papers from OpenAlex."""
    year_end = datetime.now().year
    year_start = year_end - years

    # Try English translation of domain
    print(f"[OpenAlex-EN] Searching: {domain} ({year_start}-{year_end})")
    papers = search_papers(
        query=domain,
        year_start=year_start,
        year_end=year_end,
        language="en",
        journal_issns=ENGLISH_JOURNAL_ISSNS,
        max_results=max_results,
    )
    print(f"[OpenAlex-EN] Found {len(papers)} English papers")
    return papers


def collect_from_semantic_scholar(domain: str, years: int, max_results: int,
                                  api_key: str = None) -> list:
    """Collect papers from Semantic Scholar for citation graph data."""
    year_end = datetime.now().year
    year_start = year_end - years

    print(f"[Semantic Scholar] Searching: {domain}")
    papers = ss_search(
        query=domain,
        year_start=year_start,
        year_end=year_end,
        fields_of_study=["Business", "Economics", "Sociology"],
        max_results=max_results,
        api_key=api_key,
    )
    print(f"[Semantic Scholar] Found {len(papers)} papers")
    return papers


def collect_from_local_file(file_path: str) -> list:
    """Load papers from a local BibTeX/RIS/CSV/JSON file."""
    ext = os.path.splitext(file_path)[1].lower()
    papers = []

    if ext == ".json":
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            papers = data
        elif isinstance(data, dict) and "literature" in data:
            papers = data["literature"]
    elif ext == ".bib":
        try:
            import bibtexparser
            with open(file_path, "r", encoding="utf-8") as f:
                bib_db = bibtexparser.load(f)
            for entry in bib_db.entries:
                papers.append({
                    "title": entry.get("title", ""),
                    "authors": entry.get("author", "").split(" and "),
                    "journal": entry.get("journal", ""),
                    "year": int(entry.get("year", 0)) if entry.get("year") else None,
                    "doi": entry.get("doi", ""),
                    "abstract": entry.get("abstract", ""),
                    "keywords": entry.get("keywords", "").split(","),
                    "source_db": "local_file",
                    "language": "unknown",
                })
        except ImportError:
            print("[Warning] bibtexparser not installed. Install with: pip install bibtexparser")
    else:
        print(f"[Warning] Unsupported file format: {ext}")

    print(f"[Local] Loaded {len(papers)} papers from {file_path}")
    return papers


def merge_and_deduplicate(all_papers: list) -> list:
    """Merge papers from multiple sources and deduplicate."""
    seen_dois = set()
    seen_titles = set()
    unique = []

    for paper in all_papers:
        # Dedup by DOI
        doi = paper.get("doi", "").lower().strip()
        if doi and doi in seen_dois:
            continue

        # Dedup by title (normalized)
        title = paper.get("title", "").lower().strip()
        title_normalized = "".join(c for c in title if c.isalnum())
        if title_normalized in seen_titles:
            continue

        if doi:
            seen_dois.add(doi)
        if title_normalized:
            seen_titles.add(title_normalized)

        unique.append(paper)

    return unique


def filter_by_quality(papers: list, min_citations_config: dict = None) -> list:
    """Filter papers by age-adjusted citation thresholds."""
    current_year = datetime.now().year

    if min_citations_config is None:
        min_citations_config = {
            1: 3, 2: 8, 3: 15, 5: 25
        }

    filtered = []
    for paper in papers:
        year = paper.get("year")
        citations = paper.get("citations", 0)

        if not year:
            filtered.append(paper)
            continue

        age = current_year - year
        # Find applicable threshold
        threshold = 0
        for threshold_age, threshold_cit in sorted(min_citations_config.items()):
            if age <= threshold_age:
                threshold = threshold_cit
                break
        else:
            threshold = min_citations_config.get(5, 25)

        if citations >= threshold:
            filtered.append(paper)

    return filtered


def main(domain: str, years: int = 5, max_results: int = 200,
         sources: str = "openalex_zh,openalex_en,semantic_scholar",
         local_file: str = None, output_file: str = None,
         ss_api_key: str = None):
    """Main collection pipeline.

    Args:
        domain: Research domain (e.g., "数字化转型" or "digital transformation")
        years: Number of years to search back
        max_results: Max results per source
        sources: Comma-separated source list
        local_file: Optional local file path
        output_file: Output JSON file path
        ss_api_key: Semantic Scholar API key
    """
    source_list = [s.strip() for s in sources.split(",")]
    all_papers = []

    if "openalex_zh" in source_list:
        papers = collect_from_openalex_zh(domain, years, max_results)
        all_papers.extend(papers)

    if "openalex_en" in source_list:
        papers = collect_from_openalex_en(domain, years, max_results)
        all_papers.extend(papers)

    if "semantic_scholar" in source_list:
        papers = collect_from_semantic_scholar(domain, years, max_results, ss_api_key)
        all_papers.extend(papers)

    if local_file and "file" in source_list:
        papers = collect_from_local_file(local_file)
        all_papers.extend(papers)

    # Merge and deduplicate
    print(f"\n[Merge] Total before dedup: {len(all_papers)}")
    unique_papers = merge_and_deduplicate(all_papers)
    print(f"[Merge] After dedup: {len(unique_papers)}")

    # Quality filter
    filtered_papers = filter_by_quality(unique_papers)
    print(f"[Filter] After quality filter: {len(filtered_papers)}")

    # Statistics
    zh_count = sum(1 for p in filtered_papers if p.get("language") == "zh")
    en_count = sum(1 for p in filtered_papers if p.get("language") == "en")
    other_count = len(filtered_papers) - zh_count - en_count

    # Year distribution
    year_dist = {}
    for p in filtered_papers:
        year = p.get("year")
        if year:
            year_dist[year] = year_dist.get(year, 0) + 1

    result = {
        "search_metadata": {
            "domain": domain,
            "time_range": [datetime.now().year - years, datetime.now().year],
            "sources_used": source_list,
            "collection_timestamp": datetime.now().isoformat(),
        },
        "papers": filtered_papers,
        "stats": {
            "total_papers": len(filtered_papers),
            "chinese_papers": zh_count,
            "english_papers": en_count,
            "other_language_papers": other_count,
            "by_source": {},
            "by_year": year_dist,
        },
    }

    # Source distribution
    for p in filtered_papers:
        src = p.get("source_db", "unknown")
        result["stats"]["by_source"][src] = result["stats"]["by_source"].get(src, 0) + 1

    # Output
    if output_file:
        os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n[Output] Saved to {output_file}")

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phase 1: Literature Collection")
    parser.add_argument("--domain", required=True, help="Research domain")
    parser.add_argument("--years", type=int, default=5, help="Years to search back")
    parser.add_argument("--max_results", type=int, default=200, help="Max results per source")
    parser.add_argument("--sources", default="openalex_zh,openalex_en,semantic_scholar",
                        help="Comma-separated source list")
    parser.add_argument("--local_file", default=None, help="Local literature file")
    parser.add_argument("--output", default="phase1_literature.json", help="Output file")
    parser.add_argument("--ss_api_key", default=None, help="Semantic Scholar API key")

    args = parser.parse_args()
    main(args.domain, args.years, args.max_results, args.sources,
         args.local_file, args.output, args.ss_api_key)
