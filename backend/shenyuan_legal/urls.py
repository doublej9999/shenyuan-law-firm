from django.contrib import admin
from django.urls import path
from shenyuan_legal.api import api

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("", api.urls),
]
