import { ref, computed } from 'vue'
import { getTransactions, getSummary, getCategories } from '../services/api'

export function useStatistics() {
  const loading = ref(false)
  
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

  let currentController = null

  async function fetchStatisticsData(currentMonthKey) {
    if (currentController) currentController.abort()
    currentController = new AbortController()
    loading.value = true
    try {
      // Fetch concurrent data
      // 1. Current month transactions (for daily graph and pie chart)
      // 2. Monthly summaries for last 6 months
      // 3. All categories (for colors/icons)
      const last6 = getLast6MonthsKeys(currentMonthKey)
      
      const [transactionsRes, categoriesRes, ...summariesRes] = await Promise.all([
        getTransactions(currentMonthKey),
        getCategories(),
        ...last6.map(m => getSummary(m).then(data => ({ month: m, ...data })))
      ])

      dailyTransactions.value = transactionsRes
      allCategories.value = categoriesRes
      monthlySummaries.value = summariesRes
    } catch (err) {
      if (err.name === 'CanceledError' || err.code === 'ERR_CANCELED') return
      console.error("Failed to fetch statistics data:", err)
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    dailyTransactions,
    monthlySummaries,
    allCategories,
    fetchStatisticsData
  }
}
