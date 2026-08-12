"""
Demo script for testing the Research Topic Mining skill
"""

import sys
import os
from typing import Dict, Any

# Add the skill directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from __init__ import TopicMiner
from output_generator import OutputGenerator

def main():
    """Demo the research topic mining skill"""
    print("=== 西部陆海新通道铁海联运政策效应研究选题挖掘 ===\n")

    # Initialize the topic miner
    miner = TopicMiner()
    output_generator = OutputGenerator()

    # Search for related topics
    print("正在搜索相关研究主题...")
    result = miner.search_topics(
        query="西部陆海新通道 铁海联运 政策效应",
        discipline="social_sciences",  # 社会科学领域
        time_period="last_2_years",
        max_results=150
    )

    # Generate detailed report
    report = output_generator.generate_detailed_report(result)
    print(report)

    # Save output to file
    output_file = "western_channel_research_topics.json"
    output_generator.save_output_to_file(result, output_file)
    print(f"\n详细分析结果已保存到: {output_file}")

    # Display sample topics
    print("\n=== 推荐的研究选题 ===")
    for i, topic in enumerate(result.get('topics', [])[:5]):  # Top 5 topics
        print(f"\n{i+1}. {topic.get('topic_name', 'Unknown Topic')}")
        print(f"   emergence_score: {topic.get('emergence_score', 0):.2f}")
        print(f"   trend: {topic.get('trend', 'unknown')}")
        print(f"   publications: {topic.get('publication_count', 0)}")
        print(f"   related_disciplines: {', '.join(topic.get('related_disciplines', []))}")

        # Display key papers if available
        if topic.get('key_papers'):
            print("   key_papers:")
            for paper in topic.get('key_papers', [])[:2]:  # Top 2 papers
                print(f"     - {paper.get('title', 'Unknown')}")

if __name__ == "__main__":
    main()