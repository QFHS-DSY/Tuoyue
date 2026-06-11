import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
import django
django.setup()
from django.contrib.auth.models import User
users = User.objects.all().values("id", "username", "is_active")
print("auth_user:")
for u in users:
    print(f'  ID={u["id"]} {u["username"]} active={u["is_active"]}')
