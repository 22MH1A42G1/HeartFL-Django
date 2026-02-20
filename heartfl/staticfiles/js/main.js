/**
 * HeartFL - Main Interactive JavaScript
 * Handles form validation, animations, API calls, and user interactions
 */

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Show notification/alert
 */
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.innerHTML = `
        <span>${message}</span>
        <button class="btn-close" onclick="this.parentElement.remove()">&times;</button>
    `;
    
    const container = document.querySelector('main');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
    }
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

/**
 * Format number with commas
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Debounce function
 */
function debounce(func, delay) {
    let timeoutId;
    return function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func(...args), delay);
    };
}

/**
 * Throttle function
 */
function throttle(func, limit) {
    let inThrottle;
    return function (...args) {
        if (!inThrottle) {
            func(...args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// ============================================================================
// FORM VALIDATION
// ============================================================================

class FormValidator {
    constructor(formSelector) {
        this.form = document.querySelector(formSelector);
        if (this.form) {
            this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        }
    }

    /**
     * Check if this form should use AJAX submission
     */
    isAjaxForm() {
        if (!this.form) return false;
        const ajaxFlag = this.form.dataset.ajax;
        const submitMode = this.form.dataset.submit;
        return ajaxFlag === 'true' || ajaxFlag === '1' || submitMode === 'ajax' || this.form.hasAttribute('data-ajax');
    }

    /**
     * Validate email format
     */
    validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    /**
     * Validate phone number
     */
    validatePhone(phone) {
        const re = /^\+?[\d\s\-()]{10,}$/;
        return re.test(phone.replace(/\s/g, ''));
    }

    /**
     * Validate age
     */
    validateAge(age) {
        const num = parseInt(age);
        return num >= 0 && num <= 150;
    }

    /**
     * Show field error
     */
    showError(field, message) {
        field.classList.add('is-invalid');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'form-error';
        errorDiv.textContent = message;
        field.parentElement.appendChild(errorDiv);
    }

    /**
     * Clear field error
     */
    clearError(field) {
        field.classList.remove('is-invalid');
        const errorDiv = field.parentElement.querySelector('.form-error');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    /**
     * Handle form submission
     */
    async handleSubmit(e) {
        let isValid = true;

        // Get all form fields
        const fields = this.form.querySelectorAll('input[required], textarea[required], select[required]');

        fields.forEach(field => {
            this.clearError(field);

            if (!field.value.trim()) {
                this.showError(field, 'This field is required');
                isValid = false;
            } else if (field.type === 'email' && !this.validateEmail(field.value)) {
                this.showError(field, 'Please enter a valid email');
                isValid = false;
            } else if (field.name === 'phone' && field.value && !this.validatePhone(field.value)) {
                this.showError(field, 'Please enter a valid phone number');
                isValid = false;
            } else if (field.name === 'age' && !this.validateAge(field.value)) {
                this.showError(field, 'Age must be between 0 and 150');
                isValid = false;
            }
        });

        if (!isValid) {
            e.preventDefault();
            return;
        }

        if (this.isAjaxForm()) {
            e.preventDefault();
            await this.submitForm();
        }
    }

    /**
     * Submit form via AJAX
     */
    async submitForm() {
        const submitBtn = this.form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        
        submitBtn.disabled = true;
        submitBtn.classList.add('btn-loading');

        try {
            const formData = new FormData(this.form);
            const response = await fetch(this.form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (response.ok) {
                showNotification('✅ Form submitted successfully!', 'success');
                this.form.reset();
            } else {
                showNotification('❌ Error submitting form. Please try again.', 'error');
            }
        } catch (error) {
            showNotification(`❌ Error: ${error.message}`, 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.classList.remove('btn-loading');
            submitBtn.textContent = originalText;
        }
    }
}

// ============================================================================
// PREDICTION CALCULATOR
// ============================================================================

class PredictionCalculator {
    constructor() {
        this.model = null;
        this.initializeForm();
    }

    /**
     * Initialize prediction form
     */
    initializeForm() {
        const form = document.querySelector('[data-prediction-form]');
        if (form) {
            const fields = form.querySelectorAll('input[type="number"], select');
            fields.forEach(field => {
                field.addEventListener('change', () => this.calculateRisk());
                field.addEventListener('input', debounce(() => this.calculateRisk(), 300));
            });
        }
    }

    /**
     * Calculate risk score (client-side simulation)
     */
    calculateRisk() {
        const form = document.querySelector('[data-prediction-form]');
        if (!form) return;

        const age = parseFloat(form.querySelector('[name="age"]')?.value || 0);
        const cholesterol = parseFloat(form.querySelector('[name="cholesterol"]')?.value || 0);
        const blood_pressure = parseFloat(form.querySelector('[name="blood_pressure"]')?.value || 0);
        const heart_rate = parseFloat(form.querySelector('[name="heart_rate"]')?.value || 0);

        // Simple risk calculation (0-100)
        let riskScore = 0;

        // Age factor (0-30)
        if (age > 50) riskScore += (age - 50) * 0.6;
        
        // Cholesterol factor (0-25)
        if (cholesterol > 200) riskScore += (cholesterol - 200) * 0.1;
        
        // Blood pressure factor (0-25)
        if (blood_pressure > 130) riskScore += (blood_pressure - 130) * 0.2;
        
        // Heart rate factor (0-20)
        if (heart_rate > 100) riskScore += (heart_rate - 100) * 0.2;

        // Cap at 100
        riskScore = Math.min(riskScore, 100);

        // Display result
        this.displayRiskResult(riskScore);
    }

    /**
     * Display risk result
     */
    displayRiskResult(riskScore) {
        const resultDiv = document.querySelector('[data-prediction-result]');
        if (!resultDiv) return;

        const riskLevel = riskScore > 50 ? 'HIGH' : 'LOW';
        const badgeClass = riskScore > 50 ? 'badge-danger' : 'badge-success';
        const color = riskScore > 50 ? '#EF4444' : '#10B981';

        resultDiv.innerHTML = `
            <div class="mt-3">
                <h4>Risk Assessment</h4>
                <div class="d-flex align-items-center gap-2">
                    <div class="badge ${badgeClass}" style="padding: 1rem;">${riskLevel}</div>
                    <span class="text-lg">${riskScore.toFixed(1)}%</span>
                </div>
                <div class="progress mt-2" style="height: 10px; background: #e5e7eb; border-radius: 5px; overflow: hidden;">
                    <div style="width: ${riskScore}%; height: 100%; background: ${color}; transition: width 0.3s;"></div>
                </div>
            </div>
        `;
    }
}

// ============================================================================
// API HELPER
// ============================================================================

class APIHelper {
    /**
     * Fetch with error handling
     */
    static async fetch(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    /**
     * Get dashboard statistics
     */
    static async getOverview() {
        return await this.fetch('/api/overview/');
    }

    /**
     * Get recent predictions
     */
    static async getRecentPredictions() {
        return await this.fetch('/api/recent-predictions/');
    }

    /**
     * Submit contact form
     */
    static async submitContact(data) {
        return await this.fetch('/api/contact/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
}

// ============================================================================
// ANIMATIONS
// ============================================================================

class AnimationManager {
    /**
     * Animate elements on scroll
     */
    static initScrollAnimations() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.animation = 'fadeIn 0.6s ease forwards';
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('.stat-card, .card, .container').forEach(el => {
            observer.observe(el);
        });
    }

    /**
     * Add loading animation to button
     */
    static setButtonLoading(button, isLoading) {
        if (isLoading) {
            button.disabled = true;
            button.dataset.originalText = button.textContent;
            button.innerHTML = '<span class="spinner"></span> Loading...';
        } else {
            button.disabled = false;
            button.textContent = button.dataset.originalText || 'Submit';
        }
    }

    /**
     * Pulse animation for important elements
     */
    static addPulse(element) {
        element.style.animation = 'pulse 2s infinite';
    }

    /**
     * Remove pulse animation
     */
    static removePulse(element) {
        element.style.animation = 'none';
    }
}

// ============================================================================
// MODAL MANAGEMENT
// ============================================================================

class Modal {
    constructor(modalSelector) {
        this.modal = document.querySelector(modalSelector);
        this.setupEventListeners();
    }

    /**
     * Setup modal event listeners
     */
    setupEventListeners() {
        const closeBtn = this.modal?.querySelector('.modal-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.close());
        }

        // Close on outside click
        this.modal?.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.close();
            }
        });

        // Close on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.close();
            }
        });
    }

    /**
     * Open modal
     */
    open() {
        if (this.modal) {
            this.modal.classList.add('show');
            document.body.style.overflow = 'hidden';
        }
    }

    /**
     * Close modal
     */
    close() {
        if (this.modal) {
            this.modal.classList.remove('show');
            document.body.style.overflow = 'auto';
        }
    }

    /**
     * Toggle modal
     */
    toggle() {
        if (this.modal?.classList.contains('show')) {
            this.close();
        } else {
            this.open();
        }
    }
}

// ============================================================================
// TABLE ENHANCEMENTS
// ============================================================================

class TableManager {
    /**
     * Make table sortable
     */
    static makeSortable(tableSelector) {
        const table = document.querySelector(tableSelector);
        if (!table) return;

        const headers = table.querySelectorAll('thead th');
        headers.forEach((header, index) => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => {
                this.sortTable(table, index);
            });
        });
    }

    /**
     * Sort table by column
     */
    static sortTable(table, columnIndex) {
        const rows = Array.from(table.querySelectorAll('tbody tr'));
        const isAscending = table.dataset.sortOrder !== 'asc';

        rows.sort((a, b) => {
            const aValue = a.cells[columnIndex].textContent.trim();
            const bValue = b.cells[columnIndex].textContent.trim();

            if (!isNaN(aValue) && !isNaN(bValue)) {
                return isAscending ? aValue - bValue : bValue - aValue;
            }

            return isAscending 
                ? aValue.localeCompare(bValue) 
                : bValue.localeCompare(aValue);
        });

        rows.forEach(row => {
            table.querySelector('tbody').appendChild(row);
        });

        table.dataset.sortOrder = isAscending ? 'asc' : 'desc';
    }

    /**
     * Add search filter to table
     */
    static addSearchFilter(tableSelector, searchInputSelector) {
        const table = document.querySelector(tableSelector);
        const searchInput = document.querySelector(searchInputSelector);

        if (!searchInput) return;

        searchInput.addEventListener('keyup', () => {
            const filter = searchInput.value.toLowerCase();
            const rows = table.querySelectorAll('tbody tr');

            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filter) ? '' : 'none';
            });
        });
    }
}

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('HeartFL Interactive JavaScript Loaded');

    // Initialize form validators
    new FormValidator('form[method="POST"]');

    // Initialize prediction calculator
    new PredictionCalculator();

    // Initialize scroll animations
    AnimationManager.initScrollAnimations();

    // Initialize table enhancements
    TableManager.makeSortable('table');
    TableManager.addSearchFilter('table', '[data-search-table]');

    // Initialize modals
    document.querySelectorAll('.modal').forEach(modal => {
        new Modal(`.modal[id="${modal.id || 'modal'}"]`);
    });

    // Add smooth scrolling to all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // Add ripple effect to buttons
    document.querySelectorAll('button, .btn').forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;

            ripple.style.cssText = `
                position: absolute;
                width: ${size}px;
                height: ${size}px;
                background: rgba(255, 255, 255, 0.6);
                border-radius: 50%;
                left: ${x}px;
                top: ${y}px;
                pointer-events: none;
                animation: ripple 0.6s ease-out;
            `;

            this.appendChild(ripple);
            setTimeout(() => ripple.remove(), 600);
        });
    });
});

// ============================================================================
// EXPORT FOR GLOBAL USE
// ============================================================================

window.FormValidator = FormValidator;
window.PredictionCalculator = PredictionCalculator;
window.APIHelper = APIHelper;
window.AnimationManager = AnimationManager;
window.Modal = Modal;
window.TableManager = TableManager;
window.showNotification = showNotification;
