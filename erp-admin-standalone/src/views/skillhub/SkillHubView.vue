<template>
  <div class="skillhub-view">
    <!-- 页面头部 -->
    <div class="sh-header">
      <div class="sh-header-left">
        <h2 class="sh-title">
          <el-icon :size="24"><Shop /></el-icon>
          技能商城
        </h2>
        <p class="sh-subtitle">卖家之家跨境电商 AI 技能市场 · 为您的 ERP 增添专业能力</p>
      </div>
      <div class="sh-header-right">
        <el-button
          :type="viewMode === 'market' ? 'primary' : 'default'"
          size="small"
          @click="viewMode = 'market'"
        >
          <el-icon><Search /></el-icon>
          技能市场
        </el-button>
        <el-button
          :type="viewMode === 'installed' ? 'primary' : 'default'"
          size="small"
          @click="viewMode = 'installed'"
        >
          <el-icon><FolderOpened /></el-icon>
          已安装 ({{ store.installedSkills.length }})
        </el-button>
      </div>
    </div>

    <!-- ==================== 技能市场视图 ==================== -->
    <template v-if="viewMode === 'market'">
      <!-- 筛选栏 -->
      <div class="sh-filters">
        <div class="sh-filter-row">
          <el-input
            v-model="store.filters.keywords"
            placeholder="搜索技能名称或关键词..."
            class="sh-search-input"
            clearable
            @keyup.enter="handleSearch"
            @clear="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-select
            v-model="store.filters.orderBy"
            placeholder="排序"
            class="sh-order-select"
            @change="handleSearch"
          >
            <el-option label="综合热度" value="default" />
            <el-option label="最新发布" value="new" />
            <el-option label="热门排行" value="hot" />
          </el-select>
          <el-select
            v-model="store.filters.payable"
            placeholder="付费类型"
            class="sh-pay-select"
            clearable
            @change="handleSearch"
          >
            <el-option label="全部" :value="undefined" />
            <el-option label="免费" :value="false" />
            <el-option label="付费" :value="true" />
          </el-select>
          <el-button type="primary" @click="handleSearch" :loading="store.loading">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
        </div>

        <!-- 标签筛选 -->
        <div class="sh-label-row" v-if="store.labelGroups.length">
          <template v-for="group in store.labelGroups" :key="group.groupName">
            <div class="sh-label-group">
              <span class="sh-label-group-name">{{ group.groupName }}</span>
              <template v-for="label in group.items" :key="label.id">
                <el-check-tag
                  :checked="isLabelSelected(label.id)"
                  class="sh-label-tag"
                  @change="(checked) => toggleLabel(label.id, checked)"
                >
                  {{ label.name }}
                </el-check-tag>
              </template>
            </div>
          </template>
        </div>
      </div>

      <!-- 技能列表 -->
      <div class="sh-grid" v-loading="store.loading" element-loading-text="正在搜索技能...">
        <template v-if="store.skills.length">
          <div
            v-for="skill in store.skills"
            :key="skill.id || skill.slug"
            class="sh-card"
            @click="openDetail(skill)"
          >
            <!-- 卡片头部 -->
            <div class="sh-card-header">
              <div class="sh-card-icon">
                <el-icon :size="20"><Box /></el-icon>
              </div>
              <div class="sh-card-title-wrap">
                <h4 class="sh-card-name">{{ skill.name }}</h4>
                <div class="sh-card-meta">
                  <el-tag
                    v-if="skill.priceType === 'paid' || skill.priceType === 'freeAndPaid'"
                    type="warning" size="small" effect="plain">付费</el-tag>
                  <el-tag v-else type="success" size="small" effect="plain">免费</el-tag>
                  <el-tag v-if="skill.source" size="small" type="info" effect="plain">
                    {{ formatSource(skill.source) }}
                  </el-tag>
                  <span v-if="skill.version" class="sh-version">v{{ skill.version }}</span>
                </div>
              </div>
              <!-- 已安装标记 -->
              <el-tag v-if="store.checkInstalled(skill.slug || skill.id)" type="primary" size="small" effect="dark">
                已安装
              </el-tag>
            </div>

            <!-- 描述 -->
            <p class="sh-card-desc">{{ skill.description || '暂无描述' }}</p>

            <!-- 标签 -->
            <div class="sh-card-tags" v-if="skill.tags && skill.tags.length">
              <el-tag v-for="(tag, i) in skill.tags.slice(0, 4)" :key="i" size="small" round>
                {{ tag }}
              </el-tag>
              <span v-if="skill.tags.length > 4" class="sh-tags-more">+{{ skill.tags.length - 4 }}</span>
            </div>

            <!-- 底部操作 -->
            <div class="sh-card-footer">
              <span class="sh-card-date">{{ formatDate(skill.updateTime || skill.updatedAt) }}</span>
              <el-button
                v-if="store.checkInstalled(skill.slug || skill.id)"
                size="small"
                type="danger"
                plain
                @click.stop="handleUninstallSkill(skill)"
              >
                卸载
              </el-button>
              <el-button
                v-else
                size="small"
                type="primary"
                @click.stop="handleInstallSkill(skill)"
                :loading="installingSlug === (skill.slug || skill.id)"
                :disabled="skill.priceType === 'paid'"
              >
                {{ skill.priceType === 'paid' ? '付费' : '安装' }}
              </el-button>
            </div>
          </div>
        </template>

        <!-- 空状态 -->
        <el-empty
          v-else-if="!store.loading"
          description="暂无技能数据，请尝试其他搜索条件"
          :image-size="120"
        >
          <el-button type="primary" @click="handleSearch">刷新列表</el-button>
        </el-empty>
      </div>

      <!-- 加载更多 -->
      <div class="sh-load-more" v-if="store.nextPosition && store.skills.length">
        <el-button :loading="store.loading" @click="store.loadMore()">
          加载更多技能
        </el-button>
      </div>
    </template>

    <!-- ==================== 已安装视图 ==================== -->
    <template v-else>
      <div class="sh-installed" v-if="store.installedSkills.length">
        <div class="sh-installed-grid">
          <div
            v-for="skill in store.installedSkills"
            :key="skill.slug"
            class="sh-card sh-card--installed"
          >
            <div class="sh-card-header">
              <div class="sh-card-icon sh-card-icon--installed">
                <el-icon :size="20"><CircleCheckFilled /></el-icon>
              </div>
              <div class="sh-card-title-wrap">
                <h4 class="sh-card-name">{{ skill.name }}</h4>
                <div class="sh-card-meta">
                  <span class="sh-installed-date">安装于 {{ formatDate(skill.installedAt) }}</span>
                </div>
              </div>
            </div>
            <p class="sh-card-desc">{{ skill.description || '暂无描述' }}</p>
            <div class="sh-card-footer">
              <el-tag v-if="skill.downloaded" type="success" size="small" effect="plain">已下载</el-tag>
              <el-tag v-else type="warning" size="small" effect="plain">待下载</el-tag>
              <el-button size="small" type="danger" plain @click="handleUninstallSkill(skill)">
                卸载
              </el-button>
            </div>
          </div>
        </div>
      </div>
      <el-empty v-else description="尚未安装任何技能" :image-size="120">
        <el-button type="primary" @click="viewMode = 'market'">去技能市场看看</el-button>
      </el-empty>
    </template>

    <!-- 技能详情弹窗 -->
    <SkillDetailDialog
      v-model="detailVisible"
      :skill="currentSkill"
      @installed="onSkillInstalled"
      @uninstalled="onSkillUninstalled"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Shop, Search, FolderOpened, Box, CircleCheckFilled } from '@element-plus/icons-vue'
import { useSkillHubStore } from '@/stores/skillhub'
import SkillDetailDialog from '@/components/SkillDetailDialog.vue'

const store = useSkillHubStore()

// ── 视图状态 ──
const viewMode = ref('market')       // market | installed
const detailVisible = ref(false)
const currentSkill = ref(null)
const installingSlug = ref(null)
const selectedLabels = ref([])

// ── 生命周期 ──
onMounted(async () => {
  await store.loadLabels()
  await store.searchSkills()
})

// ── 筛选方法 ──
function isLabelSelected(labelId) {
  return selectedLabels.value.includes(String(labelId))
}

function toggleLabel(labelId, checked) {
  if (checked) {
    selectedLabels.value.push(String(labelId))
  } else {
    selectedLabels.value = selectedLabels.value.filter(id => id !== String(labelId))
  }
  store.filters.labelIds = selectedLabels.value.join(',')
  handleSearch()
}

function handleSearch() {
  store.filters.pageIndex = 1
  store.searchSkills()
}

// ── 技能操作 ──
function openDetail(skill) {
  currentSkill.value = skill
  detailVisible.value = true
}

async function handleInstallSkill(skill) {
  installingSlug.value = skill.slug || skill.id
  try {
    await store.installSkill(skill)
    ElMessage.success(`「${skill.name}」安装成功`)
  } catch (e) {
    ElMessage.error('安装失败')
  } finally {
    installingSlug.value = null
  }
}

async function handleUninstallSkill(skill) {
  try {
    await ElMessageBox.confirm(
      `确定要卸载「${skill.name}」吗？`,
      '确认卸载',
      { confirmButtonText: '卸载', cancelButtonText: '取消', type: 'warning' }
    )
    store.uninstallSkill(skill.slug || skill.id)
    ElMessage.success(`「${skill.name}」已卸载`)
  } catch {
    // 用户取消
  }
}

function onSkillInstalled(skill) {
  // 详情弹窗安装回调
}

function onSkillUninstalled(skill) {
  // 详情弹窗卸载回调
}

// ── 工具方法 ──
function formatSource(source) {
  const map = { clawhub: 'ClawHub', skillhub: 'SkillHub' }
  return map[source] || source || ''
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  try {
    const d = new Date(dateStr)
    if (isNaN(d.getTime())) return dateStr
    return d.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
  } catch {
    return dateStr
  }
}
</script>

<style scoped>
.skillhub-view {
  padding: 20px 24px;
  max-width: 1400px;
  margin: 0 auto;
  min-height: calc(100vh - 120px);
}

/* ── 头部 ── */
.sh-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}
.sh-header-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.sh-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary, #303133);
}
.sh-subtitle {
  margin: 0;
  font-size: 13px;
  color: var(--text-secondary, #909399);
}
.sh-header-right {
  display: flex;
  gap: 8px;
}

/* ── 筛选栏 ── */
.sh-filters {
  background: var(--bg-card, #fff);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.sh-filter-row {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}
.sh-search-input {
  flex: 1;
  min-width: 200px;
  max-width: 400px;
}
.sh-order-select {
  width: 130px;
}
.sh-pay-select {
  width: 110px;
}
.sh-label-row {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.sh-label-group {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
.sh-label-group-name {
  font-size: 12px;
  color: var(--text-secondary, #909399);
  white-space: nowrap;
  min-width: 60px;
}
.sh-label-tag {
  font-size: 12px;
}

/* ── 卡片网格 ── */
.sh-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 14px;
  min-height: 200px;
}

/* ── 卡片 ── */
.sh-card {
  background: var(--bg-card, #fff);
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid var(--border-light, #ebeef5);
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.sh-card:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
  border-color: var(--brand, #409eff);
  transform: translateY(-1px);
}
.sh-card--installed {
  border-color: var(--el-color-success-light-5, #b3e19d);
}
.sh-card-header {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}
.sh-card-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}
.sh-card-icon--installed {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}
.sh-card-title-wrap {
  flex: 1;
  min-width: 0;
}
.sh-card-name {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary, #303133);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.sh-card-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 4px;
  flex-wrap: wrap;
}
.sh-version {
  font-size: 11px;
  color: var(--text-placeholder, #c0c4cc);
}
.sh-card-desc {
  margin: 0;
  font-size: 13px;
  color: var(--text-regular, #606266);
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.sh-card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.sh-tags-more {
  font-size: 11px;
  color: var(--text-placeholder, #c0c4cc);
  line-height: 22px;
}
.sh-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
}
.sh-card-date {
  font-size: 12px;
  color: var(--text-placeholder, #c0c4cc);
}

/* ── 加载更多 ── */
.sh-load-more {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

/* ── 已安装视图 ── */
.sh-installed {
  min-height: 200px;
}
.sh-installed-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 14px;
}
.sh-installed-date {
  font-size: 12px;
  color: var(--text-secondary, #909399);
}
</style>
