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
4. LEAD COMPLETION: When you have ALL required info, confirm everything and tell them our team will reach out within 24 hours. Then set leadComplete to true.
5. If someone asks to speak to a human or says "talk to sales", collect their contact info and tell them someone will reach out shortly.
6. If someone is just browsing / exploring, answer their questions and naturally steer toward learning more about their business.

PILOT PROGRAM SPECIAL FLOW:
If the user mentions "pilot", "pilot program", "试点", "free trial", or expresses interest in joining the pilot (check the collectedLead.pilotApplication flag or user intent):
- You are handling a PILOT APPLICATION, not just a general inquiry.
- You MUST collect these 7 pieces of info before marking leadComplete:
  1. companyName — their company name
  2. industry — their industry / business type
  3. contactName — contact person name
  4. email — email address
  5. website — their company website URL
  6. challenges — their biggest customer service challenges / pain points
  7. volume — estimated monthly chat/call volume
- Include all 7 fields in collectedLead when leadComplete is true.
- Set pilotApplication: true in collectedLead.
- Still keep the conversation natural — don't ask all 7 at once. Spread them across the conversation.
- When complete, summarize the application and confirm: "Great! I've got everything we need. Our team will review your application and reach out within 24 hours. Excited to potentially work together! 🚀"

For general leads (not pilot), collect the standard 5 fields: industry, companyName, contactName, email, needsDescription.

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
          'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
        },
      });
    }

    // Health check endpoint
    const reqUrl = new URL(request.url);
    if (request.method === 'GET' && reqUrl.pathname === '/health') {
      const apiKey = env.AI_API_KEY;
      const provider = env.AI_PROVIDER || 'gemini';
      let aiStatus = 'unknown';
      let aiError = null;

      if (apiKey) {
        try {
          const testResponse = await callAI(
            [{ role: 'user', content: 'Please respond with a simple json object, e.g. {"status":"ok"}' }],
            env
          );
          aiStatus = testResponse ? 'ok' : 'no_response';
        } catch (e) {
          aiStatus = 'error';
          aiError = e.message;
        }
      } else {
        aiStatus = 'not_configured';
      }

      return new Response(JSON.stringify({
        status: 'healthy',
        ai: {
          provider: provider,
          model: env.AI_MODEL || getDefaultModel(provider),
          status: aiStatus,
          error: aiError
        },
        email: {
          notifyEmail: env.LEAD_NOTIFY_EMAIL ? 'configured' : 'not_configured',
          resendKey: env.RESEND_API_KEY ? 'configured' : 'not_configured'
        },
        timestamp: new Date().toISOString()
      }), {
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
      });
    }

    // Pilot application endpoint
    if (request.method === 'POST' && reqUrl.pathname === '/pilot-apply') {
      try {
        const body = await request.json();
        const ip = request.headers.get('CF-Connecting-IP');

        // Validate required fields
        const required = ['company', 'industry', 'name', 'email', 'website', 'challenges', 'volume'];
        const missing = required.filter(f => !body[f] || !body[f].toString().trim());
        if (missing.length > 0) {
          return new Response(JSON.stringify({ error: 'Missing required fields', missing }), {
            status: 400,
            headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
          });
        }

        // Send email notification
        if (env.LEAD_NOTIFY_EMAIL && env.RESEND_API_KEY) {
          ctx.waitUntil(sendPilotEmail(env, body, ip));
        }

        return new Response(JSON.stringify({ success: true, message: 'Application received' }), {
          status: 200,
          headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
        });
      } catch (e) {
        console.error('Pilot apply error:', e);
        return new Response(JSON.stringify({ error: 'Internal server error' }), {
          status: 500,
          headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
        });
      }
    }

    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405 });
    }

    const startTime = Date.now();

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
        const lead = parsedResponse.collectedLead || {};
        const isPilot = lead.pilotApplication === true || lead.pilotApplication === 'true';

        if (env.LEAD_WEBHOOK_URL) {
          ctx.waitUntil(sendToWebhook(env.LEAD_WEBHOOK_URL, lead, ip));
        }

        if (env.LEAD_NOTIFY_EMAIL && env.RESEND_API_KEY) {
          if (isPilot) {
            // Map AI field names to pilot email field names
            const pilotData = {
              company: lead.companyName || lead.company || '—',
              industry: lead.industry || '—',
              name: lead.contactName || lead.name || '—',
              email: lead.email || '—',
              website: lead.website || '—',
              challenges: lead.challenges || lead.needsDescription || '—',
              volume: lead.volume || '—'
            };
            ctx.waitUntil(sendPilotEmail(env, pilotData, ip));
          } else {
            ctx.waitUntil(sendLeadEmail(env, lead, ip));
          }
        }
      }

      const duration = Date.now() - startTime;
      const leadCount = parsedResponse.leadComplete ? 1 : 0;
      console.log(`Chat request completed in ${duration}ms, leadComplete=${leadCount}`);

      return new Response(JSON.stringify(parsedResponse), {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
      });

    } catch (error) {
      const duration = Date.now() - startTime;
      console.error(`Worker error after ${duration}ms:`, error.message || error);

      // Classify error type for better debugging
      let errorType = 'unknown';
      let userMessage = 'Sorry, something went wrong. Please try again later.';

      const msg = (error.message || '').toLowerCase();
      if (msg.includes('api key') || msg.includes('apikey') || msg.includes('authentication') || msg.includes('401') || msg.includes('403')) {
        errorType = 'auth_error';
        userMessage = 'AI service configuration error. Please try again later.';
      } else if (msg.includes('not found') || msg.includes('404') || msg.includes('model')) {
        errorType = 'model_error';
        userMessage = 'AI model not available. Please try again later.';
      } else if (msg.includes('timeout') || msg.includes('abort') || msg.includes('network')) {
        errorType = 'network_error';
        userMessage = 'AI service timed out. Please try again.';
      } else if (msg.includes('safety') || msg.includes('blocked') || msg.includes('content')) {
        errorType = 'safety_filter';
        userMessage = 'Sorry, I cannot help with that request.';
      }

      return new Response(
        JSON.stringify({
          error: errorType,
          errorDetail: error.message || 'Internal server error',
          reply: userMessage
        }),
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

  // For providers that don't support system messages well (e.g. Groq/Llama),
  // prepend system content to the first user message
  let finalMessages = messages;
  if (provider === 'groq') {
    const systemMsgs = messages.filter(m => m.role === 'system');
    const systemText = systemMsgs.map(m => m.content).join('\n\n');
    if (systemText) {
      finalMessages = messages.filter(m => m.role !== 'system');
      // Ensure first message is from user
      if (finalMessages.length === 0 || finalMessages[0].role !== 'user') {
        finalMessages.unshift({ role: 'user', content: systemText });
      } else {
        finalMessages[0].content = systemText + '\n\n' + finalMessages[0].content;
      }
    }
  }

  const response = await fetch(apiUrl, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      model: model,
      messages: finalMessages,
      temperature: 0.7,
      max_tokens: 1000,
      response_format: { type: "json_object" }
    })
  });

  if (!response.ok) {
    const errorText = await response.text();
    console.error(`AI API error (${response.status}):`, errorText);
    throw new Error(`AI API request failed: ${response.status} - ${errorText.substring(0, 300)}`);
  }

  const data = await response.json();
  return data.choices[0].message.content;
}

async function callGemini(messages, apiKey, model) {
  const url = `https://generativelanguage.googleapis.com/v1/models/${model}:generateContent?key=${apiKey}`;

  // Collect all system messages
  const systemMsgs = messages.filter(m => m.role === 'system');
  const systemText = systemMsgs.map(m => m.content).join('\n\n');

  // Convert chat messages to Gemini format
  const chatMessages = messages
    .filter(m => m.role !== 'system')
    .map(m => ({
      role: m.role === 'assistant' ? 'model' : 'user',
      parts: [{ text: m.content }]
    }));

  // Gemini v1 API does NOT support systemInstruction field.
  // Prepend system prompt to the first user message instead.
  if (systemText && chatMessages.length > 0) {
    const firstUserMsg = chatMessages.find(m => m.role === 'user');
    if (firstUserMsg) {
      firstUserMsg.parts[0].text = systemText + '\n\n' + firstUserMsg.parts[0].text;
    } else {
      // No user message yet, create one with system prompt
      chatMessages.unshift({
        role: 'user',
        parts: [{ text: systemText }]
      });
    }
  } else if (systemText && chatMessages.length === 0) {
    chatMessages.push({
      role: 'user',
      parts: [{ text: systemText }]
    });
  }

  const body = {
    contents: chatMessages,
    generationConfig: {
      temperature: 0.7,
      maxOutputTokens: 1000
    }
  };

  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });

  if (!response.ok) {
    const errorText = await response.text();
    console.error(`Gemini API error (${response.status}):`, errorText);
    throw new Error(`Gemini API request failed with status ${response.status}: ${errorText.substring(0, 200)}`);
  }

  const data = await response.json();

  // Handle safety filter / blocked content
  if (!data.candidates || data.candidates.length === 0) {
    const finishReason = data.promptFeedback?.blockReason || 'unknown';
    console.warn('Gemini response blocked, reason:', finishReason);
    throw new Error(`Content blocked by safety filter: ${finishReason}`);
  }

  const candidate = data.candidates[0];
  // Handle case where content is undefined (safety filter on output)
  if (!candidate.content || !candidate.content.parts || candidate.content.parts.length === 0) {
    const finishReason = candidate.finishReason || 'unknown';
    console.warn('Gemini candidate has no content, finishReason:', finishReason);
    throw new Error(`No content in response, finishReason: ${finishReason}`);
  }

  return candidate.content.parts[0].text;
}

function getDefaultModel(provider) {
  switch (provider) {
    case 'gemini': return 'gemini-2.0-flash';
    case 'groq': return 'llama-3.3-70b-versatile';
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

async function sendPilotEmail(env, formData, ip) {
  try {
    const time = new Date().toLocaleString('en-US', { timeZone: 'Europe/Amsterdam' });
    const subject = `🚀 New Pilot Application: ${formData.company || 'Unknown Company'} - ${formData.industry || 'N/A'}`;

    const html = `
      <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #2daa58, #78df97); padding: 24px; border-radius: 12px 12px 0 0;">
          <h2 style="color: white; margin: 0; font-size: 20px;">🚀 New Pilot Program Application</h2>
        </div>
        <div style="background: #ffffff; border: 1px solid #e5e7eb; border-top: none; padding: 24px; border-radius: 0 0 12px 12px;">
          <table style="width: 100%; border-collapse: collapse;">
            <tr style="border-bottom: 1px solid #f0f0f0;">
              <td style="padding: 10px 0; font-weight: 600; color: #51705d; width: 35%;">🏢 Company</td>
              <td style="padding: 10px 0; color: #153122;">${formData.company || '—'}</td>
            </tr>
            <tr style="border-bottom: 1px solid #f0f0f0;">
              <td style="padding: 10px 0; font-weight: 600; color: #51705d;">🏭 Industry</td>
              <td style="padding: 10px 0; color: #153122;">${formData.industry || '—'}</td>
            </tr>
            <tr style="border-bottom: 1px solid #f0f0f0;">
              <td style="padding: 10px 0; font-weight: 600; color: #51705d;">👤 Contact Name</td>
              <td style="padding: 10px 0; color: #153122;">${formData.name || '—'}</td>
            </tr>
            <tr style="border-bottom: 1px solid #f0f0f0;">
              <td style="padding: 10px 0; font-weight: 600; color: #51705d;">📧 Email</td>
              <td style="padding: 10px 0; color: #153122;"><a href="mailto:${formData.email || ''}">${formData.email || '—'}</a></td>
            </tr>
            <tr style="border-bottom: 1px solid #f0f0f0;">
              <td style="padding: 10px 0; font-weight: 600; color: #51705d;">🌐 Website</td>
              <td style="padding: 10px 0; color: #153122;">${formData.website || '—'}</td>
            </tr>
            <tr style="border-bottom: 1px solid #f0f0f0;">
              <td style="padding: 10px 0; font-weight: 600; color: #51705d;">💬 Challenges</td>
              <td style="padding: 10px 0; color: #153122;">${(formData.challenges || '—').replace(/\n/g, '<br>')}</td>
            </tr>
            <tr>
              <td style="padding: 10px 0; font-weight: 600; color: #51705d;">📊 Monthly Volume</td>
              <td style="padding: 10px 0; color: #153122;">${formData.volume || '—'}</td>
            </tr>
          </table>
          <div style="margin-top: 20px; padding-top: 16px; border-top: 1px solid #e5e7eb; font-size: 13px; color: #86a191;">
            <div>🕐 Time: ${time} (CET)</div>
            <div>🌐 IP: ${ip || 'unknown'}</div>
            <div style="margin-top: 8px;">— Nexify AI Pilot Program</div>
          </div>
        </div>
      </div>
    `;

    const text = `New Pilot Program Application
==============================

Company: ${formData.company || '—'}
Industry: ${formData.industry || '—'}
Contact Name: ${formData.name || '—'}
Email: ${formData.email || '—'}
Website: ${formData.website || '—'}
Challenges: ${formData.challenges || '—'}
Monthly Volume: ${formData.volume || '—'}

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
    console.error('Pilot email send error:', e);
  }
}
