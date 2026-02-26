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

// ============================================================================
// PAGE NAVIGATION BUTTONS
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    const pageUpBtn = document.getElementById('pageUpBtn');
    const pageDownBtn = document.getElementById('pageDownBtn');
    
    if (pageUpBtn && pageDownBtn) {
        // Show/hide buttons based on scroll position
        function updatePageNavButtons() {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const scrollHeight = document.documentElement.scrollHeight;
            const clientHeight = document.documentElement.clientHeight;
            
            // Show page-up button when scrolled down
            if (scrollTop > 300) {
                pageUpBtn.classList.add('visible');
            } else {
                pageUpBtn.classList.remove('visible');
            }
            
            // Show page-down button when not at bottom
            if (scrollTop + clientHeight < scrollHeight - 100) {
                pageDownBtn.classList.add('visible');
            } else {
                pageDownBtn.classList.remove('visible');
            }
        }
        
        // Smooth scroll to top
        pageUpBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
        
        // Smooth scroll to bottom
        pageDownBtn.addEventListener('click', function() {
            window.scrollTo({
                top: document.documentElement.scrollHeight,
                behavior: 'smooth'
            });
        });
        
        // Update on scroll
        window.addEventListener('scroll', throttle(updatePageNavButtons, 100));
        
        // Initial check
        updatePageNavButtons();
    }
});

// ============================================================================
// AI CHATBOT FUNCTIONALITY
// ============================================================================

class HeartFLChatbot {
    constructor() {
        this.chatbotToggle = document.getElementById('chatbotToggle');
        this.chatbotWindow = document.getElementById('chatbotWindow');
        this.chatbotClose = document.getElementById('chatbotClose');
        this.chatbotMessages = document.getElementById('chatbotMessages');
        this.chatbotInput = document.getElementById('chatbotInput');
        this.chatbotSend = document.getElementById('chatbotSend');
        
        this.isOpen = false;
        this.messageHistory = [];
        
        this.init();
    }
    
    init() {
        if (!this.chatbotToggle) return;
        
        // Toggle chatbot
        this.chatbotToggle.addEventListener('click', () => this.toggleChat());
        this.chatbotClose.addEventListener('click', () => this.closeChat());
        
        // Send message
        this.chatbotSend.addEventListener('click', () => this.sendMessage());
        
        // Handle Enter key in textarea
        this.chatbotInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Auto-resize textarea
        this.chatbotInput.addEventListener('input', () => {
            this.chatbotInput.style.height = 'auto';
            this.chatbotInput.style.height = this.chatbotInput.scrollHeight + 'px';
        });
    }
    
    toggleChat() {
        this.isOpen = !this.isOpen;
        if (this.isOpen) {
            this.chatbotWindow.classList.add('open');
            this.chatbotInput.focus();
        } else {
            this.chatbotWindow.classList.remove('open');
        }
    }
    
    closeChat() {
        this.isOpen = false;
        this.chatbotWindow.classList.remove('open');
    }
    
    sendMessage() {
        const message = this.chatbotInput.value.trim();
        if (!message) return;
        
        // Add user message
        this.addMessage(message, 'user');
        this.messageHistory.push({role: 'user', content: message});
        
        // Clear input
        this.chatbotInput.value = '';
        this.chatbotInput.style.height = 'auto';
        
        // Disable send button
        this.chatbotSend.disabled = true;
        
        // Show typing indicator
        this.showTypingIndicator();
        
        // Get response from API or offline mode
        this.getAIResponse(message)
            .then(response => {
                this.hideTypingIndicator();
                this.addMessage(response, 'bot');
                this.messageHistory.push({role: 'bot', content: response});
            })
            .catch(error => {
                console.error('Chatbot error:', error);
                this.hideTypingIndicator();
                const fallbackResponse = this.generateOfflineResponse(message);
                this.addMessage(fallbackResponse, 'bot');
            })
            .finally(() => {
                this.chatbotSend.disabled = false;
            });
    }
    
    async getAIResponse(userMessage) {
        const config = window.CHATBOT_CONFIG || {};
        const provider = config.provider || 'offline';
        
        if (config.enableLogging) {
            console.log('Chatbot provider:', provider);
            console.log('User message:', userMessage);
        }
        
        // Use offline mode if no provider configured
        if (provider === 'offline') {
            await this.delay(config.typingDelay || 1000);
            return this.generateOfflineResponse(userMessage);
        }
        
        // Try API call based on provider
        try {
            switch (provider) {
                case 'openai':
                    return await this.callOpenAI(userMessage, config.openai);
                case 'anthropic':
                    return await this.callAnthropic(userMessage, config.anthropic);
                case 'groq':
                    return await this.callGroq(userMessage, config.groq);
                case 'local':
                    return await this.callLocalLLM(userMessage, config.local);
                default:
                    return this.generateOfflineResponse(userMessage);
            }
        } catch (error) {
            console.error('API call failed:', error);
            // Fallback to offline mode
            return this.generateOfflineResponse(userMessage);
        }
    }
    
    async callOpenAI(message, config) {
        const response = await fetch(config.apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${config.apiKey}`
            },
            body: JSON.stringify({
                model: config.model,
                messages: [
                    { role: 'system', content: config.systemPrompt },
                    ...this.messageHistory.slice(-10), // Last 10 messages
                    { role: 'user', content: message }
                ],
                max_tokens: config.maxTokens,
                temperature: config.temperature
            })
        });
        
        if (!response.ok) {
            throw new Error(`OpenAI API error: ${response.status}`);
        }
        
        const data = await response.json();
        return data.choices[0].message.content;
    }
    
    async callAnthropic(message, config) {
        const response = await fetch(config.apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-api-key': config.apiKey,
                'anthropic-version': '2023-06-01'
            },
            body: JSON.stringify({
                model: config.model,
                system: config.systemPrompt,
                messages: [
                    ...this.messageHistory.slice(-10),
                    { role: 'user', content: message }
                ],
                max_tokens: config.maxTokens,
                temperature: config.temperature
            })
        });
        
        if (!response.ok) {
            throw new Error(`Anthropic API error: ${response.status}`);
        }
        
        const data = await response.json();
        return data.content[0].text;
    }
    
    async callGroq(message, config) {
        // Groq uses OpenAI-compatible API
        const response = await fetch(config.apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${config.apiKey}`
            },
            body: JSON.stringify({
                model: config.model,
                messages: [
                    { role: 'system', content: config.systemPrompt },
                    ...this.messageHistory.slice(-10),
                    { role: 'user', content: message }
                ],
                max_tokens: config.maxTokens,
                temperature: config.temperature
            })
        });
        
        if (!response.ok) {
            throw new Error(`Groq API error: ${response.status}`);
        }
        
        const data = await response.json();
        return data.choices[0].message.content;
    }
    
    async callLocalLLM(message, config) {
        // Ollama API format
        const response = await fetch(config.apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model: config.model,
                messages: [
                    { role: 'system', content: config.systemPrompt },
                    ...this.messageHistory.slice(-10),
                    { role: 'user', content: message }
                ],
                stream: false
            })
        });
        
        if (!response.ok) {
            throw new Error(`Local LLM error: ${response.status}`);
        }
        
        const data = await response.json();
        return data.message.content;
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    addMessage(text, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chatbot-message ${type}-message`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = type === 'bot' ? '<i class="bi bi-robot"></i>' : '<i class="bi bi-person-fill"></i>';
        
        const content = document.createElement('div');
        content.className = 'message-content';
        content.innerHTML = this.formatMessage(text);
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        
        this.chatbotMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    formatMessage(text) {
        // Convert markdown-like formatting
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
    }
    
    showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'typingIndicator';
        indicator.className = 'chatbot-message bot-message';
        indicator.innerHTML = `
            <div class="message-avatar">
                <i class="bi bi-robot"></i>
            </div>
            <div class="message-content">
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        this.chatbotMessages.appendChild(indicator);
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.remove();
        }
    }
    
    scrollToBottom() {
        this.chatbotMessages.scrollTop = this.chatbotMessages.scrollHeight;
    }
    
    generateOfflineResponse(message) {
        const lowerMessage = message.toLowerCase();
        
        // Keyword-based responses (replace with actual LLM API)
        if (lowerMessage.includes('predict') || lowerMessage.includes('prediction')) {
            return 'To make a heart disease prediction, go to the **Predict** page using the navigation menu. You\'ll need to enter various health parameters like age, blood pressure, cholesterol, etc. Our federated learning model will analyze your data while keeping it private and secure.';
        }
        
        if (lowerMessage.includes('federated') || lowerMessage.includes('fl') || lowerMessage.includes('learning')) {
            return '**Federated Learning (FL)** is a privacy-preserving machine learning technique where the model is trained across multiple hospitals without sharing patient data. Each hospital trains the model locally, and only model updates are shared, ensuring patient privacy. You can learn more on our **FL Dashboard** page.';
        }
        
        if (lowerMessage.includes('issue') || lowerMessage.includes('problem') || lowerMessage.includes('bug') || lowerMessage.includes('error')) {
            return 'I\'m sorry you\'re experiencing issues! Please describe the problem in detail:\n\n• What page were you on?\n• What were you trying to do?\n• What happened instead?\n\nYou can also use the **Contact** page to report technical issues to our team.';
        }
        
        if (lowerMessage.includes('register') || lowerMessage.includes('signup') || lowerMessage.includes('account')) {
            return 'To create an account, click on the **Login** link in the navigation menu, then select "Sign Up". You\'ll need to provide your email, create a password, and choose your account type (patient or hospital administrator).';
        }
        
        if (lowerMessage.includes('how') && (lowerMessage.includes('work') || lowerMessage.includes('use'))) {
            return 'HeartFL is a heart disease risk prediction system that uses federated learning:\n\n1. **Hospitals** upload encrypted patient data\n2. **Federated Learning** trains models without sharing raw data\n3. **Patients** can get predictions while maintaining privacy\n4. **Real-time Dashboard** shows training progress\n\nNavigate through our pages to explore each feature!';
        }
        
        if (lowerMessage.includes('about') || lowerMessage.includes('information')) {
            return 'HeartFL is a privacy-preserving heart disease risk prediction platform using federated learning. Visit our **About** page to learn more about our mission, technology, and team. You can also check the **FL Dashboard** to see how the federated learning process works in real-time.';
        }
        
        if (lowerMessage.includes('contact') || lowerMessage.includes('support') || lowerMessage.includes('help')) {
            return 'You can reach our support team through the **Contact** page. Fill out the form with your question or concern, and we\'ll get back to you within 24 hours. For urgent issues, please mark them as high priority.';
        }
        
        if (lowerMessage.includes('dashboard')) {
            return 'The **Dashboard** shows your personal information and prediction history. You can view past predictions, update your profile, and manage your account settings. Access it by clicking on your username in the top menu.';
        }
        
        if (lowerMessage.includes('thank') || lowerMessage.includes('thanks')) {
            return 'You\'re welcome! I\'m here to help. Feel free to ask me anything about HeartFL, federated learning, or how to use our platform.';
        }
        
        if (lowerMessage.includes('hi') || lowerMessage.includes('hello') || lowerMessage.includes('hey')) {
            return 'Hello! How can I assist you today? I can help with:\n\n• Understanding heart disease prediction\n• Navigating the website\n• Explaining federated learning\n• Reporting technical issues\n• Account and feature questions';
        }
        
        // Default response
        return 'I\'m here to help! I can assist you with:\n\n• **Heart disease predictions** - How to use the prediction feature\n• **Federated Learning** - Understanding our privacy-preserving technology\n• **Navigation** - Finding your way around the website\n• **Technical support** - Reporting issues or bugs\n• **Account help** - Registration and settings\n\nWhat would you like to know more about?';
    }
}

// Initialize chatbot
document.addEventListener('DOMContentLoaded', function() {
    window.heartFLChatbot = new HeartFLChatbot();
});
