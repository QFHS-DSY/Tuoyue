/**
 * 达人检索 API
 * 后端 creator_mgt 模块完整，前端对接
 */
import request from '@/utils/request'

/** 达人搜索 - GET /api/creators/search/ */
export function searchCreators(params) {
  return request.get('/api/creators/search/', { params })
}

/** 达人列表 - GET /api/creators/ */
export function getCreatorList(params) {
  return request.get('/api/creators/', { params })
}

/** 达人详情 - GET /api/creators/{id}/ */
export function getCreatorDetail(id) {
  return request.get(`/api/creators/${id}/`)
}

/** 导入达人 - POST /api/creators/import/platform/ */
export function importCreator(data) {
  return request.post('/api/creators/import/platform/', data)
}

/** AI多语种邀约 - POST /api/ai/multilingual-pitch/ */
export function generatePitch(creatorId, targetLanguage = 'en') {
  return request.post('/api/ai/multilingual-pitch/', { creator_id: creatorId, target_language: targetLanguage })
}

/** 发送邀约 - POST /api/invitations/{creatorId}/send/ */
export function sendInvitation(creatorId, data) {
  return request.post(`/api/invitations/${creatorId}/send/`, data)
}

/** 达人看板聚合 - GET /api/dashboard/creator-board/ */
export function getCreatorDashboard() {
  return request.get('/api/dashboard/creator-board/')
}

/** 触发 AI 内容分析 - POST /api/ai/content-analysis/jobs/ */
export function triggerContentAnalysis(creatorId) {
  return request.post('/api/ai/content-analysis/jobs/', { creator_id: creatorId })
}

/** 获取达人 AI 洞察 - GET /api/creators/{id}/ai-insight/ */
export function getCreatorAIInsight(creatorId) {
  return request.get(`/api/creators/${creatorId}/ai-insight/`)
}

export default { searchCreators, getCreatorList, getCreatorDetail, importCreator, generatePitch,
  sendInvitation, getCreatorDashboard, triggerContentAnalysis, getCreatorAIInsight }
