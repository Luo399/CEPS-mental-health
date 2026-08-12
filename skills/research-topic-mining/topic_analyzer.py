"""
Topic Analyzer Module
Implements NLP-based topic modeling and trend analysis
"""

import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict
import pandas as pd
from datetime import datetime

class TopicAnalyzer:
    """Topic modeling and analysis for academic publications"""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.lda_model = None
        self.kmeans_model = None
        self.num_topics = 10
        self.random_state = 42

    def analyze_topics(self, processed_data: Dict) -> Dict:
        """Analyze topics from processed publication data"""
        publications = processed_data.get('publications', [])
        features = processed_data.get('processed_data', {})

        if not publications:
            return {"topics": [], "trends": {}, "gaps": []}

        # Create text corpus
        corpus = [pub.get('cleaned_text', '') for pub in publications]

        # Topic modeling
        topics = self._perform_topic_modeling(corpus, publications)

        # Trend analysis
        trends = self._analyze_trends(publications, features)

        # Gap detection
        gaps = self._detect_gaps(topics, trends)

        return {
            "topics": topics,
            "trends": trends,
            "gaps": gaps
        }

    def _perform_topic_modeling(self, corpus: List[str], publications: List[Dict]) -> List[Dict]:
        """Perform topic modeling using LDA and clustering"""
        if not corpus:
            return []

        # Vectorize text
        tfidf_matrix = self.vectorizer.fit_transform(corpus)

        # Determine optimal number of topics using silhouette score
        optimal_topics = self._find_optimal_topics(tfidf_matrix)

        # Train LDA model
        self.lda_model = LatentDirichletAllocation(
            n_components=optimal_topics,
            random_state=self.random_state,
            max_iter=10,
            learning_method='online'
        )
        topic_distribution = self.lda_model.fit_transform(tfidf_matrix)

        # Get feature names
        feature_names = self.vectorizer.get_feature_names_out()

        # Extract topics
        topics = []
        for topic_idx, topic in enumerate(self.lda_model.components_):
            top_words = [feature_names[i] for i in topic.argsort()[:-10 - 1:-1]]
            topic_docs = self._get_documents_for_topic(topic_distribution, topic_idx)

            topics.append({
                "topic_id": f"topic_{topic_idx:03d}",
                "topic_name": " ".join(top_words[:3]),  # Use top 3 words as name
                "keywords": top_words,
                "representative_documents": topic_docs[:5],  # Top 5 documents
                "document_count": sum(1 for doc in topic_distribution[:, topic_idx] if doc > 0.3),
                "avg_citations": self._calculate_avg_citations(topic_distribution, topic_idx, publications),
                "emergence_score": self._calculate_emergence_score(topic_distribution, topic_idx, publications)
            })

        return topics

    def _find_optimal_topics(self, tfidf_matrix: np.ndarray) -> int:
        """Find optimal number of topics using silhouette score"""
        max_topics = min(15, tfidf_matrix.shape[0] // 2)
        best_score = -1
        best_n = self.num_topics

        for n_topics in range(2, max_topics + 1):
            kmeans = KMeans(n_clusters=n_topics, random_state=self.random_state)
            labels = kmeans.fit_predict(tfidf_matrix.toarray())
            score = silhouette_score(tfidf_matrix.toarray(), labels)

            if score > best_score:
                best_score = score
                best_n = n_topics

        return best_n

    def _get_documents_for_topic(self, topic_distribution: np.ndarray, topic_idx: int,
                              threshold: float = 0.3) -> List[Dict]:
        """Get documents strongly associated with a topic"""
        topic_docs = []
        for doc_idx, distribution in enumerate(topic_distribution):
            if distribution[topic_idx] > threshold:
                topic_docs.append({
                    "doc_id": doc_idx,
                    "score": distribution[topic_idx]
                })

        # Sort by score and get top documents
        topic_docs.sort(key=lambda x: x['score'], reverse=True)
        return topic_docs[:10]  # Return top 10 documents

    def _calculate_avg_citations(self, topic_distribution: np.ndarray, topic_idx: int,
                              publications: List[Dict]) -> float:
        """Calculate average citations for documents in a topic"""
        total_citations = 0
        count = 0

        for doc_idx, distribution in enumerate(topic_distribution):
            if distribution[topic_idx] > 0.3:  # Documents strongly associated with topic
                total_citations += publications[doc_idx].get('citations', 0)
                count += 1

        return total_citations / count if count > 0 else 0

    def _calculate_emergence_score(self, topic_distribution: np.ndarray, topic_idx: int,
                               publications: List[Dict]) -> float:
        """Calculate emergence score based on recent publications"""
        current_year = datetime.now().year
        recent_years = [current_year - 1, current_year]  # Last 2 years

        recent_count = 0
        total_count = 0

        for doc_idx, distribution in enumerate(topic_distribution):
            if distribution[topic_idx] > 0.3:
                total_count += 1
                pub_year = publications[doc_idx].get('year', 0)
                if pub_year in recent_years:
                    recent_count += 1

        return recent_count / total_count if total_count > 0 else 0

    def _analyze_trends(self, publications: List[Dict], features: Dict) -> Dict:
        """Analyze publication trends and citation patterns"""
        if not publications:
            return {"overall_growth": 0, "discipline_distribution": {}}

        # Extract year data
        year_counts = defaultdict(int)
        for pub in publications:
            year = pub.get('year', 0)
            if year > 0:
                year_counts[year] += 1

        # Calculate trend scores
        trend_scores = {}
        years = sorted(year_counts.keys())
        if len(years) >= 2:
            for i in range(1, len(years)):
                prev_year = years[i-1]
                curr_year = years[i]
                growth = (year_counts[curr_year] - year_counts[prev_year]) / year_counts[prev_year] if year_counts[prev_year] > 0 else 0
                trend_scores[curr_year] = max(0, growth)

        # Calculate overall growth
        if years:
            first_year = years[0]
            last_year = years[-1]
            total_growth = (year_counts[last_year] - year_counts[first_year]) / year_counts[first_year] if year_counts[first_year] > 0 else 0
        else:
            total_growth = 0

        # Discipline distribution
        discipline_dist = {}
        for pub in publications:
            discipline = pub.get('discipline')
            if discipline:
                discipline_dist[discipline] = discipline_dist.get(discipline, 0) + 1

        # Normalize discipline distribution
        if discipline_dist:
            total = sum(discipline_dist.values())
            discipline_dist = {k: v/total for k, v in discipline_dist.items()}

        return {
            "overall_growth": total_growth,
            "year_distribution": dict(year_counts),
            "trend_scores": trend_scores,
            "discipline_distribution": discipline_dist,
            "citation_stats": features.get('citation_stats', {})
        }

    def _detect_gaps(self, topics: List[Dict], trends: Dict) -> List[Dict]:
        """Detect potential research gaps"""
        gaps = []

        # Identify topics with low emergence but high citation potential
        for topic in topics:
            emergence = topic.get('emergence_score', 0)
            citations = topic.get('avg_citations', 0)

            if emergence < 0.3 and citations > 50:  # Low emergence but high citation impact
                gaps.append({
                    "gap_id": f"gap_{len(gaps):03d}",
                    "description": f"Under-researched area: {topic['topic_name']}",
                    "urgency_score": 1 - emergence,
                    "potential_impact": "high",
                    "related_topic": topic['topic_id']
                })

        # Analyze trend patterns for gaps
        year_distribution = trends.get('year_distribution', {})
        if year_distribution:
            # Find years with sudden drops in publications
            years = sorted(year_distribution.keys())
            for i in range(1, len(years)):
                prev_year = years[i-1]
                curr_year = years[i]
                prev_count = year_distribution[prev_year]
                curr_count = year_distribution[curr_year]

                if prev_count > 0 and curr_count < prev_count * 0.5:  # Significant drop
                    gaps.append({
                        "gap_id": f"gap_{len(gaps):03d}",
                        "description": f"Sudden drop in publications around {curr_year}",
                        "urgency_score": 0.8,
                        "potential_impact": "medium",
                        "trend_anomaly": True
                    })

        return gaps

    def create_topic_network(self, topics: List[Dict], publications: List[Dict]) -> Dict:
        """Create network of topics and their relationships"""
        G = nx.Graph()

        # Add topics as nodes
        for topic in topics:
            G.add_node(topic['topic_id'], type='topic', name=topic['topic_name'])

        # Add publications as nodes
        for i, pub in enumerate(publications):
            pub_id = f"pub_{i}"
            G.add_node(pub_id, type='publication', title=pub.get('title', ''))

        # Add edges between topics and publications
        for topic in topics:
            for doc in topic.get('representative_documents', []):
                pub_idx = doc['doc_id']
                pub_id = f"pub_{pub_idx}"
                if pub_id in G:
                    G.add_edge(topic['topic_id'], pub_id, weight=doc['score'])

        return {
            "nodes": list(G.nodes(data=True)),
            "edges": list(G.edges(data=True))
        }

    def visualize_trends(self, trends: Dict) -> plt.Figure:
        """Create visualization of trends"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

        # Plot publication trends
        year_distribution = trends.get('year_distribution', {})
        if year_distribution:
            years = sorted(year_distribution.keys())
            counts = [year_distribution[year] for year in years]
            ax1.plot(years, counts, marker='o')
            ax1.set_title('Publication Trends Over Time')
            ax1.set_xlabel('Year')
            ax1.set_ylabel('Number of Publications')
            ax1.grid(True)

        # Plot discipline distribution
        discipline_dist = trends.get('discipline_distribution', {})
        if discipline_dist:
            disciplines = list(discipline_dist.keys())
            proportions = list(discipline_dist.values())
            ax2.bar(discipline_dist.keys(), proportions)
            ax2.set_title('Discipline Distribution')
            ax2.set_xlabel('Discipline')
            ax2.set_ylabel('Proportion')
            ax2.tick_params(axis='x', rotation=45)

        plt.tight_layout()
        return fig

    def calculate_topic_similarity(self, topic1: List[str], topic2: List[str]) -> float:
        """Calculate similarity between two topics using Jaccard similarity"""
        set1 = set(topic1)
        set2 = set(topic2)
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union > 0 else 0

    def cluster_similar_topics(self, topics: List[Dict]) -> List[List[Dict]]:
        """Cluster similar topics together"""
        if len(topics) < 2:
            return [topics]

        # Calculate similarity matrix
        similarity_matrix = np.zeros((len(topics), len(topics)))
        for i, topic1 in enumerate(topics):
            for j, topic2 in enumerate(topics):
                if i != j:
                    similarity = self.calculate_topic_similarity(
                        topic1['keywords'], topic2['keywords']
                    )
                    similarity_matrix[i, j] = similarity

        # Cluster using hierarchical clustering
        from scipy.cluster.hierarchy import linkage, fcluster
        Z = linkage(similarity_matrix, method='ward')
        clusters = fcluster(Z, t=0.5, criterion='distance')

        # Group topics by cluster
        cluster_groups = defaultdict(list)
        for i, cluster_id in enumerate(clusters):
            cluster_groups[cluster_id].append(topics[i])

        return list(cluster_groups.values())

    def identify_influential_papers(self, publications: List[Dict],
                               top_n: int = 10) -> List[Dict]:
        """Identify influential papers based on citations"""
        sorted_pubs = sorted(publications, key=lambda x: x.get('citations', 0), reverse=True)
        return sorted_pubs[:top_n]