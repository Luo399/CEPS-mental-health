"""
Phase 3-5: Topic Analysis, Gap Detection, and Research Topic Generation
Main orchestration script for the complete analysis pipeline.
"""

import json
import argparse
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from utils.network_analysis import (
    build_cooccurrence_matrix,
    compute_centrality,
    detect_communities,
    identify_bridge_keywords,
    compute_network_density,
)
from utils.clustering import lda_clustering, consensus_clustering
from utils.trend_analysis import compute_yearly_frequency, compute_all_momentum
from utils.gap_detector import (
    detect_centrality_density_gap,
    detect_theory_method_gap,
    detect_rising_sparse_gap,
    detect_cross_lingual_gap,
    detect_citation_stagnation_gap,
    detect_practical_gap,
    synthesize_gaps,
)
from utils.text_processing import segment_chinese, normalize_keyword


def load_config(config_path: str) -> dict:
    """Load analysis configuration."""
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_phase2_output(input_file: str) -> dict:
    """Load Phase 2 extraction output."""
    with open(input_file, "r", encoding="utf-8") as f:
        return json.load(f)


def run_topic_clustering(papers: list, config: dict) -> dict:
    """Phase 3: Topic clustering using LDA and network analysis."""
    print("[Phase 3] Running topic clustering...")

    # Extract keyword lists
    papers_keywords = [p.get("normalized_keywords", []) for p in papers]

    # LDA clustering
    lda_result = lda_clustering(
        papers_keywords,
        n_topics_range=tuple(config.get("analysis_settings", {}).get("lda_topics_range", [5, 15])),
        n_top_words=8,
    )

    # Build co-occurrence network
    network = build_cooccurrence_matrix(
        papers_keywords,
        min_cooccurrence=config.get("analysis_settings", {}).get("cooccurrence_min_frequency", 2),
        weighting="jaccard",
    )

    # Network-based clustering
    network_result = detect_communities(network, resolution=1.0)

    # Consensus clustering
    consensus_result = consensus_clustering(lda_result, network_result)

    print(f"[Phase 3] LDA topics: {lda_result.get('optimal_n_topics', 0)}")
    print(f"[Phase 3] Network communities: {network_result.get('n_communities', 0)}")
    print(f"[Phase 3] Consensus topics: {consensus_result.get('optimal_n_topics', 0)}")

    return {
        "lda_topics": lda_result,
        "network_topics": network_result,
        "consensus_topics": consensus_result,
        "cooccurrence_network": network,
    }


def run_trend_analysis(papers: list, clusters: dict, config: dict) -> dict:
    """Phase 4: Temporal trend analysis."""
    print("[Phase 4] Running trend analysis...")

    # Build keyword yearly frequency
    keyword_yearly = {}
    for p in papers:
        year = p.get("year")
        keywords = p.get("normalized_keywords", [])
        if not year or not keywords:
            continue
        for kw in keywords:
            if kw not in keyword_yearly:
                keyword_yearly[kw] = {}
            keyword_yearly[kw][year] = keyword_yearly[kw].get(year, 0) + 1

    # Compute momentum for all keywords
    momentum_results = compute_all_momentum(
        keyword_yearly,
        current_year=datetime.now().year,
    )

    # Identify emerging, rising, stable, and fading topics
    emerging = [m for m in momentum_results if m["classification"] == "emerging"][:10]
    rising = [m for m in momentum_results if m["classification"] == "rising"][:10]
    stable = [m for m in momentum_results if m["classification"] == "stable"][:10]
    fading = [m for m in momentum_results if m["classification"] == "fading"][:10]

    print(f"[Phase 4] Emerging: {len(emerging)}, Rising: {len(rising)}, "
          f"Stable: {len(stable)}, Fading: {len(fading)}")

    return {
        "keyword_momentum": momentum_results,
        "emerging_topics": emerging,
        "rising_topics": rising,
        "stable_topics": stable,
        "fading_topics": fading,
        "keyword_yearly_frequency": keyword_yearly,
    }


def run_gap_detection(
    papers: list,
    clusters: dict,
    network: dict,
    centrality: dict,
    trend_results: dict,
    keyword_registry: dict,
    config: dict,
) -> list:
    """Phase 5: Research gap detection across six gap types."""
    print("[Phase 5] Running gap detection...")

    gap_thresholds = config.get("analysis_settings", {}).get("gap_thresholds", {})
    all_gaps = []

    # 1. High centrality - Low density gaps
    centrality_gaps = detect_centrality_density_gap(
        centrality,
        network,
        percentile_central=gap_thresholds.get("centrality_percentile", 75),
        percentile_density=gap_thresholds.get("density_percentile", 25),
    )
    all_gaps.extend(centrality_gaps)
    print(f"[Phase 5] Centrality-density gaps: {len(centrality_gaps)}")

    # 2. Theory-method imbalance gaps
    theory_gaps = detect_theory_method_gap(
        papers,
        clusters.get("consensus_topics", {}).get("topics", []),
        ratio_threshold=gap_thresholds.get("method_ratio_threshold", 3.0),
    )
    all_gaps.extend(theory_gaps)
    print(f"[Phase 5] Theory-method gaps: {len(theory_gaps)}")

    # 3. Rising sparse gaps (high momentum, low papers)
    rising_gaps = detect_rising_sparse_gap(
        trend_results.get("keyword_momentum", []),
        keyword_registry.get("keyword_frequency", {}),
        paper_limit=gap_thresholds.get("rising_sparse_paper_limit", 30),
        momentum_threshold=0.7,
    )
    all_gaps.extend(rising_gaps)
    print(f"[Phase 5] Rising-sparse gaps: {len(rising_gaps)}")

    # 4. Cross-lingual gaps (separate Chinese/English keyword frequencies)
    zh_papers = [p for p in papers if p.get("language") == "zh"]
    en_papers = [p for p in papers if p.get("language") == "en"]

    zh_kw_freq = {}
    en_kw_freq = {}
    for p in zh_papers:
        for kw in p.get("normalized_keywords", []):
            zh_kw_freq[kw] = zh_kw_freq.get(kw, 0) + 1
    for p in en_papers:
        for kw in p.get("normalized_keywords", []):
            en_kw_freq[kw] = en_kw_freq.get(kw, 0) + 1

    cross_lingual_gaps = detect_cross_lingual_gap(
        zh_kw_freq,
        en_kw_freq,
        keyword_registry.get("unified_keyword_space", {}),
        ratio_threshold=gap_thresholds.get("cross_lingual_ratio", 5.0),
    )
    all_gaps.extend(cross_lingual_gaps)
    print(f"[Phase 5] Cross-lingual gaps: {len(cross_lingual_gaps)}")

    # 5. Citation stagnation gaps
    stagnation_gaps = detect_citation_stagnation_gap(
        papers,
        clusters.get("consensus_topics", {}).get("topics", []),
        ref_age_threshold=gap_thresholds.get("stagnation_ref_age", 8),
    )
    all_gaps.extend(stagnation_gaps)
    print(f"[Phase 5] Citation stagnation gaps: {len(stagnation_gaps)}")

    # 6. Practical problem gaps
    practical_gaps = detect_practical_gap(
        papers,
        clusters.get("consensus_topics", {}).get("topics", []),
        theory_ratio_threshold=gap_thresholds.get("practical_theory_ratio", 0.6),
    )
    all_gaps.extend(practical_gaps)
    print(f"[Phase 5] Practical problem gaps: {len(practical_gaps)}")

    # Synthesize and rank gaps
    synthesized_gaps = synthesize_gaps(all_gaps)
    print(f"[Phase 5] Total synthesized gaps: {len(synthesized_gaps)}")

    return synthesized_gaps


def generate_topic_cards(
    gaps: list,
    papers: list,
    trend_results: dict,
    clusters: dict,
    config: dict,
) -> list:
    """Generate research topic cards from detected gaps."""
    print("[Topic Generation] Generating topic cards...")

    eval_weights = config.get("evaluation_weights", {
        "theoretical": 0.35,
        "practical": 0.35,
        "feasibility": 0.30,
    })

    topic_cards = []
    topic_id = 1

    for gap in gaps[:config.get("topic_generation", {}).get("max_candidates", 10)]:
        keyword = gap.get("keyword") or gap.get("cluster", "")
        gap_type = gap.get("gap_type", "")
        opportunity = gap.get("opportunity_type", "")
        evidence = gap.get("evidence", "")

        momentum_info = None
        for m in trend_results.get("keyword_momentum", []):
            if m["keyword"] == keyword:
                momentum_info = m
                break

        representative_papers = []
        for p in papers:
            if keyword in p.get("normalized_keywords", []):
                representative_papers.append({
                    "title": p.get("title", ""),
                    "authors": p.get("authors", []),
                    "year": p.get("year", ""),
                    "citations": p.get("citations", 0),
                })
                if len(representative_papers) >= 3:
                    break

        theoretical_score = min(5, max(1, 3 + (gap.get("priority", 1) * 0.5)))
        practical_score = min(5, max(1, 3 + (gap.get("evidence_score", 1) * 0.3)))
        feasibility_score = min(5, max(1, 4 - (gap.get("total_papers", 20) / 20)))

        composite = (
            theoretical_score * eval_weights.get("theoretical", 0.35) +
            practical_score * eval_weights.get("practical", 0.35) +
            feasibility_score * eval_weights.get("feasibility", 0.30)
        )

        card = {
            "topic_id": f"T{topic_id:02d}",
            "title": keyword,
            "gap_type": gap_type,
            "opportunity_type": opportunity,
            "evidence": evidence,
            "momentum_score": momentum_info.get("momentum_score") if momentum_info else None,
            "momentum_classification": momentum_info.get("classification") if momentum_info else None,
            "total_papers": gap.get("total_papers", 0),
            "representative_papers": representative_papers,
            "evaluation": {
                "theoretical": round(theoretical_score, 1),
                "practical": round(practical_score, 1),
                "feasibility": round(feasibility_score, 1),
                "composite": round(composite, 2),
            },
            "suggested_approach": _suggest_approach(gap, gap_type),
        }
        topic_cards.append(card)
        topic_id += 1

    topic_cards.sort(key=lambda x: x["evaluation"]["composite"], reverse=True)

    for i, card in enumerate(topic_cards):
        card["topic_id"] = f"T{i+1:02d}"

    return topic_cards


def _suggest_approach(gap: dict, gap_type: str) -> dict:
    """Suggest research approach based on gap type."""
    approaches = {
        "high_centrality_low_density": {
            "method": "案例研究 / 多案例比较",
            "data": "深度访谈 + 二手文档",
            "周期": "6-12个月",
        },
        "theory_method_gap": {
            "method": "实证定量检验 / 准实验设计",
            "data": "问卷调查 / 公开数据集",
            "周期": "4-8个月",
        },
        "rising_sparse": {
            "method": "探索性研究 / 概念框架构建",
            "data": "文献分析 + 专家访谈",
            "周期": "3-6个月",
        },
        "cross_lingual": {
            "method": "跨文化比较研究 / 复制研究",
            "data": "中国情境数据 + 国际比较数据",
            "周期": "8-14个月",
        },
        "citation_stagnation": {
            "method": "文献综述 / 元分析",
            "data": "系统性文献检索",
            "周期": "4-8个月",
        },
        "practical_problem": {
            "method": "实证应用研究 / 行动研究",
            "data": "企业调研 + 案例数据",
            "周期": "6-12个月",
        },
    }
    return approaches.get(gap_type, {
        "method": "混合方法研究",
        "data": "待定",
        "周期": "待评估",
    })


def generate_report(
    topic_cards: list,
    gap_analysis: list,
    trend_results: dict,
    cluster_results: dict,
    papers: list,
    config: dict,
) -> str:
    """Generate final research topic report."""
    print("[Report] Generating research topic report...")

    eval_weights = config.get("evaluation_weights", {})

    report_lines = [
        "# 研究选题挖掘报告",
        "",
        f"**生成日期**: {datetime.now().strftime('%Y-%m-%d')}",
        f"**文献规模**: {len(papers)} 篇",
        "",
        "---",
        "",
        "## 摘要",
        "",
        f"本报告基于 {len(papers)} 篇中英文学术文献分析，识别出 {len(topic_cards)} 个具有潜力的研究选题。",
        "",
    ]

    if trend_results.get("emerging_topics"):
        emerging_kws = [m["keyword"] for m in trend_results["emerging_topics"][:3]]
        report_lines.append(f"- **新兴主题**: {', '.join(emerging_kws)}")
    if trend_results.get("rising_topics"):
        rising_kws = [m["keyword"] for m in trend_results["rising_topics"][:3]]
        report_lines.append(f"- **上升主题**: {', '.join(rising_kws)}")

    report_lines.extend(["", "---", "", "## 一、文献采集概况", ""])
    report_lines.append(f"本次分析共采集 {len(papers)} 篇文献。")

    zh_count = sum(1 for p in papers if p.get("language") == "zh")
    en_count = sum(1 for p in papers if p.get("language") == "en")
    report_lines.append(f"其中中文文献 {zh_count} 篇，英文文献 {en_count} 篇。")

    report_lines.extend(["", "---", "", "## 二、量化分析结果", ""])

    consensus_topics = cluster_results.get("consensus_topics", {}).get("topics", [])
    report_lines.append(f"### 2.1 研究主题聚类")
    report_lines.append(f"共识别出 {len(consensus_topics)} 个研究主题聚类。")
    report_lines.append("")

    report_lines.append("### 2.2 时序趋势分析")
    report_lines.append("")
    report_lines.append("**新兴主题 (Emerging)**")
    for m in trend_results.get("emerging_topics", [])[:5]:
        report_lines.append(f"- {m['keyword']}: 动量={m['momentum_score']}, 总论文={m['total_papers']}")
    report_lines.append("")

    report_lines.append("**上升主题 (Rising)**")
    for m in trend_results.get("rising_topics", [])[:5]:
        report_lines.append(f"- {m['keyword']}: 动量={m['momentum_score']}, 总论文={m['total_papers']}")
    report_lines.append("")

    report_lines.extend(["", "---", "", "## 三、研究空白识别", ""])

    gap_types = {}
    for gap in gap_analysis:
        gt = gap.get("gap_type", "unknown")
        gap_types[gt] = gap_types.get(gt, 0) + 1

    report_lines.append(f"共检测到 {len(gap_analysis)} 个研究空白，涵盖 {len(gap_types)} 种类型：")
    report_lines.append("")
    for gt, count in gap_types.items():
        report_lines.append(f"- **{gt}**: {count} 个")
    report_lines.append("")

    report_lines.extend(["", "---", "", "## 四、推荐选题", ""])
    report_lines.append(f"根据综合评分，生成以下 {len(topic_cards)} 个候选选题：")
    report_lines.append("")

    for card in topic_cards:
        report_lines.append(f"### Topic {card['topic_id']}: {card['title']}")
        report_lines.append("")
        report_lines.append(f"**空白类型**: {card['gap_type']} | **{card['opportunity_type']}**")
        report_lines.append("")
        report_lines.append("**量化证据**:")
        report_lines.append(f"- {card['evidence']}")
        if card.get("momentum_score"):
            report_lines.append(f"- 动量评分: {card['momentum_score']} ({card.get('momentum_classification', '')})")
        report_lines.append(f"- 相关论文数: {card['total_papers']}")
        report_lines.append("")

        report_lines.append("**建议研究路径**:")
        approach = card.get("suggested_approach", {})
        report_lines.append(f"- **方法**: {approach.get('method', '待定')}")
        report_lines.append(f"- **数据**: {approach.get('data', '待定')}")
        report_lines.append(f"- **周期**: {approach.get('周期', '待评估')}")
        report_lines.append("")

        report_lines.append("**评估得分**:")
        eval_data = card.get("evaluation", {})
        report_lines.append(f"| 维度 | 得分 |")
        report_lines.append(f"|------|------|")
        report_lines.append(f"| 理论意义 | {eval_data.get('theoretical', 'N/A')} |")
        report_lines.append(f"| 实践意义 | {eval_data.get('practical', 'N/A')} |")
        report_lines.append(f"| 可行性 | {eval_data.get('feasibility', 'N/A')} |")
        report_lines.append(f"| **综合** | **{eval_data.get('composite', 'N/A')}** |")
        report_lines.append("")

        report_lines.append("**奠基文献**:")
        for i, paper in enumerate(card.get("representative_papers", [])[:3], 1):
            authors = ", ".join(paper.get("authors", [])[:3]) if paper.get("authors") else "Unknown"
            year = paper.get("year", "n.d.")
            title = paper.get("title", "Untitled")
            report_lines.append(f"{i}. {authors} ({year}). {title}.")
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")

    top_topics = topic_cards[:5]
    report_lines.extend(["", "## 五、最优选题推荐", ""])
    report_lines.append("基于综合评分，推荐以下最优选题：")
    report_lines.append("")

    for card in top_topics:
        report_lines.append(f"**{card['topic_id']} {card['title']}** (综合得分: {card['evaluation']['composite']})")
        report_lines.append(f"> {card['evidence'][:100]}...")
        report_lines.append("")

    report_lines.extend(["",
                          "---",
                          "",
                          "**报告说明**: 本报告由 deepresearch-topic 技能生成，基于量化分析和AI辅助判断。",
                          "建议将本报告作为选题参考，结合个人研究兴趣、导师建议和领域专长做出最终决定。",
                          ""])

    return "\n".join(report_lines)


def main(input_file: str, config_file: str, output_file: str = None):
    """Main analysis pipeline."""
    print(f"[Deep Research Topic] Starting analysis pipeline...")
    print(f"[Deep Research Topic] Input: {input_file}")
    print(f"[Deep Research Topic] Config: {config_file}")

    data = load_phase2_output(input_file)
    config = load_config(config_file)

    papers = data.get("papers", [])
    keyword_registry = data.get("keyword_registry", {})

    print(f"[Deep Research Topic] Loaded {len(papers)} papers")

    # Phase 3: Topic Clustering
    cluster_results = run_topic_clustering(papers, config)

    network = cluster_results["cooccurrence_network"]
    centrality = compute_centrality(network)
    bridge_keywords = identify_bridge_keywords(centrality)

    cluster_results["centrality"] = centrality
    cluster_results["bridge_keywords"] = bridge_keywords

    # Phase 4: Trend Analysis
    trend_results = run_trend_analysis(papers, cluster_results, config)

    # Phase 5: Gap Detection
    gaps = run_gap_detection(
        papers,
        cluster_results,
        network,
        centrality,
        trend_results,
        keyword_registry,
        config,
    )

    # Generate Topic Cards
    topic_cards = generate_topic_cards(
        gaps,
        papers,
        trend_results,
        cluster_results,
        config,
    )

    # Generate Final Report
    report = generate_report(
        topic_cards,
        gaps,
        trend_results,
        cluster_results,
        papers,
        config,
    )

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"[Deep Research Topic] Report saved to {output_file}")

    structured_output = output_file.replace(".md", "_data.json") if output_file else "topic_analysis_data.json"
    structured_data = {
        "topic_cards": topic_cards,
        "gaps": gaps,
        "trend_results": {
            "emerging_topics": trend_results.get("emerging_topics", []),
            "rising_topics": trend_results.get("rising_topics", []),
            "fading_topics": trend_results.get("fading_topics", []),
        },
        "cluster_results": {
            "n_topics": len(cluster_results.get("consensus_topics", {}).get("topics", [])),
            "modularity": cluster_results.get("consensus_topics", {}).get("network_modularity", 0),
        },
        "network_metrics": {
            "n_nodes": len(network.get("nodes", [])),
            "n_edges": len(network.get("edges", [])),
            "density": compute_network_density(network),
        },
    }
    with open(structured_output, "w", encoding="utf-8") as f:
        json.dump(structured_data, f, ensure_ascii=False, indent=2)
    print(f"[Deep Research Topic] Structured data saved to {structured_output}")

    print(f"[Deep Research Topic] Analysis complete!")
    print(f"[Deep Research Topic] Generated {len(topic_cards)} topic recommendations")

    return {
        "topic_cards": topic_cards,
        "gaps": gaps,
        "trend_results": trend_results,
        "report": report,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Deep Research Topic Mining: Topic clustering, trend analysis, gap detection, and research topic generation"
    )
    parser.add_argument("--input", default="phase2_extracted.json",
                        help="Phase 2 output file")
    parser.add_argument("--config", default="assets/config.json",
                        help="Analysis configuration file")
    parser.add_argument("--output", default="research_topic_report.md",
                        help="Output report file (markdown)")

    args = parser.parse_args()

    skill_dir = os.path.dirname(os.path.dirname(__file__))
    input_path = args.input if os.path.isabs(args.input) else os.path.join(skill_dir, args.input)
    config_path = args.config if os.path.isabs(args.config) else os.path.join(skill_dir, args.config)
    output_path = args.output if os.path.isabs(args.output) else os.path.join(skill_dir, args.output)

    main(input_path, config_path, output_path)
