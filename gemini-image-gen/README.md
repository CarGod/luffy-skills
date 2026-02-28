# Gemini Image Gen

使用 Google Gemini API 生成或编辑图片的 Agent Skill。

## ✨ 功能

- 🎨 文本生成图片（Text-to-Image）
- ✏️ 基于参考图编辑（Image Editing）
- 📐 自定义宽高比（1:1 / 4:3 / 3:4 / 16:9 / 9:16）
- 🔍 高分辨率输出（1K / 2K / 4K）
- 🤖 多模型支持（Flash / Pro / 2.5-Flash）

## 📋 前置要求

- **Python 3.10+**
- **Gemini API Key**：需将 API Key 设置为环境变量 `GEMINI_ANTIGRAVITY_KEY`

```bash
# 添加到 ~/.zshrc 或 ~/.bashrc
export GEMINI_ANTIGRAVITY_KEY="your-api-key-here"
```

> 💡 获取 API Key：访问 [Google AI Studio](https://aistudio.google.com/apikey)

## 🚀 快速开始

```bash
# 生成一张 16:9 的风景图
python3 scripts/generate_image.py \
  --prompt "A Studio Ghibli style countryside scene with rolling green hills" \
  --aspect-ratio 16:9 \
  --output output.png

# 使用 Pro 模型生成 2K 高清图
python3 scripts/generate_image.py \
  --prompt "A cyberpunk cityscape at night" \
  --model pro \
  --image-size 2K \
  --output cyberpunk.png

# 基于已有图片编辑
python3 scripts/generate_image.py \
  --prompt "Add a rainbow in the sky" \
  --input-image original.png \
  --output edited.png
```

## 📁 目录结构

```
gemini-image-gen/
├── SKILL.md                      # Agent 指令文件
├── README.md                     # 使用说明（本文件）
└── scripts/
    └── generate_image.py         # 图片生成脚本
```

## 🤖 模型选择

| 模型 | 参数值 | 适用场景 | 特点 |
|------|--------|---------|------|
| Gemini 3.1 Flash | `flash` | 日常生成 | 速度快，性价比高 |
| Gemini 3 Pro | `pro` | 专业级输出 | 支持 4K，构图更精细 |
| Gemini 2.5 Flash | `2.5-flash` | 批量生成 | 速度最快 |

## 📄 License

MIT
