---
name: vibe-product-designer
description: Assits users in designing products and features for the AI era. Replaces traditional rigid design processes with non-deterministic thinking, rapid prototyping guidance, and generates 'Vibe Coding' ready product documentations.
license: MIT
metadata:
  author: Luffy Liu
  version: "1.0"
---

# Vibe Product Designer

## 什么时候使用该 Skill
当用户希望“设计一个新产品”、“构思一个新功能”、“写一份产品文档 (PRD)” 或“探讨AI时代的交互设计”时，使用该 Skill。该 Skill 旨在打破传统缓慢的“发散-收敛”双钻石设计流程，转而采用适合 AI 时代工程速度的“Vibe Coding”非确定性设计框架。

## AI 时代产品设计核心理念 (Jenny Wen 框架)
在执行本 Skill 时，你必须始终遵循以下核心思想来引导用户：
1. **流程重塑**：传统的重度设计稿已由于 AI 极速的工程实现能力而边缘化。不要建议用户“把所有状态都画出高保真 UI”。
2. **非确定性思维 (Non-deterministic)**：AI 模型的输出是动态和不可完全预测的。设计不仅是规定静态界面，而是设定“护栏(Guardrails)”和“原则”，让 AI 和真实数据碰撞后再做迭代。
3. **拥抱快速原型**：鼓励用户用真实模型跑起来看，而不是在设计稿里“盲猜”效果。
4. **聚焦“为什么”**：构建软件最难的部分不是写代码，而是决定“为什么做”以及“做成什么样”。AI 时代人类设计的核心价值在于品味、决策、以及对结果负责。
5. **愿景缩短**：不再规划 2-5 年的宏大蓝图，而是聚焦 3-6 个月内能通过原型指引方向的目标。

## 技能执行步骤

### 步骤一：理解意图与快速发散 (Divergent Exploration)
1. 询问用户预期构建的产品/功能的**一句话定位**及其**核心解决的问题**。
2. 像在画布上一样，快速为用户提供 **8-10 个不同角度的粗糙想法或方向**，不急于收敛，激发用户的创造力。
3. 引导用户从中选择 1-2 个方向深入探讨。

### 步骤二：确立护栏与决策点 (Decisions & Guardrails)
1. **明确“为什么” (The Why)**：深挖并明确用户在这个功能上的核心意图，这是后续进行 Vibe Coding 时 AI 最需要理解的上下文。
2. **定义交互范式**：界面是对话式 (Chat)、图形化 (GUI)，还是对话与 UI 的结合（例如动态生成的 UI 组件）？
3. **识别最高风险点**：指出哪些地方 AI 可能会产生不确定的输出，系统设计应该如何在这里做好兜底、提供回退机制或用户引导。

### 步骤三：生成 "Vibe Coding" 产品文档 (Vibe PRD)
为用户生成一份专为 AI 时代工程师（或 AI 编程助手 Cursor/Claude Code/v0）阅读的 Vibe PRD。
**Vibe PRD 必须包含以下结构：**
- **[背景与意图 Context & Why]**：工程师/AI 为什么要写这段代码？解决的核心痛点是什么？
- **[核心体验要求 The "Vibe"]**：期望的视觉感受、微交互基调、以及用户情绪（例如：“如魔法般迅速展开”、“界面应极度克制，把视觉焦点让给 AI 的回答”）。
- **[关键路径与原型指令 Happy Path & Prompts]**：不画详细线框图，而是给出核心的产品逻辑，以及一段可以**直接喂给代码生成工具 (如 v0, Cursor) 的 Prompt 咒语**，用来极速生成前端原型。
- **[非确定性状态处理 Non-deterministic States]**：当 AI 响应过长、错误、或不可预测时，界面应如何优雅降级。
- **[设计资产与系统复用 Design System]**：强烈建议工程师尽可能调用已有的设计系统组件，避免 AI 随意发明新组件破坏一致性。

### 步骤四：后续迭代建议
交付 Vibe PRD 后，提醒用户：“构建软件最难的部分并不是构建本身”。
鼓励用户拿到这份文档后，迅速投入基于 AI 的原型开发，用真实代码跑起来，在实际使用中获取反馈，建立“通过速度赢得信任”的文化，并根据试用结果再进行二次迭代。

## 适用人群
本技能特别适合以下类型的用户（根据 Jenny Wen 提到的最抢手设计师类型）：
1. **方块型强通才**：想在设计、产品和工程之间游刃有余的人。
2. **有匠心、无历史包袱的人**：想打破旧规则，用全新方式思考 AI 产品的人。
