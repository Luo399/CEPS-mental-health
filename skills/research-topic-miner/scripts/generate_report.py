"""
报告生成脚本 - 输出最终的研究选题分析报告
"""

import json
from datetime import datetime
from typing import List, Dict
import yaml


class ReportGenerator:
    """报告生成器"""

    def __init__(self, config_path: str = "../config.yaml"):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

    def generate(
        self,
        topic_query: str,
        papers: List[Dict],
        extracted: List[Dict],
        topic_result: Dict,
        citation_result: Dict,
    ) -> str:
        """生成完整报告"""

        print("\n开始生成报告...")

        # 1. 研究前沿分析
        frontier = self._analyze_research_frontier(papers, extracted, topic_result)

        # 2. 研究缺口识别
        gaps = self._identify_research_gaps(
            papers, extracted, topic_result, citation_result
        )

        # 3. 可行选题建议
        proposals = self._generate_proposals(papers, gaps, topic_result)

        # 4. 组合报告
        report = self._compose_report(topic_query, frontier, gaps, proposals, papers)

        print("报告生成完成\n")

        return report

    def _analyze_research_frontier(
        self, papers: List[Dict], extracted: List[Dict], topic_result: Dict
    ) -> Dict:
        """分析研究前沿"""

        # 热点主题
        topics = topic_result.get("topics", [])
        hot_topics = sorted(topics, key=lambda x: x["paper_count"], reverse=True)[:5]

        # 高影响力文献
        influential = citation_result.get("influential_papers", [])[:10]

        # 研究方法趋势
        methods = {}
        for paper in extracted:
            for m in paper.get("methods", []):
                methods[m] = methods.get(m, 0) + 1
        top_methods = sorted(methods.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "hot_topics": hot_topics,
            "influential_papers": influential,
            "top_methods": top_methods,
            "total_papers": len(papers),
            "total_topics": len(topics),
        }

    def _identify_research_gaps(
        self,
        papers: List[Dict],
        extracted: List[Dict],
        topic_result: Dict,
        citation_result: Dict,
    ) -> List[Dict]:
        """识别研究缺口"""

        gaps = []

        # 1. 理论缺口 - 通过高影响力文献的分析识别
        # 查找尚未形成理论框架的领域
        topics = topic_result.get("topics", [])
        weak_topics = [t for t in topics if t["paper_count"] < 10]

        if weak_topics:
            gaps.append(
                {
                    "type": "理论缺口",
                    "description": f"部分主题({', '.join([t['keywords'][0] for t in weak_topics[:3]])})缺乏系统性理论研究",
                    "suggestion": "建议开展理论框架构建研究",
                }
            )

        # 2. 方法缺口 - 通过研究方法分析识别
        # 统计已有方法
        methods = set()
        for paper in extracted:
            methods.update(paper.get("methods", []))

        # 常见缺失方法
        missing_methods = []
        if "机器学习" not in methods:
            missing_methods.append("机器学习方法")
        if "空间分析" not in methods:
            missing_methods.append("空间分析方法")

        if missing_methods:
            gaps.append(
                {
                    "type": "方法缺口",
                    "description": f"现有研究较少使用: {', '.join(missing_methods)}",
                    "suggestion": "可尝试引入新方法提升研究深度",
                }
            )

        # 3. 实证缺口 - 通过高被引文献分析
        # 查找低被引但可能重要的领域
        low_citation_topics = [
            t
            for t in topics
            if t["paper_count"] > 5
            and any(papers[i].get("citations", 0) < 10 for i in t["paper_indices"])
        ]

        if low_citation_topics:
            gaps.append(
                {
                    "type": "实证缺口",
                    "description": f"部分主题({low_citation_topics[0]['keywords'][0]})缺乏充分的实证检验",
                    "suggestion": "需要更多实证研究验证理论假设",
                }
            )

        # 4. 区域缺口 - 分析研究对象的地理分布
        regions = {}
        for paper in extracted:
            for obj in paper.get("research_objects", []):
                if "省" in obj or "市" in obj or "地区" in obj:
                    regions[obj] = regions.get(obj, 0) + 1

        if len(regions) < 10:
            gaps.append(
                {
                    "type": "区域缺口",
                    "description": "现有研究覆盖区域有限，缺乏多区域比较研究",
                    "suggestion": "可扩展研究区域范围，开展跨区域比较",
                }
            )

        return gaps

    def _generate_proposals(
        self, papers: List[Dict], gaps: List[Dict], topic_result: Dict
    ) -> List[Dict]:
        """生成可行选题建议"""

        proposals = []

        # 基于研究缺口生成选题
        for i, gap in enumerate(gaps):
            proposal = {
                "id": f"T-{i + 1:03d}",
                "research_question": gap["description"],
                "theory_perspective": "基于现有理论框架",
                "data_suggestion": "建议使用XX数据库或调研数据",
                "method_suggestion": "推荐使用实证分析方法",
                "innovation_point": f"填补{gap['type']}",
                "gap_type": gap["type"],
            }
            proposals.append(proposal)

        # 基于热点主题生成延伸选题
        topics = topic_result.get("topics", [])
        hot_topics = sorted(topics, key=lambda x: x["paper_count"], reverse=True)[:3]

        for i, topic in enumerate(hot_topics):
            if len(proposals) >= 10:
                break

            keywords = topic.get("keywords", [])
            if keywords:
                proposal = {
                    "id": f"T-{len(proposals) + 1:03d}",
                    "research_question": f"{keywords[0]}的{'影响机制' if i == 0 else '演化趋势' if i == 1 else '政策建议'}研究",
                    "theory_perspective": "基于XX理论视角",
                    "data_suggestion": "建议使用面板数据或案例数据",
                    "method_suggestion": "推荐使用计量模型或案例分析",
                    "innovation_point": "从新角度切入",
                    "gap_type": "前沿深化",
                }
                proposals.append(proposal)

        return proposals[:10]  # 最多10个

    def _compose_report(
        self,
        query: str,
        frontier: Dict,
        gaps: List[Dict],
        proposals: List[Dict],
        papers: List[Dict],
    ) -> str:
        """组合完整报告"""

        lines = []

        # 标题
        lines.append(f"# 研究选题方向分析报告")
        lines.append("")
        lines.append(f"**研究主题**: {query}")
        lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        lines.append("---")
        lines.append("")

        # 1. 摘要
        lines.append("## 一、研究概述")
        lines.append("")
        lines.append(f"- 分析文献总数: {frontier['total_papers']}")
        lines.append(f"- 识别主题数: {frontier['total_topics']}")
        lines.append(f"- 高影响力文献: {len(frontier['influential_papers'])}")
        lines.append(f"- 识别研究缺口: {len(gaps)}")
        lines.append(f"- 生成选题建议: {len(proposals)}")
        lines.append("")

        # 2. 研究前沿
        lines.append("## 二、研究前沿分析")
        lines.append("")

        lines.append("### 2.1 热点主题")
        lines.append("")
        for i, topic in enumerate(frontier["hot_topics"], 1):
            lines.append(f"**{i}. {topic['name']}**")
            lines.append(f"- 关键词: {', '.join(topic['keywords'][:5])}")
            lines.append(f"- 相关论文: {topic['paper_count']} 篇")
            lines.append("")

        lines.append("### 2.2 高影响力文献")
        lines.append("")
        for paper in frontier["influential_papers"][:5]:
            lines.append(f"- **{paper['title']}** ({paper['year']})")
            lines.append(f"  - 作者: {', '.join(paper['authors'])}")
            lines.append(f"  - 被引: {paper['citations']}")
            lines.append("")

        lines.append("### 2.3 研究方法趋势")
        lines.append("")
        for method, count in frontier["top_methods"]:
            lines.append(f"- {method}: {count} 篇")
        lines.append("")

        # 3. 研究缺口
        lines.append("## 三、研究缺口识别")
        lines.append("")

        for i, gap in enumerate(gaps, 1):
            lines.append(f"### 3.{i} {gap['type']}")
            lines.append("")
            lines.append(f"**现状**: {gap['description']}")
            lines.append("")
            lines.append(f"**建议**: {gap['suggestion']}")
            lines.append("")

        # 4. 可行选题建议
        lines.append("## 四、可行选题建议")
        lines.append("")

        for prop in proposals:
            lines.append(f"### {prop['id']}: {prop['research_question']}")
            lines.append("")
            lines.append(f"- **理论视角**: {prop['theory_perspective']}")
            lines.append(f"- **数据建议**: {prop['data_suggestion']}")
            lines.append(f"- **方法建议**: {prop['method_suggestion']}")
            lines.append(f"- **创新点**: {prop['innovation_point']}")
            lines.append("")

        # 5. 参考文献
        lines.append("## 五、参考文献")
        lines.append("")

        for paper in frontier["influential_papers"][:20]:
            authors = ", ".join(paper["authors"][:3]) if paper["authors"] else "Unknown"
            journal = paper["journal"] or ""
            year = paper["year"] or ""
            lines.append(f"- [{authors} ({year}). {paper['title'][:50]}...]({journal})")

        lines.append("")
        lines.append("---")
        lines.append(f"*报告由 research-topic-miner 自动生成*")

        return "\n".join(lines)


def main():
    """测试用"""

    # 读取数据
    try:
        with open("collected_papers.json", "r", encoding="utf-8") as f:
            papers = json.load(f)
        with open("extracted_papers.json", "r", encoding="utf-8") as f:
            extracted = json.load(f)
        with open("topic_analysis.json", "r", encoding="utf-8") as f:
            topic_result = json.load(f)
        with open("citation_network.json", "r", encoding="utf-8") as f:
            citation_result = json.load(f)
    except FileNotFoundError as e:
        print(f"错误: 缺少数据文件 - {e}")
        return

    # 生成报告
    generator = ReportGenerator()
    report = generator.generate(
        topic_query="测试主题",
        papers=papers,
        extracted=extracted,
        topic_result=topic_result,
        citation_result=citation_result,
    )

    # 保存
    with open("research_topic_report.md", "w", encoding="utf-8") as f:
        f.write(report)

    print("报告已保存到 research_topic_report.md")


if __name__ == "__main__":
    main()
