---
name: midscene-computer
description: |
  基于视觉的桌面自动化，使用 Midscene 驱动原生键鼠控制 macOS、Windows、Linux 桌面应用。
  纯截图驱动，无需 DOM 或无障碍标签，可操控屏幕上任何可见元素。
  适用于桌面原生应用（Electron、Qt、macOS/Windows/Linux 原生应用）。

  ⚠️ 此技能会接管用户的真实鼠标和键盘，自动化运行期间用户无法操作电脑。
  → 如果是 Web 应用，请优先使用 midscene-browser 技能（无头浏览器，不影响用户操作）。

  触发词：桌面自动化, 控制电脑, 打开应用, 截图桌面, 鼠标点击, 键盘快捷键, 操作桌面, 桌面测试,
  open app, desktop automation, computer control, click on screen, type text, launch application,
  test desktop app, test Electron app, test native UI
license: MIT
metadata:
  author: Luffy Liu
  version: "1.0"
  upstream: web-infra-dev/midscene-skills
allowed-tools:
  - Bash
---

# 桌面自动化（Midscene Computer）

> **⚠️ 关键规则 — 违反将导致工作流中断：**
>
> 1. **禁止后台运行 midscene 命令。** 每条命令必须同步执行，读取输出（尤其是截图）后再决定下一步操作。
> 2. **每次只运行一条 midscene 命令。** 等上一条完成、看完截图后，再执行下一条。
> 3. **给每条命令留足执行时间。** 涉及 AI 推理和屏幕交互，通常需要 1 分钟，复杂操作可能更久。
> 4. **完成后必须主动汇报。** 总结执行结果、关键数据、截图路径等，不要默默结束。

---

## 何时使用此 Skill

| 场景 | 推荐 |
|------|------|
| 操作桌面原生应用（Finder、Keynote、VSCode 等） | ✅ 使用此技能 |
| 操作 Electron 应用 | ✅ 使用此技能 |
| Web 应用测试 | ❌ 改用 `midscene-browser`（更快更稳） |
| 需要保留登录态的 Chrome 操作 | ❌ 改用 `midscene-chrome-bridge` |

---

## 环境配置

Midscene 需要具备**视觉定位能力**的多模态模型。配置文件统一存放在用户主目录 `~/.env`：

```bash
# ~/.env
MIDSCENE_MODEL_API_KEY="你的-api-key"
MIDSCENE_MODEL_NAME="模型名称"
MIDSCENE_MODEL_BASE_URL="https://..."
MIDSCENE_MODEL_FAMILY="模型族标识"
```

**⚠️ 每次执行 midscene 命令前，必须先加载环境变量：**

```bash
export $(cat ~/.env | grep -v '^#' | xargs)
```

> 💡 Midscene 默认从当前工作目录加载 `.env`，但为了避免每个目录都放一份，统一使用 `~/.env` 并通过 `export` 注入环境变量。

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

**通义千问 Qwen3.5：**
```bash
MIDSCENE_MODEL_API_KEY="你的阿里云API-Key"
MIDSCENE_MODEL_NAME="qwen3.5-plus"
MIDSCENE_MODEL_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
MIDSCENE_MODEL_FAMILY="qwen3.5"
MIDSCENE_MODEL_REASONING_ENABLED="false"
```

**豆包 Seed 2.0 Lite：**
```bash
MIDSCENE_MODEL_API_KEY="你的火山引擎API-Key"
MIDSCENE_MODEL_NAME="doubao-seed-2-0-lite"
MIDSCENE_MODEL_BASE_URL="https://ark.cn-beijing.volces.com/api/v3"
MIDSCENE_MODEL_FAMILY="doubao-seed"
```

如模型未配置，请提示用户设置。详见 [模型配置文档](https://midscenejs.com/model-common-config)。

---

## 命令参考

### 连接桌面

```bash
npx @midscene/computer@1 connect
npx @midscene/computer@1 connect --displayId <显示器ID>
```

### 列出显示器

```bash
npx @midscene/computer@1 list_displays
```

### 截图

```bash
npx @midscene/computer@1 take_screenshot
```

截图后，**必须读取截图文件**了解当前屏幕状态，再决定下一步操作。

### 执行操作

用 `act` 与电脑交互。它会自主处理所有 UI 操作（点击、输入、滚动、等待、导航），因此应给出**高层次的整体任务**描述，而非拆分成小步骤：

```bash
# 具体指令
npx @midscene/computer@1 act --prompt "在搜索框中输入 hello world 然后按回车"
npx @midscene/computer@1 act --prompt "把文件图标拖到废纸篓"

# 目标驱动指令
npx @midscene/computer@1 act --prompt "用 Chrome 浏览器搜索上海天气，告诉我结果"
```

### 断开连接

```bash
npx @midscene/computer@1 disconnect
```

---

## 标准工作流

```
1. 连接 → 2. 健康检查 → 3. 打开应用并截图 → 4. 执行操作 → 5. 断开 → 6. 汇报结果
```

1. **连接** — 建立会话
2. **健康检查** — 若 `connect` 输出已包含截图和鼠标测试则跳过；否则手动截图 + 移动鼠标验证。任一失败则先排查。
3. **打开目标应用并截图** — 确认应用已在前台
4. **执行操作** — 使用 `act` 完成自动化任务
5. **断开连接**
6. **汇报结果** — 总结完成情况、关键数据、截图路径

---

## 最佳实践

1. **先用系统命令打开应用再操作**：使用 `open -a <应用名>`（macOS）或 `start <应用名>`（Windows）把应用拉到前台，截图确认后再用 midscene 操作。避免通过 Spotlight 等启动器搜索，那样更慢。
2. **描述要具体明确**：说 `"Safari 窗口左上角的红色关闭按钮"`，不要说 `"关闭按钮"`。
3. **善用位置描述**：`"菜单栏右上角的图标"`、`"左侧边栏第三项"`。
4. **合并相关操作**：`"搜索X，点击第一个结果，向下滚动查看详情"` 应该是一条 `act` 命令，而不是三条。
5. **多显示器处理**：如果截图中看不到应用，可能在其他显示器上。用 `list_displays` 检查，或用 `connect --displayId <id>` 切换。
6. **macOS 先设置 PATH**：
   ```bash
   export PATH="/usr/sbin:/usr/bin:/bin:/sbin:$PATH"
   ```

---

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| macOS 辅助功能权限被拒 | **系统设置 > 隐私与安全 > 辅助功能**，添加并启用终端应用，然后重启终端 |
| Xcode 命令行工具未安装 | 运行 `xcode-select --install` |
| API Key 未设置 | 检查 `.env` 文件是否包含 `MIDSCENE_MODEL_API_KEY` |
| 截图失败提示找不到 `system_profiler` | 运行 `export PATH="/usr/sbin:/usr/bin:/bin:/sbin:$PATH"` |
| AI 找不到元素 | 1. 截图确认元素可见 2. 用更具体的描述（颜色、位置、周围文字）3. 确保没有被其他窗口遮挡 |
