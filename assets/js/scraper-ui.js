// Show flash messages
function showFlash(message, type = 'success') {
    const flashContainer = document.getElementById('flash-messages');
    const flashDiv = document.createElement('div');
    flashDiv.className = `flash flash-${type}`;
    flashDiv.innerHTML = message;
    flashContainer.appendChild(flashDiv);
    
    setTimeout(() => flashDiv.remove(), 5000);
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

// Add back button
function addBackButton() {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML += `
        <div style="margin-top: 20px; text-align: center;">
            <button onclick="goBackToAnalytics()" class="btn btn-secondary" style="background: #6c757d; color: white; font-family: 'Montserrat', sans-serif;">
                Back to Analytics
            </button>
        </div>
    `;
}

function goBackToAnalytics() {
    viewAnalytics();
}

// Toggle forms
function toggleAddSiteForm() {
    const formContainer = document.getElementById('add-site-form-container');
    const toggleButton = document.getElementById('add-site-toggle-btn');
    
    if (formContainer.style.display === 'none' || formContainer.style.display === '') {
        const categoriesContainer = document.getElementById('categories-form-container');
        if (categoriesContainer.style.display === 'block') {
            toggleCategoriesForm();
        }
        
        formContainer.style.display = 'block';
        toggleButton.innerHTML = 'Cancel Add Site';
        document.getElementById('add-site-form').reset();
    } else {
        formContainer.style.display = 'none';
        toggleButton.innerHTML = 'Add New Site';
    }
}

function toggleCategoriesForm() {
    const formContainer = document.getElementById('categories-form-container');
    const toggleButton = document.getElementById('scrape-categories-btn');
    
    if (formContainer.style.display === 'none' || formContainer.style.display === '') {
        const addSiteContainer = document.getElementById('add-site-form-container');
        if (addSiteContainer.style.display === 'block') {
            toggleAddSiteForm();
        }
        
        formContainer.style.display = 'block';
        toggleButton.innerHTML = 'Cancel Categories';
        const checkboxes = document.querySelectorAll('#categories-form input[type="checkbox"]');
        checkboxes.forEach(cb => cb.checked = false);
    } else {
        formContainer.style.display = 'none';
        toggleButton.innerHTML = 'Scrape Book Categories';
    }
}