"""
文献采集脚本 - 从多个数据库采集学术论文
"""

import requests
import json
import time
import sys
from typing import List, Dict, Optional
import yaml

# 设置UTF-8编码输出
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class PaperCollector:
    """多数据库学术论文采集器"""

    def __init__(self, config_path: str = "config.yaml"):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"配置文件未找到: {config_path}，使用默认配置")
            self.config = self._get_default_config()

        self.papers = []
        self.seen_dois = set()

    def _get_default_config(self) -> Dict:
        """返回默认配置"""
        return {
            "databases": {
                "openalex": {
                    "enabled": True,
                    "max_results": 100,
                    "time_range": "3years",
                    "sort_by": "cited_by_count",
                    "api_endpoint": "https://api.openalex.org"
                },
                "wos": {"enabled": False},
                "elsevier": {"enabled": False},
                "arxiv": {
                    "enabled": True,
                    "categories": ["q-fin", "cs", "stat", "econ"],
                    "max_results": 30,
                    "api_endpoint": "http://export.arxiv.org/api/query"
                },
                "google_scholar": {"enabled": False},
                "cnki": {"enabled": False}
            }
        }

    def collect_from_all(
        self, query: str, user_papers: List[Dict] = None
    ) -> List[Dict]:
        """从所有启用的数据库采集文献"""

        print(f"\n{'=' * 50}")
        print(f"开始文献采集: {query}")
        print(f"{'=' * 50}\n")

        # 1. 处理用户自有文献
        if user_papers:
            print(f"[用户文献] 加载 {len(user_papers)} 篇用户文献")
            for paper in user_papers:
                if "doi" in paper:
                    self.seen_dois.add(paper["doi"].lower())
                self.papers.append({**paper, "source": "user"})

        # 2. 并行采集各数据库
        if self.config["databases"]["openalex"]["enabled"]:
            self._collect_openalex(query)

        if self.config["databases"]["wos"]["enabled"]:
            self._collect_wos(query)

        if self.config["databases"]["elsevier"]["enabled"]:
            self._collect_elsevier(query)

        if self.config["databases"]["arxiv"]["enabled"]:
            self._collect_arxiv(query)

        if self.config["databases"]["google_scholar"]["enabled"]:
            self._collect_google_scholar(query)

        if self.config["databases"]["cnki"]["enabled"]:
            self._collect_cnki(query)

        # 3. 去重并按被引排序
        self._deduplicate_and_sort()

        print(f"\n{'=' * 50}")
        print(f"采集完成: 共 {len(self.papers)} 篇文献")
        print(f"{'=' * 50}\n")

        return self.papers

    def _collect_openalex(self, query: str):
        """从 OpenAlex 采集"""
        print("[OpenAlex] 开始采集...")

        endpoint = self.config["databases"]["openalex"]["api_endpoint"]
        max_results = self.config["databases"]["openalex"]["max_results"]

        # 构建搜索查询 - 需要URL编码
        import urllib.parse
        encoded_query = urllib.parse.quote(query)
        search_url = f"{endpoint}/works?search={encoded_query}&per_page={max_results}&sort=cited_by_count:desc"

        try:
            response = requests.get(
                search_url,
                headers={"Accept": "application/json"},
                timeout=60,
            )

            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                for item in results:
                    paper = self._parse_openalex(item)
                    if paper:
                        self._add_paper(paper)
                print(f"[OpenAlex] 采集完成: {len(results)} 篇")
            else:
                print(f"[OpenAlex] 请求失败: {response.status_code}")

        except Exception as e:
            print(f"[OpenAlex] 错误: {str(e)}")

        time.sleep(1)  # 避免请求过快

    def _collect_wos(self, query: str):
        """从 Web of Science 采集"""
        print("[Web of Science] 开始采集...")

        # 注意: 需要API密钥
        print("[Web of Science] 需要配置API密钥，跳过")
        # 实际实现需要 Clarivate API

    def _collect_elsevier(self, query: str):
        """从 Elsevier ScienceDirect 采集"""
        print("[Elsevier] 开始采集...")

        # 注意: 需要API密钥
        print("[Elsevier] 需要配置API密钥，跳过")
        # 实际实现需要 Elsevier API

    def _collect_arxiv(self, query: str):
        """从 arXiv 采集"""
        print("[arXiv] 开始采集...")

        endpoint = self.config["databases"]["arxiv"]["api_endpoint"]
        categories = self.config["databases"]["arxiv"]["categories"]
        max_results = self.config["databases"]["arxiv"]["max_results"]

        # arXiv需要URL编码
        import urllib.parse
        encoded_query = urllib.parse.quote(query)

        for cat in categories:
            search_query = f"all:{encoded_query}+AND+cat:{cat}"
            url = f"{endpoint}?search_query={search_query}&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"

            try:
                response = requests.get(url, timeout=60)
                if response.status_code == 200:
                    import xml.etree.ElementTree as ET

                    root = ET.fromstring(response.content)

                    count = 0
                    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
                        paper = self._parse_arxiv(entry)
                        if paper:
                            self._add_paper(paper)
                            count += 1

                    print(f"[arXiv] {cat} 采集完成: {count} 篇")

            except Exception as e:
                print(f"[arXiv] {cat} 错误: {str(e)}")

            time.sleep(1)

    def _collect_google_scholar(self, query: str):
        """从 Google Scholar 采集"""
        print("[Google Scholar] 开始采集...")

        # 注意: Google Scholar 有严格限制
        print("[Google Scholar] 需要手动搜索或配置API")

    def _collect_cnki(self, query: str):
        """从 CNKI 采集"""
        print("[CNKI] 开始采集...")

        # 注意: 需要知网API
        print("[CNKI] 需要配置API密钥，跳过")

    def _parse_openalex(self, item: Dict) -> Dict:
        """解析 OpenAlex 论文数据"""
        doi_raw = item.get("doi")
        if doi_raw is None:
            return None
        doi = doi_raw.lower()

        if not doi:
            return None

        authors = [a.get("display_name", "") for a in item.get("authorships", [])[:5]]

        return {
            "doi": doi,
            "title": item.get("title", ""),
            "authors": authors,
            "year": item.get("publication_year"),
            "journal": item.get("primary_location", {})
            .get("source", {})
            .get("display_name"),
            "abstract": item.get("abstract"),
            "citations": item.get("cited_by_count", 0),
            "url": item.get("doi"),
            "source": "openalex",
        }

    def _parse_arxiv(self, entry) -> Dict:
        """解析 arXiv 论文数据"""
        import re

        # 提取arXiv ID
        arxiv_id = entry.find("{http://www.w3.org/2005/Atom}id").text.split("/")[-1]
        doi = f"arXiv:{arxiv_id}"

        if doi.lower() in self.seen_dois:
            return None

        # 提取作者
        authors = []
        for author in entry.findall("{http://www.w3.org/2005/Atom}author"):
            name = author.find("{http://www.w3.org/2005/Atom}name")
            if name is not None:
                authors.append(name.text)

        # 提取日期
        published = entry.find("{http://www.w3.org/2005/Atom}published").text
        year = int(published[:4]) if published else None

        return {
            "doi": doi,
            "title": entry.find("{http://www.w3.org/2005/Atom}title").text,
            "authors": authors[:5],
            "year": year,
            "journal": "arXiv",
            "abstract": entry.find("{http://www.w3.org/2005/Atom}summary").text,
            "citations": 0,  # arXiv 不提供引用数
            "url": entry.find("{http://www.w3.org/2005/Atom}id").text,
            "source": "arxiv",
        }

    def _add_paper(self, paper: Dict):
        """添加论文（去重）"""
        if paper is None:
            return

        doi = paper.get("doi", "").lower()

        if doi and doi in self.seen_dois:
            return

        if doi:
            self.seen_dois.add(doi)

        self.papers.append(paper)

    def _deduplicate_and_sort(self):
        """去重并按被引排序"""
        # 已有去重，这里确保唯一
        unique_papers = []
        seen_titles = set()

        for paper in self.papers:
            title = paper.get("title", "").lower().strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_papers.append(paper)

        # 按被引排序
        self.papers = sorted(
            unique_papers, key=lambda x: x.get("citations", 0), reverse=True
        )


def load_user_papers(paper_list: List[str], format: str = "doi") -> List[Dict]:
    """加载用户自有文献"""
    papers = []

    if format == "doi":
        for doi in paper_list:
            papers.append({"doi": doi.strip(), "source": "user"})
    elif format == "csv":
        # 需要解析CSV
        pass
    elif format == "bibtex":
        # 需要解析BibTeX
        pass

    return papers


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python collect_papers.py <搜索关键词>")
        sys.exit(1)

    query = sys.argv[1]

    collector = PaperCollector()
    papers = collector.collect_from_all(query)

    # 输出结果
    with open("collected_papers.json", "w", encoding="utf-8") as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)

    print(f"\n结果已保存到 collected_papers.json")
