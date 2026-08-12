import requests
import time
from datetime import datetime
from typing import List, Dict, Any, Optional


class OpenAlexError(Exception):
    pass


class RateLimitError(OpenAlexError):
    def __init__(self, retry_after: int = 1):
        self.retry_after = retry_after
        super().__init__(f"速率限制，等待{retry_after}秒")


class OpenAlexClient:
    def __init__(self, endpoint: str = "https://api.openalex.org", timeout: int = 30):
        self.base_url = endpoint.rstrip('/')
        self.headers = {
            "User-Agent": "LiteratureCollector/1.0",
            "Accept": "application/json"
        }
        self.timeout = timeout

    def search(
        self,
        query: str,
        years: int,
        max_results: int = 100,
        filters: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        end_year = datetime.now().year
        start_year = end_year - years

        base_filter = f'from_publication_date:{start_year}-01-01,to_publication_date:{end_year}-12-31'
        if filters:
            base_filter += ',' + ','.join(f'{k}:{v}' for k, v in filters.items())

        results = []
        page = 1
        per_page = min(200, max_results)

        while len(results) < max_results:
            try:
                params = {
                    'filter': base_filter,
                    'search': query,
                    'per_page': per_page,
                    'page': page,
                    'sort': 'cited_by_count:desc'
                }

                response = requests.get(
                    f"{self.base_url}/works",
                    params=params,
                    headers=self.headers,
                    timeout=self.timeout
                )
                response.raise_for_status()

                data = response.json()

                if 'results' in data and data['results']:
                    works = data['results']
                    normalized = [self._normalize(work) for work in works if self._is_valid_work(work)]
                    results.extend(normalized)

                if not data.get('meta', {}).get('next_page'):
                    break

                if len(results) >= max_results:
                    break

                page += 1
                time.sleep(0.1)

            except requests.exceptions.Timeout:
                raise OpenAlexError("请求超时，请检查网络连接")
            except requests.exceptions.RequestException as e:
                raise OpenAlexError(f"API请求失败: {str(e)}")
            except Exception as e:
                raise OpenAlexError(f"未知错误: {str(e)}")

        return results[:max_results]

    def _normalize(self, work: Dict[str, Any]) -> Dict[str, Any]:
        primary_location = work.get('primary_location', {}) or {}
        source = primary_location.get('source', {}) or {}

        authors = []
        for authorship in work.get('authorships', []) or []:
            author = authorship.get('author', {})
            if author:
                authors.append(author.get('display_name', ''))

        abstract = work.get('abstract_inverted_index')
        abstract_text = ''
        if abstract:
            abstract_text = self._reconstruct_abstract(abstract)

        return {
            'title': work.get('title', ''),
            'authors': authors,
            'journal': source.get('display_name', ''),
            'year': work.get('publication_year'),
            'doi': work.get('doi', ''),
            'abstract': abstract_text,
            'citations': work.get('cited_by_count', 0),
            'source': 'OpenAlex',
            'url': work.get('id', ''),
            'keywords': [concept.get('display_name', '') for concept in work.get('concepts', []) or []][:5],
            'document_type': self._get_document_type(work)
        }

    def _is_valid_work(self, work: Dict[str, Any]) -> bool:
        title = work.get('title', '')
        return bool(title)

    def _reconstruct_abstract(self, abstract_inverted: Dict[str, List[int]]) -> str:
        if not abstract_inverted:
            return ''

        try:
            word_to_index = {}
            for word, indices in abstract_inverted.items():
                for idx in indices:
                    word_to_index[idx] = word

            sorted_words = [word_to_index[i] for i in sorted(word_to_index.keys())]
            return ' '.join(sorted_words)
        except Exception:
            return ''

    def _get_document_type(self, work: Dict[str, Any]) -> str:
        type_str = work.get('type', '')
        if type_str == 'article':
            return 'article'
        elif type_str == 'book':
            return 'book'
        elif type_str == 'chapter':
            return 'book-chapter'
        elif type_str == 'dataset':
            return 'dataset'
        return 'article'

    def get_work_by_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        try:
            response = requests.get(
                f"{self.base_url}/works/https://doi.org/{doi}",
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            if 'results' in data and data['results']:
                return self._normalize(data['results'][0])
            return None
        except Exception as e:
            raise OpenAlexError(f"获取DOI失败: {str(e)}")
