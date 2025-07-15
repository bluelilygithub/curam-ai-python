from flask import Flask, request, jsonify, render_template_string, send_from_directory
from flask_cors import CORS
import os
import sys
from datetime import datetime
import logging

# LLM API imports with error handling
try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False
    anthropic = None

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

try:
    from huggingface_hub import InferenceClient
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False
    InferenceClient = None

try:
    import feedparser
    FEEDPARSER_AVAILABLE = True
except ImportError:
    FEEDPARSER_AVAILABLE = False
    feedparser = None

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure CORS
CORS(app, origins=[
    'https://curam-ai.com.au',
    'https://curam-ai.com.au/python-hub/',
    'http://localhost:3000',
    'http://localhost:8000',
    '*'  # Remove in production
])

# Initialize LLM clients
claude_client = None
gemini_model = None
hf_client = None

def init_llm_clients():
    """Initialize LLM API clients with proper error handling"""
    global claude_client, gemini_model, hf_client
    
    # Initialize Claude
    if CLAUDE_AVAILABLE and os.getenv('CLAUDE_API_KEY'):
        try:
            claude_client = anthropic.Anthropic(api_key=os.getenv('CLAUDE_API_KEY'))
            logger.info("Claude client initialized successfully")
        except Exception as e:
            logger.error(f"Claude initialization failed: {str(e)}")
    
    # Initialize Gemini
    if GEMINI_AVAILABLE and os.getenv('GOOGLE_API_KEY'):
        try:
            genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
            gemini_model = genai.GenerativeModel('gemini-pro')
            logger.info("Gemini client initialized successfully")
        except Exception as e:
            logger.error(f"Gemini initialization failed: {str(e)}")
    
    # Initialize HuggingFace
    if HUGGINGFACE_AVAILABLE and os.getenv('HUGGINGFACE_API_KEY'):
        try:
            hf_client = InferenceClient(api_key=os.getenv('HUGGINGFACE_API_KEY'))
            logger.info("HuggingFace client initialized successfully")
        except Exception as e:
            logger.error(f"HuggingFace initialization failed: {str(e)}")

# Initialize clients on startup
init_llm_clients()

@app.route('/')
def index():
    return jsonify({
        'name': 'Brisbane Property Intelligence',
        'version': '1.0.0',
        'description': 'Multi-LLM Property Intelligence Tool for Brisbane Market Analysis',
        'endpoints': {
            'health': '/health',
            'demo': '/demo',
            'test_llm': '/api/test-*'
        },
        'status': 'running',
        'features': ['Multi-LLM Pipeline', 'Brisbane Property Data', 'RSS Feed Analysis'],
        'ai_services': {
            'claude': 'Available' if claude_client else 'Not initialized',
            'gemini': 'Available' if gemini_model else 'Not initialized',
            'huggingface': 'Available' if hf_client else 'Not initialized'
        }
    })

@app.route('/health')
def health():
    try:
        logger.info("Health check requested")
        
        response_data = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'python_version': sys.version.split()[0],
            'flask_running': True,
            'environment_variables': {
                'CLAUDE_API_KEY': 'Set' if os.getenv('CLAUDE_API_KEY') else 'Missing',
                'GOOGLE_API_KEY': 'Set' if os.getenv('GOOGLE_API_KEY') else 'Missing',
                'HUGGINGFACE_API_KEY': 'Set' if os.getenv('HUGGINGFACE_API_KEY') else 'Missing',
                'MAILCHANNELS_API_KEY': 'Set' if os.getenv('MAILCHANNELS_API_KEY') else 'Missing'
            },
            'library_availability': {
                'anthropic': CLAUDE_AVAILABLE,
                'google_generativeai': GEMINI_AVAILABLE,
                'huggingface_hub': HUGGINGFACE_AVAILABLE,
                'feedparser': FEEDPARSER_AVAILABLE
            },
            'client_status': {
                'claude': claude_client is not None,
                'gemini': gemini_model is not None,
                'huggingface': hf_client is not None
            }
        }
        
        logger.info(f"Health check successful")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# ===== LLM TESTING ENDPOINTS =====

@app.route('/demo')
def demo():
    """Serve the LLM testing demo page"""
    return render_template_string(DEMO_HTML)

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """Serve static assets (CSS, JS) from assets directory"""
    return send_from_directory('assets', filename)

@app.route('/api/test-claude', methods=['POST'])
def test_claude():
    """Test Claude API connection"""
    try:
        if not claude_client:
            return jsonify({
                'success': False,
                'error': 'Claude client not initialized',
                'details': 'Check API key and library installation'
            }), 500
        
        data = request.get_json()
        test_message = data.get('message', 'Hello, this is a connection test.')
        
        response = claude_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=100,
            messages=[
                {"role": "user", "content": test_message}
            ]
        )
        
        return jsonify({
            'success': True,
            'service': 'Claude',
            'response': response.content[0].text,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Claude test failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'service': 'Claude'
        }), 500

@app.route('/api/test-gemini', methods=['POST'])
def test_gemini():
    """Test Gemini API connection"""
    try:
        if not gemini_model:
            return jsonify({
                'success': False,
                'error': 'Gemini client not initialized',
                'details': 'Check API key and library installation'
            }), 500
        
        data = request.get_json()
        test_message = data.get('message', 'Hello, this is a connection test.')
        
        response = gemini_model.generate_content(test_message)
        
        return jsonify({
            'success': True,
            'service': 'Gemini',
            'response': response.text,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Gemini test failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'service': 'Gemini'
        }), 500

@app.route('/api/test-huggingface', methods=['POST'])
def test_huggingface():
    """Test HuggingFace API connection"""
    try:
        if not hf_client:
            return jsonify({
                'success': False,
                'error': 'HuggingFace client not initialized',
                'details': 'Check API key and library installation'
            }), 500
        
        data = request.get_json()
        test_message = data.get('message', 'This is a test message for summarization.')
        
        # Test with a simple text generation model
        response = hf_client.text_generation(
            prompt=f"Summarize this text: {test_message}",
            model="microsoft/DialoGPT-medium",
            max_new_tokens=50
        )
        
        return jsonify({
            'success': True,
            'service': 'HuggingFace',
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"HuggingFace test failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'service': 'HuggingFace'
        }), 500

@app.route('/api/test-feeds', methods=['GET'])
def test_feeds():
    """Test RSS feed parsing"""
    try:
        if not FEEDPARSER_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Feedparser not available',
                'details': 'Check library installation'
            }), 500
        
        # Test with a simple, reliable feed
        test_feed_url = "https://www.realestate.com.au/news/rss/"
        
        feed = feedparser.parse(test_feed_url)
        
        if feed.bozo:
            return jsonify({
                'success': False,
                'error': 'Feed parsing error',
                'details': str(feed.bozo_exception)
            }), 500
        
        # Get first few entries
        entries = []
        for entry in feed.entries[:3]:
            entries.append({
                'title': entry.get('title', 'No title'),
                'link': entry.get('link', 'No link'),
                'published': entry.get('published', 'No date')
            })
        
        return jsonify({
            'success': True,
            'service': 'RSS Feeds',
            'feed_title': feed.feed.get('title', 'Unknown'),
            'entries_count': len(feed.entries),
            'sample_entries': entries,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Feed test failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'service': 'RSS Feeds'
        }), 500

# Simple demo HTML for LLM testing
DEMO_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Brisbane Property Intelligence - LLM Testing</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 900px; 
            margin: 0 auto; 
            padding: 20px; 
            background: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 20px;
        }
        .status { 
            padding: 15px; 
            margin: 10px 0; 
            border-radius: 8px; 
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .success { background: #d4edda; color: #155724; border-left: 4px solid #28a745; }
        .error { background: #f8d7da; color: #721c24; border-left: 4px solid #dc3545; }
        .test-section {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin: 20px 0;
        }
        button { 
            padding: 12px 24px; 
            margin: 8px; 
            background: #007bff; 
            color: white; 
            border: none; 
            border-radius: 6px; 
            cursor: pointer;
            font-weight: bold;
        }
        button:hover { background: #0056b3; }
        button:disabled { background: #6c757d; cursor: not-allowed; }
        textarea { 
            width: 100%; 
            height: 200px; 
            margin: 15px 0; 
            padding: 15px; 
            border: 1px solid #ddd;
            border-radius: 6px;
            font-family: monospace;
            font-size: 14px;
        }
        input { 
            width: 100%; 
            padding: 12px; 
            margin: 10px 0; 
            border: 1px solid #ddd;
            border-radius: 6px;
            box-sizing: border-box;
        }
        .indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .ready { background: #28a745; }
        .not-ready { background: #dc3545; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏠 Brisbane Property Intelligence</h1>
        <p>Multi-LLM Connection Testing Dashboard</p>
    </div>
    
    <div id="status" class="status">Loading system status...</div>
    
    <div class="test-section">
        <h3>🤖 LLM API Testing</h3>
        <p>Test each LLM service individually with Brisbane-focused queries:</p>
        
        <input type="text" id="testMessage" placeholder="Enter test message" 
               value="Tell me one interesting fact about Brisbane property market.">
        
        <div>
            <button onclick="testLLM('claude')" id="claude-btn">Test Claude</button>
            <button onclick="testLLM('gemini')" id="gemini-btn">Test Gemini</button>
            <button onclick="testLLM('huggingface')" id="hf-btn">Test HuggingFace</button>
            <button onclick="testFeeds()" id="feeds-btn">Test RSS Feeds</button>
        </div>
        
        <textarea id="results" placeholder="Test results will appear here..." readonly></textarea>
    </div>

    <script>
        window.addEventListener('load', loadStatus);
        
        async function loadStatus() {
            try {
                const response = await fetch('/health');
                const data = await response.json();
                
                const statusHtml = `
                    <div class="success">
                        <h4>🟢 System Status: ${data.status}</h4>
                        <p><strong>Libraries:</strong></p>
                        <p>
                            <span class="indicator ${data.library_availability.anthropic ? 'ready' : 'not-ready'}"></span>Anthropic: ${data.library_availability.anthropic ? 'Available' : 'Missing'}<br>
                            <span class="indicator ${data.library_availability.google_generativeai ? 'ready' : 'not-ready'}"></span>Gemini: ${data.library_availability.google_generativeai ? 'Available' : 'Missing'}<br>
                            <span class="indicator ${data.library_availability.huggingface_hub ? 'ready' : 'not-ready'}"></span>HuggingFace: ${data.library_availability.huggingface_hub ? 'Available' : 'Missing'}<br>
                            <span class="indicator ${data.library_availability.feedparser ? 'ready' : 'not-ready'}"></span>Feedparser: ${data.library_availability.feedparser ? 'Available' : 'Missing'}
                        </p>
                        <p><strong>API Clients:</strong></p>
                        <p>
                            <span class="indicator ${data.client_status.claude ? 'ready' : 'not-ready'}"></span>Claude: ${data.client_status.claude ? 'Ready' : 'Not Ready'}<br>
                            <span class="indicator ${data.client_status.gemini ? 'ready' : 'not-ready'}"></span>Gemini: ${data.client_status.gemini ? 'Ready' : 'Not Ready'}<br>
                            <span class="indicator ${data.client_status.huggingface ? 'ready' : 'not-ready'}"></span>HuggingFace: ${data.client_status.huggingface ? 'Ready' : 'Not Ready'}
                        </p>
                    </div>
                `;
                
                document.getElementById('status').innerHTML = statusHtml;
                
                // Enable/disable buttons based on client status
                document.getElementById('claude-btn').disabled = !data.client_status.claude;
                document.getElementById('gemini-btn').disabled = !data.client_status.gemini;
                document.getElementById('hf-btn').disabled = !data.client_status.huggingface;
                document.getElementById('feeds-btn').disabled = !data.library_availability.feedparser;
                
            } catch (error) {
                document.getElementById('status').innerHTML = 
                    `<div class="error"><h4>❌ Error loading status</h4><p>${error.message}</p></div>`;
            }
        }
        
        async function testLLM(service) {
            const message = document.getElementById('testMessage').value;
            const results = document.getElementById('results');
            
            results.value = `Testing ${service.toUpperCase()}...\\n\\nSending: "${message}"\\n\\nWaiting for response...`;
            
            try {
                const response = await fetch(`/api/test-${service}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    results.value = `✅ ${data.service} Test SUCCESSFUL\\n\\n` +
                                  `Query: "${message}"\\n\\n` +
                                  `Response:\\n${data.response}\\n\\n` +
                                  `Timestamp: ${data.timestamp}`;
                } else {
                    results.value = `❌ ${data.service || service} Test FAILED\\n\\n` +
                                  `Error: ${data.error}\\n\\n` +
                                  `Details: ${data.details || 'None provided'}`;
                }
            } catch (error) {
                results.value = `❌ Network Error Testing ${service.toUpperCase()}\\n\\n` +
                              `Error: ${error.message}\\n\\n` +
                              `Check your network connection and try again.`;
            }
        }
        
        async function testFeeds() {
            const results = document.getElementById('results');
            
            results.value = 'Testing RSS Feeds...\\n\\nFetching Real Estate News RSS...\\n\\nPlease wait...';
            
            try {
                const response = await fetch('/api/test-feeds');
                const data = await response.json();
                
                if (data.success) {
                    results.value = `✅ RSS Feed Test SUCCESSFUL\\n\\n` +
                                  `Feed: ${data.feed_title}\\n` +
                                  `Total Entries: ${data.entries_count}\\n\\n` +
                                  `Latest Articles:\\n` +
                                  data.sample_entries.map((entry, i) => 
                                      `${i+1}. ${entry.title}\\n   Published: ${entry.published}\\n`
                                  ).join('\\n') +
                                  `\\nTimestamp: ${data.timestamp}`;
                } else {
                    results.value = `❌ RSS Feed Test FAILED\\n\\n` +
                                  `Error: ${data.error}\\n\\n` +
                                  `Details: ${data.details || 'None provided'}`;
                }
            } catch (error) {
                results.value = `❌ Network Error Testing RSS Feeds\\n\\n` +
                              `Error: ${error.message}\\n\\n` +
                              `Check your network connection and try again.`;
            }
        }
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV', 'production') == 'development'
    logger.info(f"Starting Brisbane Property Intelligence on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)