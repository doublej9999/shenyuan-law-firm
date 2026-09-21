# 深远律师事务所（Shenyuan Law Firm）技术重构方案
## Django + Vue 3 + Supabase 全栈架构升级设计

> **版本**：v1.0.0  
> **编写日期**：2025-09  
> **重构目标**：将现有的 FastAPI + 单文件原生 HTML + 本地 SQLite 单体架构，重构为 **Django（模块化后端） + Vue 3（现代工程化前端） + Supabase（云原生 PostgreSQL & Storage）** 的企业级涉外律所全栈解决方案。

---

## 一、 现状剖析与重构动机

### 1. 现有架构现状
- **后端架构**：近 5000 行的超长单文件（`app/main.py`），同时承担了 API 路由、数据库操作（裸写 SQL）、后台线程守护（CRM 提醒）、HTML 模板拼接与静态资源托管。
- **数据层**：采用本地文件型数据库 `data/lawyers.sqlite3`，高并发写入容易引发锁冲突，难以支撑多实例水平扩展；附件直接保存在本地硬盘 `data/files`。
- **前端架构**：以单文件 HTML（`index.html`, `admin.html`, `admin_content.html`, `admin_marketing.html`, `admin_research.html`）为主，混杂大量原生 JS、内嵌样式与 CDN 脚本，缺乏组件复用、模块化工程构建、状态管理及类型约束。
- **业务价值**：核心资产包含 **85+ 篇涉外法律专业文章**、多国出海指南、法务知识库、线索流转 CRM 与 AI 营销/调研助手，具备强烈的 **SEO 权重** 与 **商事线索转化** 属性。

### 2. 重构收益
1. **Django**：提供成熟的企业级 ORM、内置健壮的安全防御（CSRF、SQL 注入、XSS）、完善的用户与权限体系，并可通过模块化 App（`apps/`）将 5000 行单文件解耦为标准分层架构。
2. **Supabase (PostgreSQL + Storage)**：
   - 数据库升级为云原生 PostgreSQL，支持连接池（pgbouncer）、全文检索（`pg_trgm`）、原生 JSONB，支撑业务长期增长。
   - 文件上传迁移至 Supabase Storage，解决历史材料本地持久化安全与备份隐患。
3. **Vue 3 现代化改造**：
   - 前台支持中英双语、出海指南、咨询抽屉组件化，结合 SSR/SSG 保障 SEO 搜索引擎收录。
   - 管理后台基于 Vue 3 + Pinia + Element Plus / Tailwind 打造专业现代的 CRM + CMS 运营工作台。

---

## 二、 总体架构与选型设计

```
                    ┌────────────────────────────────────────────────────────┐
                    │                      Client Layer                      │
                    ├───────────────────────────┬────────────────────────────┤
                    │   前台涉外法律官网        │      律所管理运营后台      │
                    │  (Vue 3 + Vite / Nuxt 3)  │   (Vue 3 + Element Plus)   │
                    │  - 中英双语 (i18n)        │   - 客户线索 CRM 看板      │
                    │  - 85+ 篇法律专业文章     │   - 文章双语 CMS (Markdown)│
                    │  - 国别出海指南/案例/手册 │   - AI 法律检索 & 营销助手 │
                    │  - 智能线索收集/浮窗      │   - 统计报表 & CSV 导出    │
                    └─────────────┬─────────────┴──────────────┬─────────────┘
                                  │                            │
                            HTTPS │ RESTful / Ninja APIs       │ Bearer Token / JWT
                                  ▼                            ▼
                    ┌────────────────────────────────────────────────────────┐
                    │               Django Backend (Python 3.11+)            │
                    ├────────────────────────────────────────────────────────┤
                    │  - Django Ninja (高性能异步 API) / Django REST Framework│
                    │  - 核心模块: core, intakes(CRM), content(CMS),        │
                    │             research(KB&AI), marketing, notifications  │
                    │  - 限流排重中间件 (Redis / Django Cache)              │
                    │  - 异步任务: Celery / Django-Q (Resend 邮件, Webhook) │
                    └──────────────┬───────────────────────────┬─────────────┘
                                   │                           │
                    PostgreSQL 协议│                           │ S3 API / REST
                                   ▼                           ▼
                    ┌───────────────────────────┐ ┌──────────────────────────┐
                    │   Supabase PostgreSQL     │ │     Supabase Storage     │
                    │  - intakes, files         │ │  - 客户上传历史材料      │
                    │  - content_articles, vers │ │  - 营销物料与律师名片    │
                    │  - audit_log, search_log  │ │  - 微信二维码/静态资源   │
                    └───────────────────────────┘ └──────────────────────────┘
```

### 技术栈选型对比与决策

| 领域 | 选型 | 推荐方案 | 决策依据 |
| :--- | :--- | :--- | :--- |
| **后端框架** | Django 5.x | **Django + Django Ninja** | Django Ninja 基于 Pydantic 和类型提示，拥有类似 FastAPI 的极高开发体验和性能，天然兼容 Django ORM，省去 DRF 冗长配置。 |
| **数据库** | Supabase | **PostgreSQL (Direct / Session Pooler)** | Django 原生 `django.db.backends.postgresql`，连接 Supabase 的 PostgreSQL 实例（5432/6543 端口），无缝兼容 Django 迁移。 |
| **对象存储** | Supabase Storage | **django-storages 或 Supabase Python SDK** | 用于案件附件与媒体物料，安全可控，支持私有桶防盗链签名下载。 |
| **前台官网** | Vue 3 | **Nuxt 3 (推荐) 或 Vue 3 SSG (vite-ssg)** | **极其重要**：律所官网有 85+ 篇双语长文和高价值 SEO 需求，纯 SPA 会影响百度/Google/Bing 爬虫收录，Nuxt 3 SSR/SSG 可完整继承现有 SEO 优势。 |
| **管理后台** | Vue 3 | **Vue 3 + Vite + Pinia + Element Plus** | 纯 SPA 架构，界面美观、开发速度快，内置富文本/Markdown 编辑、线索拖拽看板、图表展示（ECharts）。 |

---

## 三、 数据库建模与 Supabase 迁移方案

### 1. 数据模型设计（对应 Django Models）

#### (1) `apps/intakes/models.py` —— 咨询线索与材料
```python
from django.db import models

class Intake(models.Model):
    STATUS_CHOICES = [
        ("new", "新线索"),
        ("contacted", "已联系"),
        ("processing", "处理中"),
        ("closed", "已结案"),
    ]
    name = models.CharField(max_length=100, verbose_name="姓名")
    email = models.EmailField(blank=True, null=True, verbose_name="邮箱")
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name="电话")
    matter = models.CharField(max_length=50, verbose_name="咨询事项类型")
    summary = models.TextField(verbose_name="案情简述")
    country_or_region = models.CharField(max_length=100, blank=True, null=True, verbose_name="国家/地区")
    language = models.CharField(max_length=10, default="zh", verbose_name="首选语言")
    user_agent = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new", db_index=True)
    note = models.TextField(blank=True, null=True, verbose_name="跟进备注")
    consent_at = models.DateTimeField(null=True, blank=True, verbose_name="隐私同意时间")
    score = models.IntegerField(default=0, verbose_name="意向评分")
    source = models.CharField(max_length=100, blank=True, null=True, db_index=True, verbose_name="渠道来源")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        db_table = "intakes"
        ordering = ["-created_at"]

class IntakeFile(models.Model):
    intake = models.ForeignKey(Intake, on_delete=models.CASCADE, related_name="files")
    original_name = models.CharField(max_length=255)
    storage_path = models.CharField(max_length=500, verbose_name="Supabase Storage 相对路径")
    size = models.BigIntegerField()
    content_type = models.CharField(max_length=100, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "intake_files"
```

#### (2) `apps/content/models.py` —— 文章与内容管理 (CMS)
```python
from django.db import models

class ContentArticle(models.Model):
    STATUS_CHOICES = [
        ("draft", "草稿"),
        ("reviewing", "待审核"),
        ("published", "已发布"),
        ("archived", "已下线"),
    ]
    slug = models.SlugField(max_length=200, unique=True)
    title_zh = models.CharField(max_length=255, default="")
    title_en = models.CharField(max_length=255, default="", blank=True)
    description_zh = models.TextField(default="", blank=True)
    description_en = models.TextField(default="", blank=True)
    body_zh = models.TextField(default="", blank=True)
    body_en = models.TextField(default="", blank=True)
    business = models.CharField(max_length=50, default="general")
    intent = models.CharField(max_length=10, default="I")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft", db_index=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "content_articles"

class ArticleVersion(models.Model):
    article = models.ForeignKey(ContentArticle, on_delete=models.CASCADE, related_name="versions")
    version = models.IntegerField()
    snapshot = models.JSONField(verbose_name="版本快照(JSONB)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content_article_versions"
        unique_together = ("article", "version")
```

#### (3) `apps/core/models.py` —— 审计与搜索统计
- `AuditLog`：记录管理后台操作人、IP、动作类别、详细 Diff 数据。
- `PageView`：轻量级全站 PV 访问转化记录。
- `SearchLog`：前台法律知识库搜索词与命中结果数，用于内容选题挖掘。

### 2. SQLite 到 Supabase PostgreSQL 数据平滑迁移
迁移脚本执行策略：
1. 读取原 `data/lawyers.sqlite3` 中的各表数据。
2. 批量将本地 `data/files/*` 自动通过 API 上传至 Supabase Storage 的私有 Bucket `intake-files`。
3. 建立映射并批量导入 Supabase PostgreSQL，确保自增主键（ID）序列正确无缝衔接。

---

## 四、 后端 Django 模块化架构规划

### 1. 目录结构
```text
backend/
├── manage.py
├── requirements.txt
├── shenyuan_legal/
│   ├── __init__.py
│   ├── settings/
│   │   ├── base.py          # 基础配置 (已集成 Supabase DB / 邮件 / 缓存)
│   │   ├── development.py   # 本地调试配置
│   │   └── production.py    # 生产安全配置
│   ├── urls.py              # 全局路由分发
│   ├── api.py               # Django Ninja 全局 API 实例
│   └── wsgi.py / asgi.py
├── apps/
│   ├── core/                # 通用中间件、限流、审计日志、基础基类
│   ├── intakes/             # 咨询线索、提交防刷、CRM 评分、逾期流转
│   ├── content/             # CMS 文章管理、Markdown 导入、版本控制、SEO Sitemap
│   ├── research/            # 法律知识库检索、AI 案情备忘录生成
│   ├── marketing/           # 营销文案生成、渠道投放打包、话题推荐
│   └── notifications/       # Resend 双语邮件、企业微信/飞书/钉钉 Webhook
└── scripts/
    └── migrate_sqlite_to_supabase.py
```

### 2. 核心服务重构要点
1. **API 接口规范（Django Ninja 路由设计）**：
   - `POST /api/intakes`：提交线索，集成 IP 限流中间件（默认 5次/分）和 24 小时排重机制。
   - `POST /api/intakes/chat`：引导式会话线索沉淀接口。
   - `GET /api/admin/intakes`：支持多条件筛选（状态、时间、搜索关键词、分页）。
   - `PATCH /api/admin/intakes/{id}`：跟进状态流转与备注更新。
   - `GET /api/admin/content/...`：完整 CMS 接口集（导入、回滚、草稿预览、批量审核与发布）。
   - `GET /api/admin/research/search` & `POST /memo`：知识库法律调研。
2. **异步与后台提醒服务解耦**：
   - 移除原 `app/main.py` 中随进程启动的粗暴 daemon thread `_crm_reminder_loop`。
   - 改为 Celery 定时任务（Celery Beat）或基于 Supabase Edge Functions / Django Management Command 结合系统 Cron 定时巡检逾期线索并推送报警通知。
3. **安全与认证体系**：
   - 引入 Django 原生用户体系配合 JWT Token，区分超级管理员、合伙人律师与助理角色。
   - 全局请求注入客户端真实 IP（正确识别反代头 `X-Forwarded-For`）。

---

## 五、 前端 Vue 3 工程化方案设计

### 1. 客户端前台（Public Portal - 推荐 Nuxt 3 或 Vite + Vue 3 SSG）
- **路由与多语言**：
  - 采用 `@nuxtjs/i18n` 或 `vue-i18n`，实现中英全站无缝切换：`/` (中文) 与 `/en/` (英文)。
  - 路由结构对齐现有业务：
    - `/` & `/en`：律所主页（涉外特色、核心合伙人、核心领域、客户评价）
    - `/services/:slug`：跨境争议解决、外商投资、涉外继承等业务专页
    - `/articles` & `/articles/:slug`：双语专业文章阅读器，支持 Markdown 渲染、右侧大纲导航、法律免责声明
    - `/countries/:slug`：全球出海国别落地法律指南
    - `/cases`、`/faq`、`/about`、`/fees`、`/privacy`、`/handbook`
- **在线咨询与转化模块**：
  - 全站底部常驻快速咨询表单，带 PIPL 个人信息保护合规勾选。
  - 右下角智能咨询浮窗（Chat Drawer）：交互式对话分步收集当事人诉求，直接调用后端 `/api/intakes/chat`。
- **SEO 保护机制**：
  - 使用 `useHead` 自动注入双语 `title`, `meta description`, Open Graph, JSON-LD 律师事务所结构化数据。
  - 后端动态生成 `/sitemap.xml`, `/robots.txt`, `/llms.txt`。

### 2. 运营管理后台（Admin Management Portal - Vue 3 + Vite + Element Plus）
目录设计：
```text
frontend-admin/
├── src/
│   ├── api/                 # 统一封装 axios/fetch API
│   │   ├── auth.ts
│   │   ├── intakes.ts       # CRM 相关接口
│   │   ├── content.ts       # CMS 文章与版本控制
│   │   └── research.ts      # 法律检索与营销
│   ├── components/          # 公共组件 (表格筛选、状态标签、Markdown 编辑器)
│   ├── views/
│   │   ├── login/           # Token/JWT 登录
│   │   ├── crm/             # 线索看板、跟进列表、评分详情、逾期警告、CSV 导出
│   │   ├── cms/             # 文章列表、双语编辑器、版本对比回滚、批量发布
│   │   ├── research/        # 法律法规/判例检索、AI 法律 Memo 生成工作台
│   │   └── marketing/       # 营销话题生成器、社交媒体文案打包下载
│   ├── stores/              # Pinia 状态管理 (user, app, settings)
│   └── router/              # Vue Router 鉴权守卫
```
- **核心交互亮点**：
  - **CRM 看板**：可使用拖拽式看板（Kanban）在“新线索 → 已联系 → 处理中 → 已结案”之间流畅流转。
  - **CMS 双语编辑器**：左中右三栏布局（中文编辑区、英文对照区、实时预览区），集成历史版本 Diff 比对，支持一键回滚。

---

## 六、 实施步骤与演进里程碑 (Milestones)

```
[Phase 1: 基础设施与数据] ──> [Phase 2: Django 后端搭建] ──> [Phase 3: Vue 后台开发] ──> [Phase 4: 前台官网重构] ──> [Phase 5: 部署上线]
```

1. **第 1 阶段：Supabase 环境配置与数据迁移**
   - 创建 Supabase 项目，获取 PostgreSQL 连接串与 API Key。
   - 创建 Storage 私有 Bucket（`intake-files`）。
   - 编写并运行 SQLite 到 PostgreSQL 数据迁移脚本，完成数据校验。
2. **第 2 阶段：Django 后端工程搭建与核心 API 重写**
   - 初始化 Django 5 项目，配置 Supabase PostgreSQL 连接。
   - 实现 `intakes`, `content`, `research`, `marketing`, `core` 模块 Models 与 Migrations。
   - 基于 Django Ninja 实现全套 REST 接口，移植限流、排重、Resend 邮件与 Webhook 发送。
   - 迁移 85 篇现有文章与 legal_kb 数据至 PostgreSQL。
3. **第 3 阶段：Vue 3 管理后台开发与对接**
   - 初始化 Vite + Vue 3 + Pinia + Element Plus 后台项目。
   - 实现线索管理（CRM 列表、详情、流转、逾期提醒、CSV 导出）。
   - 实现文章管理（CMS 编辑、Markdown 上传、版本回滚、发布流）。
   - 实现法律检索与营销文案生成界面对接。
4. **第 4 阶段：Vue 3 / Nuxt 3 客户端官网重构**
   - 搭建双语前台项目，复刻并组件化首页、服务、国别、文章阅读器、全站搜索等页面。
   - 实现咨询表单与智能咨询对话浮窗组件。
   - 配置 SEO Meta、Sitemap、Robots 动态生成。
5. **第 5 阶段：联调测试与容器化生产部署**
   - 编写单元测试覆盖核心逻辑（线索排重、限流、状态流转）。
   - 编写统一的 `Dockerfile` 与 `docker-compose.yml`（Nginx + Gunicorn/Uvicorn Django + 前端静态托管）。
   - 生产环境配置与正式上线切换。

---

## 七、 验收标准与回滚策略

### 1. 验收标准 (Definition of Done)
- **数据一致性**：SQLite 内所有历史线索、跟进记录、85 篇双语文章及历史版本无损导入 Supabase。
- **业务功能完整度**：
  - 前台提交咨询：成功入库 Supabase、触发 IP 限制、24 小时排重生效、自动收到 Resend 确认邮件、企业微信群机器人收到提醒。
  - 后台运营流：管理员登录、状态流转正常、备注追加正常、CSV 导出字段无乱码。
  - CMS 流程：在线编辑双语 Markdown、发布状态同步生效、历史版本回滚正确。
- **SEO 守恒**：双语文章与静态页面在 Lighthouse SEO 评分达到 95 分以上，Meta 标签、Canonical、OpenGraph、sitemap.xml 格式规范。

### 2. 回滚策略
- 保留现有的 `app/main.py` 与 `data/lawyers.sqlite3` 作为冷备运行环境。
- 新旧系统可在 Nginx 层面通过反向代理路由权重或蓝绿部署进行切换；若新系统上线出现异常，可瞬间切回原 FastAPI 服务。
