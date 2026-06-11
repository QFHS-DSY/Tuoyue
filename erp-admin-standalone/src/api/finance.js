/**
 * 财务系统 API
 * 对接 /api/finance/ 前缀
 */
import request from '@/utils/request'

const prefix = '/api/finance'

// 请款池
export const getPaymentPool = (params) => request.get(`${prefix}/payment-pool/`, { params })
export const getPaymentPoolById = (id) => request.get(`${prefix}/payment-pool/${id}/`)

// 请款单
export const getPaymentRequests = (params) => request.get(`${prefix}/payment-request/`, { params })
export const getPaymentRequestById = (id) => request.get(`${prefix}/payment-request/${id}/`)
export const createPaymentRequest = (data) => request.post(`${prefix}/payment-request/`, data)
export const updatePaymentRequest = (id, data) => request.put(`${prefix}/payment-request/${id}/`, data)
export const deletePaymentRequest = (id) => request.delete(`${prefix}/payment-request/${id}/`)
export const approvePaymentRequest = (id, data) => request.post(`${prefix}/payment-request/${id}/approve/`, data)
export const rejectPaymentRequest = (id, data) => request.post(`${prefix}/payment-request/${id}/reject/`, data)
export const payPaymentRequest = (id, data) => request.post(`${prefix}/payment-request/${id}/pay/`, data)

// 收款单
export const getReceiptOrders = (params) => request.get(`${prefix}/receipt-order/`, { params })
export const getReceiptOrderById = (id) => request.get(`${prefix}/receipt-order/${id}/`)
export const createReceiptOrder = (data) => request.post(`${prefix}/receipt-order/`, data)
export const updateReceiptOrder = (id, data) => request.put(`${prefix}/receipt-order/${id}/`, data)
export const receiveReceiptOrder = (id, data) => request.post(`${prefix}/receipt-order/${id}/receive/`, data)

// 往来流水
export const getTransactionFlows = (params) => request.get(`${prefix}/transaction-flow/`, { params })
export const exportTransactionFlows = (params) => request.post(`${prefix}/transaction-flow/export/`, params)

// 订单利润
export const getOrderProfits = (params) => request.get(`${prefix}/order-profit/`, { params })
export const recalculateOrderProfit = (data) => request.post(`${prefix}/order-profit/recalculate/`, data)
export const exportOrderProfit = (params) => request.post(`${prefix}/order-profit/export/`, params)

// 结算利润
export const getSettlementProfits = (params) => request.get(`${prefix}/settlement-profit/`, { params })

// 账单明细
export const getBillDetails = (params) => request.get(`${prefix}/bill-detail/`, { params })

// 回款明细
export const getCollectionDetails = (params) => request.get(`${prefix}/collection-detail/`, { params })

// 费用管理
export const getExpenseTypes = (params) => request.get(`${prefix}/expense-type/`, { params })
export const createExpenseType = (data) => request.post(`${prefix}/expense-type/`, data)
export const updateExpenseType = (id, data) => request.put(`${prefix}/expense-type/${id}/`, data)
export const deleteExpenseType = (id) => request.delete(`${prefix}/expense-type/${id}/`)
export const getExpenseOrders = (params) => request.get(`${prefix}/expense-order/`, { params })
export const createExpenseOrder = (data) => request.post(`${prefix}/expense-order/`, data)
export const updateExpenseOrder = (id, data) => request.put(`${prefix}/expense-order/${id}/`, data)
export const deleteExpenseOrder = (id) => request.delete(`${prefix}/expense-order/${id}/`)

// 成本诊断
export const getCostDiagnoses = (params) => request.get(`${prefix}/cost-diagnosis/`, { params })
export const getCostResetRecords = (params) => request.get(`${prefix}/cost-reset-record/`, { params })

// 成本计价
export const getCostValuations = (params) => request.get(`${prefix}/cost-valuation/`, { params })
export const recalculateCostValuation = (data) => request.post(`${prefix}/cost-valuation/recalculate/`, data)
export const getWfsCosts = (params) => request.get(`${prefix}/wfs-cost/`, { params })

// 结账管理
export const getClosingPeriods = (params) => request.get(`${prefix}/closing-period/`, { params })
export const getClosingLogs = (params) => request.get(`${prefix}/closing-log/`, { params })
export const getClosingSetting = () => request.get(`${prefix}/closing-setting/1/`)

// 利润报表
export const getProfitReportConfigs = (params) => request.get(`${prefix}/profit-report-config/`, { params })
export const getProfitReportVersions = (params) => request.get(`${prefix}/profit-report-version/`, { params })
export const getExpenseAllocationRules = (params) => request.get(`${prefix}/expense-allocation-rule/`, { params })

// 业绩报表
export const getPerformanceReports = (params) => request.get(`${prefix}/performance-report/`, { params })
export const getTurnoverHandovers = (params) => request.get(`${prefix}/turnover-handover/`, { params })

export default {
  getPaymentPool, getPaymentRequests, getPaymentRequestById, createPaymentRequest, updatePaymentRequest,
  approvePaymentRequest, rejectPaymentRequest, payPaymentRequest,
  getReceiptOrders, getReceiptOrderById, createReceiptOrder, updateReceiptOrder, receiveReceiptOrder,
  getTransactionFlows, getOrderProfits, getSettlementProfits, getBillDetails, getCollectionDetails,
  getExpenseTypes, createExpenseType, getExpenseOrders, createExpenseOrder,
  getCostDiagnoses, getCostValuations, getClosingPeriods, getPerformanceReports,
}
