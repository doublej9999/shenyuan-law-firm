# 分支策略与自动部署（Branching & Deploy）

> 最后更新：2026-09-24

## 一、分支模型

| 分支 | 角色 | Vercel 环境 | 站点 |
| :--- | :--- | :--- | :--- |
| `main` | **生产（Production）** | Production | https://shenyuanlegal.com |
| `dev` | **预览（Preview）** | Preview | https://shenyuan-web-git-dev-doub.vercel.app |
| `feat/*` / `fix/*` | 功能开发 | Preview（自动） | 每次 push 生成临时预览 URL |

- 所有日常开发从 `dev` 切出特性分支，合回 `dev` 验证，再 `dev` → `main` 上线。
- `dev` 与 `main` 的差异即"待上线内容"。

## 二、自动部署由谁负责

**Vercel 原生 Git 集成**（已连接 `doublej9999/shenyuan-law-firm`），三个项目均已配置
`productionBranch = main`：

| Vercel 项目 | Root Directory | 域名 |
| :--- | :--- | :--- |
| `shenyuan-web` | `frontend-web` | shenyuanlegal.com |
| `shenyuan-backend` | 仓库根目录 | shenyuan-backend.vercel.app |
| `shenyuan-admin` | `frontend-admin` | shenyuan-admin.vercel.app |

行为：
- push 到 `main` → 自动 **Production** 部署并更新生产域名。
- push 到 `dev` 或任意其他分支 → 自动 **Preview** 部署，并生成分支别名
  `<project>-git-<branch-slug>-doub.vercel.app`。

> ⚠️ 历史上曾存在 `.github/workflows/deploy.yml`，它对**任意分支**执行
> `vercel deploy --prod`，会把非生产分支的代码直接推上生产域名，且与 Git 集成
> 重复构建。该工作流已删除。

## 三、GitHub Actions 的剩余职责

| 工作流 | 触发 | 作用 |
| :--- | :--- | :--- |
| `ci.yml` | push 到 `main` / `dev`、所有 PR | 运行 `pytest` |
| `keepalive.yml` | 定时（北京 08:00–24:00 每 10 分钟） | 保活后端 Serverless 实例 |
| `supabase-migrate.yml` | push 到 `main` 且 `supabase/**` 变更 | `supabase db push` 数据库迁移 |

**部署（backend / frontend-web / frontend-admin）不再由 Actions 负责。**

## 四、环境变量与作用域

- Vercel 项目环境变量按 `production` / `preview` / `development` 分开配置。
- 前端 API 地址：
  - 生产（`frontend-web`、`frontend-admin`）：`https://shenyuan-backend.vercel.app`
  - 预览：`https://shenyuan-backend-git-dev-doub.vercel.app`
- 后端敏感变量（`SUPABASE_DB_URL`、`DJANGO_SECRET_KEY`、`ADMIN_TOKEN` 等）目前
  同时作用于 production / preview / development，**预览与生产共用同一数据库**，
  预览环境请勿写入破坏性数据。

## 五、常用命令

```bash
# 查看 Vercel 项目与域名
vercel project ls
vercel project inspect shenyuan-web

# 查看 Git 集成状态（需 Vercel Token）
curl -s -H "Authorization: Bearer $VERCEL_TOKEN" \
  "https://api.vercel.com/v9/projects/<projectId>?teamId=team_baQbEk5gnm89oRwBuZzA7ppi"

# 手动触发一次生产部署
vercel --prod

# 查看 GitHub Actions 运行
gh run list --repo doublej9999/shenyuan-law-firm
```
