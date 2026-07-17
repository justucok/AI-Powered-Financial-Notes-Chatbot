<script setup>
import { ref, onMounted } from 'vue'

const emit = defineEmits({
  'logged-in': () => true,
})

defineProps({
  expiredMessage: {
    type: String,
    default: ''
  }
})

// Tab state
const activeTab = ref('login')

// Form fields
const email = ref('')
const fullName = ref('')
const nickname = ref('')
const gender = ref('L')
const password = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)
const resetMessage = ref('')
const resetToken = ref('')

// Import composable inline to avoid prop drilling
import { useAuth } from '../composables/useAuth'

const { isLoading, error, login, register, forgotPassword, resetPassword } = useAuth()

onMounted(() => {
  const urlParams = new URLSearchParams(window.location.search)
  const token = urlParams.get('reset_token')
  if (token) {
    resetToken.value = token
    switchTab('reset')
    // Remove the query parameter from URL to make it clean
    window.history.replaceState({}, document.title, window.location.pathname)
  }
})

function switchTab(tab) {
  activeTab.value = tab
  error.value = null
  email.value = ''
  fullName.value = ''
  nickname.value = ''
  gender.value = 'L'
  password.value = ''
  confirmPassword.value = ''
  showPassword.value = false
  resetMessage.value = ''
}

function togglePassword() {
  showPassword.value = !showPassword.value
}

async function handleSubmit() {
  error.value = null

  if (activeTab.value === 'register') {
    if (password.value !== confirmPassword.value) {
      error.value = 'Password dan konfirmasi password tidak cocok.'
      return
    }
    const ok = await register({
      email: email.value,
      full_name: fullName.value,
      nickname: nickname.value,
      gender: gender.value,
      password: password.value,
    })
    if (ok) {
      emit('logged-in')
    }
  } else if (activeTab.value === 'login') {
    const ok = await login(email.value, password.value)
    if (ok) {
      emit('logged-in')
    }
  } else if (activeTab.value === 'forgot') {
    const res = await forgotPassword(email.value)
    if (res.success) {
      // Tunggu user klik dari email, jangan langsung ke reset tab kecuali testing
      resetMessage.value = res.message
      // Untuk testing lokal tanpa email, biarkan switchTab reset (opsional)
    } else {
      if (error.value && error.value.includes('belum terdaftar')) {
        switchTab('register')
        error.value = 'Email belum terdaftar. Silakan buat akun terlebih dahulu.'
      }
    }
  } else if (activeTab.value === 'reset') {
    if (password.value !== confirmPassword.value) {
      error.value = 'Password dan konfirmasi password tidak cocok.'
      return
    }
    if (!resetToken.value) {
      error.value = 'Token tidak ditemukan. Silakan request link reset ulang.'
      return
    }
    const res = await resetPassword(resetToken.value, password.value)
    if (res.success) {
      resetMessage.value = res.message
      // switch to login automatically or stay
      switchTab('login')
      // but preserve message
      resetMessage.value = res.message
    }
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-slate-50 px-4 py-8">
    <!-- Background decorative blobs -->
    <div class="pointer-events-none fixed inset-0 overflow-hidden">
      <div class="absolute -left-40 -top-40 h-96 w-96 rounded-full bg-sky-300/30 blur-3xl" />
      <div class="absolute -bottom-40 -right-40 h-96 w-96 rounded-full bg-emerald-300/30 blur-3xl" />
    </div>

    <div class="relative w-full max-w-md">
      <!-- Logo / Header -->
      <div class="mb-8 text-center">
        <div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-sky-600 text-3xl shadow-lg shadow-sky-600/30 text-white">
          💼
        </div>
        <h1 class="text-2xl font-bold tracking-tight text-slate-900">
          AI Financial Notes
        </h1>
        <p class="mt-1 text-sm text-slate-500">
          Asisten keuangan pribadi berbasis AI
        </p>
      </div>

      <!-- Card -->
      <div class="rounded-3xl border border-slate-200 bg-white p-8 shadow-xl shadow-slate-200/50 backdrop-blur-xl">
        <div v-if="expiredMessage"
             class="mb-4 p-3 rounded-xl bg-amber-50 border border-amber-200 text-amber-800 text-sm flex items-center gap-2">
          ⏰ {{ expiredMessage }}
        </div>

        <!-- Tab switcher (only show in login/register) -->
        <div v-if="activeTab === 'login' || activeTab === 'register'" class="mb-6 flex rounded-xl bg-slate-100 p-1">
          <button
            id="tab-login"
            type="button"
            :class="[
              'flex-1 rounded-lg py-2 text-sm font-medium transition-all duration-200',
              activeTab === 'login'
                ? 'bg-sky-600 text-white shadow-md'
                : 'text-slate-500 hover:text-slate-900',
            ]"
            @click="switchTab('login')"
          >
            Login
          </button>
          <button
            id="tab-register"
            type="button"
            :class="[
              'flex-1 rounded-lg py-2 text-sm font-medium transition-all duration-200',
              activeTab === 'register'
                ? 'bg-sky-600 text-white shadow-md'
                : 'text-slate-500 hover:text-slate-900',
            ]"
            @click="switchTab('register')"
          >
            Register
          </button>
        </div>

        <div v-if="activeTab === 'forgot' || activeTab === 'reset'" class="mb-6 text-center">
          <h2 class="text-xl font-bold text-slate-900">
            {{ activeTab === 'forgot' ? 'Lupa Password' : 'Atur Ulang Password' }}
          </h2>
          <p class="mt-2 text-sm text-slate-500">
            {{ activeTab === 'forgot' ? 'Masukkan email Anda untuk mengatur ulang password.' : 'Masukkan password baru Anda.' }}
          </p>
        </div>

        <!-- Success message -->
        <Transition
          enter-active-class="transition-all duration-200"
          enter-from-class="opacity-0 scale-95"
          enter-to-class="opacity-100 scale-100"
        >
          <div
            v-if="resetMessage"
            class="mb-4 flex items-start gap-2 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3"
          >
            <span class="mt-0.5 shrink-0 text-emerald-500">✓</span>
            <p class="text-sm text-emerald-600">{{ resetMessage }}</p>
          </div>
        </Transition>

        <!-- Form -->
        <form id="auth-form" class="space-y-4" @submit.prevent="handleSubmit">
          <!-- Email field (login, register, forgot) -->
          <div v-if="activeTab !== 'reset'">
            <label for="auth-email" class="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-slate-600">
              Email
            </label>
            <input
              id="auth-email"
              v-model="email"
              type="email"
              autocomplete="email"
              required
              placeholder="nama@email.com"
              class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-500/30 focus:bg-white"
            >
          </div>

          <!-- Registration specific fields -->
          <template v-if="activeTab === 'register'">
            <!-- Nama Lengkap -->
            <div>
              <label for="auth-fullname" class="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-slate-600">
                Nama Lengkap
              </label>
              <input
                id="auth-fullname"
                v-model="fullName"
                type="text"
                required
                minlength="1"
                placeholder="Masukkan nama lengkap Anda"
                class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-500/30 focus:bg-white"
              >
            </div>

            <div class="flex gap-4">
              <!-- Preferensi Nama Panggilan untuk Bot -->
              <div class="flex-1">
                <label for="auth-nickname" class="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-slate-600">
                  Nama Panggilan (untuk Bot AI)
                </label>
                <input
                  id="auth-nickname"
                  v-model="nickname"
                  type="text"
                  required
                  minlength="1"
                  placeholder="Contoh: Budi, Kak, Mba"
                  class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-500/30 focus:bg-white"
                >
              </div>

              <!-- Gender -->
              <div class="w-32">
                <label for="auth-gender" class="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-slate-600">
                  Gender
                </label>
                <select
                  id="auth-gender"
                  v-model="gender"
                  required
                  class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-500/30 focus:bg-white"
                >
                  <option value="L">Laki-laki</option>
                  <option value="P">Perempuan</option>
                </select>
              </div>
            </div>
          </template>

          <!-- Password field -->
          <div v-if="activeTab !== 'forgot'">
            <div class="flex items-center justify-between mb-1.5">
              <label for="auth-password" class="block text-xs font-semibold uppercase tracking-wider text-slate-600">
                {{ activeTab === 'reset' ? 'Password Baru' : 'Password' }}
              </label>
              <button
                v-if="activeTab === 'login'"
                type="button"
                @click="switchTab('forgot')"
                class="text-xs font-medium text-sky-600 hover:text-sky-700 underline"
              >
                Forgot Password?
              </button>
            </div>
            <div class="relative">
              <input
                id="auth-password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                autocomplete="current-password"
                required
                minlength="6"
                placeholder="Minimal 6 karakter"
                class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-500/30 focus:bg-white pr-10"
              >
              <button
                type="button"
                class="absolute inset-y-0 right-0 flex items-center pr-3 text-slate-400 hover:text-slate-700 focus:outline-none"
                @click="togglePassword"
              >
                <span v-if="showPassword">👁️‍🗨️</span>
                <span v-else>👁️</span>
              </button>
            </div>
          </div>

          <!-- Confirm password (register and reset only) -->
          <div v-if="activeTab === 'register' || activeTab === 'reset'">
            <label for="auth-confirm-password" class="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-slate-600">
              Konfirmasi Password
            </label>
            <div class="relative">
              <input
                id="auth-confirm-password"
                v-model="confirmPassword"
                :type="showPassword ? 'text' : 'password'"
                autocomplete="new-password"
                required
                minlength="6"
                placeholder="Ulangi password Anda"
                class="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-500/30 focus:bg-white pr-10"
              >
              <button
                type="button"
                class="absolute inset-y-0 right-0 flex items-center pr-3 text-slate-400 hover:text-slate-700 focus:outline-none"
                @click="togglePassword"
              >
                <span v-if="showPassword">👁️‍🗨️</span>
                <span v-else>👁️</span>
              </button>
            </div>
          </div>

          <!-- Error message -->
          <Transition
            enter-active-class="transition-all duration-200"
            enter-from-class="opacity-0 scale-95"
            enter-to-class="opacity-100 scale-100"
          >
            <div
              v-if="error"
              id="auth-error"
              class="flex items-start gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3"
            >
              <span class="mt-0.5 shrink-0 text-red-500">⚠</span>
              <p class="text-sm text-red-600">{{ error }}</p>
            </div>
          </Transition>

          <!-- Submit button -->
          <button
            id="auth-submit"
            type="submit"
            :disabled="isLoading"
            class="mt-2 w-full rounded-xl bg-sky-600 py-3 text-sm font-semibold text-white shadow-lg shadow-sky-600/30 transition hover:bg-sky-500 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <span v-if="isLoading" class="inline-flex items-center gap-2">
              <span class="loading-spinner" />
              Processing...
            </span>
            <span v-else>
              {{ 
                activeTab === 'login' ? 'Sign In' : 
                activeTab === 'register' ? 'Sign Up' :
                activeTab === 'forgot' ? 'Send Reset Link' : 'Save New Password'
              }}
            </span>
          </button>
        </form>

        <!-- Tab switcher link -->
        <p class="mt-5 text-center text-xs text-slate-500">
          <template v-if="activeTab === 'login'">
            Belum punya akun?
            <button type="button" class="font-medium text-sky-600 hover:text-sky-700 underline" @click="switchTab('register')">
              Register now
            </button>
          </template>
          <template v-else-if="activeTab === 'register'">
            Sudah punya akun?
            <button type="button" class="font-medium text-sky-600 hover:text-sky-700 underline" @click="switchTab('login')">
              Sign In here
            </button>
          </template>
          <template v-else>
            Ingat password Anda?
            <button type="button" class="font-medium text-sky-600 hover:text-sky-700 underline" @click="switchTab('login')">
              Back to Login
            </button>
          </template>
        </p>
      </div>

      <!-- Security note -->
      <p class="mt-4 text-center text-xs text-slate-500">
        🔒 Data keuangan Anda tersimpan di database personal yang terisolasi
      </p>
    </div>
  </div>
</template>

<style scoped>
.loading-spinner {
  display: inline-block;
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 9999px;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
