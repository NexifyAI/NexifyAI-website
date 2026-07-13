/**
 * Nexify AI Chatbot - Cloudflare Worker
 * 
 * Smart customer service AI agent with multilingual support & lead collection.
 * Deploy to Cloudflare Workers, set environment variables.
 * 
 * ENV VARS:
 * - AI_PROVIDER: "gemini" | "groq" | "openai"  (default: gemini)
 * - AI_API_KEY: your API key
 * - AI_MODEL: (optional) model name, e.g. "gemini-2.0-flash" for Gemini
 * - LEAD_NOTIFY_EMAIL: (optional) email to notify when a lead is collected
 * - RESEND_API_KEY: (optional) required if LEAD_NOTIFY_EMAIL is set
 * - LEAD_WEBHOOK_URL: (optional) webhook URL for lead notifications
 */

const SYSTEM_PROMPT = `You are the friendly, professional AI assistant for Nexify AI — a smart customer service platform that provides 24/7 AI agents for businesses across chat, phone, and email.

YOUR PRIMARY GOAL: Have natural conversations with website visitors and gently guide them to share their information so our sales team can follow up. Collect these 5 pieces of information naturally through conversation:
1. Industry / what their business does
2. Company name
3. Contact person name
4. Email address
5. Brief description of their needs / challenges with customer service

NEXIFY AI KNOWLEDGE:
- What we do: 24/7 AI customer service agents that handle chat, phone calls, and emails
- Key features: 
  • 24/7 always-on operation (no sleep, no breaks, no missed calls)
  • 30+ languages with native fluency (auto-detection)
  • Launch in 7 days or less
  • Instant response time (< 1 second)
  • Captures every high-value lead and order
- Target customers: Restaurants, e-commerce, hotels, service businesses, any company with customer interactions
- Pricing: Flexible plans starting from a few hundred euros/month (tailored to needs)

IMPORTANT RULES:
1. LANGUAGE: ALWAYS reply in the SAME LANGUAGE as the user's last message. Auto-detect. Support: English, Dutch, French, Spanish, Chinese, German, Italian, Portuguese, and more. Never switch languages unless the user does.
2. NATURAL FLOW: Don't ask for all info at once like a form. Have a real conversation and collect info gradually. Ask max 1-2 questions per message.
3. TONE: Friendly, professional, helpful. Not robotic or salesy. Like a smart concierge.
4. LEAD COMPLETION: When you have ALL 5 pieces of info, confirm everything and tell them our team will reach out within 24 hours. Then set leadComplete to true.
5. If someone asks to speak to a human or says "talk to sales", collect their contact info and tell them someone will reach out shortly.
6. If someone is just browsing / exploring, answer their questions and naturally steer toward learning more about their business.

OUTPUT FORMAT - You MUST respond with valid JSON in this exact format:
{
  "reply": "your response to the user (in their language)",
  "collectedLead": {
    "industry": "value or null if not yet known",
    "companyName": "value or null if not yet known",
    "contactName": "value or null if not yet known",
    "email": "value or null if not yet known",
    "needsDescription": "value or null if not yet known"
  },
  "leadComplete": false
}

Only respond with the JSON object. No other text, no markdown, no code blocks.`;

export default {
  async fetch(request, env, ctx) {
    // CORS headers
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
        },
      });
    }

    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405 });
    }

    try {
      const body = await request.json();
      const { messages, collectedLead = {}, brandName = 'Nexify AI' } = body;

      if (!messages || !Array.isArray(messages)) {
        return new Response(JSON.stringify({ error: 'Invalid messages format' }), { status: 400 });
      }

      // Build the conversation for the AI
      const aiMessages = [
        { role: 'system', content: SYSTEM_PROMPT },
        ...messages.map(m => ({ role: m.role, content: m.content }))
      ];

      // Add current lead state to help AI track what's collected
      if (Object.keys(collectedLead).length > 0) {
        aiMessages.push({
          role: 'system',
          content: `Current collected lead data (update these fields as you gather more info): ${JSON.stringify(collectedLead)}`
        });
      }

      // Call AI provider
      const aiResponse = await callAI(aiMessages, env);

      // Parse the JSON response from AI
      let parsedResponse;
      try {
        const jsonMatch = aiResponse.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          parsedResponse = JSON.parse(jsonMatch[0]);
        } else {
          parsedResponse = JSON.parse(aiResponse);
        }
      } catch (parseError) {
        console.error('Failed to parse AI response as JSON:', aiResponse);
        parsedResponse = {
          reply: aiResponse,
          collectedLead: collectedLead,
          leadComplete: false
        };
      }

      // If lead is complete, send notifications (webhook + email)
      if (parsedResponse.leadComplete) {
        const ip = request.headers.get('CF-Connecting-IP');
        if (env.LEAD_WEBHOOK_URL) {
          ctx.waitUntil(sendToWebhook(env.LEAD_WEBHOOK_URL, parsedResponse.collectedLead, ip));
        }
        if (env.LEAD_NOTIFY_EMAIL && env.RESEND_API_KEY) {
          ctx.waitUntil(sendLeadEmail(env, parsedResponse.collectedLead, ip));
        }
      }

      return new Response(JSON.stringify(parsedResponse), {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
      });

    } catch (error) {
      console.error('Worker error:', error);
      return new Response(
        JSON.stringify({ error: 'Internal server error', reply: 'Sorry, something went wrong. Please try again later.' }),
        { status: 500, headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' } }
      );
    }
  }
};

async function callAI(messages, env) {
  const provider = env.AI_PROVIDER || 'gemini';
  const apiKey = env.AI_API_KEY;
  const model = env.AI_MODEL || getDefaultModel(provider);

  if (!apiKey) {
    throw new Error('AI_API_KEY not configured');
  }

  if (provider === 'gemini') {
    return callGemini(messages, apiKey, model);
  }

  // OpenAI-compatible providers (OpenAI, Groq, etc.)
  let apiUrl, headers;

  if (provider === 'openai') {
    apiUrl = 'https://api.openai.com/v1/chat/completions';
  } else if (provider === 'groq') {
    apiUrl = 'https://api.groq.com/openai/v1/chat/completions';
  } else {
    throw new Error(`Unsupported AI provider: ${provider}`);
  }

  headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${apiKey}`
  };

  const response = await fetch(apiUrl, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      model: model,
      messages: messages,
      temperature: 0.7,
      max_tokens: 1000,
      response_format: { type: "json_object" }
    })
  });

  if (!response.ok) {
    const errorText = await response.text();
    console.error(`AI API error (${response.status}):`, errorText);
    throw new Error(`AI API request failed: ${response.status}`);
  }

  const data = await response.json();
  return data.choices[0].message.content;
}

async function callGemini(messages, apiKey, model) {
  const url = `https://generativelanguage.googleapis.com/v1/models/${model}:generateContent?key=${apiKey}`;

  // Gemini format: separate system instruction from user/assistant messages
  const systemInstruction = messages.find(m => m.role === 'system');
  const chatMessages = messages
    .filter(m => m.role !== 'system')
    .map(m => ({
      role: m.role === 'assistant' ? 'model' : 'user',
      parts: [{ text: m.content }]
    }));

  const body = {
    contents: chatMessages,
    generationConfig: {
      temperature: 0.7,
      maxOutputTokens: 1000,
      responseMimeType: 'application/json'
    }
  };

  if (systemInstruction) {
    body.systemInstruction = {
      parts: [{ text: systemInstruction.content }]
    };
  }

  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });

  if (!response.ok) {
    const errorText = await response.text();
    console.error(`Gemini API error (${response.status}):`, errorText);
    throw new Error(`Gemini API request failed: ${response.status}`);
  }

  const data = await response.json();
  return data.candidates[0].content.parts[0].text;
}

function getDefaultModel(provider) {
  switch (provider) {
    case 'gemini': return 'gemini-2.0-flash';
    case 'groq': return 'llama-3.1-70b-versatile';
    case 'openai': return 'gpt-4o-mini';
    default: return 'gemini-2.0-flash';
  }
}

async function sendToWebhook(webhookUrl, leadData, ip) {
  try {
    await fetch(webhookUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        lead: leadData,
        timestamp: new Date().toISOString(),
        source: 'nexifyai-chatbot',
        ip: ip || 'unknown'
      })
    });
  } catch (e) {
    console.error('Webhook error:', e);
  }
}

async function sendLeadEmail(env, leadData, ip) {
  try {
    const lead = leadData || {};
    const time = new Date().toLocaleString('en-US', { timeZone: 'Europe/Amsterdam' });
    const subject = `🔔 New Lead: ${lead.companyName || lead.contactName || 'Unknown'} - ${lead.industry || 'N/A'}`;

    const html = `
      <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #2daa58, #78df97); padding: 24px; border-radius: 12px 12px 0 0;">
          <h2 style="color: white; margin: 0; font-size: 20px;">🔔 New Lead from Nexify AI Chatbot</h2>
        </div>
        <div style="background: #ffffff; border: 1px solid #e5e7eb; border-top: none; padding: 24px; border-radius: 0 0 12px 12px;">
          <table style="width: 100%; border-collapse: collapse;">
            <tr style="border-bottom: 1px solid #f0f0f0;">
              <td style="padding: 10px 0; font-weight: 600; color: #51705d; width: 35%;">🏢 Industry</td>
              <td style="padding: 10px 0; color: #153122;">${lead.industry || '—'}</td>
            </tr>
            <tr style="border-bottom: 1px solid #f0f0f0;">
              <td style="padding: 10px 0; font-weight: 600; color: #51705d;">🏪 Company</td>
              <td style="padding: 10px 0; color: #153122;">${lead.companyName || '—'}</td>
            </tr>
            <tr style="border-bottom: 1px solid #f0f0f0;">
              <td style="padding: 10px 0; font-weight: 600; color: #51705d;">👤 Contact</td>
              <td style="padding: 10px 0; color: #153122;">${lead.contactName || '—'}</td>
            </tr>
            <tr style="border-bottom: 1px solid #f0f0f0;">
              <td style="padding: 10px 0; font-weight: 600; color: #51705d;">📧 Email</td>
              <td style="padding: 10px 0; color: #153122;">${lead.email || '—'}</td>
            </tr>
            <tr>
              <td style="padding: 10px 0; font-weight: 600; color: #51705d;">💡 Needs</td>
              <td style="padding: 10px 0; color: #153122;">${lead.needsDescription || '—'}</td>
            </tr>
          </table>
          <div style="margin-top: 20px; padding-top: 16px; border-top: 1px solid #e5e7eb; font-size: 13px; color: #86a191;">
            <div>🕐 Time: ${time} (CET)</div>
            <div>🌐 IP: ${ip || 'unknown'}</div>
            <div style="margin-top: 8px;">— Nexify AI Chatbot</div>
          </div>
        </div>
      </div>
    `;

    const text = `New Lead from Nexify AI Chatbot
===============================

Industry: ${lead.industry || '—'}
Company: ${lead.companyName || '—'}
Contact: ${lead.contactName || '—'}
Email: ${lead.email || '—'}
Needs: ${lead.needsDescription || '—'}

Time: ${time} (CET)
IP: ${ip || 'unknown'}
`;

    await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${env.RESEND_API_KEY}`
      },
      body: JSON.stringify({
        from: 'Nexify AI <onboarding@resend.dev>',
        to: [env.LEAD_NOTIFY_EMAIL],
        subject: subject,
        html: html,
        text: text
      })
    });
  } catch (e) {
    console.error('Email send error:', e);
  }
}
