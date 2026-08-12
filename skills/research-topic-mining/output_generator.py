"""
Output Generator Module
Generates structured JSON output for research topic mining results
"""

import json
import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class Topic:
    """Represents a research topic with metadata"""
    topic_id: str
    topic_name: str
    keywords: List[str]
    emergence_score: float
    trend: str
    publication_count: int
    citation_growth: float
    research_gap_score: float
    key_papers: List[str]
    related_disciplines: List[str]

@dataclass
class Trend:
    """Represents trend analysis data"""
    overall_growth: float
    year_distribution: Dict[int, int]
    trend_scores: Dict[int, float]
    discipline_distribution: Dict[str, float]
    citation_stats: Dict[str, float]

@dataclass
class ResearchGap:
    """Represents a detected research gap"""
    gap_id: str
    description: str
    urgency_score: float
    potential_impact: str

@dataclass
class TimeSeriesData:
    """Represents time series data for visualization"""
    dates: List[str]
    values: List[float]

@dataclass
class NetworkNode:
    """Represents a node in the topic network"""
    id: str
    type: str
    name: Optional[str] = None
    title: Optional[str] = None

@dataclass
class NetworkEdge:
    """Represents an edge in the topic network"""
    source: str
    target: str
    weight: float

class OutputGenerator:
    """Generates structured JSON output for research topic mining results"""

    def __init__(self):
        self.current_time = datetime.now().isoformat()

    def generate_output(self, analysis_results: Dict) -> Dict:
        """Generate structured JSON output from analysis results"""
        topics = analysis_results.get('topics', [])
        trends = analysis_results.get('trends', {})
        gaps = analysis_results.get('gaps', [])

        # Convert topics to dataclass format
        topic_objects = [self._create_topic_object(topic) for topic in topics]

        # Create trend object
        trend_object = self._create_trend_object(trends)

        # Create gap objects
        gap_objects = [self._create_gap_object(gap) for gap in gaps]

        # Create visualization data
        visualization_data = self._create_visualization_data(trends, topics)

        output = {
            "metadata": {
                "generated_at": self.current_time,
                "analysis_version": "1.0",
                "total_topics": len(topic_objects),
                "total_gaps": len(gap_objects)
            },
            "topics": [asdict(topic) for topic in topic_objects],
            "trends": asdict(trend_object),
            "gaps": [asdict(gap) for gap in gap_objects],
            "visualization": visualization_data
        }

        return output

    def _create_topic_object(self, topic_data: Dict) -> Topic:
        """Create Topic dataclass from topic data"""
        # Determine trend based on emergence score
        emergence = topic_data.get('emergence_score', 0)
        if emergence > 0.7:
            trend = "increasing"
        elif emergence > 0.4:
            trend = "stable"
        else:
            trend = "decreasing"

        # Extract related disciplines (simplified - in real implementation would analyze keywords)
        related_disciplines = self._extract_related_disciplines(topic_data.get('keywords', []))

        return Topic(
            topic_id=topic_data.get('topic_id', ''),
            topic_name=topic_data.get('topic_name', ''),
            keywords=topic_data.get('keywords', []),
            emergence_score=emergence,
            trend=trend,
            publication_count=topic_data.get('document_count', 0),
            citation_growth=topic_data.get('avg_citations', 0),
            research_gap_score=topic_data.get('emergence_score', 0) * 0.8,  # Simplified calculation
            key_papers=topic_data.get('representative_documents', [])[:3],  # Top 3 papers
            related_disciplines=related_disciplines
        )

    def _create_trend_object(self, trends_data: Dict) -> Trend:
        """Create Trend dataclass from trend data"""
        return Trend(
            overall_growth=trends_data.get('overall_growth', 0),
            year_distribution=trends_data.get('year_distribution', {}),
            trend_scores=trends_data.get('trend_scores', {}),
            discipline_distribution=trends_data.get('discipline_distribution', {}),
            citation_stats=trends_data.get('citation_stats', {})
        )

    def _create_gap_object(self, gap_data: Dict) -> ResearchGap:
        """Create ResearchGap dataclass from gap data"""
        return ResearchGap(
            gap_id=gap_data.get('gap_id', ''),
            description=gap_data.get('description', ''),
            urgency_score=gap_data.get('urgency_score', 0),
            potential_impact=gap_data.get('potential_impact', 'medium')
        )

    def _create_visualization_data(self, trends_data: Dict, topics_data: List[Dict]) -> Dict:
        """Create visualization data for output"""
        # Time series data for publication trends
        year_distribution = trends_data.get('year_distribution', {})
        if year_distribution:
            years = sorted(year_distribution.keys())
            publication_counts = [year_distribution[year] for year in years]
            time_series = TimeSeriesData(
                dates=[str(year) for year in years],
                values=publication_counts
            )
        else:
            time_series = TimeSeriesData(dates=[], values=[])

        # Network data (simplified - would be generated from topic relationships)
        network_nodes = []
        network_edges = []

        # Add topic nodes
        for topic in topics_data:
            network_nodes.append(NetworkNode(
                id=topic.get('topic_id', ''),
                type='topic',
                name=topic.get('topic_name', '')
            ))

        visualization_data = {
            "time_series": asdict(time_series),
            "network": {
                "nodes": [asdict(node) for node in network_nodes],
                "edges": [asdict(edge) for edge in network_edges]
            }
        }

        return visualization_data

    def _extract_related_disciplines(self, keywords: List[str]) -> List[str]:
        """Extract related disciplines from keywords"""
        discipline_keywords = {
            'computer_science': ['ai', 'machine', 'learning', 'algorithm', 'software', 'computing'],
            'biomedical': ['medicine', 'biology', 'genetics', 'protein', 'cell', 'disease'],
            'physics': ['quantum', 'particle', 'relativity', 'mechanics', 'thermodynamics'],
            'mathematics': ['algebra', 'calculus', 'geometry', 'statistics', 'probability'],
            'engineering': ['mechanical', 'electrical', 'civil', 'chemical', 'industrial'],
            'technology': ['innovation', 'development', 'implementation', 'design', 'prototype'],
            'social_sciences': ['sociology', 'psychology', 'economics', 'political', 'anthropology'],
            'humanities': ['literature', 'history', 'philosophy', 'art', 'culture', 'language'],
            'chemistry': ['molecule', 'compound', 'reaction', 'element', 'organic', 'inorganic'],
            'materials_science': ['nanomaterial', 'composite', 'polymer', 'crystal', 'structure']
        }

        related_disciplines = set()
        keywords_lower = [kw.lower() for kw in keywords]

        for discipline, kw_list in discipline_keywords.items():
            if any(kw in keywords_lower for kw in kw_list):
                related_disciplines.add(discipline)

        return list(related_disciplines)

    def generate_detailed_report(self, output_data: Dict) -> str:
        """Generate a detailed text report from the output data"""
        report = []

        report.append("=== Research Topic Mining Analysis Report ===")
        report.append(f"Generated: {output_data.get('metadata', {}).get('generated_at', 'N/A')}")
        report.append(f"Total Topics Identified: {output_data.get('metadata', {}).get('total_topics', 0)}")
        report.append(f"Research Gaps Detected: {output_data.get('metadata', {}).get('total_gaps', 0)}")
        report.append("")

        # Top emerging topics
        report.append("=== Top Emerging Topics ===")
        for topic in output_data.get('topics', [])[:5]:  # Top 5 topics
            report.append(f"• {topic.get('topic_name', 'Unknown')}")
            report.append(f"  Emergence Score: {topic.get('emergence_score', 0):.2f}")
            report.append(f"  Trend: {topic.get('trend', 'unknown')}")
            report.append(f"  Publications: {topic.get('publication_count', 0)}")
            report.append(f"  Related Disciplines: {', '.join(topic.get('related_disciplines', []))}")
            report.append("")

        # Research gaps
        report.append("=== Potential Research Gaps ===")
        for gap in output_data.get('gaps', [])[:3]:  # Top 3 gaps
            report.append(f"• {gap.get('description', 'Unknown')}")
            report.append(f"  Urgency: {gap.get('urgency_score', 0):.2f}")
            report.append(f"  Impact: {gap.get('potential_impact', 'medium')}")
            report.append("")

        # Overall trends
        report.append("=== Overall Trends ===")
        trends = output_data.get('trends', {})
        report.append(f"Overall Growth: {trends.get('overall_growth', 0):.2f}")
        report.append("Top Disciplines:")
        for discipline, proportion in list(trends.get('discipline_distribution', {}).items())[:3]:
            report.append(f"  • {discipline}: {proportion:.2%}")

        return "\n".join(report)

    def save_output_to_file(self, output_data: Dict, filename: str) -> None:
        """Save output to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

    def validate_output_structure(self, output_data: Dict) -> bool:
        """Validate that output structure matches expected format"""
        required_fields = ['metadata', 'topics', 'trends', 'gaps', 'visualization']
        return all(field in output_data for field in required_fields)

    def generate_sample_output(self) -> Dict:
        """Generate sample output for documentation and testing"""
        sample_topics = [
            {
                "topic_id": "topic_001",
                "topic_name": "AI in drug discovery",
                "keywords": ["ai", "drug", "discovery", "machine", "learning"],
                "emergence_score": 0.92,
                "document_count": 342,
                "avg_citations": 45,
                "representative_documents": [
                    {"doc_id": 0, "score": 0.95},
                    {"doc_id": 1, "score": 0.88}
                ]
            }
        ]

        sample_trends = {
            "overall_growth": 0.68,
            "year_distribution": {2022: 120, 2023: 180, 2024: 250},
            "discipline_distribution": {"biomedical": 0.42, "computer_science": 0.35}
        }

        sample_gaps = [
            {
                "gap_id": "gap_001",
                "description": "Lack of studies on AI applications in rare disease research",
                "urgency_score": 0.85
            }
        ]

        return self.generate_output({
            "topics": sample_topics,
            "trends": sample_trends,
            "gaps": sample_gaps
        })