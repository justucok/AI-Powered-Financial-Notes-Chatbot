import { ref } from 'vue'

import { getNickname, getFullName, getGreeting, isLoggedIn as isLoggedInFn, login as loginApi, logout as logoutFn, register as registerApi, forgotPassword as forgotPasswordApi, resetPassword as resetPasswordApi } from '../services/auth'

/**
 * Composable for managing authentication state with nickname support.
 */
export function useAuth() {
  const isLoggedIn = ref(isLoggedInFn())
  const fullName = ref(getFullName())
  const nickname = ref(getNickname())
  const greeting = ref(getGreeting())
  const isLoading = ref(false)
  const error = ref(null)

  /**
   * Login using email and password.
   */
  async function login(email, password) {
    isLoading.value = true
    error.value = null

    try {
      const data = await loginApi(email, password)
      isLoggedIn.value = true
      fullName.value = data.full_name
      nickname.value = data.nickname
      greeting.value = data.preferred_greeting || 'Kak'
      return true
    } catch (err) {
      const detail = err.response?.data?.detail
      error.value = detail || 'Login gagal. Periksa email dan password Anda.'
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Register a new account.
   */
  async function register(payload) {
    isLoading.value = true
    error.value = null

    try {
      await registerApi(payload)
      // Auto-login using email
      return await login(payload.email, payload.password)
    } catch (err) {
      const detail = err.response?.data?.detail
      error.value = detail || 'Pendaftaran gagal. Silakan coba lagi.'
      return false
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Logout.
   */
  function logout() {
    logoutFn()
    isLoggedIn.value = false
    fullName.value = null
    nickname.value = null
    greeting.value = null
  }

  async function forgotPassword(email) {
    isLoading.value = true
    error.value = null
    try {
      const data = await forgotPasswordApi(email)
      return { success: true, message: data.message }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Gagal mengirim tautan.'
      return { success: false }
    } finally {
      isLoading.value = false
    }
  }

  async function resetPassword(token, new_password) {
    isLoading.value = true
    error.value = null
    try {
      const data = await resetPasswordApi(token, new_password)
      return { success: true, message: data.message }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Gagal mereset password.'
      return { success: false }
    } finally {
      isLoading.value = false
    }
  }

  return {
    isLoggedIn,
    fullName,
    nickname,
    greeting,
    isLoading,
    error,
    login,
    register,
    logout,
    forgotPassword,
    resetPassword,
  }
}
