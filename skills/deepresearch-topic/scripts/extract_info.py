"""
Phase 2: Information Extraction
Extract structured data from collected papers.
"""

import json
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from utils.text_processing import (
    segment_chinese,
    normalize_keyword,
    find_synonym_group,
    build_unified_keyword_space,
    extract_keywords_tfidf,
    classify_methodology,
)


def extract_info(papers: list) -> dict:
    """Extract structured information from papers.

    Args:
        papers: List of paper dicts from Phase 1

    Returns:
        Dict with processed papers, keyword registry, and citation graph
    """
    processed_papers = []
    all_keywords = []
    citation_adj = {}

    for i, paper in enumerate(papers):
        # Normalize keywords
        raw_keywords = paper.get("keywords", [])
        normalized = [normalize_keyword(kw) for kw in raw_keywords if kw]
        normalized = [kw for kw in normalized if len(kw) > 1]

        # If no keywords, try extracting from abstract
        if not normalized and paper.get("abstract"):
            abstract = paper["abstract"]
            if any("一" <= c <= "鿿" for c in abstract):
                extracted = segment_chinese(abstract)
                normalized = [kw for kw in extracted if len(kw) >= 2][:8]
            else:
                # TF-IDF will be done in batch later
                normalized = []

        all_keywords.extend(normalized)

        # Classify methodology
        method_type = classify_methodology(paper.get("abstract", ""))

        # Build citation links
        ref_works = paper.get("referenced_works", [])
        paper_id = paper.get("id") or paper.get("doi") or f"paper_{i}"
        if ref_works:
            citation_adj[paper_id] = ref_works

        processed = {
            **paper,
            "normalized_keywords": normalized,
            "method_type": method_type,
            "themes": [],  # Will be assigned after clustering
            "citation_links": ref_works,
        }
        processed_papers.append(processed)

    # Batch TF-IDF for papers without keywords
    papers_without_kw = [p for p in processed_papers if not p["normalized_keywords"]]
    if papers_without_kw:
        abstracts = [p.get("abstract", "") for p in papers_without_kw]
        tfidf_keywords = extract_keywords_tfidf(abstracts, top_n=8)
        # Distribute keywords (simplified: assign top keywords to papers)
        for p in papers_without_kw:
            if p.get("abstract"):
                abstract = p["abstract"]
                kw_scores = []
                for kw, score in tfidf_keywords:
                    if kw.lower() in abstract.lower():
                        kw_scores.append(kw)
                p["normalized_keywords"] = kw_scores[:8]

    # Build keyword registry
    keyword_freq = {}
    for p in processed_papers:
        for kw in p["normalized_keywords"]:
            keyword_freq[kw] = keyword_freq.get(kw, 0) + 1

    # Build unified keyword space (Chinese-English synonym mapping)
    unique_keywords = list(keyword_freq.keys())
    unified_space = build_unified_keyword_space(unique_keywords)

    # Assign unified keywords to papers
    for p in processed_papers:
        unified_kws = []
        kw_weights = {}
        for kw in p["normalized_keywords"]:
            unified_kws.append(kw)
            # Find canonical form
            for canonical, variants in unified_space.items():
                if kw in variants:
                    unified_kws[-1] = canonical  # Replace with canonical
                    break
            kw_weights[unified_kws[-1]] = kw_weights.get(unified_kws[-1], 0) + 1

        p["normalized_keywords"] = list(set(unified_kws))
        p["keyword_weights"] = kw_weights

    return {
        "papers": processed_papers,
        "keyword_registry": {
            "all_keywords": unique_keywords,
            "keyword_frequency": keyword_freq,
            "unified_keyword_space": unified_space,
        },
        "citation_graph": citation_adj,
    }


def main(input_file: str, output_file: str = "phase2_extracted.json"):
    """Run Phase 2 extraction pipeline."""
    print(f"[Phase 2] Loading from {input_file}")
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    papers = data.get("papers", [])
    print(f"[Phase 2] Processing {len(papers)} papers")

    result = extract_info(papers)

    # Statistics
    method_dist = {}
    for p in result["papers"]:
        mt = p.get("method_type", "unknown")
        method_dist[mt] = method_dist.get(mt, 0) + 1

    n_with_kw = sum(1 for p in result["papers"] if p["normalized_keywords"])
    print(f"[Phase 2] Papers with keywords: {n_with_kw}/{len(papers)}")
    print(f"[Phase 2] Method distribution: {method_dist}")
    print(f"[Phase 2] Unique keywords: {len(result['keyword_registry']['keyword_frequency'])}")
    print(f"[Phase 2] Unified keyword groups: {len(result['keyword_registry']['unified_keyword_space'])}")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[Phase 2] Saved to {output_file}")

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phase 2: Information Extraction")
    parser.add_argument("--input", default="phase1_literature.json", help="Input file")
    parser.add_argument("--output", default="phase2_extracted.json", help="Output file")
    args = parser.parse_args()
    main(args.input, args.output)
