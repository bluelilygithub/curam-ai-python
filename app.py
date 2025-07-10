from flask import Flask, render_template, request, send_file, flash, redirect, url_for, jsonify
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import os
from werkzeug.utils import secure_filename
from scraper import WebScraper
import sqlite3
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize scraper
scraper = WebScraper()

@app.route('/')
def index():
    return render_template('index.html')

# Original report generator routes
@app.route('/reports')
def reports():
    return render_template('reports.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(url_for('reports'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('reports'))
    
    if file and file.filename.endswith('.csv'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        try:
            report_path = generate_report(filepath)
            return send_file(report_path, as_attachment=True, download_name='report.pdf')
        except Exception as e:
            flash(f'Error generating report: {str(e)}')
            return redirect(url_for('reports'))
    
    flash('Please upload a CSV file')
    return redirect(url_for('reports'))

# New scraper routes
@app.route('/scraper')
def scraper_dashboard():
    conn = sqlite3.connect('scraper.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, url, price_selector FROM monitored_sites')
    sites = cursor.fetchall()
    conn.close()
    return render_template('scraper.html', sites=sites)

@app.route('/add_site', methods=['POST'])
def add_site():
    name = request.form['name']
    url = request.form['url']
    price_selector = request.form['price_selector']
    
    scraper.add_site(name, url, price_selector)
    flash(f'Added {name} to monitoring list')
    return redirect(url_for('scraper_dashboard'))

@app.route('/scrape_now')
def scrape_now():
    results = scraper.scrape_all_sites()
    return jsonify({'results': results})

@app.route('/price_history/<int:site_id>')
def price_history(site_id):
    history = scraper.get_price_history(site_id)
    return jsonify({'history': history})

def generate_report(csv_file):
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
    report_filename = 'report.pdf'
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)