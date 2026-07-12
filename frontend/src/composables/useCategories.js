import { ref } from 'vue'

import { createCategory as createCategoryRequest, deleteCategory as deleteCategoryRequest, getCategories } from '../services/api'

export function useCategories() {
  const categories = ref([])
  const loading = ref(false)

  async function fetchCategories() {
    loading.value = true
    try {
      categories.value = await getCategories()
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
