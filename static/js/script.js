// Medical Shop App JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize app
    initializeApp();
});

function initializeApp() {
    // Set active navigation item
    setActiveNavigation();
    
    // Initialize form validation
    initializeFormValidation();
    
    // Initialize mobile optimizations
    initializeMobileOptimizations();
    
    // Initialize tooltips and popovers
    initializeTooltips();
    
    // Initialize auto-hide alerts
    initializeAlerts();
    

}

// Navigation Management
function setActiveNavigation() {
    const currentPath = window.location.pathname;
    const navItems = document.querySelectorAll('.mobile-bottom-nav .nav-item, .desktop-nav .nav-link');
    
    navItems.forEach(item => {
        const href = item.getAttribute('href');
        if (href && currentPath.includes(href) && href !== '/') {
            item.classList.add('active');
        }
    });
}

// Form Validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        // Real-time validation
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    validateField(this);
                }
            });
        });
        
        // Form submission validation
        form.addEventListener('submit', function(e) {
            let isValid = true;
            
            inputs.forEach(input => {
                if (!validateField(input)) {
                    isValid = false;
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showAlert('Please correct the errors in the form', 'error');
                
                // Focus on first invalid field
                const firstInvalid = form.querySelector('.is-invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                }
            } else {
                // Show loading state
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    showLoading(submitBtn);
                }
            }
        });
    });
}

function validateField(field) {
    const value = field.value.trim();
    const type = field.type;
    const name = field.name;
    let isValid = true;
    let errorMessage = '';
    
    // Remove existing validation classes
    field.classList.remove('is-valid', 'is-invalid');
    
    // Required field validation
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'This field is required';
    }
    
    // Only continue validation if there is actually a value
    if (value) {
        // Specific field validations
        switch (name) {
            case 'mobile_no':
                if (value.length !== 10 || !/^\d{10}$/.test(value)) {
                    isValid = false;
                    errorMessage = 'Please enter a valid 10-digit mobile number';
                }
                break;
                
            case 'pincode':
                if (value.length !== 6 || !/^\d{6}$/.test(value)) {
                    isValid = false;
                    errorMessage = 'Please enter a valid 6-digit pincode';
                }
                break;
                
            case 'password':
                if (value.length < 6) {
                    isValid = false;
                    errorMessage = 'Password must be at least 6 characters long';
                }
                break;
                
            case 'confirm_password':
                const password = document.getElementById('password');
                if (password && value !== password.value) {
                    isValid = false;
                    errorMessage = 'Passwords do not match';
                }
                break;
                
            case 'map_link':
                if (value && !isValidURL(value)) {
                    isValid = false;
                    errorMessage = 'Please enter a valid URL';
                }
                break;
        }
        
        // Email validation
        if (type === 'email' && !isValidEmail(value)) {
            isValid = false;
            errorMessage = 'Please enter a valid email address';
        }
        
        // URL validation
        if (type === 'url' && !isValidURL(value)) {
            isValid = false;
            errorMessage = 'Please enter a valid URL';
        }
    }
    
    // Apply validation classes and messages - only add is-valid class if there is a value
    if (isValid && value) {
        field.classList.add('is-valid');
    } else if (!isValid) {
        field.classList.add('is-invalid');
        updateValidationMessage(field, errorMessage);
    }
    
    return isValid;
}

function updateValidationMessage(field, message) {
    let feedback = field.parentNode.querySelector('.invalid-feedback');
    if (!feedback) {
        feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        field.parentNode.appendChild(feedback);
    }
    feedback.textContent = message;
}

// Mobile Optimizations
function initializeMobileOptimizations() {
    // Viewport height fix for mobile browsers
    function setViewportHeight() {
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
    }
    
    setViewportHeight();
    window.addEventListener('resize', setViewportHeight);
    
    // Touch-friendly interactions
    if (isMobileDevice()) {
        document.body.classList.add('touch-device');
        
        // Improve touch targets
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(btn => {
            btn.style.minHeight = '44px';
            btn.style.minWidth = '44px';
        });
        
        // Add haptic feedback for buttons (if supported)
        buttons.forEach(btn => {
            btn.addEventListener('click', function() {
                if (navigator.vibrate) {
                    navigator.vibrate(10);
                }
            });
        });
    }
    
    // Handle orientation changes
    window.addEventListener('orientationchange', function() {
        setTimeout(setViewportHeight, 100);
    });
}

// Utility Functions
function isMobileDevice() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function isValidURL(url) {
    try {
        new URL(url);
        return true;
    } catch {
        return false;
    }
}

// Loading States
function showLoading(element) {
    element.classList.add('loading');
    element.disabled = true;
    
    const originalText = element.textContent;
    element.setAttribute('data-original-text', originalText);
    
    // Auto-hide loading after 10 seconds
    setTimeout(() => {
        hideLoading(element);
    }, 10000);
}

function hideLoading(element) {
    element.classList.remove('loading');
    element.disabled = false;
    
    const originalText = element.getAttribute('data-original-text');
    if (originalText) {
        element.textContent = originalText;
        element.removeAttribute('data-original-text');
    }
}

// Alert Management
function initializeAlerts() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.parentNode) {
                alert.style.opacity = '0';
                setTimeout(() => {
                    if (alert.parentNode) {
                        alert.remove();
                    }
                }, 300);
            }
        }, 5000);
    });
}

function showAlert(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.className = 'container mt-3';
    
    const alertClass = type === 'error' ? 'danger' : type;
    alertContainer.innerHTML = `
        <div class="alert alert-${alertClass} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Insert at the top of main content
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.insertBefore(alertContainer, mainContent.firstChild);
    }
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        const alert = alertContainer.querySelector('.alert');
        if (alert) {
            alert.style.opacity = '0';
            setTimeout(() => {
                if (alertContainer.parentNode) {
                    alertContainer.remove();
                }
            }, 300);
        }
    }, 5000);
}

// Tooltip and Popover Initialization
function initializeTooltips() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Local Storage Management
function saveToLocalStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (e) {
        console.warn('Could not save to localStorage:', e);
    }
}

function getFromLocalStorage(key) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : null;
    } catch (e) {
        console.warn('Could not get from localStorage:', e);
        return null;
    }
}

// Form Auto-save (for longer forms)
function initializeAutoSave(formId, interval = 30000) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const saveKey = `autosave_${formId}`;
    
    // Load saved data
    const savedData = getFromLocalStorage(saveKey);
    if (savedData) {
        Object.keys(savedData).forEach(name => {
            const field = form.querySelector(`[name="${name}"]`);
            if (field && field.type !== 'password') {
                field.value = savedData[name];
            }
        });
    }
    
    // Auto-save interval
    setInterval(() => {
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            if (key !== 'password' && key !== 'confirm_password') {
                data[key] = value;
            }
        }
        
        saveToLocalStorage(saveKey, data);
    }, interval);
    
    // Clear auto-save on successful submission
    form.addEventListener('submit', function() {
        localStorage.removeItem(saveKey);
    });
}

// Network Status Management
function initializeNetworkStatus() {
    function updateNetworkStatus() {
        if (!navigator.onLine) {
            showAlert('You are currently offline. Some features may not work properly.', 'warning');
        }
    }
    
    window.addEventListener('online', function() {
        showAlert('You are back online!', 'success');
    });
    
    window.addEventListener('offline', updateNetworkStatus);
    
    // Check initial status
    updateNetworkStatus();
}

// Initialize network status monitoring
initializeNetworkStatus();

// Keyboard Navigation Enhancement
document.addEventListener('keydown', function(e) {
    // Escape key to close modals
    if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal) {
            const modal = bootstrap.Modal.getInstance(openModal);
            if (modal) {
                modal.hide();
            }
        }
    }
    
    // Enter key to submit forms (when focus is on submit button)
    if (e.key === 'Enter' && e.target.type === 'submit') {
        e.target.click();
    }
});

// Performance Monitoring
function measurePerformance() {
    if ('performance' in window) {
        window.addEventListener('load', function() {
            setTimeout(function() {
                const perfData = performance.getEntriesByType('navigation')[0];
                const loadTime = perfData.loadEventEnd - perfData.loadEventStart;
                
                if (loadTime > 3000) {
                    console.warn('Page load time is slow:', loadTime + 'ms');
                }
            }, 0);
        });
    }
}



measurePerformance();