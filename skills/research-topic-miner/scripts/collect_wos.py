"""
Web of Science 采集模块
使用 Web of Science API 检索文献
基于成功测试的实现
"""

import requests
import time
import urllib.parse
from typing import List, Dict, Optional


class WosCollector:
    """Web of Science 文献采集器"""

    def __init__(self, api_key: str, config: Dict = None):
        self.api_key = api_key
        self.config = config or {}
        self.papers = []
        self.endpoint = self.config.get("api_endpoint", "https://api.clarivate.com/apis/wos-starter/v1/")

    def collect(
        self,
        query: str,
        journal_whitelist=None,
        journal_categories: List[str] = None,
        max_results: int = 50
    ) -> List[Dict]:
        """
        从 Web of Science 采集文献

        Args:
            query: 搜索关键词
            journal_whitelist: 期刊白名单对象
            journal_categories: 期刊分类列表
            max_results: 最大返回结果数

        Returns:
            文献列表
        """
        print("[Web of Science] 开始采集...")

        # 构建搜索查询 - 使用TS（主题搜索）
        search_query = f"TS=({query})"
        print(f"[Web of Science] 查询语句: {search_query}")

        # 构建请求头
        headers = {
            "X-APIKey": self.api_key,
            "Accept": "application/json"
        }

        # 构建查询参数 - 使用GET请求
        query_params = {
            "db": "WOS",
            "limit": max_results,
            "q": search_query,
            "sortField": "PY+D"  # 按年份降序排列
        }

        # 调用搜索API - 使用GET请求（如成功测试所示）
        url = f"{self.endpoint}documents"

        try:
            response = requests.get(
                url,
                headers=headers,
                params=query_params,
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()

                # 提取检索结果 - WoS Starter API格式
                hits = data.get("hits", [])
                metadata = data.get("metadata", {})

                print(f"[Web of Science] 找到总数: {metadata.get('total', 'Unknown')}")

                if isinstance(hits, list):
                    for record in hits:
                        paper = self._parse_wos_starter(record)
                        if paper:
                            self.papers.append(paper)

                    print(f"[Web of Science] 采集完成: {len(self.papers)} 篇")
                else:
                    print(f"[Web of Science] 响应中未找到记录")

            elif response.status_code == 401:
                print("[Web of Science] 认证失败 - API Key无效或已过期")
            elif response.status_code == 403:
                print("[Web of Science] 权限被拒绝 - 检查API Key权限")
            elif response.status_code == 429:
                print("[Web of Science] 速率限制 - 请稍后重试")
            else:
                print(f"[Web of Science] 请求失败: {response.status_code}")
                print(f"[Web of Science] 响应: {response.text[:500]}")

        except requests.exceptions.JSONDecodeError as e:
            print(f"[Web of Science] JSON解析错误: {str(e)}")
            # 尝试打印原始响应
            if 'response' in locals():
                print(f"[Web of Science] 原始响应: {response.text[:500]}")
        except Exception as e:
            print(f"[Web of Science] 错误: {str(e)}")
            import traceback
            traceback.print_exc()

        time.sleep(1)
        return self.papers

    def _parse_wos_starter(self, record: Dict) -> Optional[Dict]:
        """
        解析 Web of Science Starter API 论文数据

        Args:
            record: Web of Science Starter API返回的单个论文记录

        Returns:
            解析后的论文字典
        """
        try:
            # 提取DOI
            doi = None
            identifiers = record.get("identifiers", {})
            if identifiers and "doi" in identifiers:
                doi = identifiers["doi"]

            # 提取标题
            title = record.get("title", "")

            # 提取作者
            authors = []
            names = record.get("names", {})
            if names and "authors" in names:
                author_list = names["authors"]
                if isinstance(author_list, list):
                    for a in author_list[:5]:
                        if isinstance(a, dict) and "displayName" in a:
                            authors.append(a["displayName"])

            # 提取年份
            year = None
            source = record.get("source", {})
            if source and "publishYear" in source:
                year = int(source["publishYear"])

            # 提取期刊
            journal = None
            if source and "sourceTitle" in source:
                journal = source["sourceTitle"]

            # 提取摘要
            abstract = record.get("abstract", "")

            # 提取引用数
            citations = 0
            citations_list = record.get("citations", [])
            if citations_list and isinstance(citations_list, list) and len(citations_list) > 0:
                citations = int(citations_list[0].get("count", 0))

            # 提取关键词
            keywords = []
            keywords_obj = record.get("keywords", {})
            if keywords_obj and "authorKeywords" in keywords_obj:
                keywords = keywords_obj["authorKeywords"]

            # 提取URL
            url = None
            if doi:
                url = f"https://doi.org/{doi}"

            return {
                "doi": doi,
                "title": title,
                "authors": authors,
                "year": year,
                "journal": journal,
                "abstract": abstract,
                "citations": citations,
                "keywords": keywords,
                "url": url,
                "source": "wos"
            }

        except Exception as e:
            print(f"[Web of Science] 解析记录时出错: {str(e)}")
            return None


if __name__ == "__main__":
    # 测试代码
    API_KEY = "93cd9e7de9d29a24f854ea7598417e740f87b2aa"

    collector = WosCollector(API_KEY)

    # 测试搜索
    papers = collector.collect("machine learning", max_results=10)

    print(f"\n=== 搜索结果 ===")
    for i, paper in enumerate(papers, 1):
        print(f"{i}. {paper.get('title')}")
        print(f"   期刊: {paper.get('journal')}")
        print(f"   作者: {', '.join(paper.get('authors', [])[:3])}")
        print(f"   DOI: {paper.get('doi')}")
        print(f"   被引: {paper.get('citations', 0)}")
        print()
