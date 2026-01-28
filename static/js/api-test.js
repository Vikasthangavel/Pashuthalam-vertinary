// This JavaScript file will be used to test the API endpoints
// It's for diagnostic purposes to ensure the antibiotics API is working correctly

function testAntibioticsAPI() {
    // List of common diseases to test with
    const diseases = [
        "Mastitis",
        "Pneumonia", 
        "Foot Rot",
        "Calf Scours",
        "Bloat"
    ];

    // Test each disease
    diseases.forEach(disease => {
        console.log(`Testing antibiotics API with disease: ${disease}`);
        
        fetch('/api/medicine/antibiotics', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ disease: disease })
        })
        .then(response => {
            console.log(`Response status for ${disease}: ${response.status}`);
            return response.json();
        })
        .then(data => {
            console.log(`Data received for ${disease}:`, data);
            
            if (data.success && Array.isArray(data.antibiotics)) {
                console.log(`✅ Success: Found ${data.antibiotics.length} antibiotics for ${disease}`);
            } else {
                console.error(`❌ Error: No antibiotics found for ${disease}`, data);
            }
        })
        .catch(error => {
            console.error(`❌ API error for ${disease}:`, error);
        });
    });
}

// Export for use in the browser console
window.testAntibioticsAPI = testAntibioticsAPI;