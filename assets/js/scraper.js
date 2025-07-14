// API Configuration - UPDATE THIS WITH YOUR RAILWAY URL
const API_BASE = 'https://curam-ai-python-production.up.railway.app';

// Global state
let apiConnected = false;
let sites = [];

// Initialize page
document.addEventListener('DOMContentLoaded', async function() {
    await checkAPIConnection();  // Wait for API check to complete
    loadSites();                 // Then load sites
    
    // Setup form submissions
    document.getElementById('add-site-form').addEventListener('submit', handleAddSite);
    
    // Only add categories form listener if the form exists
    const categoriesForm = document.getElementById('categories-form');
    if (categoriesForm) {
        categoriesForm.addEventListener('submit', handleAddCategories);
    }
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
    document.getElementById('add-site-toggle-btn').disabled = false;
    document.getElementById('scrape-categories-btn').disabled = false;
    document.getElementById('add-site-btn').disabled = false;
    const addCategoriesBtn = document.getElementById('add-categories-btn');
    if (addCategoriesBtn) addCategoriesBtn.disabled = false;
    // Enable analytics buttons if they exist
    const demoBtn = document.getElementById('demo-btn');
    const analyticsBtn = document.getElementById('analytics-btn');
    if (demoBtn) demoBtn.disabled = false;
    if (analyticsBtn) analyticsBtn.disabled = false;
}

function disableButtons() {
    document.getElementById('scrape-btn').disabled = true;
    document.getElementById('refresh-btn').disabled = true;
    document.getElementById('add-site-toggle-btn').disabled = true;
    document.getElementById('scrape-categories-btn').disabled = true;
    document.getElementById('add-site-btn').disabled = true;
    const addCategoriesBtn = document.getElementById('add-categories-btn');
    if (addCategoriesBtn) addCategoriesBtn.disabled = true;
    // Disable analytics buttons if they exist
    const demoBtn = document.getElementById('demo-btn');
    const analyticsBtn = document.getElementById('analytics-btn');
    if (demoBtn) demoBtn.disabled = true;
    if (analyticsBtn) analyticsBtn.disabled = true;
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

// Show progress bar
function showProgressBar(message, progressId = 'main-progress') {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = `
        <div class="results">
            <h4 style="font-family: 'Montserrat', sans-serif;">${message}</h4>
            <div style="background: #f8f9fa; border-radius: 8px; padding: 20px; margin: 20px 0;">
                <div style="margin-bottom: 10px; font-weight: bold; font-family: 'Montserrat', sans-serif;">${message}</div>
                <div style="background: #e9ecef; border-radius: 10px; height: 20px; overflow: hidden;">
                    <div id="${progressId}" style="background: linear-gradient(90deg, #007bff, #0056b3); height: 100%; width: 0%; transition: width 0.3s ease; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white; font-size: 12px; font-weight: bold; font-family: 'Montserrat', sans-serif;"></div>
                </div>
                <div id="progress-status" style="margin-top: 10px; font-size: 14px; color: #6c757d; font-family: 'Montserrat', sans-serif;">Starting...</div>
            </div>
        </div>
    `;
}

// Update progress bar
function updateProgress(percentage, status, progressId = 'main-progress') {
    const progressBar = document.getElementById(progressId);
    const statusElement = document.getElementById('progress-status');
    
    if (progressBar) {
        progressBar.style.width = percentage + '%';
        progressBar.textContent = percentage + '%';
    }
    
    if (statusElement) {
        statusElement.textContent = status;
    }
}

// Add back button to results
function addBackButton() {
    const resultsDiv = document.getElementById('results');
    const backButton = `
        <div style="margin-top: 20px; text-align: center;">
            <button onclick="goBackToAnalytics()" class="btn btn-secondary" style="background: #6c757d; color: white; font-family: 'Montserrat', sans-serif;">
                Back to Analytics
            </button>
        </div>
    `;
    resultsDiv.innerHTML += backButton;
}

// Toggle categories form visibility
function toggleCategoriesForm() {
    const formContainer = document.getElementById('categories-form-container');
    const toggleButton = document.getElementById('scrape-categories-btn');
    
    if (formContainer.style.display === 'none' || formContainer.style.display === '') {
        // Hide add site form if it's open
        const addSiteContainer = document.getElementById('add-site-form-container');
        if (addSiteContainer.style.display === 'block') {
            toggleAddSiteForm();
        }
        
        formContainer.style.display = 'block';
        toggleButton.innerHTML = 'Cancel Categories';
        toggleButton.className = 'btn btn-secondary';
        // Clear checkboxes
        const checkboxes = document.querySelectorAll('#categories-form input[type="checkbox"]');
        checkboxes.forEach(cb => cb.checked = false);
    } else {
        formContainer.style.display = 'none';
        toggleButton.innerHTML = 'Scrape Book Categories';
        toggleButton.className = 'btn btn-secondary';
    }
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
            toggleAddSiteForm(); // Hide the form after successful addition
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

// Handle categories form submission
async function handleAddCategories(e) {
    e.preventDefault();
    
    if (!apiConnected) {
        showFlash('Cannot add categories - API not connected', 'error');
        return;
    }
    
    // Get selected categories
    const checkboxes = document.querySelectorAll('#categories-form input[type="checkbox"]:checked');
    
    if (checkboxes.length === 0) {
        showFlash('Please select at least one category', 'error');
        return;
    }
    
    const selectedCategories = Array.from(checkboxes).map(cb => cb.value);
    
    const addButton = document.getElementById('add-categories-btn');
    addButton.disabled = true;
    addButton.innerHTML = 'Adding Categories...';
    
    // Show progress bar
    showProgressBar('Adding Book Categories');
    updateProgress(10, 'Preparing book lists...');
    
    try {
        // Define books for each category
        const categoryBooks = {
            fiction: [
                { name: 'Fiction - The Requiem Red', url: 'http://books.toscrape.com/catalogue/the-requiem-red_995/index.html' },
                { name: 'Fiction - The Dirty Little Secrets', url: 'http://books.toscrape.com/catalogue/the-dirty-little-secrets-of-getting-your-dream-job_994/index.html' },
                { name: 'Fiction - The Coming Woman', url: 'http://books.toscrape.com/catalogue/the-coming-woman-a-novel-based-on-the-life-of-the-infamous-feminist-victoria-woodhull_993/index.html' },
                { name: 'Fiction - The Black Maria', url: 'http://books.toscrape.com/catalogue/the-black-maria_991/index.html' }
            ],
            mystery: [
                { name: 'Mystery - Sharp Objects', url: 'http://books.toscrape.com/catalogue/sharp-objects_997/index.html' },
                { name: 'Mystery - In a Dark Place', url: 'http://books.toscrape.com/catalogue/in-a-dark-dark-wood_963/index.html' },
                { name: 'Mystery - The Murder of Roger Ackroyd', url: 'http://books.toscrape.com/catalogue/the-murder-of-roger-ackroyd-poirot-hercule-poirot-series_618/index.html' }
            ],
            romance: [
                { name: 'Romance - Tipping the Velvet', url: 'http://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html' },
                { name: 'Romance - Romeo and Juliet', url: 'http://books.toscrape.com/catalogue/romeo-and-juliet_450/index.html' },
                { name: 'Romance - Pride and Prejudice', url: 'http://books.toscrape.com/catalogue/pride-and-prejudice_242/index.html' }
            ],
            science: [
                { name: 'Science - The Origin of Species', url: 'http://books.toscrape.com/catalogue/the-origin-of-species_541/index.html' },
                { name: 'Science - The Gene: An Intimate History', url: 'http://books.toscrape.com/catalogue/the-gene-an-intimate-history_297/index.html' },
                { name: 'Science - Cosmos', url: 'http://books.toscrape.com/catalogue/cosmos_239/index.html' }
            ],
            history: [
                { name: 'History - Sapiens', url: 'http://books.toscrape.com/catalogue/sapiens-a-brief-history-of-humankind_996/index.html' },
                { name: 'History - The Guns of August', url: 'http://books.toscrape.com/catalogue/the-guns-of-august_459/index.html' },
                { name: 'History - A Short History of Nearly Everything', url: 'http://books.toscrape.com/catalogue/a-short-history-of-nearly-everything_841/index.html' }
            ],
            business: [
                { name: 'Business - The Intelligent Investor', url: 'http://books.toscrape.com/catalogue/the-intelligent-investor_576/index.html' },
                { name: 'Business - Good to Great', url: 'http://books.toscrape.com/catalogue/good-to-great-why-some-companies-make-the-leap-and-others-dont_642/index.html' },
                { name: 'Business - The Lean Startup', url: 'http://books.toscrape.com/catalogue/the-lean-startup-how-todays-entrepreneurs-use-continuous-innovation-to-create-radically-successful-businesses_340/index.html' }
            ]
        };
        
        let booksToAdd = [];
        selectedCategories.forEach(category => {
            if (categoryBooks[category]) {
                booksToAdd = booksToAdd.concat(categoryBooks[category]);
            }
        });
        
        updateProgress(30, `Adding ${booksToAdd.length} books...`);
        
        let addedCount = 0;
        let errors = [];
        
        // Add each book to monitoring
        for (let i = 0; i < booksToAdd.length; i++) {
            const book = booksToAdd[i];
            
            try {
                const response = await fetch(`${API_BASE}/api/scraper/add-site`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        name: book.name,
                        url: book.url,
                        price_selector: '.price_color'
                    })
                });
                
                const result = await response.json();
                if (result.success) {
                    addedCount++;
                } else {
                    errors.push(`${book.name}: ${result.error}`);
                }
                
                // Update progress
                const progress = 30 + ((i + 1) / booksToAdd.length) * 60;
                updateProgress(Math.round(progress), `Added ${addedCount}/${booksToAdd.length} books...`);
                
            } catch (error) {
                errors.push(`${book.name}: ${error.message}`);
            }
        }
        
        // Complete progress
        updateProgress(100, 'Completed!');
        
        setTimeout(() => {
            let resultHtml = '<div class="results" style="font-family: \'Montserrat\', sans-serif;"><h4>Book Categories Added</h4>';
            
            if (addedCount > 0) {
                resultHtml += `<p><strong>Successfully added ${addedCount} books from ${selectedCategories.length} categories!</strong></p>`;
                resultHtml += `<p>Categories added: ${selectedCategories.join(', ')}</p>`;
                
                if (errors.length > 0) {
                    resultHtml += `<p style="color: #dc3545;">Failed to add ${errors.length} books:</p>`;
                    resultHtml += '<ul>';
                    errors.forEach(error => {
                        resultHtml += `<li style="color: #dc3545;">${error}</li>`;
                    });
                    resultHtml += '</ul>';
                }
                
                showFlash(`Added ${addedCount} books from selected categories!`, 'success');
                
                // Hide form and refresh sites list
                toggleCategoriesForm();
                setTimeout(() => {
                    loadSites();
                }, 1000);
                
            } else {
                resultHtml += '<p style="color: #dc3545;">No books were added. All requests failed.</p>';
                showFlash('Failed to add book categories', 'error');
            }
            
            resultHtml += '</div>';
            document.getElementById('results').innerHTML = resultHtml;
        }, 500);
        
    } catch (error) {
        updateProgress(100, 'Error occurred');
        setTimeout(() => {
            showFlash(`Error adding categories: ${error.message}`, 'error');
        }, 500);
    } finally {
        addButton.disabled = false;
        addButton.innerHTML = 'Add Selected Categories';
    }
}

// Scrape all sites now with progress bar
async function scrapeNow() {
    if (!apiConnected) {
        showFlash('Cannot scrape - API not connected', 'error');
        return;
    }
    
    const scrapeButton = document.getElementById('scrape-btn');
    scrapeButton.disabled = true;
    scrapeButton.innerHTML = 'Scraping...';
    
    // Show progress bar
    showProgressBar('Scraping All Sites');
    
    // Simulate progress updates
    updateProgress(10, 'Connecting to sites...');
    
    setTimeout(() => updateProgress(30, 'Extracting price data...'), 1000);
    setTimeout(() => updateProgress(60, 'Processing results...'), 2000);
    setTimeout(() => updateProgress(90, 'Saving to database...'), 3000);
    
    try {
        const response = await fetch(`${API_BASE}/api/scraper/scrape-now`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        // Complete progress
        updateProgress(100, 'Completed!');
        
        setTimeout(() => {
            if (data.success) {
                let resultHtml = '<div class="results"><h4>Scraping Results:</h4>';
                
                if (data.results && data.results.length > 0) {
                    resultHtml += '<ul>';
                    data.results.forEach(result => {
                        const status = result.status === 'success' ? 'Success' : 'Failed';
                        const price = result.price ? `$${result.price}` : 'Failed to get price';
                        resultHtml += `<li><strong>${result.name}</strong>: ${status} - ${price}</li>`;
                    });
                    resultHtml += '</ul>';
                } else {
                    resultHtml += '<p>No sites to scrape. Add some sites first!</p>';
                }
                
                resultHtml += `<small>Scraped at: ${data.timestamp}</small></div>`;
                document.getElementById('results').innerHTML = resultHtml;
                
                showFlash('Scraping completed!', 'success');
            } else {
                document.getElementById('results').innerHTML = `<div class="flash flash-error">Scraping failed: ${data.error}</div>`;
            }
        }, 500);
        
    } catch (error) {
        updateProgress(100, 'Error occurred');
        setTimeout(() => {
            document.getElementById('results').innerHTML = `<div class="flash flash-error">Scraping error: ${error.message}</div>`;
        }, 500);
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

// NEW ANALYTICS FUNCTIONS WITH PROGRESS AND BACK BUTTONS

// Generate demo historical data with progress
async function generateDemoData() {
    if (!apiConnected) {
        showFlash('Cannot generate data - API not connected', 'error');
        return;
    }
    
    const demoButton = document.getElementById('demo-btn');
    if (!demoButton) return;
    
    demoButton.disabled = true;
    demoButton.innerHTML = 'Generating...';
    
    // Show progress bar
    showProgressBar('Generating Demo Data');
    
    // Simulate progress updates
    updateProgress(20, 'Initializing data generation...');
    setTimeout(() => updateProgress(40, 'Creating historical records...'), 800);
    setTimeout(() => updateProgress(70, 'Adding price variations...'), 1600);
    setTimeout(() => updateProgress(90, 'Saving to database...'), 2400);
    
    try {
        const response = await fetch(`${API_BASE}/api/simulate-data`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({days: 14}) // Generate 14 days of data
        });
        
        const result = await response.json();
        
        // Complete progress
        updateProgress(100, 'Completed!');
        
        setTimeout(() => {
            if (result.success) {
                showFlash(`Generated demo data: ${result.message}`, 'success');
                
                // Show what was generated
                document.getElementById('results').innerHTML = `
                    <div class="results">
                        <h4 style="font-family: 'Montserrat', sans-serif;">Demo Data Generated!</h4>
                        <p style="font-family: 'Montserrat', sans-serif;"><strong>${result.message}</strong></p>
                        <p style="font-family: 'Montserrat', sans-serif;">You now have historical price data for all monitored sites.</p>
                        <p style="font-family: 'Montserrat', sans-serif;">Click "View Analytics" to see charts and graphs!</p>
                        <div style="margin-top: 20px; text-align: center;">
                            <button onclick="viewAnalytics()" class="btn btn-primary" style="font-family: 'Montserrat', sans-serif;">
                                View Analytics
                            </button>
                        </div>
                    </div>
                `;
            } else {
                showFlash(`Error generating data: ${result.error}`, 'error');
            }
        }, 500);
        
    } catch (error) {
        updateProgress(100, 'Error occurred');
        setTimeout(() => {
            showFlash(`Error: ${error.message}`, 'error');
        }, 500);
    } finally {
        demoButton.disabled = false;
        demoButton.innerHTML = 'Generate Demo Data';
    }
}

// View analytics and charts
async function viewAnalytics() {
    if (!apiConnected) {
        showFlash('Cannot view analytics - API not connected', 'error');
        return;
    }
    
    showProgressBar('Loading Analytics');
    updateProgress(50, 'Fetching summary statistics...');
    
    try {
        // Get summary stats
        const summaryResponse = await fetch(`${API_BASE}/api/analytics/summary`);
        const summaryData = await summaryResponse.json();
        
        updateProgress(100, 'Complete!');
        
        setTimeout(() => {
            if (summaryData.success) {
                const summary = summaryData.summary;
                
                document.getElementById('results').innerHTML = `
                    <div class="results">
                        <h4 style="font-family: 'Montserrat', sans-serif;">Analytics Summary</h4>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0;">
                            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                                <h5 style="margin: 0; color: #495057; font-family: 'Montserrat', sans-serif;">Total Sites</h5>
                                <p style="font-size: 24px; font-weight: bold; margin: 5px 0; color: #007bff; font-family: 'Montserrat', sans-serif;">${summary.total_sites}</p>
                            </div>
                            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                                <h5 style="margin: 0; color: #495057; font-family: 'Montserrat', sans-serif;">Data Points</h5>
                                <p style="font-size: 24px; font-weight: bold; margin: 5px 0; color: #28a745; font-family: 'Montserrat', sans-serif;">${summary.total_data_points}</p>
                            </div>
                            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                                <h5 style="margin: 0; color: #495057; font-family: 'Montserrat', sans-serif;">Avg Price</h5>
                                <p style="font-size: 24px; font-weight: bold; margin: 5px 0; color: #ffc107; font-family: 'Montserrat', sans-serif;">${summary.average_price}</p>
                            </div>
                            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                                <h5 style="margin: 0; color: #495057; font-family: 'Montserrat', sans-serif;">Price Range</h5>
                                <p style="font-size: 16px; font-weight: bold; margin: 5px 0; color: #dc3545; font-family: 'Montserrat', sans-serif;">${summary.price_range.min} - ${summary.price_range.max}</p>
                            </div>
                        </div>
                        
                        <div style="margin-top: 20px; text-align: center;">
                            <button onclick="showPriceComparison()" class="btn btn-info" style="margin: 5px; font-family: 'Montserrat', sans-serif;">
                                Price Comparison Chart
                            </button>
                            <button onclick="showPriceTrends()" class="btn btn-success" style="margin: 5px; font-family: 'Montserrat', sans-serif;">
                                Price Trends Chart
                            </button>
                        </div>
                    </div>
                `;
            }
        }, 500);
        
    } catch (error) {
        updateProgress(100, 'Error occurred');
        setTimeout(() => {
            showFlash(`Analytics error: ${error.message}`, 'error');
        }, 500);
    }
}

// Show price comparison chart with back button
async function showPriceComparison() {
    showProgressBar('Loading Price Comparison');
    updateProgress(50, 'Fetching price data...');
    
    try {
        const response = await fetch(`${API_BASE}/api/analytics/price-comparison`);
        const data = await response.json();
        
        updateProgress(100, 'Complete!');
        
        setTimeout(() => {
            if (data.success) {
                let chartHtml = '<div class="results"><h4 style="font-family: \'Montserrat\', sans-serif;">Price Comparison</h4>';
                
                // Simple bar chart representation
                const maxPrice = Math.max(...data.raw_data.map(item => item.avg_price));
                
                chartHtml += '<div style="margin: 20px 0;">';
                data.raw_data.forEach(item => {
                    const barWidth = (item.avg_price / maxPrice) * 100;
                    chartHtml += `
                        <div style="margin: 10px 0;">
                            <div style="display: flex; align-items: center;">
                                <div style="width: 200px; font-size: 12px; padding-right: 10px; font-family: 'Montserrat', sans-serif;">${item.name}</div>
                                <div style="background: #007bff; height: 30px; width: ${barWidth}%; border-radius: 4px; display: flex; align-items: center; padding-left: 10px; color: white; font-weight: bold; font-family: 'Montserrat', sans-serif;">
                                    ${item.avg_price.toFixed(2)}
                                </div>
                            </div>
                        </div>
                    `;
                });
                chartHtml += '</div></div>';
                
                document.getElementById('results').innerHTML = chartHtml;
                addBackButton();
            }
        }, 500);
        
    } catch (error) {
        updateProgress(100, 'Error occurred');
        setTimeout(() => {
            showFlash(`Chart error: ${error.message}`, 'error');
        }, 500);
    }
}

// Show price trends with back button
async function showPriceTrends() {
    showProgressBar('Loading Price Trends');
    updateProgress(50, 'Fetching trend data...');
    
    try {
        const response = await fetch(`${API_BASE}/api/analytics/price-trends`);
        const data = await response.json();
        
        updateProgress(100, 'Complete!');
        
        setTimeout(() => {
            if (data.success) {
                let trendHtml = '<div class="results"><h4 style="font-family: \'Montserrat\', sans-serif;">Recent Price Trends</h4>';
                
                trendHtml += '<div style="max-height: 400px; overflow-y: auto;">';
                trendHtml += '<table class="sites-table" style="font-family: \'Montserrat\', sans-serif;"><thead><tr><th>Product</th><th>Price</th><th>Date</th></tr></thead><tbody>';
                
                data.raw_data.slice(0, 20).forEach(item => {
                    const date = new Date(item.date).toLocaleDateString();
                    trendHtml += `
                        <tr>
                            <td>${item.name}</td>
                            <td><strong>$${item.price.toFixed(2)}</strong></td>
                            <td>${date}</td>
                        </tr>
                    `;
                });
                
                trendHtml += '</tbody></table></div></div>';
                
                document.getElementById('results').innerHTML = trendHtml;
                addBackButton();
            }
        }, 500);
        
    } catch (error) {
        updateProgress(100, 'Error occurred');
        setTimeout(() => {
            showFlash(`Trends error: ${error.message}`, 'error');
        }, 500);
    }
}