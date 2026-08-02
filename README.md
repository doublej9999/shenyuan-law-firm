# shenyuan-law-firm

一个最小可运行的 FastAPI 项目，使用现有 `index.html` 作为前端，并把咨询表单保存到 SQLite。

## 启动

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
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

## 接口

```text
GET /api/health
POST /api/intakes
```
