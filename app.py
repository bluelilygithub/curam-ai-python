from flask import Flask, request, send_file, jsonify, Response
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

# Brisbane Property Intelligence imports
from llm_pipeline import BrisbanePropertyPipeline
from database import PropertyDatabase

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

# Initialize Brisbane Property Intelligence
property_pipeline = BrisbanePropertyPipeline()

# Initialize scraper with error handling (keep existing scraper if needed)
scraper = None
try:
    from scraper import WebScraper
    scraper = WebScraper()
    logger.info("Scraper initialized successfully")
except Exception as e:
    logger.error(f"Scraper initialization failed: {str(e)}")
    scraper = None

# ===== MAIN ENDPOINTS =====

@app.route('/')
def index():
    """Brisbane Property Intelligence API"""
    return jsonify({
        'name': 'Brisbane Property Intelligence API',
        'version': '1.0.0',
        'description': 'Multi-LLM Brisbane property analysis with Claude, Gemini, and real-time data scraping',
        'endpoints': {
            'health': '/health',
            'property_questions': 'GET /api/property/questions',
            'property_analyze': 'POST /api/property/analyze',
            'property_stream': 'POST /api/property/analyze-stream',
            'property_history': 'GET /api/property/history',
            'property_query_details': 'GET /api/property/query/<id>',
            'property_reset': 'POST /api/property/reset',
            'property_stats': 'GET /api/property/stats',
            'email_results': 'POST /api/property/email-results'
        },
        'status': 'running',
        'features': [
            'Multi-LLM Analysis (Claude + Gemini)',
            'Real-time Brisbane Property Data',
            'Query History & Analytics',
            'Streaming Progress Updates',
            'Brisbane-specific Insights'
        ],
        'ai_services': {
            'claude': 'Available' if property_pipeline.claude_client else 'Mock Mode',
            'gemini': 'Available' if property_pipeline.gemini_model else 'Mock Mode',
            'data_scraping': 'Active'
        },
        'preset_questions': property_pipeline.get_preset_questions(),
        'data_sources': [
            'Brisbane City Council RSS',
            'Property Observer Brisbane',
            'RealEstate.com.au News',
            'Queensland Government Data'
        ]
    })

@app.route('/health')
def health():
    """Health check for Brisbane Property Intelligence"""
    try:
        logger.info("Health check requested")
        
        # Test database connection
        try:
            stats = property_pipeline.get_database_stats()
            database_status = True
        except Exception as e:
            database_status = False
            logger.error(f"Database health check failed: {str(e)}")
        
        # Test LLM connections
        claude_status = property_pipeline.claude_client is not None
        gemini_status = property_pipeline.gemini_model is not None
        
        response_data = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'python_version': sys.version.split()[0],
            'services': {
                'flask': True,
                'database': database_status,
                'claude': claude_status,
                'gemini': gemini_status,
                'data_scraping': True,
                'scraper': scraper is not None
            },
            'database_stats': stats if database_status else {},
            'environment': {
                'claude_api_configured': bool(os.getenv('CLAUDE_API_KEY')),
                'gemini_api_configured': bool(os.getenv('GEMINI_API_KEY'))
            }
        }
        
        # Test core libraries
        try:
            response_data['flask_version'] = Flask.__version__
            response_data['pandas_version'] = pd.__version__
            response_data['requests_version'] = requests.__version__
        except Exception as e:
            response_data['library_error'] = str(e)
        
        overall_status = all([
            response_data['services']['flask'],
            response_data['services']['database']
        ])
        
        if not overall_status:
            response_data['status'] = 'degraded'
        
        status_code = 200 if overall_status else 503
        
        logger.info(f"Health check completed: {response_data['status']}")
        return jsonify(response_data), status_code
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# ===== BRISBANE PROPERTY INTELLIGENCE ENDPOINTS =====

@app.route('/api/property/questions', methods=['GET'])
def get_property_questions():
    """Return dropdown questions (preset + popular from database)"""
    try:
        questions = property_pipeline.get_popular_questions(15)
        
        response = {
            'success': True,
            'questions': questions,
            'preset_questions': property_pipeline.get_preset_questions(),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Get questions error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/property/analyze', methods=['POST'])
def analyze_property_question():
    """Main LLM pipeline endpoint"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Question is required'
            }), 400
        
        # Determine question type
        preset_questions = property_pipeline.get_preset_questions()
        question_type = 'preset' if question in preset_questions else 'custom'
        
        logger.info(f"Processing property question: {question} (type: {question_type})")
        
        # Process through pipeline and collect all updates
        updates = []
        final_result = None
        
        for update in property_pipeline.process_query(question, question_type):
            updates.append(update)
            if update['status'] == 'complete':
                final_result = update.get('data', {})
        
        # Return complete response
        response = {
            'success': True,
            'question': question,
            'question_type': question_type,
            'processing_updates': updates,
            'final_answer': final_result.get('final_answer', '') if final_result else '',
            'processing_time': final_result.get('processing_time', 0) if final_result else 0,
            'query_id': final_result.get('query_id') if final_result else None,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Property analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/property/analyze-stream', methods=['POST'])
def analyze_property_stream():
    """Stream processing updates in real-time"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Question is required'
            }), 400
        
        # Determine question type
        preset_questions = property_pipeline.get_preset_questions()
        question_type = 'preset' if question in preset_questions else 'custom'
        
        def generate_stream():
            """Generate streaming response"""
            try:
                # Send initial message
                yield f"data: {json.dumps({'status': 'started', 'message': f'Processing: {question}'})}\n\n"
                
                # Process through pipeline
                for update in property_pipeline.process_query(question, question_type):
                    yield f"data: {json.dumps(update)}\n\n"
                
                # Send completion signal
                yield f"data: {json.dumps({'status': 'stream_complete'})}\n\n"
                
            except Exception as e:
                error_update = {
                    'status': 'error',
                    'message': f'Streaming error: {str(e)}',
                    'timestamp': datetime.now().isoformat()
                }
                yield f"data: {json.dumps(error_update)}\n\n"
        
        return Response(
            generate_stream(),
            content_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        )
        
    except Exception as e:
        logger.error(f"Property stream error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/property/history', methods=['GET'])
def get_property_history():
    """Get query history"""
    try:
        limit = request.args.get('limit', 50, type=int)
        history = property_pipeline.get_query_history(limit)
        
        response = {
            'success': True,
            'history': history,
            'count': len(history),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Get history error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/property/query/<int:query_id>', methods=['GET'])
def get_query_details(query_id):
    """Get detailed information about a specific query"""
    try:
        details = property_pipeline.get_query_details(query_id)
        
        if not details:
            return jsonify({
                'success': False,
                'error': 'Query not found'
            }), 404
        
        response = {
            'success': True,
            'query_details': details,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Get query details error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/property/reset', methods=['POST'])
def reset_property_session():
    """Reset database/session"""
    try:
        property_pipeline.reset_database()
        
        response = {
            'success': True,
            'message': 'Database reset successfully',
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Reset session error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/property/stats', methods=['GET'])
def get_property_stats():
    """Get database and processing statistics"""
    try:
        stats = property_pipeline.get_database_stats()
        data_sources = property_pipeline.get_data_sources_status()
        
        response = {
            'success': True,
            'stats': stats,
            'data_sources': data_sources,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Get stats error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/property/email-results', methods=['POST'])
def email_property_results():
    """Email query results to user"""
    try:
        data = request.get_json()
        query_id = data.get('query_id')
        email = data.get('email')
        
        if not query_id or not email:
            return jsonify({
                'success': False,
                'error': 'Query ID and email are required'
            }), 400
        
        # Get query details
        query_details = property_pipeline.get_query_details(query_id)
        if not query_details:
            return jsonify({
                'success': False,
                'error': 'Query not found'
            }), 404
        
        # For now, return success (implement actual email sending later)
        response = {
            'success': True,
            'message': f'Results would be sent to {email}',
            'query_id': query_id,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Email results error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ===== KEEP EXISTING USEFUL ENDPOINTS =====

# CSV Upload and Analysis API (keep this - it's useful)
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

# Generate Report API (keep this - it's useful)
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

# ===== KEEP EXISTING SCRAPER ENDPOINTS IF NEEDED =====

# Scraper APIs - Only if you want to keep existing scraper functionality
if scraper:
    @app.route('/api/scraper/sites', methods=['GET'])
    def get_monitored_sites():
        try:
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

# ===== HELPER FUNCTIONS =====

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
    logger.info(f"Starting Brisbane Property Intelligence on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)