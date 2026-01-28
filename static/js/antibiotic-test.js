// Test script for antibiotics API
// This can be included in the HTML or run from the browser console

function testAntibiotic(disease) {
    console.log(`Testing API with disease: ${disease}`);
    
    fetch('/api/medicine/antibiotics', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ disease: disease })
    })
    .then(response => response.json())
    .then(data => {
        console.log(`Results for ${disease}:`, data);
        if (data.success && data.antibiotics) {
            console.log(`Found ${data.antibiotics.length} antibiotics: ${data.antibiotics.join(', ')}`);
        } else {
            console.error('API call failed:', data.error || 'Unknown error');
        }
    })
    .catch(error => {
        console.error('Fetch error:', error);
    });
}

// Test with common diseases
function runTests() {
    const diseases = [
        'Mastitis',
        'Pneumonia',
        'Coccidiosis',
        'Newcastle Disease',
        'Avian Influenza'
    ];
    
    diseases.forEach(disease => {
        testAntibiotic(disease);
    });
}

// Make functions available globally
window.testAntibiotic = testAntibiotic;
window.runTests = runTests;