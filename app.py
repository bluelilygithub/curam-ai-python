from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import logging
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

@app.route('/')
def index():
    """Simple index endpoint"""
    return jsonify({
        'name': 'Brisbane Property Intelligence API',
        'version': '1.0.0',
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'message': 'API is working! Next step: add Brisbane Property Intelligence features'
    })

@app.route('/health')
def health():
    """Basic health check"""
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'python_version': sys.version.split()[0],
            'environment': {
                'claude_api_configured': bool(os.getenv('CLAUDE_API_KEY')),
                'gemini_api_configured': bool(os.getenv('GEMINI_API_KEY'))
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Test endpoint for Brisbane property questions
@app.route('/api/property/test', methods=['GET'])
def test_property_endpoint():
    """Test endpoint to verify property API structure"""
    preset_questions = [
        "What new development applications were submitted in Brisbane this month?",
        "Which Brisbane suburbs are trending in property news?",
        "Are there any major infrastructure projects affecting property values?",
        "What zoning changes have been approved recently?",
        "Which areas have the most development activity?"
    ]
    
    return jsonify({
        'success': True,
        'preset_questions': preset_questions,
        'message': 'Property API structure is ready',
        'timestamp': datetime.now().isoformat()
    })

# Simple test analysis endpoint (no LLM integration yet)
@app.route('/api/property/analyze', methods=['POST'])
def analyze_property_simple():
    """Simple analysis endpoint without LLM integration"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Question is required'
            }), 400
        
        # Simple mock response
        mock_answer = f"""Brisbane Property Analysis for: "{question}"

This is a mock response. The question has been received and would be processed through:
1. Claude analysis for strategy
2. Data scraping from Brisbane sources
3. Gemini processing for insights
4. Final formatted response

Next steps: Add LLM integration and database storage."""
        
        return jsonify({
            'success': True,
            'question': question,
            'answer': mock_answer,
            'timestamp': datetime.now().isoformat(),
            'note': 'This is a mock response. LLM integration coming next.'
        })
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Brisbane Property Intelligence API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)