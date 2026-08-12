"""
Elsevier ScienceDirect 采集模块
使用 Elsevier Content API 检索文献
"""

import requests
import time
import urllib.parse
from typing import List, Dict, Optional


class ElsevierCollector:
    """Elsevier ScienceDirect 文献采集器"""

    def __init__(self, api_key: str, config: Dict = None):
        self.api_key = api_key
        self.config = config or {}
        self.papers = []
        self.endpoint = self.config.get("api_endpoint", "https://api.elsevier.com/content")

    def collect(
        self,
        query: str,
        journal_whitelist=None,
        journal_categories: List[str] = None,
        max_results: int = 50
    ) -> List[Dict]:
        """
        从 Elsevier ScienceDirect 采集文献

        Args:
            query: 搜索关键词
            journal_whitelist: 期刊白名单对象
            journal_categories: 期刊分类列表
            max_results: 最大返回结果数

        Returns:
            文献列表
        """
        print("[Elsevier] 开始采集...")

        # 构建搜索查询
        search_query = self._build_search_query(
            query,
            journal_whitelist,
            journal_categories
        )

        print(f"[Elsevier] 查询语句: {search_query}")

        # 调用搜索API
        url = f"{self.endpoint}/search/sciencedirect"
        params = {
            "query": search_query,
            "count": str(max_results),
            "httpAccept": "application/json"
        }

        headers = {
            "X-ELS-APIKey": self.api_key,
            "Accept": "application/json"
        }

        try:
            response = requests.get(url, params=params, headers=headers, timeout=60)

            if response.status_code == 200:
                data = response.json()
                results = data.get("search-results", {}).get("entry", [])

                for item in results:
                    paper = self._parse_elsevier(item)
                    if paper:
                        self.papers.append(paper)

                print(f"[Elsevier] 采集完成: {len(self.papers)} 篇")
            else:
                print(f"[Elsevier] 请求失败: {response.status_code}")
                print(f"[Elsevier] 响应: {response.text[:300]}")

        except Exception as e:
            print(f"[Elsevier] 错误: {str(e)}")

        time.sleep(1)
        return self.papers

    def _build_search_query(
        self,
        query: str,
        journal_whitelist=None,
        journal_categories: List[str] = None
    ) -> str:
        """
        构建 Elsevier 搜索查询

        Args:
            query: 原始查询
            journal_whitelist: 期刊白名单
            journal_categories: 期刊分类

        Returns:
            构建的查询字符串
        """
        # 基础查询 - 使用简化的查询语法
        search_query = query

        # 添加期刊过滤（限制为3本期刊以避免查询过长）
        if journal_whitelist and journal_categories:
            journals = journal_whitelist.get_journals(journal_categories)

            if journals:
                # Elsevier 查询语法: SRCTITLE("Journal Name")
                # 只使用前3本期刊以避免查询超限
                journal_list = list(journals)[:3]
                journal_filter = " OR ".join([
                    f'SRCTITLE("{j}")' for j in journal_list
                ])
                search_query = f'({query}) AND ({journal_filter})'
                print(f"[Elsevier] 使用期刊过滤: {len(journal_list)} 本期刊")

        return search_query

    def _parse_elsevier(self, item: Dict) -> Optional[Dict]:
        """
        解析 Elsevier 论文数据

        Args:
            item: Elsevier API返回的单个论文条目

        Returns:
            解析后的论文字典
        """
        # 提取DOI
        doi = None
        if "prism:doi" in item:
            doi = item["prism:doi"]
        elif "dc:identifier" in item:
            identifier = item["dc:identifier"]
            if identifier.startswith("DOI:"):
                doi = identifier[4:]

        if not doi:
            return None

        # 提取标题
        title = item.get("dc:title", "")

        # 提取作者
        authors = []
        if "dc:creator" in item:
            creator = item["dc:creator"]
            if isinstance(creator, list):
                authors = creator[:5]
            else:
                authors = [creator]

        # 提取年份
        year = None
        if "prism:coverDate" in item:
            cover_date = item["prism:coverDate"]
            if "-" in cover_date:
                year = int(cover_date.split("-")[0])

        # 提取期刊
        journal = None
        if "prism:publicationName" in item:
            journal = item["prism:publicationName"]
        elif "dc:source" in item:
            journal = item["dc:source"]

        # 提取摘要
        abstract = item.get("dc:description", "")

        # 提取URL
        url = None
        if "link" in item:
            for link in item["link"]:
                if link.get("@ref") == "self":
                    url = link.get("@href")
                    break

        # 提取引用数（Elsevier 不直接提供）
        citations = item.get("citedby-count", 0)

        return {
            "doi": doi,
            "title": title,
            "authors": authors,
            "year": year,
            "journal": journal,
            "abstract": abstract,
            "citations": int(citations) if citations else 0,
            "url": url,
            "source": "elsevier"
        }


if __name__ == "__main__":
    # 测试代码 - 使用用户提供的API Key
    API_KEY = "43734f3022020d6f29376bb637d70023"

    collector = ElsevierCollector(API_KEY)

    # 测试搜索
    papers = collector.collect("machine learning", max_results=10)

    print(f"\n=== 搜索结果 ===")
    for i, paper in enumerate(papers, 1):
        print(f"{i}. {paper.get('title')}")
        print(f"   期刊: {paper.get('journal')}")
        print(f"   作者: {', '.join(paper.get('authors', [])[:3])}")
        print(f"   DOI: {paper.get('doi')}")
        print()
