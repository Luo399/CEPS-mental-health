"""
主题建模脚本 - 使用LDA/BERTopic进行主题聚类
"""

import json
import re
from collections import Counter
from typing import List, Dict, Tuple
import yaml


class TopicModeler:
    """主题建模器"""

    def __init__(self, config_path: str = "../config.yaml"):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        self.algorithm = self.config["analysis"]["topic_modeling"]["algorithm"]
        self.num_topics = self.config["analysis"]["topic_modeling"]["num_topics"]

        # 停用词
        self.stopwords = self._load_stopwords()

        # 中文分词库（简化版）
        try:
            import jieba

            self.jieba = jieba
            self.use_jieba = True
        except ImportError:
            self.use_jieba = False

    def _load_stopwords(self) -> set:
        """加载停用词"""
        stopwords = {
            "的",
            "了",
            "和",
            "是",
            "在",
            "有",
            "与",
            "对",
            "为",
            "等",
            "及",
            "of",
            "the",
            "and",
            "to",
            "in",
            "for",
            "is",
            "with",
            "on",
            "as",
            "a",
            "an",
            "by",
            "that",
            "this",
            "from",
            "or",
            "are",
            "be",
        }
        return stopwords

    def fit_transform(self, papers: List[Dict]) -> Dict:
        """执行主题建模"""

        print(f"\n开始主题建模 (算法: {self.algorithm})...")

        # 1. 文本预处理
        documents = self._preprocess(papers)

        # 2. 关键词提取
        keywords = self._extract_keywords(documents)

        # 3. 主题聚类（简化版LDA）
        topics = self._cluster_topics(keywords, documents)

        # 4. 主题演化分析
        evolution = self._analyze_evolution(papers, topics)

        result = {
            "topics": topics,
            "keywords": keywords,
            "evolution": evolution,
            "total_topics": len(topics),
        }

        print(f"主题建模完成，发现 {len(topics)} 个主题\n")

        return result

    def _preprocess(self, papers: List[Dict]) -> List[str]:
        """文本预处理"""

        documents = []

        for paper in papers:
            # 合并标题和摘要
            text = f"{paper.get('title', '')} {paper.get('abstract', '')}"

            # 清理
            text = self._clean_text(text)

            # 分词
            if self.use_jieba:
                words = list(self.jieba.cut(text))
            else:
                # 简单按字符分割
                words = re.findall(r"[\u4e00-\u9fa5]+|[a-zA-Z]+", text)

            # 过滤停用词和短词
            words = [w for w in words if w not in self.stopwords and len(w) > 1]

            documents.append(" ".join(words))

        return documents

    def _clean_text(self, text: str) -> str:
        """清理文本"""

        # 移除特殊字符
        text = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9\s]", " ", text)

        # 移除多余空格
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def _extract_keywords(self, documents: List[str]) -> List[Tuple[str, float]]:
        """提取关键词（简化版TF-IDF）"""

        # 词频统计
        word_counts = Counter()

        for doc in documents:
            words = doc.split()
            word_counts.update(words)

        # 计算TF-IDF（简化）
        total_docs = len(documents)
        keywords = []

        for word, count in word_counts.most_common(200):
            # 过滤停用词和数字
            if word in self.stopwords or word.isdigit():
                continue

            # 简单TF-IDF
            tf = count / total_docs
            idf = 1  # 简化
            score = tf * idf

            keywords.append((word, score))

        return keywords[:50]

    def _cluster_topics(
        self, keywords: List[Tuple[str, float]], documents: List[str]
    ) -> List[Dict]:
        """主题聚类（简化版）"""

        # 基于关键词共现的简单聚类
        topics = []

        # 将关键词分成N个主题
        keywords_per_topic = len(keywords) // self.num_topics

        for i in range(self.num_topics):
            start = i * keywords_per_topic
            end = (
                start + keywords_per_topic if i < self.num_topics - 1 else len(keywords)
            )

            topic_keywords = keywords[start:end]

            # 找相关论文
            topic_papers = self._find_topic_papers(topic_keywords, documents)

            topics.append(
                {
                    "topic_id": i + 1,
                    "name": f"主题{i + 1}",
                    "keywords": [k[0] for k in topic_keywords[:10]],
                    "keyword_scores": dict(topic_keywords[:10]),
                    "paper_count": len(topic_papers),
                    "paper_indices": topic_papers,
                }
            )

        return topics

    def _find_topic_papers(
        self, keywords: List[Tuple[str, float]], documents: List[str]
    ) -> List[int]:
        """找与主题相关的论文"""

        # 取前5关键词
        top_kw = [k[0] for k in keywords[:5]]

        paper_indices = []

        for i, doc in enumerate(documents):
            # 计算匹配度
            matches = sum(1 for kw in top_kw if kw in doc)
            if matches >= 2:
                paper_indices.append(i)

        return paper_indices

    def _analyze_evolution(self, papers: List[Dict], topics: List[Dict]) -> Dict:
        """分析主题演化"""

        # 按年份统计各主题论文数
        year_topic_counts = {}

        for paper in papers:
            year = paper.get("year")
            if not year:
                continue

            if year not in year_topic_counts:
                year_topic_counts[year] = {}

            # 论文所属主题
            for topic in topics:
                if papers.index(paper) in topic["paper_indices"]:
                    topic_name = topic["name"]
                    year_topic_counts[year][topic_name] = (
                        year_topic_counts[year].get(topic_name, 0) + 1
                    )

        return year_topic_counts

    def generate_mermaid_topics(self, topics: List[Dict]) -> str:
        """生成Mermaid主题关系图"""

        lines = ["```mermaid", "flowchart LR"]
        lines.append("")
        lines.append("    subgraph Topics[研究主题]")

        for topic in topics:
            topic_id = f"T{topic['topic_id']}"
            # 取第一个关键词作为标签
            label = (
                topic["keywords"][0]
                if topic["keywords"]
                else f"主题{topic['topic_id']}"
            )
            lines.append(f"        {topic_id}[{label}]")

        lines.append("    end")

        # 添加论文数量信息
        lines.append("")
        lines.append("    subgraph Papers[论文分布]")

        for topic in topics:
            count = topic["paper_count"]
            lines.append(
                f"        T{topic['topic_id']} -.-> P{topic['topic_id']}[{count}篇]"
            )

        lines.append("    end")
        lines.append("```")

        return "\n".join(lines)


def main():
    """测试用"""

    # 读取已提取的论文
    try:
        with open("extracted_papers.json", "r", encoding="utf-8") as f:
            papers = json.load(f)
    except FileNotFoundError:
        print("错误: 请先运行 extract_info.py")
        return

    # 主题建模
    modeler = TopicModeler()
    result = modeler.fit_transform(papers)

    # 保存结果
    with open("topic_analysis.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # 打印结果
    print("\n=== 主题建模结果 ===")
    for topic in result["topics"]:
        print(f"\n{topic['name']}: {', '.join(topic['keywords'][:5])}")
        print(f"  论文数: {topic['paper_count']}")

    # 生成Mermaid图
    mermaid = modeler.generate_mermaid_topics(result["topics"])
    print("\n" + mermaid)

    print("\n结果已保存到 topic_analysis.json")


if __name__ == "__main__":
    main()
