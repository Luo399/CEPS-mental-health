"""
引文网络分析脚本 - 构建和分析文献引用网络
"""

import json
from collections import defaultdict
from typing import List, Dict, Tuple
import yaml


class CitationNetworkAnalyzer:
    """引文网络分析器"""

    def __init__(self, config_path: str = "../config.yaml"):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        self.metrics = self.config["analysis"]["citation_network"]["metrics"]

    def analyze(self, papers: List[Dict]) -> Dict:
        """分析引文网络"""

        print("\n开始引文网络分析...")

        # 1. 构建网络
        network = self._build_network(papers)

        # 2. 计算中心性
        centrality = self._calculate_centrality(network, papers)

        # 3. 识别高影响力文献
        influential = self._identify_influential(papers, centrality)

        # 4. 社区检测
        communities = self._detect_communities(network, papers)

        result = {
            "network": network,
            "centrality": centrality,
            "influential_papers": influential,
            "communities": communities,
            "total_nodes": len(papers),
            "total_edges": sum(len(v) for v in network.values()),
        }

        print(f"引文网络分析完成: {len(papers)} 个节点\n")

        return result

    def _build_network(self, papers: List[Dict]) -> Dict:
        """构建引文网络"""

        # 简化: 基于主题相似性构建网络
        # 实际应用中需要真实的引用数据

        network = defaultdict(list)

        n = len(papers)

        # 计算论文间的相似度
        for i in range(n):
            for j in range(i + 1, n):
                similarity = self._calculate_similarity(papers[i], papers[j])

                if similarity > 0.3:  # 阈值
                    # 双向连接
                    if similarity > 0.5:
                        network[i].append(j)
                        network[j].append(i)

        return dict(network)

    def _calculate_similarity(self, paper1: Dict, paper2: Dict) -> float:
        """计算论文相似度"""

        # 基于关键词重叠
        kw1 = set(paper1.get("keywords", []))
        kw2 = set(paper2.get("keywords", []))

        if not kw1 or not kw2:
            return 0

        # Jaccard相似度
        intersection = len(kw1 & kw2)
        union = len(kw1 | kw2)

        return intersection / union if union > 0 else 0

    def _calculate_centrality(self, network: Dict, papers: List[Dict]) -> Dict:
        """计算中心性指标"""

        centrality = {}
        n = len(papers)

        # 1. 度中心性
        degree = {i: len(network.get(i, [])) for i in range(n)}

        # 2. 简化PageRank
        pagerank = self._simplified_pagerank(network, n)

        # 3. 简化中介中心性
        betweenness = self._simplified_betweenness(network, n)

        # 整合
        for i in range(n):
            centrality[i] = {
                "degree": degree.get(i, 0),
                "pagerank": pagerank.get(i, 0),
                "betweenness": betweenness.get(i, 0),
            }

        return centrality

    def _simplified_pagerank(self, network: Dict, n: int, iterations: int = 20) -> Dict:
        """简化PageRank算法"""

        # 初始值
        pr = {i: 1 / n for i in range(n)}
        damping = 0.85

        for _ in range(iterations):
            new_pr = {}

            for i in range(n):
                # 从引用它的论文获得PR
                sum_pr = 0
                neighbors = network.get(i, [])

                for neighbor in neighbors:
                    out_degree = len(network.get(neighbor, []))
                    if out_degree > 0:
                        sum_pr += pr[neighbor] / out_degree

                new_pr[i] = (1 - damping) / n + damping * sum_pr

            pr = new_pr

        return pr

    def _simplified_betweenness(self, network: Dict, n: int) -> Dict:
        """简化中介中心性"""

        betweenness = {i: 0 for i in range(n)}

        # 简化: 只计算直接路径
        for i in range(n):
            for j in range(i + 1, n):
                if i != j:
                    # 找从i到j的中间节点
                    neighbors_i = network.get(i, [])
                    neighbors_j = network.get(j, [])
                    middle = set(neighbors_i) & set(neighbors_j)

                    betweenness[i] += len(middle)
                    betweenness[j] += len(middle)

        return betweenness

    def _identify_influential(self, papers: List[Dict], centrality: Dict) -> List[Dict]:
        """识别高影响力文献"""

        # 综合评分
        scores = []

        for i, paper in enumerate(papers):
            # 归一化
            c = centrality.get(i, {})

            # 综合得分 = 0.4*被引 + 0.3*PageRank + 0.3*中介中心性
            score = (
                0.4 * paper.get("citations", 0) / 100  # 归一化
                + 0.3 * c.get("pagerank", 0) * 10
                + 0.3 * c.get("betweenness", 0) / 10
            )

            scores.append((i, score))

        # 排序
        scores.sort(key=lambda x: x[1], reverse=True)

        # 取前20
        influential = []

        for idx, score in scores[:20]:
            paper = papers[idx]
            influential.append(
                {
                    "rank": len(influential) + 1,
                    "title": paper.get("title", "")[:100],
                    "authors": paper.get("authors", [])[:3],
                    "year": paper.get("year"),
                    "journal": paper.get("journal", ""),
                    "citations": paper.get("citations", 0),
                    "score": round(score, 3),
                }
            )

        return influential

    def _detect_communities(self, network: Dict, papers: List[Dict]) -> List[List[int]]:
        """社区检测（简化版）"""

        # 基于聚类的简单社区检测
        visited = set()
        communities = []

        for i in range(len(papers)):
            if i in visited:
                continue

            # BFS找社区
            community = []
            queue = [i]

            while queue:
                node = queue.pop(0)
                if node in visited:
                    continue

                visited.add(node)
                community.append(node)

                for neighbor in network.get(node, []):
                    if neighbor not in visited:
                        queue.append(neighbor)

            if community:
                communities.append(community)

        return communities

    def generate_mermaid_network(
        self, papers: List[Dict], centrality: Dict, top_n: int = 15
    ) -> str:
        """生成Mermaid引文网络图"""

        lines = ["```mermaid", "flowchart TB"]
        lines.append("")
        lines.append("    subgraph Core[核心论文网络]")

        # 取Top N论文
        top_papers = sorted(
            range(len(papers)),
            key=lambda x: centrality.get(x, {}).get("pagerank", 0),
            reverse=True,
        )[:top_n]

        # 添加节点
        for idx in top_papers:
            paper = papers[idx]
            title = paper.get("title", "")[:20]
            c = centrality.get(idx, {})
            # 大小按PageRank
            size = int(c.get("pagerank", 0) * 100) + 10
            lines.append(f"        P{idx}[{title}...]({size},{size})")

        lines.append("    end")

        # 添加连接
        for i in range(len(top_papers)):
            for j in range(i + 1, len(top_papers)):
                if papers[top_papers[i]].get("title") != papers[top_papers[j]].get(
                    "title"
                ):
                    lines.append(f"    P{top_papers[i]} --- P{top_papers[j]}")

        lines.append("```")

        return "\n".join(lines)


def main():
    """测试用"""

    # 读取数据
    try:
        with open("extracted_papers.json", "r", encoding="utf-8") as f:
            papers = json.load(f)
    except FileNotFoundError:
        print("错误: 请先运行 extract_info.py")
        return

    # 分析
    analyzer = CitationNetworkAnalyzer()
    result = analyzer.analyze(papers)

    # 保存
    with open("citation_network.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # 打印高影响力文献
    print("\n=== 高影响力文献 Top 10 ===")
    for paper in result["influential_papers"][:10]:
        print(f"\n{paper['rank']}. {paper['title']}")
        print(f"   作者: {', '.join(paper['authors'])} | 年份: {paper['year']}")
        print(f"   被引: {paper['citations']} | 评分: {paper['score']}")

    # 生成Mermaid图
    mermaid = analyzer.generate_mermaid_network(papers, result["centrality"])
    print("\n" + mermaid)

    print("\n结果已保存到 citation_network.json")


if __name__ == "__main__":
    main()
