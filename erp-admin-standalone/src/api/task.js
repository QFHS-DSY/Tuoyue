/**
 * 通用任务管理 API
 * 接口 25-26
 */

import axios from 'axios'

const request = axios.create({
  timeout: 15000,
})

request.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

request.interceptors.response.use((response) => response.data, (error) => Promise.reject(error))

// ===================== API 函数 =====================

/**
 * 任务列表
 * GET /api/tasks/
 * @param {Object} params - { type?, status?, page, page_size }
 */
export const getTaskList = (params) =>
  request.get('/api/tasks/', { params })

/**
 * 任务详情
 * GET /api/tasks/{id}/
 */
export const getTaskDetail = (id) =>
  request.get(`/api/tasks/${id}/`)

/**
 * 创建任务
 * POST /api/tasks/
 * @param {Object} data - { name, type, config }
 */
export const createTask = (data) =>
  request.post('/api/tasks/', data)

/**
 * 更新任务
 * PUT /api/tasks/{id}/
 * @param {number} id
 * @param {Object} data
 */
export const updateTask = (id, data) =>
  request.put(`/api/tasks/${id}/`, data)

/**
 * 部分更新任务
 * PATCH /api/tasks/{id}/
 * @param {number} id
 * @param {Object} data
 */
export const patchTask = (id, data) =>
  request.patch(`/api/tasks/${id}/`, data)

/**
 * 删除任务
 * DELETE /api/tasks/{id}/
 * @param {number} id
 */
export const deleteTask = (id) =>
  request.delete(`/api/tasks/${id}/`)

export default { getTaskList, getTaskDetail, createTask, updateTask, patchTask, deleteTask }
