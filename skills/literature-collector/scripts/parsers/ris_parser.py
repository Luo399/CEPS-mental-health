from pathlib import Path
from typing import List, Dict, Any, Optional


class RISError(Exception):
    pass


class RISParser:
    def __init__(self):
        self.field_mapping = {
            'TY': 'document_type',
            'TI': 'title',
            'AU': 'author',
            'A1': 'author',
            'A2': 'author',
            'A3': 'author',
            'JO': 'journal',
            'JF': 'journal',
            'JA': 'journal',
            'T2': 'journal',
            'Y1': 'year',
            'PY': 'year',
            'Y2': 'year',
            'DO': 'doi',
            'N2': 'doi',
            'AB': 'abstract',
            'N1': 'abstract',
            'N2': 'abstract',
            'KW': 'keyword',
            'K1': 'keyword',
            'K2': 'keyword',
            'K3': 'keyword',
            'UR': 'url',
            'M3': 'url',
            'AD': 'address',
            'C1': 'notes'
        }

        self.type_mapping = {
            'JOUR': 'article',
            'JFULL': 'article',
            'MGZN': 'magazine',
            'NEWS': 'news',
            'CONF': 'conference',
            'CHAP': 'book-chapter',
            'BOOK': 'book',
            'THES': 'thesis',
            'RPRT': 'report',
            'DATA': 'dataset',
            'COMP': 'software',
            'GEN': 'generic',
            'ELEC': 'electronic',
            'UNPB': 'unpublished'
        }

    def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
        try:
            path = Path(file_path)
            if not path.exists():
                raise RISError(f"文件不存在: {file_path}")

            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            return self.parse_string(content)
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                return self.parse_string(content)
            except Exception as e:
                raise RISError(f"无法解码文件: {str(e)}")
        except Exception as e:
            raise RISError(f"读取文件失败: {str(e)}")

    def parse_string(self, content: str) -> List[Dict[str, Any]]:
        entries = []
        current_entry = {}
        multi_field = None
        multi_value = []

        for line in content.split('\n'):
            line = line.rstrip()

            if not line:
                if current_entry and (current_entry.get('title') or current_entry.get('TY')):
                    entries.append(self._normalize(current_entry))
                    current_entry = {}
                    multi_field = None
                    multi_value = []
                continue

            if len(line) < 6 or line[2] != ' ' or line[4] != '-':
                if multi_field:
                    line = line.lstrip()
                    if line:
                        multi_value.append(line)
                continue

            tag = line[:2].upper()
            value = line[6:].strip() if len(line) > 6 else ''

            if tag == 'ER' or tag == 'EF':
                if multi_field and multi_value:
                    self._add_field(current_entry, multi_field, multi_value)
                    multi_field = None
                    multi_value = []

                if current_entry and (current_entry.get('title') or current_entry.get('TY')):
                    entries.append(self._normalize(current_entry))
                    current_entry = {}
                continue

            if tag in self.field_mapping:
                if multi_field and multi_value:
                    self._add_field(current_entry, multi_field, multi_value)
                    multi_field = None
                    multi_value = []

                mapped_field = self.field_mapping[tag]

                if tag == 'AU' or tag == 'A1' or tag == 'A2' or tag == 'A3':
                    if 'authors' not in current_entry:
                        current_entry['authors'] = []
                    current_entry['authors'].append(value)
                elif tag == 'KW' or tag == 'K1' or tag == 'K2' or tag == 'K3':
                    if 'keywords' not in current_entry:
                        current_entry['keywords'] = []
                    keywords = [kw.strip() for kw in value.split(';') if kw.strip()]
                    current_entry['keywords'].extend(keywords)
                elif tag == 'AB' or tag == 'N1' or tag == 'N2':
                    multi_field = 'abstract'
                    multi_value = [value]
                else:
                    self._add_field(current_entry, mapped_field, value)

        if multi_field and multi_value:
            self._add_field(current_entry, multi_field, multi_value)

        if current_entry and (current_entry.get('title') or current_entry.get('TY')):
            entries.append(self._normalize(current_entry))

        return entries

    def _add_field(self, entry: Dict[str, Any], field: str, value: Any) -> None:
        if field == 'document_type':
            if not value:
                entry[field] = 'article'
            else:
                entry[field] = self.type_mapping.get(value.upper(), value.lower())
        else:
            entry[field] = value

    def _normalize(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        title = entry.get('title', '')
        authors = entry.get('authors', [])
        journal = entry.get('journal', '')
        year = self._extract_year(entry)
        doi = entry.get('doi', '')
        abstract = entry.get('abstract', '')
        keywords = entry.get('keywords', [])
        doc_type = entry.get('document_type', 'article')
        url = entry.get('url', '')

        if doi and not url:
            url = f"https://doi.org/{doi}"

        return {
            'title': title,
            'authors': authors,
            'journal': journal,
            'year': year,
            'doi': doi,
            'abstract': abstract,
            'citations': 0,
            'source': 'RIS File',
            'url': url,
            'keywords': keywords[:10],
            'document_type': doc_type
        }

    def _extract_year(self, entry: Dict[str, Any]) -> Optional[int]:
        year_field = entry.get('year', '')

        if not year_field:
            return None

        if isinstance(year_field, int):
            return year_field

        year_str = str(year_field).strip()

        if year_str.isdigit():
            try:
                return int(year_str)
            except ValueError:
                pass

        year_match = ''.join(filter(str.isdigit, year_str[:4]))
        if year_match:
            try:
                return int(year_match)
            except ValueError:
                pass

        return None
