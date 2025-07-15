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

# Initialize LLM processor (with error handling)
llm_processor = None
try:
    from simple_llm import SimpleLLMProcessor
    llm_processor = SimpleLLMProcessor()
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
            'Database Storage',
            'Query History',
            'Brisbane Property Focus',
            'Multi-LLM Pipeline'
        ],
        'services': {
            'database': 'connected' if db else 'disconnected',
            'llm_processor': 'connected' if llm_processor else 'disconnected',
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

# -------------------------------------------------------------------------

# Add this endpoint to your app.py file

@app.route('/debug/run-claude-test', methods=['GET'])
def run_claude_debug():
    """Run the Claude debug test via web endpoint"""
    import io
    import contextlib
    
    # Capture the debug output
    output_buffer = io.StringIO()
    
    try:
        with contextlib.redirect_stdout(output_buffer):
            # Run the debug functions
            result = {
                'timestamp': datetime.now().isoformat(),
                'debug_output': [],
                'tests': {}
            }
            
            # Check environment
            print("🐍 Python Environment Check")
            print("=" * 30)
            print(f"Python version: {sys.version}")
            print(f"Current working directory: {os.getcwd()}")
            
            # Check API keys
            print("\n🔑 API Keys Check")
            print("=" * 20)
            
            claude_key = os.getenv('CLAUDE_API_KEY')
            gemini_key = os.getenv('GEMINI_API_KEY')
            
            if claude_key:
                print(f"✅ CLAUDE_API_KEY: {claude_key[:8]}...{claude_key[-4:]}")
                result['tests']['claude_key'] = 'found'
            else:
                print("❌ CLAUDE_API_KEY: Not found")
                result['tests']['claude_key'] = 'missing'
            
            if gemini_key:
                print(f"✅ GEMINI_API_KEY: {gemini_key[:8]}...{gemini_key[-4:]}")
                result['tests']['gemini_key'] = 'found'
            else:
                print("❌ GEMINI_API_KEY: Not found")
                result['tests']['gemini_key'] = 'missing'
            
            # Test Claude API
            print("\n🔍 Claude API Debug Test")
            print("=" * 50)
            
            if not claude_key:
                print("❌ Cannot test Claude - API key missing")
                result['tests']['claude_api'] = 'skipped_no_key'
            else:
                try:
                    import anthropic
                    print("✅ anthropic library imported successfully")
                    
                    client = anthropic.Anthropic(api_key=claude_key.strip())
                    print("✅ Claude client initialized")
                    
                    # Test working models from JS app
                    working_models = [
                        "claude-3-5-sonnet-20241022",
                        "claude-3-haiku-20240307",
                        "claude-3-sonnet-20240229"
                    ]
                    
                    successful_models = []
                    
                    for model_name in working_models:
                        print(f"\n🤖 Testing model: {model_name}")
                        try:
                            response = client.messages.create(
                                model=model_name,
                                max_tokens=50,
                                messages=[{"role": "user", "content": "Hello"}]
                            )
                            print(f"✅ SUCCESS: {model_name}")
                            successful_models.append(model_name)
                        except Exception as e:
                            print(f"❌ FAILED: {model_name} - {str(e)}")
                    
                    result['tests']['claude_api'] = {
                        'status': 'completed',
                        'successful_models': successful_models,
                        'total_tested': len(working_models)
                    }
                    
                    if successful_models:
                        print(f"\n✅ {len(successful_models)} Claude models working!")
                    else:
                        print("\n❌ No Claude models working")
                        
                except Exception as e:
                    print(f"❌ Claude test failed: {str(e)}")
                    result['tests']['claude_api'] = {'status': 'failed', 'error': str(e)}
            
            # Test Gemini for comparison
            print("\n🤖 Gemini API Comparison Test")
            print("=" * 35)
            
            if not gemini_key:
                print("❌ Cannot test Gemini - API key missing")
                result['tests']['gemini_api'] = 'skipped_no_key'
            else:
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=gemini_key.strip())
                    
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content("Hello")
                    print("✅ Gemini test successful!")
                    result['tests']['gemini_api'] = 'working'
                    
                except Exception as e:
                    print(f"❌ Gemini test failed: {e}")
                    result['tests']['gemini_api'] = {'status': 'failed', 'error': str(e)}
        
        # Get the captured output
        debug_output = output_buffer.getvalue()
        result['debug_output'] = debug_output.split('\n')
        
        return jsonify({
            'success': True,
            'result': result,
            'debug_text': debug_output
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'debug_output': output_buffer.getvalue().split('\n') if output_buffer else []
        }), 500


# -----------------------------------------------------------------------

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
    """Enhanced Brisbane property question analysis with LLM integration"""
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
        
        # Use LLM processor if available
        if llm_processor:
            try:
                # Use real LLM processing
                result = llm_processor.process_question(question)
                answer = result['final_answer']
                llm_status = result.get('processing_stages', {})
                llm_status['llm_available'] = True
                llm_status['claude_success'] = result.get('claude_result', {}).get('success', False)
                llm_status['gemini_success'] = result.get('gemini_result', {}).get('success', False)
            except Exception as e:
                logger.error(f"LLM processing failed: {str(e)}")
                answer = generate_mock_answer(question)
                llm_status = {'error': str(e), 'llm_available': False}
        else:
            # Use mock answer
            answer = generate_mock_answer(question)
            llm_status = {'note': 'LLM processor not available', 'llm_available': False}
        
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
            'llm_status': llm_status,
            'timestamp': datetime.now().isoformat()
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

@app.route('/api/property/test-llm', methods=['POST'])
def test_llm_integration():
    """Test LLM integration specifically"""
    try:
        data = request.get_json()
        question = data.get('question', 'What is the Brisbane property market like?')
        
        if not llm_processor:
            return jsonify({
                'success': False,
                'error': 'LLM processor not available'
            }), 500
        
        # Test Claude
        claude_result = llm_processor.analyze_with_claude(question)
        
        # Test Gemini
        gemini_result = llm_processor.process_with_gemini(question, claude_result['analysis'])
        
        return jsonify({
            'success': True,
            'question': question,
            'claude_test': {
                'success': claude_result['success'],
                'response': claude_result['analysis'][:200] + '...' if len(claude_result['analysis']) > 200 else claude_result['analysis'],
                'error': claude_result.get('error')
            },
            'gemini_test': {
                'success': gemini_result['success'],
                'response': gemini_result['analysis'][:200] + '...' if len(gemini_result['analysis']) > 200 else gemini_result['analysis'],
                'error': gemini_result.get('error')
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"LLM test error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def generate_mock_answer(question: str) -> str:
    """Generate enhanced mock answers when LLM is not available"""
    question_lower = question.lower()
    
    if 'development' in question_lower and 'application' in question_lower:
        return """# Brisbane Development Applications - January 2025

## Recent Applications Submitted

**Major Projects:**
- **South Brisbane Mixed-Use Tower** - 45-story development at 123 Main Street
  - 400 residential units + commercial space
  - Application A/24/001234 - Currently under council review
  - Estimated completion: 2026

- **Fortitude Valley Residential** - 28-story tower at James Street
  - 220 apartments with ground floor retail
  - Application A/24/001235 - Public consultation period open
  - Focus on young professional market

## Development Activity Summary
- **This month:** 12 new applications submitted
- **Total value:** $240M in proposed developments
- **Focus areas:** South Brisbane, Fortitude Valley, New Farm

## Market Implications
Strong development pipeline indicates continued confidence in Brisbane's inner-city residential market.

---
*Enhanced mock analysis - Full LLM integration will provide real-time Brisbane City Council data*"""
    
    elif 'suburb' in question_lower and 'trending' in question_lower:
        return """# Trending Brisbane Suburbs - January 2025

## Current Market Leaders

**🔥 Paddington** - 15% quarterly growth
- Character housing driving premium demand
- Average price: $1.2M (houses), $650K (units)
- Days on market: 18 days

**📈 New Farm** - 12% quarterly growth
- Riverfront premium locations
- Strong apartment market performance
- Cross River Rail proximity benefits

**⚡ Teneriffe** - 11% quarterly growth
- Industrial heritage conversions popular
- Young professional demographic
- Excellent connectivity to CBD

## Market Drivers
- Cross River Rail infrastructure investment
- Character housing scarcity
- CBD accessibility premium

## Investment Outlook
Inner-city Brisbane suburbs with character housing and infrastructure connectivity showing strongest growth momentum.

---
*Enhanced mock analysis - Full LLM integration will provide real-time property market data*"""
    
    elif 'infrastructure' in question_lower:
        return """# Brisbane Infrastructure Projects - Property Impact Analysis

## Major Active Projects

**🚆 Cross River Rail** - $5.4B investment
- **New Stations:** Woolloongabba, Boggo Road, Exhibition, Roma Street
- **Property impact:** 20-30% value uplift within 800m radius
- **Completion:** 2025

**🌉 Brisbane Metro** - $1.2B investment
- **Route:** Eight Mile Plains to Roma Street via Cultural Centre
- **Property impact:** Improved connectivity boosting apartment demand
- **Status:** Operational 2024

**🏗️ Queen's Wharf** - $3.6B development
- **Impact:** South Brisbane gentrification accelerating
- **Property flow-on:** Premium residential demand in surrounding areas
- **Timeline:** Full completion 2025

## Investment Implications
Properties within 1km of major infrastructure projects showing 15-25% premium over Brisbane market average.

---
*Enhanced mock analysis - Full LLM integration will provide real Queensland Government project data*"""
    
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

---
*Enhanced mock analysis - Full LLM integration will provide real Brisbane City Council planning data*"""
    
    else:
        return f"""# Brisbane Property Analysis: {question}

## Market Overview
Brisbane's property market demonstrates strong fundamentals with selective growth across key precincts.

## Key Insights
- **Development Pipeline:** Robust activity in inner-city areas
- **Infrastructure Impact:** Cross River Rail and Metro driving value growth
- **Market Dynamics:** Balanced supply/demand with infrastructure-led growth

## Strategic Areas
- **South Brisbane:** Major mixed-use development hub
- **Fortitude Valley:** High-density residential focus
- **New Farm/Teneriffe:** Premium riverfront market
- **Paddington:** Character housing premium market

## Professional Outlook
Brisbane property market positioned for continued growth driven by infrastructure investment and strategic urban development.

---
*Enhanced mock analysis - Full LLM integration will provide real-time multi-source data analysis*"""

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Brisbane Property Intelligence API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)