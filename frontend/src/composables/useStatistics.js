import { ref, computed } from 'vue'
import { getTransactions, getSummary, getCategories } from '../services/api'

export function useStatistics() {
  const loading = ref(false)
  const error = ref(null)
  
  // Data State
  const dailyTransactions = ref([])
  const monthlySummaries = ref([])
  const allCategories = ref([])
  
  // To get the last 6 months keys relative to a selected month
  function getLast6MonthsKeys(targetMonthKey) {
    const keys = []
    const [yearStr, monthStr] = targetMonthKey.split('-')
    const targetDate = new Date(parseInt(yearStr), parseInt(monthStr) - 1, 1)
    
    for (let i = 5; i >= 0; i--) {
      const m = new Date(targetDate.getFullYear(), targetDate.getMonth() - i, 1)
      const year = m.getFullYear()
      const month = String(m.getMonth() + 1).padStart(2, '0')
      keys.push(`${year}-${month}`)
    }
    return keys
  }

  let abortController = null
  
  async function fetchStatisticsData(currentMonthKey) {
    if (abortController) {
      abortController.abort()
    }
    abortController = new AbortController()

    loading.value = true
    try {
      // Fetch concurrent data
      // 1. Current month transactions (for daily graph and pie chart)
      // 2. Monthly summaries for last 6 months
      // 3. All categories (for colors/icons)
      const last6 = getLast6MonthsKeys(currentMonthKey)
      
      const [transactionsRes, categoriesRes, ...summariesRes] = await Promise.all([
        getTransactions(currentMonthKey, { signal: abortController.signal }),
        getCategories({ signal: abortController.signal }),
        ...last6.map(m => getSummary(m, { signal: abortController.signal }).then(data => ({ month: m, ...data })))
      ])

      dailyTransactions.value = transactionsRes
      allCategories.value = categoriesRes
      monthlySummaries.value = summariesRes
    } catch (err) {
      if (err.name === 'CanceledError' || err.message === 'canceled') {
        console.log('fetchStatisticsData request canceled')
        return // Do not update error or loading state if it was canceled
      }
      error.value = err.message || 'Gagal memuat data statistik'
      console.error("Failed to fetch statistics data:", err)
    } finally {
      if (!abortController || !abortController.signal.aborted) {
        loading.value = false
      }
    }
  }

  return {
    loading,
    error,
    dailyTransactions,
    monthlySummaries,
    allCategories,
    fetchStatisticsData
  }
}
