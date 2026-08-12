import requests
import time
from datetime import datetime
from typing import List, Dict, Any, Optional


class ElsevierError(Exception):
    pass


class RateLimitError(ElsevierError):
    def __init__(self, retry_after: int = 5):
        self.retry_after = retry_after
        super().__init__(f"速率限制，等待{retry_after}秒")


class AuthenticationError(ElsevierError):
    pass


class ElsevierClient:
    def __init__(self, api_key: str, endpoint: str = "https://api.elsevier.com/content", timeout: int = 30):
        self.api_key = api_key
        self.base_url = endpoint.rstrip('/')
        self.headers = {
            "X-ELS-APIKey": api_key,
            "Accept": "application/json"
        }
        self.timeout = timeout
        self.last_request_time = 0
        self.min_request_interval = 1.0

    def _rate_limit_wait(self) -> None:
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.min_request_interval:
            wait_time = self.min_request_interval - time_since_last
            time.sleep(wait_time)

        self.last_request_time = time.time()

    def search(
        self,
        query: str,
        years: int,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        end_year = datetime.now().year
        start_year = end_year - years

        results = []
        start = 0
        count = 25

        while len(results) < max_results:
            self._rate_limit_wait()

            try:
                els_query = f'KEYWORD("{query}") AND PUB-YEAR > {start_year} AND PUB-YEAR <= {end_year}'

                params = {
                    'query': els_query,
                    'count': count,
                    'start': start,
                    'sort': 'citedby-count:desc'
                }

                response = requests.get(
                    f"{self.base_url}/search/sciencedirect",
                    params=params,
                    headers=self.headers,
                    timeout=self.timeout
                )

                if response.status_code == 401:
                    raise AuthenticationError("API密钥无效或已过期")
                elif response.status_code == 429:
                    raise RateLimitError(5)
                elif response.status_code == 403:
                    raise ElsevierError("访问被拒绝，请检查API密钥权限")
                elif response.status_code >= 500:
                    raise ElsevierError(f"服务器错误: {response.status_code}")

                response.raise_for_status()
                data = response.json()

                search_results = data.get('search-results', {}) or {}
                entries = search_results.get('entry', []) or []

                if not entries:
                    break

                normalized = [self._normalize(entry) for entry in entries if self._is_valid_entry(entry)]
                results.extend(normalized)

                if len(results) >= max_results or len(entries) < count:
                    break

                start += count

            except requests.exceptions.Timeout:
                raise ElsevierError("请求超时，请检查网络连接")
            except requests.exceptions.RequestException as e:
                if "429" in str(e):
                    raise RateLimitError(5)
                raise ElsevierError(f"API请求失败: {str(e)}")
            except Exception as e:
                raise ElsevierError(f"未知错误: {str(e)}")

        return results[:max_results]

    def _normalize(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        creators = entry.get('dc:creator', []) or []
        if isinstance(creators, str):
            authors = [c.strip() for c in creators.split(';') if c.strip()]
        else:
            authors = creators

        return {
            'title': entry.get('dc:title', ''),
            'authors': authors,
            'journal': entry.get('prism:publicationName', ''),
            'year': self._extract_year(entry),
            'doi': entry.get('prism:doi', ''),
            'abstract': entry.get('dc:description', entry.get('abstract', '')),
            'citations': self._extract_citations(entry),
            'source': 'Elsevier',
            'url': self._construct_url(entry),
            'keywords': self._extract_keywords(entry),
            'document_type': self._extract_doc_type(entry)
        }

    def _is_valid_entry(self, entry: Dict[str, Any]) -> bool:
        title = entry.get('dc:title', '')
        return bool(title)

    def _extract_year(self, entry: Dict[str, Any]) -> Optional[int]:
        cover_date = entry.get('prism:coverDate', '')
        if cover_date:
            try:
                year_str = cover_date.split('-')[0]
                return int(year_str)
            except (ValueError, IndexError):
                pass

        pub_year = entry.get('prism:publicationDate', '')
        if pub_year:
            try:
                year_str = pub_year.split('-')[0]
                return int(year_str)
            except (ValueError, IndexError):
                pass

        return None

    def _extract_citations(self, entry: Dict[str, Any]) -> int:
        cited_by = entry.get('citedby-count', '')
        if isinstance(cited_by, str):
            try:
                return int(cited_by)
            except ValueError:
                return 0
        return int(cited_by) if cited_by else 0

    def _construct_url(self, entry: Dict[str, Any]) -> str:
        doi = entry.get('prism:doi', '')
        if doi:
            return f"https://doi.org/{doi}"

        pii = entry.get('pii', '')
        if pii:
            return f"https://doi.org/10.1016/{pii}"

        eid = entry.get('eid', '')
        if eid:
            return eid

        return ''

    def _extract_keywords(self, entry: Dict[str, Any]) -> List[str]:
        keywords = entry.get('authkeywords', []) or []
        if not keywords:
            keywords = entry.get('dcterms:subject', []) or []

        if isinstance(keywords, str):
            return [k.strip() for k in keywords.split(';') if k.strip()]

        return keywords[:10]

    def _extract_doc_type(self, entry: Dict[str, Any]) -> str:
        subtype = entry.get('subtypeDescription', '')
        if subtype:
            return subtype.lower()

        pub_type = entry.get('prism:aggregationType', '')
        if pub_type:
            return pub_type.lower()

        return 'article'

    def get_work_by_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        try:
            self._rate_limit_wait()

            params = {
                'query': f'DOI("{doi}")',
                'count': 1,
                'start': 0
            }

            response = requests.get(
                f"{self.base_url}/search/sciencedirect",
                params=params,
                headers=self.headers,
                timeout=self.timeout
            )

            if response.status_code == 401:
                raise AuthenticationError("API密钥无效或已过期")

            response.raise_for_status()
            data = response.json()

            search_results = data.get('search-results', {}) or {}
            entries = search_results.get('entry', []) or []

            if entries and self._is_valid_entry(entries[0]):
                return self._normalize(entries[0])

            return None
        except Exception as e:
            raise ElsevierError(f"获取DOI失败: {str(e)}")
