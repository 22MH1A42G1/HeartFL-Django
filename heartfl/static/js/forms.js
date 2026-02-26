/**
 * HeartFL - Form Handling & Validation
 * Advanced form validation, submission, and real-time feedback
 */

class AdvancedFormValidator {
    constructor(formSelector) {
        this.form = document.querySelector(formSelector);
        this.fields = {};
        this.errors = {};
        this.touched = {};
        
        if (this.form) {
            this.initializeFields();
            this.attachEventListeners();
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
     * Initialize field references
     */
    initializeFields() {
        this.form.querySelectorAll('[name]').forEach(field => {
            this.fields[field.name] = field;
            this.touched[field.name] = false;
        });
    }

    /**
     * Attach event listeners to all form fields
     */
    attachEventListeners() {
        Object.values(this.fields).forEach(field => {
            // Real-time validation on input
            field.addEventListener('input', (e) => this.validateField(e.target));
            
            // Mark as touched on blur
            field.addEventListener('blur', (e) => {
                this.touched[e.target.name] = true;
                this.validateField(e.target);
            });

            // Visual feedback on focus
            field.addEventListener('focus', (e) => {
                this.clearFieldError(e.target);
            });
        });

        // Handle form submission
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    /**
     * Validation rules
     */
    validationRules = {
        // Text fields
        required: (value) => value.trim() !== '' || 'This field is required',
        
        // Email
        email: (value) => {
            const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return re.test(value) || 'Please enter a valid email address';
        },

        // Phone
        phone: (value) => {
            if (!value) return true;
            const re = /^\+?[\d\s\-()]{10,}$/;
            return re.test(value.replace(/\s/g, '')) || 'Please enter a valid phone number';
        },

        // Age
        age: (value) => {
            const num = parseInt(value);
            return (num >= 0 && num <= 150) || 'Age must be between 0 and 150';
        },

        // Numeric fields
        numeric: (value) => {
            return !isNaN(value) || 'Please enter a valid number';
        },

        // Min length
        minLength: (min) => (value) => {
            return value.length >= min || `Minimum ${min} characters required`;
        },

        // Max length
        maxLength: (max) => (value) => {
            return value.length <= max || `Maximum ${max} characters allowed`;
        },

        // Min value
        min: (min) => (value) => {
            return parseFloat(value) >= min || `Minimum value is ${min}`;
        },

        // Max value
        max: (max) => (value) => {
            return parseFloat(value) <= max || `Maximum value is ${max}`;
        },

        // Pattern (regex)
        pattern: (pattern, message) => (value) => {
            return pattern.test(value) || message;
        }
    };

    /**
     * Validate individual field
     */
    validateField(field) {
        const name = field.name;
        const value = field.value;
        const rules = field.dataset.rules;

        if (!rules) return true;

        const ruleList = rules.split('|');
        let isValid = true;
        let errorMessage = '';

        for (const rule of ruleList) {
            const [ruleName, ...params] = rule.split(':');
            
            if (ruleName === 'required' && !this.touched[name] && !value) {
                continue;
            }

            const validationFn = this.validationRules[ruleName];
            if (validationFn) {
                const result = params.length > 0 
                    ? validationFn(...params)(value)
                    : validationFn(value);

                if (result !== true) {
                    isValid = false;
                    errorMessage = result;
                    break;
                }
            }
        }

        if (!isValid && this.touched[name]) {
            this.showFieldError(field, errorMessage);
        } else {
            this.clearFieldError(field);
        }

        this.errors[name] = isValid ? null : errorMessage;
        return isValid;
    }

    /**
     * Show field error
     */
    showFieldError(field, message) {
        field.classList.add('is-invalid');
        
        let errorDiv = field.parentElement.querySelector('.invalid-feedback');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback d-block';
            field.parentElement.appendChild(errorDiv);
        }
        
        errorDiv.textContent = message;
        errorDiv.style.animation = 'fadeIn 0.3s ease';
    }

    /**
     * Clear field error
     */
    clearFieldError(field) {
        field.classList.remove('is-invalid');
        const errorDiv = field.parentElement.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    /**
     * Validate entire form
     */
    validateForm() {
        let isValid = true;

        Object.values(this.fields).forEach(field => {
            this.touched[field.name] = true;
            if (!this.validateField(field)) {
                isValid = false;
            }
        });

        return isValid;
    }

    /**
     * Handle form submission
     */
    async handleSubmit(e) {
        if (!this.validateForm()) {
            e.preventDefault();
            this.showFormError('Please fix the errors above');
            return;
        }

        if (this.isAjaxForm()) {
            e.preventDefault();
            await this.submitForm();
        }
    }

    /**
     * Submit form data
     */
    async submitForm() {
        const submitBtn = this.form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;

        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Submitting...';

        try {
            const formData = new FormData(this.form);
            const response = await fetch(this.form.action || '/api/contact/', {
                method: 'POST',
                body: this.form.enctype === 'multipart/form-data' 
                    ? formData 
                    : JSON.stringify(Object.fromEntries(formData)),
                headers: this.form.enctype === 'multipart/form-data' 
                    ? {} 
                    : { 'Content-Type': 'application/json' },
                credentials: 'same-origin'
            });

            if (response.ok) {
                this.showFormSuccess('✅ Form submitted successfully!');
                this.form.reset();
                this.touched = {};
                
                // Redirect after delay if specified
                const redirectUrl = this.form.dataset.redirect;
                if (redirectUrl) {
                    setTimeout(() => {
                        window.location.href = redirectUrl;
                    }, 2000);
                }
            } else {
                const error = await response.json();
                this.showFormError(error.message || '❌ Error submitting form');
            }
        } catch (error) {
            console.error('Form submission error:', error);
            this.showFormError(`❌ Error: ${error.message}`);
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    }

    /**
     * Show form-level error
     */
    showFormError(message) {
        this.removeFormAlert();
        
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show';
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        this.form.parentElement.insertBefore(alertDiv, this.form);
    }

    /**
     * Show form-level success
     */
    showFormSuccess(message) {
        this.removeFormAlert();
        
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-success alert-dismissible fade show';
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        this.form.parentElement.insertBefore(alertDiv, this.form);
    }

    /**
     * Remove existing form alerts
     */
    removeFormAlert() {
        const existingAlert = this.form.parentElement.querySelector('.alert');
        if (existingAlert) {
            existingAlert.remove();
        }
    }

    /**
     * Reset form
     */
    resetForm() {
        this.form.reset();
        this.touched = {};
        this.errors = {};
        
        Object.values(this.fields).forEach(field => {
            this.clearFieldError(field);
        });
    }

    /**
     * Get form data as object
     */
    getFormData() {
        const formData = new FormData(this.form);
        return Object.fromEntries(formData);
    }

    /**
     * Populate form with data
     */
    populateForm(data) {
        Object.entries(data).forEach(([key, value]) => {
            const field = this.fields[key];
            if (field) {
                field.value = value;
                field.dispatchEvent(new Event('input'));
            }
        });
    }
}

// ============================================================================
// SPECIALIZED FORM VALIDATORS
// ============================================================================

/**
 * Contact Form Validator
 */
class ContactFormValidator extends AdvancedFormValidator {
    constructor() {
        super('form[data-contact-form]');
    }
}

/**
 * Prediction Form Validator
 */
class PredictionFormValidator extends AdvancedFormValidator {
    constructor() {
        super('form[data-prediction-form]');
        this.setupLiveUpdates();
    }

    setupLiveUpdates() {
        Object.values(this.fields).forEach(field => {
            if (field.type === 'number' || field.type === 'range') {
                field.addEventListener('input', () => this.updatePreview());
            }
        });
    }

    updatePreview() {
        const data = this.getFormData();
        console.log('Prediction data updated:', data);
        
        // Trigger prediction update if needed
        const event = new CustomEvent('predictionDataChanged', { detail: data });
        document.dispatchEvent(event);
    }
}

/**
 * Login Form Validator
 */
class LoginFormValidator extends AdvancedFormValidator {
    constructor() {
        super('form[data-login-form]');
    }
}

/**
 * Registration Form Validator
 */
class RegistrationFormValidator extends AdvancedFormValidator {
    constructor() {
        super('form[data-registration-form]');
        this.setupPasswordConfirmation();
    }

    setupPasswordConfirmation() {
        const passwordField = this.fields['password'];
        const confirmField = this.fields['password_confirm'];

        if (confirmField) {
            confirmField.dataset.rules = `required|pattern:^${passwordField.value.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&')}$:Passwords do not match`;
            
            passwordField.addEventListener('input', () => {
                confirmField.dataset.rules = `required|pattern:^${passwordField.value.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&')}$:Passwords do not match`;
                this.validateField(confirmField);
            });

            confirmField.addEventListener('input', () => {
                this.validateField(confirmField);
            });
        }
    }
}

// ============================================================================
// FORM UTILITIES
// ============================================================================

/**
 * Auto-format phone number
 */
function autoFormatPhone(input) {
    let value = input.value.replace(/\D/g, '');
    
    if (value.length > 0) {
        if (value.length <= 3) {
            value = `(${value}`;
        } else if (value.length <= 6) {
            value = `(${value.slice(0, 3)}) ${value.slice(3)}`;
        } else {
            value = `(${value.slice(0, 3)}) ${value.slice(3, 6)}-${value.slice(6, 10)}`;
        }
    }
    
    input.value = value;
}

/**
 * Auto-capitalize words
 */
function autoCapitalize(input) {
    input.value = input.value.replace(/\b\w/g, char => char.toUpperCase());
}

/**
 * Set form field focus with error
 */
function focusFirstError(formSelector) {
    const form = document.querySelector(formSelector);
    const errorField = form?.querySelector('.is-invalid');
    if (errorField) {
        errorField.focus();
        errorField.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

/**
 * Enable/Disable form submit button based on validation
 */
function toggleSubmitButton(formSelector, validator) {
    const submitBtn = document.querySelector(`${formSelector} button[type="submit"]`);
    if (!submitBtn) return;

    const hasErrors = Object.values(validator.errors).some(error => error !== null);
    const isComplete = Object.values(validator.fields).every(field => 
        !field.dataset.rules?.includes('required') || field.value.trim() !== ''
    );

    submitBtn.disabled = hasErrors || !isComplete;
}

// ============================================================================
// DYNAMIC FORM FIELDS
// ============================================================================

class DynamicFormBuilder {
    /**
     * Add form field dynamically
     */
    static addField(formSelector, fieldHTML) {
        const form = document.querySelector(formSelector);
        if (!form) return;

        const div = document.createElement('div');
        div.innerHTML = fieldHTML;
        form.appendChild(div.firstElementChild);
    }

    /**
     * Remove form field
     */
    static removeField(fieldSelector) {
        const field = document.querySelector(fieldSelector);
        if (field) {
            field.style.animation = 'slideOutLeft 0.3s ease';
            setTimeout(() => field.remove(), 300);
        }
    }

    /**
     * Clear form
     */
    static clearForm(formSelector) {
        const form = document.querySelector(formSelector);
        if (form) {
            form.reset();
            form.querySelectorAll('[class*="invalid"]').forEach(el => {
                el.classList.remove('is-invalid');
            });
        }
    }
}

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('HeartFL Form Validators Loaded');

    // Initialize contact form
    if (document.querySelector('form[data-contact-form]')) {
        new ContactFormValidator();
    }

    // Initialize prediction form
    if (document.querySelector('form[data-prediction-form]')) {
        new PredictionFormValidator();
    }

    // Initialize login form
    if (document.querySelector('form[data-login-form]')) {
        new LoginFormValidator();
    }

    // Initialize registration form
    if (document.querySelector('form[data-registration-form]')) {
        new RegistrationFormValidator();
    }

    // Setup phone formatting
    document.querySelectorAll('input[data-phone]').forEach(input => {
        input.addEventListener('input', () => autoFormatPhone(input));
    });

    // Setup auto-capitalization
    document.querySelectorAll('input[data-capitalize]').forEach(input => {
        input.addEventListener('input', () => autoCapitalize(input));
    });
});

// ============================================================================
// EXPORT FOR GLOBAL USE
// ============================================================================

window.AdvancedFormValidator = AdvancedFormValidator;
window.ContactFormValidator = ContactFormValidator;
window.PredictionFormValidator = PredictionFormValidator;
window.LoginFormValidator = LoginFormValidator;
window.RegistrationFormValidator = RegistrationFormValidator;
window.DynamicFormBuilder = DynamicFormBuilder;
window.autoFormatPhone = autoFormatPhone;
window.autoCapitalize = autoCapitalize;
window.focusFirstError = focusFirstError;
