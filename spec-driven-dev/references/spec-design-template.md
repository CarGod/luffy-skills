# Design Tokens — {项目名称}

> 本文档定义项目的视觉设计系统。AI 在实现任何 UI 时必须严格遵循。

## 色彩体系 (Color Palette)

| 用途 | 色值 | 使用场景 |
|------|------|---------|
| 主色 (Primary) | `{#2563eb}` | 按钮、链接、高亮、活跃状态 |
| 主色悬停 | `{#1d4ed8}` | 主色元素的 hover 状态 |
| 副色 (Secondary) | `{#64748b}` | 次要文字、辅助图标 |
| 成功 | `{#10b981}` | 成功提示、在线状态 |
| 警告 | `{#f59e0b}` | 警告信息 |
| 危险 | `{#ef4444}` | 错误、删除操作 |
| 背景 (Base) | `{#ffffff}` | 页面主背景 |
| 背景 (Elevated) | `{#f8fafc}` | 卡片、模态框背景 |
| 边框 | `{#e2e8f0}` | 分割线、卡片边框 |

## 字体排版 (Typography)

| 元素 | 字体 | 大小 | 粗细 | 行高 |
|------|------|------|------|------|
| H1 标题 | {系统字体栈} | {28px} | {700} | {1.3} |
| H2 标题 | {同上} | {22px} | {600} | {1.4} |
| H3 标题 | {同上} | {18px} | {600} | {1.4} |
| 正文 | {同上} | {14px} | {400} | {1.6} |
| 小字/标签 | {同上} | {12px} | {500} | {1.5} |

## 间距与圆角 (Spacing & Radius)

| Token | 值 | 使用场景 |
|-------|-----|---------|
| `--space-xs` | {4px} | 元素内紧凑间距 |
| `--space-sm` | {8px} | 表单元素内边距 |
| `--space-md` | {16px} | 卡片内边距、段落间距 |
| `--space-lg` | {24px} | 区块间距 |
| `--space-xl` | {32px} | 页面级外边距 |
| `--radius-sm` | {4px} | 输入框、小按钮 |
| `--radius-md` | {8px} | 按钮、标签 |
| `--radius-lg` | {12px} | 卡片 |
| `--radius-xl` | {16px} | 模态框、弹窗 |

## 阴影 (Shadows)

| 层级 | 值 | 使用场景 |
|------|-----|---------|
| 低浮 | `{0 1px 3px rgba(0,0,0,0.1)}` | 卡片默认状态 |
| 中浮 | `{0 4px 12px rgba(0,0,0,0.1)}` | 卡片 hover、下拉菜单 |
| 高浮 | `{0 10px 25px rgba(0,0,0,0.15)}` | 模态框、Toast |

## 动效 (Animations)

| 效果 | 属性 | 使用场景 |
|------|------|---------|
| 默认过渡 | `{all 0.2s ease}` | 按钮、链接状态变化 |
| 弹性入场 | `{transform 0.3s cubic-bezier(0.16,1,0.3,1)}` | 模态框、Toast 出现 |
| 淡入 | `{opacity 0.15s ease}` | 列表项、页面切换 |

## 布局 (Layout)

| 属性 | 值 | 说明 |
|------|-----|------|
| 最大内容宽度 | `{1200px}` | 页面内容区域 |
| 侧边栏宽度 | `{240px}` | 左侧导航（如有） |
| 响应式断点 | `{768px}` | 移动端切换点 |
| 页面内边距 | `{24px}` | 内容区域左右 padding |

## 组件样式速查 (Component Quick Reference)

| 组件 | 默认样式 | Hover 样式 |
|------|---------|-----------|
| 主按钮 | `bg: Primary, color: #fff, radius: --radius-md` | `bg: Primary-hover, translateY(-1px)` |
| 次按钮 | `bg: transparent, border: 边框色, radius: --radius-md` | `bg: #f8fafc` |
| 输入框 | `border: 边框色, radius: --radius-sm, padding: --space-sm` | `border: Primary` |
| 卡片 | `bg: Elevated, radius: --radius-lg, shadow: 低浮` | `shadow: 中浮, translateY(-2px)` |
| 标签 (Badge) | `bg: Primary/10%, color: Primary, radius: 12px` | — |
