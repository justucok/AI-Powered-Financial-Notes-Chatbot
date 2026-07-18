<script setup>
import { onMounted, ref } from 'vue'

import AppShell from './components/AppShell.vue'
import LoginPage from './components/LoginPage.vue'
import { getFullName, getNickname } from './services/auth'
import { useAuth } from './composables/useAuth'
import { useTransactions } from './composables/useTransactions'
import AddTransactionPage from './views/AddTransactionPage.vue'
import DashboardPage from './views/DashboardPage.vue'
import HistoryPage from './views/HistoryPage.vue'
import SettingsPage from './views/SettingsPage.vue'
import StatisticsPage from './views/StatisticsPage.vue'
import BudgetPage from './views/BudgetPage.vue'
import CategoryHistoryPage from './views/CategoryHistoryPage.vue'
import CategoryHistoryModal from './components/CategoryHistoryModal.vue'
import { useIdleTimer } from './composables/useIdleTimer'

const { isLoggedIn, fullName, nickname, logout } = useAuth()
const currentPage = ref('dashboard')
const selectedStatType = ref('expense')
const sessionExpiredMsg = ref('')
const {
  transactions,
  summary,
  loading,
  selectedMonth,
  fetchAll,
  createTransaction,
  deleteTransaction,
  updateTransaction,
  setMonth,
  lastUpdate,
  triggerUpdate,
} = useTransactions()

onMounted(() => {
  if (isLoggedIn.value) {
    fetchAll()
  }
})

function handleLoggedIn() {
  isLoggedIn.value = true
  fullName.value = getFullName()
  nickname.value = getNickname()
  fetchAll()
}

async function handleDataRefresh() {
  await fetchAll()
  triggerUpdate()
}

function handleLogout() {
  logout()
  currentPage.value = 'dashboard'
}

onMounted(() => {
  window.addEventListener('session-expired', () => {
    handleLogout()
    sessionExpiredMsg.value = 'Sesi Anda telah berakhir. Silakan login kembali.'
  })
})

useIdleTimer(() => {
  if (isLoggedIn.value) {
    handleLogout()
    sessionExpiredMsg.value = 'Sesi Anda telah berakhir karena tidak ada aktivitas selama 30 menit.'
  }
})

const showCategoryModal = ref(false)
const categoryFilter = ref({ category: '', month: '', transactions: [] })
const previousPage = ref('dashboard')

function handleShowCategoryHistory(payload, sourcePage) {
  categoryFilter.value = payload
  previousPage.value = sourcePage
  if (window.innerWidth >= 1024) {
    showCategoryModal.value = true
  } else {
    currentPage.value = 'category-history'
  }
}
</script>

<template>
  <!-- Auth gate: show login page when not authenticated -->
  <LoginPage v-if="!isLoggedIn" :expired-message="sessionExpiredMsg" @logged-in="handleLoggedIn" />

  <!-- Main layout shell: shown when authenticated -->
  <AppShell
    v-else
    :current-page="currentPage"
    :full-name="fullName || ''"
    :nickname="nickname || ''"
    :balance="summary.balance"
    @navigate="currentPage = $event"
    @logout="handleLogout"
    @transaction-added="handleDataRefresh"
  >
    <!-- View Switcher -->
    <DashboardPage
      v-if="currentPage === 'dashboard'"
      :balance="summary.balance"
      :income="summary.income"
      :expense="summary.expense"
      :nickname="nickname || ''"
      :refresh-key="lastUpdate"
      @refresh="handleDataRefresh"
      @show-category-history="handleShowCategoryHistory($event, 'dashboard')"
    />

    <AddTransactionPage
      v-else-if="currentPage === 'add'"
      :create-transaction="createTransaction"
      @transaction-added="handleDataRefresh"
    />

    <HistoryPage
      v-else-if="currentPage === 'history'"
      :transactions="transactions"
      :loading="loading"
      :selected-month="selectedMonth"
      @month-changed="setMonth"
      @delete-transaction="deleteTransaction"
      @edit-transaction="(data) => updateTransaction(data.id, data)"
    />

    <StatisticsPage
      v-else-if="currentPage === 'statistics'"
      :initial-type="selectedStatType"
      :refresh-key="lastUpdate"
      @show-category-history="handleShowCategoryHistory($event, 'statistics')"
    />

    <SettingsPage
      v-else-if="currentPage === 'settings'"
    />
    
    <BudgetPage
      v-else-if="currentPage === 'budget'"
    />

    <CategoryHistoryPage
      v-else-if="currentPage === 'category-history'"
      :category="categoryFilter.category"
      :month="categoryFilter.month"
      :transactions="categoryFilter.transactions"
      @back="currentPage = previousPage"
    />
  </AppShell>

  <CategoryHistoryModal
    :visible="showCategoryModal"
    :category="categoryFilter.category"
    :month="categoryFilter.month"
    :transactions="categoryFilter.transactions"
    @close="showCategoryModal = false"
  />
</template>
