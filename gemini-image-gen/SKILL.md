---
name: gemini-image-gen
description: 使用 Gemini API 生成或编辑图片，支持指定宽高比（16:9、9:16、4:3 等）、分辨率（2K/4K）和模型选择。当需要生成图片且对宽高比、分辨率有要求，或需要基于参考图编辑图片时，使用此 Skill 代替内置 generate_image 工具。
license: MIT
metadata:
  author: Luffy Liu
  version: "1.0"
---

# Gemini Image Generation Skill

## 何时使用此 Skill

当满足以下**任一**条件时，优先使用此 Skill 而非内置 `generate_image` 工具：

- 需要指定图片宽高比（如 16:9、9:16、4:3、3:4）
- 需要高分辨率输出（2K / 4K）
- 需要基于参考图片进行编辑
- 需要使用特定 Gemini 模型（Flash / Pro）
- 用户明确要求使用 Gemini API 生图

---

## ⚠️ 使用前必须检查（Agent 必读）

在调用生成脚本之前，**必须**先通过以下命令检查环境变量是否已设置：

```bash
source ~/.zshrc 2>/dev/null; echo $GEMINI_ANTIGRAVITY_KEY | head -c 10
```

- 如果输出非空（如 `AIzaSyC-OX`），说明 Key 已配置，可以继续。
- 如果输出为空，**必须立即停止并提示用户**：
  > 未检测到 Gemini API Key。请先设置环境变量：
  > 1. 访问 [Google AI Studio](https://aistudio.google.com/apikey) 获取 API Key
  > 2. 在 `~/.zshrc` 或 `~/.bashrc` 中添加：`export GEMINI_ANTIGRAVITY_KEY="你的Key"`
  > 3. 重启终端或执行 `source ~/.zshrc`

---

## 环境要求

- **Python 3.10+**（脚本使用 `str | None` 类型注解）
- **环境变量**：`GEMINI_ANTIGRAVITY_KEY` 必须设置为有效的 Gemini API Key
- **无额外依赖**：脚本仅使用 Python 标准库（urllib, json, base64）

---

## 使用方法

通过 `run_command` 工具执行 Python 脚本。脚本路径：

```
gemini-image-gen/scripts/generate_image.py
```

### 基本参数

| 参数 | 缩写 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `--prompt` | `-p` | ✅ | 图片描述 | — |
| `--output` | `-o` | ❌ | 输出文件路径 | `./generated_image.png` |
| `--aspect-ratio` | `-ar` | ❌ | 宽高比：`1:1` `4:3` `3:4` `16:9` `9:16` | `1:1` |
| `--model` | `-m` | ❌ | 模型：`flash` `pro` `2.5-flash` | `flash` |
| `--image-size` | `-s` | ❌ | 分辨率：`1K` `2K` `4K`（仅 Gemini 3 模型） | 不设置 |
| `--input-image` | `-i` | ❌ | 参考图片路径（图片编辑模式） | 不设置 |

---

## 调用示例

### 1. 生成 16:9 宽屏图片

```bash
python3 gemini-image-gen/scripts/generate_image.py \
  --prompt "A Studio Ghibli style countryside scene with rolling green hills and a blue sky" \
  --aspect-ratio 16:9 \
  --output /tmp/ghibli_scene.png
```

### 2. 使用 Pro 模型生成 2K 高清图片

```bash
python3 gemini-image-gen/scripts/generate_image.py \
  --prompt "A cyberpunk cityscape at night with neon lights" \
  --model pro \
  --image-size 2K \
  --aspect-ratio 16:9 \
  --output /tmp/cyberpunk_2k.png
```

### 3. 基于参考图编辑

```bash
python3 gemini-image-gen/scripts/generate_image.py \
  --prompt "Add a rainbow in the sky and make the colors more vibrant" \
  --input-image /path/to/original.png \
  --output /tmp/edited.png
```

### 4. 生成 9:16 竖版图片（手机壁纸）

```bash
python3 gemini-image-gen/scripts/generate_image.py \
  --prompt "A serene Japanese garden with cherry blossoms" \
  --aspect-ratio 9:16 \
  --output /tmp/wallpaper.png
```

---

## 输出说明

- 脚本会将生成的图片保存到 `--output` 指定的路径
- 如果 API 返回多张图片，后续图片会以 `_1`、`_2` 后缀命名
- 脚本会打印图片的绝对路径，方便后续使用 `view_file` 查看或嵌入到 artifact 中
- 如果 API 同时返回文字，也会一并打印

## 模型选择建议

| 模型 | 适用场景 | 特点 |
|------|---------|------|
| `flash`（默认） | 日常图片生成 | 性价比最高，速度快 |
| `pro` | 专业级图片、复杂指令 | 支持 4K、思维链优化构图 |
| `2.5-flash` | 高并发批量生成 | 速度最快，1024px 分辨率 |

## 错误处理

- 如果 `GEMINI_ANTIGRAVITY_KEY` 未设置，脚本会报错并退出
- API 错误会打印详细的错误信息（HTTP 状态码 + 错误 JSON）
- 网络超时设置为 120 秒
