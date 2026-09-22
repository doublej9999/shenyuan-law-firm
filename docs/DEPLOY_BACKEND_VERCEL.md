# 后端 (Django) 部署至 Vercel 指南

深远律师事务所管理后端基于 **Django 5 + Django Ninja + Supabase (PostgreSQL)** 构建。已全面适配为 Vercel Serverless Function 架构，彻底解决 Render 免费容器休眠与冷启动慢的问题。

---

## 1. 核心变更概览

- **部署入口**：`backend/shenyuan_legal/wsgi.py`（已注入根目录模块路径并暴露 `app = application`）
- **配置文件**：`backend/vercel.json`（采用 `@vercel/python`，配置 Python 3.11 及全局路由转发）
- **废弃清理**：已移除旧的 `render.yaml` 容器配置
- **前端联动**：`frontend-admin/.env.production` 和 `frontend-web/.env.production` 中的 API 指向已更新为 Vercel 域名占位符

---

## 2. Vercel 部署步骤 (两种方式)

### 方式 A：通过 Vercel Web 控制台导入（推荐）

1. 打开 [Vercel Dashboard](https://vercel.com/dashboard)，点击 **Add New... -> Project**。
2. 选择该 GitHub 代码仓库并点击 **Import**。
3. 在 **Configure Project** 页面：
   - **Project Name**：例如 `shenyuan-backend`（或自定义名称）
   - **Framework Preset**：选择 **Other**
   - **Root Directory**：点击 **Edit**，选择并设置为 `backend` 目录（**关键步骤！**）
4. 展开 **Environment Variables**，添加下列生产环境变量（参见第 3 节）。
5. 点击 **Deploy** 开始部署。

### 方式 B：通过 Vercel CLI 命令行部署

```bash
cd backend
# 登录并部署预览版
npx vercel
# 部署到生产环境
npx vercel --prod
```

---

## 3. 环境变量配置清单 (Vercel Project Settings)

请在 Vercel 项目的 **Settings -> Environment Variables** 中配置以下变量：

| 环境变量名 | 必填 | 示例/说明 |
|---|---|---|
| `DJANGO_SECRET_KEY` | 是 | 生产随机安全密钥，例如 `prod-django-key-xxxx-yyyy-zzzz` |
| `DEBUG` | 是 | 设置为 `False` |
| `SUPABASE_DB_URL` | **是** | **必须使用 Supabase 连接池 (Transaction 模式, 端口 6543)**，例如：<br>`postgres://postgres.[ref]:[password]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres` |
| `SUPABASE_URL` | 是 | Supabase 项目 URL，例如 `https://jaevfeneyjcvljwgmfxv.supabase.co` |
| `SUPABASE_KEY` | 是 | Supabase `service_role` 密钥或 `anon` 密钥 |
| `ADMIN_TOKEN` | 是 | 管理员鉴权 Token（如 `shenyuan-admin-prod-2025`） |
| `SUPABASE_STORAGE_BUCKET` | 否 | 附件 Bucket 名称（默认为 `intake-files`） |
| `RESEND_API_KEY` | 否 | 邮件通知服务密钥（如果有） |
| `NOTIFY_WEBHOOK_URL` | 否 | 飞书/企微/钉钉机器人通知 Webhook |

> ⚠️ **关于数据库连接池的重要警告**：
> Vercel Serverless 函数在高并发时会同时拉起数十个无状态实例。**切勿使用直连端口 5432**，务必在 Supabase 控制台的 `Database Settings -> Connection Pooling` 中复制 **Transaction Mode (端口 6543)** 的连接串配置为 `SUPABASE_DB_URL`。

---

## 4. 数据库迁移 (Migrations) 执行方式

Vercel Serverless 构建阶段不会执行 `python manage.py migrate`。请在有数据库访问权限的本地环境中执行迁移：

```bash
# 进入 backend 目录
cd backend

# 配置本地环境变量或在 .env 中设置好 SUPABASE_DB_URL
python manage.py migrate
```

---

## 5. 前端 API 域名联动

部署完成后，Vercel 会为后端生成形如 `https://shenyuan-backend.vercel.app` 的生产域名。
请确保：
1. 访问 `https://<your-backend>.vercel.app/api/health`，确认返回 `status: ok` 及数据库连接成功。
2. 将该真实域名回填至前端项目的环境变量：
   - `frontend-admin/.env.production` -> `VITE_API_URL`
   - `frontend-web/.env.production` -> `VITE_API_URL`
3. 重新部署 `frontend-admin` 与 `frontend-web`。
