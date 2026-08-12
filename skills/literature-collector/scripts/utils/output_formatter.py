import json
from datetime import datetime
from typing import List, Dict, Any, Optional


def format_json_output(
    literature: List[Dict[str, Any]],
    search_params: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> str:
    output = {
        'search_parameters': format_search_parameters(search_params),
        'literature': format_literature_list(literature, config),
        'summary': format_summary(literature, search_params.get('sources', []))
    }

    return json.dumps(output, indent=2, ensure_ascii=False)


def format_search_parameters(search_params: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'research_field': search_params.get('research_field', ''),
        'years': search_params.get('years', 3),
        'sources': search_params.get('sources', []),
        'timestamp': datetime.now().isoformat()
    }


def format_literature_list(
    literature: List[Dict[str, Any]],
    config: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    formatted = []

    include_abstract = True
    max_abstract_length = 500

    if config:
        output_settings = config.get('output_settings', {})
        include_abstract = output_settings.get('include_abstract', True)
        max_abstract_length = output_settings.get('max_abstract_length', 500)

    for item in literature:
        formatted_item = {
            'title': item.get('title', ''),
            'authors': item.get('authors', []),
            'journal': item.get('journal', ''),
            'year': item.get('year'),
            'doi': item.get('doi', ''),
            'citations': item.get('citations', 0),
            'source': item.get('source', ''),
           'url': item.get('url', ''),
            'keywords': item.get('keywords', []),
            'document_type': item.get('document_type', 'article')
        }

        if include_abstract:
            abstract = item.get('abstract', '')
            if max_abstract_length and len(abstract) > max_abstract_length:
                abstract = abstract[:max_abstract_length] + '...'
            formatted_item['abstract'] = abstract

        formatted.append(formatted_item)

    return formatted


def format_summary(
    literature: List[Dict[str, Any]],
    sources: List[str]
) -> Dict[str, Any]:
    total_results = len(literature)

    by_source = {}
    source_counts = {}

    for item in literature:
        source = item.get('source', 'Unknown')
        source_counts[source] = source_counts.get(source, 0) + 1

    for source in sources:
        source_name = get_source_display_name(source)
        by_source[source_name] = source_counts.get(source_name, 0)

    total_citations = sum(item.get('citations', 0) for item in literature)
    average_citations = total_citations / total_results if total_results > 0 else 0

    unique_dois = len(set(item.get('doi', '') for item in literature if item.get('doi')))

    return {
        'total_results': total_results,
        'by_source': by_source,
        'average_citations': round(average_citations, 2),
        'unique_dois': unique_dois
    }


def get_source_display_name(source: str) -> str:
    source_map = {
        'openalex': 'OpenAlex',
        'elsevier': 'Elsevier',
        'wos': 'Web of Science',
        'web': 'Web Search',
        'file': 'Local File'
    }
    return source_map.get(source.lower(), source.capitalize())


def sort_literature(
    literature: List[Dict[str, Any]],
    sort_by: str = 'citations',
    reverse: bool = True
) -> List[Dict[str, Any]]:
    if sort_by == 'citations':
        return sorted(literature, key=lambda x: x.get('citations', 0), reverse=reverse)
    elif sort_by == 'year':
        return sorted(literature, key=lambda x: x.get('year', 0), reverse=reverse)
    elif sort_by == 'title':
        return sorted(literature, key=lambda x: x.get('title', ''), reverse=reverse)
    else:
        return literature


def deduplicate_by_doi(literature: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen_dois = set()
    unique_literature = []

    for item in literature:
        doi = item.get('doi', '')

        if not doi:
            unique_literature.append(item)
            continue

        if doi not in seen_dois:
            seen_dois.add(doi)
            unique_literature.append(item)

    return unique_literature


def deduplicate_by_title(literature: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen_titles = set()
    unique_literature = []

    for item in literature:
        title = item.get('title', '').lower().strip()

        if not title:
            unique_literature.append(item)
            continue

        if title not in seen_titles:
            seen_titles.add(title)
            unique_literature.append(item)

    return unique_literature


def save_json_output(output: str, output_file: str) -> None:
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
    except Exception as e:
        raise IOError(f"保存输出文件失败: {str(e)}")


def validate_output(output: str) -> bool:
    try:
        data = json.loads(output)

        required_keys = ['search_parameters', 'literature', 'summary']
        for key in required_keys:
            if key not in data:
                return False

        if not isinstance(data['literature'], list):
            return False

        return True
    except json.JSONDecodeError:
        return False
