// CSV Analysis
async function analyzeCsv() {
    const fileInput = document.getElementById('csvFile');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Please select a CSV file');
        return;
    }
    
    showLoading(true);
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_BASE}/api/upload-csv`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            document.getElementById('analysis-card').style.display = 'block';
            displayResults(result.analysis, 'analysis-results');
        } else {
            displayError(result.error, 'analysis-results');
        }
    } catch (error) {
        displayError(error.message, 'analysis-results');
    } finally {
        showLoading(false);
    }
}

// Generate PDF Report
async function generateReport() {
    const fileInput = document.getElementById('csvFile');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Please select a CSV file');
        return;
    }
    
    showLoading(true);
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_BASE}/api/generate-report`, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `report_${new Date().toISOString().slice(0,10)}.pdf`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            alert('✅ PDF report downloaded successfully!');
        } else {
            const error = await response.json();
            displayError(error.error, 'analysis-results');
        }
    } catch (error) {
        displayError(error.message, 'analysis-results');
    } finally {
        showLoading(false);
    }
}

// Generate Chart
async function generateChart() {
    const chartType = document.getElementById('chartType').value;
    const title = document.getElementById('chartTitle').value || 'Generated Chart';
    
    // Sample data - in real app, this would come from uploaded CSV
    const chartData = {
        data: [
            {value: 10}, {value: 25}, {value: 15}, {value: 30}, 
            {value: 20}, {value: 35}, {value: 18}, {value: 28}
        ],
        type: chartType,
        title: title
    };
    
    try {
        const response = await fetch(`${API_BASE}/api/generate-chart`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(chartData)
        });
        
        const result = await response.json();
        if (result.success) {
            document.getElementById('chart-container').innerHTML = 
                `<img src="${result.chart}" class="img-fluid" alt="Generated Chart">`;
        } else {
            displayError(result.error, 'chart-container');
        }
    } catch (error) {
        displayError(error.message, 'chart-container');
    }
}