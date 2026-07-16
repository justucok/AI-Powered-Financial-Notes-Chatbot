<script setup>
import { ref, onMounted } from 'vue'
import ChatBubble from './ChatBubble.vue'
import HelpModal from './HelpModal.vue'

const showHelp = ref(false)

onMounted(() => {
  if (!localStorage.getItem('help_shown')) {
    showHelp.value = true
    localStorage.setItem('help_shown', 'true')
  }
})

defineProps({
  currentPage: {
    type: String,
    required: true,
  },
  fullName: {
    type: String,
    default: '',
  },
  nickname: {
    type: String,
    required: true,
  },
  balance: {
    type: Number,
    default: 0,
  }
})

const showMobileProfile = ref(false)

const emit = defineEmits({
  navigate: (page) => typeof page === 'string',
  logout: () => true,
  'transaction-added': () => true,
})

const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: '🏠' },
  { id: 'add', label: 'Tambah', icon: '➕' },
  { id: 'history', label: 'Riwayat', icon: '📋' },
  { id: 'statistics', label: 'Statistik', icon: '📊' },
  { id: 'settings', label: 'Pengaturan', icon: '⚙️' },
]
</script>

<template>
  <div class="min-h-screen bg-slate-50 pb-20 lg:pb-0 lg:pl-64">
    <!-- Desktop Sidebar -->
    <aside class="fixed inset-y-0 left-0 hidden w-64 flex-col border-r border-slate-200 bg-slate-900 text-slate-300 lg:flex">
      <div class="flex h-16 items-center gap-2 border-b border-slate-800 px-6">
        <span class="text-2xl">💼</span>
        <span class="text-lg font-bold tracking-tight text-white">FinanceBot</span>
      </div>

      <div class="flex items-center gap-3 px-6 py-6 border-b border-slate-800 relative">
        <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-sky-600 text-lg font-semibold text-white shadow-lg shadow-sky-600/30">
          {{ nickname ? nickname[0].toUpperCase() : '?' }}
        </span>
        <div class="min-w-0 flex-1">
          <p class="truncate text-sm font-semibold text-white">{{ fullName || nickname }}</p>
          <p class="truncate text-xs text-slate-500">Saldo: Rp {{ balance.toLocaleString('id-ID') }}</p>
        </div>
      </div>

      <nav class="flex-1 space-y-1 px-4 py-6">
        <button
          type="button"
          :class="['flex w-full items-center gap-3 rounded-2xl px-4 py-3.5 text-sm font-semibold transition duration-200', currentPage === 'dashboard' ? 'bg-sky-600 text-white shadow-lg shadow-sky-600/20' : 'hover:bg-slate-800 hover:text-white']"
          @click="emit('navigate', 'dashboard')"
        >
          <span class="text-lg">🏠</span> Dashboard
        </button>

        <button
          type="button"
          :class="['flex w-full items-center gap-3 rounded-2xl px-4 py-3.5 text-sm font-semibold transition duration-200', currentPage === 'add' ? 'bg-sky-600 text-white shadow-lg shadow-sky-600/20' : 'hover:bg-slate-800 hover:text-white']"
          @click="emit('navigate', 'add')"
        >
          <span class="text-lg">➕</span> Add
        </button>
        <button
          type="button"
          :class="['flex w-full items-center gap-3 rounded-2xl px-4 py-3.5 text-sm font-semibold transition duration-200', currentPage === 'budget' ? 'bg-sky-600 text-white shadow-lg shadow-sky-600/20' : 'hover:bg-slate-800 hover:text-white']"
          @click="emit('navigate', 'budget')"
        >
          <span class="text-lg">🎯</span> Budget
        </button>
        <button
          type="button"
          :class="['flex w-full items-center gap-3 rounded-2xl px-4 py-3.5 text-sm font-semibold transition duration-200', currentPage === 'history' ? 'bg-sky-600 text-white shadow-lg shadow-sky-600/20' : 'hover:bg-slate-800 hover:text-white']"
          @click="emit('navigate', 'history')"
        >
          <span class="text-lg">📋</span> History
        </button>
        <button
          type="button"
          :class="['flex w-full items-center gap-3 rounded-2xl px-4 py-3.5 text-sm font-semibold transition duration-200', currentPage === 'statistics' ? 'bg-sky-600 text-white shadow-lg shadow-sky-600/20' : 'hover:bg-slate-800 hover:text-white']"
          @click="emit('navigate', 'statistics')"
        >
          <span class="text-lg">📊</span> Statistik
        </button>
      </nav>

      <div class="p-4 border-t border-slate-800">
        <button
          type="button"
          class="flex w-full items-center gap-3 rounded-2xl px-4 py-3.5 text-sm font-semibold text-slate-400 transition hover:bg-slate-800 hover:text-white mb-2"
          @click="emit('navigate', 'settings')"
        >
          <span class="text-lg">⚙️</span> Settings
        </button>
        <button
          type="button"
          class="flex w-full items-center gap-3 rounded-2xl px-4 py-3.5 text-sm font-semibold text-sky-400 transition hover:bg-slate-800 hover:text-white mb-2"
          @click="showHelp = true"
        >
          <span class="text-lg">❓</span> Help
        </button>
        <button
          type="button"
          class="flex w-full items-center gap-3 rounded-2xl px-4 py-3.5 text-sm font-semibold text-rose-400 transition hover:bg-rose-500/10 hover:text-rose-300"
          @click="emit('logout')"
        >
          <span class="text-lg">↩</span> Logout
        </button>
      </div>
    </aside>

    <!-- Mobile Header -->
    <header class="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-slate-200 bg-white/80 px-4 shadow-sm backdrop-blur lg:hidden relative">
      <div class="flex items-center gap-2">
        <span class="text-2xl">💼</span>
        <span class="text-lg font-bold tracking-tight text-slate-900">FinanceBot</span>
      </div>

      <div class="flex items-center gap-3 relative">
        <button
          type="button"
          class="flex h-8 px-3 items-center justify-center rounded-lg bg-sky-100 text-sm font-semibold text-sky-700 focus:outline-none focus:ring-2 focus:ring-sky-500 truncate max-w-[120px]"
          @click="showMobileProfile = !showMobileProfile"
        >
          {{ nickname || '?' }}
        </button>
        
        <!-- Mobile Profile Dropdown -->
        <div v-if="showMobileProfile" class="absolute right-0 top-full mt-2 w-48 rounded-xl bg-white shadow-xl ring-1 ring-black ring-opacity-5 z-40 overflow-hidden">
          <div class="px-4 py-3 border-b border-gray-100">
            <p class="text-sm font-semibold text-gray-900 truncate">{{ fullName || nickname }}</p>
            <p class="text-xs text-gray-500 truncate mt-1">Saldo: Rp {{ balance.toLocaleString('id-ID') }}</p>
          </div>
          <button
            type="button"
            class="w-full text-left px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 transition-colors"
            @click="showMobileProfile = false; emit('navigate', 'settings')"
          >
            Settings
          </button>
          <button
            type="button"
            class="w-full text-left px-4 py-2 text-sm text-sky-600 hover:bg-sky-50 transition-colors"
            @click="showMobileProfile = false; showHelp = true"
          >
            Help
          </button>
          <button
            type="button"
            class="w-full text-left px-4 py-2 text-sm text-rose-600 hover:bg-rose-50 transition-colors"
            @click="showMobileProfile = false; emit('logout')"
          >
            Logout
          </button>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <div class="mx-auto max-w-[1400px]">
      <slot />
    </div>

    <!-- Mobile Bottom Navigation -->
    <nav class="fixed bottom-0 inset-x-0 z-50 flex h-16 items-center justify-around border-t border-slate-200 bg-white/95 px-2 sm:px-6 shadow-[0_-4px_16px_rgba(0,0,0,0.04)] backdrop-blur lg:hidden">
      <!-- Dashboard -->
      <button 
        type="button"
        :class="['flex flex-col items-center justify-center gap-1 w-14 transition duration-200', currentPage === 'dashboard' ? 'text-sky-600' : 'text-slate-400 hover:text-slate-500']"
        @click="emit('navigate', 'dashboard')"
      >
        <span class="text-[1.3rem] leading-none mb-0.5">🏠</span>
        <span class="text-[9px] sm:text-[10px] font-bold uppercase tracking-wide">Home</span>
      </button>

      <!-- Statistics -->
      <button 
        type="button"
        :class="['flex flex-col items-center justify-center gap-1 w-14 transition duration-200', currentPage === 'statistics' ? 'text-sky-600' : 'text-slate-400 hover:text-slate-500']"
        @click="emit('navigate', 'statistics')"
      >
        <span class="text-[1.3rem] leading-none mb-0.5">📊</span>
        <span class="text-[9px] sm:text-[10px] font-bold uppercase tracking-wide">Stats</span>
      </button>

      <!-- Center FAB for Add Transaction -->
      <div class="relative w-14 flex justify-center">
        <button 
          type="button"
          class="absolute -top-10 flex h-14 w-14 items-center justify-center rounded-full bg-sky-600 text-white shadow-lg shadow-sky-600/40 border-4 border-slate-50 transition active:scale-95"
          @click="emit('navigate', 'add')"
        >
          <span class="text-2xl">➕</span>
        </button>
      </div>

      <!-- Budget -->
      <button 
        type="button"
        :class="['flex flex-col items-center justify-center gap-1 w-14 transition duration-200', currentPage === 'budget' ? 'text-sky-600' : 'text-slate-400 hover:text-slate-500']"
        @click="emit('navigate', 'budget')"
      >
        <span class="text-[1.3rem] leading-none mb-0.5">🎯</span>
        <span class="text-[9px] sm:text-[10px] font-bold uppercase tracking-wide">Budget</span>
      </button>

      <!-- History -->
      <button 
        type="button"
        :class="['flex flex-col items-center justify-center gap-1 w-14 transition duration-200', currentPage === 'history' ? 'text-sky-600' : 'text-slate-400 hover:text-slate-500']"
        @click="emit('navigate', 'history')"
      >
        <span class="text-[1.3rem] leading-none mb-0.5">📋</span>
        <span class="text-[9px] sm:text-[10px] font-bold uppercase tracking-wide">History</span>
      </button>
    </nav>

    <!-- Global Chat Bubble (Desktop Only) -->
    <ChatBubble class="hidden lg:block" @transaction-added="emit('transaction-added')" />

    <HelpModal :show="showHelp" @close="showHelp = false" />
  </div>
</template>
