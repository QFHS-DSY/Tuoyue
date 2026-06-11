"""
一体化种子数据生成命令
涵盖：设置系统 / 财务系统 / 采购 & 仓库 / 产品 & 销售 / 管理与服务
用法: python manage.py seed_all
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, date, datetime
import random
import json


class Command(BaseCommand):
    help = '为所有 ERP 系统生成非硬编码测试数据'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='清除已有测试数据')

    def handle(self, *args, **options):
        if options['clear']:
            self._clear_all()
        self._ensure_admin()
        self._seed_settings_sys()
        self._seed_finance()
        self._seed_purchase_wms()
        self._seed_product_sales()
        self._seed_team_mgt()
        self.stdout.write(self.style.SUCCESS('\n✅ 所有系统测试数据生成完毕！'))

    def _ensure_admin(self):
        self.admin, _ = User.objects.get_or_create(username='admin', defaults={'is_superuser': True, 'is_staff': True})
        self.admin.set_password('123456'); self.admin.save()
        # 额外测试用户
        names = [('zhangsan', '张运营'), ('lisi', '李财务'), ('wangwu', '王采购'), ('zhaoliu', '赵仓管'), ('sunqi', '孙销售')]
        self.users = {}
        for uname, full_name in names:
            u, _ = User.objects.get_or_create(username=uname, defaults={'is_staff': True})
            u.first_name = full_name; u.set_password('123456'); u.save()
            self.users[uname] = u

    # ───────────────── 设置系统 ─────────────────
    def _seed_settings_sys(self):
        self.stdout.write('📦 设置系统...')
        from apps.settings_sys.models import (
            Department, Role, Permission, UserProfile, Tag, SystemConfig,
            WarehouseConfig, ThirdPartyWarehouse, PlatformConfig, AssistantTask,
            SSOConfig, NotificationSetting, ApiToken
        )

        # 部门
        dept_tree = {
            '总公司': [('技术部', [('后端组', []), ('前端组', []), ('测试组', [])]),
                       ('运营部', [('Amazon运营', []), ('1688运营', [])]),
                       ('财务部', [('会计组', []), ('出纳组', [])]),
                       ('采购部', [('国内采购', []), ('海外采购', [])]),
                       ('仓储部', [('国内仓', []), ('海外仓', [])]),
                       ('销售部', [('北美组', []), ('欧洲组', []), ('东南亚组', [])])],
        }
        self.depts = {}
        def _create_dept(name, parent, level):
            d, _ = Department.objects.get_or_create(
                code=f'DEPT_{name}',
                defaults={'name': name, 'parent': parent, 'level': level, 'sort_order': level * 10}
            )
            self.depts[name] = d
            return d
        for root_name, children in dept_tree.items():
            root = _create_dept(root_name, None, 1)
            for cname, subs in children:
                c = _create_dept(cname, root, 2)
                for sname, _ in subs:
                    _create_dept(sname, c, 3)

        # 角色
        role_defs = [
            ('超级管理员', 'SUPER_ADMIN', '系统超级管理员，拥有全部权限', True),
            ('部门经理', 'DEPT_MANAGER', '部门管理权限', False),
            ('运营专员', 'OPS_SPECIALIST', '运营权限', False),
            ('财务专员', 'FINANCE_SPECIALIST', '财务权限', False),
            ('采购专员', 'PURCHASE_SPECIALIST', '采购权限', False),
            ('仓管专员', 'WMS_SPECIALIST', '仓库管理权限', False),
        ]
        self.roles = {}
        for rname, rcode, rdesc, sys in role_defs:
            r, _ = Role.objects.get_or_create(code=rcode,
                defaults={'name': rname, 'description': rdesc, 'is_system': sys})
            self.roles[rcode] = r

        # 权限
        perm_defs = [
            (None, '系统管理', 'system_admin', 'MENU', '/settings'),
            (None, '部门管理', 'dept_manage', 'MENU', '/settings/departments'),
            (None, '角色管理', 'role_manage', 'MENU', '/settings/roles'),
            (None, '权限管理', 'perm_manage', 'MENU', '/settings/permissions'),
            (None, '平台授权', 'platform_auth', 'MENU', '/settings/platform-auth'),
            (None, '仓库配置', 'warehouse_config', 'MENU', '/settings/warehouse'),
            (None, '财务系统', 'finance_access', 'MENU', '/finance'),
            (None, '请款管理', 'payment_manage', 'MENU', '/finance/payment-pool'),
            (None, '收款管理', 'receipt_manage', 'MENU', '/finance/receipt-order'),
            (None, '费用管理', 'expense_manage', 'MENU', '/finance/expense'),
            (None, '采购系统', 'purchase_access', 'MENU', '/purchase'),
            (None, '供应商管理', 'supplier_manage', 'MENU', '/purchase/supplier'),
            (None, '采购单管理', 'purchase_order_manage', 'MENU', '/purchase/order'),
            (None, '仓库系统', 'wms_access', 'MENU', '/wms'),
            (None, '库存管理', 'inventory_manage', 'MENU', '/wms/inventory'),
            (None, '产品系统', 'product_access', 'MENU', '/product'),
            (None, '销售系统', 'sales_access', 'MENU', '/sales'),
            (None, 'API访问', 'api_access', 'API', '/api/'),
        ]
        self.perms = {}
        for parent_name, name, code, ptype, path in perm_defs:
            parent = self.perms.get(parent_name) if parent_name else None
            p, _ = Permission.objects.get_or_create(code=code,
                defaults={'name': name, 'perm_type': ptype, 'resource_path': path, 'parent': parent})
            self.perms[name] = p

        # 角色-权限：超级管理员分配全部权限
        from apps.settings_sys.models import RolePermission
        admin_role = self.roles['SUPER_ADMIN']
        for p in self.perms.values():
            RolePermission.objects.get_or_create(role=admin_role, permission=p)

        # 标签
        tag_defs = [
            ('爆款', 'HOT', 'SKU', '#FF4D4F'),
            ('新品', 'NEW', 'SKU', '#52C41A'),
            ('清仓', 'CLEARANCE', 'SKU', '#FAAD14'),
            ('FBA', 'FBA', 'WAREHOUSE', '#1890FF'),
            ('FBM', 'FBM', 'WAREHOUSE', '#722ED1'),
            ('VIP客户', 'VIP', 'SUPPLIER', '#EB2F96'),
            ('高风险', 'HIGH_RISK', 'ORDER', '#FF4D4F'),
            ('优先处理', 'PRIORITY', 'ORDER', '#1890FF'),
        ]
        for tname, tcode, ttype, tcolor in tag_defs:
            Tag.objects.get_or_create(code=tcode, defaults={'name': tname, 'tag_type': ttype, 'color': tcolor})

        # 系统配置
        configs = [
            ('SYS_NAME', {'zh': '拓岳ERP', 'en': 'Tuoyue ERP'}, 'GENERAL', '系统名称'),
            ('DEFAULT_CURRENCY', 'CNY', 'GENERAL', '默认货币'),
            ('PAGE_SIZE', 20, 'GENERAL', '默认分页大小'),
            ('JWT_EXPIRE_HOURS', 24, 'SECURITY', 'JWT过期时间'),
            ('MAX_LOGIN_ATTEMPTS', 5, 'SECURITY', '最大登录尝试次数'),
        ]
        for key, val, group, desc in configs:
            SystemConfig.objects.get_or_create(config_key=key,
                defaults={'config_value': val if isinstance(val, dict) else str(val),
                          'config_group': group, 'description': desc})

        # WMS仓库
        wms_defs = [
            ('深圳国内仓', 'SZ_CN', 'SELF', '广东省深圳市宝安区', 'CHINA'),
            ('义乌国内仓', 'YW_CN', 'SELF', '浙江省义乌市', 'CHINA'),
            ('洛杉矶海外仓', 'LA_US', 'FBA', 'Los Angeles, CA, USA', 'USA'),
            ('德国海外仓', 'DE_EU', 'FBA', 'Berlin, Germany', 'DE'),
        ]
        for wname, wcode, wtype, addr, country in wms_defs:
            WarehouseConfig.objects.get_or_create(warehouse_code=wcode,
                defaults={'warehouse_name': wname, 'warehouse_type': wtype, 'address': addr, 'country': country})

        # 第三方海外仓
        third_defs = [
            ('谷仓美西仓', 'GUCANG', '谷仓', 'GUCANG_USW', 'USA', 'https://api.gucang.com'),
            ('谷仓欧洲仓', 'GUCANG', '谷仓', 'GUCANG_EU', 'DE', 'https://api.gucang.com'),
            ('万邑通美东仓', 'WANYITONG', '万邑通', 'WYT_US', 'USA', 'https://api.winit.com'),
            ('4PX日本仓', '4PX', '4PX', '4PX_JP', 'JP', 'https://api.4px.com'),
        ]
        for name, provider_code, provider_name, wcode, country, endpoint in third_defs:
            ThirdPartyWarehouse.objects.get_or_create(warehouse_code=wcode,
                defaults={'name': name, 'provider_code': provider_code, 'provider_name': provider_name,
                          'country': country, 'api_endpoint': endpoint})

        # 平台配置
        platforms = [
            ('Amazon', 'AMAZON', 'OAUTH2', 'https://sellercentral.amazon.com', 'https://api.amazon.com/auth/o2/token'),
            ('1688', 'ALIBABA', 'OAUTH2', 'https://login.1688.com', 'https://api.1688.com'),
            ('eBay', 'EBAY', 'OAUTH2', 'https://auth.ebay.com', 'https://api.ebay.com/identity/v1/oauth2/token'),
            ('Shopee', 'SHOPEE', 'TOKEN', 'https://partner.shopeemobile.com', ''),
            ('Walmart', 'WALMART', 'TOKEN', 'https://marketplace.walmart.com', ''),
            ('Temu', 'TEMU', 'API_KEY', 'https://seller.kuajingmaihuo.com', ''),
        ]
        self.platforms = {}
        for pname, pcode, atype, auth_url, token_url in platforms:
            p, _ = PlatformConfig.objects.get_or_create(platform_code=pcode,
                defaults={'platform_name': pname, 'auth_type': atype, 'auth_url': auth_url, 'token_url': token_url})
            self.platforms[pcode] = p

        # 平台授权
        from apps.settings_sys.models import PlatformAuth
        auth_defs = [
            ('AMAZON', 'Amazon主账号', 'AMZ-001', 'ACTIVE', timezone.now() + timedelta(days=30)),
            ('AMAZON', 'Amazon欧洲', 'AMZ-EU-001', 'ACTIVE', timezone.now() + timedelta(days=60)),
            ('ALIBABA', '1688主账号', '1688-001', 'ACTIVE', timezone.now() + timedelta(days=90)),
            ('SHOPEE', 'Shopee东南亚', 'SP-001', 'ACTIVE', timezone.now() + timedelta(days=45)),
        ]
        for pcode, acc_name, acc_id, status, expires in auth_defs:
            PlatformAuth.objects.get_or_create(account_id=acc_id,
                defaults={'platform': self.platforms[pcode], 'account_name': acc_name,
                          'auth_status': status, 'token_expires_at': expires,
                          'access_token': f'TOKEN_{pcode}_{acc_id}_XXXXX'})

        # 助手任务
        tasks = [
            ('库存自动同步', 'SYNC', '0 */6 * * *', 1),
            ('Amazon订单采集', 'COLLECT', '0 * * * *', 2),
            ('Walmart价格监控', 'MONITOR', '0 */2 * * *', 1),
            ('日报生成', 'REPORT', '0 8 * * *', 3),
            ('数据库备份', 'BACKUP', '0 2 * * *', 5),
            ('SKU标签自动更新', 'SYNC', '0 */4 * * *', 2),
        ]
        for tname, ttype, cron, pri in tasks:
            AssistantTask.objects.get_or_create(task_name=tname,
                defaults={'task_type': ttype, 'cron_expression': cron, 'priority': pri,
                          'task_no': f'TASK_{ttype}_{random.randint(1000,9999)}',
                          'status': 'IDLE'})

        # SSO
        SSOConfig.objects.get_or_create(sso_name='拓岳JWT认证',
            defaults={'sso_provider': 'JWT', 'issuer': 'tuoyue-erp', 'signing_algorithm': 'HS256',
                      'token_lifetime_hours': 24, 'status': True})

        self.stdout.write('   ✅ 设置系统: 部门/角色/权限/标签/仓库/平台/助手 测试数据已生成')

    # ───────────────── 财务系统 ─────────────────
    def _seed_finance(self):
        self.stdout.write('📦 财务系统...')
        from apps.finance.models import (
            PaymentRequestPool, PaymentRequest, PaymentRequestItem, PaymentRecord,
            ReceiptOrder, ReceiptOrderItem, TransactionFlow,
            OrderProfit, SettlementProfit, ExpenseRecord, ExpenseType,
            CostValuation, BillDetail, CollectionDetail
        )

        now = timezone.now()
        today = now.date()

        # 费用类型
        etypes = {k: ExpenseType.objects.get_or_create(type_name=v, type_code=k,
            defaults={'description': f'{v}费用'})[0]
            for k, v in [('AD_FEE', '广告费'), ('SHIPPING', '运费'), ('STORAGE', '仓储费'),
                         ('PLATFORM', '平台费'), ('OFFICE', '办公费'), ('REFUND', '退款')]}

        # 请款池
        for i in range(6):
            PaymentRequestPool.objects.get_or_create(source_no=f'POOL-{1000+i}',
                defaults={'pool_type': random.choice(['PURCHASE', 'LOGISTICS', 'AD']),
                          'source_type': 'PURCHASE_ORDER', 'supplier_name': f'供应商{i+1}号',
                          'payable_amount': random.uniform(500, 50000),
                          'paid_amount': random.uniform(0, 30000),
                          'currency': 'CNY', 'status': random.choice(['UNAPPLIED', 'PARTIAL', 'APPLIED']),
                          'goods_value': random.uniform(300, 40000)})

        # 请款单
        for i in range(4):
            req, _ = PaymentRequest.objects.get_or_create(request_no=f'REQ-{1000+i}',
                defaults={'supplier_id': 1000 + i, 'supplier_name': f'供应商{i+1}号',
                          'total_amount': random.uniform(2000, 80000),
                          'paid_amount': 0, 'currency': 'CNY',
                          'status': random.choice(['PENDING_APPROVAL', 'APPROVED', 'PAID']),
                          'created_by': self.admin})
            # 请款单明细
            for j in range(random.randint(1, 4)):
                PaymentRequestItem.objects.get_or_create(request=req, source_no=f'ITEM-{1000+i}-{j}',
                    defaults={'source_type': 'PURCHASE', 'item_name': f'采购物品{i+1}-{j+1}',
                              'quantity': random.randint(10, 500), 'unit_price': random.uniform(5, 200),
                              'amount': random.uniform(200, 20000)})
            # 付款记录
            pay_half = float(req.total_amount) * 0.5
            PaymentRecord.objects.get_or_create(request=req, pay_amount=pay_half, pay_currency='CNY',
                defaults={'pay_method': 'BANK_TRANSFER',
                          'pay_date': today - timedelta(days=random.randint(1, 30))})

        # 收款单
        for i in range(4):
            r, _ = ReceiptOrder.objects.get_or_create(receipt_no=f'REC-{1000+i}',
                defaults={'customer_name': f'客户{i+1}号',
                          'total_amount': random.uniform(3000, 60000),
                          'currency': 'CNY', 'status': random.choice(['PENDING', 'COMPLETED']),
                          'created_by': self.admin})
            ReceiptOrderItem.objects.get_or_create(receipt=r, source_no=f'SO-{1000+i}',
                defaults={'item_name': f'订单{1000+i}收款', 'amount': r.total_amount})

        # 往来流水
        for i in range(8):
            TransactionFlow.objects.get_or_create(flow_no=f'FLOW-{10000+i}',
                defaults={'transaction_type': random.choice(['收款', '付款']),
                          'source_type': random.choice(['PURCHASE', 'SALES', 'LOGISTICS']),
                          'source_no': f'SRC-{2000+i}', 'counterparty_name': f'往来方{i+1}',
                          'amount': random.uniform(-50000, 50000), 'currency': 'CNY',
                          'transaction_date': today - timedelta(days=random.randint(0, 90))})

        # 订单利润
        for i in range(6):
            OrderProfit.objects.get_or_create(order_id=f'ORDER-{5000+i}',
                defaults={'msku': f'MSKU-{random.randint(100,999)}',
                          'sku': f'SKU-{random.randint(1000,9999)}',
                          'sales_amount': random.uniform(100, 5000),
                          'purchase_cost': random.uniform(50, 2500),
                          'shipping_cost': random.uniform(10, 500),
                          'platform_fee': random.uniform(5, 200),
                          'fba_fee': random.uniform(20, 300),
                          'advertising_fee': random.uniform(10, 400),
                          'profit': random.uniform(-200, 2000),
                          'profit_rate': random.uniform(-10, 40),
                          'settlement_month': f'2026-0{random.randint(1,5)}'})

        # 结算利润
        for m in range(1, 5):
            SettlementProfit.objects.get_or_create(settlement_month=f'2026-0{m}',
                defaults={'total_sales': random.uniform(50000, 200000),
                          'total_cost': random.uniform(30000, 150000),
                          'total_profit': random.uniform(5000, 80000),
                          'profit_rate': random.uniform(10, 40),
                          'order_count': random.randint(50, 500)})

        # 费用记录
        for i in range(5):
            ExpenseRecord.objects.get_or_create(expense_no=f'EXP-{3000+i}',
                defaults={'expense_type': random.choice(list(etypes.keys())),
                          'amount': random.uniform(500, 30000), 'currency': 'CNY',
                          'remark': f'测试费用记录{i+1}', 'created_by': self.admin})

        # 成本计价
        for i in range(5):
            CostValuation.objects.get_or_create(sku=f'SKU-A{100+i}',
                defaults={'msku': f'M-A{100+i}', 'source_doc_no': f'DOC-{4000+i}',
                          'cost_source': random.choice(['PURCHASE', 'LOGISTICS', 'PROCESS']),
                          'purchase_cost': random.uniform(30, 500),
                          'shipping_cost': random.uniform(5, 100),
                          'valuation_month': f'2026-0{random.randint(1,5)}'})

        self.stdout.write('   ✅ 财务系统: 请款/收款/流水/利润/费用/成本 测试数据已生成')

    # ───────────────── 采购 & 仓库 ─────────────────
    def _seed_purchase_wms(self):
        self.stdout.write('📦 采购 & 仓库...')
        from apps.purchase.models import Supplier, PurchaseOrder, PurchaseOrderItem
        from apps.wms.models import WarehouseWms, Inventory, ReceiptOrder, ReceiptOrderItem, DeliveryOrder, DeliveryOrderItem, StockFlow, Product as WmsProduct

        # 供应商
        suppliers_data = [
            ('深圳数码科技有限公司', 'SZ-DIGITAL', '数码产品', 5.0),
            ('义乌商贸有限公司', 'YW-TRADE', '日用百货', 4.5),
            ('广州服装进出口公司', 'GZ-GARMENT', '服装鞋帽', 4.2),
            ('东莞电子器材厂', 'DG-ELEC', '电子配件', 4.8),
            ('杭州制造科技有限公司', 'HZ-MFG', '五金工具', 4.0),
        ]
        self.suppliers = {}
        for sname, scode, warehouse, rating in suppliers_data:
            s, _ = Supplier.objects.get_or_create(code=scode,
                defaults={'name': sname, 'warehouse_name': warehouse,
                          'contact_name': f'{sname[:2]}联系人', 'phone': f'138{random.randint(10000000,99999999)}',
                          'status': 1, 'rating': rating})
            self.suppliers[scode] = s

        # WMS仓库 (必须先于采购单创建)
        wms_defs = [
            ('深圳仓库', 'SZ-WH'), ('义乌仓库', 'YW-WH'), ('洛杉矶仓库', 'LA-WH'), ('德国仓库', 'DE-WH'),
        ]
        self.wms_warehouses = {}
        for name, code in wms_defs:
            w, _ = WarehouseWms.objects.get_or_create(code=code, defaults={'name': name})
            self.wms_warehouses[code] = w

        # 采购单 — 需要 warehouse_id
        wh_ids = [w.id for w in self.wms_warehouses.values()]
        for i in range(5):
            supplier = random.choice(list(self.suppliers.values()))
            wh_id = random.choice(wh_ids) if wh_ids else 1
            po, _ = PurchaseOrder.objects.get_or_create(order_no=f'PO-{8000+i}',
                defaults={'supplier': supplier, 'warehouse_id': wh_id,
                          'order_type': 'NORMAL',
                          'total_amount': random.uniform(5000, 100000),
                          'order_date': date.today() - timedelta(days=random.randint(1, 60)),
                          'status': random.choice(['PENDING', 'APPROVED', 'RECEIVED', 'COMPLETED']),
                          'remark': f'测试采购单{i+1}', 'creator': 'admin'})
            for j in range(random.randint(1, 4)):
                PurchaseOrderItem.objects.get_or_create(order=po, sku_id=1000+i*10+j,
                    defaults={'product_name': f'采购商品{po.order_no}-{j+1}',
                              'msku': f'MSKU-{random.randint(1000,9999)}',
                              'quantity': random.randint(10, 500),
                              'unit_price': random.uniform(10, 300),
                              'total_amount': random.uniform(500, 50000),
                              'received_quantity': random.randint(0, 200)})

        # WMS产品
        skus = [('iPhone15Case', 'iPhone15保护壳', 'X001ABCDEF', 'B0XXXXXX01'),
                ('USBC-Cable', 'USB-C充电线', 'X002ABCDEF', 'B0XXXXXX02'),
                ('LED-DeskLamp', 'LED台灯', 'X003ABCDEF', 'B0XXXXXX03'),
                ('Bluetooth-Speaker', '蓝牙音箱', 'X004ABCDEF', 'B0XXXXXX04'),
                ('Yoga-Mat', '瑜伽垫', 'X005ABCDEF', 'B0XXXXXX05'),
                ('Stainless-Bottle', '不锈钢水瓶', 'X006ABCDEF', 'B0XXXXXX06'),
                ('Wireless-Mouse', '无线鼠标', 'X007ABCDEF', 'B0XXXXXX07'),
                ('Phone-Stand', '手机支架', 'X008ABCDEF', 'B0XXXXXX08')]
        self.wms_products = {}
        for sku, name, fnsku, asin in skus:
            p, _ = WmsProduct.objects.get_or_create(sku=sku,
                defaults={'sku_name': name, 'fnsku': fnsku, 'asin': asin,
                          'category': random.choice(['电子', '家居', '运动', '办公']),
                          'brand': random.choice(['BrandA', 'BrandB', 'BrandC']),
                          'weight': random.uniform(0.1, 5.0)})
            self.wms_products[sku] = p

        # 库存
        for wh_code, wh in self.wms_warehouses.items():
            for sku, prod in random.sample(list(self.wms_products.items()), 5):
                inv, _ = Inventory.objects.get_or_create(warehouse=wh, sku=sku,
                    defaults={'sku_name': prod.sku_name,
                              'quantity': random.randint(50, 5000),
                              'locked_qty': random.randint(0, 200)})

        # 收货单
        for i in range(3):
            wh = random.choice(list(self.wms_warehouses.values()))
            ro, _ = ReceiptOrder.objects.get_or_create(order_no=f'RO-{6000+i}',
                defaults={'warehouse': wh, 'source_type': 'PURCHASE', 'source_id': 8000+i,
                          'status': random.choice([0, 1, 2]), 'creator': 'admin'})
            for j in range(random.randint(1, 3)):
                sku = random.choice(list(self.wms_products.keys()))
                ritem, _ = ReceiptOrderItem.objects.get_or_create(order=ro, sku=sku,
                    defaults={'sku_name': self.wms_products[sku].sku_name,
                              'expected_qty': random.randint(50, 500),
                              'actual_qty': random.randint(30, 500),
                              'unit_cost': random.uniform(10, 200)})

        # 出库单
        for i in range(3):
            wh = random.choice(list(self.wms_warehouses.values()))
            do, _ = DeliveryOrder.objects.get_or_create(order_no=f'DO-{7000+i}',
                defaults={'warehouse': wh, 'source_type': 'SALES', 'source_id': 5000+i,
                          'status': random.choice([0, 1, 2, 3]), 'creator': 'admin'})
            for j in range(random.randint(1, 3)):
                sku = random.choice(list(self.wms_products.keys()))
                DeliveryOrderItem.objects.get_or_create(order=do, sku=sku,
                    defaults={'sku_name': self.wms_products[sku].sku_name,
                              'order_qty': random.randint(10, 200),
                              'picked_qty': random.randint(0, 200),
                              'shipped_qty': random.randint(0, 200)})

        # 库存流水
        invs = list(Inventory.objects.all()[:10])
        for inv in invs:
            for _ in range(3):
                change = random.randint(-100, 100)
                StockFlow.objects.create(
                    inventory=inv, flow_type='IN' if change > 0 else 'OUT',
                    change_qty=abs(change), before_qty=max(0, inv.quantity - change),
                    after_qty=inv.quantity, order_no=f'FLOW-{random.randint(1000,9999)}',
                    remark=f'自动流水记录')

        self.stdout.write('   ✅ 采购&仓库: 供应商/采购单/WMS仓库/库存/收货/出库 测试数据已生成')

    # ───────────────── 产品 & 销售 ─────────────────
    def _seed_product_sales(self):
        self.stdout.write('📦 产品 & 销售...')
        from apps.product_sys.models import Brand, Category, Product, ProductSku, SpuInfo, DevelopmentTask
        from apps.sales.models import AmazonListing, ListingSkuMapping

        # 品牌
        brand_names = ['Apple', 'Samsung', 'Huawei', 'Xiaomi', 'Anker', 'UGREEN', 'Baseus', 'Aukey', 'Ravpower', 'Generic']
        self.brands = {}
        for bname in brand_names:
            b, _ = Brand.objects.get_or_create(code=bname.upper(), defaults={'name': bname, 'status': 'ACTIVE'})
            self.brands[bname] = b

        # 分类
        cat_tree = {
            '电子数码': ['手机配件', '电脑配件', '音频设备', '智能穿戴'],
            '家居生活': ['厨房用品', '收纳整理', '家装饰品', '灯具照明'],
            '运动户外': ['健身器材', '户外装备', '骑行工具', '游泳用品'],
            '服装鞋帽': ['男装', '女装', '童装', '鞋类'],
        }
        self.categories = {}
        for parent_name, children in cat_tree.items():
            pc, _ = Category.objects.get_or_create(code=f'CAT_{parent_name}', defaults={
                'name': parent_name, 'level': 1, 'status': 'ACTIVE'})
            self.categories[parent_name] = pc
            for cname in children:
                cc, _ = Category.objects.get_or_create(code=f'CAT_{cname}', defaults={
                    'name': cname, 'parent': pc, 'level': 2, 'status': 'ACTIVE'})
                self.categories[cname] = cc

        # 产品
        products_data = [
            ('P-10001', 'iPhone 15 Pro Max 手机壳', '电子数码', '手机配件', 'Apple', 15.00),
            ('P-10002', 'USB-C 快充数据线 2米', '电子数码', '手机配件', 'UGREEN', 8.50),
            ('P-10003', '蓝牙5.3无线耳机', '电子数码', '音频设备', 'Baseus', 45.00),
            ('P-10004', '铝合金笔记本支架', '电子数码', '电脑配件', 'Generic', 28.00),
            ('P-10005', '不锈钢保温杯 500ml', '家居生活', '厨房用品', 'Generic', 22.00),
            ('P-10006', 'LED护眼台灯', '家居生活', '灯具照明', 'Generic', 35.00),
            ('P-10007', '防滑瑜伽垫 6mm', '运动户外', '健身器材', 'Generic', 18.50),
            ('P-10008', '折叠露营椅', '运动户外', '户外装备', 'Generic', 42.00),
            ('P-10009', '无线充电器 15W快充', '电子数码', '手机配件', 'Anker', 25.00),
            ('P-10010', '桌面收纳盒', '家居生活', '收纳整理', 'Generic', 12.00),
        ]
        self.products = {}
        for pno, name, pcat, subcat, brand, price in products_data:
            cat_obj = self.categories.get(subcat)
            brand_obj = self.brands.get(brand)
            p, _ = Product.objects.get_or_create(product_no=pno,
                defaults={'name': name,
                          'category_id': cat_obj.id if cat_obj else None,
                          'brand_id': brand_obj.id if brand_obj else None,
                          'cost_price': price * 0.4, 'status': 'ACTIVE',
                          'created_by': self.admin})
            self.products[pno] = p
            # SKU
            s, _ = ProductSku.objects.get_or_create(product=p, sku=f'{pno}-BLK',
                defaults={'variant_info': json.dumps({'color': '黑色'}),
                          'barcode': f'690{random.randint(1000000000, 9999999999)}',
                          'cost_price': price * 0.4, 'stock_qty': random.randint(10, 500)})

        # SPU
        for i in range(3):
            spu, _ = SpuInfo.objects.get_or_create(spu_code=f'SPU-{200+i}',
                defaults={'spu_name': f'爆款产品套装{i+1}',
                          'status': 'ACTIVE', 'cost_price': random.uniform(50, 200),
                          'sku_count': random.randint(2, 5), 'created_by': self.admin})

        # 新品开发任务
        for i in range(4):
            DevelopmentTask.objects.get_or_create(task_no=f'DEV-{500+i}',
                defaults={'demand_name': f'新品需求-{i+1}: 智能家居产品{i+1}',
                          'country': random.choice(['US', 'DE', 'JP', 'UK']),
                          'level': random.choice(['P1', 'P2', 'P3']),
                          'status': random.choice(['PROCESSING', 'COMPLETED', 'PROCESSING']),
                          'estimated_cost': random.uniform(30, 200),
                          'actual_cost': random.uniform(25, 220),
                          'created_by': self.admin})

        # Amazon Listing
        listing_data = [
            ('MSKU-001', 'B0XXXXAA01', 'US', 29.99, 19.99, 120, 567),
            ('MSKU-002', 'B0XXXXAA02', 'US', 19.99, 14.99, 85, 1230),
            ('MSKU-003', 'B0XXXXAA03', 'US', 59.99, 49.99, 200, 340),
            ('MSKU-004', 'B0XXXXAA04', 'US', 39.99, 29.99, 150, 890),
            ('MSKU-005', 'B0XXXXAA05', 'US', 25.99, 19.99, 95, 1500),
            ('MSKU-006', 'B0XXXXBB01', 'DE', 32.99, 24.99, 60, 230),
            ('MSKU-007', 'B0XXXXBB02', 'DE', 45.99, 35.99, 45, 180),
            ('MSKU-008', 'B0XXXXCC01', 'JP', 3500, 2800, 80, 420),
        ]
        for msku, asin, country, price, sale_price, fba, rev in listing_data:
            AmazonListing.objects.get_or_create(msku=msku,
                defaults={'asin': asin, 'shop_id': random.randint(1, 5),
                          'shop_name': random.choice(['US-Store', 'EU-Store', 'JP-Store']),
                          'country': country, 'title': f'Product {msku} Title',
                          'price': price, 'sale_price': sale_price,
                          'total_price': price * 1.1, 'status': 'ACTIVE',
                          'fba_available': fba, 'review_count': rev,
                          'rating': random.uniform(3.5, 5.0),
                          'sales_volume': random.randint(10, 2000)})

        # SKU-Listing映射
        for i, msku in enumerate(['MSKU-001', 'MSKU-002', 'MSKU-003', 'MSKU-004', 'MSKU-005']):
            ListingSkuMapping.objects.get_or_create(msku=msku,
                defaults={'sku': f'P-{10001+i}-BLK', 'asin': f'B0XXXXAA0{i+1}',
                          'shop_id': random.randint(1, 5), 'created_by': self.admin})

        self.stdout.write('   ✅ 产品&销售: 品牌/分类/产品/SPU/开发任务/Amazon Listing 测试数据已生成')

    # ───────────────── 管理与服务 ─────────────────
    def _seed_team_mgt(self):
        self.stdout.write('📦 管理与服务...')
        from apps.settings_sys.models import UserProfile, UserRole, UserDepartment

        # 用户资料
        for uname, u in self.users.items():
            UserProfile.objects.get_or_create(user=u,
                defaults={'phone': f'138{random.randint(10000000,99999999)}',
                          'employee_no': f'TY{random.randint(100, 999)}',
                          'position': random.choice(['运营专员', '财务专员', '采购专员', '仓库管理员', '销售经理']),
                          'entry_date': date.today() - timedelta(days=random.randint(30, 1000))})

        # 用户角色分配
        role_map = {
            'zhangsan': 'OPS_SPECIALIST', 'lisi': 'FINANCE_SPECIALIST',
            'wangwu': 'PURCHASE_SPECIALIST', 'zhaoliu': 'WMS_SPECIALIST',
            'sunqi': 'OPS_SPECIALIST',
        }
        for uname, rcode in role_map.items():
            UserRole.objects.get_or_create(user=self.users[uname], role=self.roles.get(rcode),
                defaults={'assigned_by': self.admin})

        # 管理员全部角色
        for rcode in self.roles:
            UserRole.objects.get_or_create(user=self.admin, role=self.roles[rcode],
                defaults={'assigned_by': self.admin})

        # 用户部门分配
        dept_map = {
            'zhangsan': 'Amazon运营', 'lisi': '会计组', 'wangwu': '国内采购',
            'zhaoliu': '国内仓', 'sunqi': '北美组',
        }
        for uname, dname in dept_map.items():
            dept = self.depts.get(dname)
            if dept:
                UserDepartment.objects.get_or_create(user=self.users[uname], department=dept)

        self.stdout.write('   ✅ 管理与服务: 用户资料/角色分配/部门分配 测试数据已生成')

    # ───────────────── 清空数据 ─────────────────
    def _clear_all(self):
        self.stdout.write('🗑️  清空所有数据...')
        from apps.settings_sys.models import (
            Department, Role, Permission, RolePermission, Tag, SystemConfig,
            WarehouseConfig, ThirdPartyWarehouse, PlatformConfig, PlatformAuth,
            AssistantTask, SSOConfig, UserProfile, UserRole, UserDepartment
        )
        from apps.finance.models import (
            PaymentRequestPool, PaymentRequest, ReceiptOrder, TransactionFlow,
            OrderProfit, SettlementProfit, ExpenseRecord, ExpenseType, CostValuation
        )
        from apps.purchase.models import Supplier, PurchaseOrder
        from apps.wms.models import WarehouseWms, Inventory, Product as WmsProduct
        from apps.sales.models import AmazonListing, ListingSkuMapping

        for m in [Department, Role, Permission, RolePermission, Tag, SystemConfig,
                  WarehouseConfig, ThirdPartyWarehouse, PlatformConfig, PlatformAuth,
                  AssistantTask, SSOConfig, UserProfile, UserRole, UserDepartment,
                  PaymentRequestPool, PaymentRequest, ReceiptOrder, TransactionFlow,
                  OrderProfit, SettlementProfit, ExpenseRecord, ExpenseType, CostValuation,
                  Supplier, PurchaseOrder, WarehouseWms, Inventory, WmsProduct,
                  AmazonListing, ListingSkuMapping]:
            try:
                m.objects.all().delete()
            except Exception:
                pass
        self.stdout.write('   ✅ 数据已清空')
