import { ref } from 'vue'
import { getBudgetSummary as apiGetBudgetSummary, setBudget as apiSetBudget, setCategoryBudget as apiSetCategoryBudget } from '../services/api'

export function useBudget() {
  const loading = ref(false)
  const error = ref('')
  
  const summary = ref({
    month: '',
    total_budget: 0,
    total_actual: 0,
    total_remaining: 0,
    total_percent: 0,
    category_budgets: []
  })

  async function fetchBudgetSummary(month) {
    loading.value = true
    error.value = ''
    try {
      summary.value = await apiGetBudgetSummary(month)
    } catch (err) {
      console.error('Failed to fetch budget summary:', err)
      error.value = 'Gagal memuat data anggaran.'
    } finally {
      loading.value = false
    }
  }

  async function updateBudget(month, amount) {
    loading.value = true
    error.value = ''
    try {
      await apiSetBudget({ month, amount })
      await fetchBudgetSummary(month)
    } catch (err) {
      console.error('Failed to set budget:', err)
      error.value = 'Gagal menyimpan anggaran.'
    } finally {
      loading.value = false
    }
  }

  async function updateCategoryBudget(month, categoryName, amount) {
    loading.value = true
    error.value = ''
    try {
      await apiSetCategoryBudget({ month, category_name: categoryName, amount })
      await fetchBudgetSummary(month)
    } catch (err) {
      console.error('Failed to set category budget:', err)
      error.value = 'Gagal menyimpan anggaran kategori.'
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    summary,
    fetchBudgetSummary,
    updateBudget,
    updateCategoryBudget
  }
}
