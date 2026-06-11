"""快速创建/重置超级管理员 admin / 123456"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

from django.contrib.auth.models import User

user = User.objects.filter(username="admin").first()
if user:
    user.is_active = True
    user.is_staff = True
    user.is_superuser = True
    user.set_password("123456")
    user.save()
    print("账号 admin 已存在，已重置密码为 123456 并激活")
else:
    User.objects.create_superuser(username="admin", password="123456", email="admin@tuoyue-tech.com")
    print("超级管理员 admin / 123456 创建成功")
