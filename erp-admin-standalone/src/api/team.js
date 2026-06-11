import request from '@/utils/request'

export function getTeamMembers(params) { return request.get('/api/team/members/', { params }) }
export function createTeamMember(data) { return request.post('/api/team/members/', data) }
export function updateTeamMember(id, data) { return request.put(`/api/team/members/${id}/`, data) }
export function deleteTeamMember(id) { return request.delete(`/api/team/members/${id}/`) }
export function getTeamAuditLogs(params) { return request.get('/api/team/audit-logs/', { params }) }
