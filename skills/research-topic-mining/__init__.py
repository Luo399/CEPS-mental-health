"""
Research Topic Mining Skill
Multi-disciplinary research topic mining tool for identifying emerging research trends and gaps
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from api_integrators import TopicMiner, PubMedAPI, arXivAPI, CrossrefAPI, GoogleScholarAPI
from data_processor import DataProcessor
from topic_analyzer import TopicAnalyzer
from output_generator import OutputGenerator

__all__ = [
    'TopicMiner',
    'PubMedAPI',
    'arXivAPI',
    'CrossrefAPI',
    'GoogleScholarAPI',
    'DataProcessor',
    'TopicAnalyzer',
    'OutputGenerator'
]