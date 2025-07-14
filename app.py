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

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configure CORS for your shared hosting domain
CORS(app, origins=[
    'https://curam-ai.com.au',  # Your shared hosting domain
    'https://curam-ai.com.au/curam-ai-python/',     # Replace with actual domain where HTML is hosted
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
        'name': 'Python Data Analytics API',
        'version': '1.0.0',
        'description': 'Flask API with pandas, matplotlib, web scraping, and PDF generation',
        'endpoints': {
            'health': '/health',
            'upload_csv': 'POST /api/upload-csv',
            'generate_report': 'POST /api/generate-report',
            'add_site': 'POST /api/scraper/add-site',
            'scrape_now': 'POST /api/scraper/scrape-now',
            'price_history': 'GET /api/scraper/price-history/<site_id>',
            'get_sites': 'GET /api/scraper/sites'
        },
        'status': 'running'
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


    # Add these endpoints to your app.py for analytics and graphing

@app.route('/api/analytics/price-comparison', methods=['GET'])
def price_comparison():
    """Get price comparison data for bar charts"""
    try:
        if not scraper:
            return jsonify({'success': False, 'error': 'Scraper not available'}), 500
        
        analytics = scraper.get_price_analytics()
        
        # Format for chart.js
        chart_data = {
            'labels': [item['name'][:20] + '...' if len(item['name']) > 20 else item['name'] 
                      for item in analytics['average_prices']],
            'datasets': [{
                'label': 'Average Price ($)',
                'data': [item['avg_price'] for item in analytics['average_prices']],
                'backgroundColor': [
                    'rgba(255, 99, 132, 0.6)',
                    'rgba(54, 162, 235, 0.6)',
                    'rgba(255, 205, 86, 0.6)',
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(153, 102, 255, 0.6)',
                    'rgba(255, 159, 64, 0.6)',
                    'rgba(199, 199, 199, 0.6)',
                    'rgba(83, 102, 255, 0.6)'
                ],
                'borderColor': [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 205, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)',
                    'rgba(199, 199, 199, 1)',
                    'rgba(83, 102, 255, 1)'
                ],
                'borderWidth': 1
            }]
        }
        
        return jsonify({
            'success': True,
            'chart_data': chart_data,
            'raw_data': analytics['average_prices']
        })
        
    except Exception as e:
        logger.error(f"Price comparison error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analytics/price-trends', methods=['GET'])
def price_trends():
    """Get price trends over time for line charts"""
    try:
        if not scraper:
            return jsonify({'success': False, 'error': 'Scraper not available'}), 500
        
        analytics = scraper.get_price_analytics()
        
        # Group by site for multiple lines
        site_data = {}
        for item in analytics['price_trends']:
            site_name = item['name'][:15] + '...' if len(item['name']) > 15 else item['name']
            if site_name not in site_data:
                site_data[site_name] = {'dates': [], 'prices': []}
            
            site_data[site_name]['dates'].append(item['date'])
            site_data[site_name]['prices'].append(item['price'])
        
        # Format for chart.js line chart
        datasets = []
        colors = [
            'rgb(255, 99, 132)', 'rgb(54, 162, 235)', 'rgb(255, 205, 86)',
            'rgb(75, 192, 192)', 'rgb(153, 102, 255)', 'rgb(255, 159, 64)'
        ]
        
        for i, (site, data) in enumerate(site_data.items()):
            datasets.append({
                'label': site,
                'data': data['prices'][:10],  # Last 10 data points
                'borderColor': colors[i % len(colors)],
                'backgroundColor': colors[i % len(colors)] + '20',  # 20% opacity
                'tension': 0.4
            })
        
        # Use dates from first site for x-axis
        first_site = list(site_data.values())[0] if site_data else {'dates': []}
        labels = [datetime.fromisoformat(date).strftime('%m/%d %H:%M') 
                 for date in first_site['dates'][:10]]
        
        chart_data = {
            'labels': labels,
            'datasets': datasets
        }
        
        return jsonify({
            'success': True,
            'chart_data': chart_data,
            'raw_data': analytics['price_trends']
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