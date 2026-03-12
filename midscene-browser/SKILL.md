---
name: midscene-browser
description: |
  基于视觉的浏览器自动化，使用 Midscene 驱动无头 Puppeteer 浏览器。
  纯截图驱动，无需 DOM 或无障碍标签，可操控页面上任何可见元素。
  运行在无头浏览器中，不会接管用户的鼠标键盘，用户可同时使用电脑。

  适用于：浏览网页、抓取数据、填写表单、点击按钮、测试前端 UI、截图网页、自动化 Web 工作流。

  触发词：浏览器自动化, 打开网页, 网页截图, 抓取数据, 填写表单, 测试网页, 前端测试,
  browser automation, open URL, web scraping, fill form, test web app, take screenshot,
  browse website, check page, QA frontend, end-to-end test
license: MIT
metadata:
  author: Luffy Liu
  version: "1.0"
  upstream: web-infra-dev/midscene-skills
allowed-tools:
  - Bash
---

# 浏览器自动化（Midscene Browser）

> **⚠️ 关键规则 — 违反将导致工作流中断：**
>
> 1. **禁止后台运行 midscene 命令。** 每条命令必须同步执行，读取截图后再决定下一步。
> 2. **每次只运行一条 midscene 命令。** 等上一条完成后再执行下一条。
> 3. **给每条命令留足执行时间。** 涉及 AI 推理，通常需要 1 分钟，复杂操作可能更久。
> 4. **完成后必须主动汇报。** 总结执行结果、提取的数据、截图路径等。

---

## 何时使用此 Skill

| 场景 | 推荐 |
|------|------|
| 访问网页、抓取数据 | ✅ 使用此技能 |
| 测试前端 UI 功能 | ✅ 使用此技能 |
| 填写表单、自动化 Web 流程 | ✅ 使用此技能 |
| 需要保持登录态（如访问已登录的系统） | ❌ 改用 `midscene-chrome-bridge` |
| 操作桌面原生应用 | ❌ 改用 `midscene-computer` |

---

## 环境配置

Midscene 需要具备**视觉定位能力**的多模态模型。在当前工作目录创建 `.env` 文件：

```bash
MIDSCENE_MODEL_API_KEY="你的-api-key"
MIDSCENE_MODEL_NAME="模型名称"
MIDSCENE_MODEL_BASE_URL="https://..."
MIDSCENE_MODEL_FAMILY="模型族标识"
```

### 常用模型配置示例

**智谱 GLM-4.6V：**
```bash
MIDSCENE_MODEL_API_KEY="你的智谱API-Key"
MIDSCENE_MODEL_NAME="glm-4.6v"
MIDSCENE_MODEL_BASE_URL="https://open.bigmodel.cn/api/paas/v4"
MIDSCENE_MODEL_FAMILY="glm-v"
```

**Gemini-3-Flash：**
```bash
MIDSCENE_MODEL_API_KEY="你的Google-API-Key"
MIDSCENE_MODEL_NAME="gemini-3-flash"
MIDSCENE_MODEL_BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai/"
MIDSCENE_MODEL_FAMILY="gemini"
```

详见 [模型配置文档](https://midscenejs.com/model-common-config)。

---

## 命令参考

### 连接网页

```bash
npx @midscene/web@1 connect --url https://example.com
```

### 截图

```bash
npx @midscene/web@1 take_screenshot
```

截图后，**必须读取截图文件**了解页面状态，再决定下一步操作。

### 执行操作

用 `act` 与页面交互。它会自主处理点击、输入、滚动、悬停、等待、导航等操作，应给出**高层次的整体任务**：

```bash
# 具体指令
npx @midscene/web@1 act --prompt "点击登录按钮，在邮箱输入框填入 user@example.com"
npx @midscene/web@1 act --prompt "向下滚动，点击提交按钮"

# 目标驱动指令
npx @midscene/web@1 act --prompt "点击国家下拉框，选择日本"
```

### 断开连接（保持浏览器运行）

```bash
npx @midscene/web@1 disconnect
```

### 关闭浏览器

```bash
npx @midscene/web@1 close
```

---

## 标准工作流

```
1. 连接网页 → 2. 截图确认 → 3. 执行操作 → 4. 关闭浏览器 → 5. 汇报结果
```

1. **连接** — 用 `connect --url` 打开目标网页
2. **截图** — 确认页面已加载
3. **执行操作** — 用 `act` 完成自动化任务
4. **关闭** — 用 `close` 关闭浏览器释放资源（或 `disconnect` 保留会话）
5. **汇报** — 总结完成情况、提取的数据、截图路径

> 💡 **浏览器会跨命令持久化**。`connect` 后的浏览器实例不会在命令间丢失，可以连续执行多条命令。

---

## 最佳实践

1. **先连接再操作**：必须先 `connect --url` 打开目标页面。
2. **描述要具体**：说 `"联系表单中蓝色的提交按钮"`，不要说 `"那个按钮"`。
3. **用自然语言**：说 `"红色的立即购买按钮"`，不要说 `"#buy-btn"`。
4. **处理加载状态**：导航或触发页面加载后，先截图确认页面就绪。
5. **合并相关操作**：`"填写邮箱和密码，然后点击登录按钮"` 应该是一条 `act`，不是三条。
6. **用完就关**：用 `close` 关闭浏览器释放资源。

---

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| 连接失败 | 确认系统已安装 Chrome/Chromium（Puppeteer 默认会下载） |
| API Key 错误 | 检查 `.env` 文件中的 `MIDSCENE_MODEL_API_KEY` |
| 操作超时 | 页面可能较慢，连接后先截图确认加载完成 |
| 截图无法显示 | 截图路径是本地绝对路径，用 Read 工具查看 |
