---
name: md-illustration-inserter
description: 为 Markdown 格式的公众号文章自动生成并插入手绘简约风格的中文插图。使用 gemini-image-gen Skill 调用 Gemini API 生成 16:9 横版配图，并将图片插入到 Markdown 文件的对应位置。当用户要求为 Markdown 文章配图、添加插图、或美化公众号文章时，使用此 Skill。
license: MIT
metadata:
  author: Luffy Liu
  version: "2.0"
---

# Markdown 文章插图生成器

## 何时使用此 Skill

当用户满足以下任一场景时，激活此 Skill：

- 要求为 Markdown（.md）文章添加插图 / 配图
- 要求美化公众号文章、让文章图文并茂
- 提供了一篇 Markdown 文件并希望插入适当数量的图片
- 提到"手绘风格"、"简约插图"、"文章配图"等关键词

---

## 第一步：分析文章结构

1. 使用 `view_file` 工具读取用户提供的 Markdown 文件的全部内容。
2. **解析文章的层级结构**，识别以下元素：
   - `#` 一级标题（文章标题）
   - `##` 二级标题（主要章节）
   - `###` 三级标题（子章节）
   - 普通段落文本
   - 已有的图片（`![](...)` 语法）
   - 代码块、引用块等特殊元素
3. **统计文章规模**：总字数、段落数量、章节数量。

---

## 第二步：制定插图计划

根据文章结构和长度，制定一个合理的插图计划。遵循以下规则：

### 插图密度规则

| 文章总字数 | 建议插图数量 | 说明 |
|-----------|------------|------|
| < 800 字 | 1-2 张 | 开头题图 + 可选结尾图 |
| 800-2000 字 | 2-4 张 | 题图 + 每个主要章节 1 张 |
| 2000-4000 字 | 4-6 张 | 题图 + 关键章节配图 |
| 4000-8000 字 | 6-8 张 | 题图 + 各章节配图 + 转场图 |
| > 8000 字 | 8-12 张 | 按需分布，避免图片荒漠 |

### 插图位置规则

插图应插入到**标题的下方、正文段落的上方**，具体遵循以下优先级：

1. **文章开头**（必须）：在一级标题 `#` 之后，正文之前，插入一张**题图/封面图**，概括文章主题。
2. **每个二级标题 `##` 之后**（强烈建议）：在二级标题之后插入一张匹配该章节核心概念的插图。
3. **三级标题 `###` 之后**（视长度而定）：如果某个二级章节内有多个三级标题且内容较长（超过 500 字），可以选择性地为部分三级标题配图。
4. **长段落之间**（可选补充）：如果两个标题之间的正文连续超过 800 字且没有任何插图，可以在适当的段落分界处插入一张过渡插图。
5. **文章结尾**（可选）：在文章末尾可以插入一张总结性/收尾性的插图。

### 不应插入图片的位置

- 代码块内部或紧邻代码块的位置
- 已有图片的紧邻位置（避免图片堆叠）
- 引用块内部
- 列表项之间（除非列表特别长）

---

## 第三步：为每张插图设计提示词

对于每一张计划中的插图，根据对应段落的内容，构造高质量的提示词。

### 核心风格模板（必须严格遵循）

每张图片的提示词**必须**以下面的风格前缀开始：

```
Full-bleed hand-drawn sketch illustration that fills the entire image.
Clean white background with very subtle light gray texture.
Soft watercolor wash accents in gentle tones (soft blue, sage green, light coral, lavender, peach).
Simple doodle-style icons and elements with thin ink outlines.
Balanced composition that utilizes the full width and height of the canvas.
Cute, friendly, and approachable visual tone.
Small decorative elements scattered around: tiny stars ✦, sparkles, dots, and simple shapes.
Chinese text labels rendered in a casual handwritten font style.
The overall feel is like a beautifully illustrated notebook page or mind-map sketch.
```

### 提示词构造规则

在风格前缀之后，根据段落内容添加具体的画面描述：

1. **提取核心概念**：从对应段落中提取 1-3 个核心关键词或概念。
2. **转化为视觉隐喻**：将抽象概念转化为具体的视觉元素。例如：
   - "数据流转" → 箭头连接的文件框和数据库图标
   - "团队协作" → 多个小人图标通过线条连接
   - "安全性" → 盾牌和锁的图标
   - "性能优化" → 火箭或速度仪表盘图标
   - "用户体验" → 手机界面草图和笑脸
   - "API 接口" → 齿轮和连接管道图标
3. **添加中文标注**：在提示词中明确要求图中包含 1-3 个与内容相关的中文关键词标注。使用格式：`Chinese text labels reading "关键词1", "关键词2"`。
4. **指定构图方式**：根据内容选择合适的构图：
   - **概念图/思维导图**：适合介绍多个相关概念的段落
   - **流程图**：适合描述步骤、流程的段落
   - **对比图**：适合对比两个事物的段落
   - **单一图标聚焦**：适合介绍一个核心概念的段落
   - **场景图**：适合描述具体使用场景的段落

### 提示词示例

**示例 1：文章题图 - 关于 AI Agent 开发的文章**
```
Full-bleed hand-drawn sketch illustration that fills the entire image. Clean white background with very subtle light gray texture. Soft watercolor wash accents in gentle tones (soft blue, sage green, light coral, lavender). Simple doodle-style icons with thin ink outlines. Balanced composition that utilizes the full width and height of the canvas. Cute, friendly visual tone. Small decorative stars and sparkles scattered around.

Central concept: An adorable robot character with a lightbulb above its head, surrounded by floating code snippets, chat bubbles, and gear icons. Dashed arrows connect different elements showing a workflow. Chinese text labels reading "AI 智能体", "自动化", "协作". The composition is like a mind-map centered around the robot.
```

**示例 2：章节配图 - 关于消息路由的段落**
```
Full-bleed hand-drawn sketch illustration that fills the entire image. Clean white background with very subtle light gray texture. Soft watercolor wash accents in gentle tones (soft blue, sage green, light coral, lavender). Simple doodle-style icons with thin ink outlines. Balanced composition that utilizes the full width and height of the canvas. Decorative dots and tiny stars.

A message envelope icon on the left with dashed arrows branching out to three different destination boxes on the right, each with a small icon (a person, a gear, a book). The arrows are labeled with small tags. Chinese text labels reading "消息路由", "精准分发". A small target/bullseye icon near the bottom.
```

**示例 3：流程类配图 - 关于部署步骤的段落**
```
Full-bleed hand-drawn sketch illustration that fills the entire image. Clean white background with very subtle light gray texture. Soft watercolor wash accents in gentle tones (soft blue, sage green, light coral, lavender). Simple doodle-style icons with thin ink outlines. Balanced composition that utilizes the full width and height of the canvas.

A horizontal flow from left to right: a code editor icon → an arrow → a box labeled with gears (build) → an arrow → a cloud icon (deploy) → an arrow → a rocket launching upward. Each step has a circled number (①②③④). Chinese text labels reading "编写代码", "构建", "部署", "上线". Small celebratory sparkles around the rocket.
```

---

## 第四步：检查环境变量并生成图片

在生成图片之前，必须确保环境变量 `GEMINI_ANTIGRAVITY_KEY` 存在。

1. **检查密钥**：先执行 `echo $GEMINI_ANTIGRAVITY_KEY` 或通过 Python 环境检查密钥是否已配置。
2. **处理缺失情况**：如果不存在，应向用户询问该密钥，或者询问去哪个配置文件里读取，**不要盲目执行 `source ~/.zshrc`**（可能导致脚本挂起）。获取到密钥后，在命令前加上 `export GEMINI_ANTIGRAVITY_KEY="..."`。
3. **调用生成脚本**：如果密钥已存在环境或通过 export 配置好后，使用 `run_command` 工具调用生成脚本：

```bash
python3 gemini-image-gen/scripts/generate_image.py \
  --prompt "<提示词>" \
  --aspect-ratio 16:9 \
  --output "<Markdown文件目录>/assets/illustration_01_xxx.png"
```

### 调用规范

- **--prompt**：使用第三步中构造的完整提示词（风格前缀 + 具体内容描述）。
- **--aspect-ratio**：固定使用 `16:9`，生成横版配图。
- **--output**：直接输出到 Markdown 文件同级的 `assets/` 目录，文件名格式为 `illustration_章节编号_关键词.png`，例如 `illustration_01_overview.png`、`illustration_02_routing.png`。
- **--model**：默认使用 `flash`，如需更高质量可使用 `pro`。
- **如果生成效果不理想**：调整提示词后重新生成，但不要超过 2 次重试。

> **⚠️ 重要**：调用脚本时，环境里必须要有 `GEMINI_ANTIGRAVITY_KEY` 变量。如环境变量未准备好，需用 `export GEMINI_ANTIGRAVITY_KEY="xxx"; python3 ...` 方式执行。

### 生成顺序

按照插图在文章中出现的顺序依次生成。

### 调用示例

```bash
# 先创建 assets 目录
mkdir -p "<Markdown文件目录>/assets"

# 假设环境变量已存在，直接调用生成题图
python3 gemini-image-gen/scripts/generate_image.py \
  --prompt "Wide landscape composition... Central concept: An adorable robot..." \
  --aspect-ratio 16:9 \
  --output "<Markdown文件目录>/assets/illustration_01_overview.png"

# 生成章节配图
python3 gemini-image-gen/scripts/generate_image.py \
  --prompt "Wide landscape composition... A message envelope icon..." \
  --aspect-ratio 16:9 \
  --output "<Markdown文件目录>/assets/illustration_02_routing.png"
```

---

## 第五步：将图片插入 Markdown 文件

使用 `multi_replace_file_content` 或 `replace_file_content` 工具将图片引用插入到 Markdown 文件中。

### 插入格式（使用相对路径）

```markdown
![插图描述](assets/illustration_01_xxx.png)
```

> **重要**：必须使用**相对路径**（`assets/xxx.png`），不要使用绝对路径。这样可以确保图片在 Obsidian、GitHub、以及其他 Markdown 渲染器中都能正常显示。

### 插入位置规范

- 图片引用独占一行
- 图片引用的**上方**留一个空行
- 图片引用的**下方**留一个空行
- 图片描述（alt text）使用简短的中文描述，概括图片内容

### 插入示例

原始 Markdown：
```markdown
## 消息路由机制

当系统收到一条新消息时，首先需要判断该消息应该被发送到哪个通道...
```

插入后：
```markdown
## 消息路由机制

![消息路由流程示意图](assets/illustration_02_routing.png)

当系统收到一条新消息时，首先需要判断该消息应该被发送到哪个通道...
```

---

## 第六步：最终检查

完成所有图片插入后，执行以下检查：

1. **再次 `view_file` 查看修改后的 Markdown 文件**，确保：
   - 所有图片路径正确（使用相对路径 `assets/xxx.png`）
   - 图片文件确实存在于 `assets/` 目录中
   - 图片分布均匀，没有"图片荒漠"（连续超过 800 字无图）
   - 没有图片堆叠（两张图片之间不足 200 字）
   - Markdown 语法正确，无格式错误
2. **向用户报告**：列出生成的图片数量、每张图片的位置和描述。

---

## 注意事项

- **不要修改文章的文字内容**：只插入图片引用，不要修改、删除或重新排列任何原有文字。
- **图片直接生成到目标目录**：使用 `--output` 参数直接将图片输出到 `assets/` 目录，无需额外复制步骤。
- **图片格式**：生成的图片为 PNG 格式。
- **图片比例**：通过 `--aspect-ratio 16:9` 参数直接生成 16:9 横版图片，无需裁剪。
- **已有图片处理**：如果文章中已有一些图片，在计算插图数量时应将已有图片计入，避免过度插图。
- **尊重文章风格**：技术文章的配图应偏向示意图和流程图风格；叙事性文章的配图可以更具场景感；观点性文章的配图可以更加抽象和隐喻化。
- **iCloud 兼容性**：向 iCloud 同步目录生成文件时，请逐个生成，避免并发操作导致问题。
