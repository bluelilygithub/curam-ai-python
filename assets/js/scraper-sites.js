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
                <p>No sites are being monitored yet.</p>
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
                        View History
                    </button>
                </td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

function refreshSites() {
    loadSites();
    showFlash('Sites list refreshed!', 'success');
}

// Handle add site form
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
            toggleAddSiteForm();
            loadSites();
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

// View price history
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
                <h4>Price History for: ${siteName}</h4>`;
            
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
            
            historyHtml += `
                <div style="margin-top: 20px; text-align: center;">
                    <button onclick="loadSites(); document.getElementById('results').innerHTML = '';" class="btn btn-secondary" style="background: #6c757d; color: white; font-family: 'Montserrat', sans-serif;">
                        Back to Sites
                    </button>
                </div>
            </div>`;
            
            document.getElementById('results').innerHTML = historyHtml;
        } else {
            showFlash(`Error loading history: ${result.error}`, 'error');
        }
    } catch (error) {
        showFlash(`Error loading history: ${error.message}`, 'error');
    }
}