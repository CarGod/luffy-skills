# 🧩 Luffy Skills

[English](./README_EN.md)

> 一组开源的 AI Agent Skills，遵循 [Agent Skills 开放规范](https://agentskills.io)，可被任何兼容的 AI 代理加载和使用。

## 📦 Skills 列表

| Skill | 描述 | 版本 |
|-------|------|------|
| [create-agent-skill](./create-agent-skill/) | 帮助用户创建符合规范的新 Agent Skill，包括目录结构和 SKILL.md 模板 | 1.0 |
| [gemini-image-gen](./gemini-image-gen/) | 使用 Gemini API 生成或编辑图片，支持自定义宽高比、分辨率和模型选择 | 1.0 |
| [md-illustration-inserter](./md-illustration-inserter/) | 为 Markdown 文章自动生成手绘风格插图并插入到对应位置 | 2.0 |
| [video-subtitle-extractor](./video-subtitle-extractor/) | 从 YouTube、Bilibili 等平台提取视频字幕，转换为可读文本 | 1.0 |

## ⚡ 一键安装（懒人版）

复制下面这段话，直接发给你的 AI Agent（Claude Code / Gemini CLI / Antigravity 等），即可自动完成安装：

```
帮我安装 Agent Skills：
1. 克隆仓库 https://github.com/CarGod/luffy-skills.git 到 ~/skills 目录（如果已存在则 git pull 更新）
2. 如果 ~/.gemini/antigravity/skills 不存在，创建符号链接指向 ~/skills
3. 安装 video-subtitle-extractor 的 Python 依赖：pip install -r ~/skills/video-subtitle-extractor/requirements.txt
4. 检查环境变量 GEMINI_ANTIGRAVITY_KEY 是否已设置，如果没有，提醒我去 https://aistudio.google.com/apikey 获取并配置
```

---

## 🚀 手动安装

### 1. 克隆仓库

```bash
git clone https://github.com/CarGod/luffy-skills.git
```

### 2. 配置为 Agent Skills 目录

将此目录配置为你的 AI Agent 的 Skills 搜索路径。例如，对于 Antigravity：

```bash
ln -s /path/to/luffy-skills ~/.gemini/antigravity/skills
```

### 3. 环境配置

部分 Skill 需要额外配置：

- **gemini-image-gen** / **md-illustration-inserter**：需要设置 `GEMINI_ANTIGRAVITY_KEY` 环境变量（[获取 API Key](https://aistudio.google.com/apikey)）
- **video-subtitle-extractor**：需要安装 Python 依赖（`pip install -r video-subtitle-extractor/requirements.txt`）

## 📁 项目结构

```
luffy-skills/
├── create-agent-skill/          # Skill 脚手架工具
│   └── SKILL.md
├── gemini-image-gen/            # Gemini 图片生成
│   ├── SKILL.md
│   ├── README.md
│   └── scripts/
│       └── generate_image.py
├── md-illustration-inserter/    # Markdown 文章配图
│   └── SKILL.md
└── video-subtitle-extractor/    # 视频字幕提取
    ├── SKILL.md
    ├── requirements.txt
    └── scripts/
        └── extract_subtitles.py
```

## 🤝 什么是 Agent Skill？

Agent Skill 是一个包含 `SKILL.md` 文件的目录，用于扩展 AI Agent 的能力。每个 Skill 通过结构化的指令告诉 Agent 何时使用、如何使用该技能，可以包含脚本、参考文档和资源模板。

详细规范请参考：[Agent Skills Specification](https://agentskills.io)

## 📄 License

MIT
