<script setup>
import { nextTick, ref, watch } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false,
  },
  file: {
    type: File,
    default: null,
  },
  isLoading: {
    type: Boolean,
    default: false,
  }
})

const emit = defineEmits(['close', 'confirm'])

const password = ref('')
const passwordInput = ref(null)
const showPassword = ref(false)

watch(
  () => props.show,
  (newVal) => {
    if (newVal) {
      password.value = ''
      showPassword.value = false
      nextTick(() => {
        if (passwordInput.value) {
          passwordInput.value.focus()
        }
      })
    }
  }
)

function handleSubmit() {
  if (!password.value.trim()) return
  emit('confirm', password.value)
}

function handleClose() {
  if (props.isLoading) return
  emit('close')
}
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="show"
        class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4 backdrop-blur-sm"
        @click.self="handleClose"
      >
        <div class="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl relative overflow-hidden">
          
          <div class="mb-5">
            <h3 class="text-xl font-bold text-slate-900">📄 Upload E-Statement</h3>
            <p class="mt-1 text-sm text-slate-500">
              Masukkan password untuk mengekstrak transaksi dari e-statement Anda.
            </p>
          </div>
          
          <div v-if="file" class="mb-5 flex items-center gap-3 rounded-xl bg-slate-50 p-3 ring-1 ring-slate-200">
            <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-red-100 text-red-600">
              PDF
            </div>
            <div class="min-w-0 flex-1">
              <p class="truncate text-sm font-medium text-slate-900">{{ file.name }}</p>
              <p class="text-xs text-slate-500">{{ (file.size / 1024 / 1024).toFixed(2) }} MB</p>
            </div>
          </div>

          <form @submit.prevent="handleSubmit">
            <div class="mb-6">
              <label class="mb-2 block text-sm font-medium text-slate-700">Password PDF</label>
              <div class="relative">
                <input
                  ref="passwordInput"
                  :type="showPassword ? 'text' : 'password'"
                  v-model="password"
                  required
                  placeholder="Biasanya 6 digit akhir no. rekening"
                  class="w-full rounded-xl border-slate-200 bg-slate-50 py-2.5 pl-4 pr-10 text-slate-900 outline-none transition focus:border-sky-500 focus:bg-white focus:ring-1 focus:ring-sky-500"
                  :disabled="isLoading"
                >
                <button
                  type="button"
                  class="absolute inset-y-0 right-0 flex items-center px-3 text-slate-400 hover:text-slate-600 focus:outline-none"
                  @click="showPassword = !showPassword"
                >
                  <span v-if="showPassword">🙈</span>
                  <span v-else>👁️</span>
                </button>
              </div>
            </div>

            <div class="flex gap-3">
              <button
                type="button"
                class="flex-1 rounded-xl bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 ring-1 ring-inset ring-slate-300 hover:bg-slate-50 disabled:opacity-50"
                @click="handleClose"
                :disabled="isLoading"
              >
                Batal
              </button>
              <button
                type="submit"
                class="flex-1 rounded-xl bg-sky-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-sky-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                :disabled="!password.trim() || isLoading"
              >
                <span v-if="isLoading" class="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></span>
                {{ isLoading ? 'Mengekstrak...' : 'Proses Sekarang' }}
              </button>
            </div>
          </form>
          
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: all 0.25s ease-out;
}

.modal-enter-from {
  opacity: 0;
  transform: scale(0.95);
}

.modal-leave-to {
  opacity: 0;
  transform: scale(0.95);
}
</style>
