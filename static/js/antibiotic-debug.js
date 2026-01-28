// Anti-debug helper for the antibiotics dropdown
document.addEventListener('DOMContentLoaded', function() {
    // Attach console logger to antibiotics API responses
    const originalFetch = window.fetch;
    window.fetch = function() {
        const url = arguments[0];
        
        // Only intercept antibiotics API calls
        if (typeof url === 'string' && url.includes('/api/medicine/antibiotics')) {
            console.log('🔍 Intercepted antibiotics API call:', arguments);
            
            return originalFetch.apply(this, arguments)
                .then(response => {
                    console.log('📡 API Response status:', response.status);
                    
                    // Clone the response so we can read the body and still return a usable response
                    const clonedResponse = response.clone();
                    
                    clonedResponse.json().then(data => {
                        console.log('📊 API Response data:', data);
                        
                        if (data.success && data.antibiotics) {
                            console.log('✅ Found antibiotics:', data.antibiotics);
                            
                            // Check if select exists and update debug info
                            setTimeout(() => {
                                const antibioticSelect = document.getElementById('antibiotic');
                                if (antibioticSelect) {
                                    console.log('📋 Antibiotic dropdown options:', antibioticSelect.options.length);
                                    console.log('📋 Antibiotic dropdown HTML:', antibioticSelect.innerHTML);
                                }
                            }, 100);
                        } else {
                            console.warn('⚠️ No antibiotics in response');
                        }
                    }).catch(e => console.error('Error parsing API response:', e));
                    
                    return response;
                })
                .catch(error => {
                    console.error('❌ API fetch error:', error);
                    throw error;
                });
        }
        
        return originalFetch.apply(this, arguments);
    };
    
    // Add debug info for form elements
    const debugFormElements = () => {
        const diseaseSelect = document.getElementById('disease');
        const antibioticSelect = document.getElementById('antibiotic');
        
        if (diseaseSelect) {
            console.log('🔍 Disease select exists:', diseaseSelect.value);
        } else {
            console.warn('⚠️ Disease select does not exist!');
        }
        
        if (antibioticSelect) {
            console.log('🔍 Antibiotic select exists, options:', antibioticSelect.options.length);
        } else {
            console.warn('⚠️ Antibiotic select does not exist!');
        }
    };
    
    // Run after a short delay to ensure page is loaded
    setTimeout(debugFormElements, 500);
});