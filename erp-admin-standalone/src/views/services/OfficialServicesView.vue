<template>
  <div class="page-container">
    <div class="page-header">
      <div class="page-header-left"><h1>官方服务</h1><p>合规体检 · 政策申报 · 供应链对接</p></div>
    </div>

    <el-row :gutter="20">
      <!-- 1. 合规体检 -->
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header><div class="sc-header"><el-icon color="#085B9C"><Checked /></el-icon><span>一键合规体检</span></div></template>
          <p style="font-size:13px;color:#606266;margin:0 0 12px;line-height:1.6">AI 全局扫描，覆盖跨境出海核心合规风险点，3 分钟出具体检报告</p>
          <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px">
            <el-tag size="small" type="primary">知识产权排查</el-tag>
            <el-tag size="small" type="warning">VAT 税务合规</el-tag>
            <el-tag size="small" type="danger">海关政策预警</el-tag>
            <el-tag size="small" type="success">产品资质审查</el-tag>
            <el-tag size="small">平台禁售品校验</el-tag>
            <el-tag size="small">出口管制筛查</el-tag>
          </div>
          <el-divider style="margin:8px 0" />
          <div v-if="complianceResult" class="sc-result">
            <div class="sc-score"><span>{{ complianceResult.score }}</span>分</div>
            <div class="sc-section"><div class="sc-label green">✅ 通过 ({{complianceResult.passed.length}}项)</div><div v-for="p in complianceResult.passed" :key="p" class="sc-item">{{p}}</div></div>
            <div class="sc-section"><div class="sc-label red">❌ 未通过 ({{complianceResult.failed.length}}项)</div><div v-for="f in complianceResult.failed" :key="f.item" class="sc-item red">{{f.item}}: {{f.reason}}</div></div>
            <div class="sc-section"><div class="sc-label orange">💡 AI整改建议</div><div v-for="s in complianceResult.suggestions" :key="s" class="sc-item">{{s}}</div></div>
            <el-divider style="margin:8px 0" />
          </div>
          <el-button type="primary" :loading="checkLoading" @click="runCheck" style="width:100%">{{ complianceResult?'重新体检':'开始体检' }}</el-button>
        </el-card>
      </el-col>

      <!-- 2. 扶持政策 -->
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header><div class="sc-header"><el-icon color="#E6A23C"><Trophy /></el-icon><span>扶持政策申报</span></div></template>
          <div style="margin-bottom:12px;font-size:13px;color:#606266;line-height:1.6">实时跟踪省、市、区三级跨境电商扶持资金与补贴政策</div>
          <div style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:8px">
            <el-tag size="small" type="warning" effect="plain">🔥 即将截止</el-tag>
            <el-tag size="small" type="success" effect="plain">省级补贴</el-tag>
            <el-tag size="small" effect="plain">市级项目</el-tag>
          </div>
          <ul class="policy-static-list">
            <li><span class="policy-bullet">📋</span><div><strong>2026年度省级跨境电商发展专项资金申报</strong><br><span style="font-size:12px;color:#E6A23C">即将截止 · 最高补贴 200 万元</span></div></li>
            <li><span class="policy-bullet">🏗️</span><div><strong>独立站建设及海外仓租赁补贴指引</strong><br><span style="font-size:12px;color:#909399">建站费用 50% 补贴，上限 20 万元</span></div></li>
            <li><span class="policy-bullet">💰</span><div><strong>OPC 个人创业者专项免息贷款通道</strong><br><span style="font-size:12px;color:#909399">最高额度 50 万元，2 年免息期</span></div></li>
          </ul>
          <el-divider style="margin:8px 0" />
          <div v-loading="policyLoading" style="min-height:40px">
            <div v-for="p in policies" :key="p.id" class="policy-card">
              <h4>{{ p.name }}</h4>
              <div class="policy-meta">
                <el-tag size="small" type="success">{{ p.subsidy }}</el-tag>
                <span style="font-size:12px;color:#909399;margin-left:8px">截止: {{ p.deadline }}</span>
              </div>
              <div class="policy-cond">{{ p.condition }}</div>
              <el-button size="small" type="primary" plain @click="applyPolicy(p.id)" style="margin-top:8px">一键申报</el-button>
            </div>
          </div>
          <div style="text-align:right;margin-top:8px">
            <el-button type="primary" plain size="small" @click="handleApplyPolicy">立即申报</el-button>
          </div>
        </el-card>
      </el-col>

      <!-- 3. 辽宁供应链 -->
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header><div class="sc-header"><el-icon color="#2ead3e"><Shop /></el-icon><span>辽宁本地供应链</span></div></template>
          <div style="margin-bottom:12px;font-size:13px;color:#606266;line-height:1.6">深耕辽宁 14 个地级市产业带，源头工厂直供，跨境卖家专属供货通道</div>
          <ul class="supply-static-list">
            <li><span class="supply-bullet">👙</span><div><strong>葫芦岛泳装产业带</strong><br><span style="font-size:12px;color:#909399">源头工厂直供，支持一件代发，覆盖全球尺码</span></div></li>
            <li><span class="supply-bullet">⚙️</span><div><strong>沈阳装备制造/五金配件</strong><br><span style="font-size:12px;color:#909399">重工品质，适合亚马逊 B2B 及企业采购</span></div></li>
            <li><span class="supply-bullet">🐟</span><div><strong>大连/丹东农产品及海鲜加工</strong><br><span style="font-size:12px;color:#909399">跨境生鲜、休闲食品及预制菜供应链</span></div></li>
          </ul>
          <el-divider style="margin:8px 0" />
          <div v-loading="supplierLoading" style="min-height:40px">
            <div v-for="s in suppliers" :key="s.id" class="supplier-card">
              <h4>{{ s.name }}</h4>
              <div class="supplier-tags">
                <el-tag size="small">{{ s.category }}</el-tag>
                <el-tag size="small" type="warning">起订: {{ s.moq }}件</el-tag>
                <el-tag v-if="s.dropship" size="small" type="success">一件代发</el-tag>
              </div>
              <div class="supplier-subsidy">{{ s.subsidy }}</div>
              <el-button size="small" type="success" plain @click="contactSupplier(s.id)" style="margin-top:8px">一键对接工厂</el-button>
            </div>
          </div>
          <div style="text-align:right;margin-top:8px">
            <el-button type="success" plain size="small" @click="handleViewSuppliers">查看供应商库</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 政策申报弹窗 -->
    <el-dialog v-model="policyDialogVisible" title="辽宁省跨境电商扶持资金申报" width="500px" destroy-on-close>
      <el-form label-width="90px">
        <el-form-item label="企业名称">
          <el-input v-model="policyForm.companyName" placeholder="请输入企业全称" />
        </el-form-item>
        <el-form-item label="信用代码">
          <el-input v-model="policyForm.creditCode" placeholder="统一社会信用代码" />
        </el-form-item>
        <el-form-item label="申报项目">
          <el-select v-model="policyForm.project" placeholder="请选择申报项目" style="width:100%">
            <el-option label="省级跨境电商发展专项资金" value="provincial" />
            <el-option label="独立站及海外仓建设补贴" value="overseas" />
            <el-option label="创业免息贷款" value="loan" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="policyDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="policySubmitting" @click="submitPolicy">提交申报</el-button>
      </template>
    </el-dialog>

    <!-- 供应商库抽屉 -->
    <el-drawer v-model="supplierDrawerVisible" title="辽宁优质供应商名录" size="400px" direction="rtl">
      <div style="display:flex;flex-direction:column;gap:14px">
        <div style="padding:14px;border-radius:10px;background:var(--bg-page);border:1px solid var(--border)">
          <div style="font-size:15px;font-weight:600;margin-bottom:6px">🏭 葫芦岛泳装工厂</div>
          <div style="display:flex;gap:4px;margin-bottom:6px">
            <el-tag size="small" type="success">一件代发</el-tag>
            <el-tag size="small" type="warning">支持定制</el-tag>
          </div>
          <div style="font-size:12px;color:#909399">主营：泳装、沙滩裤、防晒衣 | 年产能 200 万件</div>
        </div>
        <div style="padding:14px;border-radius:10px;background:var(--bg-page);border:1px solid var(--border)">
          <div style="font-size:15px;font-weight:600;margin-bottom:6px">⚙️ 沈阳精密五金厂</div>
          <div style="display:flex;gap:4px;margin-bottom:6px">
            <el-tag size="small" type="primary">源头工厂</el-tag>
            <el-tag size="small">B2B 批量</el-tag>
          </div>
          <div style="font-size:12px;color:#909399">主营：五金配件、工具套装 | 亚马逊 FBA 包装适配</div>
        </div>
        <div style="padding:14px;border-radius:10px;background:var(--bg-page);border:1px solid var(--border)">
          <div style="font-size:15px;font-weight:600;margin-bottom:6px">🐟 大连海产加工基地</div>
          <div style="display:flex;gap:4px;margin-bottom:6px">
            <el-tag size="small" type="success">一件代发</el-tag>
            <el-tag size="small" type="warning">跨境冷链</el-tag>
          </div>
          <div style="font-size:12px;color:#909399">主营：即食海鲜、休闲零食 | 支持跨境冷链物流</div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import { Checked, Trophy, Shop, List } from '@element-plus/icons-vue'
import { runComplianceCheck, getPolicies, applyPolicy, getSuppliers } from '@/api/services'

const checkLoading = ref(false); const complianceResult = ref(null)
const policyLoading = ref(false); const policies = ref([])
const supplierLoading = ref(false); const suppliers = ref([])

const policyDialogVisible = ref(false)
const policySubmitting = ref(false)
const policyForm = reactive({ companyName: '', creditCode: '', project: '' })
const supplierDrawerVisible = ref(false)

function handleApplyPolicy() {
  ElMessage.info('政策匹配中，请稍候...')
  setTimeout(() => { policyDialogVisible.value = true }, 1000)
}

function handleViewSuppliers() {
  ElMessage.info('正在打开供应商库...')
  setTimeout(() => { supplierDrawerVisible.value = true }, 1000)
}

async function submitPolicy() {
  if (!policyForm.companyName || !policyForm.creditCode || !policyForm.project) {
    ElMessage.warning('请完整填写企业信息')
    return
  }
  policySubmitting.value = true
  await new Promise(r => setTimeout(r, 1500))
  policySubmitting.value = false
  policyDialogVisible.value = false
  ElMessage.success('申报已提交！工作人员将在 3 个工作日内联系您')
  policyForm.companyName = ''; policyForm.creditCode = ''; policyForm.project = ''
}

function runCheck() {
  checkLoading.value = true
  setTimeout(() => {
    checkLoading.value = false
    complianceResult.value = {
      score: 92,
      passed: ['知识产权排查', '平台禁售品校验', '出口管制筛查'],
      failed: [
        { item: 'VAT 税务合规', reason: '欧洲区 VAT 政策近期调整，建议重新核查' },
      ],
      suggestions: ['关注欧洲区 VAT 政策变动，及时更新税务设置', '建议对德国站 WEEE 注册号进行年度复审'],
    }
    ElNotification({
      title: '合规体检完成',
      message: 'AI 扫描已结束。您的商品库未发现严重侵权风险。温馨提示：近期欧洲区 VAT 政策有变动，请关注税务合规模块的相关预警。',
      type: 'success',
      duration: 5000,
    })
  }, 2000)
}
async function loadPolicies() { policyLoading.value = true; try { const r = await getPolicies(); policies.value = r?.data?.policies || [] } finally { policyLoading.value = false } }
async function contactSupplier(id) { ElMessage.success('已发送对接请求，专属客户经理将联系您') }
async function loadSuppliers() { supplierLoading.value = true; try { const r = await getSuppliers(); suppliers.value = r?.data?.suppliers || [] } finally { supplierLoading.value = false } }

onMounted(() => { loadPolicies(); loadSuppliers() })
</script>

<style scoped>
.page-container { padding:24px;max-width:1400px;margin:0 auto }
.page-header { margin-bottom:24px }
.page-header h1 { margin:0 0 4px;font-size:22px }
.page-header p { margin:0;color:#909399;font-size:13px }
.sc-header { display:flex;align-items:center;gap:8px;font-weight:600 }
.sc-score { text-align:center;font-size:28px;font-weight:700;color:#085B9C;padding:12px 0 }
.sc-score span { font-size:48px }
.sc-section { margin-top:12px }
.sc-label { font-weight:600;margin-bottom:6px }.sc-label.green{color:#2ead3e}.sc-label.red{color:#F56C6C}.sc-label.orange{color:#E6A23C}
.sc-item { font-size:12px;color:#606266;padding:2px 0 }.sc-item.red{color:#F56C6C}
.policy-card { padding:12px 0;border-bottom:1px solid #f5f7fa }
.policy-card h4 { margin:0 0 6px;font-size:14px }
.policy-meta { margin-bottom:4px }
.policy-cond { font-size:12px;color:#909399 }
.supplier-card { padding:12px 0;border-bottom:1px solid #f5f7fa }
.supplier-card h4 { margin:0 0 6px;font-size:14px }
.supplier-tags { display:flex;gap:4px;margin-bottom:4px }
.supplier-subsidy { font-size:12px;color:#E6A23C }

/* 静态列表样式 */
.policy-static-list, .supply-static-list {
  list-style:none; padding:0; margin:0;
}
.policy-static-list li, .supply-static-list li {
  display:flex; align-items:flex-start; gap:8px;
  padding:8px 0; border-bottom:1px solid #f5f7fa; font-size:13px;
}
.policy-static-list li:last-child, .supply-static-list li:last-child { border-bottom:none; }
.policy-bullet, .supply-bullet { font-size:18px; flex-shrink:0; line-height:1.4; }
</style>
