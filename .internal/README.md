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

### 第一步：获取 Google Gemini API Key

你已经有了，跳过。如果你还没有：
1. 访问 https://aistudio.google.com/apikey
2. 点击「Create API Key」→ 选择项目 → 复制 Key
3. 免费额度很高，起步阶段完全够用

---

### 第二步：获取 Resend API Key（邮件通知用）

用来收到新 lead 时自动发邮件提醒你。

1. 访问 https://resend.com 注册账号（免费）
2. 登录后，左侧菜单 → **API Keys** → **Create API Key**
3. 名称随便填（比如 `nexify-leads`），权限选 `Full access` → 创建
4. **复制 Key 保存好**（只显示一次）

> 💡 免费额度：每天 100 封邮件，起步完全够用。
>
> 🔒 你的收件邮箱 `yuanxin0222@gmail.com` 只会存在 Worker 后端，前端完全不可见。

---

### 第三步：部署 Cloudflare Worker

#### 3.1 创建 Worker

1. 登录 https://dash.cloudflare.com/
2. 左侧菜单 → **Workers & Pages** → **Create** → **Create Worker**
3. 给 Worker 起个名字，比如 `nexify-chatbot` → 点 **Deploy**
4. 先随便部署一个默认的，等下替换代码

#### 3.2 替换 Worker 代码

1. 进入刚创建的 Worker → 点右上角 **Edit Code**
2. 把 `worker.js` 的全部内容**复制粘贴**进去，覆盖原有代码
3. 点右上角 **Deploy** 保存

#### 3.3 设置环境变量（关键步骤）

回到 Worker 详情页 → **Settings** → **Variables** → 往下找到 **Environment Variables** → 点 **Add variable**

依次添加以下 5 个变量：

| # | 变量名 | 值 | Encrypt |
|---|--------|-----|---------|
| 1 | `AI_PROVIDER` | `gemini` | 不用勾 |
| 2 | `AI_API_KEY` | 你的 Google API Key（`AQ.Ab8RN6Ih...`） | ✅ 勾上 |
| 3 | `AI_MODEL` | `gemini-2.0-flash` | 不用勾 |
| 4 | `LEAD_NOTIFY_EMAIL` | `yuanxin0222@gmail.com` | ✅ 勾上 |
| 5 | `RESEND_API_KEY` | 你的 Resend API Key（`re_` 开头） | ✅ 勾上 |

> 🔐 **Encrypt 加密**：敏感信息（API Key、邮箱）一定要勾上 Encrypt，加密后的值谁都看不到，包括你自己，只能整体替换。

添加完后点 **Deploy** 生效。

#### 3.4 记下 Worker URL

在 Worker 详情页顶部能看到一个 URL，类似：
```
https://nexify-chatbot.yourname.workers.dev
```
复制这个地址，下一步要用。

---

### 第四步：把页面部署到你的网站

1. 打开 `index.html`，找到这一行（大概在 JS 代码开头）：
   ```js
   const API_URL = '';
   ```
2. 把你的 Worker URL 填进去：
   ```js
   const API_URL = 'https://nexify-chatbot.yourname.workers.dev';
   ```
3. 保存文件，上传到你 nexifyai.org 的网站服务器

---

### 第五步：测试验证

1. 打开你的网站 `nexifyai.org`
2. 点右下角的聊天气泡，说几句话，看 AI 是否正常回复
3. 或者直接点 **Book Demo** 按钮，看是否自动弹出聊天并开始收集信息
4. 把 5 项信息（行业、公司名、联系人、邮箱、需求）都聊完，检查你的 gmail 邮箱是否收到 lead 通知邮件

📧 邮件通知长这样：
- 标题：`🔔 New Lead: 公司名 - 行业`
- 内容：HTML 格式的 lead 详情卡片，包含所有收集到的信息 + 时间 + IP

---

## 环境变量速查表

| 变量名 | 必须 | 说明 |
|--------|------|------|
| `AI_PROVIDER` | ✅ | `gemini` / `groq` / `openai` |
| `AI_API_KEY` | ✅ | 对应的 API Key |
| `AI_MODEL` | ❌ | 模型名，不填用默认值 |
| `LEAD_NOTIFY_EMAIL` | ❌ | 接收 lead 通知的邮箱 |
| `RESEND_API_KEY` | ❌ | Resend API Key（邮件通知必填） |
| `LEAD_WEBHOOK_URL` | ❌ | Webhook 推送地址（可选） |

> ✅ 你目前只需要配置前 5 个（gemini + 邮件通知）。

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
