import { ref } from 'vue'

import {
  changePassword as changePasswordRequest,
  deleteAccount as deleteAccountRequest,
  getProfile,
  updateProfile,
} from '../services/api'

export function useSettings() {
  const profile = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const successMessage = ref(null)

  async function fetchProfile() {
    loading.value = true
    error.value = null
    try {
      profile.value = await getProfile()
      return profile.value
    } catch (err) {
      error.value = err.response?.data?.detail || 'Gagal mengambil data profil'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updatePassword(currentPassword, newPassword) {
    loading.value = true
    error.value = null
    successMessage.value = null
    try {
      const response = await changePasswordRequest({
        current_password: currentPassword,
        new_password: newPassword,
      })
      successMessage.value = response.message
    } catch (err) {
      error.value = err.response?.data?.detail || 'Gagal mengubah password'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateProfileDetails(fullName, nickname) {
    loading.value = true
    error.value = null
    successMessage.value = null
    try {
      const response = await updateProfile({
        full_name: fullName,
        nickname: nickname,
      })
      profile.value.full_name = response.full_name
      profile.value.nickname = response.nickname
      successMessage.value = response.message
      
      // Update local storage so that other parts of the app get updated
      localStorage.setItem('auth_full_name', response.full_name)
      localStorage.setItem('auth_nickname', response.nickname)
      
      return true
    } catch (err) {
      error.value = err.response?.data?.detail || 'Gagal mengubah profil'
      return false
    } finally {
      loading.value = false
    }
  }

  async function removeAccount(password) {
    loading.value = true
    error.value = null
    try {
      await deleteAccountRequest({ password })
    } catch (err) {
      error.value = err.response?.data?.detail || 'Gagal menghapus akun'
      throw err
    } finally {
      loading.value = false
    }
  }

  function clearMessages() {
    error.value = null
    successMessage.value = null
  }

  return {
    profile,
    loading,
    error,
    successMessage,
    fetchProfile,
    updatePassword,
    updateProfileDetails,
    removeAccount,
    clearMessages,
  }
}
