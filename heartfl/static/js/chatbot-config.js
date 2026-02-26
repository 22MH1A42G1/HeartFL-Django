/**
 * HeartFL Chatbot Configuration
 * Configure your AI/LLM API settings here
 */

const CHATBOT_CONFIG = {
    // ==========================================
    // API PROVIDER SETTINGS
    // ==========================================
    // Options: 'openai', 'anthropic', 'groq', 'local', 'offline'
    provider: 'offline',  // Change this to your preferred provider
    
    // ==========================================
    // OPENAI CONFIGURATION
    // ==========================================
    openai: {
        apiKey: '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',  // Replace with your OpenAI API key
        model: 'gpt-4-turbo-preview',        // or 'gpt-3.5-turbo', 'gpt-4', etc.
        apiUrl: 'https://api.openai.com/v1/chat/completions',
        maxTokens: 500,
        temperature: 0.7,
        systemPrompt: `You are HeartFL AI Assistant, a helpful and knowledgeable assistant for a heart disease prediction platform that uses federated learning. 

Your role:
- Help users understand heart disease risk prediction
- Explain federated learning concepts in simple terms
- Guide users through the website navigation
- Assist with troubleshooting technical issues
- Answer questions about features and functionality

Be concise, friendly, and professional. Always prioritize user privacy and data security in your responses.`
    },
    
    // ==========================================
    // ANTHROPIC CLAUDE CONFIGURATION
    // ==========================================
    anthropic: {
        apiKey: 'YOUR_ANTHROPIC_API_KEY_HERE',  // Replace with your Anthropic API key
        model: 'claude-3-5-sonnet-20241022',     // or 'claude-3-opus', etc.
        apiUrl: 'https://api.anthropic.com/v1/messages',
        maxTokens: 500,
        temperature: 0.7,
        systemPrompt: 'You are HeartFL AI Assistant, helping users with heart disease prediction and federated learning.'
    },
    
    // ==========================================
    // GROQ CONFIGURATION (Fast & Free)
    // ==========================================
    groq: {
        apiKey: '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',  // Get free API key from https://console.groq.com
        model: 'mixtral-8x7b-32768',       // or 'llama3-70b-8192', 'gemma-7b-it'
        apiUrl: 'https://api.groq.com/openai/v1/chat/completions',
        maxTokens: 500,
        temperature: 0.7,
        systemPrompt: 'You are HeartFL AI Assistant for heart disease prediction and federated learning.'
    },
    
    // ==========================================
    // LOCAL LLM CONFIGURATION (Ollama, LM Studio, etc.)
    // ==========================================
    local: {
        apiUrl: 'http://localhost:11434/api/chat',  // Ollama default endpoint
        model: 'llama2',                            // or 'mistral', 'phi', etc.
        maxTokens: 500,
        temperature: 0.7,
        systemPrompt: 'You are HeartFL AI Assistant.'
    },
    
    // ==========================================
    // GENERAL SETTINGS
    // ==========================================
    enableLogging: true,           // Log API calls to console
    streamResponse: false,         // Stream responses (if supported)
    welcomeMessage: true,          // Show welcome message on open
    typingDelay: 1000,            // Typing indicator delay (ms)
    errorRetries: 2,              // Number of retry attempts on error
};

// Export configuration
window.CHATBOT_CONFIG = CHATBOT_CONFIG;
