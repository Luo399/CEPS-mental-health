"""
Research gap identification across six gap types.
"""

from collections import defaultdict, Counter


def detect_centrality_density_gap(
    centrality: dict,
    network: dict,
    percentile_central: float = 75,
    percentile_density: float = 25,
) -> list:
    """Detect high betweenness + low density keywords.

    These keywords bridge research areas but their local neighborhood
    is sparse, meaning integration is underexplored.

    Args:
        centrality: Output from network_analysis.compute_centrality
        network: Co-occurrence network data
        percentile_central: Threshold percentile for betweenness centrality
        percentile_density: Threshold percentile for clustering coefficient

    Returns:
        List of gap dicts
    """
    if not centrality:
        return []

    # Compute betweenness percentiles
    betweenness_values = sorted([v["betweenness"] for v in centrality.values()])
    degree_values = sorted([v["degree"] for v in centrality.values()])

    n = len(betweenness_values)
    if n < 4:
        return []

    p75_idx = int(n * percentile_central / 100)
    p25_idx = int(n * percentile_density / 100)

    threshold_betweenness = betweenness_values[min(p75_idx, n-1)]
    threshold_degree = degree_values[min(p25_idx, n-1)]

    # Build local adjacency for clustering coefficient
    adj = defaultdict(set)
    for edge in network.get("edges", []):
        adj[edge["source"]].add(edge["target"])
        adj[edge["target"]].add(edge["source"])

    gaps = []
    for kw, metrics in centrality.items():
        if metrics["betweenness"] >= threshold_betweenness:
            # Compute local clustering coefficient
            neighbors = adj[kw]
            if len(neighbors) < 2:
                local_cc = 0
            else:
                possible_edges = len(neighbors) * (len(neighbors) - 1) / 2
                actual_edges = 0
                for n1 in neighbors:
                    for n2 in neighbors:
                        if n2 in adj[n1]:
                            actual_edges += 1
                actual_edges /= 2  # Each edge counted twice
                local_cc = actual_edges / possible_edges if possible_edges > 0 else 0

            if local_cc <= 0.3:  # Low local density
                gaps.append({
                    "gap_type": "high_centrality_low_density",
                    "keyword": kw,
                    "betweenness": metrics["betweenness"],
                    "local_clustering_coefficient": round(local_cc, 3),
                    "degree": metrics["degree"],
                    "evidence": (
                        f"'{kw}'的中介中心度={metrics['betweenness']:.3f}（>P{percentile_central}），"
                        f"局部聚类系数={local_cc:.3f}（低密度），"
                        f"表明其连接不同研究流但整合研究不足"
                    ),
                    "opportunity_type": "跨领域整合选题",
                })

    gaps.sort(key=lambda x: x["betweenness"], reverse=True)
    return gaps


def detect_theory_method_gap(
    papers: list,
    clusters: list,
    ratio_threshold: float = 3.0,
) -> list:
    """Detect theory-method imbalances within clusters.

    Clusters with theory/qualitative >> empirical quantitative (or vice versa)
    reveal opportunities for methodological or theoretical contribution.

    Args:
        papers: List of paper dicts with 'method_type' field
        clusters: List of cluster dicts with 'paper_ids' field
        ratio_threshold: Imbalance ratio threshold

    Returns:
        List of gap dicts
    """
    if not papers or not clusters:
        return []

    paper_map = {p.get("id"): p for p in papers}
    gaps = []

    for cluster in clusters:
        paper_ids = cluster.get("paper_ids", [])
        cluster_papers = [paper_map[pid] for pid in paper_ids if pid in paper_map]

        if len(cluster_papers) < 5:
            continue

        # Count methodology types
        method_counts = Counter()
        for p in cluster_papers:
            method = p.get("method_type", "unknown")
            method_counts[method] += 1

        theoretical = (method_counts.get("theoretical", 0) +
                       method_counts.get("review", 0))
        empirical_qual = method_counts.get("empirical_qualitative", 0)
        empirical_quant = method_counts.get("empirical_quantitative", 0)

        theory_heavy = theoretical + empirical_qual
        method_heavy = empirical_quant

        if theory_heavy > 0 and method_heavy > 0:
            ratio = theory_heavy / method_heavy
        elif theory_heavy > 0:
            ratio = float("inf")
        elif method_heavy > 0:
            ratio = 0
        else:
            continue

        gap = None
        if ratio >= ratio_threshold:
            gap = {
                "gap_type": "theory_method_gap",
                "cluster": cluster.get("name", ""),
                "theory_papers": theory_heavy,
                "empirical_papers": method_heavy,
                "ratio": round(ratio, 2),
                "direction": "needs_empirical",
                "evidence": (
                    f"聚类'{cluster.get('name', '')}'中理论/定性论文{theory_heavy}篇，"
                    f"实证定量论文仅{method_heavy}篇（比例{ratio:.1f}:1），"
                    f"亟需实证检验"
                ),
                "opportunity_type": "方法论贡献选题",
            }
        elif ratio <= 1 / ratio_threshold:
            gap = {
                "gap_type": "theory_method_gap",
                "cluster": cluster.get("name", ""),
                "theory_papers": theory_heavy,
                "empirical_papers": method_heavy,
                "ratio": round(ratio, 2),
                "direction": "needs_theory",
                "evidence": (
                    f"聚类'{cluster.get('name', '')}'中实证定量论文{method_heavy}篇，"
                    f"理论/定性论文仅{theory_heavy}篇（比例1:{1/ratio:.1f}），"
                    f"缺乏理论框架支撑"
                ),
                "opportunity_type": "理论建构选题",
            }

        if gap:
            gaps.append(gap)

    return gaps


def detect_rising_sparse_gap(
    momentum_results: list,
    keyword_frequencies: dict,
    paper_limit: int = 30,
    momentum_threshold: float = 0.7,
) -> list:
    """Detect keywords with high momentum but few papers.

    These are gaining attention but remain underexplored.

    Args:
        momentum_results: Output from trend_analysis.compute_all_momentum
        keyword_frequencies: Dict mapping keyword -> total paper count
        paper_limit: Maximum papers for "sparse" classification
        momentum_threshold: Minimum momentum score

    Returns:
        List of gap dicts
    """
    gaps = []

    for result in momentum_results:
        keyword = result["keyword"]
        momentum = result["momentum_score"]
        total = result.get("total_papers", keyword_frequencies.get(keyword, 0))

        if momentum > momentum_threshold and total < paper_limit:
            gaps.append({
                "gap_type": "rising_sparse",
                "keyword": keyword,
                "momentum_score": momentum,
                "total_papers": total,
                "classification": result.get("classification", ""),
                "evidence": (
                    f"'{keyword}'的动量评分={momentum:.2f}（>0.7），"
                    f"但仅有{total}篇论文，属于高增长-低文献空白"
                ),
                "opportunity_type": "前沿探索选题",
            })

    return gaps


def detect_cross_lingual_gap(
    chinese_keyword_freq: dict,
    english_keyword_freq: dict,
    unified_keywords: dict,
    ratio_threshold: float = 5.0,
) -> list:
    """Detect research topics prominent in one language but absent in another.

    Args:
        chinese_keyword_freq: Dict mapping keyword -> count (Chinese papers)
        english_keyword_freq: Dict mapping keyword -> count (English papers)
        unified_keywords: Output from text_processing.build_unified_keyword_space
        ratio_threshold: Asymmetry ratio threshold

    Returns:
        List of gap dicts
    """
    gaps = []

    for canonical, variants in unified_keywords.items():
        zh_count = 0
        en_count = 0

        for variant in variants:
            zh_count += chinese_keyword_freq.get(variant, 0)
            en_count += english_keyword_freq.get(variant, 0)

        if zh_count == 0 and en_count == 0:
            continue

        if zh_count > 0 and en_count > 0:
            ratio = zh_count / en_count
        elif zh_count > 0:
            ratio = float("inf")
        else:
            ratio = 0

        if ratio >= ratio_threshold and zh_count >= 3:
            gaps.append({
                "gap_type": "cross_lingual",
                "keyword": canonical,
                "chinese_papers": zh_count,
                "english_papers": en_count,
                "ratio": f"{zh_count}:{en_count}",
                "direction": "zh_dominated",
                "evidence": (
                    f"'{canonical}'在中文文献中{zh_count}篇，英文文献中仅{en_count}篇，"
                    f"比例{zh_count}:{en_count}，属于中文主导的跨语言空白"
                ),
                "opportunity_type": "跨文化/跨制度选题（向国际推广）",
            })
        elif ratio <= 1 / ratio_threshold and en_count >= 3:
            gaps.append({
                "gap_type": "cross_lingual",
                "keyword": canonical,
                "chinese_papers": zh_count,
                "english_papers": en_count,
                "ratio": f"{zh_count}:{en_count}",
                "direction": "en_dominated",
                "evidence": (
                    f"'{canonical}'在英文文献中{en_count}篇，中文文献中仅{zh_count}篇，"
                    f"比例{zh_count}:{en_count}，属于英文主导的跨语言空白"
                ),
                "opportunity_type": "跨文化/跨制度选题（在中国情境验证）",
            })

    gaps.sort(key=lambda x: max(x["chinese_papers"], x["english_papers"]), reverse=True)
    return gaps


def detect_citation_stagnation_gap(
    papers: list,
    clusters: list,
    ref_age_threshold: int = 8,
    declining_recent: bool = True,
) -> list:
    """Detect mature but stagnating research areas.

    Areas where foundational work is heavily cited but few new
    contributions emerge.

    Args:
        papers: List of paper dicts
        clusters: List of cluster dicts
        ref_age_threshold: Average reference age threshold (years)
        declining_recent: Whether to check for declining recent output

    Returns:
        List of gap dicts
    """
    gaps = []

    for cluster in clusters:
        cluster_papers = [p for p in papers if cluster.get("name") in p.get("themes", [])]

        if len(cluster_papers) < 5:
            continue

        # Estimate average reference age from paper years
        # (Simplified: use age of papers themselves as proxy)
        years = [p.get("year", 2020) for p in cluster_papers if p.get("year")]
        if len(years) < 3:
            continue

        current_year = max(years) if years else 2026
        avg_age = current_year - (sum(years) / len(years))

        # Check for declining recent output
        recent_count = len([y for y in years if y >= current_year - 2])
        prev_count = len([y for y in years if current_year - 5 <= y < current_year - 2])
        recent_avg = recent_count / 2 if recent_count else 0
        prev_avg = prev_count / 3 if prev_count else 0

        is_declining = recent_avg < prev_avg * 0.8 if prev_avg > 0 else False

        if avg_age > ref_age_threshold and is_declining:
            gaps.append({
                "gap_type": "citation_stagnation",
                "cluster": cluster.get("name", ""),
                "avg_reference_age": round(avg_age, 1),
                "recent_papers": recent_count,
                "prev_period_papers": prev_count,
                "evidence": (
                    f"聚类'{cluster.get('name', '')}'平均文献年龄{avg_age:.1f}年（>{ref_age_threshold}年），"
                    f"近期发文量下降（近2年{recent_count}篇 vs 前3年{prev_count}篇），"
                    f"属于引用停滞空白"
                ),
                "opportunity_type": "理论刷新选题",
            })

    return gaps


def detect_practical_gap(
    papers: list,
    clusters: list,
    theory_ratio_threshold: float = 0.6,
) -> list:
    """Detect clusters with predominantly theoretical/conceptual papers.

    These areas need empirical validation and practical application studies.

    Args:
        papers: List of paper dicts with 'method_type' field
        clusters: List of cluster dicts
        theory_ratio_threshold: Ratio of theoretical papers for gap

    Returns:
        List of gap dicts
    """
    paper_map = {p.get("id"): p for p in papers}
    gaps = []

    for cluster in clusters:
        paper_ids = cluster.get("paper_ids", [])
        cluster_papers = [paper_map[pid] for pid in paper_ids if pid in paper_map]

        if len(cluster_papers) < 5:
            continue

        theoretical_count = 0
        for p in cluster_papers:
            method = p.get("method_type", "unknown")
            if method in ("theoretical", "review", "empirical_qualitative"):
                theoretical_count += 1

        theory_ratio = theoretical_count / len(cluster_papers)

        if theory_ratio > theory_ratio_threshold:
            gaps.append({
                "gap_type": "practical_problem",
                "cluster": cluster.get("name", ""),
                "theory_ratio": round(theory_ratio, 2),
                "total_papers": len(cluster_papers),
                "theoretical_papers": theoretical_count,
                "evidence": (
                    f"聚类'{cluster.get('name', '')}'中{theory_ratio:.0%}的论文为"
                    f"理论/概念/定性研究，缺乏实证应用验证，属于实践问题空白"
                ),
                "opportunity_type": "应用验证选题",
            })

    return gaps


def synthesize_gaps(all_gaps: list) -> list:
    """Deduplicate, rank, and synthesize across gap types.

    Args:
        all_gaps: Combined list from all six gap detectors

    Returns:
        Ranked list of gap dicts with composite scoring
    """
    if not all_gaps:
        return []

    # Score each gap by type priority and evidence strength
    type_priority = {
        "high_centrality_low_density": 5,
        "rising_sparse": 4,
        "cross_lingual": 4,
        "theory_method_gap": 3,
        "citation_stagnation": 2,
        "practical_problem": 2,
    }

    scored_gaps = []
    for gap in all_gaps:
        priority = type_priority.get(gap["gap_type"], 1)

        # Evidence strength based on available metrics
        evidence_score = 1.0
        if gap.get("betweenness"):
            evidence_score *= min(gap["betweenness"] * 5, 2.0)
        if gap.get("momentum_score"):
            evidence_score *= min(gap["momentum_score"] + 0.5, 2.0)
        if gap.get("total_papers"):
            evidence_score *= min(1.0, 5.0 / max(gap["total_papers"], 1))

        scored_gaps.append({
            **gap,
            "priority": priority,
            "evidence_score": round(evidence_score, 2),
            "composite_gap_score": round(priority * evidence_score, 2),
        })

    scored_gaps.sort(key=lambda x: x["composite_gap_score"], reverse=True)

    # Deduplicate: if same keyword appears in multiple gap types, keep highest score
    seen_keywords = set()
    unique_gaps = []
    for gap in scored_gaps:
        key = (gap.get("keyword") or gap.get("cluster"), gap["gap_type"])
        if key not in seen_keywords:
            seen_keywords.add(key)
            unique_gaps.append(gap)

    return unique_gaps
