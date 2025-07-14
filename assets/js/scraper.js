// API Configuration - UPDATE THIS WITH YOUR RAILWAY URL
const API_BASE = 'https://curam-ai-python-production.up.railway.app';

// Global state
let apiConnected = false;
let sites = [];

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    checkAPIConnection();
    loadSites();
    
    // Setup form submission
    document.getElementById('add-site-form').addEventListener('submit', handleAddSite);
});

// Check API connection
async function checkAPIConnection() {
    const statusElement = document.getElementById('api-status');
    
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        
        if (data.status === 'healthy') {
            statusElement.className = 'api-status status-connected';
            statusElement.innerHTML = 'Connected to API - Status: ' + data.status;
            apiConnected = true;
            enableButtons();
        } else {
            throw new Error('API not healthy');
        }
    } catch (error) {
        statusElement.className = 'api-status status-error';
        statusElement.innerHTML = 'Cannot connect to API: ' + error.message;
        apiConnected = false;
        disableButtons();
    }
}

// Enable/disable buttons based on API connection
function enableButtons() {
    document.getElementById('scrape-btn').disabled = false;
    document.getElementById('refresh-btn').disabled = false;
    document.getElementById('add-site-btn').disabled = false;
}

function disableButtons() {
    document.getElementById('scrape-btn').disabled = true;
    document.getElementById('refresh-btn').disabled = true;
    document.getElementById('add-site-btn').disabled = true;
}

// Show flash messages
function showFlash(message, type = 'success') {
    const flashContainer = document.getElementById('flash-messages');
    const flashDiv = document.createElement('div');
    flashDiv.className = `flash flash-${type}`;
    flashDiv.innerHTML = message;
    flashContainer.appendChild(flashDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        flashDiv.remove();
    }, 5000);
}

// Load monitored sites
async function loadSites() {
    if (!apiConnected) return;
    
    const container = document.getElementById('sites-container');
    container.innerHTML = '<div class="loading">Loading monitored sites</div>';
    
    try {
        const response = await fetch(`${API_BASE}/api/scraper/sites`);
        const data = await response.json();
        
        if (data.success) {
            sites = data.sites;
            displaySites(sites);
        } else {
            container.innerHTML = `<div class="flash flash-error">Error loading sites: ${data.error}</div>`;
        }
    } catch (error) {
        container.innerHTML = `<div class="flash flash-error">Error loading sites: ${error.message}</div>`;
    }
}

// Display sites in table
function displaySites(sitesList) {
    const container = document.getElementById('sites-container');
    
    if (sitesList.length === 0) {
        container.innerHTML = `
            <div class="no-sites">
                <p>🔍 No sites are being monitored yet.</p>
                <p>Add your first site using the form above!</p>
            </div>
        `;
        return;
    }
    
    let html = `
        <table class="sites-table">
            <thead>
                <tr>
                    <th>Site Name</th>
                    <th>URL</th>
                    <th>Price Selector</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    sitesList.forEach(site => {
        html += `
            <tr>
                <td><strong>${site.name}</strong></td>
                <td class="site-url">
                    <a href="${site.url}" target="_blank" title="${site.url}">
                        ${site.url.length > 50 ? site.url.substring(0, 50) + '...' : site.url}
                    </a>
                </td>
                <td><code>${site.price_selector}</code></td>
                <td>
                    <button onclick="viewHistory(${site.id})" class="btn btn-info" style="font-size: 12px; padding: 6px 12px;">
                        📊 View History
                    </button>
                </td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

// Refresh sites list
function refreshSites() {
    loadSites();
    showFlash('Sites list refreshed!', 'success');
}

// Handle add site form submission
async function handleAddSite(e) {
    e.preventDefault();
    
    if (!apiConnected) {
        showFlash('Cannot add site - API not connected', 'error');
        return;
    }
    
    const formData = {
        name: document.getElementById('site-name').value.trim(),
        url: document.getElementById('site-url').value.trim(),
        price_selector: document.getElementById('price-selector').value.trim()
    };
    
    // Validate form
    if (!formData.name || !formData.url || !formData.price_selector) {
        showFlash('Please fill in all fields', 'error');
        return;
    }
    
    const addButton = document.getElementById('add-site-btn');
    addButton.disabled = true;
    addButton.innerHTML = 'Adding...';
    
    try {
        const response = await fetch(`${API_BASE}/api/scraper/add-site`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showFlash(`Successfully added "${formData.name}" to monitoring list!`, 'success');
            document.getElementById('add-site-form').reset();
            loadSites(); // Refresh the sites list
        } else {
            showFlash(`Error adding site: ${result.error}`, 'error');
        }
    } catch (error) {
        showFlash(`Error adding site: ${error.message}`, 'error');
    } finally {
        addButton.disabled = false;
        addButton.innerHTML = 'Add Site to Monitor';
    }
}

// Scrape all sites now
async function scrapeNow() {
    if (!apiConnected) {
        showFlash('Cannot scrape - API not connected', 'error');
        return;
    }
    
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '<div class="results"><div class="loading">Scraping all sites in progress</div></div>';
    
    const scrapeButton = document.getElementById('scrape-btn');
    scrapeButton.disabled = true;
    scrapeButton.innerHTML = 'Scraping...';
    
    try {
        const response = await fetch(`${API_BASE}/api/scraper/scrape-now`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            let resultHtml = '<div class="results"><h4>📊 Scraping Results:</h4>';
            
            if (data.results && data.results.length > 0) {
                resultHtml += '<ul>';
                data.results.forEach(result => {
                    const status = result.status === 'success' ? 'yes' : 'no';
                    const price = result.price ? `$${result.price}` : 'Failed to get price';
                    resultHtml += `<li><strong>${result.name}</strong>: ${status} ${price}</li>`;
                });
                resultHtml += '</ul>';
            } else {
                resultHtml += '<p>No sites to scrape. Add some sites first!</p>';
            }
            
            resultHtml += `<small>Scraped at: ${data.timestamp}</small></div>`;
            resultsDiv.innerHTML = resultHtml;
            
            showFlash('Scraping completed!', 'success');
        } else {
            resultsDiv.innerHTML = `<div class="flash flash-error">Scraping failed: ${data.error}</div>`;
        }
    } catch (error) {
        resultsDiv.innerHTML = `<div class="flash flash-error">Scraping error: ${error.message}</div>`;
    } finally {
        scrapeButton.disabled = false;
        scrapeButton.innerHTML = 'Scrape All Sites Now';
    }
}

// View price history for a site
async function viewHistory(siteId) {
    if (!apiConnected) {
        showFlash('Cannot view history - API not connected', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/scraper/price-history/${siteId}`);
        const result = await response.json();
        
        if (result.success) {
            const site = sites.find(s => s.id === siteId);
            const siteName = site ? site.name : `Site ${siteId}`;
            
            let historyHtml = `<div class="results">
                <h4>📊 Price History for: ${siteName}</h4>`;
            
            if (result.history && result.history.length > 0) {
                historyHtml += '<table class="sites-table"><thead><tr><th>Price</th><th>Date</th></tr></thead><tbody>';
                result.history.slice(0, 10).forEach(record => {
                    historyHtml += `<tr>
                        <td><strong>$${record.price}</strong></td>
                        <td>${new Date(record.scraped_at).toLocaleString()}</td>
                    </tr>`;
                });
                historyHtml += '</tbody></table>';
                
                if (result.history.length > 10) {
                    historyHtml += `<small>Showing latest 10 of ${result.history.length} records</small>`;
                }
            } else {
                historyHtml += '<p>No price history available for this site yet.</p>';
            }
            
            historyHtml += '</div>';
            document.getElementById('results').innerHTML = historyHtml;
        } else {
            showFlash(`Error loading history: ${result.error}`, 'error');
        }
    } catch (error) {
        showFlash(`Error loading history: ${error.message}`, 'error');
    }
}