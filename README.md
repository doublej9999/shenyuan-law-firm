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
`language`、`user_agent`、`created_at`。

数据库使用 WAL 模式并设置 busy_timeout，支持单写多读并发；schema 变更通过
`PRAGMA user_version` 做版本化、非破坏性迁移（只加列，不删数据）。

## 接口

```text
GET  /api/health
POST /api/intakes
```

`POST /api/intakes` 有按 IP 的速率限制（默认每个 IP 每分钟 5 次），防止垃圾流量刷库。
部署在反向代理（Nginx / Caddy）后面时，限流依据 `X-Forwarded-For` 取真实客户端 IP。

## 查看咨询记录（管理导出）

```text
GET /admin/intakes.csv
```

返回全部咨询记录（最新在前）的 CSV，带 UTF-8 BOM（Excel 直接打开不乱码）。
需要 `Authorization: Bearer <ADMIN_TOKEN>` 请求头；`ADMIN_TOKEN` 未设置时该接口
默认禁用（返回 401）。建议设置一个足够强的随机值，例如：

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
```

1Panel 中可直接作为“Docker Compose 应用”导入 `docker-compose.yml`，然后在应用环境
变量里填 `ADMIN_TOKEN`。
