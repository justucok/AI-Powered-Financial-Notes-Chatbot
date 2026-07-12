<script setup>
import { nextTick, ref, watchEffect } from 'vue'

import { useChat } from '../composables/useChat'

const emit = defineEmits({
  'transaction-added': (payload) => payload && typeof payload === 'object',
  'requires-fund-source': (pending, reply) => true,
})

const props = defineProps({
  fundSources: {
    type: Array,
    default: () => [],
  }
})

const fileInputRef = ref(null)
const messagesContainerRef = ref(null)

const {
  messages,
  isLoading,
  imagePreview,
  draftMessage,
  selectedImageFile,
  selectImage,
  clearImage,
  submitCurrentInput,
} = useChat(
  (transaction) => {
    emit('transaction-added', transaction)
  },
  (pending, reply) => {
    emit('requires-fund-source', pending, reply)
  }
)

async function handleSubmit() {
  await submitCurrentInput(props.fundSources)

  if (!selectedImageFile.value && fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

watchEffect(() => {
  messages.value.length
  isLoading.value

  void nextTick().then(() => {
    if (messagesContainerRef.value) {
      messagesContainerRef.value.scrollTop = messagesContainerRef.value.scrollHeight
    }
  })
})

function handleFileChange(event) {
  const [file] = event.target.files || []
  selectImage(file || null)
}

function openFilePicker() {
  fileInputRef.value?.click()
}

function handleClearImage() {
  clearImage()

  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

</script>

<template>
  <section class="rounded-[2rem] border border-white/70 bg-white/80 p-5 shadow-[0_24px_80px_rgba(15,23,42,0.08)] backdrop-blur sm:p-6">
    <div class="mb-4 flex items-center justify-between">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.28em] text-sky-600">
          AI Chat Assistant
        </p>
        <h2 class="mt-1 text-xl font-semibold text-slate-900">
          Catat transaksi lewat chat atau foto nota
        </h2>
      </div>
    </div>

    <div
      ref="messagesContainerRef"
      class="h-[26rem] space-y-4 overflow-y-auto rounded-[1.5rem] bg-slate-50/80 p-4"
    >
      <article
        v-for="(message, index) in messages"
        :key="`${message.role}-${index}`"
        :class="[
          'flex',
          message.role === 'user' ? 'justify-end' : 'justify-start',
        ]"
      >
        <div class="max-w-[85%]">
          <p
            v-if="message.role === 'bot'"
            class="mb-1 px-1 text-xs font-semibold uppercase tracking-[0.22em] text-slate-500"
          >
            Asisten Keuangan
          </p>
          <div
            :class="[
              'rounded-[1.4rem] px-4 py-3 text-sm leading-6 shadow-sm',
              message.role === 'user'
                ? 'rounded-br-md bg-sky-600 text-white'
                : 'rounded-bl-md bg-white text-slate-700 ring-1 ring-slate-200',
            ]"
          >
            <p class="whitespace-pre-wrap">
              {{ message.text }}
            </p>
          </div>
          <span
            v-if="message.hasTransaction"
            class="mt-2 inline-flex rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-700"
          >
            ✅ Transaksi Dicatat
          </span>
          <span
            v-if="message.hasFundSource"
            class="mt-2 ml-2 inline-flex rounded-full bg-sky-100 px-3 py-1 text-xs font-semibold text-sky-700"
          >
            💳 Sumber Uang Ditambahkan
          </span>
        </div>
      </article>

      <div v-if="isLoading" class="flex justify-start">
        <div class="rounded-[1.25rem] rounded-bl-md bg-white px-4 py-3 ring-1 ring-slate-200 shadow-sm">
          <p class="mb-2 text-xs font-semibold uppercase tracking-[0.22em] text-slate-500">
            Asisten Keuangan
          </p>
          <div class="loading-dots">
            <span />
            <span />
            <span />
          </div>
        </div>
      </div>
    </div>

    <div
      v-if="imagePreview"
      class="mt-4 flex items-start gap-3 rounded-[1.25rem] border border-sky-100 bg-sky-50/70 p-3"
    >
      <img
        :src="imagePreview"
        alt="Preview nota"
        class="h-16 w-16 rounded-xl object-cover ring-1 ring-sky-100"
      >
      <div class="min-w-0 flex-1">
        <p class="text-sm font-medium text-slate-800">
          Gambar siap dikirim
        </p>
        <p class="truncate text-xs text-slate-500">
          {{ selectedImageFile?.name }}
        </p>
      </div>
      <button
        type="button"
        class="inline-flex h-8 w-8 items-center justify-center rounded-full bg-white text-slate-500 ring-1 ring-slate-200 transition hover:bg-slate-100"
        @click="handleClearImage"
      >
        X
      </button>
    </div>

    <form class="mt-4 flex items-end gap-3" @submit.prevent="handleSubmit">
      <input
        ref="fileInputRef"
        type="file"
        accept="image/*"
        class="hidden"
        @change="handleFileChange"
      >
      <button
        type="button"
        class="inline-flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-slate-900 text-lg text-white transition hover:bg-slate-800"
        @click="openFilePicker"
      >
        📎
      </button>
      <textarea
        v-model="draftMessage"
        rows="1"
        placeholder="Tulis transaksi atau pertanyaan keuangan..."
        class="min-h-12 max-h-32 flex-1 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-sky-400 focus:ring-4 focus:ring-sky-100 resize-none"
        @keydown.enter.exact.prevent="handleSubmit"
      />
      <button
        type="submit"
        :disabled="isLoading"
        class="inline-flex h-12 shrink-0 items-center justify-center rounded-2xl bg-sky-600 px-5 text-sm font-semibold text-white transition hover:bg-sky-500 disabled:cursor-not-allowed disabled:bg-sky-300"
      >
        Kirim
      </button>
    </form>
  </section>
</template>

<style scoped>
.loading-dots {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.loading-dots span {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 9999px;
  background: #64748b;
  animation: bounce 1s infinite ease-in-out;
}

.loading-dots span:nth-child(2) {
  animation-delay: 0.15s;
}

.loading-dots span:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes bounce {
  0%,
  80%,
  100% {
    transform: translateY(0);
    opacity: 0.5;
  }

  40% {
    transform: translateY(-0.25rem);
    opacity: 1;
  }
}
</style>
