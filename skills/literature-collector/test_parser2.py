#!/usr/bin/env python3
import re

def test_bibtex_patterns():
    content = """@article{zhang2024,
  title={基于深度学习的图像识别方法研究},
  author={张三 and 李四 and 王五},
  journal={计算机学报},
  year={2024}
}"""

    entry_pattern = re.compile(r'@(\w+)\s*{([^}]+)},?\s*', re.MULTILINE | re.DOTALL)

    matches = list(entry_pattern.finditer(content))
    print(f"匹配到的条目数: {len(matches)}")

    for i, match in enumerate(matches):
        print(f"\n条目 {i+1}:")
        print(f"  类型: {match.group(1)}")
        print(f"  键: {match.group(2)}")
        print(f"  完整匹配: {match.group(0)}")

def test_content_read():
    import json
    from pathlib import Path
    file_path = r"C:\Users\张亮\Downloads\test_references.bib"

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        print(f"\n文件内容（前200字符）:")
        print(content[:200])
        print(f"\n包含@: {'@' in content}")
        print(f"包含article: {'article' in content}")
        print(f"包含book: {'book' in content}")

        entry_pattern = re.compile(r'@(\w+)\s*{([^}]+)},?\s*', re.MULTILINE | re.DOTALL)
        matches = list(entry_pattern.finditer(content))
        print(f"\n匹配到的条目数: {len(matches)}")

    except Exception as e:
        print(f"错误: {e}")

if __name__ == '__main__':
    print("测试正则表达式:")
    test_bibtex_patterns()
    print("\n" + "="*50 + "\n")
    print("测试文件读取:")
    test_content_read()
