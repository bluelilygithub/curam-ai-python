from flask import Flask, request, jsonify, render_template_string
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
    """Serve the demo HTML page"""
    return render_template_string(INDEX_HTML)

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        response_data = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'python_version': sys.version.split()[0],
            'flask_version': Flask.__version__,
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
        
        # Test with a simple summarization model
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

# HTML template for the demo page
INDEX_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Brisbane Property Intelligence - Connection Testing</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .status-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }
        .status-ok { background-color: #28a745; }
        .status-error { background-color: #dc3545; }
        .status-warning { background-color: #ffc107; }
        .test-section {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .test-button {
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin-right: 10px;
            margin-bottom: 10px;
        }
        .test-button:hover {
            background: #0056b3;
        }
        .test-button:disabled {
            background: #6c757d;
            cursor: not-allowed;
        }
        .response-area {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 15px;
            margin-top: 15px;
            white-space: pre-wrap;
            max-height: 300px;
            overflow-y: auto;
        }
        .loading {
            color: #007bff;
            font-style: italic;
        }
        .success { color: #28a745; }
        .error { color: #dc3545; }
        .input-field {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏠 Brisbane Property Intelligence</h1>
        <p>Multi-LLM Connection Testing Dashboard</p>
    </div>

    <div class="status-grid">
        <div class="status-card">
            <h3>System Status</h3>
            <div id="system-status">
                <div class="loading">Loading system status...</div>
            </div>
        </div>
        
        <div class="status-card">
            <h3>API Keys</h3>
            <div id="api-status">
                <div class="loading">Checking API keys...</div>
            </div>
        </div>
        
        <div class="status-card">
            <h3>Libraries</h3>
            <div id="library-status">
                <div class="loading">Checking libraries...</div>
            </div>
        </div>
        
        <div class="status-card">
            <h3>LLM Clients</h3>
            <div id="client-status">
                <div class="loading">Checking LLM clients...</div>
            </div>
        </div>
    </div>

    <div class="test-section">
        <h3>🤖 LLM API Testing</h3>
        <p>Test each LLM service individually:</p>
        
        <input type="text" id="test-message" class="input-field" 
               placeholder="Enter test message (or use default)" 
               value="Tell me one interesting fact about Brisbane.">
        
        <div>
            <button class="test-button" onclick="testLLM('claude')">Test Claude</button>
            <button class="test-button" onclick="testLLM('gemini')">Test Gemini</button>
            <button class="test-button" onclick="testLLM('huggingface')">Test HuggingFace</button>
            <button class="test-button" onclick="testFeeds()">Test RSS Feeds</button>
        </div>
        
        <div id="test-response" class="response-area" style="display: none;"></div>
    </div>

    <script>
        // Load system status on page load
        window.addEventListener('load', function() {
            loadSystemStatus();
        });

        async function loadSystemStatus() {
            try {
                const response = await fetch('/health');
                const data = await response.json();
                
                // Update system status
                document.getElementById('system-status').innerHTML = `
                    <div><span class="status-indicator status-ok"></span>Status: ${data.status}</div>
                    <div>Python: ${data.python_version}</div>
                    <div>Flask: ${data.flask_version}</div>
                `;
                
                // Update API status
                const apiStatus = data.environment_variables;
                document.getElementById('api-status').innerHTML = Object.entries(apiStatus)
                    .map(([key, value]) => `
                        <div>
                            <span class="status-indicator ${value === 'Set' ? 'status-ok' : 'status-error'}"></span>
                            ${key}: ${value}
                        </div>
                    `).join('');
                
                // Update library status
                const libStatus = data.library_availability;
                document.getElementById('library-status').innerHTML = Object.entries(libStatus)
                    .map(([key, value]) => `
                        <div>
                            <span class="status-indicator ${value ? 'status-ok' : 'status-error'}"></span>
                            ${key}: ${value ? 'Available' : 'Missing'}
                        </div>
                    `).join('');
                
                // Update client status
                const clientStatus = data.client_status;
                document.getElementById('client-status').innerHTML = Object.entries(clientStatus)
                    .map(([key, value]) => `
                        <div>
                            <span class="status-indicator ${value ? 'status-ok' : 'status-error'}"></span>
                            ${key}: ${value ? 'Ready' : 'Not Initialized'}
                        </div>
                    `).join('');
                    
            } catch (error) {
                document.getElementById('system-status').innerHTML = 
                    `<div class="error">Error loading status: ${error.message}</div>`;
            }
        }

        async function testLLM(service) {
            const responseArea = document.getElementById('test-response');
            const message = document.getElementById('test-message').value;
            
            responseArea.style.display = 'block';
            responseArea.innerHTML = `<div class="loading">Testing ${service}...</div>`;
            
            try {
                const response = await fetch(`/api/test-${service}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    responseArea.innerHTML = `
                        <div class="success">✅ ${data.service} Test Successful</div>
                        <div><strong>Response:</strong></div>
                        <div>${data.response}</div>
                        <div><small>Timestamp: ${data.timestamp}</small></div>
                    `;
                } else {
                    responseArea.innerHTML = `
                        <div class="error">❌ ${data.service || service} Test Failed</div>
                        <div><strong>Error:</strong> ${data.error}</div>
                        ${data.details ? `<div><strong>Details:</strong> ${data.details}</div>` : ''}
                    `;
                }
            } catch (error) {
                responseArea.innerHTML = `
                    <div class="error">❌ Network Error</div>
                    <div><strong>Error:</strong> ${error.message}</div>
                `;
            }
        }

        async function testFeeds() {
            const responseArea = document.getElementById('test-response');
            
            responseArea.style.display = 'block';
            responseArea.innerHTML = `<div class="loading">Testing RSS feeds...</div>`;
            
            try {
                const response = await fetch('/api/test-feeds');
                const data = await response.json();
                
                if (data.success) {
                    responseArea.innerHTML = `
                        <div class="success">✅ RSS Feed Test Successful</div>
                        <div><strong>Feed:</strong> ${data.feed_title}</div>
                        <div><strong>Entries found:</strong> ${data.entries_count}</div>
                        <div><strong>Sample entries:</strong></div>
                        ${data.sample_entries.map(entry => `
                            <div style="margin: 10px 0; padding: 10px; background: #f0f0f0; border-radius: 5px;">
                                <div><strong>${entry.title}</strong></div>
                                <div><small>${entry.published}</small></div>
                            </div>
                        `).join('')}
                        <div><small>Timestamp: ${data.timestamp}</small></div>
                    `;
                } else {
                    responseArea.innerHTML = `
                        <div class="error">❌ RSS Feed Test Failed</div>
                        <div><strong>Error:</strong> ${data.error}</div>
                        ${data.details ? `<div><strong>Details:</strong> ${data.details}</div>` : ''}
                    `;
                }
            } catch (error) {
                responseArea.innerHTML = `
                    <div class="error">❌ Network Error</div>
                    <div><strong>Error:</strong> ${error.message}</div>
                `;
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