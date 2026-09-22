import os
import sys
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
REPO_DIR = BASE_DIR.parent
load_dotenv(BASE_DIR / ".env")
load_dotenv(REPO_DIR / ".env")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-shenyuan-legal-firm-secret-key-2025")
DEBUG = os.environ.get("DEBUG", "True").lower() in ("true", "1", "yes")
ALLOWED_HOSTS = ["*"]

# Vercel 反向代理 SSL 终结感知与 Host 信任
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "apps.core",
    "apps.intakes",
    "apps.content",
    "apps.research",
    "apps.marketing",
    "apps.notifications",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.core.middleware.ClientIpMiddleware",
]

ROOT_URLCONF = "shenyuan_legal.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "shenyuan_legal.wsgi.application"
ASGI_APPLICATION = "shenyuan_legal.asgi.application"

# 数据库配置: 生产环境强制连接云端 Supabase (PostgreSQL)，杜绝使用无盘 SQLite 造成数据丢失
SUPABASE_DB_URL = os.environ.get("SUPABASE_DB_URL") or os.environ.get("DATABASE_URL")
if SUPABASE_DB_URL:
    import urllib.parse as up
    url = up.urlparse(SUPABASE_DB_URL)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": url.path.lstrip("/"),
            "USER": up.unquote(url.username) if url.username else "",
            "PASSWORD": up.unquote(url.password) if url.password else "",
            "HOST": url.hostname,
            "PORT": url.port or 5432,
            "CONN_MAX_AGE": 60,  # 允许 Serverless 热实例复用连接（适配 Supabase 连接池）
            "CONN_HEALTH_CHECKS": True,  # 避免因空闲被断开导致的连接异常
            "OPTIONS": {
                "sslmode": "require",
            },
        }
    }
else:
    # 如果处于生产环境 (DEBUG=False 或 Render/Vercel 环境)，严禁使用易失的 SQLite，直接明确抛出异常
    if not DEBUG or os.environ.get("RENDER") or os.environ.get("VERCEL"):
        raise ValueError(
            "【严重安全错误】生产环境未检测到有效的 SUPABASE_DB_URL。"
            "Vercel/Render 属于无状态 Serverless/临时容器，严禁使用本地 SQLite 存储业务数据，否则重启或重新部署会导致所有客户线索全部丢失！"
            "请在 Vercel / 云端控制台 Environment Variables 中配置 SUPABASE_DB_URL (建议使用 Supabase 连接池 6543 端口)。"
        )
    # 本地脱机开发调试备用
    sqlite_dir = BASE_DIR / "data"
    sqlite_dir.mkdir(parents=True, exist_ok=True)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": sqlite_dir / "lawyers.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CORS 配置：默认开放前端域名及本地开发环境，支持环境变量灵活扩展
CORS_ALLOW_ALL_ORIGINS = os.environ.get("CORS_ALLOW_ALL_ORIGINS", "False").lower() in ("true", "1")
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "CORS_ALLOWED_ORIGINS",
        "https://shenyuan-web.vercel.app,https://shenyuan-admin.vercel.app,http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000",
    ).split(",")
    if origin.strip()
]
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https:\/\/.*\.vercel\.app$",
]
CORS_ALLOW_CREDENTIALS = True

# Supabase 配置
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
SUPABASE_STORAGE_BUCKET = os.environ.get("SUPABASE_STORAGE_BUCKET", "intake-files")

# 业务密钥与配置
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "shenyuan-dev-token-2025")
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
RESEND_FROM = os.environ.get("RESEND_FROM", "no-reply@shenyuanlegal.com")
NOTIFY_WEBHOOK_URL = os.environ.get("NOTIFY_WEBHOOK_URL", "")
DEDUPE_WINDOW_HOURS = int(os.environ.get("DEDUPE_WINDOW_HOURS", "24"))
RATE_LIMIT_PER_MINUTE = int(os.environ.get("RATE_LIMIT_PER_MINUTE", "5"))
