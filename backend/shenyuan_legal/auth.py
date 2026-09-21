from ninja.security import HttpBearer
from django.conf import settings

class GlobalAdminAuth(HttpBearer):
    def authenticate(self, request, token):
        if not settings.ADMIN_TOKEN:
            return None
        if token == settings.ADMIN_TOKEN:
            return token
        return None
