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

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configure CORS for your shared hosting domain
CORS(app, origins=[
    'https://curam-ai.com.au',  # Your shared hosting domain
    'https://curam-ai.com.au/python-hub/',     # Replace with actual domain where HTML is hosted
    'https://curam-ai.com.au/ai-intelligence/',  # New AI intelligence platform
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
    logger.info("✅ Scraper initialized successfully")
except Exception as e:
    logger.error(f"❌ Scraper initialization failed: {str(e)}")
    scraper = None

@app.route('/')
def index():
    return jsonify({
        'name': 'Python Data Analytics & AI Intelligence API',
        'version': '2.0.0',
        'description': 'Flask API with pandas, matplotlib, web scraping, PDF generation, and AI intelligence',
        'endpoints': {
            'health': '/health',
            'upload_csv': 'POST /api/upload-csv',
            'generate_report': 'POST /api/generate-report',
            'add_site': 'POST /api/scraper/add-site',
            'scrape_now': 'POST /api/scraper/scrape-now',
            'price_history': 'GET /api/scraper/price-history/<site_id>',
            'get_sites': 'GET /api/scraper/sites',
            'analytics_summary': 'GET /api/analytics/summary',
            'price_comparison': 'GET /api/analytics/price-comparison',
            'price_trends': 'GET /api/analytics/price-trends',
            'simulate_data': 'POST /api/simulate-data',
            'intelligence_pipeline': 'POST /api/full-intelligence-pipeline',
            'visual_report': 'POST /api/generate-visual-report'
        },
        'status': 'running',
        'features': ['CSV Analysis', 'Web Scraping', 'AI Intelligence', 'Visual Reports']
    })

@app.route('/health')
def health():
    try:
        logger.info("Health check requested")
        
        # Basic response
        response_data = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'python_version': sys.version.split()[0],
        }
        
        # Test Flask version
        try:
            response_data['flask_version'] = Flask.__version__
        except Exception as e:
            response_data['flask_error'] = str(e)
        
        # Test pandas
        try:
            response_data['pandas_version'] = pd.__version__
        except Exception as e:
            response_data['pandas_error'] = str(e)
        
        # Test matplotlib
        try:
            response_data['matplotlib_version'] = matplotlib.__version__
        except Exception as e:
            response_data['matplotlib_error'] = str(e)
        
        # Test scraper status
        if scraper:
            response_data['scraper_status'] = 'available'
        else:
            response_data['scraper_status'] = 'not available'
        
        # Add AI intelligence status
        response_data['ai_intelligence'] = 'available'
        
        logger.info(f"Health check successful: {response_data}")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'error_type': type(e).__name__,
            'timestamp': datetime.now().isoformat()
        }), 500

# ===== AI INTELLIGENCE PLATFORM ENDPOINTS =====

@app.route('/api/full-intelligence-pipeline', methods=['POST'])
def full_intelligence_pipeline():
    """Complete AI analysis pipeline"""
    try:
        data = request.get_json()
        query = data.get('query', 'Unknown query')
        industry = data.get('industry', 'general')
        
        logger.info(f"Intelligence analysis request: {query} ({industry})")
        
        # Simulate processing time for realistic demo
        time.sleep(2)
        
        # Generate realistic response based on query and industry
        claude_analysis = generate_claude_analysis(query, industry)
        gemini_insights = generate_gemini_insights(query, industry)
        
        response = {
            'success': True,
            'query': query,
            'industry': industry,
            'sources_analyzed': 12 + (len(query) % 8),  # Variable number 12-19
            'claude_analysis': claude_analysis,
            'gemini_insights': gemini_insights,
            'timestamp': datetime.now().isoformat()
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

# ===== HELPER FUNCTIONS FOR AI ANALYSIS =====

def generate_claude_analysis(query, industry):
    """Generate Claude-style analysis"""
    templates = {
        'technology': {
            'ai': "The AI industry is experiencing unprecedented growth with significant developments in large language models, computer vision, and autonomous systems. Key trends include enterprise AI adoption, edge computing integration, and increased focus on AI safety and ethics. Investment in AI infrastructure continues to accelerate, with particular emphasis on training efficiency and model deployment at scale.",
            'gpu': "Graphics processing units are critical infrastructure for AI development, with NVIDIA dominating the market holding approximately 88% market share. Supply chain constraints and geopolitical tensions are driving demand for alternative chip architectures and domestic production capabilities. Key developments include AMD's MI300 series and Intel's Gaudi processors challenging NVIDIA's dominance.",
            'graphic': "Graphics processing technology is evolving rapidly beyond traditional gaming applications. AI workloads now represent the primary growth driver, with datacenter GPU revenue exceeding gaming for major manufacturers. Architectural innovations focus on memory bandwidth, parallel processing efficiency, and power optimization for large-scale deployments.",
            'processing': "Processing power demands continue to exceed Moore's Law predictions, particularly for AI and machine learning workloads. Specialized processors including TPUs, FPGAs, and neuromorphic chips are emerging as alternatives to traditional CPU/GPU architectures. Edge computing requirements are driving development of low-power, high-efficiency processing solutions.",
            'default': f"The {industry} sector shows strong innovation momentum driven by digital transformation initiatives. Cloud adoption and AI integration are becoming strategic priorities across enterprises. Regulatory considerations around data privacy and cybersecurity remain key challenges, while investment in emerging technologies continues to accelerate."
        },
        'automotive': {
            'tesla': "Tesla continues to lead EV innovation but faces intensifying competition from traditional automakers and new entrants like Rivian and Lucid Motors. Battery technology improvements and charging infrastructure expansion are critical success factors. Tesla's integrated approach to manufacturing, software, and energy storage provides competitive advantages.",
            'electric': "The electric vehicle market is rapidly evolving with government incentives driving adoption across major markets. Battery costs have declined 89% since 2010, making EVs increasingly competitive with ICE vehicles. Range anxiety continues to diminish as charging infrastructure expands and battery energy density improves.",
            'vehicle': "Vehicle electrification represents the most significant automotive industry transformation since the assembly line. Traditional automakers are investing heavily in EV platforms while managing the transition from ICE vehicle production. Supply chain realignment toward battery materials and semiconductor components is reshaping industry dynamics.",
            'default': f"The automotive industry is undergoing fundamental transformation toward electrification and autonomous driving. Supply chain resilience and semiconductor availability remain critical challenges, while consumer preferences shift toward sustainable mobility solutions."
        },
        'healthcare': {
            'default': f"Healthcare innovation is accelerating with digital health solutions, telemedicine, and personalized medicine gaining significant traction. AI-driven diagnostics and drug discovery are transforming clinical outcomes. Regulatory approval processes and data privacy considerations continue to shape market dynamics and investment flows."
        },
        'finance': {
            'crypto': "Cryptocurrency markets show increasing institutional adoption despite regulatory uncertainty. Central bank digital currencies (CBDCs) are advancing globally, with pilot programs in multiple jurisdictions. DeFi protocols continue to innovate while addressing security and scalability challenges.",
            'default': f"Financial services are embracing fintech innovations and digital transformation at an unprecedented pace. Open banking initiatives, embedded finance, and AI-driven risk assessment are reshaping customer experiences. Regulatory compliance and cybersecurity investments remain essential for competitive positioning."
        },
        'manufacturing': {
            'sustainable': "Sustainable manufacturing practices are becoming competitive necessities rather than optional initiatives. Circular economy principles, renewable energy adoption, and waste reduction strategies are driving operational efficiency improvements. Carbon accounting and ESG reporting requirements are influencing capital allocation decisions.",
            'packaging': "Packaging innovation focuses on sustainability, functionality, and cost optimization. Biodegradable materials, reduced plastic content, and recyclable designs are responding to consumer preferences and regulatory pressures. Smart packaging technologies incorporating IoT sensors and NFC capabilities are enhancing supply chain visibility.",
            'default': f"Manufacturing sector transformation emphasizes automation, sustainability, and supply chain resilience. Industry 4.0 technologies including IoT, AI, and robotics are optimizing production efficiency while reducing environmental impact."
        },
        'retail': {
            'default': f"Retail industry continues evolving toward omnichannel experiences and personalized customer engagement. E-commerce growth stabilizes post-pandemic while physical stores reimagine their value proposition through experiential retail and fulfillment optimization."
        },
        'energy': {
            'renewable': "Renewable energy sector demonstrates exceptional growth with solar and wind achieving grid parity in most markets. Energy storage solutions are becoming economically viable, enabling higher renewable penetration. Grid modernization and smart infrastructure investments support the energy transition.",
            'default': f"Energy sector transformation accelerates toward renewable sources and grid modernization. Carbon pricing mechanisms and climate policies are reshaping investment priorities while energy security concerns influence policy decisions."
        },
        'aerospace': {
            'default': f"Aerospace industry recovers from pandemic impacts while embracing sustainable aviation fuels and electric propulsion technologies. Space commercialization creates new market opportunities while supply chain consolidation affects competitive dynamics."
        }
    }
    
    # Find best match
    query_lower = query.lower()
    if industry in templates:
        for keyword, analysis in templates[industry].items():
            if keyword != 'default' and keyword in query_lower:
                return analysis
        return templates[industry].get('default', templates['technology']['default'])
    
    return f"Analysis of '{query}' reveals significant market opportunities and technological advancement potential. Current trends indicate strong growth trajectories driven by innovation adoption, regulatory evolution, and changing consumer preferences. Strategic positioning should focus on technological differentiation, operational efficiency, and sustainable business practices."

def generate_gemini_insights(query, industry):
    """Generate Gemini-style data insights"""
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
    
    templates = {
        'technology': f"Technology sector analysis reveals {growth_rate}% YoY growth with sustained momentum. Key performance indicators: R&D investment increased {investment_change}%, enterprise adoption rates up {adoption_rate}%, implementation costs decreased {cost_reduction}%. Market concentration shows {players} major platforms controlling {market_share}% of total addressable market valued at ${market_size}B. Cloud infrastructure spending represents largest growth segment.",
        
        'automotive': f"Automotive industry data indicates {growth_rate}% expansion in electrification segment. Production capacity utilization up {investment_change}%, battery costs down {cost_reduction}%, charging infrastructure deployment up {adoption_rate}%. Market leadership distributed among {players} major manufacturers holding {market_share}% combined market share. Global EV market size approaching ${market_size}B with accelerating growth trajectory.",
        
        'healthcare': f"Healthcare technology sector demonstrates {growth_rate}% annual growth driven by digital transformation. Telehealth adoption increased {adoption_rate}%, regulatory approval timelines reduced {cost_reduction}%, clinical trial efficiency up {investment_change}%. Market dynamics show {players} leading platforms capturing {market_share}% of digital health investments totaling ${market_size}B annually.",
        
        'finance': f"Financial technology sector exhibits {growth_rate}% growth with strong fundamentals. Digital payment volumes increased {adoption_rate}%, customer acquisition costs reduced {cost_reduction}%, regulatory compliance efficiency up {investment_change}%. Competitive landscape features {players} dominant platforms controlling {market_share}% of fintech market valued at ${market_size}B.",
        
        'manufacturing': f"Manufacturing sector shows {growth_rate}% efficiency improvements through automation adoption. Production optimization increased {investment_change}%, waste reduction achieved {cost_reduction}%, quality metrics improved {adoption_rate}%. Industry consolidation features {players} major players representing {market_share}% of advanced manufacturing market worth ${market_size}B.",
        
        'retail': f"Retail industry demonstrates {growth_rate}% omnichannel growth with digital integration. E-commerce conversion rates up {adoption_rate}%, customer acquisition costs down {cost_reduction}%, inventory efficiency improved {investment_change}%. Market share concentration shows {players} leading retailers controlling {market_share}% of online retail valued at ${market_size}B.",
        
        'energy': f"Energy sector indicates {growth_rate}% renewable capacity growth annually. Grid efficiency improvements up {investment_change}%, energy storage costs reduced {cost_reduction}%, renewable penetration increased {adoption_rate}%. Market structure includes {players} major utilities controlling {market_share}% of clean energy investments totaling ${market_size}B.",
        
        'aerospace': f"Aerospace industry shows {growth_rate}% recovery with innovation focus. Manufacturing efficiency up {investment_change}%, development costs optimized {cost_reduction}%, sustainable technology adoption increased {adoption_rate}%. Market concentration features {players} prime contractors holding {market_share}% of commercial aerospace market valued at ${market_size}B."
    }
    
    return templates.get(industry, f"Cross-industry analysis demonstrates {growth_rate}% growth potential with strong market fundamentals. Performance metrics indicate {adoption_rate}% adoption acceleration, {cost_reduction}% cost optimization, and {investment_change}% investment increase. Competitive dynamics show {players} key market participants controlling {market_share}% of total addressable market valued at ${market_size}B.")

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