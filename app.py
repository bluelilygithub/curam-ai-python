from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server
import io
import base64
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import os
import sys
from werkzeug.utils import secure_filename
import sqlite3
import json
from datetime import datetime
import logging
import requests
import time
import random
import re

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configure CORS for your shared hosting domain
CORS(app, origins=[
    'https://curam-ai.com.au',
    'https://curam-ai.com.au/python-hub/',
    'https://curam-ai.com.au/ai-intelligence/',
    'http://localhost:3000',
    'http://localhost:8000',
    '*'  # Allow all for testing - remove in production
])

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize scraper with error handling
scraper = None
try:
    from scraper import WebScraper
    scraper = WebScraper()
    logger.info("Scraper initialized successfully")
except Exception as e:
    logger.error(f"Scraper initialization failed: {str(e)}")
    scraper = None

@app.route('/')
def index():
    return jsonify({
        'name': 'Curam AI - Intelligence & Analytics API',
        'version': '2.1.0',
        'description': 'Flask API with pandas, matplotlib, web scraping, PDF generation, and AI intelligence',
        'endpoints': {
            'health': '/health',
            'upload_csv': 'POST /api/upload-csv',
            'generate_report': 'POST /api/generate-report',
            'intelligence_pipeline': 'POST /api/full-intelligence-pipeline',
            'visual_report': 'POST /api/generate-visual-report',
            'scraper_apis': '/api/scraper/*',
            'analytics': '/api/analytics/*'
        },
        'status': 'running',
        'features': ['CSV Analysis', 'Web Scraping', 'AI Intelligence', 'Visual Reports'],
        'ai_services': {
            'claude': 'Available (simulated)',
            'gemini': 'Available (simulated)', 
            'stability_ai': 'Available (simulated)'
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
            'services': {
                'flask': True,
                'pandas': True,
                'matplotlib': True,
                'scraper': scraper is not None,
                'ai_intelligence': True
            }
        }
        
        # Test core libraries
        try:
            response_data['flask_version'] = Flask.__version__
            response_data['pandas_version'] = pd.__version__
            response_data['matplotlib_version'] = matplotlib.__version__
        except Exception as e:
            response_data['library_error'] = str(e)
        
        logger.info(f"Health check successful: {response_data}")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# ===== AI INTELLIGENCE PLATFORM ENDPOINTS =====

@app.route('/api/full-intelligence-pipeline', methods=['POST'])
def full_intelligence_pipeline():
    """Complete AI analysis pipeline with enhanced responses"""
    try:
        data = request.get_json()
        query = data.get('query', 'Unknown query')
        industry = data.get('industry', 'general')
        
        logger.info(f"Intelligence analysis request: {query} ({industry})")
        
        # Simulate realistic processing time
        time.sleep(random.uniform(1.5, 3.0))
        
        # Generate enhanced AI responses
        claude_analysis = generate_enhanced_claude_analysis(query, industry)
        gemini_insights = generate_enhanced_gemini_insights(query, industry)
        
        # Simulate data source analysis
        sources_analyzed = simulate_data_sources(query, industry)
        
        response = {
            'success': True,
            'query': query,
            'industry': industry,
            'sources_analyzed': sources_analyzed['count'],
            'source_details': sources_analyzed['sources'],
            'claude_analysis': claude_analysis,
            'gemini_insights': gemini_insights,
            'timestamp': datetime.now().isoformat(),
            'processing_time': round(random.uniform(1.5, 3.0), 2)
        }
        
        logger.info(f"Intelligence analysis completed for: {query}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Intelligence pipeline error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate-visual-report', methods=['POST'])
def generate_visual_report():
    """Generate visual charts for analysis"""
    try:
        data = request.get_json()
        description = data.get('description', 'Analysis Chart')
        
        logger.info(f"Visual report request: {description}")
        
        # For demo purposes, we'll return success without actual image generation
        # In production, this would call Stability AI API
        response = {
            'success': True,
            'description': description,
            'image_data': None,  # Frontend will use placeholder chart
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Visual generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ===== ENHANCED AI ANALYSIS FUNCTIONS =====

def generate_enhanced_claude_analysis(query, industry):
    """Generate high-quality Claude-style analysis with deeper insights"""
    query_lower = query.lower()
    
    # Enhanced templates with comprehensive analysis
    if 'gpu' in query_lower or 'graphic' in query_lower or 'processing' in query_lower:
        return """The graphics processing unit market is experiencing transformational growth driven by AI workloads, with datacenter GPU revenue now exceeding gaming segments for major manufacturers. NVIDIA maintains dominant market position with approximately 88% share in AI training chips, though AMD's MI300 series and Intel's emerging Gaudi processors represent growing competitive pressure.

Market Dynamics: The shift from gaming-centric to AI-optimized architectures has fundamentally altered GPU design priorities. Memory bandwidth, parallel processing efficiency, and power optimization now drive innovation cycles. Enterprise customers increasingly demand specialized AI accelerators rather than repurposed gaming hardware.

Supply Chain Evolution: Geopolitical tensions have accelerated domestic chip manufacturing initiatives, with US CHIPS Act funding and European semiconductor sovereignty programs reshaping global production. Taiwan's TSMC remains critical for advanced node manufacturing, creating strategic vulnerabilities.

Future Outlook: Edge AI deployment requirements are driving development of low-power, high-efficiency processing solutions. Neuromorphic chips and quantum processing represent emerging paradigms that could disrupt traditional GPU architectures within 5-7 years.

Strategic Implications: Companies should diversify supplier relationships, invest in software optimization for multi-vendor hardware, and prepare for architectural transitions as Moore's Law scaling becomes economically challenging."""

    elif 'ai' in query_lower and 'industry' in query_lower:
        return """The artificial intelligence industry has reached an inflection point where enterprise adoption accelerates beyond experimental phases into production deployment at scale. Large language models, computer vision, and autonomous systems represent the three primary growth vectors, each with distinct market dynamics and competitive landscapes.

Enterprise Transformation: AI implementation has moved from isolated use cases to comprehensive workflow integration. Companies report 15-30% productivity gains in knowledge work, with particular strength in content generation, code development, and customer service automation. However, integration complexity and skill gaps remain significant barriers.

Infrastructure Evolution: The computational demands of modern AI models have created a new infrastructure category focused on training and inference optimization. Cloud providers are developing AI-specific hardware and services, while edge computing growth enables real-time AI applications in manufacturing, healthcare, and autonomous vehicles.

Regulatory Landscape: Government initiatives worldwide are establishing AI governance frameworks, with EU AI Act leading comprehensive regulation. These frameworks will significantly impact development timelines, deployment strategies, and competitive positioning across different market segments.

Investment Patterns: Venture capital flows increasingly favor AI applications with clear ROI metrics rather than purely technical innovations. Enterprise AI software represents the fastest-growing segment, while hardware infrastructure investments focus on specialized chips and edge computing solutions.

Competitive Dynamics: Big Tech companies leverage platform advantages and compute resources, while specialized AI companies compete on domain expertise and customer intimacy. Open-source models are democratizing access but creating new challenges around model governance and intellectual property."""

    # Industry-specific comprehensive analysis
    templates = {
        'technology': f"""The technology sector demonstrates unprecedented convergence across multiple innovation vectors, with artificial intelligence, quantum computing, and biotechnology creating synergistic opportunities. Cloud infrastructure has evolved beyond simple compute provisioning to comprehensive AI-as-a-Service platforms, fundamentally altering competitive dynamics.

Digital Transformation Acceleration: Enterprise software adoption has permanently shifted toward cloud-native, API-first architectures. Companies investing in modern infrastructure report 25-40% faster time-to-market for new products. Legacy system migration represents a $500B+ opportunity through 2027.

Emerging Technology Integration: The intersection of AI, 5G, and edge computing enables previously impossible applications in autonomous vehicles, smart manufacturing, and personalized healthcare. First-mover advantages in these convergence areas are creating substantial market valuations.

Talent and Skills Evolution: The shift toward AI-augmented development is reshaping software engineering roles. Companies successfully adapting to AI-assisted workflows report 35% productivity improvements, while those lagging face increasing competitive disadvantage.

Regulatory and Ethical Considerations: Technology companies face growing scrutiny around data privacy, algorithmic bias, and market concentration. Proactive compliance and ethical AI frameworks are becoming competitive differentiators rather than regulatory burdens.

Investment Strategy: Focus on companies with strong data moats, AI-native architectures, and proven ability to monetize emerging technologies. Avoid legacy technology companies without clear transformation roadmaps.""",

        'automotive': f"""The automotive industry is undergoing its most significant transformation since the invention of the automobile, with electrification, autonomous driving, and mobility services converging to reshape the entire value chain. Traditional automotive manufacturers face existential challenges as software capabilities become primary differentiators.

Electrification Timeline: Battery cost reductions have reached tipping points where EVs achieve total cost of ownership parity with ICE vehicles in most markets. Range anxiety continues diminishing as charging infrastructure expands and battery energy density improves 8-12% annually.

Autonomous Vehicle Progress: While full autonomy remains elusive, Level 3-4 systems in controlled environments are achieving commercial viability. Waymo's robotaxi service expansion and Tesla's FSD improvements demonstrate different approaches to autonomous capabilities, with distinct risk-reward profiles.

Supply Chain Transformation: The shift from mechanical to electronic components is realigning supplier relationships. Semiconductor shortage experiences have accelerated vertical integration strategies and geographic diversification of critical component sourcing.

Mobility as a Service: Urban transportation patterns favor access over ownership, particularly among younger demographics. Ride-sharing, car-sharing, and micromobility solutions are creating new business models and challenging traditional automotive revenue streams.

Strategic Positioning: Success requires simultaneous execution across electrification, software development, and customer experience innovation. Companies unable to master all three dimensions face marginalization in the evolving mobility ecosystem.""",

        'healthcare': f"""Healthcare innovation is accelerating through convergence of digital health, personalized medicine, and AI-driven diagnostics, fundamentally transforming patient care delivery and medical research methodologies. The COVID-19 pandemic permanently altered healthcare delivery models and accelerated technology adoption timelines.

Digital Health Integration: Telemedicine adoption reached 85% of healthcare providers during the pandemic and has stabilized at 60%+ penetration. Remote patient monitoring and virtual care delivery models demonstrate superior outcomes for chronic disease management while reducing costs 20-35%.

Personalized Medicine Advancement: Genomic sequencing costs have declined 99.9% since 2003, enabling routine integration into clinical workflows. Precision medicine approaches show particular promise in oncology, with targeted therapies achieving significantly better outcomes than traditional chemotherapy approaches.

AI-Powered Diagnostics: Machine learning models now exceed human radiologist performance in specific imaging tasks. Early detection algorithms for diabetic retinopathy, skin cancer, and cardiac abnormalities are gaining FDA approval and clinical adoption.

Regulatory Innovation: FDA breakthrough device pathways and software as medical device guidelines are accelerating approval timelines for digital health innovations. European MDR implementation creates additional compliance requirements but also establishes global quality standards.

Market Opportunities: Focus on solutions addressing physician burnout, chronic disease management, and health equity challenges. Successful companies demonstrate clear clinical outcomes, regulatory compliance, and sustainable reimbursement models."""

    }
    
    # Get industry-specific analysis or default
    if industry in templates:
        return templates[industry]
    else:
        # Generate contextual analysis for other industries
        return f"""The {industry} sector is experiencing significant transformation driven by digital innovation, changing consumer expectations, and evolving regulatory landscapes. Companies that successfully navigate these transitions are positioning themselves for sustained competitive advantage.

Technology Integration: Digital transformation initiatives across {industry} organizations are showing measurable ROI, with leaders reporting 20-30% efficiency improvements through automation and data analytics implementation. Cloud adoption and AI integration are becoming strategic imperatives rather than optional upgrades.

Market Dynamics: Consumer behavior shifts and regulatory changes are reshaping traditional business models. Organizations with agile operating models and customer-centric approaches are capturing disproportionate market share while legacy players struggle to adapt.

Competitive Landscape: New entrants leveraging technology advantages are disrupting established market hierarchies. Successful companies are building platform-based business models that create network effects and sustainable competitive moats.

Future Outlook: The next 3-5 years will determine market leadership positions as current transformation investments mature. Companies investing proactively in technology capabilities, talent development, and customer experience innovation are best positioned for long-term success.

Strategic Recommendations: Prioritize data-driven decision making, invest in digital capabilities, and maintain customer-centric focus while building operational resilience for future market volatility."""

def generate_enhanced_gemini_insights(query, industry):
    """Generate Gemini-style data insights with enhanced metrics"""
    # Generate realistic metrics based on industry and query
    base_growth = {'technology': 35, 'automotive': 25, 'healthcare': 20, 'finance': 30, 'manufacturing': 18, 'retail': 15, 'energy': 28, 'aerospace': 22}
    growth_rate = base_growth.get(industry, 25) + random.randint(-8, 12)
    
    market_size = random.randint(8, 85)
    players = random.randint(3, 9)
    market_share = random.randint(52, 78)
    
    # Add query-specific metrics
    query_lower = query.lower()
    if 'gpu' in query_lower or 'graphic' in query_lower:
        market_size = random.randint(45, 120)
        growth_rate = random.randint(28, 45)
    elif 'ai' in query_lower:
        growth_rate = random.randint(35, 55)
        market_size = random.randint(25, 95)
    elif 'electric' in query_lower or 'tesla' in query_lower:
        growth_rate = random.randint(22, 38)
        market_size = random.randint(15, 60)
    
    investment_change = growth_rate - random.randint(5, 12)
    adoption_rate = growth_rate // 2 + random.randint(-3, 8)
    cost_reduction = random.randint(8, 22)
    efficiency_gain = random.randint(15, 35)
    roi_improvement = random.randint(12, 28)
    
    templates = {
        'technology': f"Technology sector analysis reveals {growth_rate}% YoY growth with sustained momentum. Key performance indicators show R&D investment increased {investment_change}%, enterprise adoption rates up {adoption_rate}%, implementation costs decreased {cost_reduction}%. Operational efficiency improved {efficiency_gain}% while ROI increased {roi_improvement}%. Market concentration shows {players} major platforms controlling {market_share}% of total addressable market valued at ${market_size}B. Cloud infrastructure spending represents largest growth segment with 40% of total enterprise IT budgets.",
        
        'automotive': f"Automotive industry data indicates {growth_rate}% expansion in electrification segment with accelerating transformation metrics. Production capacity utilization up {investment_change}%, battery costs down {cost_reduction}%, charging infrastructure deployment up {adoption_rate}%. Manufacturing efficiency gained {efficiency_gain}% through automation while supply chain optimization delivered {roi_improvement}% cost savings. Market leadership distributed among {players} major manufacturers holding {market_share}% combined market share. Global EV market size approaching ${market_size}B with projected compound annual growth rate of 28%.",
        
        'healthcare': f"Healthcare technology sector demonstrates {growth_rate}% annual growth driven by comprehensive digital transformation initiatives. Telehealth adoption increased {adoption_rate}%, regulatory approval timelines reduced {cost_reduction}%, clinical trial efficiency up {investment_change}%. Patient outcome improvements of {efficiency_gain}% while healthcare delivery costs decreased {roi_improvement}%. Market dynamics show {players} leading platforms capturing {market_share}% of digital health investments totaling ${market_size}B annually. Precision medicine segment represents fastest-growing subsector.",
        
        'finance': f"Financial technology sector exhibits {growth_rate}% growth with strong underlying fundamentals and regulatory support. Digital payment volumes increased {adoption_rate}%, customer acquisition costs reduced {cost_reduction}%, regulatory compliance efficiency up {investment_change}%. Transaction processing speed improved {efficiency_gain}% while operational costs decreased {roi_improvement}%. Competitive landscape features {players} dominant platforms controlling {market_share}% of fintech market valued at ${market_size}B. Open banking initiatives driving innovation acceleration.",
        
        'manufacturing': f"Manufacturing sector shows {growth_rate}% efficiency improvements through comprehensive automation adoption and Industry 4.0 implementation. Production optimization increased {investment_change}%, waste reduction achieved {cost_reduction}%, quality metrics improved {adoption_rate}%. Overall equipment effectiveness up {efficiency_gain}% while total cost of ownership reduced {roi_improvement}%. Industry consolidation features {players} major players representing {market_share}% of advanced manufacturing market worth ${market_size}B. Smart factory investments leading transformation.",
        
        'retail': f"Retail industry demonstrates {growth_rate}% omnichannel growth with seamless digital integration across customer touchpoints. E-commerce conversion rates up {adoption_rate}%, customer acquisition costs down {cost_reduction}%, inventory efficiency improved {investment_change}%. Customer satisfaction increased {efficiency_gain}% while operational costs optimized {roi_improvement}%. Market share concentration shows {players} leading retailers controlling {market_share}% of online retail valued at ${market_size}B. Personalization technology driving competitive advantage.",
        
        'energy': f"Energy sector indicates {growth_rate}% renewable capacity growth annually with accelerating clean energy transition. Grid efficiency improvements up {investment_change}%, energy storage costs reduced {cost_reduction}%, renewable penetration increased {adoption_rate}%. System reliability improved {efficiency_gain}% while operational expenses decreased {roi_improvement}%. Market structure includes {players} major utilities controlling {market_share}% of clean energy investments totaling ${market_size}B. Smart grid technologies enabling transformation.",
        
        'aerospace': f"Aerospace industry shows {growth_rate}% recovery with strong innovation focus and sustainable technology integration. Manufacturing efficiency up {investment_change}%, development costs optimized {cost_reduction}%, sustainable technology adoption increased {adoption_rate}%. Production throughput improved {efficiency_gain}% while time-to-market reduced {roi_improvement}%. Market concentration features {players} prime contractors holding {market_share}% of commercial aerospace market valued at ${market_size}B. Next-generation propulsion systems driving innovation."
    }
    
    return templates.get(industry, f"Cross-industry analysis demonstrates {growth_rate}% growth potential with strong market fundamentals and technological innovation drivers. Performance metrics indicate {adoption_rate}% adoption acceleration, {cost_reduction}% cost optimization, and {investment_change}% investment increase. Operational efficiency improved {efficiency_gain}% while return on investment enhanced {roi_improvement}%. Competitive dynamics show {players} key market participants controlling {market_share}% of total addressable market valued at ${market_size}B. Digital transformation initiatives driving sustainable competitive advantages.")

def simulate_data_sources(query, industry):
    """Simulate data source collection for analysis"""
    industry_sources = {
        'technology': ['TechCrunch.com', 'VentureBeat.com', 'Ars Technica', 'The Verge', 'Wired.com', 'IEEE Spectrum', 'MIT Technology Review'],
        'automotive': ['Automotive News', 'Motor Trend', 'Car and Driver', 'InsideEVs.com', 'Electrek.co', 'Reuters Autos', 'Automotive Dive'],
        'healthcare': ['Modern Healthcare', 'Healthcare Dive', 'STAT News', 'MedTech Dive', 'BioPharma Dive', 'Health Affairs', 'NEJM.org'],
        'finance': ['Financial Times', 'Bloomberg Markets', 'Reuters Finance', 'WSJ Markets', 'American Banker', 'Fintech News', 'CoinDesk.com'],
        'manufacturing': ['Manufacturing.net', 'Industry Week', 'Plant Engineering', 'Automation World', 'Manufacturing Dive', 'Smart Industry', 'Assembly Magazine'],
        'retail': ['Retail Dive', 'Chain Store Age', 'Progressive Grocer', 'Retail Leader', 'NRF.com', 'RetailWire.com', 'Modern Retail'],
        'energy': ['Energy News', 'Renewable Energy World', 'Oil & Gas Journal', 'Utility Dive', 'Greentech Media', 'Energy Storage News', 'CleanTechnica'],
        'aerospace': ['Aviation Week', 'FlightGlobal', 'Aerospace Daily', 'Space News', 'Defense News', 'Avionics International', 'Aerospace Testing']
    }
    
    sources = industry_sources.get(industry, industry_sources['technology'])
    count = random.randint(5, min(len(sources), 8))
    selected_sources = random.sample(sources, count)
    
    return {
        'count': count,
        'sources': selected_sources
    }

# ===== ORIGINAL ENDPOINTS (UNCHANGED) =====

# CSV Upload and Analysis API
@app.route('/api/upload-csv', methods=['POST'])
def upload_csv():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'success': False, 'error': 'File must be CSV format'}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Analyze CSV
        df = pd.read_csv(filepath)
        
        analysis = {
            'filename': filename,
            'total_rows': len(df),
            'columns': list(df.columns),
            'data_types': df.dtypes.astype(str).to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'numeric_summary': df.describe().to_dict() if len(df.select_dtypes(include=['number']).columns) > 0 else {},
            'sample_data': df.head(5).to_dict('records')
        }
        
        # Clean up file
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"CSV upload error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Generate Report API
@app.route('/api/generate-report', methods=['POST'])
def generate_report_api():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if not file.filename.endswith('.csv'):
            return jsonify({'success': False, 'error': 'File must be CSV format'}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Generate report
        report_path = generate_report(filepath)
        
        # Clean up CSV file
        os.remove(filepath)
        
        return send_file(
            report_path,
            as_attachment=True,
            download_name=f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Report generation error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Scraper APIs - Only available if scraper is working
@app.route('/api/scraper/sites', methods=['GET'])
def get_monitored_sites():
    try:
        if not scraper:
            return jsonify({'success': False, 'error': 'Scraper not available'}), 500
        
        # Get sites directly from database
        conn = sqlite3.connect('scraper.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, url, price_selector FROM monitored_sites')
        sites = [{'id': row[0], 'name': row[1], 'url': row[2], 'price_selector': row[3]} for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'success': True,
            'sites': sites
        })
    except Exception as e:
        logger.error(f"Get sites error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/scraper/add-site', methods=['POST'])
def add_site_api():
    try:
        if not scraper:
            return jsonify({'success': False, 'error': 'Scraper not available'}), 500
        
        data = request.get_json()
        name = data.get('name')
        url = data.get('url')
        price_selector = data.get('price_selector')
        
        if not all([name, url, price_selector]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        site_id = scraper.add_site(name, url, price_selector)
        
        return jsonify({
            'success': True,
            'message': f'Added {name} to monitoring list',
            'site_id': site_id
        })
    except Exception as e:
        logger.error(f"Add site error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/scraper/scrape-now', methods=['POST'])
def scrape_now_api():
    try:
        if not scraper:
            return jsonify({'success': False, 'error': 'Scraper not available'}), 500
        
        results = scraper.scrape_all_sites()
        return jsonify({
            'success': True,
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Scrape now error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/scraper/price-history/<int:site_id>', methods=['GET'])
def price_history_api(site_id):
    try:
        if not scraper:
            return jsonify({'success': False, 'error': 'Scraper not available'}), 500
        
        history = scraper.get_price_history(site_id)
        return jsonify({
            'success': True,
            'site_id': site_id,
            'history': history
        })
    except Exception as e:
        logger.error(f"Price history error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ANALYTICS ENDPOINTS

@app.route('/api/analytics/summary', methods=['GET'])
def analytics_summary():
    """Get summary statistics"""
    try:
        if not scraper:
            return jsonify({'success': False, 'error': 'Scraper not available'}), 500
        
        conn = sqlite3.connect('scraper.db')
        cursor = conn.cursor()
        
        # Summary stats
        cursor.execute('SELECT COUNT(*) FROM monitored_sites')
        total_sites = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM price_history')
        total_data_points = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(price) FROM price_history WHERE price > 0')
        avg_price = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT MIN(price), MAX(price) FROM price_history WHERE price > 0')
        price_range = cursor.fetchone()
        min_price, max_price = price_range if price_range[0] else (0, 0)
        
        conn.close()
        
        return jsonify({
            'success': True,
            'summary': {
                'total_sites': total_sites,
                'total_data_points': total_data_points,
                'average_price': round(avg_price, 2),
                'price_range': {
                    'min': min_price,
                    'max': max_price
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Analytics summary error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analytics/price-comparison', methods=['GET'])
def price_comparison():
    """Get price comparison data for bar charts"""
    try:
        if not scraper:
            return jsonify({'success': False, 'error': 'Scraper not available'}), 500
        
        conn = sqlite3.connect('scraper.db')
        cursor = conn.cursor()
        
        # Average prices by site
        cursor.execute('''
            SELECT ms.name, AVG(ph.price) as avg_price, COUNT(ph.price) as data_points
            FROM monitored_sites ms
            LEFT JOIN price_history ph ON ms.id = ph.site_id
            GROUP BY ms.id, ms.name
            HAVING COUNT(ph.price) > 0
            ORDER BY avg_price DESC
        ''')
        avg_prices = cursor.fetchall()
        conn.close()
        
        raw_data = [{'name': row[0], 'avg_price': row[1], 'data_points': row[2]} for row in avg_prices]
        
        return jsonify({
            'success': True,
            'raw_data': raw_data
        })
        
    except Exception as e:
        logger.error(f"Price comparison error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analytics/price-trends', methods=['GET'])
def price_trends():
    """Get price trends over time"""
    try:
        if not scraper:
            return jsonify({'success': False, 'error': 'Scraper not available'}), 500
        
        conn = sqlite3.connect('scraper.db')
        cursor = conn.cursor()
        
        # Price trends over time
        cursor.execute('''
            SELECT ms.name, ph.price, ph.scraped_at
            FROM monitored_sites ms
            JOIN price_history ph ON ms.id = ph.site_id
            ORDER BY ph.scraped_at DESC
            LIMIT 50
        ''')
        price_trends = cursor.fetchall()
        conn.close()
        
        raw_data = [{'name': row[0], 'price': row[1], 'date': row[2]} for row in price_trends]
        
        return jsonify({
            'success': True,
            'raw_data': raw_data
        })
        
    except Exception as e:
        logger.error(f"Price trends error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/simulate-data', methods=['POST'])
def simulate_data():
    """Generate demo data for testing"""
    try:
        if not scraper:
            return jsonify({'success': False, 'error': 'Scraper not available'}), 500
        
        data = request.get_json() or {}
        days = data.get('days', 7)
        
        scraper.simulate_historical_data(days)
        
        return jsonify({
            'success': True,
            'message': f'Generated {days} days of demo data',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Simulate data error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Chart Generation API
@app.route('/api/generate-chart', methods=['POST'])
def generate_chart():
    try:
        data = request.get_json()
        chart_data = data.get('data', [])
        chart_type = data.get('type', 'line')
        title = data.get('title', 'Chart')
        
        if not chart_data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Convert to DataFrame
        df = pd.DataFrame(chart_data)
        
        # Create chart
        plt.figure(figsize=(10, 6))
        
        if chart_type == 'histogram' and len(df.columns) > 0:
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                df[numeric_cols[0]].hist()
                plt.title(f'Distribution of {numeric_cols[0]}')
        elif chart_type == 'line' and len(df.columns) >= 2:
            plt.plot(df.iloc[:, 0], df.iloc[:, 1])
            plt.title(title)
        else:
            plt.text(0.5, 0.5, 'No suitable data for chart', ha='center', va='center')
            plt.title('No Data')
        
        # Save to base64
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
        img_buffer.seek(0)
        
        img_base64 = base64.b64encode(img_buffer.read()).decode()
        plt.close()
        
        return jsonify({
            'success': True,
            'chart': f'data:image/png;base64,{img_base64}',
            'type': chart_type,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Chart generation error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def generate_report(csv_file):
    """Generate PDF report from CSV file"""
    try:
        # Read CSV
        df = pd.read_csv(csv_file)
        
        # Basic analysis
        total_rows = len(df)
        columns = list(df.columns)
        
        # Create a simple chart
        plt.figure(figsize=(10, 6))
        if len(df.columns) > 1:
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                df[numeric_cols[0]].hist()
                plt.title(f'Distribution of {numeric_cols[0]}')
                plt.xlabel(numeric_cols[0])
                plt.ylabel('Frequency')
        
        # Save chart to bytes
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        # Create PDF report
        report_filename = f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        doc = SimpleDocTemplate(report_filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title = Paragraph("Data Analysis Report", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Summary
        summary = Paragraph(f"<b>Data Summary:</b><br/>Total Rows: {total_rows}<br/>Columns: {', '.join(columns)}", styles['Normal'])
        story.append(summary)
        story.append(Spacer(1, 12))
        
        # Add chart
        if len(df.select_dtypes(include=['number']).columns) > 0:
            img = Image(img_buffer, width=400, height=240)
            story.append(img)
        
        doc.build(story)
        return report_filename
        
    except Exception as e:
        logger.error(f"PDF generation error: {str(e)}")
        raise e

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV', 'production') == 'development'
    logger.info(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)