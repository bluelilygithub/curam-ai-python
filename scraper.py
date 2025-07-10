import requests
from bs4 import BeautifulSoup
import sqlite3
import datetime
import re
import time

class WebScraper:
    def __init__(self, db_path='scraper.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monitored_sites (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                price_selector TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY,
                site_id INTEGER,
                price REAL,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (site_id) REFERENCES monitored_sites (id)
            )
        ''')
        conn.commit()
        conn.close()
    
    def add_site(self, name, url, price_selector):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO monitored_sites (name, url, price_selector) VALUES (?, ?, ?)',
            (name, url, price_selector)
        )
        conn.commit()
        conn.close()
    
    def scrape_price(self, url, price_selector):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find price element
            price_element = soup.select_one(price_selector)
            if price_element:
                price_text = price_element.get_text()
                # Extract number from price text
                price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                if price_match:
                    return float(price_match.group())
            return None
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return None
    
    def scrape_all_sites(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, url, price_selector FROM monitored_sites')
        sites = cursor.fetchall()
        
        results = []
        for site_id, name, url, price_selector in sites:
            price = self.scrape_price(url, price_selector)
            if price:
                cursor.execute(
                    'INSERT INTO price_history (site_id, price) VALUES (?, ?)',
                    (site_id, price)
                )
                results.append(f"{name}: ${price}")
            time.sleep(2)  # Be respectful to websites
        
        conn.commit()
        conn.close()
        return results
    
    def get_price_history(self, site_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT price, scraped_at FROM price_history 
            WHERE site_id = ? 
            ORDER BY scraped_at DESC LIMIT 50
        ''', (site_id,))
        history = cursor.fetchall()
        conn.close()
        return history