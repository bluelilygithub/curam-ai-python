// Load monitored sites
async function loadSites() {
    try {
        const response = await fetch(`${API_BASE}/api/scraper/sites`);
        const result = await response.json();
        
        if (result.success) {
            displaySites(result.sites);
        } else {
            displayError(result.error, 'sites-list');
        }
    } catch (error) {
        displayError(error.message, 'sites-list');
    }
}

// Display sites in table
function displaySites(sites) {
    const container = document.getElementById('sites-list');
    
    if (sites.length === 0) {
        container.innerHTML = '<p class="text-muted">No sites being monitored yet.</p>';
        return;
    }
    
    let html = `
        <div class="table-responsive">
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>URL</th>
                        <th>Price Selector</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    sites.forEach(site => {
        html += `
            <tr>
                <td>${site.name}</td>
                <td><a href="${site.url}" target="_blank">${site.url}</a></td>
                <td><code>${site.price_selector}</code></td>
                <td>
                    <button class="btn btn-sm btn-info" onclick="viewHistory(${site.id})">View History</button>
                </td>
            </tr>
        `;
    });
    
    html += '</tbody></table></div>';
    container.innerHTML = html;
}

// Add new site
document.getElementById('addSiteForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = {
        name: document.getElementById('siteName').value,
        url: document.getElementById('siteUrl').value,
        price_selector: document.getElementById('priceSelector').value
    };
    
    try {
        const response = await fetch(`${API_BASE}/api/scraper/add-site`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('✅ Site added successfully!');
            this.reset();
            loadSites(); // Reload the sites list
        } else {
            alert(`❌ Error: ${result.error}`);
        }
    } catch (error) {
        alert(`❌ Error: ${error.message}`);
    }
});

// Scrape all sites now
async function scrapeAllNow() {
    try {
        const response = await fetch(`${API_BASE}/api/scraper/scrape-now`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            document.getElementById('results-card').style.display = 'block';
            displayResults(result.results, 'scraping-results');
        } else {
            displayError(result.error, 'scraping-results');
        }
    } catch (error) {
        displayError(error.message, 'scraping-results');
    }
}

// View price history for a site
async function viewHistory(siteId) {
    try {
        const response = await fetch(`${API_BASE}/api/scraper/price-history/${siteId}`);
        const result = await response.json();
        
        if (result.success) {
            displayResults(result.history, 'scraping-results');
            document.getElementById('results-card').style.display = 'block';
        } else {
            displayError(result.error, 'scraping-results');
        }
    } catch (error) {
        displayError(error.message, 'scraping-results');
    }
}

// Initialize scraper page
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('sites-list')) {
        loadSites();
    }
});