"""
API Integrators for Academic Databases
Handles connections and data retrieval from various academic APIs
"""

import requests
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class Publication:
    """Represents a publication with basic metadata"""
    title: str
    authors: List[str]
    journal: str
    year: int
    doi: str
    abstract: str
    citations: int
    keywords: List[str]

class BaseAPI:
    """Base class for API integrators"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ResearchTopicMining/1.0',
            'Accept': 'application/json'
        })

    def _make_request(self, url: str, params: Dict = None, timeout: int = 30) -> Dict:
        """Make API request with error handling"""
        try:
            response = self.session.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON response: {str(e)}")

    def _handle_rate_limit(self, response: requests.Response) -> None:
        """Handle rate limiting by waiting and retrying"""
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            time.sleep(retry_after)
            raise Exception(f"Rate limited, retrying after {retry_after} seconds")

class PubMedAPI(BaseAPI):
    """PubMed API Integrator"""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def search_publications(self, query: str, max_results: int = 100,
                         from_date: Optional[str] = None,
                         to_date: Optional[str] = None) -> List[Publication]:
        """Search PubMed for publications"""
        params = {
            'db': 'pubmed',
            'term': query,
            'retmode': 'json',
            'retmax': max_results,
            'sort': 'pubdate'
        }

        if from_date:
            params[' mindate'] = from_date
        if to_date:
            params[' maxdate'] = to_date

        response = self._make_request(f"{self.base_url}/esearch.fcgi", params)
        id_list = response.get('esearchresult', {}).get('idlist', [])

        if not id_list:
            return []

        # Fetch details for each publication
        details = []
        for i in range(0, len(id_list), 100):  # Batch requests (max 100 per call)
            batch = id_list[i:i+100]
            batch_params = {
                'db': 'pubmed',
                'id': ','.join(batch),
                'retmode': 'json',
                'rettype': 'full'
            }
            batch_response = self._make_request(f"{self.base_url}/efetch.fcgi", batch_params)
            details.extend(batch_response.get('esearchresult', {}).get('idlist', []))

        return self._parse_publications(details)

    def _parse_publications(self, data: List[Dict]) -> List[Publication]:
        """Parse publication data from PubMed response"""
        publications = []

        for item in data:
            try:
                # Extract basic information (simplified parsing)
                title = item.get('title', 'Unknown')
                authors = item.get('authors', [])
                journal = item.get('journal', 'Unknown')
                year = int(item.get('year', 0))
                doi = item.get('doi', '')
                abstract = item.get('abstract', '')
                citations = int(item.get('citations', 0))
                keywords = item.get('keywords', [])

                publications.append(Publication(
                    title=title,
                    authors=authors,
                    journal=journal,
                    year=year,
                    doi=doi,
                    abstract=abstract,
                    citations=citations,
                    keywords=keywords
                ))
            except (ValueError, AttributeError) as e:
                continue  # Skip malformed entries

        return publications

class arXivAPI(BaseAPI):
    """arXiv API Integrator"""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.base_url = "https://export.arxiv.org/api/query"

    def search_preprints(self, query: str, max_results: int = 100,
                       time_period: str = "all") -> List[Publication]:
        """Search arXiv for preprints"""
        params = {
            'search_query': query,
            'start': 0,
            'max_results': max_results,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }

        response = self._make_request(self.base_url, params)
        # Parse XML response (simplified)
        # In a real implementation, would use xml.etree.ElementTree

        # For demonstration, return empty list
        return []

    def get_latest_submissions(self, category: str, max_results: int = 50) -> List[Publication]:
        """Get latest submissions in a specific category"""
        params = {
            'search_query': f'cat:{category}',
            'start': 0,
            'max_results': max_results,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }

        response = self._make_request(self.base_url, params)
        # Parse XML response
        return []

class CrossrefAPI(BaseAPI):
    """Crossref API Integrator"""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.base_url = "https://api.crossref.org/works"

    def search_doi(self, doi: str) -> Optional[Publication]:
        """Search by DOI"""
        url = f"{self.base_url}/{doi}"
        response = self._make_request(url)

        item = response.get('message', {})
        if not item:
            return None

        return self._parse_crossref_item(item)

    def search_query(self, query: str, max_results: int = 100) -> List[Publication]:
        """Search by query"""
        params = {
            'query': query,
            'rows': max_results,
            'sort': 'relevance',
            'filter': 'from-pub-date:2020'
        }

        response = self._make_request(self.base_url, params)
        items = response.get('message', {}).get('items', [])

        return [self._parse_crossref_item(item) for item in items if item]

    def _parse_crossref_item(self, item: Dict) -> Publication:
        """Parse Crossref item into Publication object"""
        title = item.get('title', ['Unknown'])[0]
        authors = [author.get('name', '') for author in item.get('author', [])]
        journal = item.get('container-title', ['Unknown'])[0]
        year = int(item.get('published', {}).get('date-parts', [[0]])[0][0])
        doi = item.get('DOI', '')
        abstract = item.get('abstract', '')

        # Estimate citations (Crossref doesn't provide direct citation count)
        citations = 0

        return Publication(
            title=title,
            authors=authors,
            journal=journal,
            year=year,
            doi=doi,
            abstract=abstract,
            citations=citations,
            keywords=[]
        )

class GoogleScholarAPI(BaseAPI):
    """Google Scholar API Integrator (using third-party service)"""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.base_url = "https://serpapi.com/search"

    def search_scholar(self, query: str, max_results: int = 20) -> List[Publication]:
        """Search Google Scholar"""
        params = {
            'engine': 'google_scholar',
            'q': query,
            'hl': 'en',
            'as_sdt': '0,5',
            'num': max_results
        }

        if self.api_key:
            params['api_key'] = self.api_key

        response = self._make_request(self.base_url, params)
        organic_results = response.get('organic_results', [])

        return [self._parse_scholar_result(result) for result in organic_results]

    def _parse_scholar_result(self, result: Dict) -> Publication:
        """Parse Google Scholar result"""
        title = result.get('title', 'Unknown')
        authors = result.get('authors', '').split(', ')
        year = int(result.get('year', 0))
        publication_info = result.get('publication_info', 'Unknown')
        link = result.get('link', '')
        citations = int(result.get('cited_by', 0))

        return Publication(
            title=title,
            authors=authors,
            journal=publication_info,
            year=year,
            doi='',
            abstract='',
            citations=citations,
            keywords=[]
        )

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TopicMiner:
    """Main class for research topic mining"""

    def __init__(self):
        self.pubmed = PubMedAPI()
        self.arxiv = arXivAPI()
        self.crossref = CrossrefAPI()
        self.scholar = GoogleScholarAPI()
        from data_processor import DataProcessor
        from topic_analyzer import TopicAnalyzer
        from output_generator import OutputGenerator
        self.data_processor = DataProcessor()
        self.topic_analyzer = TopicAnalyzer()
        self.output_generator = OutputGenerator()

    def search_topics(self, query: str, discipline: str = "all",
                    time_period: str = "last_2_years",
                    max_results: int = 200) -> Dict:
        """Search for topics in academic literature"""
        # Determine time period
        end_date = datetime.now()
        if time_period == "last_2_years":
            start_date = end_date - timedelta(days=730)
        elif time_period == "last_year":
            start_date = end_date - timedelta(days=365)
        elif time_period == "last_6_months":
            start_date = end_date - timedelta(days=180)
        else:
            start_date = end_date - timedelta(days=365)

        # Search across relevant APIs based on discipline
        publications = []

        if discipline in ["all", "biomedical", "medicine", "biology"]:
            publications.extend(self.pubmed.search_publications(
                query, max_results=max_results//4,
                from_date=start_date.strftime('%Y/%m/%d'),
                to_date=end_date.strftime('%Y/%m/%d')
            ))

        if discipline in ["all", "computer_science", "physics", "mathematics"]:
            publications.extend(self.arxiv.search_preprints(
                query, max_results=max_results//4
            ))

        if discipline in ["all", "engineering", "technology"]:
            publications.extend(self.crossref.search_query(
                query, max_results=max_results//4
            ))

        if discipline in ["all", "social_sciences", "humanities"]:
            publications.extend(self.scholar.search_scholar(
                query, max_results=max_results//4
            ))

        # Process and analyze the data
        processed_data = self.data_processor.process_publications(publications)
        topics = self.topic_analyzer.analyze_topics(processed_data)
        output = self.output_generator.generate_output(topics)

        return output

    def analyze_multi_disciplinary(self, topics: List[str],
                               time_range: str = "2022-2024") -> Dict:
        """Analyze multiple topics across disciplines"""
        results = {}

        for topic in topics:
            result = self.search_topics(
                query=topic,
                discipline="all",
                time_period=time_range
            )
            results[topic] = result

        return results

    def detect_research_gaps(self, discipline: str,
                          min_publications: int = 50,
                          time_period: str = "last_3_years") -> Dict:
        """Detect potential research gaps"""
        # This would involve more complex analysis
        # For now, return placeholder
        return {
            "gaps": [],
            "analysis": "Research gap detection requires advanced topic modeling and trend analysis"
        }