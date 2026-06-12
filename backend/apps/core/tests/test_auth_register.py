from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from unittest.mock import patch

from apps.core.models import UserPhoneBinding
from apps.core.sms_service import store_sms_code


@override_settings(CELERY_TASK_ALWAYS_EAGER=True, SMS_PROVIDER_CHAIN=["mock"])
class SmsRegisterTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = "/api/auth/register"
        self.login_url = "/api/auth/login"
        self.mobile = "13900139000"
        self.full_phone = f"+86{self.mobile}"
        self.code = "654321"
        self.password = "abc12345"

    def test_sms_register_creates_user_and_supports_phone_password_login(self):
        store_sms_code(self.full_phone, self.code)
        register_resp = self.client.post(
            self.register_url,
            {
                "phone": self.mobile,
                "country_code": "86",
                "sms_code": self.code,
                "password": self.password,
                "agreed_privacy": True,
            },
            format="json",
        )
        self.assertEqual(register_resp.status_code, 200)
        self.assertTrue(UserPhoneBinding.objects.filter(country_code="86", phone_number=self.mobile).exists())
        self.assertTrue(register_resp.data["data"]["access"])
        self.assertTrue(register_resp.data["data"]["refresh"])

        login_resp = self.client.post(
            self.login_url,
            {"phone": self.mobile, "password": self.password},
            format="json",
        )
        self.assertEqual(login_resp.status_code, 200)
        self.assertTrue(login_resp.data["data"]["access_token"])

    def test_sms_register_requires_privacy_agreement(self):
        store_sms_code(self.full_phone, self.code)
        resp = self.client.post(
            self.register_url,
            {
                "phone": self.mobile,
                "country_code": "86",
                "sms_code": self.code,
                "password": self.password,
                "agreed_privacy": False,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("隐私", resp.data["message"])

    def test_sms_register_rejects_existing_phone(self):
        store_sms_code(self.full_phone, self.code)
        first_resp = self.client.post(
            self.register_url,
            {
                "phone": self.mobile,
                "country_code": "86",
                "sms_code": self.code,
                "password": self.password,
                "agreed_privacy": True,
            },
            format="json",
        )
        self.assertEqual(first_resp.status_code, 200)

        store_sms_code(self.full_phone, self.code)
        second_resp = self.client.post(
            self.register_url,
            {
                "phone": self.mobile,
                "country_code": "86",
                "sms_code": self.code,
                "password": self.password,
                "agreed_privacy": True,
            },
            format="json",
        )
        self.assertEqual(second_resp.status_code, 400)
        self.assertIn("已注册", second_resp.data["message"])

    def test_sms_register_should_fail_closed_when_sms_backend_unavailable(self):
        with patch("apps.core.views.verify_sms_code_with_lua", side_effect=RuntimeError("redis unavailable")):
            resp = self.client.post(
                self.register_url,
                {
                    "phone": self.mobile,
                    "country_code": "86",
                    "sms_code": self.code,
                    "password": self.password,
                    "agreed_privacy": True,
                },
                format="json",
            )

        self.assertEqual(resp.status_code, 503)
        self.assertEqual(resp.data["code"], 503)
        self.assertIn("暂不可用", resp.data["message"])
