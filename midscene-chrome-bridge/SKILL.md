---
name: midscene-chrome-bridge
description: |
  基于视觉的 Chrome Bridge 模式自动化，通过 Midscene Chrome 扩展连接用户真实的桌面 Chrome 浏览器。
  保留 Cookie、会话和登录状态，不接管鼠标键盘（通过 Chrome DevTools Protocol 操作）。

  适用于需要已登录状态的网页操作、保留会话的数据抓取、使用用户真实浏览器环境的场景。

  触发词：Chrome Bridge, 用户浏览器, 保留登录状态, 已登录页面, 真实浏览器操作,
  chrome bridge, preserve login, real browser, user's Chrome, existing session
license: MIT
metadata:
  author: Luffy Liu
  version: "1.0"
  upstream: web-infra-dev/midscene-skills
allowed-tools:
  - Bash
---

# Chrome Bridge 自动化（Midscene Chrome Bridge）

> **⚠️ 关键规则 — 违反将导致工作流中断：**
>
> 1. **禁止后台运行 midscene 命令。** 每条必须同步执行。
> 2. **每次只运行一条命令。** 等上一条完成后再执行下一条。
> 3. **留足执行时间。** 涉及 AI 推理，通常需要 1 分钟以上。
> 4. **完成后必须主动汇报结果。**

---

## 何时使用此 Skill

| 场景 | 推荐 |
|------|------|
| 访问需要登录的页面（如后台管理系统） | ✅ 使用此技能 |
| 需要保留 Cookie 和会话的操作 | ✅ 使用此技能 |
| 使用用户真实 Chrome 浏览器环境 | ✅ 使用此技能 |
| 普通网页访问（无需登录） | ❌ 改用 `midscene-browser`（更简单） |
| 操作桌面原生应用 | ❌ 改用 `midscene-computer` |

---

## 命令格式

**⚠️ 每条命令必须使用以下格式，`--bridge` 标志是必须的：**

```
npx @midscene/web@1 --bridge <子命令> [参数]
```

---

## 环境配置

Midscene 需要具备**视觉定位能力**的多模态模型。在当前工作目录创建 `.env` 文件：

```bash
MIDSCENE_MODEL_API_KEY="你的-api-key"
MIDSCENE_MODEL_NAME="模型名称"
MIDSCENE_MODEL_BASE_URL="https://..."
MIDSCENE_MODEL_FAMILY="模型族标识"
```

详见 [模型配置文档](https://midscenejs.com/model-common-config)。

## 前置条件

用户需已安装并启用 Midscene Chrome 扩展。无需手动检查 — 直接连接即可。

---

## 命令参考

### 连接网页

```bash
npx @midscene/web@1 --bridge connect --url https://example.com
```

### 截图

```bash
npx @midscene/web@1 --bridge take_screenshot
```

### 执行操作

```bash
# 具体指令
npx @midscene/web@1 --bridge act --prompt "点击登录按钮，填入邮箱和密码"

# 目标驱动指令
npx @midscene/web@1 --bridge act --prompt "点击国家下拉框，选择日本"
```

### 断开连接

```bash
npx @midscene/web@1 --bridge disconnect
```

---

## 标准工作流

1. **连接** — 用 `connect --url` 打开页面
2. **截图** — 确认页面已加载
3. **执行操作** — 用 `act` 完成任务
4. **汇报结果**
5. **断开连接** — 仅在用户任务完全结束时断开。多轮对话中保持连接以便继续操作。

> 💡 **Bridge 模式的特点**：断开连接只关闭 CLI 端的桥接，不会关闭浏览器或标签页。所有 Cookie、登录状态始终保留。

---

## 最佳实践

1. **先连接再操作**：必须先 `connect --url` 打开目标页面。
2. **描述要具体**：用自然语言描述页面元素，不要用 CSS 选择器。
3. **多轮对话中不要断开**：用户可能还有后续操作，保持连接。
4. **合并相关操作**：多个连续操作合并为一条 `act` 命令。

---

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| Bridge 连接失败 | 确认 Chrome 已打开并安装了 [Midscene 扩展](https://chromewebstore.google.com/detail/midscenejs/gbldofcpkknbggpkmbdaefngejllnief)，扩展中 bridge mode 显示 "Listening" |
| 操作超时 | 页面可能较慢，连接后先截图确认加载完成 |
| 截图无法显示 | 截图路径是本地绝对路径，用 Read 工具查看 |
