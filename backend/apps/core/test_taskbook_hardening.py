from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.core.models import Product, ProductVariant


class LoginRateLimitTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username="lock-me", password="Pass123456")

    def tearDown(self):
        cache.clear()

    @override_settings(AUTH_LOGIN_FAIL_MAX_ATTEMPTS=5, AUTH_LOGIN_FAIL_LOCK_SECONDS=900)
    def test_sixth_attempt_is_rejected_after_five_failures(self):
        for _ in range(5):
            response = self.client.post(
                "/api/auth/login",
                {"username": "lock-me", "password": "wrong-password"},
                format="json",
                REMOTE_ADDR="203.0.113.9",
            )
            self.assertEqual(response.status_code, 401)

        locked = self.client.post(
            "/api/auth/login",
            {"username": "lock-me", "password": "Pass123456"},
            format="json",
            REMOTE_ADDR="203.0.113.9",
        )
        self.assertEqual(locked.status_code, 429)
        self.assertIn("Retry-After", locked)
        self.assertGreater(int(locked["Retry-After"]), 0)


@override_settings(DEMO_MODE=True)
class PlatformFlowTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username="integrator", password="Pass123456")
        self.client.force_authenticate(user=self.user)
        self.product = Product.objects.create(
            platform="amazon",
            platform_product_id="LOCAL-1001",
            title="Demo Product",
            images=["https://example.com/main.jpg"],
            attributes={"description": "Demo desc", "brand": "Demo"},
            price="29.90",
            stock=18,
        )
        ProductVariant.objects.create(
            product=self.product,
            sku="LOCAL-1001-BLK-M",
            title="Black / M",
            price="29.90",
            stock=8,
            attributes={"color": "black", "size": "M"},
        )

    def tearDown(self):
        cache.clear()

    def test_shein_listing_returns_mock_success_in_demo_mode(self):
        response = self.client.post(
            "/api/v1/goods/listing/",
            {"goods_id": self.product.id, "platform": "shein", "shop_id": "shop-demo"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]["platform"], "shein")
        self.assertTrue(response.data["data"]["result"]["mocked"])
        self.assertEqual(response.data["data"]["result"]["shop_id"], "shop-demo")

    def test_collect_1688_single_persists_product_detail(self):
        response = self.client.post(
            "/api/v1/collect/1688/single/",
            {"url": "https://detail.1688.com/offer/123456789012.html", "source": "1688"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        collected = Product.objects.get(platform="1688", platform_product_id="123456789012")
        self.assertEqual(response.data["data"]["item_id"], "123456789012")
        self.assertEqual(response.data["data"]["product"]["id"], collected.id)
        self.assertGreater(collected.variants.count(), 0)
