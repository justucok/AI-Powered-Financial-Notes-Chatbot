import { ref } from 'vue'

import { createCategory as createCategoryRequest, deleteCategory as deleteCategoryRequest, getCategories } from '../services/api'

export function useCategories() {
  const categories = ref([])
  const loading = ref(false)

  async function fetchCategories() {
    loading.value = true
    try {
      const data = await getCategories()
      categories.value = data.sort((a, b) => {
        if (a.type !== b.type) return a.type === 'expense' ? -1 : 1
        const aIsLainnya = a.name.toLowerCase() === 'lainnya'
        const bIsLainnya = b.name.toLowerCase() === 'lainnya'
        if (aIsLainnya && !bIsLainnya) return 1
        if (!aIsLainnya && bIsLainnya) return -1
        return a.name.localeCompare(b.name)
      })
      return categories.value
    } catch (error) {
      console.error('Failed to fetch categories:', error)
      return []
    } finally {
      loading.value = false
    }
  }

  async function createCategory(data) {
    loading.value = true
    try {
      const response = await createCategoryRequest(data)
      await fetchCategories()
      return response
    } finally {
      loading.value = false
    }
  }

  async function deleteCategory(id) {
    loading.value = true
    try {
      const response = await deleteCategoryRequest(id)
      await fetchCategories()
      return response
    } finally {
      loading.value = false
    }
  }

  return {
    categories,
    loading,
    fetchCategories,
    createCategory,
    deleteCategory,
  }
}
