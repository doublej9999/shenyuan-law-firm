import os
import sys
from pathlib import Path
from django.core.wsgi import get_wsgi_application

# 确保 backend 根目录在 Python 模块搜索路径中（适配 Vercel Serverless 环境）
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shenyuan_legal.settings")
application = get_wsgi_application()
app = application

