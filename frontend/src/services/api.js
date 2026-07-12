import axios from 'axios'

import { getToken, removeAuthData } from './auth'

const apiClient = axios.create({
  baseURL: '/api',
})

// ---------------------------------------------------------------------------
// Request interceptor — attach JWT token to every request
// ---------------------------------------------------------------------------
apiClient.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ---------------------------------------------------------------------------
// Response interceptor — handle errors globally
// ---------------------------------------------------------------------------
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API request failed:', error)

    // If the server returns 401, the token is expired or invalid — force logout
    if (error.response?.status === 401) {
      removeAuthData()
      window.location.reload()
    }

    return Promise.reject(error)
  }
)

// ---------------------------------------------------------------------------
// Transaction API calls
// ---------------------------------------------------------------------------

export async function getTransactions(month) {
  const response = await apiClient.get('/v1/transactions', {
    params: month ? { month } : undefined,
  })
  return response.data
}

export async function createTransaction(data) {
  const response = await apiClient.post('/v1/transactions', data)
  return response.data
}

export async function deleteTransaction(id) {
  const response = await apiClient.delete(`/v1/transactions/${id}`)
  return response.data
}

export async function getSummary(month) {
  const response = await apiClient.get('/v1/summary', {
    params: month ? { month } : undefined,
  })
  return response.data
}

// ---------------------------------------------------------------------------
// Chat API calls
// ---------------------------------------------------------------------------

export async function sendChat(message, history, fundSources = []) {
  const response = await apiClient.post('/v1/chat', {
    message,
    history,
    fund_sources: fundSources,
  })
  return response.data
}

export async function sendChatImage(file, message = '', fundSources = []) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('message', message)
  formData.append('fund_sources', JSON.stringify(fundSources))

  const response = await apiClient.post('/v1/chat/image', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}


// --- Fund Sources ---
export async function getFundSources() {
  const response = await apiClient.get('/v1/fund-sources/')
  return response.data
}

export async function createFundSource(data) {
  const response = await apiClient.post('/v1/fund-sources/', data)
  return response.data
}

export async function deleteFundSource(id) {
  const response = await apiClient.delete(`/v1/fund-sources/${id}`)
  return response.data
}

// --- Categories ---
export async function getCategories() {
  const response = await apiClient.get('/v1/categories')
  return response.data
}

export async function createCategory(data) {
  const response = await apiClient.post('/v1/categories', data)
  return response.data
}

export async function deleteCategory(id) {
  const response = await apiClient.delete(`/v1/categories/${id}`)
  return response.data
}

// --- Transactions (confirm pending from chat) ---
export async function confirmTransactions(data) {
  const response = await apiClient.post('/v1/transactions/confirm', data)
  return response.data
}

// --- Settings & Auth ---
export async function getProfile() {
  const response = await apiClient.get('/v1/auth/profile')
  return response.data
}

export async function updateProfile(data) {
  const response = await apiClient.put('/v1/auth/profile', data)
  return response.data
}

export async function changePassword(data) {
  const response = await apiClient.put('/v1/auth/password', data)
  return response.data
}

export async function deleteAccount(data) {
  const response = await apiClient.delete('/v1/auth/account', { data })
  return response.data
}

// --- Budgets ---
export async function getBudgetSummary(month) {
  const response = await apiClient.get('/v1/budgets/summary', {
    params: { month },
  })
  return response.data
}

export async function setBudget(data) {
  const response = await apiClient.post('/v1/budgets', data)
  return response.data
}

export async function setCategoryBudget(data) {
  const response = await apiClient.post('/v1/budgets/categories', data)
  return response.data
}

