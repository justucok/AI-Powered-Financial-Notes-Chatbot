import { ref } from 'vue'

import {
  createTransaction as createTransactionRequest,
  deleteTransaction as deleteTransactionRequest,
  updateTransaction as updateTransactionRequest,
  getSummary,
  getTransactions,
} from '../services/api'

function formatMonthKey(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  return `${year}-${month}`
}

function getCurrentMonth() {
  return formatMonthKey(new Date())
}

function mapSummaryPayload(payload) {
  return {
    balance: Number(payload?.balance || 0),
    income: Number(payload?.total_income || payload?.income || 0),
    expense: Number(payload?.total_expense || payload?.expense || 0),
  }
}

export function useTransactions() {
  const transactions = ref([])
  const summary = ref({
    balance: 0,
    income: 0,
    expense: 0,
  })
  const loading = ref(false)
  const selectedMonth = ref(getCurrentMonth())
  const lastUpdate = ref(Date.now())

  async function fetchTransactions() {
    transactions.value = await getTransactions(selectedMonth.value)
    return transactions.value
  }

  async function fetchSummary() {
    const response = await getSummary(selectedMonth.value)
    summary.value = mapSummaryPayload(response)
    return summary.value
  }

  async function fetchAll() {
    loading.value = true

    try {
      const [transactionList, summaryData] = await Promise.all([
        fetchTransactions(),
        fetchSummary(),
      ])

      return {
        transactions: transactionList,
        summary: summaryData,
      }
    } finally {
      loading.value = false
    }
  }

  function triggerUpdate() {
    lastUpdate.value = Date.now()
  }

  async function createTransaction(data) {
    loading.value = true

    try {
      const response = await createTransactionRequest(data)
      await fetchAll()
      triggerUpdate()
      return response
    } finally {
      loading.value = false
    }
  }

  async function deleteTransaction(id) {
    loading.value = true

    try {
      const response = await deleteTransactionRequest(id)
      await fetchAll()
      triggerUpdate()
      return response
    } finally {
      loading.value = false
    }
  }

  async function updateTransaction(id, data) {
    loading.value = true

    try {
      const response = await updateTransactionRequest(id, data)
      await fetchAll()
      triggerUpdate()
      return response
    } finally {
      loading.value = false
    }
  }

  async function setMonth(month) {
    selectedMonth.value = month
    await fetchAll()
  }

  return {
    transactions,
    summary,
    loading,
    selectedMonth,
    fetchTransactions,
    fetchSummary,
    fetchAll,
    createTransaction,
    deleteTransaction,
    updateTransaction,
    setMonth,
    lastUpdate,
    triggerUpdate,
  }
}
