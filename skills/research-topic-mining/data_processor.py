"""
Data Processor Module
Handles data cleaning, normalization, and preprocessing
"""

import re
import nltk
from typing import List, Dict, Any, Optional
from collections import defaultdict
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

class DataProcessor:
    """Data processing and preprocessing for academic publications"""

    def __init__(self):
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('punkt')
            nltk.download('stopwords')
            nltk.download('wordnet')

        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.valid_disciplines = {
            'computer_science', 'biomedical', 'physics', 'mathematics',
            'engineering', 'technology', 'social_sciences', 'humanities',
            'chemistry', 'materials_science', 'environmental_science'
        }

    def process_publications(self, publications: List[Dict]) -> Dict:
        """Process and clean publication data"""
        if not publications:
            return {"publications": [], "processed_data": {}}

        # Convert to DataFrame for easier processing
        df = pd.DataFrame(publications)

        # Data cleaning
        df = self._clean_data(df)

        # Text preprocessing
        df = self._preprocess_text(df)

        # Extract features
        features = self._extract_features(df)

        return {
            "publications": df.to_dict('records'),
            "processed_data": features
        }

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate publication data"""
        # Remove duplicates
        df = df.drop_duplicates(subset=['doi'], keep='first')

        # Filter by year (keep recent publications)
        current_year = pd.Timestamp.now().year
        df = df[df['year'] >= current_year - 10]  # Keep last 10 years

        # Remove entries with missing critical information
        df = df.dropna(subset=['title', 'year', 'journal'])

        # Validate discipline (if available)
        if 'discipline' in df.columns:
            df = df[df['discipline'].isin(self.valid_disciplines)]

        return df

    def _preprocess_text(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess text data (title, abstract, keywords)"""
        # Combine text fields for analysis
        df['combined_text'] = df['title'].fillna('') + ' ' + df['abstract'].fillna('') + ' ' + ' '.join(df['keywords'].fillna(''))

        # Text cleaning functions
        def clean_text(text: str) -> str:
            # Convert to lowercase
            text = text.lower()
            # Remove special characters and numbers
            text = re.sub(r'[^a-zA-Z\s]', '', text)
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            return text

        # Apply text cleaning
        df['cleaned_text'] = df['combined_text'].apply(clean_text)

        # Tokenization and lemmatization
        def tokenize_and_lemmatize(text: str) -> List[str]:
            tokens = word_tokenize(text)
            lemmatized = [self.lemmatizer.lemmatize(token) for token in tokens
                         if token not in self.stop_words and len(token) > 2]
            return lemmatized

        df['tokens'] = df['cleaned_text'].apply(tokenize_and_lemmatize)

        return df

    def _extract_features(self, df: pd.DataFrame) -> Dict:
        """Extract features for topic analysis"""
        features = {
            "publication_count": len(df),
            "year_distribution": df['year'].value_counts().to_dict(),
            "journal_distribution": df['journal'].value_counts().head(10).to_dict(),
            "citation_stats": {
                "mean_citations": df['citations'].mean(),
                "median_citations": df['citations'].median(),
                "max_citations": df['citations'].max()
            },
            "text_stats": {
                "avg_tokens_per_doc": df['tokens'].apply(len).mean(),
                "total_unique_tokens": len(set().union(*df['tokens'].tolist()))
            }
        }

        return features

    def normalize_citations(self, citations: List[int]) -> List[float]:
        """Normalize citation counts for comparison"""
        if not citations:
            return []

        max_citations = max(citations)
        if max_citations == 0:
            return [0.0] * len(citations)

        return [c / max_citations for c in citations]

    def extract_discipline(self, text: str) -> Optional[str]:
        """Extract discipline from text using keyword matching"""
        discipline_keywords = {
            'computer_science': ['machine learning', 'deep learning', 'algorithm', 'programming', 'software', 'computing'],
            'biomedical': ['medicine', 'biology', 'genetics', 'protein', 'cell', 'disease', 'clinical'],
            'physics': ['quantum', 'particle', 'relativity', 'mechanics', 'thermodynamics', 'optics'],
            'mathematics': ['algebra', 'calculus', 'geometry', 'statistics', 'probability', 'equation'],
            'engineering': ['mechanical', 'electrical', 'civil', 'chemical', 'industrial', 'systems'],
            'technology': ['innovation', 'development', 'implementation', 'design', 'prototype', 'testing'],
            'social_sciences': ['sociology', 'psychology', 'economics', 'political', 'anthropology', 'education'],
            'humanities': ['literature', 'history', 'philosophy', 'art', 'culture', 'language'],
            'chemistry': ['molecule', 'compound', 'reaction', 'element', 'organic', 'inorganic'],
            'materials_science': ['nanomaterial', 'composite', 'polymer', 'crystal', 'structure', 'property'],
            'environmental_science': ['climate', 'ecology', 'sustainability', 'pollution', 'conservation', 'renewable']
        }

        text_lower = text.lower()
        for discipline, keywords in discipline_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return discipline

        return None

    def create_corpus(self, publications: List[Dict]) -> List[str]:
        """Create text corpus for topic modeling"""
        corpus = []
        for pub in publications:
            text = f"{pub.get('title', '')} {pub.get('abstract', '')} {' '.join(pub.get('keywords', []))}"
            corpus.append(text)
        return corpus

    def calculate_trend_scores(self, year_data: Dict[int, int]) -> Dict[int, float]:
        """Calculate trend scores from year distribution data"""
        if not year_data:
            return {}

        years = sorted(year_data.keys())
        if len(years) < 2:
            return {years[0]: 1.0}

        scores = {}
        for i, year in enumerate(years):
            if i == 0:
                scores[year] = 0.0  # Base year
            else:
                prev_year = years[i-1]
                current_count = year_data[year]
                prev_count = year_data[prev_year]
                growth = (current_count - prev_count) / prev_count if prev_count > 0 else 0
                scores[year] = max(0, growth)

        # Normalize scores
        max_score = max(scores.values()) if scores else 1.0
        if max_score > 0:
            scores = {year: score / max_score for year, score in scores.items()}

        return scores

    def detect_outliers(self, data: List[float]) -> List[int]:
        """Detect outliers in numerical data using IQR method"""
        if len(data) < 3:
            return []

        q1 = pd.Series(data).quantile(0.25)
        q3 = pd.Series(data).quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        outliers = [i for i, value in enumerate(data) if value < lower_bound or value > upper_bound]
        return outliers

    def aggregate_by_discipline(self, publications: List[Dict]) -> Dict[str, Dict]:
        """Aggregate publications by discipline"""
        discipline_data = defaultdict(lambda: {
            'count': 0,
            'citations': [],
            'years': defaultdict(int)
        })

        for pub in publications:
            discipline = pub.get('discipline') or self.extract_discipline(pub.get('title', ''))
            if discipline:
                discipline_data[discipline]['count'] += 1
                discipline_data[discipline]['citations'].append(pub.get('citations', 0))
                discipline_data[discipline]['years'][pub.get('year', 0)] += 1

        # Calculate statistics for each discipline
        for discipline, data in discipline_data.items():
            data['avg_citations'] = sum(data['citations']) / len(data['citations']) if data['citations'] else 0
            data['trend_scores'] = self.calculate_trend_scores(data['years'])

        return dict(discipline_data)