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
        this.chatbotVoice = document.getElementById('chatbotVoice');
        this.voiceIndicator = document.getElementById('voiceIndicator');
        
        this.isOpen = false;
        this.messageHistory = [];
        this.isListening = false;
        
        // Voice Recognition Setup
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = SpeechRecognition ? new SpeechRecognition() : null;
        
        if (this.recognition) {
            this.recognition.continuous = false;
            this.recognition.interimResults = true;
            this.recognition.lang = 'en-US';
        }
        
        // Speech Synthesis
        this.synthesis = window.speechSynthesis;
        
        this.init();
    }
    
    init() {
        if (!this.chatbotToggle) return;
        
        // Toggle chatbot
        this.chatbotToggle.addEventListener('click', () => this.toggleChat());
        this.chatbotClose.addEventListener('click', () => this.closeChat());
        
        // Send message
        this.chatbotSend.addEventListener('click', () => this.sendMessage());
        
        // Voice input (always bind so users get clear fallback messages)
        if (this.chatbotVoice) {
            this.chatbotVoice.addEventListener('click', () => this.toggleVoiceInput());
        }
        
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
        
        // Setup voice recognition handlers
        if (this.recognition) {
            this.setupVoiceRecognition();
        }
    }
    
    setupVoiceRecognition() {
        this.recognition.onstart = () => {
            this.isListening = true;
            if (this.chatbotVoice) {
                this.chatbotVoice.classList.add('listening');
            }
            if (this.voiceIndicator) {
                this.voiceIndicator.style.display = 'block';
            }
        };
        
        this.recognition.onend = () => {
            this.isListening = false;
            if (this.chatbotVoice) {
                this.chatbotVoice.classList.remove('listening');
            }
            if (this.voiceIndicator) {
                this.voiceIndicator.style.display = 'none';
            }
        };
        
        this.recognition.onerror = (event) => {
            console.error('Voice recognition error:', event.error);
            this.isListening = false;
            if (this.chatbotVoice) {
                this.chatbotVoice.classList.remove('listening');
            }
            if (this.voiceIndicator) {
                this.voiceIndicator.style.display = 'none';
            }

            let message = 'Voice input error. Please try again or type your message.';
            if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
                message = 'Microphone permission is blocked. Please allow microphone access in your browser settings and try again.';
            } else if (event.error === 'no-speech') {
                message = 'No speech was detected. Please tap the mic and speak clearly.';
            } else if (event.error === 'audio-capture') {
                message = 'No microphone was found. Please connect a microphone and try again.';
            }

            this.addMessage(message, 'bot');
        };
        
        this.recognition.onresult = (event) => {
            let transcript = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {
                transcript += event.results[i][0].transcript;
            }
            if (event.results[event.results.length - 1].isFinal) {
                this.chatbotInput.value = transcript;
                this.sendMessage();
            }
        };
    }
    
    toggleVoiceInput() {
        if (!this.recognition) {
            this.addMessage('Voice input is not supported in this browser. Please use Chrome, Edge, or Safari.', 'bot');
            return;
        }

        if (!window.isSecureContext) {
            this.addMessage('Voice input needs a secure connection (HTTPS or localhost). Please open this app in a secure context.', 'bot');
            return;
        }
        
        if (this.isListening) {
            this.recognition.stop();
        } else {
            try {
                this.recognition.start();
            } catch (error) {
                console.error('Voice start error:', error);
                this.addMessage('Could not start voice input. Please try again in a moment.', 'bot');
            }
        }
    }
    
    speakResponse(text) {
        if (!this.synthesis || typeof this.synthesis.speak !== 'function') {
            return;
        }

        // Stop any ongoing speech
        this.synthesis.cancel();
        
        // Create utterance from plain text (remove HTML)
        const plainText = text
            .replace(/<[^>]*>/g, '')
            .replace(/\*\*(.*?)\*\*/g, '$1')
            .replace(/\*(.*?)\*/g, '$1');
        
        const utterance = new SpeechSynthesisUtterance(plainText);
        utterance.rate = 0.95;
        utterance.pitch = 1;
        utterance.volume = 0.9;
        
        this.synthesis.speak(utterance);
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
                // Speak response
                setTimeout(() => this.speakResponse(response), 300);
            })
            .catch(error => {
                console.error('Chatbot error:', error);
                this.hideTypingIndicator();
                const fallbackResponse = this.generateOfflineResponse(message);
                this.addMessage(fallbackResponse, 'bot');
                // Speak fallback response
                setTimeout(() => this.speakResponse(fallbackResponse), 300);
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

        const heartflKeywords = [
            'heartfl', 'heart', 'prediction', 'predict', 'federated', 'fl',
            'dashboard', 'hospital', 'doctor', 'patient', 'privacy', 'model',
            'account', 'login', 'register', 'settings', 'theme', 'contact',
            'support', 'bug', 'error', 'about', 'project', 'team', 'developer',
            'website', 'page', 'navigation', 'dataset'
        ];
        const offTopicKeywords = [
            'weather', 'temperature', 'rain', 'movie', 'music', 'song', 'sports',
            'cricket', 'football', 'politics', 'election', 'stock', 'crypto',
            'bitcoin', 'recipe', 'cooking', 'travel', 'joke', 'poem', 'relationship'
        ];
        const isHeartFLRelated = heartflKeywords.some(keyword => lowerMessage.includes(keyword));
        const isLikelyOffTopic = offTopicKeywords.some(keyword => lowerMessage.includes(keyword));

        if (isLikelyOffTopic && !isHeartFLRelated) {
            return 'That topic is outside this application\'s scope. I can best help with **HeartFL** features like heart disease prediction, federated learning, dashboard usage, account settings, and technical support.\n\nIf you share your HeartFL-related question, I\'ll help right away.';
        }
        
        // Practical scenario: explain binary risk output before generic prediction help
        if (
            (lowerMessage.includes('why') || lowerMessage.includes('how')) &&
            (lowerMessage.includes('high') || lowerMessage.includes('low')) &&
            (lowerMessage.includes('predict') || lowerMessage.includes('prediction') || lowerMessage.includes('value'))
        ) {
            return 'Great question. The current HeartFL model is configured as a **binary classifier**, so it returns only two risk classes: **low** or **high**.\n\nBehind the scenes, the model computes a probability score and then applies a decision threshold (for example, 0.5) to map that score into one of the two classes.\n\nIf your team wants richer outputs, you can extend this to:\n• show the exact probability score\n• add risk bands like low/medium/high\n• provide feature-level explanation for each prediction';
        }

        if (lowerMessage.includes('how are you') || lowerMessage === 'how r u') {
            return 'I am doing well and ready to help with HeartFL. If you want practical guidance, ask me scenario-based questions like prediction behavior, federated learning flow, or dashboard troubleshooting.';
        }

        // Keyword-based responses (replace with actual LLM API)
        if (lowerMessage.includes('predict') || lowerMessage.includes('prediction')) {
            return 'To make a heart disease prediction, go to the **Predict** page using the navigation menu. Enter the required health parameters, submit the form, and the model will return a risk category. For practical use-cases, you can also ask me why a result is high or low and I will explain the logic.';
        }

        if (lowerMessage.includes('federated') || lowerMessage.includes('fl') || lowerMessage.includes('learning')) {
            return '**Federated Learning (FL)** is a privacy-preserving machine learning technique where the model is trained across multiple hospitals without sharing patient data. Each hospital trains the model locally, and only model updates are shared, ensuring patient privacy. You can learn more on our **FL Dashboard** page.';
        }

        if (
            lowerMessage.includes('who developed') ||
            lowerMessage.includes('who made') ||
            lowerMessage.includes('who created') ||
            lowerMessage.includes('develop you') ||
            lowerMessage.includes('developer') ||
            lowerMessage.includes('your team') ||
            lowerMessage.includes('aditya') ||
            lowerMessage.includes('suresh') ||
            lowerMessage.includes('jnanadeep') ||
            lowerMessage.includes('hemanth')
        ) {
            return '**HeartFL Project Developers:**\n\n• **Aditya** - Project Lead & Full-Stack Developer\n• **Suresh** - Backend & Federated Learning Architecture\n• **Jnanadeep** - Frontend UI/UX & Theme System\n• **Hemanth** - Database & Admin Panel\n\n**Guided By:**\n• **Y. Suresh Kumar** - Project Advisor & Teacher\n\nWe designed and built this application for privacy-preserving heart disease risk prediction using federated learning. This is a final year engineering project focusing on real-world healthcare solutions.\n\n⚠️ **Research & Reference Project**: This application is currently for research, educational, and hospital testing purposes. It is not yet a complete enterprise application - features and scaling will be enhanced soon.';
        }

        if (
            lowerMessage.includes('why use') ||
            (lowerMessage.includes('why') && lowerMessage.includes('application')) ||
            lowerMessage.includes('benefit') ||
            lowerMessage.includes('advantage')
        ) {
            return '**Why Use HeartFL:**\n\n✅ **Privacy Protection** - Patient data stays in hospitals; only model updates shared\n✅ **Accurate Predictions** - ML model trained on multi-hospital federated data\n✅ **Easy Hospital Integration** - Simple CSV upload for datasets\n✅ **Doctor-Friendly** - One-click predictions with instant reports\n✅ **Real-Time Monitoring** - Dashboard shows FL training progress\n✅ **Compliance-Ready** - No raw patient data leaves hospital sites\n✅ **Role-Based Access** - Hospital Admin, Doctor, and System Admin workflows\n\nPerfect for healthcare systems that need predictive analytics without compromising patient privacy.';
        }

        if (
            (lowerMessage.includes('architecture') || lowerMessage.includes('system design')) &&
            (lowerMessage.includes('explain') || lowerMessage.includes('describe') || lowerMessage.includes('how') || lowerMessage.includes('work'))
        ) {
            return '**HeartFL Architecture Overview:**\n\n**Backend:** Django 5.2 + SQLite3\n**Frontend:** Django Templates + Bootstrap 5.3\n**ML Engine:** scikit-learn models\n\n**Component Flow:**\n1. **Hospitals** upload patient CSV datasets\n2. **Database** stores normalized patient records\n3. **Doctors** enter patient data via web form\n4. **Prediction Engine** runs ML model on features\n5. **Result** returns Low/High risk with probability\n6. **Report** generates PDF for doctor-patient consultation\n\n**Federated Learning:**\n• Each hospital trains locally on private data\n• Model updates (not raw data) sent to central server\n• Central aggregation creates improved global model\n• Global model distributed back for better predictions';
        }

        if (
            lowerMessage.includes('federated learning') &&
            (lowerMessage.includes('why') || lowerMessage.includes('important') || lowerMessage.includes('benefit'))
        ) {
            return '**Why Federated Learning Matters in HeartFL:**\n\n🔒 **Data Privacy** - Patient records never leave hospitals\n🌐 **Collaborative Learning** - Multiple hospitals improve one model together\n📊 **Better Predictions** - More data = more accurate ML model without sharing raw patient info\n✅ **Regulatory Compliance** - Meets HIPAA, GDPR requirements\n🚀 **Scalability** - Add hospitals without data transfer complexity\n\nInstead of centralizing sensitive patient data, FL allows hospitals to contribute to model training while keeping data secure on-site. This is revolutionary for healthcare analytics.';
        }

        if (
            (lowerMessage.includes('verify') || lowerMessage.includes('verification')) &&
            lowerMessage.includes('doctor')
        ) {
            return '**How to Verify Doctors in Admin Dashboard:**\n\n1. Go to **Admin Dashboard** → Click **Doctors** section\n2. Find doctor in list\n3. Click **Edit** to open doctor details\n4. Check: Medical License Number, Phone, Hospital Association\n5. Toggle **Is Active** checkbox to activate/deactivate\n6. Click **Save**\n\n**Verification Checklist:**\n✓ License number matches official registry\n✓ Email domain is professional medical institution\n✓ Hospital association is verified first\n✓ Contact details are valid\n\nOnce verified and activated, the doctor can log in and make predictions.';
        }

        if (
            (lowerMessage.includes('verify') || lowerMessage.includes('verification')) &&
            lowerMessage.includes('hospital')
        ) {
            return '**How to Verify Hospitals in Admin Dashboard:**\n\n1. Go to **Admin Dashboard** → Click **Hospitals** section\n2. Find hospital pending verification\n3. Click **Edit** to open hospital details\n4. Verify: Registration Number, Address, Email, Contact\n5. Check: is_verified checkbox to mark as verified\n6. Click **Save**\n\n**Verification Checklist:**\n✓ Hospital registration number matches government records\n✓ Email is institutional domain (not personal)\n✓ Address verified with official registry\n✓ Phone contact responds to verification call\n\nOnce verified, the hospital can upload datasets and register doctors. Unverified hospitals cannot upload data.';
        }

        if (
            lowerMessage.includes('admin') &&
            (lowerMessage.includes('how') || lowerMessage.includes('manage') || lowerMessage.includes('handle') || lowerMessage.includes('operate'))
        ) {
            return '**How to Handle Admin Dashboard Operations:**\n\n**Admin Panel Access:** http://yoursite/admin/\n\n**Main Tasks:**\n1. **Verify Hospitals** - Check registration details, approve is_verified\n2. **Activate Doctors** - Toggle is_active checkbox for doctor accounts\n3. **Review Messages** - Check contact form submissions\n4. **View Statistics** - Dashboard shows users, hospitals, doctors, predictions\n5. **User Management** - Create/edit/delete user accounts\n\n**Bulk Actions:**\n• Select multiple hospitals/doctors\n• Apply bulk verification from dropdown\n• Mark as read/delete contact messages\n\n**Search & Filter:**\n• Search by hospital name, city, registration\n• Filter doctors by hospital or is_active status\n• Sort messages by date\n\nUse custom actions for batch operations to save time.';
        }

        if (
            lowerMessage.includes('database') &&
            (lowerMessage.includes('admin') || lowerMessage.includes('manage') || lowerMessage.includes('access'))
        ) {
            return '**How to Handle Database in Admin Panel:**\n\n**Database:** SQLite3 (db.sqlite3)\n\n**Admin Interface Tables:**\n• **Users** - Django user accounts with auth credentials\n• **UserProfile** - Extended user info (phone, user type, theme)\n• **Hospital** - Hospital details, registration, verification status\n• **Doctor** - Doctor info, license, hospital link, active status\n• **PatientData** - Patient clinical features (age, BP, cholesterol, etc)\n• **PredictionResult** - ML prediction outcomes, probability, timestamp\n• **HospitalDataset** - Uploaded CSV file metadata\n• **ContactMessage** - User inquiries, read status\n\n**Admin Actions:**\n✓ View all records in table format\n✓ Add new records via form\n✓ Edit existing fields\n✓ Delete records (use with caution)\n✓ Filter by date ranges\n✓ Export data (if configured)\n\n**Best Practices:**\n• Backup db.sqlite3 regularly\n• Do not delete user accounts if predictions exist (referential integrity)\n• Archive old prediction records to keep DB performance fast';
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

        if (
            (lowerMessage.includes('upload') || lowerMessage.includes('dataset') || lowerMessage.includes('csv')) &&
            (lowerMessage.includes('hospital') || lowerMessage.includes('how'))
        ) {
            return '**How Hospitals Upload Datasets:**\n\n1. Hospital Admin logs in and goes to **Hospital Dashboard**\n2. Click **Upload Dataset** button\n3. Select CSV file with patient records\n4. Provide dataset description (optional)\n5. Enter number of patient records\n6. Click **Upload**\n\n**CSV Format Requirements:**\n• Comma-separated values (.csv file)\n• Columns: age, blood_pressure, cholesterol, etc.\n• No raw patient IDs (anonymized data recommended)\n• Valid numeric values\n\n**After Upload:**\n• Data stored securely in hospital\'s database\n• Used for local model training\n• Only model updates sent to central server\n• Raw patient data never leaves hospital';
        }

        if (
            lowerMessage.includes('pdf') ||
            (lowerMessage.includes('report') && lowerMessage.includes('prediction'))
        ) {
            return '**PDF Report Generation:**\n\nAfter making a heart disease prediction, doctors can download a PDF report containing:\n\n📄 **Report Contents:**\n• Patient name & age\n• Clinical parameters entered\n• Prediction result (Low Risk / High Risk)\n• Probability score (0-100%)\n• Timestamp of prediction\n• Doctor name & hospital\n• Recommendation for follow-up\n\nReports are used for:\n✓ Doctor-patient consultation\n✓ Clinical record keeping\n✓ Insurance documentation\n✓ Medical audit trails\n\nEach report is automatically timestamped and includes prediction confidence metrics.';
        }

        if (
            lowerMessage.includes('feature') ||
            (lowerMessage.includes('what') && lowerMessage.includes('predict'))
        ) {
            return '**Prediction Features (Patient Data):**\n\nThe model considers these clinical parameters to make predictions:\n\n**Demographic:**\n• Age (years)\n• Gender (M/F)\n\n**Cardiovascular:**\n• Resting Blood Pressure (mmHg)\n• Serum Cholesterol (mg/dl)\n• Max Heart Rate Achieved\n• Exercise-induced Angina (Yes/No)\n\n**ECG & Results:**\n• Resting ECG values (0-2)\n• ST depression induced by exercise\n• Slope of ST segment (0-2)\n\n**Lifestyle:**\n• Fasting Blood Sugar > 120 mg/dl (Yes/No)\n• Chest pain type (0-3)\n\nOur ML model uses these inputs to compute a heart disease risk probability.\n\n⚠️ **For Hospital/Doctor Use Only:**\n✅ Reference point for clinical decision-making\n✅ Supports professional medical assessment\n✅ Not substitute for complete cardiac evaluation';
        }

        if (lowerMessage.includes('accuracy') || lowerMessage.includes('performance')) {
            return '**Model Performance:**\n\n🎉 **Metrics:**\n• Overall Accuracy: ~92% on test datasets\n• Sensitivity (True Positive Rate): High\n• Specificity (True Negative Rate): Well-balanced\n• AUC-ROC: Excellent discrimination\n\n**Continuous Improvement:**\n• Model updates with new hospital data\n• Federated learning trains on distributed datasets\n• No single hospital\'s data dominates\n• Accuracy improves as more hospitals participate\n\n⚠️ **IMPORTANT HEALTH DISCLAIMER:**\n❌ **NOT a substitute for professional medical diagnosis**\n❌ Model is for **screening and reference only**\n✅ **Always consult a cardiologist for final diagnosis**\n✅ This research application supports healthcare professionals\n\n📋 **Project Status**: Currently in research/testing phase. Performance may vary by population demographics.';
        }

        if (
            (lowerMessage.includes('threshold') || lowerMessage.includes('cutoff')) &&
            lowerMessage.includes('predict')
        ) {
            return '**Prediction Threshold Explained:**\n\nHeartFL uses a binary classification threshold of **0.5** (50% probability).\n\n**How It Works:**\n• Model computes probability score (0-100%)\n• If score >= 50% ➡ **HIGH RISK**\n• If score < 50% ➡ **LOW RISK**\n\n**Clinical Implications:**\n🔴 **High Risk:** Recommend cardiology consultation, ECG, further tests\n🟢 **Low Risk:** Routine check-up, healthy lifestyle recommended\n\n**Why 0.5?**\n• Balances sensitivity and specificity\n• Minimizes false positives and false negatives\n• Standard practice in medical ML\n\n⚠️ **HEALTH REMINDER:**\n✅ Use this for **screening guidance only**\n✅ Results assist healthcare professionals\n✅ Not diagnostic - consult doctors for final decisions\n\n**Future Enhancement:**\n• May allow threshold adjustment per hospital policy\n• Risk bands (low/medium/high) could be added';
        }

        if (
            lowerMessage.includes('theme') ||
            (lowerMessage.includes('dark') && lowerMessage.includes('light'))
        ) {
            return '**Theme Customization:**\n\nHeartFL features a **Dual Theme System** for optimal viewing:\n\n🔷 **Light Blue Mode** (Default)\n• Professional light blue background (#E3F2FD)\n• Easy reading in bright environments\n• Less eye strain during daytime\n\n🌙 **Dark Green Mode**\n• Calming dark green background (#1B4332)\n• Better for night-time use\n• Reduced blue light emission\n\n**How to Customize:**\n1. Click your username in top menu\n2. Select **Settings**\n3. Choose custom colors for each theme\n4. Select preferred default: Light, Dark, or Auto\n5. Click **Save Settings**\n\nYour preference saves automatically. Toggle theme anytime with the moon/sun button.';
        }
        
        if (lowerMessage.includes('dashboard')) {
            return 'The **Dashboard** shows your personal information and prediction history. You can view past predictions, update your profile, and manage your account settings. Access it by clicking on your username in the top menu.';
        }
        
        if (lowerMessage.includes('thank') || lowerMessage.includes('thanks')) {
            return 'You\'re welcome! I\'m here to help. Feel free to ask me anything about HeartFL, federated learning, or how to use our platform.';
        }
        
        if (lowerMessage.includes('hi') || lowerMessage.includes('hello') || lowerMessage.includes('hey')) {
            return 'Hello! I\'m here to help with **HeartFL**. I can assist with:\n\n• **Why Use HeartFL** - Privacy protection & clinical benefits\n• **Architecture** - How the system works end-to-end\n• **Federated Learning** - Privacy-preserving ML technology\n• **Making Predictions** - Feature details & model threshold\n• **Hospital Operations** - Dataset upload & verification\n• **Admin Dashboard** - Verify doctors/hospitals, manage database\n• **PDF Reports** - How to generate clinical reports\n• **Developers** - Meet the team (Guided by Y. Suresh Kumar, Built by Aditya, Suresh, Jnanadeep, Hemanth)\n• **Technical Issues** - Bugs or problems\n\n📍 **Note**: This is a research project for hospitals and doctors. Use for reference and learning.\n\nWhat would you like to know about?';
        }
        
        // Default response
        return 'I\'m here to help with **HeartFL**. I can assist you with:\n\n• **Why Use HeartFL** - Privacy protection & accuracy benefits\n• **Architecture & Design** - System components & data flow\n• **Federated Learning** - Privacy-preserving ML approach\n• **Making Predictions** - Clinical features, model, threshold explained\n• **Hospital Operations** - How to upload datasets & get verified\n• **Admin Dashboard** - Verify doctors/hospitals, manage database, contact messages\n• **PDF Reports** - Generate clinical reports for consultations\n• **Model Performance** - Accuracy, metrics, and limitations\n• **Developers** - Team (Guided by Y. Suresh Kumar; Built by Aditya, Suresh, Jnanadeep, Hemanth)\n• **Technical Issues** - Bugs or feature questions\n\n⚕️ **IMPORTANT**: This application is for **research, educational, and hospital testing purposes only**. It is not yet a complete enterprise application. Always consult healthcare professionals for medical decisions.\n\nWhat would you like to know more about?';
    }
}

// Initialize chatbot
document.addEventListener('DOMContentLoaded', function() {
    window.heartFLChatbot = new HeartFLChatbot();
});
