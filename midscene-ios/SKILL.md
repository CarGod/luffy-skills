---
name: midscene-ios
description: |
  基于视觉的 iOS 设备自动化，使用 Midscene 通过 WebDriverAgent 控制 iPhone/iPad。
  纯截图驱动，无需 DOM 或无障碍标签，可操控屏幕上任何可见元素。

  触发词：iOS, iPhone, iPad, 苹果手机, iOS测试, 移动端测试,
  ios automation, iphone, ipad, test ios app, mobile app ios
license: MIT
metadata:
  author: Luffy Liu
  version: "1.0"
  upstream: web-infra-dev/midscene-skills
allowed-tools:
  - Bash
---

# iOS 设备自动化（Midscene iOS）

> **⚠️ 关键规则：**
>
> 1. **禁止后台运行 midscene 命令。** 每条必须同步执行。
> 2. **每次只运行一条命令。** 等上一条完成后再执行下一条。
> 3. **留足执行时间。** 涉及 AI 推理，通常需要 1 分钟以上。
> 4. **完成后必须主动汇报结果。**

---

## 环境配置

在当前工作目录创建 `.env` 文件：

```bash
MIDSCENE_MODEL_API_KEY="你的-api-key"
MIDSCENE_MODEL_NAME="模型名称"
MIDSCENE_MODEL_BASE_URL="https://..."
MIDSCENE_MODEL_FAMILY="模型族标识"
```

详见 [模型配置文档](https://midscenejs.com/model-common-config)。

---

## 命令参考

### 连接设备

```bash
npx @midscene/ios@1 connect
```

### 截图

```bash
npx @midscene/ios@1 take_screenshot
```

### 执行操作

```bash
# 具体指令
npx @midscene/ios@1 act --prompt "在搜索框中输入 hello world 然后按回车"
npx @midscene/ios@1 act --prompt "点击删除按钮，在弹窗中确认"

# 目标驱动指令
npx @midscene/ios@1 act --prompt "打开设置，进入 Wi-Fi，告诉我连接的网络名称"
```

### 断开连接

```bash
npx @midscene/ios@1 disconnect
```

---

## 标准工作流

1. **连接** — 建立会话
2. **打开目标应用并截图** — 确认应用已在前台
3. **执行操作** — 用 `act` 完成任务
4. **断开连接**
5. **汇报结果**

---

## 最佳实践

1. **描述要具体**：说 `"右上角的设置图标"` 而不是 `"图标"`。
2. **善用位置描述**：`"右上角的搜索图标"`、`"列表第三项"`。
3. **合并相关操作**：多个连续操作合并为一条 `act` 命令。

---

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| WebDriverAgent 未运行 | 确认设备上已安装并运行 WebDriverAgent。详见 [iOS 使用文档](https://midscenejs.com/zh/usage-ios.html) |
| 设备未找到 | 确认设备已通过 USB 连接并信任此电脑 |
| API Key 错误 | 检查 `.env` 文件中的 `MIDSCENE_MODEL_API_KEY` |
