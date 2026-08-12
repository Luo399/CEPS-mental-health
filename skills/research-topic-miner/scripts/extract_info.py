"""
信息提取脚本 - 从论文数据中提取关键信息
"""

import json
import re
from typing import List, Dict, Tuple
import yaml


class PaperInfoExtractor:
    """论文信息提取器"""

    def __init__(self):
        # 研究方法关键词库
        self.method_keywords = {
            "实证研究": [
                "实证",
                "empirical",
                "regression",
                "面板数据",
                "DID",
                "双重差分",
            ],
            "案例研究": ["案例", "case study", "案例分析", "单案例", "多案例"],
            "理论研究": ["理论", "theoretical", "模型构建", "理论框架"],
            "综述研究": ["综述", "review", "meta", "元分析", "系统综述"],
            "实验研究": ["实验", "experiment", "实验室", "随机对照"],
            "计量分析": ["计量", "econometric", "时间序列", "VAR", "GARCH"],
            "定性分析": ["定性", "qualitative", "访谈", "扎根理论"],
            "问卷调查": ["问卷", "survey", "量表", "SEM", "结构方程"],
            "机器学习": ["机器学习", "machine learning", "深度学习", "神经网络", "AI"],
            "空间分析": ["空间分析", "GIS", "空间计量", "地理加权"],
        }

        # 研究领域关键词库
        self.field_keywords = {
            "经济学": ["宏观经济", "微观经济", "经济增长", "产业发展", "贸易"],
            "管理学": ["企业管理", "战略管理", "人力资源", "组织行为", "营销"],
            "金融学": ["金融", "投资", "证券", "银行", "风险管理"],
            "区域经济学": ["区域经济", "城市经济", "产业集群", "区域创新"],
            "技术创新": ["创新", "技术进步", "R&D", "知识产权"],
            "可持续发展": ["绿色发展", "碳排放", "环境", "ESG", "可持续"],
            "数字经济": ["数字经济", "数字化", "人工智能", "大数据"],
        }

    def extract_all(self, papers: List[Dict]) -> List[Dict]:
        """提取所有论文的关键信息"""

        print(f"\n开始信息提取，共 {len(papers)} 篇论文...")

        extracted = []

        for i, paper in enumerate(papers):
            try:
                info = self.extract_paper_info(paper)
                extracted.append(info)

                if (i + 1) % 20 == 0:
                    print(f"  已处理 {i + 1}/{len(papers)} 篇")

            except Exception as e:
                print(f"  警告: 处理论文 {i} 时出错: {str(e)}")
                extracted.append(self._basic_info(paper))

        print(f"信息提取完成\n")

        return extracted

    def extract_paper_info(self, paper: Dict) -> Dict:
        """提取单篇论文信息"""

        # 基础信息
        title = paper.get("title", "")
        abstract = paper.get("abstract", "") or ""

        # 提取研究方法
        methods = self._extract_methods(title + " " + abstract)

        # 提取研究领域
        fields = self._extract_fields(title + " " + abstract)

        # 提取研究对象
        objects = self._extract_research_objects(title + " " + abstract)

        # 提取数据来源
        data_sources = self._extract_data_sources(abstract)

        # 提取核心创新点（简化版）
        innovation = self._extract_innovation(title, abstract)

        # 提取主要结论（简化版）
        conclusion = self._extract_conclusion(abstract)

        return {
            **self._basic_info(paper),
            "methods": methods,
            "fields": fields,
            "research_objects": objects,
            "data_sources": data_sources,
            "innovation": innovation,
            "conclusion": conclusion,
        }

    def _basic_info(self, paper: Dict) -> Dict:
        """基础信息"""
        return {
            "doi": paper.get("doi", ""),
            "title": paper.get("title", ""),
            "authors": paper.get("authors", []),
            "year": paper.get("year"),
            "journal": paper.get("journal", ""),
            "citations": paper.get("citations", 0),
            "source": paper.get("source", ""),
        }

    def _extract_methods(self, text: str) -> List[str]:
        """提取研究方法"""
        text = text.lower()
        methods = []

        for method, keywords in self.method_keywords.items():
            for kw in keywords:
                if kw.lower() in text:
                    if method not in methods:
                        methods.append(method)
                    break

        return methods if methods else ["其他"]

    def _extract_fields(self, text: str) -> List[str]:
        """提取研究领域"""
        text = text.lower()
        fields = []

        for field, keywords in self.field_keywords.items():
            for kw in keywords:
                if kw.lower() in text:
                    if field not in fields:
                        fields.append(field)
                    break

        return fields if fields else ["其他"]

    def _extract_research_objects(self, text: str) -> List[str]:
        """提取研究对象"""
        objects = []

        # 常见研究对象模式
        patterns = [
            (r"([\u4e00-\u9fa5]+)省", "省份"),
            (r"([\u4e00-\u9fa5]+)市", "城市"),
            (r"([\u4e00-\u9fa5]+)企业", "企业"),
            (r"([\u4e00-\u9fa5]+)行业", "行业"),
            (r"([\u4e00-\u9fa5]+)地区", "地区"),
        ]

        for pattern, obj_type in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) >= 2:  # 过滤单字
                    obj = f"{match}({obj_type})"
                    if obj not in objects:
                        objects.append(obj)

        return objects[:5]  # 最多5个

    def _extract_data_sources(self, abstract: str) -> List[str]:
        """提取数据来源"""
        data_sources = []

        # 常见数据库关键词
        db_keywords = {
            "统计年鉴": ["统计年鉴", "年鉴数据"],
            "CSMAR": ["CSMAR", "国泰安"],
            "CNRDS": ["CNRDS", "锐思"],
            "Wind": ["Wind", "万得"],
            "CEIC": ["CEIC", "环京"],
            "CHFS": ["CHFS", "微观调查"],
            "CHARLS": ["CHARLS", "老龄化"],
            "CFPS": ["CFPS", "家庭追踪"],
            "上市公司": ["上市公司", "A股", "IPO"],
            "海关数据": ["海关", "进出口"],
            "专利数据": ["专利", "知识产权"],
        }

        for source, keywords in db_keywords.items():
            for kw in keywords:
                if kw in abstract:
                    if source not in data_sources:
                        data_sources.append(source)
                    break

        return data_sources

    def _extract_innovation(self, title: str, abstract: str) -> str:
        """提取创新点摘要"""
        if not abstract:
            return ""

        # 简化: 取摘要前100字
        abstract = abstract.replace("\n", " ").strip()
        return abstract[:150] + "..." if len(abstract) > 150 else abstract

    def _extract_conclusion(self, abstract: str) -> str:
        """提取结论摘要"""
        if not abstract:
            return ""

        # 简化: 取摘要后50字
        abstract = abstract.replace("\n", " ").strip()
        return abstract[-100:] if len(abstract) > 100 else abstract

    def generate_summary(self, extracted: List[Dict]) -> Dict:
        """生成提取结果摘要"""

        # 统计研究方法分布
        method_counts = {}
        for paper in extracted:
            for m in paper.get("methods", []):
                method_counts[m] = method_counts.get(m, 0) + 1

        # 统计研究领域分布
        field_counts = {}
        for paper in extracted:
            for f in paper.get("fields", []):
                field_counts[f] = field_counts.get(f, 0) + 1

        # 统计年份分布
        year_counts = {}
        for paper in extracted:
            year = paper.get("year")
            if year:
                year_counts[year] = year_counts.get(year, 0) + 1

        return {
            "total_papers": len(extracted),
            "method_distribution": dict(
                sorted(method_counts.items(), key=lambda x: x[1], reverse=True)
            ),
            "field_distribution": dict(
                sorted(field_counts.items(), key=lambda x: x[1], reverse=True)
            ),
            "year_distribution": dict(sorted(year_counts.items(), reverse=True)),
        }


def main():
    """主函数 - 测试用"""

    # 读取采集的论文
    try:
        with open("collected_papers.json", "r", encoding="utf-8") as f:
            papers = json.load(f)
    except FileNotFoundError:
        print("错误: 请先运行 collect_papers.py 采集文献")
        return

    # 提取信息
    extractor = PaperInfoExtractor()
    extracted = extractor.extract_all(papers)

    # 保存结果
    with open("extracted_papers.json", "w", encoding="utf-8") as f:
        json.dump(extracted, f, ensure_ascii=False, indent=2)

    # 打印摘要
    summary = extractor.generate_summary(extracted)
    print("\n=== 信息提取摘要 ===")
    print(f"总论文数: {summary['total_papers']}")
    print(f"\n研究方法分布: {summary['method_distribution']}")
    print(f"\n研究领域分布: {summary['field_distribution']}")

    print("\n结果已保存到 extracted_papers.json")


if __name__ == "__main__":
    main()
