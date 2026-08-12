"""
Test suite for the Research Topic Mining skill
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock
from typing import Dict, Any

# Add the skill directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from __init__ import TopicMiner
from api_integrators import PubMedAPI, arXivAPI, CrossrefAPI, GoogleScholarAPI
from data_processor import DataProcessor
from topic_analyzer import TopicAnalyzer
from output_generator import OutputGenerator

class TestResearchTopicMining(unittest.TestCase):
    """Test cases for the Research Topic Mining skill"""

    def setUp(self):
        """Set up test fixtures"""
        self.topic_miner = TopicMiner()
        self.data_processor = DataProcessor()
        self.topic_analyzer = TopicAnalyzer()
        self.output_generator = OutputGenerator()

    @patch('api_integrators.PubMedAPI.search_publications')
    @patch('api_integrators.arXivAPI.search_preprints')
    @patch('api_integrators.CrossrefAPI.search_query')
    @patch('api_integrators.GoogleScholarAPI.search_scholar')
    def test_search_topics(self, mock_scholar, mock_crossref, mock_arxiv, mock_pubmed):
        """Test topic search functionality"""
        # Mock API responses
        mock_pubmed.return_value = []
        mock_arxiv.return_value = []
        mock_crossref.return_value = []
        mock_scholar.return_value = []

        # Test search
        result = self.topic_miner.search_topics(
            query="machine learning",
            discipline="computer_science"
        )

        # Verify result structure
        self.assertIn('topics', result)
        self.assertIn('trends', result)
        self.assertIn('gaps', result)
        self.assertIsInstance(result['topics'], list)
        self.assertIsInstance(result['trends'], dict)
        self.assertIsInstance(result['gaps'], list)

    def test_data_processor(self):
        """Test data processing functionality"""
        # Sample publication data
        publications = [
            {
                'title': 'Test Publication',
                'authors': ['Author 1', 'Author 2'],
                'journal': 'Test Journal',
                'year': 2023,
                'doi': '10.1234/test',
                'abstract': 'This is a test abstract.',
                'citations': 10,
                'keywords': ['test', 'sample', 'data']
            }
        ]

        # Test processing
        result = self.data_processor.process_publications(publications)

        # Verify processing results
        self.assertIn('publications', result)
        self.assertIn('processed_data', result)
        self.assertEqual(len(result['publications']), 1)
        self.assertIn('cleaned_text', result['publications'][0])
        self.assertIn('tokens', result['publications'][0])

    def test_topic_analyzer(self):
        """Test topic analysis functionality"""
        # Sample processed data
        processed_data = {
            'publications': [
                {
                    'title': 'Test Publication',
                    'cleaned_text': 'test publication text',
                    'tokens': ['test', 'publication', 'text'],
                    'year': 2023,
                    'citations': 10,
                    'discipline': 'computer_science'
                }
            ],
            'processed_data': {
                'publication_count': 1,
                'year_distribution': {2023: 1}
            }
        }

        # Test analysis
        result = self.topic_analyzer.analyze_topics(processed_data)

        # Verify analysis results
        self.assertIn('topics', result)
        self.assertIn('trends', result)
        self.assertIn('gaps', result)
        self.assertIsInstance(result['topics'], list)

    def test_output_generator(self):
        """Test output generation functionality"""
        # Sample analysis results
        analysis_results = {
            'topics': [
                {
                    'topic_id': 'topic_001',
                    'topic_name': 'Test Topic',
                    'keywords': ['test', 'topic', 'keywords'],
                    'emergence_score': 0.8,
                    'document_count': 10,
                    'avg_citations': 5,
                    'representative_documents': []
                }
            ],
            'trends': {
                'overall_growth': 0.5,
                'year_distribution': {2023: 10},
                'discipline_distribution': {'computer_science': 1.0}
            },
            'gaps': [
                {
                    'gap_id': 'gap_001',
                    'description': 'Test gap',
                    'urgency_score': 0.7
                }
            ]
        }

        # Test output generation
        result = self.output_generator.generate_output(analysis_results)

        # Verify output structure
        self.assertIn('metadata', result)
        self.assertIn('topics', result)
        self.assertIn('trends', result)
        self.assertIn('gaps', result)
        self.assertIn('visualization', result)
        self.assertIsInstance(result['topics'], list)
        self.assertIsInstance(result['trends'], dict)
        self.assertIsInstance(result['gaps'], list)

    def test_topic_miner_initialization(self):
        """Test TopicMiner initialization"""
        # Test that all components are initialized
        self.assertIsNotNone(self.topic_miner.pubmed)
        self.assertIsNotNone(self.topic_miner.arxiv)
        self.assertIsNotNone(self.topic_miner.crossref)
        self.assertIsNotNone(self.topic_miner.scholar)
        self.assertIsNotNone(self.topic_miner.data_processor)
        self.assertIsNotNone(self.topic_miner.topic_analyzer)
        self.assertIsNotNone(self.topic_miner.output_generator)

    def test_discipline_extraction(self):
        """Test discipline extraction from text"""
        # Test discipline extraction
        text = "Machine learning algorithms for medical diagnosis"
        discipline = self.data_processor.extract_discipline(text)
        self.assertEqual(discipline, 'biomedical')

        text = "Quantum computing and cryptography"
        discipline = self.data_processor.extract_discipline(text)
        self.assertEqual(discipline, 'computer_science')

    def test_trend_score_calculation(self):
        """Test trend score calculation"""
        # Test trend score calculation
        year_data = {2022: 100, 2023: 150, 2024: 200}
        trend_scores = self.data_processor.calculate_trend_scores(year_data)

        self.assertIn(2023, trend_scores)
        self.assertIn(2024, trend_scores)
        self.assertGreater(trend_scores[2024], trend_scores[2023])

    def test_output_validation(self):
        """Test output validation"""
        # Generate sample output
        sample_output = self.output_generator.generate_sample_output()

        # Test validation
        is_valid = self.output_generator.validate_output_structure(sample_output)
        self.assertTrue(is_valid)

    def test_detailed_report_generation(self):
        """Test detailed report generation"""
        # Generate sample output
        sample_output = self.output_generator.generate_sample_output()

        # Test report generation
        report = self.output_generator.generate_detailed_report(sample_output)
        self.assertIsInstance(report, str)
        self.assertIn("Research Topic Mining Analysis Report", report)

if __name__ == '__main__':
    unittest.main()