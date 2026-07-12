import { ref } from 'vue'

import {
  createFundSource as createFundSourceRequest,
  deleteFundSource as deleteFundSourceRequest,
  getFundSources,
} from '../services/api'

export function useFundSources() {
  const sources = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function fetchSources() {
    loading.value = true
    error.value = null
    try {
      sources.value = await getFundSources()
      return sources.value
    } catch (err) {
      error.value = err.response?.data?.detail || 'Gagal mengambil data sumber uang'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function addSource(data) {
    loading.value = true
    error.value = null
    try {
      await createFundSourceRequest(data)
      await fetchSources()
    } catch (err) {
      error.value = err.response?.data?.detail || 'Gagal menambahkan sumber uang'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function removeSource(id) {
    loading.value = true
    error.value = null
    try {
      await deleteFundSourceRequest(id)
      await fetchSources()
    } catch (err) {
      error.value = err.response?.data?.detail || 'Gagal menghapus sumber uang'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    sources,
    loading,
    error,
    fetchSources,
    addSource,
    removeSource,
  }
}
