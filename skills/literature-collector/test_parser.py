#!/usr/bin/env python3
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

from parsers.bibtex_parser import BibTeXParser

def main():
    file_path = r"C:\Users\张亮\Downloads\test_references.bib"

    print(f"测试文件: {file_path}")

    parser = BibTeXParser()
    results = parser.parse_file(file_path)

    print(f"\n解析结果数: {len(results)}")

    if results:
        print("\n第一个文献:")
        print(json.dumps(results[0], indent=2, ensure_ascii=False))
    else:
        print("无结果")

if __name__ == '__main__':
    main()
