"""
Chinese/English text processing utilities for literature analysis.
Handles segmentation, keyword extraction, synonym mapping, and normalization.
"""

import re
from collections import Counter
from typing import Optional


# Management domain keyword synonym mapping (Chinese <-> English)
MANAGEMENT_SYNONYMS = {
    "数字化转型": "digital transformation",
    "组织韧性": "organizational resilience",
    "创新绩效": "innovation performance",
    "企业绩效": "firm performance",
    "公司治理": "corporate governance",
    "供应链管理": "supply chain management",
    "知识管理": "knowledge management",
    "战略联盟": "strategic alliance",
    "竞争优势": "competitive advantage",
    "组织学习": "organizational learning",
    "动态能力": "dynamic capability",
    "资源基础观": "resource-based view",
    "制度理论": "institutional theory",
    "交易成本": "transaction cost",
    "利益相关者": "stakeholder",
    "企业社会责任": "corporate social responsibility",
    "环境社会治理": "ESG",
    "平台经济": "platform economy",
    "共享经济": "sharing economy",
    "人工智能": "artificial intelligence",
    "大数据": "big data",
    "区块链": "blockchain",
    "创业导向": "entrepreneurial orientation",
    "服务创新": "service innovation",
    "商业模式": "business model",
    "组织变革": "organizational change",
    "领导力": "leadership",
    "团队效能": "team effectiveness",
    "员工敬业度": "employee engagement",
    "心理契约": "psychological contract",
    "组织承诺": "organizational commitment",
    "工作满意度": "job satisfaction",
    "绩效考核": "performance appraisal",
    "薪酬激励": "compensation incentive",
    "技术创新": "technological innovation",
    "开放式创新": "open innovation",
    "吸收能力": "absorptive capacity",
    "技术溢出": "technology spillover",
    "产业集群": "industrial cluster",
    "区域创新": "regional innovation",
    "数字经济": "digital economy",
    "绿色创新": "green innovation",
    "可持续发展": "sustainable development",
    "新质生产力": "new quality productive forces",
    "高质量发展": "high-quality development",
    "共同富裕": "common prosperity",
}

# Build reverse mapping (English -> Chinese)
EN_TO_ZH = {v: k for k, v in MANAGEMENT_SYNONYMS.items()}

# Chinese stopwords for management text processing
CHINESE_STOPWORDS = {
    "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个",
    "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好",
    "自己", "这", "他", "她", "它", "们", "那", "些", "什么", "如何", "为什么",
    "可以", "能够", "通过", "基于", "进行", "分析", "研究", "本文", "本文认为",
    "发现", "表明", "结果", "显示", "影响", "作用", "关系", "机制", "效应",
    "以及", "及其", "其中", "之间", "对", "从", "以", "为", "与", "及", "或",
    "但", "而", "且", "则", "将", "被", "由", "于", "中", "等",
}

# English stopwords
ENGLISH_STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "dare", "ought",
    "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
    "as", "into", "through", "during", "before", "after", "above", "below",
    "between", "out", "off", "over", "under", "again", "further", "then",
    "once", "and", "but", "or", "nor", "not", "so", "yet", "both",
    "either", "neither", "each", "every", "all", "any", "few", "more",
    "most", "other", "some", "such", "no", "only", "own", "same", "than",
    "too", "very", "just", "because", "if", "when", "where", "how",
    "what", "which", "who", "whom", "this", "that", "these", "those",
    "paper", "study", "research", "article", "result", "finding",
    "method", "approach", "analysis", "effect", "impact", "relationship",
}


def segment_chinese(text: str, use_jieba: bool = True) -> list:
    """Segment Chinese text into words.

    Tries jieba first; falls back to simple character-based segmentation.
    """
    if not text:
        return []

    if use_jieba:
        try:
            import jieba
            words = list(jieba.cut(text))
            return [w.strip() for w in words
                    if w.strip() and len(w.strip()) > 1
                    and w.strip() not in CHINESE_STOPWORDS]
        except ImportError:
            pass

    # Fallback: bigram-based segmentation for management terms
    words = []
    i = 0
    while i < len(text):
        # Try 4-char matches first (common in management terms)
        matched = False
        for length in [4, 3, 2]:
            if i + length <= len(text):
                candidate = text[i:i+length]
                if candidate in MANAGEMENT_SYNONYMS or len(candidate) >= 3:
                    if candidate not in CHINESE_STOPWORDS:
                        words.append(candidate)
                        i += length
                        matched = True
                        break
        if not matched:
            i += 1

    return words


def extract_noun_phrases(text: str, language: str = "en") -> list:
    """Extract noun phrases from text.

    For English: simple regex-based noun phrase extraction.
    For Chinese: use segment_chinese and filter noun-like terms.
    """
    if not text:
        return []

    if language == "zh":
        return segment_chinese(text)

    # English noun phrase extraction (simple regex approach)
    pattern = r'\b([A-Z][a-z]+(?:\s+[a-z]+){0,3})\b'
    phrases = re.findall(pattern, text)

    # Also extract multi-word terms with hyphens
    hyphenated = re.findall(r'\b[a-z]+-[a-z]+\b', text.lower())

    all_phrases = phrases + hyphenated
    return [p for p in all_phrases
            if p.lower() not in ENGLISH_STOPWORDS and len(p) > 2]


def normalize_keyword(keyword: str, language: Optional[str] = None) -> str:
    """Normalize a keyword: lowercase, strip, standardize."""
    kw = keyword.strip().lower()
    if language == "zh":
        return kw  # Don't lowercase Chinese
    return kw


def find_synonym_group(keyword: str) -> list:
    """Find all synonyms for a keyword (cross-language).

    Returns:
        List of synonymous keywords including the original
    """
    group = [keyword]

    kw_lower = keyword.lower().strip()

    # Check Chinese -> English mapping
    if kw_lower in MANAGEMENT_SYNONYMS:
        en_term = MANAGEMENT_SYNONYMS[kw_lower]
        if en_term not in group:
            group.append(en_term)

    # Check English -> Chinese mapping
    if kw_lower in EN_TO_ZH:
        zh_term = EN_TO_ZH[kw_lower]
        if zh_term not in group:
            group.append(zh_term)

    return group


def build_unified_keyword_space(keywords: list) -> dict:
    """Build a unified keyword space mapping Chinese/English synonyms.

    Args:
        keywords: List of keyword strings

    Returns:
        Dict mapping canonical_keyword -> list_of_variants
    """
    groups = {}
    assigned = set()

    # First pass: known synonym pairs
    for kw in keywords:
        kw_stripped = kw.strip()
        if kw_stripped in assigned:
            continue

        synonym_list = find_synonym_group(kw_stripped)
        canonical = kw_stripped  # Use first occurrence as canonical

        # Check if any synonym already has a group
        existing_canonical = None
        for s in synonym_list:
            for canon, members in groups.items():
                if s in members:
                    existing_canonical = canon
                    break
            if existing_canonical:
                break

        if existing_canonical:
            # Merge into existing group
            for s in synonym_list:
                if s not in groups[existing_canonical]:
                    groups[existing_canonical].append(s)
                assigned.add(s)
        else:
            groups[canonical] = synonym_list
            for s in synonym_list:
                assigned.add(s)

    return groups


def extract_keywords_tfidf(texts: list, top_n: int = 10) -> list:
    """Extract keywords using TF-IDF.

    Args:
        texts: List of text strings (abstracts)
        top_n: Number of keywords to extract

    Returns:
        List of (keyword, score) tuples
    """
    from collections import Counter
    import math

    if not texts:
        return []

    # Tokenize all texts
    tokenized = []
    for text in texts:
        tokens = extract_noun_phrases(text, "en") if re.match(r'[a-zA-Z]', text[:5]) else segment_chinese(text)
        tokenized.append(tokens)

    # Document frequency
    doc_freq = Counter()
    for tokens in tokenized:
        for token in set(tokens):
            doc_freq[token] += 1

    n_docs = len(tokenized)

    # TF-IDF scoring
    keyword_scores = Counter()
    for tokens in tokenized:
        tf = Counter(tokens)
        for term, count in tf.items():
            if doc_freq[term] < 2:  # Ignore terms in only 1 doc
                continue
            idf = math.log(n_docs / doc_freq[term])
            keyword_scores[term] += count * idf

    return keyword_scores.most_common(top_n)


def classify_methodology(abstract: str) -> str:
    """Classify paper methodology based on abstract text.

    Returns one of: empirical_quantitative, empirical_qualitative,
    theoretical, review, case_study, mixed
    """
    if not abstract:
        return "unknown"

    text = abstract.lower()

    # Review papers
    review_indicators = ["review", "literature review", "meta-analysis", "systematic review",
                         "综述", "文献回顾", "元分析"]
    if any(ind in text for ind in review_indicators):
        return "review"

    # Case study
    case_indicators = ["case study", "case analysis", "qualitative case",
                       "案例研究", "案例分析", "单案例", "多案例"]
    if any(ind in text for ind in case_indicators):
        return "case_study"

    # Empirical quantitative
    quant_indicators = ["regression", "structural equation", "sem", "survey",
                        "quantitative", "panel data", "econometric", "experiment",
                        "回归", "结构方程", "问卷", "面板数据", "计量", "实证",
                        "hierarchical linear", "multilevel model", "fsqca"]
    if any(ind in text for ind in quant_indicators):
        # Check if also qualitative
        qual_indicators = ["interview", "qualitative", "ethnograph", "grounded theory",
                          "访谈", "扎根理论", "民族志", "质性"]
        if any(ind in text for ind in qual_indicators):
            return "mixed"
        return "empirical_quantitative"

    # Empirical qualitative
    qual_indicators = ["interview", "qualitative", "ethnograph", "grounded theory",
                      "narrative", "phenomenolog", "访谈", "扎根理论", "民族志",
                      "质性研究", "叙事", "现象学"]
    if any(ind in text for ind in qual_indicators):
        return "empirical_qualitative"

    # Theoretical
    theory_indicators = ["theory", "conceptual", "framework", "model",
                         "理论", "概念", "框架", "模型构建", "命题"]
    if any(ind in text for ind in theory_indicators):
        return "theoretical"

    return "mixed"
