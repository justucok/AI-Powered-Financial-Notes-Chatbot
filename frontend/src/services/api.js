import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api',
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API request failed:', error)
    return Promise.reject(error)
  }
)

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

export async function sendChat(message, history) {
  const response = await apiClient.post('/v1/chat', {
    message,
    history,
  })
  return response.data
}

export async function sendChatImage(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await apiClient.post('/v1/chat/image', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}
