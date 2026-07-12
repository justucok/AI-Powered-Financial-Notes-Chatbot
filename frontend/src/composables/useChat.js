import { computed, onBeforeUnmount, ref } from 'vue'

import { sendChat, sendChatImage } from '../services/api'

function isRecordedTransaction(data) {
  if (Array.isArray(data)) {
    return data.length > 0 && typeof data[0] === 'object' && 'id' in data[0]
  }
  return Boolean(data && typeof data === 'object' && 'id' in data && 'type' in data)
}

export function useChat(onTransactionAdded = () => {}, onRequiresFundSource = () => {}) {
  const messages = ref([
    {
      role: 'bot',
      text: 'Selamat datang. Saya siap membantu mencatat transaksi, menambah sumber uang, dan merangkum keuangan Anda.',
      hasTransaction: false,
      hasFundSource: false,
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

  function appendBotMessage(text, hasTransaction = false, hasFundSource = false) {
    messages.value.push({
      role: 'bot',
      text,
      hasTransaction,
      hasFundSource,
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

  async function sendTextMessage(message, fundSources = []) {
    const trimmedMessage = message.trim()
    if (!trimmedMessage || isLoading.value) {
      return
    }

    const requestHistory = history.value
    messages.value.push({
      role: 'user',
      text: trimmedMessage,
      hasTransaction: false,
      hasFundSource: false,
    })
    draftMessage.value = ''
    isLoading.value = true

    try {
      const response = await sendChat(trimmedMessage, requestHistory, fundSources)
      
      if (response.requires_fund_source) {
        onRequiresFundSource(response.pending_transactions, response.reply)
        return
      }

      const hasTransaction = isRecordedTransaction(response.data) && response.action !== 'add_fund_source_success'
      const hasFundSource = response.action === 'add_fund_source_success'
      const hasAdjustment = response.action === 'adjust_balance_success'

      appendBotMessage(
        response.reply || 'Permintaan Anda sudah saya proses.',
        hasTransaction,
        hasFundSource
      )

      if (response.action === 'update_greeting_success') {
        const newGreeting = response.data?.greeting
        if (newGreeting) {
          localStorage.setItem('auth_greeting', newGreeting)
        }
      }

      if (hasTransaction || hasFundSource || hasAdjustment) {
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
      hasFundSource: false,
    })
    draftMessage.value = ''
    isLoading.value = true

    try {
      const response = await sendChatImage(file, trimmedMessage)
      
      if (response.requires_fund_source) {
        onRequiresFundSource(response.pending_transactions, response.reply)
        return
      }

      const hasTransaction = isRecordedTransaction(response.data) && response.action !== 'add_fund_source_success'
      const hasFundSource = response.action === 'add_fund_source_success'

      appendBotMessage(
        response.reply || 'Gambar sudah saya proses.',
        hasTransaction,
        hasFundSource
      )

      if (hasTransaction || hasFundSource) {
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

  async function submitCurrentInput(fundSources = []) {
    if (selectedImageFile.value) {
      await sendImageMessage(selectedImageFile.value, draftMessage.value)
      return
    }

    await sendTextMessage(draftMessage.value, fundSources)
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
    appendBotMessage,
  }
}
