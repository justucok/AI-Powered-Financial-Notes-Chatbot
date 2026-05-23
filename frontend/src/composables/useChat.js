import { computed, onBeforeUnmount, ref } from 'vue'

import { sendChat, sendChatImage } from '../services/api'

function isRecordedTransaction(data) {
  return Boolean(data && typeof data === 'object' && 'id' in data && 'type' in data)
}

export function useChat(onTransactionAdded = () => {}) {
  const messages = ref([
    {
      role: 'bot',
      text: 'Selamat datang. Saya siap membantu mencatat transaksi dan merangkum keuangan Anda.',
      hasTransaction: false,
    },
  ])
  const isLoading = ref(false)
  const imagePreview = ref(null)
  const selectedImageFile = ref(null)
  const draftMessage = ref('')

  const history = computed(() =>
    messages.value.slice(-10).map((message) => ({
      role: message.role === 'user' ? 'user' : 'assistant',
      content: message.text,
    }))
  )

  function revokePreviewUrl() {
    if (imagePreview.value) {
      URL.revokeObjectURL(imagePreview.value)
    }
  }

  function appendBotMessage(text, hasTransaction = false) {
    messages.value.push({
      role: 'bot',
      text,
      hasTransaction,
    })
  }

  function clearImage() {
    revokePreviewUrl()
    imagePreview.value = null
    selectedImageFile.value = null
  }

  function selectImage(file) {
    clearImage()

    if (!file) {
      return
    }

    selectedImageFile.value = file
    imagePreview.value = URL.createObjectURL(file)
  }

  async function sendTextMessage(message) {
    const trimmedMessage = message.trim()
    if (!trimmedMessage || isLoading.value) {
      return
    }

    const requestHistory = history.value
    messages.value.push({
      role: 'user',
      text: trimmedMessage,
      hasTransaction: false,
    })
    draftMessage.value = ''
    isLoading.value = true

    try {
      const response = await sendChat(trimmedMessage, requestHistory)
      const hasTransaction = isRecordedTransaction(response.data)

      appendBotMessage(
        response.reply || 'Permintaan Anda sudah saya proses.',
        hasTransaction
      )

      if (hasTransaction) {
        onTransactionAdded(response.data)
      }
    } catch (error) {
      console.error('Failed to send text message:', error)
      appendBotMessage('Maaf, pesan Anda belum dapat diproses saat ini.')
    } finally {
      isLoading.value = false
    }
  }

  async function sendImageMessage(file, message = '') {
    if (!file || isLoading.value) {
      return
    }

    const trimmedMessage = message.trim()
    const messageText = trimmedMessage
      ? `${trimmedMessage}\n\n[Melampirkan gambar: ${file.name}]`
      : `Mengirim gambar: ${file.name}`

    messages.value.push({
      role: 'user',
      text: messageText,
      hasTransaction: false,
    })
    draftMessage.value = ''
    isLoading.value = true

    try {
      const response = await sendChatImage(file, trimmedMessage)
      const hasTransaction = isRecordedTransaction(response.data)

      appendBotMessage(
        response.reply || 'Gambar sudah saya proses.',
        hasTransaction
      )

      if (hasTransaction) {
        onTransactionAdded(response.data)
      }
    } catch (error) {
      console.error('Failed to send image message:', error)
      appendBotMessage('Maaf, gambar belum dapat diproses saat ini.')
    } finally {
      isLoading.value = false
      clearImage()
    }
  }

  async function submitCurrentInput() {
    if (selectedImageFile.value) {
      await sendImageMessage(selectedImageFile.value, draftMessage.value)
      return
    }

    await sendTextMessage(draftMessage.value)
  }

  onBeforeUnmount(() => {
    clearImage()
  })

  return {
    messages,
    history,
    isLoading,
    imagePreview,
    draftMessage,
    selectedImageFile,
    sendTextMessage,
    sendImageMessage,
    selectImage,
    clearImage,
    submitCurrentInput,
  }
}
