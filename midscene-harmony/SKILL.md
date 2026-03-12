---
name: midscene-harmony
description: |
  基于视觉的鸿蒙 HarmonyOS NEXT 设备自动化，使用 Midscene 通过 HDC 控制华为设备。
  纯截图驱动，无需 DOM 或无障碍标签，可操控屏幕上任何可见元素。

  触发词：鸿蒙, HarmonyOS, 华为设备, HDC, 鸿蒙自动化, 鸿蒙测试,
  harmony, harmonyos, huawei device, hdc, harmony automation
license: MIT
metadata:
  author: Luffy Liu
  version: "1.0"
  upstream: web-infra-dev/midscene-skills
allowed-tools:
  - Bash
---

# 鸿蒙设备自动化（Midscene HarmonyOS）

> **⚠️ 关键规则：**
>
> 1. **禁止后台运行 midscene 命令。** 每条必须同步执行。
> 2. **每次只运行一条命令。** 等上一条完成后再执行下一条。
> 3. **留足执行时间。** 涉及 AI 推理，通常需要 1 分钟以上。

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

## HDC 环境

HDC（HarmonyOS Device Connector）需提前安装：

- 通过 [DevEco Studio](https://developer.huawei.com/consumer/cn/deveco-studio/) 安装
- 或设置 `HDC_HOME` 环境变量指向 HDC 目录

验证 HDC：

```bash
hdc version
hdc list targets
```

---

## 命令参考

### 连接设备

```bash
npx @midscene/harmony@1 connect
npx @midscene/harmony@1 connect --deviceId 0123456789ABCDEF
```

### 截图

```bash
npx @midscene/harmony@1 take_screenshot
```

### 执行操作

```bash
# 具体指令
npx @midscene/harmony@1 act --prompt "在搜索框中输入 hello world 然后按回车"
npx @midscene/harmony@1 act --prompt "长按消息气泡，在弹出菜单中点击删除"

# 目标驱动指令
npx @midscene/harmony@1 act --prompt "打开设置，进入 Wi-Fi 设置，告诉我连接的网络名称"
```

### 断开连接

```bash
npx @midscene/harmony@1 disconnect
```

---

## 标准工作流

1. **连接** — 建立会话
2. **打开目标应用并截图** — 确认应用已在前台
3. **执行操作** — 用 `act` 完成任务
4. **断开连接**

---

## 最佳实践

1. **先用 HDC 启动应用**：`hdc shell aa start -a EntryAbility -b <bundleName>` 比用 midscene 导航快得多。
2. **描述要具体**：说 `"右侧的 Wi-Fi 开关"` 而不是 `"开关"`。
3. **合并相关操作**：多个连续操作合并为一条 `act` 命令。

---

## 常用鸿蒙应用包名

| 应用 | 包名 |
|------|------|
| 设置 | `com.huawei.hmos.settings` |
| 相机 | `com.huawei.hmos.camera` |
| 图库 | `com.huawei.hmos.photos` |
| 日历 | `com.huawei.hmos.calendar` |
| 时钟 | `com.huawei.hmos.clock` |
| 计算器 | `com.huawei.hmos.calculator` |
| 浏览器 | `com.huawei.hmos.browser` |
| 天气 | `com.huawei.hmos.weather` |

---

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| HDC 未找到 | 通过 DevEco Studio 安装，或设置 `HDC_HOME` 环境变量 |
| 设备未列出 | 检查 USB 连接，确认开发者选项中 USB 调试已开启 |
| 命令超时 | 设备可能息屏或锁定，唤醒并解锁设备 |
| 多设备时操作错设备 | 用 `--deviceId <id>` 指定目标设备 |
