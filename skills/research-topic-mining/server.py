"""
MCP Server for Research Topic Mining Skill
Implements the MCP server interface for the research topic mining skill
"""

import json
import os
import sys
import logging
from typing import Dict, Any, List, Optional
import argparse
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add the skill directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from __init__ import TopicMiner

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Research Topic Mining MCP Server",
    description="Multi-disciplinary research topic mining skill",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response validation
class SearchRequest(BaseModel):
    query: str
    discipline: str = "all"
    time_period: str = "last_2_years"
    max_results: int = 200

class MultiDisciplinaryRequest(BaseModel):
    topics: List[str]
    time_range: str = "2022-2024"

class GapDetectionRequest(BaseModel):
    discipline: str
    min_publications: int = 50
    time_period: str = "last_3_years"

class TopicResponse(BaseModel):
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

class TrendResponse(BaseModel):
    overall_growth: float
    year_distribution: Dict[int, int]
    trend_scores: Dict[int, float]
    discipline_distribution: Dict[str, float]
    citation_stats: Dict[str, float]

class GapResponse(BaseModel):
    gap_id: str
    description: str
    urgency_score: float
    potential_impact: str

class ResearchOutput(BaseModel):
    metadata: Dict[str, Any]
    topics: List[TopicResponse]
    trends: TrendResponse
    gaps: List[GapResponse]
    visualization: Dict[str, Any]

class ErrorResponse(BaseModel):
    error: str
    details: Optional[Dict] = None

# Initialize the topic miner
try:
    topic_miner = TopicMiner()
    logger.info("Topic Miner initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Topic Miner: {str(e)}")
    topic_miner = None

@app.post("/search", response_model=ResearchOutput, responses={400: {"model": ErrorResponse}})
async def search_topics(request: SearchRequest):
    """Search for research topics"""
    if not topic_miner:
        raise HTTPException(status_code=500, detail="Topic Miner not initialized")

    try:
        logger.info(f"Searching topics: query='{request.query}', discipline='{request.discipline}'")

        result = topic_miner.search_topics(
            query=request.query,
            discipline=request.discipline,
            time_period=request.time_period,
            max_results=request.max_results
        )

        # Convert the result to the response model
        research_output = ResearchOutput(**result)
        return research_output

    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/multidisciplinary", response_model=Dict[str, ResearchOutput], responses={400: {"model": ErrorResponse}})
async def analyze_multidisciplinary(request: MultiDisciplinaryRequest):
    """Analyze multiple topics across disciplines"""
    if not topic_miner:
        raise HTTPException(status_code=500, detail="Topic Miner not initialized")

    try:
        logger.info(f"Analyzing multidisciplinary topics: {request.topics}")

        result = topic_miner.analyze_multi_disciplinary(
            topics=request.topics,
            time_range=request.time_range
        )

        # Convert each result to the response model
        output = {}
        for topic, data in result.items():
            output[topic] = ResearchOutput(**data)

        return output

    except Exception as e:
        logger.error(f"Multidisciplinary analysis failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/gaps", response_model=ResearchOutput, responses={400: {"model": ErrorResponse}})
async def detect_gaps(request: GapDetectionRequest):
    """Detect research gaps"""
    if not topic_miner:
        raise HTTPException(status_code=500, detail="Topic Miner not initialized")

    try:
        logger.info(f"Detecting gaps: discipline='{request.discipline}'")

        result = topic_miner.detect_research_gaps(
            discipline=request.discipline,
            min_publications=request.min_publications,
            time_period=request.time_period
        )

        # Convert the result to the response model
        research_output = ResearchOutput(**result)
        return research_output

    except Exception as e:
        logger.error(f"Gap detection failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health", response_model=Dict[str, str])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "research-topic-mining"}

@app.get("/config", response_model=Dict[str, Any])
async def get_config():
    """Get current configuration"""
    return {
        "supported_disciplines": [
            "computer_science", "biomedical", "physics", "mathematics",
            "engineering", "technology", "social_sciences", "humanities",
            "chemistry", "materials_science", "environmental_science"
        ],
        "supported_time_periods": ["last_6_months", "last_year", "last_2_years", "last_3_years"],
        "version": "1.0.0"
    }

def start_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Start the MCP server"""
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Research Topic Mining MCP Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")

    args = parser.parse_args()
    start_server(host=args.host, port=args.port, reload=args.reload)