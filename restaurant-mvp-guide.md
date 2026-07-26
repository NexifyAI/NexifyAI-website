# 餐厅 AI 智能客服 — 快速接入指南

> 不用换系统、不用培训、5分钟上线，24小时自动接订座、答菜单、回外卖咨询

---

## 🎯 能帮餐厅做什么

### 1. 自动接订座 📅
- 客人在网站上直接和 AI 聊，就能完成订座
- 自动收集：人数、时间、姓名、电话、特殊要求
- 订座完成后**即时邮件通知**餐厅
- 不用再怕忙的时候漏接电话

### 2. 菜单问答 🍜
- 客人问菜品、价格、辣度、素食、过敏
- AI 秒回，不用服务员反复解释
- 支持中/英/荷三语自动切换

### 3. 外卖指引 🛵
- 告诉客人在哪几个平台可以点外卖
- Uber Eats、Thuisbezorgd、微信小程序
- 不用再一一回复同样的问题

### 4. 常见问题解答 ❓
- 营业时间、地址、停车、WiFi、支付方式
- 包厢预订、宴席包场咨询
- 减少前台80%的重复问答

---

## 🚀 接入方式（两种方案）

### 方案 A：嵌入餐厅官网（推荐）

**一行代码搞定，5分钟上线**

```html
<script src="https://nexifyai.org/chatbot.js"
  data-api-url="https://chatbox.yuanxin0222.workers.dev"
  data-brand="餐厅名字"
  data-persona="restaurant"
  data-persona-config='{"restaurantName":"金龙轩","cuisineType":"粤菜","address":"...","phone":"...","openingHours":"...","deliveryPlatforms":"...","specialties":"..."}'
  data-greeting="您好！欢迎光临XX餐厅，有什么可以帮您？">
</script>
```

把这段代码加到餐厅网站的 `</body>` 标签前面就可以了。

---

### 方案 B：微信接入

通过公众号菜单或小程序跳转到对话页面，适合以微信客户为主的中餐厅。

（待开发，可按需定制）

---

## ⚙️ 餐厅配置项

每家餐厅可以自定义以下信息，AI 就会用这些内容回答客人：

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `restaurantName` | 餐厅名称 | 金龙轩 Golden Dragon |
| `cuisineType` | 菜系 | 正宗粤菜 Cantonese Cuisine |
| `address` | 地址 | Kruisplein 123, 3012 CC Rotterdam |
| `phone` | 电话 | +31 10 123 4567 |
| `openingHours` | 营业时间 | 周一至周日 11:30-22:00 |
| `priceRange` | 价格区间 | 人均 €25-40 |
| `deliveryPlatforms` | 外卖平台 | Uber Eats, Thuisbezorgd, 微信小程序 |
| `specialties` | 招牌菜 | 北京烤鸭、港式点心、海鲜火锅 |
| `languages` | 服务语言 | 中文/英文/荷兰文 |
| `parkingInfo` | 停车信息 | Kruisplein停车场，步行2分钟 |
| `privateRooms` | 包厢信息 | 3个包厢，6-20人 |
| `additionalInfo` | 其他 | 支持微信支付、支付宝、免费WiFi |

---

## 💰 定价

| 方案 | 价格 | 包含 |
|------|------|------|
| **基础版** | €99/月 | AI客服widget + 订座功能 + 邮件通知 + 菜单问答 |
| **专业版** | €199/月 | 基础版全部 + 多语言 + 数据分析月报 + 微信接入 |
| **定制版** | 面议 | 品牌定制 + 系统对接 + 专属训练 |

> 🎁 首月免费试用，满意再付款

---

## 📞 技术支持

- 部署协助：免费
- 日常维护：包含在月费中
- 功能定制：按需报价

---

*由 Nexify AI 提供技术支持 · 让AI帮你看店，让人做更重要的事*
