// API Configuration
const API_BASE = 'https://curam-ai-python-production.up.railway.app';

// Global state
let apiConnected = false;
let sites = [];

// Initialize page
document.addEventListener('DOMContentLoaded', async function() {
    await checkAPIConnection();
    loadSites();
    
    // Setup form submissions
    document.getElementById('add-site-form').addEventListener('submit', handleAddSite);
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

// Enable/disable buttons
function enableButtons() {
    const buttons = ['scrape-btn', 'refresh-btn', 'add-site-toggle-btn', 'scrape-categories-btn', 'add-site-btn', 'add-categories-btn', 'demo-btn', 'analytics-btn'];
    buttons.forEach(id => {
        const btn = document.getElementById(id);
        if (btn) btn.disabled = false;
    });
}

function disableButtons() {
    const buttons = ['scrape-btn', 'refresh-btn', 'add-site-toggle-btn', 'scrape-categories-btn', 'add-site-btn', 'add-categories-btn', 'demo-btn', 'analytics-btn'];
    buttons.forEach(id => {
        const btn = document.getElementById(id);
        if (btn) btn.disabled = true;
    });
}