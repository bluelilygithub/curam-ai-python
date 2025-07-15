from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import logging
import time
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

# Initialize database (with error handling)
db = None
try:
    from database import PropertyDatabase
    db = PropertyDatabase()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Database initialization failed: {str(e)}")
    db = None

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
            'Database Storage',
            'Query History',
            'Brisbane Property Questions',
            'Ready for LLM Integration'
        ],
        'database_status': 'connected' if db else 'disconnected',
        'preset_questions': PRESET_QUESTIONS
    })

@app.route('/health')
def health():
    """Enhanced health check with database status"""
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
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'python_version': sys.version.split()[0],
            'services': {
                'database': database_status,
                'claude_api': bool(os.getenv('CLAUDE_API_KEY')),
                'gemini_api': bool(os.getenv('GEMINI_API_KEY'))
            },
            'database_stats': database_stats
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
    """Analyze Brisbane property question (enhanced mock for now)"""
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
        
        # Simulate processing time
        start_time = time.time()
        time.sleep(1)  # Simulate processing
        
        # Generate enhanced mock answer based on question
        answer = generate_mock_answer(question)
        
        processing_time = time.time() - start_time
        
        # Store in database
        query_id = None
        if db:
            try:
                query_id = db.store_query(
                    question=question,
                    answer=answer,
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
            'answer': answer,
            'processing_time': round(processing_time, 2),
            'query_id': query_id,
            'timestamp': datetime.now().isoformat(),
            'next_step': 'LLM integration (Claude + Gemini) coming next'
        })
        
    except Exception as e:
        logger.error(f"Property analysis error: {str(e)}")
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

def generate_mock_answer(question: str) -> str:
    """Generate contextual mock answers for Brisbane property questions"""
    question_lower = question.lower()
    
    if 'development' in question_lower and 'application' in question_lower:
        return """# Brisbane Development Applications - January 2025

## Recent Applications Submitted

**Major Projects:**
- **South Brisbane Mixed-Use Tower** - 45-story development at 123 Main Street, South Brisbane
  - 400 residential units + commercial space
  - Application A/24/001234 submitted January 10, 2025
  - Currently under council review

- **Fortitude Valley Residential** - 28-story tower at James Street, Fortitude Valley  
  - 220 apartments with ground floor retail
  - Application A/24/001235 submitted January 8, 2025
  - Public consultation period open

## Development Activity Summary
- **This month:** 12 new applications submitted
- **Total value:** $240M in proposed developments
- **Focus areas:** South Brisbane, Fortitude Valley, New Farm

*Analysis complete - Next: Add real Brisbane City Council RSS feed integration*"""
    
    elif 'suburb' in question_lower and 'trending' in question_lower:
        return """# Trending Brisbane Suburbs - January 2025

## Current Market Leaders

**🔥 Paddington** - 15% quarterly growth
- Character housing driving demand
- Average price: $1.2M
- Days on market: 18 days

**📈 New Farm** - 12% quarterly growth  
- Riverfront premium locations
- Strong apartment market
- Infrastructure benefits from CRR

**⚡ Teneriffe** - 11% quarterly growth
- Industrial heritage conversions
- Young professional demographic
- Excellent connectivity

## Market Drivers
- Cross River Rail proximity
- Character housing scarcity
- Infrastructure investment

*Analysis complete - Next: Add real property news RSS integration*"""
    
    elif 'infrastructure' in question_lower:
        return """# Brisbane Infrastructure Projects - Property Impact Analysis

## Major Active Projects

**🚆 Cross River Rail** - $5.4B investment
- **Stations:** Woolloongabba, Boggo Road, Exhibition
- **Property impact:** 20-30% value uplift within 800m of stations
- **Timeline:** 2025 completion

**🌉 Brisbane Metro** - $1.2B investment
- **Route:** Eight Mile Plains to Roma Street
- **Property impact:** Improved connectivity boosting apartment demand
- **Timeline:** 2024 operational

**🏗️ Queen's Wharf** - $3.6B development
- **Impact:** South Brisbane gentrification accelerating
- **Property flow-on:** Residential demand in surrounding areas
- **Timeline:** 2025 full completion

## Investment Implications
Properties within 1km of major infrastructure seeing 15-25% premium over market average.

*Analysis complete - Next: Add real Queensland Government data integration*"""
    
    elif 'zoning' in question_lower:
        return """# Brisbane Zoning Changes - January 2025

## Recently Approved Changes

**🏢 Fortitude Valley Precinct**
- **Change:** Low-medium density to High density residential
- **Impact:** Enables 15+ story developments
- **Area:** James Street corridor
- **Approval date:** December 2024

**🏘️ Paddington Character Area**
- **Change:** Updated character overlays
- **Impact:** Balanced development vs heritage protection
- **Area:** Latrobe Terrace precinct
- **Approval date:** January 2025

## Implications for Property
- **Developers:** New opportunities in Fortitude Valley
- **Investors:** Character areas maintain value stability
- **Residents:** Managed growth with heritage protection

*Analysis complete - Next: Add real Brisbane City Council planning data*"""
    
    else:
        return f"""# Brisbane Property Analysis: {question}

## Current Market Overview
Brisbane's property market continues showing strong fundamentals with sustained growth across multiple sectors.

## Key Trends
- **Development Activity:** Strong pipeline of residential and mixed-use projects
- **Infrastructure Impact:** Cross River Rail and Brisbane Metro driving growth
- **Market Dynamics:** Balanced supply/demand with selective growth areas

## Areas of Interest
- **South Brisbane:** Major development hub
- **Fortitude Valley:** High-density residential focus  
- **New Farm/Teneriffe:** Premium riverfront market
- **Paddington:** Character housing premium

## Investment Implications
Strategic opportunities exist in infrastructure-adjacent areas with strong development pipelines.

*This is an enhanced mock response. Next step: Real LLM integration with Claude and Gemini for deeper analysis.*"""

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Brisbane Property Intelligence API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)