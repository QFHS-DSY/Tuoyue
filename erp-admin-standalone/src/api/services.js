import request from '@/utils/request'

export function runComplianceCheck() { return request.post('/api/services/compliance-check/') }
export function getPolicies() { return request.get('/api/services/policies/') }
export function applyPolicy(policyId) { return request.post('/api/services/policies/', { policy_id: policyId }) }
export function getSuppliers() { return request.get('/api/services/suppliers/') }
