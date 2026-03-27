# {项目名称}

> 一句话定位：{用一句话描述这个系统解决什么问题}

## 身份卡片 (Identity)

| 属性 | 值 |
|------|-----|
| 项目名 | {英文标识，如 `smart-attendance`} |
| 中文名 | {中文名称} |
| 技术栈 | {如：Spring Boot 3 + React 18 + MySQL} |
| 当前版本 | {如：1.0.0} |
| 最后更新 | {日期} by {操作者} |

## 全局约束 (Global Constraints)

> ⚠️ 以下规则在任何开发过程中都**绝对不可违反**。

| # | 约束 | 说明 |
|---|------|------|
| 1 | {如：只用 Vanilla CSS} | {不使用 Tailwind/Bootstrap 等框架} |
| 2 | {如：时间格式统一 UTC} | {前端展示时转换为本地时区} |
| 3 | {如：API 响应统一格式} | `{code, data, message}` |
| 4 | {如：禁止修改 SDK 目录} | `aulp-sdk/` 由平台维护 |

## 架构拓扑 (Directory Topology)

> 每个目录的**设计意图**和**修改规则**。

| 目录 | 职责 | 修改规则 |
|------|------|---------|
| `backend/src/.../controller/` | REST 接口层 | 每个文件对应一个业务模块 |
| `backend/src/.../service/` | 业务逻辑层 | 禁止直接操作 HTTP 请求/响应 |
| `backend/src/.../entity/` | 数据库实体 | 与表一一对应，改动须同步 `spec-database.md` |
| `frontend/src/pages/` | 页面级组件 | 一个文件对应一个路由 |
| `frontend/src/components/` | 可复用 UI 组件 | 禁止包含业务逻辑 |
| `frontend/src/aulp-sdk/` | ⛔ 平台 SDK | **禁止修改** |

## 数据模型概览 (Data Model Overview)

> 📖 详细设计：[spec-database.md](spec-database.md)

| 表名 | 核心字段 | 关联 | 业务含义 |
|------|---------|------|---------|
| {users} | {id, name, role} | {→ departments} | {用户主表} |
| ... | ... | ... | ... |

## 核心业务流 (Core Flows)

> 📖 详细逻辑：[spec-logic.md](spec-logic.md)

### 流程 1：{流程名称}

1. {用户触发动作}
2. {前端调用 API}
3. {后端校验逻辑}
4. {数据库操作}
5. {返回结果}

### 流程 2：{流程名称}

1. ...

## 页面路由 (Routes)

> 📖 详细设计：[spec-ui.md](spec-ui.md) | 视觉规范：[spec-design.md](spec-design.md)

| 路由 | 页面名称 | 核心功能 |
|------|---------|---------|
| `/` | {首页} | {功能描述} |
| `/detail/:id` | {详情页} | {功能描述} |
| ... | ... | ... |

## API 概览 (API Overview)

> 📖 详细设计：[spec-api.md](spec-api.md)

| Method | Path | 功能 | 鉴权 |
|--------|------|------|------|
| GET | `/api/xxx` | {列表查询} | {Token} |
| POST | `/api/xxx` | {新建} | {Token} |
| ... | ... | ... | ... |

## 开发日志 (Changelog)

| 日期 | 版本 | 变更内容 | 操作者 |
|------|------|---------|--------|
| {YYYY-MM-DD} | {1.0.0} | {初始版本，包含核心功能} | {AI-Agent} |
