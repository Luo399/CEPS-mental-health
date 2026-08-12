import re
from pathlib import Path
from typing import List, Dict, Any, Optional


class BibTeXError(Exception):
    pass


class BibTeXParser:
    def __init__(self):
        self.entry_pattern = re.compile(r'@([a-zA-Z0-9]+)\s*{([^}]+)},?\s*', re.MULTILINE | re.DOTALL)
        self.field_pattern = re.compile(r'([a-zA-Z0-9]+)\s*=\s*(.+?)\s*(?=,\s*[a-zA-Z0-9]+\s*=|\s*})', re.DOTALL)
        self.brace_pattern = re.compile(r'^\s*{.*}\s*$', re.DOTALL)
        self.quote_pattern = re.compile(r'^\s*".*"\s*$')

    def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
        try:
            path = Path(file_path)
            if not path.exists():
                raise BibTeXError(f"文件不存在: {file_path}")

            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            return self.parse_string(content)
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                return self.parse_string(content)
            except Exception as e:
                raise BibTeXError(f"无法解码文件: {str(e)}")
        except Exception as e:
            raise BibTeXError(f"读取文件失败: {str(e)}")

    def parse_string(self, content: str) -> List[Dict[str, Any]]:
        content = self._preprocess(content)

        results = []
        for match in self.entry_pattern.finditer(content):
            entry_type = match.group(1)
            entry_key = match.group(2).strip()

            entry_start = match.end()
            entry_end = self._find_entry_end(content, entry_start)

            entry_content = content[entry_start:entry_end]
            fields = self._parse_fields(entry_content)

            if fields and self._is_valid_entry(fields):
                normalized = self._normalize(entry_type, entry_key, fields)
                if normalized:
                    results.append(normalized)

        return results

    def _preprocess(self, content: str) -> str:
        content = re.sub(r'%.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'\n\s+', ' ', content)
        return content

    def _find_entry_end(self, content: str, start: int) -> int:
        brace_count = 0
        i = start

        while i < len(content):
            char = content[i]

            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    return i

            i += 1

        return len(content)

    def _parse_fields(self, content: str) -> Dict[str, str]:
        fields = {}

        for match in self.field_pattern.finditer(content):
            field_name = match.group(1).lower()
            field_value = match.group(2).strip()

            field_value = self._clean_value(field_value)

            if field_name and field_value:
                fields[field_name] = field_value

        return fields

    def _clean_value(self, value: str) -> str:
        value = value.strip()

        if self.brace_pattern.match(value):
            value = value[1:-1].strip()
            value = re.sub(r'\s+', ' ', value)
        elif self.quote_pattern.match(value):
            value = value[1:-1].strip()

        value = value.rstrip(',').strip()

        value = re.sub(r'\{\s*', '', value)
        value = re.sub(r'\s*\}', '', value)

        return value

    def _is_valid_entry(self, fields: Dict[str, str]) -> bool:
        return 'title' in fields and bool(fields['title'])

    def _normalize(self, entry_type: str, entry_key: str, fields: Dict[str, str]) -> Dict[str, Any]:
        title = fields.get('title', '')
        author = fields.get('author', '')
        journal = fields.get('journal', fields.get('journaltitle', fields.get('publisher', '')))
        year = self._extract_year(fields)
        doi = fields.get('doi', '')
        abstract = fields.get('abstract', fields.get('note', ''))
        keywords = self._extract_keywords(fields)

        return {
            'title': title,
            'authors': self._parse_authors(author),
            'journal': journal,
            'year': year,
            'doi': doi,
            'abstract': abstract,
            'citations': 0,
            'source': 'BibTeX File',
            'url': f"https://doi.org/{doi}" if doi else '',
            'keywords': keywords[:10],
            'document_type': entry_type.lower(),
            'entry_key': entry_key
        }

    def _extract_year(self, fields: Dict[str, str]) -> Optional[int]:
        year_field = fields.get('year', '')
        if not year_field:
            year_field = fields.get('date', '')

        if not year_field:
            return None

        year_match = re.search(r'\d{4}', year_field)
        if year_match:
            try:
                return int(year_match.group())
            except ValueError:
                pass

        return None

    def _extract_keywords(self, fields: Dict[str, str]) -> List[str]:
        keywords = fields.get('keywords', '')
        if not keywords:
            keywords = fields.get('subject', '')
        if not keywords:
            keywords = fields.get('keyword', '')

        if not keywords:
            return []

        keyword_list = re.split(r'[;,]\s*', keywords)
        keyword_list = [kw.strip() for kw in keyword_list if kw.strip()]

        return keyword_list

    def _parse_authors(self, author_str: str) -> List[str]:
        if not author_str:
            return []

        authors = re.split(r'\s+and\s+', author_str)
        authors = [self._clean_author(author) for author in authors]
        authors = [author for author in authors if author]

        return authors

    def _clean_author(self, author: str) -> str:
        author = author.strip()

        author = re.sub(r'^\s*\{?', '', author)
        author = re.sub(r'\}?\s*$', '', author)

        author = re.sub(r'\s+', ' ', author)

        return author.strip()
