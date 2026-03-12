---
name: midscene-android
description: |
  基于视觉的 Android 设备自动化，使用 Midscene 通过 ADB 控制 Android 手机/模拟器。
  纯截图驱动，无需 DOM 或无障碍标签，可操控屏幕上任何可见元素。

  适用于：点击、滑动、输入文字、启动应用、截图等操作。

  触发词：Android, 安卓, 手机自动化, ADB, 移动端测试, 安卓测试, 手机操作,
  android automation, mobile app, tap, swipe, adb, test android app
license: MIT
metadata:
  author: Luffy Liu
  version: "1.0"
  upstream: web-infra-dev/midscene-skills
allowed-tools:
  - Bash
---

# Android 设备自动化（Midscene Android）

> **⚠️ 关键规则：**
>
> 1. **禁止后台运行 midscene 命令。** 每条必须同步执行。
> 2. **每次只运行一条命令。** 等上一条完成后再执行下一条。
> 3. **留足执行时间。** 涉及 AI 推理，通常需要 1 分钟以上。
> 4. **完成后必须主动汇报结果。**

---

## 环境配置

配置文件统一存放在用户主目录 `~/.env`：

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

详见 [模型配置文档](https://midscenejs.com/model-common-config)。

---

## 命令参考

### 连接设备

```bash
npx @midscene/android@1 connect
npx @midscene/android@1 connect --deviceId emulator-5554
```

### 截图

```bash
npx @midscene/android@1 take_screenshot
```

### 执行操作

```bash
# 具体指令
npx @midscene/android@1 act --prompt "在搜索框中输入 hello world 然后按回车"
npx @midscene/android@1 act --prompt "长按消息气泡，在弹出菜单中点击删除"

# 目标驱动指令
npx @midscene/android@1 act --prompt "打开设置，进入 Wi-Fi 设置，告诉我连接的网络名称"
```

### 断开连接

```bash
npx @midscene/android@1 disconnect
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

1. **先用 ADB 启动应用**：`adb shell am start -n <包名/Activity>` 比用 midscene 导航到应用快得多。
2. **描述要具体**：说 `"右侧的 Wi-Fi 开关"` 而不是 `"开关"`。
3. **善用位置描述**：`"右上角的搜索图标"`、`"列表第三项"`。
4. **合并相关操作**：多个连续操作合并为一条 `act` 命令。

---

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| ADB 未找到 | macOS: `brew install android-platform-tools` |
| 设备未列出 | 检查 USB 连接，确认开发者选项中 USB 调试已开启，运行 `adb devices` |
| 设备显示 "unauthorized" | 解锁设备，接受 USB 调试授权弹窗 |
| 设备显示 "offline" | 拔插 USB，运行 `adb kill-server && adb start-server` |
| 命令超时 | 设备可能息屏或锁定，用 `adb shell input keyevent KEYCODE_WAKEUP` 唤醒 |
| 多设备时操作错设备 | 用 `--deviceId <id>` 指定目标设备 |
