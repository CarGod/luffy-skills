# {项目中文名} — AI Agent 工作指引

## 项目结构

| 目录 | 职责 | 修改规则 |
|------|------|---------|
| `backend/` | 后端服务 | 业务代码在 `com.duodian.{appName}/` 下，SDK 目录只读 |
| `frontend/src/` | 前端页面 | 页面在 `pages/`，SDK 目录只读 |
| `specs/` | 项目设计文档 | 代码变更后同步更新对应 spec |

## 技术栈

- 后端：{后端技术栈}
- 前端：{前端技术栈}
- 数据库：MySQL (OceanBase 兼容)

## 核心约束

1. **SDK 目录只读** — `frontend/src/aulp-sdk/` 和 `backend/.../aulpsdk/` 禁止修改
2. **统一登录** — 使用 AULP SSO，禁止自建登录逻辑
3. **生产端口不可改** — `application-prod.yml` 的 `server.port: 8080` 禁止修改
4. **两种 Token 不能混用**：
   - `Authorization: Bearer {appToken}` —— 子应用自己的业务 JWT，业务 Controller 处理
   - `X-Aulp-Token: {aulpToken}` —— AULP 平台 Token，由 `AulpAuthFilter` 自动写入 `AulpTokenHolder`（ThreadLocal），SDK 内部使用，**业务代码不要碰**
5. **AI 调用必须通过 SDK 的三种模式之一**（详见 `aulp-ai` Skill）：
   - 槽位模式：`aulpAi.chatBySlot("chat", messages)` —— 平台决定模型，推荐
   - 原始透传：`aulpAi.rawProxy(path, body)` —— 子应用自己指定厂商接口路径
   - OpenAI 兼容：直接调 `/api/platform/ai/proxy/{slot}`，请求/响应符合 OpenAI 规范
   - **禁止**自己 new HttpClient 直连厂商，禁止在业务代码里手写 `request.getHeader("X-Aulp-Token")`
6. **AulpAuthFilter 只做 token 注入**：它不创建用户、不做权限校验，业务侧的用户体系自己维护
7. **跨线程调用 AI/OSS**（@Async、CompletableFuture、定时任务）：ThreadLocal **不会**自动跨线程传递，必须在主线程先 `String token = AulpTokenHolder.get()` 保存，然后调用带 token 参数的重载
8. {其他项目特定约束}

## 文档体系

| 文件 | 用途 |
|------|------|
| `specs/spec.md` | 全局架构与核心业务流 |
| `specs/spec-api.md` | REST API 详细设计 |
| `specs/spec-database.md` | 数据库表结构 |
| `specs/spec-ui.md` | 页面路由与组件 |

## 提交规范

格式：`类型(作者名)：中文描述`（冒号为中文全角）
