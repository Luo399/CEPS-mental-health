import csv
from pathlib import Path
from typing import List, Dict, Any, Optional
from io import StringIO


class CSVError(Exception):
    pass


class CSVParser:
    def __init__(self):
        self.column_mapping = {
            'title': ['title', 'Title', 'TITLE', '论文标题', '标题'],
            'author': ['author', 'Author', 'AUTHOR', 'authors', 'Authors', 'AUTHORS', '作者'],
            'journal': ['journal', 'Journal', 'JOURNAL', 'source', 'Source', 'SOURCE', '期刊'],
            'year': ['year', 'Year', 'YEAR', 'date', 'Date', 'DATE', '年份', '发表年份'],
            'doi': ['doi', 'Doi', 'DOI', 'DO'],
            'abstract': ['abstract', 'Abstract', 'ABSTRACT', '摘要', '简介'],
            'citations': ['citations', 'Citations', 'CITATIONS', 'citation_count', 'CitationCount', '引用次数'],
            'url': ['url', 'Url', 'URL', 'link', 'Link', 'LINK', '链接'],
            'keywords': ['keywords', 'Keywords', 'KEYWORDS', 'subject', 'Subject', 'SUBJECT', '关键词'],
            'document_type': ['type', 'Type', 'TYPE', 'document_type', 'DocumentType', '文献类型']
        }

    def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
        try:
            path = Path(file_path)
            if not path.exists():
                raise CSVError(f"文件不存在: {file_path}")

            with open(path, 'r', encoding='utf-8') as f:
                return self.parse_csv(f)
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return self.parse_csv(f)
            except Exception as e:
                raise CSVError(f"无法解码文件: {str(e)}")
        except Exception as e:
            raise CSVError(f"读取文件失败: {str(e)}")

    def parse_string(self, content: str) -> List[Dict[str, Any]]:
        try:
            return self.parse_csv(StringIO(content))
        except Exception as e:
            raise CSVError(f"解析CSV字符串失败: {str(e)}")

    def parse_csv(self, file_handle) -> List[Dict[str, Any]]:
        try:
            reader = csv.DictReader(file_handle)
            rows = list(reader)

            if not rows:
                return []

            column_map = self._map_columns(rows[0].keys())

            results = []
            for row in rows:
                normalized = self._normalize(row, column_map)
                if normalized and normalized.get('title'):
                    results.append(normalized)

            return results

        except csv.Error as e:
            raise CSVError(f"CSV解析错误: {str(e)}")
        except Exception as e:
            raise CSVError(f"读取CSV失败: {str(e)}")

    def _map_columns(self, columns: List[str]) -> Dict[str, str]:
        column_map = {}
        used_columns = set()

        for field, possible_names in self.column_mapping.items():
            for column in columns:
                if column in possible_names and column not in used_columns:
                    column_map[field] = column
                    used_columns.add(column)
                    break

            if field not in column_map:
                for column in columns:
                    if column not in used_columns:
                        column_map[field] = column
                        used_columns.add(column)
                        break

        return column_map

    def _normalize(self, row: Dict[str, str], column_map: Dict[str, str]) -> Dict[str, Any]:
        title = self._get_value(row, column_map, 'title')
        author_str = self._get_value(row, column_map, 'author')
        journal = self._get_value(row, column_map, 'journal')
        year_str = self._get_value(row, column_map, 'year')
        doi = self._get_value(row, column_map, 'doi')
        abstract = self._get_value(row, column_map, 'abstract')
        citations_str = self._get_value(row, column_map, 'citations')
        url = self._get_value(row, column_map, 'url')
        keywords_str = self._get_value(row, column_map, 'keywords')
        document_type = self._get_value(row, column_map, 'document_type')

        if doi and not url:
            url = f"https://doi.org/{doi}"

        return {
            'title': title,
            'authors': self._parse_authors(author_str),
            'journal': journal,
            'year': self._parse_year(year_str),
            'doi': doi,
            'abstract': abstract,
            'citations': self._parse_citations(citations_str),
            'source': 'CSV File',
            'url': url,
            'keywords': self._parse_keywords(keywords_str)[:10],
            'document_type': document_type.lower() if document_type else 'article'
        }

    def _get_value(self, row: Dict[str, str], column_map: Dict[str, str], field: str) -> str:
        column = column_map.get(field)
        if column and column in row:
            return row[column].strip()
        return ''

    def _parse_authors(self, author_str: str) -> List[str]:
        if not author_str:
            return []

        separators = [';', '|', '\\n', ', and ', ' and ']
        authors = [author_str]

        for sep in separators:
            if sep in author_str:
                authors = [a.strip() for a in author_str.split(sep)]
                break

        authors = [a for a in authors if a]
        return authors

    def _parse_year(self, year_str: str) -> Optional[int]:
        if not year_str:
            return None

        year_str = year_str.strip()

        try:
            return int(year_str)
        except ValueError:
            pass

        year_digits = ''.join(filter(str.isdigit, year_str[:4]))
        if year_digits:
            try:
                return int(year_digits)
            except ValueError:
                pass

        return None

    def _parse_citations(self, citations_str: str) -> int:
        if not citations_str:
            return 0

        citations_str = citations_str.strip()

        digits = ''.join(filter(str.isdigit, citations_str))
        if digits:
            try:
                return int(digits)
            except ValueError:
                pass

        return 0

    def _parse_keywords(self, keywords_str: str) -> List[str]:
        if not keywords_str:
            return []

        separators = [';', '|', '\\n', ',', ' and ']
        keywords = [keywords_str]

        for sep in separators:
            if sep in keywords_str:
                keywords = [k.strip() for k in keywords_str.split(sep)]
                break

        keywords = [k for k in keywords if k]
        return keywords
