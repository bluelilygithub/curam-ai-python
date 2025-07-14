// Railway API endpoint - UPDATE THIS WITH YOUR ACTUAL RAILWAY URL
const API_BASE = 'curam-ai-agent-mcp-production.up.railway.app';

// Common utility functions
function showLoading(show = true) {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.style.display = show ? 'block' : 'none';
    }
}

function displayResults(data, elementId) {
    const element = document.getElementById(elementId);
    element.innerHTML = `<pre class="bg-light p-3 rounded">${JSON.stringify(data, null, 2)}</pre>`;
}

function displayError(error, elementId) {
    const element = document.getElementById(elementId);
    element.innerHTML = `<div class="alert alert-danger">❌ Error: ${error}</div>`;
}

// API Health Check
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const health = await response.json();
        
        const statusElement = document.getElementById('api-status');
        const statusText = document.getElementById('status-text');
        
        if (statusElement && statusText) {
            statusElement.className = 'alert alert-success';
            statusText.innerHTML = `API Connected - Status: ${health.status}`;
        }
        
        console.log('API Health:', health);
        return true;
    } catch (error) {
        const statusElement = document.getElementById('api-status');
        const statusText = document.getElementById('status-text');
        
        if (statusElement && statusText) {
            statusElement.className = 'alert alert-danger';
            statusText.innerHTML = `❌ API Connection Failed: ${error.message}`;
        }
        
        console.error('API Health Check Failed:', error);
        return false;
    }
}

// Test API functionality
async function testAPI() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        displayResults(data, 'test-results');
    } catch (error) {
        displayError(error.message, 'test-results');
    }
}

// Generate sample chart
async function testChart() {
    const sampleData = {
        data: [
            {x: 1, y: 2}, {x: 2, y: 4}, {x: 3, y: 1}, 
            {x: 4, y: 5}, {x: 5, y: 3}
        ],
        type: 'line',
        title: 'Sample Chart Test'
    };
    
    try {
        const response = await fetch(`${API_BASE}/api/generate-chart`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(sampleData)
        });
        
        const result = await response.json();
        if (result.success) {
            document.getElementById('test-results').innerHTML = 
                `<img src="${result.chart}" class="img-fluid" alt="Sample Chart">`;
        } else {
            displayError(result.error, 'test-results');
        }
    } catch (error) {
        displayError(error.message, 'test-results');
    }
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    checkAPIHealth();
});