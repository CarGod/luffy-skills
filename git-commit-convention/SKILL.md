---
name: git-commit-convention
description: Git Commit 提交规范。当用户需要提交代码（git commit）时使用此 Skill，确保 commit 消息使用中文、格式规范、内容简洁且准确描述本次修改。
license: MIT
metadata:
  author: Luffy Liu
  version: "1.0"
---

# Git Commit 提交规范

## 使用场景

当用户说「提交代码」「commit」「push」时，**必须**遵循此 Skill 的规范来编写 commit 消息，并 push 到当前分支。

> **⚠️ 重要提醒：**
> 提交代码 = commit + push 到**当前分支**。如果用户需要合并分支，那是另一个独立操作，不在本 Skill 范围内。

## Commit 消息格式

```
类型(作者名)：改动点描述
```

**要求：**
- commit 消息**必须使用中文**
- 内容必须**简洁明了**，准确描述本次提交的修改内容
- 一行搞定，不需要多余的描述

## Commit 类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 (Feature) | `feat(luffy)：新增用户登录功能` |
| `fix` | 修复 Bug | `fix(luffy)：修复订单金额计算错误` |
| `docs` | 文档修改 | `docs(luffy)：更新 API 接口文档` |
| `style` | 代码格式修改（不影响逻辑） | `style(luffy)：统一代码缩进格式` |
| `refactor` | 重构（非新功能、非 Bug 修复） | `refactor(luffy)：重构用户服务层代码` |
| `perf` | 性能优化 | `perf(luffy)：优化首页加载速度` |
| `test` | 增加或修改测试代码 | `test(luffy)：补充支付模块单元测试` |
| `chore` | 构建过程或辅助工具变动 | `chore(luffy)：升级 webpack 到 v5` |
| `revert` | 回滚 | `revert(luffy)：回滚用户模块变更` |

## 操作步骤

### 1. 分析本次修改内容

在提交前，先执行以下命令查看本次修改：

```bash
# 查看修改了哪些文件
git status

# 查看具体改动内容
git diff --staged
```

### 2. 确定 Commit 类型

根据修改内容判断属于哪种类型：

- 新增了功能代码 → `feat`
- 修复了一个 Bug → `fix`
- 只改了文档 → `docs`
- 只调整了代码格式（空格、分号等） → `style`
- 重写了某段逻辑但功能不变 → `refactor`
- 提升了性能 → `perf`
- 增加或修改了测试 → `test`
- 修改了构建配置或工具 → `chore`
- 回滚了之前的提交 → `revert`

### 3. 获取作者名

通过 `git config user.name` 获取当前用户名，用于 commit 消息中的括号部分。

### 4. 编写 Commit 消息并提交

```bash
# 暂存修改
git add .

# 提交（消息必须是中文）
git commit -m "类型(作者名)：改动点描述"
```

### 5. Push 到当前分支

提交完成后，将代码 push 到远程的**当前分支**：

```bash
# push 到当前分支
git push origin HEAD
```

> **注意：这里只 push 到当前分支，不要执行合并操作。**

### 6. 多个不相关改动

如果本次暂存区包含多个不相关的改动，应当拆分为多次提交：

```bash
# 只暂存部分文件
git add src/user/login.js
git commit -m "feat(luffy)：新增用户登录功能"

git add src/order/payment.js
git commit -m "fix(luffy)：修复订单支付金额计算错误"
```

### 7. 检查 README 等文档

提交前，检查项目中是否有 README 或类似文档需要同步更新。如果本次修改涉及 README 中**已有内容**的变更（如功能列表、项目结构、版本号等），应一并更新。

> **注意：只更新 README 中已有的相关部分，不要擅自新增章节。**

## 好的 Commit 示例

```
feat(luffy)：新增用户注册手机号验证
fix(alex)：修复商品列表分页查询越界问题
docs(luffy)：补充部署文档中的环境变量说明
style(bob)：移除多余的空行和未使用的导入
refactor(luffy)：将订单状态机逻辑抽取为独立模块
perf(alex)：优化商品搜索接口响应速度
test(luffy)：补充用户服务的边界条件测试
chore(luffy)：升级 Node.js 版本至 v20
revert(luffy)：回滚商品价格计算逻辑变更
```

## 不好的 Commit 示例

```
❌ update                        → 太笼统，不知道改了什么
❌ fix bug                       → 没有说明修复了什么 Bug
❌ feat: add login               → 必须使用中文描述
❌ 修复了一个问题                  → 缺少类型和作者名
❌ feat(luffy)：修改了一些东西    → 描述不具体
```

## 注意事项

1. **commit 消息必须使用中文**，类型关键字（feat/fix 等）保持英文
2. **一次 commit 只做一件事**，避免将不相关的修改混在一起
3. **描述要具体**，让其他人看到 commit 消息就能理解改了什么
4. **冒号使用中文全角冒号 `：`**，类型和作者名之间无空格
