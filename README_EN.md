# 🧩 Luffy Skills

[中文](./README.md)

> A collection of open-source AI Agent Skills following the [Agent Skills Specification](https://agentskills.io). These skills can be loaded and used by any compatible AI agent.

## 📦 Available Skills

| Skill | Description | Version |
|-------|-------------|---------|
| [create-agent-skill](./create-agent-skill/) | Scaffolds new Agent Skills with proper directory structure and SKILL.md template | 1.0 |
| [gemini-image-gen](./gemini-image-gen/) | Generate or edit images via Gemini API with custom aspect ratios, resolutions, and model selection | 1.0 |
| [md-illustration-inserter](./md-illustration-inserter/) | Auto-generate hand-drawn style illustrations and insert them into Markdown articles | 2.0 |
| [video-subtitle-extractor](./video-subtitle-extractor/) | Extract subtitles from YouTube, Bilibili, and other platforms via yt-dlp | 1.0 |

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/CarGod/luffy-skills.git
```

### 2. Configure as Agent Skills Directory

Point your AI Agent's skills search path to this directory. For example, with Antigravity:

```bash
ln -s /path/to/luffy-skills ~/.gemini/antigravity/skills
```

### 3. Environment Setup

Some skills require additional configuration:

- **gemini-image-gen** / **md-illustration-inserter**: Set the `GEMINI_ANTIGRAVITY_KEY` environment variable ([Get API Key](https://aistudio.google.com/apikey))
- **video-subtitle-extractor**: Install Python dependencies (`pip install -r video-subtitle-extractor/requirements.txt`)

## 📁 Project Structure

```
luffy-skills/
├── create-agent-skill/          # Skill scaffolding helper
│   └── SKILL.md
├── gemini-image-gen/            # Gemini image generation
│   ├── SKILL.md
│   ├── README.md
│   └── scripts/
│       └── generate_image.py
├── md-illustration-inserter/    # Markdown illustration inserter
│   └── SKILL.md
└── video-subtitle-extractor/    # Video subtitle extraction
    ├── SKILL.md
    ├── requirements.txt
    └── scripts/
        └── extract_subtitles.py
```

## 🤝 What is an Agent Skill?

An Agent Skill is a directory containing a `SKILL.md` file that extends an AI Agent's capabilities. Each skill provides structured instructions telling the agent when and how to use it, and may include scripts, reference documentation, and resource templates.

Learn more: [Agent Skills Specification](https://agentskills.io)

## 📄 License

MIT
