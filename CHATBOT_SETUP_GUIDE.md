# HeartFL Chatbot Integration Guide

## 🎯 Overview
This guide will help you integrate an AI/LLM API with your HeartFL chatbot to enable intelligent conversations.

---

## 📋 Table of Contents
1. [Quick Start](#quick-start)
2. [Troubleshooting Buttons](#troubleshooting-buttons)
3. [API Integration Options](#api-integration-options)
4. [Step-by-Step Setup by Provider](#step-by-step-setup)
5. [Testing the Chatbot](#testing)
6. [Common Issues](#common-issues)

---

## 🚀 Quick Start

### Step 1: Clear Browser Cache
The buttons may not work due to browser caching. Clear your cache:
1. Press `Ctrl + Shift + Delete` (Windows) or `Cmd + Shift + Delete` (Mac)
2. Select "Cached images and files"
3. Click "Clear data"
4. **OR** do a hard refresh: `Ctrl + F5` (Windows) or `Cmd + Shift + R` (Mac)

### Step 2: Restart Django Server
```bash
# In your terminal running the server, press Ctrl+C
# Then restart:
cd heartfl
python manage.py runserver
```

### Step 3: Collect Static Files (Important!)
```bash
# Stop the server first (Ctrl+C)
cd heartfl
python manage.py collectstatic --clear --noinput
python manage.py runserver
```

---

## 🔧 Troubleshooting Buttons

### If Chatbot/Page Navigation Buttons Still Don't Work:

#### Option 1: Check Console for Errors
1. Open browser Developer Tools: `F12` or `Right-click > Inspect`
2. Go to "Console" tab
3. Look for errors (red text)
4. Share any errors you see for further help

#### Option 2: Verify Elements are Present
Open Console and type:
```javascript
console.log('Chatbot toggle:', document.getElementById('chatbotToggle'));
console.log('Page up button:', document.getElementById('pageUpBtn'));
console.log('Page down button:', document.getElementById('pageDownBtn'));
```

If any return `null`, the HTML elements aren't loading properly.

#### Option 3: Force Reload JavaScript
Add version parameter to force reload:
```html
<!-- In base.html, change this: -->
<script src="{% static 'js/main.js' %}"></script>
<!-- To this: -->
<script src="{% static 'js/main.js' %}?v=2.0"></script>
```

---

## 🤖 API Integration Options

### Option 1: OpenAI (ChatGPT) - Recommended for Best Quality
- **Cost**: Pay-as-you-go (~$0.002 per response with GPT-3.5)
- **Quality**: Excellent
- **Speed**: Fast
- **Get API Key**: https://platform.openai.com/api-keys

### Option 2: Groq - Recommended for FREE & FAST
- **Cost**: FREE (with rate limits)
- **Quality**: Very Good
- **Speed**: Ultra-Fast
- **Get API Key**: https://console.groq.com/keys

### Option 3: Anthropic Claude - Great Alternative
- **Cost**: Pay-as-you-go
- **Quality**: Excellent
- **Speed**: Fast
- **Get API Key**: https://console.anthropic.com/

### Option 4: Local LLM (Ollama) - FREE & Private
- **Cost**: FREE
- **Quality**: Good
- **Speed**: Depends on hardware
- **Setup**: Runs on your computer

### Option 5: Offline Mode (Default)
- Uses keyword-based responses
- No API required
- Works immediately

---

## 📝 Step-by-Step Setup

### OPTION A: Using Groq (FREE - Recommended!)

#### Step 1: Get Groq API Key
1. Go to https://console.groq.com
2. Sign up for free account
3. Navigate to "API Keys" section
4. Click "Create API Key"
5. Copy the key (starts with `gsk_...`)

#### Step 2: Configure Chatbot
1. Open file: `heartfl/static/js/chatbot-config.js`
2. Find line 10:
   ```javascript
   provider: 'offline',  // Change this to your preferred provider
   ```
3. Change to:
   ```javascript
   provider: 'groq',  // Using Groq API
   ```

4. Find line 45:
   ```javascript
   apiKey: 'YOUR_GROQ_API_KEY_HERE',
   ```
5. Replace with your actual API key:
   ```javascript
   apiKey: 'gsk_your_actual_key_here',
   ```

#### Step 3: Save and Test
1. Save the file
2. Clear browser cache (`Ctrl + F5`)
3. Reload the page
4. Open chatbot and try a message!

---

### OPTION B: Using OpenAI (ChatGPT)

#### Step 1: Get OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-...`)
5. Add credits to your account: https://platform.openai.com/account/billing

#### Step 2: Configure Chatbot
1. Open: `heartfl/static/js/chatbot-config.js`
2. Change line 10:
   ```javascript
   provider: 'openai',
   ```
3. Update line 17:
   ```javascript
   apiKey: 'sk-your_actual_openai_key_here',
   ```

#### Step 3: Choose Model (Optional)
Line 18:
```javascript
model: 'gpt-3.5-turbo',  // Cheaper, faster
// OR
model: 'gpt-4-turbo-preview',  // Better quality, more expensive
```

#### Step 4: Save and Test
1. Save the file
2. Clear browser cache
3. Test the chatbot!

---

### OPTION C: Using Local LLM (Ollama) - FREE!

#### Step 1: Install Ollama
1. Download from: https://ollama.ai/download
2. Install on your computer
3. Open terminal and pull a model:
   ```bash
   ollama pull llama2
   # OR for better quality:
   ollama pull mistral
   ```

#### Step 2: Start Ollama Server
```bash
ollama serve
```
Keep this terminal running!

#### Step 3: Configure Chatbot
1. Open: `heartfl/static/js/chatbot-config.js`
2. Change line 10:
   ```javascript
   provider: 'local',
   ```
3. Verify line 58-59:
   ```javascript
   apiUrl: 'http://localhost:11434/api/chat',
   model: 'llama2',  // or 'mistral', 'phi', etc.
   ```

#### Step 4: Save and Test
1. Save the file
2. Keep Ollama server running
3. Reload webpage and test!

---

### OPTION D: Using Anthropic Claude

#### Step 1: Get Claude API Key
1. Go to https://console.anthropic.com
2. Sign up and add billing
3. Go to "API Keys"
4. Create new key
5. Copy the key

#### Step 2: Configure Chatbot
1. Open: `heartfl/static/js/chatbot-config.js`
2. Change line 10:
   ```javascript
   provider: 'anthropic',
   ```
3. Update line 29:
   ```javascript
   apiKey: 'sk-ant-your_actual_key_here',
   ```

#### Step 3: Save and Test

---

## 🧪 Testing the Chatbot

### Test Messages to Try:
1. "How do I make a prediction?"
2. "What is federated learning?"
3. "I'm having an issue with the website"
4. "Tell me about heart disease risk factors"
5. "How does the FL Dashboard work?"

### Expected Behavior:
- ✅ Chatbot toggle button pulses with animation
- ✅ Chat window opens when clicked
- ✅ Messages appear with typing indicator
- ✅ Responses are relevant and helpful
- ✅ Page up/down buttons appear when scrolling

---

## ❗ Common Issues & Solutions

### Issue 1: "Buttons appear but don't respond to clicks"

**Solution A: Check Static Files**
```bash
cd heartfl
python manage.py collectstatic --clear --noinput
```

**Solution B: Hard Refresh**
- Windows: `Ctrl + F5`
- Mac: `Cmd + Shift + R`

**Solution C: Check Browser Console**
- Press `F12`
- Look for JavaScript errors
- Fix any errors shown

---

### Issue 2: "Chatbot responds but with generic/offline responses"

**Cause**: API not configured or API key invalid

**Solution**:
1. Verify `provider` is set correctly in `chatbot-config.js`
2. Check API key is correct (no spaces, complete key)
3. Open browser console (`F12`) and look for API errors
4. Check API account has credits (for paid APIs)

---

### Issue 3: "API Error in console"

**OpenAI Errors**:
- `401 Unauthorized`: Invalid API key
- `429 Rate Limit`: Too many requests, wait or upgrade plan
- `insufficient_quota`: Add credits to account

**Groq Errors**:
- `401`: Invalid API key
- `429`: Free tier rate limit, wait 60 seconds

**Solution**:
1. Verify API key is correct
2. Check account status on provider website
3. Add billing/credits if needed
4. Switch to `offline` provider temporarily

---

### Issue 4: "Page navigation buttons don't appear"

**Solution**:
1. Scroll down the page (buttons appear after 300px scroll)
2. Check browser console for errors
3. Verify theme.css is loaded (check Network tab in F12)
4. Clear cache and hard refresh

---

### Issue 5: "Chatbot window is blank/white"

**Cause**: CSS not loading properly

**Solution**:
```bash
cd heartfl
python manage.py collectstatic --clear --noinput
python manage.py runserver
```
Then hard refresh browser: `Ctrl + F5`

---

## 🔍 Advanced Configuration

### Customize System Prompt
Edit the `systemPrompt` in `chatbot-config.js` to change chatbot behavior:

```javascript
systemPrompt: `You are Dr. HeartFL, a cardiologist AI assistant...
- Always prioritize heart health
- Explain medical terms simply
- Be encouraging and supportive`
```

### Adjust Response Length
Change `maxTokens` value:
```javascript
maxTokens: 500,  // Shorter responses
// OR
maxTokens: 1000, // Longer, detailed responses
```

### Change Response Style
Modify `temperature`:
```javascript
temperature: 0.3,  // More focused, consistent
// OR
temperature: 0.9,  // More creative, varied
```

---

## 📊 Monitoring & Debugging

### Enable Detailed Logging
In `chatbot-config.js`:
```javascript
enableLogging: true,
```

Then check browser console (`F12`) for:
- API requests
- Response times
- Errors
- Message history

### Test API Connection
Open browser console (`F12`) and run:
```javascript
// Test if chatbot is initialized
console.log(window.heartFLChatbot);

// Test if config is loaded
console.log(window.CHATBOT_CONFIG);

// Manually trigger test
window.heartFLChatbot.sendMessage();
```

---

## 💡 Best Practices

### 1. Start with Groq (Free Tier)
- No cost
- Fast responses
- Easy setup
- Good for testing

### 2. Use Offline Mode During Development
```javascript
provider: 'offline',
```
- No API costs
- Instant responses
- Works offline

### 3. Monitor API Usage
- Check provider dashboard regularly
- Set up billing alerts
- Use rate limiting

### 4. Handle Errors Gracefully
The chatbot automatically falls back to offline mode if API fails.

---

## 🎓 Next Steps

After getting the chatbot working:

1. **Customize responses** in `chatbot-config.js`
2. **Add more triggers** in `generateOfflineResponse()` method
3. **Style the chatbot** by editing `theme.css`
4. **Add analytics** to track usage
5. **Create conversation flows** for common questions

---

## 📞 Need Help?

If buttons still don't work after following ALL troubleshooting steps:

1. **Check browser console** (`F12`) and copy any errors
2. **Verify file structure**:
   ```
   heartfl/
   └── static/
       └── js/
           ├── main.js
           ├── chatbot-config.js
           └── utils.js
   ```
3. **Run collectstatic** again
4. **Try different browser** (Chrome, Firefox, Edge)

---

## ✅ Checklist for Success

- [ ] Cleared browser cache
- [ ] Ran `collectstatic` command
- [ ] Restarted Django server
- [ ] Hard refreshed page (`Ctrl + F5`)
- [ ] Checked console for errors
- [ ] Configured API provider in `chatbot-config.js`
- [ ] Added valid API key
- [ ] Tested chatbot with sample message
- [ ] Verified page up/down buttons appear when scrolling

---

## 🎉 Success Indicators

You'll know everything works when:
- ✅ Chatbot button pulses in bottom-right
- ✅ Chat window opens smoothly
- ✅ Messages send and receive
- ✅ Typing indicator shows
- ✅ Responses are intelligent (if API configured)
- ✅ Page up button appears after scrolling down
- ✅ Page down button appears when not at bottom
- ✅ Smooth scroll animations work

---

**Good luck! Your chatbot is ready to help users navigate HeartFL! 🚀**
