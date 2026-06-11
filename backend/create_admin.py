import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
import django
django.setup()
from django.contrib.auth.models import User
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser(username="admin", password="123456")
    print("admin 用户已创建（密码: 123456）")
else:
    print("admin 用户已存在")
