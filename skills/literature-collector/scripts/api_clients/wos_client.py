import requests
import time
from datetime import datetime
from typing import List, Dict, Any, Optional


class WOSError(Exception):
    pass


class RateLimitError(WOSError):
    def __init__(self, retry_after: int = 10):
        self.retry_after = retry_after
        super().__init__(f"速率限制，等待{retry_after}秒")


class AuthenticationError(WOSError):
    pass


class WOSClient:
    def __init__(self, api_key: str, endpoint: str = "https://api.clarivate.com/apis/wos-starter/v1", timeout: int = 30):
        self.api_key = api_key
        self.base_url = endpoint.rstrip('/')
        self.headers = {
            "X-APIKey": api_key,
            "Accept": "application/json",
            "Content-Type": "application/json"
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
        first_record = 1
        count = 100

        while len(results) < max_results:
            self._rate_limit_wait()

            try:
                wos_query = f'TS=({query}) AND PY=({start_year}-{end_year})'

                payload = {
                    "databaseId": "WOS",
                    "queryLanguage": "en",
                    "queryExpression": wos_query,
                    "count": min(count, max_results - len(results)),
                    "firstRecord": first_record
                }

                response = requests.post(
                    f"{self.base_url}/search",
                    json=payload,
                    headers=self.headers,
                    timeout=self.timeout
                )

                if response.status_code == 401:
                    raise AuthenticationError("API密钥无效或已过期")
                elif response.status_code == 429:
                    raise RateLimitError(10)
                elif response.status_code == 403:
                    raise WOSError("访问被拒绝，请检查API密钥权限")
                elif response.status_code >= 500:
                    raise WOSError(f"服务器错误: {response.status_code}")

                response.raise_for_status()
                data = response.json()

                if not data.get('Data', {}).get('Records'):
                    break

                records_data = data['Data']['Records']
                records = records_data.get('records', [])

                if not records:
                    break

                normalized = [self._normalize(record) for record in records if self._is_valid_record(record)]
                results.extend(normalized)

                if len(results) >= max_results:
                    break

                first_record += count

            except requests.exceptions.Timeout:
                raise WOSError("请求超时，请检查网络连接")
            except requests.exceptions.RequestException as e:
                if "429" in str(e):
                    raise RateLimitError(10)
                raise WOSError(f"API请求失败: {str(e)}")
            except Exception as e:
                raise WOSError(f"未知错误: {str(e)}")

        return results[:max_results]

    def _normalize(self, record: Dict[str, Any]) -> Dict[str, Any]:
        titles = record.get('titles', {}) or {}
        title = titles.get('title', '')
        if isinstance(title, list):
            title = title[0] if title else ''

        authors_data = record.get('authors', {}) or {}
        authors = authors_data.get('authors', []) or []

        author_names = []
        if authors:
            if isinstance(authors, list):
                for author in authors:
                    if isinstance(author, dict):
                        author_names.append(author.get('wos_standard', ''))
            else:
                author_names.append(str(authors))

        source = record.get('static_data', {}).get('summary', {}).get('source', {}) or {}
        journal = source.get('sourceTitle', '')
        if isinstance(journal, list):
            journal = journal[0] if journal else ''

        pub_year_data = record.get('pubyear', {}) or {}
        year = pub_year_data.get('text', '')
        if isinstance(year, list):
            year = year[0] if year else ''

        doi = self._extract_doi(record)

        abstract_data = record.get('abstract', {}) or {}
        abstract = ''
        if 'abstractText' in abstract_data:
            abstract_text = abstract_data['abstractText']
            if isinstance(abstract_text, list):
                abstract = abstract_text[0] if abstract_text else ''
            else:
                abstract = abstract_text

        citations_data = record.get('citationInfo', {}) or {}
        citations = citations_data.get('citationCount', '0')
        if isinstance(citations, str):
            try:
                citations = int(citations)
            except ValueError:
                citations = 0

        keywords_data = record.get('keywords', {}) or {}
        keywords = keywords_data.get('keywords', []) or []

        keyword_list = []
        if keywords:
            if isinstance(keywords, list):
                for kw in keywords:
                    if isinstance(kw, dict):
                        keyword_list.append(kw.get('keyword', ''))
            elif isinstance(keywords, str):
                keyword_list.append(keywords)

        doc_type = self._extract_doc_type(record)

        return {
            'title': title,
            'authors': author_names,
            'journal': journal,
            'year': self._parse_year(year),
            'doi': doi,
            'abstract': abstract,
            'citations': citations,
            'source': 'Web of Science',
            'url': f"https://doi.org/{doi}" if doi else '',
            'keywords': keyword_list[:10],
            'document_type': doc_type
        }

    def _is_valid_record(self, record: Dict[str, Any]) -> bool:
        titles = record.get('titles', {}) or {}
        title = titles.get('title', '')
        if isinstance(title, list):
            title = title[0] if title else ''
        return bool(title)

    def _extract_doi(self, record: Dict[str, Any]) -> str:
        other = record.get('other', {}) or {}
        identifiers = other.get('identifiers', {}) or {}

        if isinstance(identifiers, list):
            for identifier in identifiers:
                if isinstance(identifier, dict):
                    if identifier.get('type') == 'doi':
                        return identifier.get('value', '')
        elif isinstance(identifiers, dict):
            if identifiers.get('type') == 'doi':
                return identifiers.get('value', '')

        doi_data = record.get('dynamic_data', {}).get('cluster_related', {}).get('doi', {})
        doi = doi_data.get('value', '')
        if isinstance(doi, list):
            return doi[0] if doi else ''

        return doi

    def _parse_year(self, year: Any) -> Optional[int]:
        if isinstance(year, int):
            return year

        if isinstance(year, str):
            year = year.strip()
            if year.isdigit():
                return int(year)
            else:
                match = ''.join(filter(str.isdigit, year[:4]))
                if match:
                    return int(match)

        return None

    def _extract_doc_type(self, record: Dict[str, Any]) -> str:
        static_data = record.get('static_data', {}) or {}
        summary = static_data.get('summary', {}) or {}

        doctypes = summary.get('doctypes', {}) or {}
        doctype = doctypes.get('doctype', '')

        if isinstance(doctype, list):
            return doctype[0].lower() if doctype else 'article'

        return doctype.lower() if doctype else 'article'

    def get_work_by_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        try:
            self._rate_limit_wait()

            payload = {
                "databaseId": "WOS",
                "queryLanguage": "en",
                "queryExpression": f'DOI=("{doi}")',
                "count": 1,
                "firstRecord": 1
            }

            response = requests.post(
                f"{self.base_url}/search",
                json=payload,
                headers=self.headers,
                timeout=self.timeout
            )

            if response.status_code == 401:
                raise AuthenticationError("API密钥无效或已过期")

            response.raise_for_status()
            data = response.json()

            if data.get('Data', {}).get('Records'):
                records_data = data['Data']['Records']
                records = records_data.get('records', [])

                if records and self._is_valid_record(records[0]):
                    return self._normalize(records[0])

            return None
        except Exception as e:
            raise WOSError(f"获取DOI失败: {str(e)}")
