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

## 测试

```powershell
pip install -r requirements-dev.txt
pytest
```

覆盖 schema 迁移（全新库 / 旧库三种状态）、字段校验、API 增删查和限流。

## 部署提示

- 生产环境建议单 worker + `--proxy-headers`（配合反向代理获取真实 IP）：
  `uvicorn app.main:app --proxy-headers`
- 若使用多 worker，SQLite 仍是单文件写入瓶颈，WAL + busy_timeout 已缓解锁冲突。
- 咨询数据包含个人隐私，请定期备份 `data/` 目录，并确保该目录不可被 Web 静态访问。
