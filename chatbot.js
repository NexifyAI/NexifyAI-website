/**
 * NexifyAI Smart Chatbot Widget
 * 7x24 AI customer support with automatic lead collection & multi-language support
 * 
 * Usage: <script src="chatbot.js" data-api-url="YOUR_WORKER_URL" data-brand="NexifyAI"></script>
 */

(function() {
  'use strict';

  // ========== Configuration ==========
  const config = {
    brandName: 'NexifyAI',
    primaryColor: '#6366f1',
    bubbleSize: 60,
    chatWidth: 380,
    chatHeight: 560,
    positionBottom: 24,
    positionRight: 24,
    greetingMessage: "Hi there! 👋 I'm the NexifyAI assistant. How can I help protect your brand today?",
    typingSpeed: 30 // ms per character simulation
  };

  // Read config from script tag data attributes
  const scriptTag = document.currentScript;
  if (scriptTag) {
    if (scriptTag.dataset.brand) config.brandName = scriptTag.dataset.brand;
    if (scriptTag.dataset.primaryColor) config.primaryColor = scriptTag.dataset.primaryColor;
    if (scriptTag.dataset.apiUrl) config.apiUrl = scriptTag.dataset.apiUrl;
    if (scriptTag.dataset.greeting) config.greetingMessage = scriptTag.dataset.greeting;
  }

  // ========== State ==========
  let isOpen = false;
  let messages = [];
  let collectedLead = {};
  let leadSubmitted = false;

  // ========== DOM Elements ==========
  let bubble, chatWindow, chatMessages, chatInput, chatSendBtn;

  // ========== Initialize ==========
  function init() {
    injectStyles();
    createBubble();
    createChatWindow();
  }

  // ========== Styles ==========
  function injectStyles() {
    const styles = `
      #nexify-chatbot-bubble {
        position: fixed;
        bottom: ${config.positionBottom}px;
        right: ${config.positionRight}px;
        width: ${config.bubbleSize}px;
        height: ${config.bubbleSize}px;
        border-radius: 50%;
        background: linear-gradient(135deg, ${config.primaryColor}, #8b5cf6);
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 99999;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      }
      #nexify-chatbot-bubble:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 24px rgba(99, 102, 241, 0.5);
      }
      #nexify-chatbot-bubble svg {
        width: 28px;
        height: 28px;
        color: white;
      }
      #nexify-chatbot-window {
        position: fixed;
        bottom: ${config.positionBottom + config.bubbleSize + 16}px;
        right: ${config.positionRight}px;
        width: ${config.chatWidth}px;
        height: ${config.chatHeight}px;
        max-height: calc(100vh - 120px);
        background: #ffffff;
        border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        display: none;
        flex-direction: column;
        overflow: hidden;
        z-index: 99999;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        animation: slideUp 0.3s ease;
      }
      #nexify-chatbot-window.open {
        display: flex;
      }
      @keyframes slideUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
      }
      .nexify-chat-header {
        padding: 16px 20px;
        background: linear-gradient(135deg, ${config.primaryColor}, #8b5cf6);
        color: white;
        display: flex;
        align-items: center;
        justify-content: space-between;
      }
      .nexify-chat-header-title {
        font-weight: 600;
        font-size: 15px;
        display: flex;
        align-items: center;
        gap: 8px;
      }
      .nexify-chat-header-status {
        width: 8px;
        height: 8px;
        background: #4ade80;
        border-radius: 50%;
        animation: pulse 2s infinite;
      }
      @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
      }
      .nexify-chat-close {
        background: none;
        border: none;
        color: white;
        font-size: 20px;
        cursor: pointer;
        padding: 0 4px;
        opacity: 0.8;
      }
      .nexify-chat-close:hover { opacity: 1; }
      .nexify-chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: 16px;
        background: #f8fafc;
        display: flex;
        flex-direction: column;
        gap: 12px;
      }
      .nexify-chat-messages::-webkit-scrollbar { width: 6px; }
      .nexify-chat-messages::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 3px;
      }
      .nexify-msg {
        max-width: 85%;
        padding: 10px 14px;
        border-radius: 14px;
        font-size: 14px;
        line-height: 1.5;
        word-wrap: break-word;
      }
      .nexify-msg.bot {
        background: white;
        color: #1e293b;
        border-bottom-left-radius: 4px;
        align-self: flex-start;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
      }
      .nexify-msg.user {
        background: ${config.primaryColor};
        color: white;
        border-bottom-right-radius: 4px;
        align-self: flex-end;
      }
      .nexify-typing {
        display: flex;
        gap: 4px;
        padding: 10px 14px;
        background: white;
        border-radius: 14px;
        border-bottom-left-radius: 4px;
        align-self: flex-start;
        width: fit-content;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
      }
      .nexify-typing span {
        width: 8px;
        height: 8px;
        background: #94a3b8;
        border-radius: 50%;
        animation: bounce 1.4s infinite;
      }
      .nexify-typing span:nth-child(2) { animation-delay: 0.2s; }
      .nexify-typing span:nth-child(3) { animation-delay: 0.4s; }
      @keyframes bounce {
        0%, 60%, 100% { transform: translateY(0); }
        30% { transform: translateY(-6px); }
      }
      .nexify-chat-input-area {
        padding: 12px 16px;
        background: white;
        border-top: 1px solid #e2e8f0;
        display: flex;
        gap: 8px;
      }
      .nexify-chat-input {
        flex: 1;
        padding: 10px 14px;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        font-size: 14px;
        outline: none;
        font-family: inherit;
        transition: border-color 0.2s;
      }
      .nexify-chat-input:focus { border-color: ${config.primaryColor}; }
      .nexify-chat-send {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: ${config.primaryColor};
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        transition: opacity 0.2s;
      }
      .nexify-chat-send:hover { opacity: 0.9; }
      .nexify-chat-send:disabled { opacity: 0.5; cursor: not-allowed; }
      .nexify-chat-send svg { width: 18px; height: 18px; }
      .nexify-powered {
        text-align: center;
        font-size: 11px;
        color: #94a3b8;
        padding: 6px;
        background: white;
        border-top: 1px solid #f1f5f9;
      }
      .nexify-powered a { color: ${config.primaryColor}; text-decoration: none; }

      @media (max-width: 480px) {
        #nexify-chatbot-window {
          width: calc(100vw - 32px);
          right: 16px;
          left: 16px;
          height: 70vh;
        }
      }
    `;
    const styleSheet = document.createElement('style');
    styleSheet.textContent = styles;
    document.head.appendChild(styleSheet);
  }

  // ========== Bubble ==========
  function createBubble() {
    bubble = document.createElement('div');
    bubble.id = 'nexify-chatbot-bubble';
    bubble.innerHTML = `
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
      </svg>
    `;
    bubble.addEventListener('click', toggleChat);
    document.body.appendChild(bubble);
  }

  // ========== Chat Window ==========
  function createChatWindow() {
    chatWindow = document.createElement('div');
    chatWindow.id = 'nexify-chatbot-window';
    chatWindow.innerHTML = `
      <div class="nexify-chat-header">
        <div class="nexify-chat-header-title">
          <span class="nexify-chat-header-status"></span>
          ${config.brandName} Assistant
        </div>
        <button class="nexify-chat-close">×</button>
      </div>
      <div class="nexify-chat-messages" id="nexify-chat-messages"></div>
      <div class="nexify-chat-input-area">
        <input type="text" class="nexify-chat-input" id="nexify-chat-input" placeholder="Type your message..." />
        <button class="nexify-chat-send" id="nexify-chat-send">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </div>
      <div class="nexify-powered">Powered by <a href="https://nexifyai.com" target="_blank">NexifyAI</a></div>
    `;
    document.body.appendChild(chatWindow);

    chatMessages = document.getElementById('nexify-chat-messages');
    chatInput = document.getElementById('nexify-chat-input');
    chatSendBtn = document.getElementById('nexify-chat-send');

    chatWindow.querySelector('.nexify-chat-close').addEventListener('click', toggleChat);
    chatSendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });
  }

  function toggleChat() {
    isOpen = !isOpen;
    chatWindow.classList.toggle('open', isOpen);
    if (isOpen) {
      chatInput.focus();
      if (messages.length === 0) {
        addBotMessage(config.greetingMessage);
      }
    }
  }

  // ========== Messages ==========
  function addUserMessage(text) {
    const msg = document.createElement('div');
    msg.className = 'nexify-msg user';
    msg.textContent = text;
    chatMessages.appendChild(msg);
    messages.push({ role: 'user', content: text });
    scrollToBottom();
  }

  function addBotMessage(text) {
    const msg = document.createElement('div');
    msg.className = 'nexify-msg bot';
    msg.textContent = text;
    chatMessages.appendChild(msg);
    messages.push({ role: 'assistant', content: text });
    scrollToBottom();
  }

  function showTyping() {
    const typing = document.createElement('div');
    typing.className = 'nexify-typing';
    typing.id = 'nexify-typing-indicator';
    typing.innerHTML = '<span></span><span></span><span></span>';
    chatMessages.appendChild(typing);
    scrollToBottom();
  }

  function hideTyping() {
    const typing = document.getElementById('nexify-typing-indicator');
    if (typing) typing.remove();
  }

  function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  // ========== API Call ==========
  async function callAI(userMessage) {
    if (!config.apiUrl) {
      return "⚠️ API URL not configured. Please set data-api-url attribute on the script tag.";
    }

    try {
      const response = await fetch(config.apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: messages,
          collectedLead: collectedLead,
          brandName: config.brandName
        })
      });

      if (!response.ok) throw new Error('API call failed');
      
      const data = await response.json();
      
      // Update collected lead data
      if (data.collectedLead) {
        collectedLead = { ...collectedLead, ...data.collectedLead };
      }
      
      // If lead is complete, trigger webhook
      if (data.leadComplete && !leadSubmitted) {
        leadSubmitted = true;
        submitLead(data.collectedLead);
      }

      return data.reply;
    } catch (error) {
      console.error('Chatbot API error:', error);
      return "Sorry, I'm having trouble connecting right now. Please try again later or email us directly.";
    }
  }

  function submitLead(leadData) {
    // Send lead to webhook if configured
    if (config.webhookUrl) {
      fetch(config.webhookUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lead: leadData,
          timestamp: new Date().toISOString(),
          source: window.location.href,
          userAgent: navigator.userAgent
        })
      }).catch(err => console.error('Lead submission error:', err));
    }
    
    // Also store locally for backup
    const leads = JSON.parse(localStorage.getItem('nexify_leads') || '[]');
    leads.push({
      ...leadData,
      timestamp: new Date().toISOString(),
      source: window.location.href
    });
    localStorage.setItem('nexify_leads', JSON.stringify(leads));
  }

  // ========== Send Message ==========
  async function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    chatInput.value = '';
    chatSendBtn.disabled = true;

    addUserMessage(text);
    showTyping();

    const reply = await callAI(text);
    
    hideTyping();
    addBotMessage(reply);

    chatSendBtn.disabled = false;
    chatInput.focus();
  }

  // Programmatically send a message
  async function sendUserMessage(text) {
    if (!text) return;
    chatSendBtn.disabled = true;

    addUserMessage(text);
    showTyping();

    const reply = await callAI(text);

    hideTyping();
    addBotMessage(reply);

    chatSendBtn.disabled = false;
    if (isOpen) chatInput.focus();
  }

  // Start demo flow — open chat & trigger lead collection
  async function startDemoFlow() {
    if (!isOpen) {
      toggleChat();
      await new Promise(r => setTimeout(r, 100));
    }

    const lang = detectLanguage();
    const demoMessages = {
      en: "I'd like to book a demo",
      nl: "Ik wil een demo boeken",
      fr: "Je voudrais réserver une démo",
      es: "Me gustaría reservar una demo",
      zh: "我想预约一个演示"
    };

    if (messages.length <= 1) {
      if (messages.length === 1 && messages[0].role === 'assistant') {
        chatMessages.removeChild(chatMessages.lastElementChild);
        messages.pop();
      }
      sendUserMessage(demoMessages[lang] || demoMessages.en);
    } else {
      chatInput.focus();
    }
  }

  // ========== Expose API ==========
  window.NexifyChatbot = {
    open: () => { if (!isOpen) toggleChat(); },
    close: () => { if (isOpen) toggleChat(); },
    startDemo: startDemoFlow,
    sendMessage: sendUserMessage,
    getLead: () => collectedLead,
    getMessages: () => messages
  };

  // ========== Auto-init ==========
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
