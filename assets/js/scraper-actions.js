// Handle categories form
async function handleAddCategories(e) {
    e.preventDefault();
    
    if (!apiConnected) {
        showFlash('Cannot add categories - API not connected', 'error');
        return;
    }
    
    const checkboxes = document.querySelectorAll('#categories-form input[type="checkbox"]:checked');
    if (checkboxes.length === 0) {
        showFlash('Please select at least one category', 'error');
        return;
    }
    
    const selectedCategories = Array.from(checkboxes).map(cb => cb.value);
    const addButton = document.getElementById('add-categories-btn');
    addButton.disabled = true;
    addButton.innerHTML = 'Adding Categories...';
    
    showProgressBar('Adding Book Categories');
    updateProgress(10, 'Preparing book lists...');
    
    try {
        const categoryBooks = {
            fiction: [
                { name: 'Fiction - The Requiem Red', url: 'http://books.toscrape.com/catalogue/the-requiem-red_995/index.html' },
                { name: 'Fiction - The Coming Woman', url: 'http://books.toscrape.com/catalogue/the-coming-woman-a-novel-based-on-the-life-of-the-infamous-feminist-victoria-woodhull_993/index.html' }
            ],
            mystery: [
                { name: 'Mystery - Sharp Objects', url: 'http://books.toscrape.com/catalogue/sharp-objects_997/index.html' },
                { name: 'Mystery - In a Dark Place', url: 'http://books.toscrape.com/catalogue/in-a-dark-dark-wood_963/index.html' }
            ],
            romance: [
                { name: 'Romance - Tipping the Velvet', url: 'http://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html' },
                { name: 'Romance - Pride and Prejudice', url: 'http://books.toscrape.com/catalogue/pride-and-prejudice_242/index.html' }
            ],
            science: [
                { name: 'Science - The Origin of Species', url: 'http://books.toscrape.com/catalogue/the-origin-of-species_541/index.html' },
                { name: 'Science - Cosmos', url: 'http://books.toscrape.com/catalogue/cosmos_239/index.html' }
            ],
            history: [
                { name: 'History - Sapiens', url: 'http://books.toscrape.com/catalogue/sapiens-a-brief-history-of-humankind_996/index.html' }
            ],
            business: [
                { name: 'Business - The Intelligent Investor', url: 'http://books.toscrape.com/catalogue/the-intelligent-investor_576/index.html' }
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
                
                if ((await response.json()).success) addedCount++;
                
                const progress = 30 + ((i + 1) / booksToAdd.length) * 60;
                updateProgress(Math.round(progress), `Added ${addedCount}/${booksToAdd.length} books...`);
            } catch (error) {
                console.error(`Error adding ${book.name}:`, error);
            }
        }
        
        updateProgress(100, 'Completed!');
        
        setTimeout(() => {
            showFlash(`Added ${addedCount} books from selected categories!`, 'success');
            toggleCategoriesForm();
            setTimeout(() => loadSites(), 1000);
        }, 500);
        
    } catch (error) {
        showFlash(`Error adding categories: ${error.message}`, 'error');
    } finally {
        addButton.disabled = false;
        addButton.innerHTML = 'Add Selected Categories';
    }
}

// Scrape all sites
async function scrapeNow() {
    if (!apiConnected) {
        showFlash('Cannot scrape - API not connected', 'error');
        return;
    }
    
    const scrapeButton = document.getElementById('scrape-btn');
    scrapeButton.disabled = true;
    scrapeButton.innerHTML = 'Scraping...';
    
    showProgressBar('Scraping All Sites');
    updateProgress(10, 'Connecting to sites...');
    
    setTimeout(() => updateProgress(50, 'Extracting price data...'), 1000);
    setTimeout(() => updateProgress(90, 'Saving to database...'), 2000);
    
    try {
        const response = await fetch(`${API_BASE}/api/scraper/scrape-now`, {
            method: 'POST'
        });
        
        const data = await response.json();
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
            }
        }, 500);
        
    } catch (error) {
        showFlash(`Scraping error: ${error.message}`, 'error');
    } finally {
        scrapeButton.disabled = false;
        scrapeButton.innerHTML = 'Scrape All Sites Now';
    }
}

// Generate demo data
async function generateDemoData() {
    if (!apiConnected) {
        showFlash('Cannot generate data - API not connected', 'error');
        return;
    }
    
    const demoButton = document.getElementById('demo-btn');
    demoButton.disabled = true;
    demoButton.innerHTML = 'Generating...';
    
    showProgressBar('Generating Demo Data');
    updateProgress(50, 'Creating historical records...');
    
    try {
        const response = await fetch(`${API_BASE}/api/simulate-data`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({days: 14})
        });
        
        const result = await response.json();
        updateProgress(100, 'Completed!');
        
        setTimeout(() => {
            if (result.success) {
                showFlash(`Generated demo data: ${result.message}`, 'success');
                document.getElementById('results').innerHTML = `
                    <div class="results">
                        <h4>Demo Data Generated!</h4>
                        <p><strong>${result.message}</strong></p>
                        <p>Click "View Analytics" to see charts and graphs!</p>
                        <div style="margin-top: 20px; text-align: center;">
                            <button onclick="viewAnalytics()" class="btn btn-primary">View Analytics</button>
                        </div>
                    </div>
                `;
            }
        }, 500);
        
    } catch (error) {
        showFlash(`Error: ${error.message}`, 'error');
    } finally {
        demoButton.disabled = false;
        demoButton.innerHTML = 'Generate Demo Data';
    }
}

// View analytics
async function viewAnalytics() {
    if (!apiConnected) {
        showFlash('Cannot view analytics - API not connected', 'error');
        return;
    }
    
    showProgressBar('Loading Analytics');
    updateProgress(50, 'Fetching summary statistics...');
    
    try {
        const summaryResponse = await fetch(`${API_BASE}/api/analytics/summary`);
        const summaryData = await summaryResponse.json();
        updateProgress(100, 'Complete!');
        
        setTimeout(() => {
            if (summaryData.success) {
                const summary = summaryData.summary;
                document.getElementById('results').innerHTML = `
                    <div class="results">
                        <h4>Analytics Summary</h4>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0;">
                            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                                <h5 style="margin: 0; color: #495057;">Total Sites</h5>
                                <p style="font-size: 24px; font-weight: bold; color: #007bff;">${summary.total_sites}</p>
                            </div>
                            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                                <h5 style="margin: 0; color: #495057;">Data Points</h5>
                                <p style="font-size: 24px; font-weight: bold; color: #28a745;">${summary.total_data_points}</p>
                            </div>
                            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                                <h5 style="margin: 0; color: #495057;">Avg Price</h5>
                                <p style="font-size: 24px; font-weight: bold; color: #ffc107;">$${summary.average_price}</p>
                            </div>
                        </div>
                        <div style="margin-top: 20px; text-align: center;">
                            <button onclick="showPriceComparison()" class="btn btn-info" style="margin: 5px;">Price Comparison</button>
                            <button onclick="showPriceTrends()" class="btn btn-success" style="margin: 5px;">Price Trends</button>
                        </div>
                    </div>
                `;
            }
        }, 500);
    } catch (error) {
        showFlash(`Analytics error: ${error.message}`, 'error');
    }
}

// Show price comparison chart
async function showPriceComparison() {
    showProgressBar('Loading Price Comparison');
    updateProgress(50, 'Fetching price data...');
    
    try {
        const response = await fetch(`${API_BASE}/api/analytics/price-comparison`);
        const data = await response.json();
        updateProgress(100, 'Complete!');
        
        setTimeout(() => {
            if (data.success) {
                let chartHtml = '<div class="results"><h4>Price Comparison</h4>';
                const maxPrice = Math.max(...data.raw_data.map(item => item.avg_price));
                
                chartHtml += '<div style="margin: 20px 0;">';
                data.raw_data.forEach(item => {
                    const barWidth = (item.avg_price / maxPrice) * 100;
                    chartHtml += `
                        <div style="margin: 10px 0;">
                            <div style="display: flex; align-items: center;">
                                <div style="width: 200px; font-size: 12px; padding-right: 10px;">${item.name}</div>
                                <div style="background: #007bff; height: 30px; width: ${barWidth}%; border-radius: 4px; display: flex; align-items: center; padding-left: 10px; color: white; font-weight: bold;">
                                    $${item.avg_price.toFixed(2)}
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
        showFlash(`Chart error: ${error.message}`, 'error');
    }
}

// Show price trends
async function showPriceTrends() {
    showProgressBar('Loading Price Trends');
    updateProgress(50, 'Fetching trend data...');
    
    try {
        const response = await fetch(`${API_BASE}/api/analytics/price-trends`);
        const data = await response.json();
        updateProgress(100, 'Complete!');
        
        setTimeout(() => {
            if (data.success) {
                let trendHtml = '<div class="results"><h4>Recent Price Trends</h4>';
                trendHtml += '<table class="sites-table"><thead><tr><th>Product</th><th>Price</th><th>Date</th></tr></thead><tbody>';
                
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
                
                trendHtml += '</tbody></table></div>';
                document.getElementById('results').innerHTML = trendHtml;
                addBackButton();
            }
        }, 500);
    } catch (error) {
        showFlash(`Trends error: ${error.message}`, 'error');
    }
}