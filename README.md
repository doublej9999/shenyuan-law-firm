# shenyuan-law-firm

一个最小可运行的 FastAPI 项目，使用现有 `index.html` 作为前端，并把咨询表单保存到 SQLite。

## 启动

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

打开浏览器访问：

```text
http://127.0.0.1:8000
```

## 数据

咨询表单会保存到：

```text
data/lawyers.sqlite3
```

主要数据表：

```text
intakes
```

字段：`name`、`email`、`phone`、`matter`、`summary`、`country_or_region`（国家/地区，可选）、
`language`、`user_agent`、`created_at`、`status`（线索状态）、`note`（跟进备注）、
`consent_at`（隐私同意时间，提交时必须勾选同意）。

数据库使用 WAL 模式并设置 busy_timeout，支持单写多读并发；schema 变更通过
`PRAGMA user_version` 做版本化、非破坏性迁移（只加列，不删数据）。

## 接口

```text
GET  /api/health
POST /api/intakes
```

`POST /api/intakes` 有按 IP 的速率限制（默认每个 IP 每分钟 5 次），防止垃圾流量刷库。
部署在反向代理（Nginx / Caddy）后面时，限流依据 `X-Forwarded-For` 取真实客户端 IP。

`POST /api/intakes` 必须携带 `"consent": true`（隐私同意），否则返回 422。
同一邮箱或电话在 `DEDUPE_WINDOW_HOURS`（默认 24 小时）内重复提交会返回 409，
前端会提示“请勿重复提交”。

## 客户自动回复邮件（Resend）

配置 `RESEND_API_KEY` 后，提交成功会自动通过 **Resend API** 向客户发送中英双语
确认邮件（发件人默认 `no-reply@shenyuanlegal.com`，可用 `RESEND_FROM` 覆盖），附带
按事项类型区分的材料清单。未配置密钥时自动跳过；发送失败（含被 Resend 拒绝）只记
日志，不影响提交。

使用前需要在 Resend 控制台完成两件事：

1. **验证发件域名**：Domains → 添加 `shenyuanlegal.com` → 按提示添加 DNS 记录
   （SPF / DKIM），等待验证通过。
2. **创建 API Key**：API Keys → Create，复制 `re_` 开头的密钥填入 `RESEND_API_KEY`。

## 已上传材料（客户端上传入口已移除）

客户端文件上传功能已隐藏/停用（公开上传接口一并关闭）。如历史数据中存在已上传
的材料，后台仍可查看和下载：

```text
GET  /admin/api/intakes/{id}/files
GET  /admin/api/intakes/{id}/files/{file_id}/download
```

材料文件存放在 `data/files/`（不在 Web 根目录，已被 .gitignore 排除）。

## 新咨询通知（webhook）

配置环境变量 `NOTIFY_WEBHOOK_URL` 后，每次新咨询提交成功会自动推送一条文本消息。
默认格式兼容**企业微信群机器人**（群设置 → 添加群机器人 → 复制 Webhook 地址），
也可用于钉钉/飞书等自定义接口。通知失败只记日志，不影响表单提交。

## 管理后台

```text
GET  /admin                    # 后台页面（输入 ADMIN_TOKEN 登录）
GET  /admin/api/intakes        # 线索列表，支持 ?status= 过滤、?q= 搜索、?limit=
PATCH /admin/api/intakes/{id}  # 更新状态 / 备注，body: {"status": "...", "note": "..."}
```

线索状态流转：**新线索 → 已联系 → 处理中 → 已结案**。所有接口都需要
`Authorization: Bearer <ADMIN_TOKEN>` 请求头；`ADMIN_TOKEN` 未设置时整个后台禁用。
后台页面本身只是登录壳，数据接口全部带 token 鉴权。

## SEO 与转化分析

- **SEO**:首页含 Open Graph 标签、Twitter Card、canonical 和 LocalBusiness
  结构化数据（JSON-LD）；`GET /sitemap.xml` 自动生成站点地图。生产环境务必设置
  `SITE_URL`（如 `https://你的域名`），这些标签和地图里的链接都基于它生成。
- **独立服务落地页**:`/services/trade`、`/services/recovery`、`/services/legacy`
  三个页面，含各自的服务情形与材料清单，适合投放广告时直接链接。
- **转化分析**:后台首页显示累计/今日线索、今日访问量与转化率，由 `GET /admin/api/stats`
  提供；首页每次访问记一条匿名计数（仅时间戳，不采集任何个人信息）。

## 内容日历（150 篇 SEO 选题）

首页改版按《海外市场运营增长方案》的 8 区块结构落地（Hero / 信任徽章条 / 核心服务 /
处理路径 / 数据成果 / 案例展示 / 全球网络 / 律师团队 / 客户信任 / FAQ / 咨询入口）。
内容营销体系配套文档：

- `docs/content-calendar.md` — 40 周排期明细（每月主题 + 每周 3–4 篇，含中英双语标题
  与搜索意图分级），并含 20 条视频脚本排期。
- `docs/content-calendar.csv` — 同数据 CSV（UTF-8 BOM，Excel 直接打开），可导入
  Notion / Google Sheets / 飞书等排期工具。

生成脚本在 `docs/` 外维护（`/tmp/gen_calendar.py` 为一次性生成器，数据源见 md 首页说明）；
修改排期后如需重新生成 CSV，按 md 文件中的结构同步更新即可。

## 查看咨询记录（管理导出）

```text
GET /admin/intakes.csv
```

返回全部咨询记录（最新在前）的 CSV（含状态、备注、同意时间），带 UTF-8 BOM（Excel
直接打开不乱码）。需要 `Authorization: Bearer <ADMIN_TOKEN>` 请求头；`ADMIN_TOKEN`
未设置时该接口默认禁用（返回 401）。建议设置一个足够强的随机值，例如：

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 测试

```powershell
pip install -r requirements-dev.txt
pytest
```

覆盖 schema 迁移（全新库 / 旧库三种状态）、字段校验、API 增删查和限流。

## 依赖锁定

`requirements.txt` 声明版本范围，`requirements.lock` 是 `pip-compile` 生成的精确
锁定版本，Docker 构建即使用它保证可复现。修改依赖后重新生成：

```bash
pip install pip-tools
pip-compile requirements.txt -o requirements.lock --strip-extras --no-annotate
```

## 部署提示

- 生产环境建议单 worker + `--proxy-headers`（配合反向代理获取真实 IP）：
  `uvicorn app.main:app --proxy-headers`
- 若使用多 worker，SQLite 仍是单文件写入瓶颈，WAL + busy_timeout 已缓解锁冲突。
- 咨询数据包含个人隐私，请定期备份 `data/` 目录，并确保该目录不可被 Web 静态访问。
- 设置 `APP_ENV=production` 会关闭 `/docs`、`/redoc` 和 `/openapi.json`（避免泄露接口 schema）。

## Docker / 1Panel 部署

```bash
docker compose up -d --build
```

容器内以非 root 用户运行，数据保存在命名卷 `intake-data`。在 compose 文件同目录的
`.env` 中配置（参考 `.env.example`）：

```text
ADMIN_TOKEN=这里填随机令牌
NOTIFY_WEBHOOK_URL=企业微信机器人Webhook地址（可选）
```

1Panel 中可直接作为“Docker Compose 应用”导入 `docker-compose.yml`，然后在应用环境
变量里填 `ADMIN_TOKEN` 和 `NOTIFY_WEBHOOK_URL`。

## 运维脚本（备份 / 清理 / 告警）

```text
scripts/backup.sh          # SQLite + 上传文件备份，保留最近 BACKUP_KEEP（默认14）份
scripts/prune_intakes.py   # 删除超过 N 天的旧线索（含上传文件），需 --older-than + --yes
scripts/watchdog.sh        # 磁盘/数据库体积告警，超过阈值推送到 webhook
```

建议 crontab 配置（按需修改路径）：

```cron
0 3 * * *  /path/to/shenyuan-law-firm/scripts/backup.sh
0 4 1 * *  /path/to/.venv/bin/python /path/to/shenyuan-law-firm/scripts/prune_intakes.py --older-than 365 --yes
*/15 * * * * /path/to/shenyuan-law-firm/scripts/watchdog.sh
```

清理是破坏性操作：先 `--dry-run` 预览，再 `--yes` 执行；每次删除都会写入审计日志。
备份目录 `backups/` 已加入 `.gitignore`。

## 数据保留与审计

- 所有后台敏感操作（导出、状态/备注修改、鉴权失败、清理删除）都会写入 `audit_log`
  表：时间、来源 IP、动作、详情。建议定期检查，尤其是 `auth_failed` 条目。
- 咨询数据包含个人隐私，请按业务需要设置保留期（用 `prune_intakes.py` 执行清理），
  并在 README/隐私说明中写明保留政策。
