---
AIGC:
    Label: "1"
    ContentProducer: 001191110102MACQD9K64018705
    ProduceID: 692027999912291_0-data_volume/7662074350652408083-files/所有对话/主对话/nexifyai-chatbot/README.md
    ReservedCode1: ""
    ContentPropagator: 001191110102MACQD9K64028705
    PropagateID: 692027999912291#1783975416786
    ReservedCode2: ""
---
# NexifyAI Smart Chatbot

一个 7x24 AI 智能客服 Widget，支持多语言自动识别与潜在客户信息自动收集。

## ✨ 功能特性

- **24/7 全天候在线** - 不眠不休的 AI 客服
- **自动语言识别** - 英文/荷兰语/法语/西班牙语/中文 + 更多
- **自然收集 Leads** - 像真人一样聊天，自然收集：行业、公司名、联系人、邮箱、需求简述
- **纯前端嵌入** - 一行 script 标签即可接入任何网站
- **移动端适配** - 响应式设计，手机端完美体验
- **成本极低** - 基于 Google Gemini / Groq / OpenAI，几乎可以忽略不计

## 📁 文件结构

```
├── chatbot.js      # 前端 Widget 脚本（嵌入网站用）
├── worker.js       # Cloudflare Worker（AI 对话核心）
├── demo.html       # 本地测试页面
└── README.md       # 部署说明
```

## 🚀 部署步骤

### 第一步：部署 Cloudflare Worker

1. 登录 Cloudflare Dashboard → Workers & Pages → Create Worker

2. 把 `worker.js` 的内容复制进去

3. 设置环境变量（Settings → Variables）：

| 变量名 | 必须 | 说明 | 示例 |
|--------|------|------|------|
| `AI_PROVIDER` | ✅ | AI 提供商 | `gemini` / `groq` / `openai` |
| `AI_API_KEY` | ✅ | API Key | 你的 API key |
| `AI_MODEL` | ❌ | 模型名称，不填用默认 | `gemini-2.0-flash` |
| `LEAD_NOTIFY_EMAIL` | ❌ | 收到新 lead 的通知邮箱 | `you@example.com` |
| `RESEND_API_KEY` | ❌ | Resend API Key（邮件通知需要） | `re_...` |
| `LEAD_WEBHOOK_URL` | ❌ | 收集到 lead 后推送到 webhook | `https://...` |

> **邮箱完全不可见**：`LEAD_NOTIFY_EMAIL` 只存在于 Worker 后端，前端代码中完全不会出现。

4. 保存并部署，记下 Worker 的 URL（类似 `https://your-worker.xxx.workers.dev`）

### 第二步：嵌入网站

在你的网站 `</body>` 前加入这一行：

```html
<script 
  src="https://your-domain.com/chatbot.js"
  data-api-url="YOUR_WORKER_URL"
  data-brand="NexifyAI"
  data-primary-color="#6366f1"
></script>
```

**参数说明：**

| 参数 | 必须 | 说明 |
|------|------|------|
| `data-api-url` | ✅ | 你的 Cloudflare Worker URL |
| `data-brand` | ❌ | 显示的品牌名称，默认 NexifyAI |
| `data-primary-color` | ❌ | 主题色，默认 #6366f1 |
| `data-greeting` | ❌ | 自定义欢迎语 |

### 第三步：本地测试

```bash
# 方式一：Python 启动本地服务器
python3 -m http.server 8080

# 然后打开 http://localhost:8080/demo.html
```

## 💰 成本对比

| 提供商 | 模型 | 1000 次对话估算 | 月付价格 |
|--------|------|-----------------|----------|
| Google | gemini-2.0-flash | ~$0.15 | 免费额度很高，起步几乎免费 |
| Groq | llama-3.1-70b-versatile | ~$0.50 | 免费额度足够起步 |
| OpenAI | gpt-4o-mini | ~$0.30 | 按量付费 |

**推荐 Google Gemini**：免费额度最高、支持 JSON 模式原生、速度快，是起步阶段性价比最高的选择。

## 📬 Leads 通知

收集到完整的客户信息后，可以通过以下方式通知你：

### 方式一：邮件通知 ✅ 推荐
1. 去 [resend.com](https://resend.com) 注册免费账号（每天 100 封免费额度）
2. 在 Resend 里验证你的发件域名（或用默认的 resend.dev 测试域名）
3. Worker 设置两个环境变量：
   - `LEAD_NOTIFY_EMAIL` = 你的收件邮箱（yuanxin0222@gmail.com）
   - `RESEND_API_KEY` = 你在 Resend 创建的 API Key

> 🔒 **隐私保护**：邮箱地址只保存在 Worker 后端，前端代码和访客完全看不到。

### 方式二：Webhook 推送
设置 `LEAD_WEBHOOK_URL`，自动推送到：
- Make.com / Zapier - 转发到邮箱、Notion、Google Sheets 等
- 飞书/企业微信/Slack - 群机器人 webhook
- 自己的后端 API

### 方式三：本地存储（补充）
浏览器 localStorage 自动备份（仅作补充，不推荐作为主要方式）

## 🎨 自定义

### 修改欢迎语

```html
<script 
  src="chatbot.js"
  data-greeting="Hi! Welcome to NexifyAI. How can we help protect your brand today?"
></script>
```

### 修改主题色

```html
<script 
  src="chatbot.js"
  data-primary-color="#10b981"
></script>
```

### 后续可以嵌入到你网站任何一个页面，测试对话效果

## 可以后续定制：

- 自定义开场白和 FAQ 自动触发
- 工作时间外的离线模式
- 人工转接（用户指定时间触发人工
- 自定义对话历史记录
- 多语言欢迎语自定义
- 自定义品牌名称和图标

需要调整什么随时说！

---

> 本内容由 Coze AI 生成，请遵循相关法律法规及《人工智能生成合成内容标识办法》使用与传播。
