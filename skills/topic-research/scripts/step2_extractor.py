"""
步骤2：信息提取 (Information Extraction)
对采集的文献进行深度阅读分析，提取：
- 研究问题
- 研究内容
- 研究方法
- 创新点
- 研究结论
- 局限性
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import argparse

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@dataclass
class ExtractedPaper:
    """提取后的文献数据结构"""
    id: str
    title: str
    research_question: str       # 研究问题
    research_content: str        # 研究内容
    methods: str                 # 研究方法
    innovations: str             # 创新点
    conclusions: str             # 研究结论
    limitations: str             # 局限性（若无则为空


class InformationExtractor:
    """信息提取器"""

    def __init__(self, output_dir: str = "."):
        self.output_dir = output_dir
        self.extracted_papers: List[ExtractedPaper] = []

    def extract_from_json(self, input_file: str) -> List[Dict]:
        """从JSON文件读取文献数据"""
        filepath = os.path.join(self.output_dir, input_file)

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"文件不存在: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return data.get('papers', [])

    def extract_paper_info(self, paper: Dict[str, Any]) -> ExtractedPaper:
        """
        使用LLM提取文献关键信息

        这里使用模拟方法，实际需要调用LLM API
        """
        paper_id = paper.get('id', 'unknown')
        title = paper.get('title', '')
        abstract = paper.get('abstract', '')

        # 构建prompt
        prompt = self._build_extraction_prompt(title, abstract)

        # 调用LLM提取信息（这里使用模拟）
        extracted = self._simulate_llm_extraction(paper_id, title, abstract)

        return extracted

    def _build_extraction_prompt(self, title: str, abstract: str) -> str:
        """构建信息提取的prompt"""
        prompt = f"""请仔细阅读以下学术论文摘要，并提取关键信息：

论文标题：{title}

摘要：{abstract}

请提取以下信息（用中文回答）：
1. 研究问题：这篇论文试图回答什么问题？
2. 研究内容：具体研究了什么？
3. 研究方法：使用了什么方法/技术/模型？
4. 创新点：与现有研究相比的独特贡献是什么？
5. 研究结论：主要发现和结论是什么？
6. 局限性：研究存在哪些不足（如果没有则回答"无"）？

请以JSON格式输出：
{{
    "research_question": "...",
    "research_content": "...",
    "methods": "...",
    "innovations": "...",
    "conclusions": "...",
    "limitations": "..."
}}"""
        return prompt

    def _simulate_llm_extraction(
        self,
        paper_id: str,
        title: str,
        abstract: str
    ) -> ExtractedPaper:
        """
        模拟LLM提取（实际使用时替换为真实LLM调用）
        """
        # 实际实现中，这里应该调用LLM API
        # 例如：使用Anthropic API / OpenAI API

        # 模拟提取结果
        # 实际使用时需要根据论文内容真实提取

        # 提取标题中的关键词用于生成模拟内容
        keywords = title.lower().replace(":", " ").replace(",", " ").split()[:5]

        return ExtractedPaper(
            id=paper_id,
            title=title,
            research_question=f"探索{keywords[0] if keywords else '该主题'}的关键技术和方法",
            research_content=f"针对{keywords[0] if keywords else '研究主题'}进行深入分析和探索",
            methods="采用深度学习/机器学习/统计分析等方法",
            innovations="提出了新的算法/模型/框架，在性能上优于现有方法",
            conclusions=f"实验结果表明，该方法在{keywords[0] if keywords else '相关'}任务上取得了显著改进",
            limitations="数据规模和计算资源的限制"
        )

    def extract_batch(
        self,
        papers: List[Dict[str, Any]],
        show_progress: bool = True
    ) -> List[ExtractedPaper]:
        """
        批量提取文献信息

        Args:
            papers: 文献列表
            show_progress: 是否显示进度

        Returns:
            提取后的文献列表
        """
        extracted = []
        total = len(papers)

        for i, paper in enumerate(papers):
            if show_progress:
                print(f"[{i+1}/{total}] 提取中: {paper.get('title', '')[:50]}...")

            try:
                extracted_paper = self.extract_paper_info(paper)
                extracted.append(extracted_paper)
            except Exception as e:
                print(f"  提取失败: {e}")
                # 添加空记录
                extracted.append(ExtractedPaper(
                    id=paper.get('id', f'paper_{i}'),
                    title=paper.get('title', ''),
                    research_question="提取失败",
                    research_content="",
                    methods="",
                    innovations="",
                    conclusions="",
                    limitations=""
                ))

        self.extracted_papers = extracted
        return extracted

    def extract(
        self,
        input_file: str = "step1_literature_collection.json"
    ) -> Dict[str, Any]:
        """
        主提取方法

        Args:
            input_file: 步骤1输出的JSON文件名

        Returns:
            提取结果字典
        """
        print(f"\n{'='*50}")
        print("步骤2：信息提取")
        print(f"输入文件: {input_file}")
        print(f"{'='*50}\n")

        # 读取步骤1的数据
        papers = self.extract_from_json(input_file)
        print(f"共读取 {len(papers)} 篇文献\n")

        # 批量提取
        extracted = self.extract_batch(papers)

        # 统计
        success_count = sum(1 for e in extracted if e.research_question != "提取失败")

        # 构建输出
        result = {
            "extraction_time": datetime.now().isoformat(),
            "input_file": input_file,
            "papers": [asdict(e) for e in extracted],
            "summary": {
                "total_papers": len(papers),
                "successfully_extracted": success_count,
                "failed": len(papers) - success_count
            }
        }

        return result

    def save_result(self, result: Dict[str, Any], filename: str = None) -> str:
        """保存结果到文件"""
        if filename is None:
            filename = "step2_information_extraction.json"

        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"\n[保存] 结果已保存到: {filepath}")
        return filepath


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="文献信息提取工具")
    parser.add_argument("-i", "--input", type=str,
                       default="step1_literature_collection.json",
                       help="步骤1输出的JSON文件")
    parser.add_argument("-o", "--output", type=str, default=".",
                       help="输出目录")
    parser.add_argument("-f", "--output-file", type=str,
                       default="step2_information_extraction.json",
                       help="输出文件名")

    args = parser.parse_args()

    # 创建提取器
    extractor = InformationExtractor(output_dir=args.output)

    # 执行提取
    result = extractor.extract(input_file=args.input)

    # 保存结果
    extractor.save_result(result, args.output_file)

    # 打印摘要
    print(f"\n{'='*50}")
    print("提取完成！")
    print(f"总文献数: {result['summary']['total_papers']}")
    print(f"成功提取: {result['summary']['successfully_extracted']}")
    print(f"提取失败: {result['summary']['failed']}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()