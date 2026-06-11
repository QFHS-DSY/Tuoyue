/**
 * 设置系统 API 服务
 * 涵盖：部门管理 / 角色权限 / 数据权限 / 仓库配置 / 平台授权 / 助手 / 安全
 */
import request from '@/utils/request'

const BASE = '/api/settings'

// ======================== 部门管理 ========================
export const getDepartments = (params) => request.get(`${BASE}/departments/`, { params })
export const getDepartmentTree = () => request.get(`${BASE}/departments/tree/`)
export const getDepartmentSimple = () => request.get(`${BASE}/departments/simple/`)
export const createDepartment = (data) => request.post(`${BASE}/departments/`, data)
export const updateDepartment = (id, data) => request.put(`${BASE}/departments/${id}/`, data)
export const deleteDepartment = (id) => request.delete(`${BASE}/departments/${id}/`)

// ======================== 用户扩展资料 ========================
export const getUserProfiles = (params) => request.get(`${BASE}/user-profiles/`, { params })
export const updateUserProfile = (id, data) => request.put(`${BASE}/user-profiles/${id}/`, data)

// ======================== 角色管理 ========================
export const getRoles = (params) => request.get(`${BASE}/roles/`, { params })
export const createRole = (data) => request.post(`${BASE}/roles/`, data)
export const updateRole = (id, data) => request.put(`${BASE}/roles/${id}/`, data)
export const deleteRole = (id) => request.delete(`${BASE}/roles/${id}/`)
export const getRolePermissions = (id) => request.get(`${BASE}/roles/${id}/permissions/`)
export const setRolePermissions = (id, data) => request.post(`${BASE}/roles/${id}/set_permissions/`, data)

// ======================== 权限管理 ========================
export const getPermissions = (params) => request.get(`${BASE}/permissions/`, { params })
export const getPermissionTree = () => request.get(`${BASE}/permissions/tree/`)
export const createPermission = (data) => request.post(`${BASE}/permissions/`, data)
export const updatePermission = (id, data) => request.put(`${BASE}/permissions/${id}/`, data)
export const deletePermission = (id) => request.delete(`${BASE}/permissions/${id}/`)

// ======================== 角色-权限关联 ========================
export const getRolePermRelations = (params) => request.get(`${BASE}/role-permissions/`, { params })

// ======================== 用户-角色关联 ========================
export const getUserRoles = (params) => request.get(`${BASE}/user-roles/`, { params })
export const assignUserRole = (data) => request.post(`${BASE}/user-roles/`, data)
export const removeUserRole = (id) => request.delete(`${BASE}/user-roles/${id}/`)

// ======================== 用户-部门关联 ========================
export const getUserDepartments = (params) => request.get(`${BASE}/user-departments/`, { params })
export const assignUserDepartment = (data) => request.post(`${BASE}/user-departments/`, data)
export const removeUserDepartment = (id) => request.delete(`${BASE}/user-departments/${id}/`)

// ======================== 数据权限 ========================
export const getDataPermissions = (params) => request.get(`${BASE}/data-permissions/`, { params })
export const createDataPermission = (data) => request.post(`${BASE}/data-permissions/`, data)
export const getUserDataPermissions = (params) => request.get(`${BASE}/user-data-permissions/`, { params })
export const assignUserDataPermission = (data) => request.post(`${BASE}/user-data-permissions/`, data)

// ======================== 离职交接 ========================
export const getHandoverRecords = (params) => request.get(`${BASE}/handover-records/`, { params })
export const createHandover = (data) => request.post(`${BASE}/handover-records/`, data)

// ======================== 日志 ========================
export const getOperationLogs = (params) => request.get(`${BASE}/operation-logs/`, { params })
export const getBatchImportLogs = (params) => request.get(`${BASE}/batch-import-logs/`, { params })
export const getAuditLogs = (params) => request.get(`${BASE}/audit-logs/`, { params })

// ======================== 系统配置 ========================
export const getSystemConfigs = (params) => request.get(`${BASE}/system-configs/`, { params })
export const createSystemConfig = (data) => request.post(`${BASE}/system-configs/`, data)
export const updateSystemConfig = (id, data) => request.put(`${BASE}/system-configs/${id}/`, data)
export const deleteSystemConfig = (id) => request.delete(`${BASE}/system-configs/${id}/`)
export const getConfigByGroup = (group) => request.get(`${BASE}/system-configs/by_group/`, { params: { group } })

// ======================== 全局标签 ========================
export const getTags = (params) => request.get(`${BASE}/tags/`, { params })
export const createTag = (data) => request.post(`${BASE}/tags/`, data)
export const updateTag = (id, data) => request.put(`${BASE}/tags/${id}/`, data)
export const deleteTag = (id) => request.delete(`${BASE}/tags/${id}/`)

// ======================== 仓库配置 ========================
export const getWarehouseConfigs = (params) => request.get(`${BASE}/warehouse-configs/`, { params })
export const createWarehouseConfig = (data) => request.post(`${BASE}/warehouse-configs/`, data)
export const updateWarehouseConfig = (id, data) => request.put(`${BASE}/warehouse-configs/${id}/`, data)
export const deleteWarehouseConfig = (id) => request.delete(`${BASE}/warehouse-configs/${id}/`)

// ======================== 第三方海外仓 ========================
export const getThirdPartyWarehouses = (params) => request.get(`${BASE}/third-party-warehouses/`, { params })
export const createThirdPartyWarehouse = (data) => request.post(`${BASE}/third-party-warehouses/`, data)
export const updateThirdPartyWarehouse = (id, data) => request.put(`${BASE}/third-party-warehouses/${id}/`, data)

// ======================== 仓库配对映射 ========================
export const getWarehouseMappings = (params) => request.get(`${BASE}/warehouse-mappings/`, { params })
export const createWarehouseMapping = (data) => request.post(`${BASE}/warehouse-mappings/`, data)
export const updateWarehouseMapping = (id, data) => request.put(`${BASE}/warehouse-mappings/${id}/`, data)

// ======================== 平台配置 ========================
export const getPlatformConfigs = (params) => request.get(`${BASE}/platform-configs/`, { params })
export const createPlatformConfig = (data) => request.post(`${BASE}/platform-configs/`, data)
export const updatePlatformConfig = (id, data) => request.put(`${BASE}/platform-configs/${id}/`, data)

// ======================== 平台授权 ========================
export const getPlatformAuths = (params) => request.get(`${BASE}/platform-auths/`, { params })
export const createPlatformAuth = (data) => request.post(`${BASE}/platform-auths/`, data)
export const updatePlatformAuth = (id, data) => request.put(`${BASE}/platform-auths/${id}/`, data)
export const deletePlatformAuth = (id) => request.delete(`${BASE}/platform-auths/${id}/`)
export const refreshPlatformToken = (id) => request.post(`${BASE}/platform-auths/${id}/refresh_token/`)

// ======================== 店铺授权 ========================
export const getShopAuths = (params) => request.get(`${BASE}/shop-auths/`, { params })
export const createShopAuth = (data) => request.post(`${BASE}/shop-auths/`, data)
export const updateShopAuth = (id, data) => request.put(`${BASE}/shop-auths/${id}/`, data)

// ======================== 广告授权 ========================
export const getAdAccountAuths = (params) => request.get(`${BASE}/ad-account-auths/`, { params })

// ======================== 邮箱绑定 ========================
export const getEmailBindings = (params) => request.get(`${BASE}/email-bindings/`, { params })
export const createEmailBinding = (data) => request.post(`${BASE}/email-bindings/`, data)
export const updateEmailBinding = (id, data) => request.put(`${BASE}/email-bindings/${id}/`, data)

// ======================== 助手任务 ========================
export const getAssistantTasks = (params) => request.get(`${BASE}/assistant-tasks/`, { params })
export const createAssistantTask = (data) => request.post(`${BASE}/assistant-tasks/`, data)
export const updateAssistantTask = (id, data) => request.put(`${BASE}/assistant-tasks/${id}/`, data)
export const executeAssistantTask = (id) => request.post(`${BASE}/assistant-tasks/${id}/execute/`)
export const toggleAssistantTask = (id) => request.post(`${BASE}/assistant-tasks/${id}/toggle/`)

// ======================== API Token ========================
export const getApiTokens = (params) => request.get(`${BASE}/api-tokens/`, { params })
export const createApiToken = (data) => request.post(`${BASE}/api-tokens/`, data)
export const revokeApiToken = (id) => request.post(`${BASE}/api-tokens/${id}/revoke/`)

// ======================== SSO 配置 ========================
export const getSSOConfigs = (params) => request.get(`${BASE}/sso-configs/`, { params })
export const createSSOConfig = (data) => request.post(`${BASE}/sso-configs/`, data)
export const updateSSOConfig = (id, data) => request.put(`${BASE}/sso-configs/${id}/`, data)

// ======================== 通知设置 ========================
export const getNotificationSettings = (params) => request.get(`${BASE}/notification-settings/`, { params })
export const updateNotificationSetting = (id, data) => request.put(`${BASE}/notification-settings/${id}/`, data)
