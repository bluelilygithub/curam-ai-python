from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import logging
import time
import json
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure CORS for your shared hosting domain
CORS(app, origins=[
    'https://curam-ai.com.au',
    'https://curam-ai.com.au/python-hub/',
    'https://curam-ai.com.au/ai-intelligence/',
    'http://localhost:3000',
    'http://localhost:8000',
    '*'  # Allow all for testing - remove in production
])

# Initialize database and LLM integration
db = None
llm_processor = None

try:
    from database import PropertyDatabase
    db = PropertyDatabase()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Database initialization failed: {str(e)}")
    db = None

try:
    from llm_integration import BrisbanePropertyLLM
    llm_processor = BrisbanePropertyLLM()
    logger.info("LLM processor initialized successfully")
except Exception as e:
    logger.error(f"LLM processor initialization failed: {str(e)}")
    llm_processor = None

# Preset Brisbane property questions
PRESET_QUESTIONS = [
    "What new development applications were submitted in Brisbane this month?",
    "Which Brisbane suburbs are trending in property news?",
    "Are there any major infrastructure projects affecting property values?",
    "What zoning changes have been approved recently?",
    "Which areas have the most development activity?"
]

@app.route('/')
def index():
    """Brisbane Property Intelligence API"""
    return jsonify({
        'name': 'Brisbane Property Intelligence API',
        'version': '1.0.0',
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'features': [
            'Real Claude Analysis',
            'Real Gemini Processing',
            'Brisbane Data Scraping',
            'Database Storage',
            'Query History'
        ],
        'services': {
            'database': 'connected' if db else 'disconnected',
            'claude': 'connected' if llm_processor and llm_processor.claude_client else 'disconnected',
            'gemini': 'connected' if llm_processor and llm_processor.gemini_model else 'disconnected'
        },
        'preset_questions': PRESET_QUESTIONS
    })

@app.route('/health')
def health():
    """Enhanced health check with all services"""
    try:
        # Test database connection
        database_stats = {}
        database_status = False
        
        if db:
            try:
                database_stats = db.get_database_stats()
                database_status = True
            except Exception as e:
                logger.error(f"Database health check failed: {str(e)}")
        
        # Check LLM services
        claude_status = llm_processor and llm_processor.claude_client is not None
        gemini_status = llm_processor and llm_processor.gemini_model is not None
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'python_version': sys.version.split()[0],
            'services': {
                'database': database_status,
                'claude': claude_status,
                'gemini': gemini_status,
                'llm_processor': llm_processor is not None
            },
            'database_stats': database_stats,
            'api_keys': {
                'claude_configured': bool(os.getenv('CLAUDE_API_KEY')),
                'gemini_configured': bool(os.getenv('GEMINI_API_KEY'))
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/property/questions', methods=['GET'])
def get_property_questions():
    """Get preset questions plus popular questions from database"""
    try:
        questions = []
        
        # Add preset questions
        for question in PRESET_QUESTIONS:
            questions.append({
                'question': question,
                'type': 'preset',
                'count': 0
            })
        
        # Add popular questions from database
        if db:
            try:
                popular = db.get_popular_questions(5)
                for item in popular:
                    if item['question'] not in PRESET_QUESTIONS:
                        questions.append({
                            'question': item['question'],
                            'type': 'popular',
                            'count': item['count']
                        })
            except Exception as e:
                logger.error(f"Failed to get popular questions: {str(e)}")
        
        return jsonify({
            'success': True,
            'questions': questions,
            'preset_questions': PRESET_QUESTIONS,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Get questions error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/property/analyze', methods=['POST'])
def analyze_property_question():
    """Analyze Brisbane property question using real LLM pipeline"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Question is required'
            }), 400
        
        # Determine question type
        question_type = 'preset' if question in PRESET_QUESTIONS else 'custom'
        
        logger.info(f"Processing property question: {question} (type: {question_type})")
        
        start_time = time.time()
        
        # Check if LLM processor is available
        if not llm_processor:
            return jsonify({
                'success': False,
                'error': 'LLM processor not available'
            }), 500
        
        # Stage 1: Claude Analysis
        logger.info("Stage 1: Analyzing with Claude...")
        claude_result = llm_processor.analyze_question_with_claude(question)
        
        # Stage 2: Data Scraping
        logger.info("Stage 2: Scraping Brisbane data...")
        scraped_data = llm_processor.scrape_brisbane_data(claude_result)
        
        # Stage 3: Gemini Processing
        logger.info("Stage 3: Processing with Gemini...")
        gemini_result = llm_processor.process_data_with_gemini(scraped_data, question, claude_result)
        
        processing_time = time.time() - start_time
        
        # Format final answer
        final_answer = format_final_answer(
            question=question,
            claude_result=claude_result,
            scraped_data=scraped_data,
            gemini_result=gemini_result,
            processing_time=processing_time
        )
        
        # Store in database
        query_id = None
        if db:
            try:
                query_id = db.store_query(
                    question=question,
                    answer=final_answer,
                    question_type=question_type,
                    processing_time=processing_time,
                    success=True
                )
            except Exception as e:
                logger.error(f"Failed to store query: {str(e)}")
        
        return jsonify({
            'success': True,
            'question': question,
            'question_type': question_type,
            'claude_analysis': claude_result,
            'scraped_sources': len(scraped_data),
            'gemini_processing': gemini_result,
            'final_answer': final_answer,
            'processing_time': round(processing_time, 2),
            'query_id': query_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Property analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/property/analyze-detailed', methods=['POST'])
def analyze_property_detailed():
    """Detailed analysis with step-by-step results"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Question is required'
            }), 400
        
        if not llm_processor:
            return jsonify({
                'success': False,
                'error': 'LLM processor not available'
            }), 500
        
        logger.info(f"Detailed analysis for: {question}")
        
        start_time = time.time()
        results = {}
        
        # Stage 1: Claude Analysis
        logger.info("Stage 1: Claude Analysis...")
        stage1_start = time.time()
        claude_result = llm_processor.analyze_question_with_claude(question)
        results['claude_analysis'] = {
            'result': claude_result,
            'processing_time': time.time() - stage1_start
        }
        
        # Stage 2: Data Scraping
        logger.info("Stage 2: Data Scraping...")
        stage2_start = time.time()
        scraped_data = llm_processor.scrape_brisbane_data(claude_result)
        results['data_scraping'] = {
            'sources_found': len(scraped_data),
            'data': scraped_data,
            'processing_time': time.time() - stage2_start
        }
        
        # Stage 3: Gemini Processing
        logger.info("Stage 3: Gemini Processing...")
        stage3_start = time.time()
        gemini_result = llm_processor.process_data_with_gemini(scraped_data, question, claude_result)
        results['gemini_processing'] = {
            'result': gemini_result,
            'processing_time': time.time() - stage3_start
        }
        
        total_time = time.time() - start_time
        
        return jsonify({
            'success': True,
            'question': question,
            'pipeline_results': results,
            'total_processing_time': round(total_time, 2),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Detailed analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/property/history', methods=['GET'])
def get_property_history():
    """Get query history from database"""
    try:
        if not db:
            return jsonify({
                'success': False,
                'error': 'Database not available'
            }), 500
        
        limit = request.args.get('limit', 50, type=int)
        history = db.get_query_history(limit)
        
        return jsonify({
            'success': True,
            'history': history,
            'count': len(history),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Get history error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/property/stats', methods=['GET'])
def get_property_stats():
    """Get database statistics"""
    try:
        if not db:
            return jsonify({
                'success': False,
                'error': 'Database not available'
            }), 500
        
        stats = db.get_database_stats()
        
        return jsonify({
            'success': True,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Get stats error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/property/reset', methods=['POST'])
def reset_property_database():
    """Reset database (clear all queries)"""
    try:
        if not db:
            return jsonify({
                'success': False,
                'error': 'Database not available'
            }), 500
        
        db.clear_all_data()
        
        return jsonify({
            'success': True,
            'message': 'Database reset successfully',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Reset database error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def format_final_answer(question: str, claude_result: Dict, scraped_data: List[Dict], 
                       gemini_result: Dict, processing_time: float) -> str:
    """Format the final answer combining all analysis stages"""
    
    # Extract key information
    claude_success = claude_result.get('success', False)
    gemini_success = gemini_result.get('success', False)
    
    # Build comprehensive answer
    answer = f"""# Brisbane Property Intelligence Analysis

## Query: {question}

## Executive Summary
{gemini_result.get('analysis', 'Analysis not available')}

## Analysis Methodology
- **Claude Analysis**: {'✅ Completed' if claude_success else '❌ Used fallback'}
- **Data Sources**: {len(scraped_data)} sources analyzed
- **Gemini Processing**: {'✅ Completed' if gemini_success else '❌ Used fallback'}
- **Processing Time**: {processing_time:.2f} seconds

## Data Sources Analyzed
"""
    
    # Add data sources
    for i, source in enumerate(scraped_data[:5], 1):
        answer += f"- **{source['source']}**: {source['title']}\n"
    
    if len(scraped_data) > 5:
        answer += f"- ... and {len(scraped_data) - 5} more sources\n"
    
    answer += f"""
## Analysis Strategy
{claude_result.get('analysis', {}).get('analysis_approach', 'Standard property analysis approach')}

## Key Brisbane Areas
{', '.join(claude_result.get('analysis', {}).get('brisbane_areas', ['Various Brisbane areas']))}

---
*Analysis completed on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*
"""
    
    return answer

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Brisbane Property Intelligence API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)