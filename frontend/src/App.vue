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

const { isLoggedIn, fullName, nickname, logout } = useAuth()
const currentPage = ref('dashboard')
const selectedStatType = ref('expense')
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

function handleLogout() {
  logout()
  currentPage.value = 'dashboard'
}
</script>

<template>
  <!-- Auth gate: show login page when not authenticated -->
  <LoginPage v-if="!isLoggedIn" @logged-in="handleLoggedIn" />

  <!-- Main layout shell: shown when authenticated -->
  <AppShell
    v-else
    :current-page="currentPage"
    :full-name="fullName || ''"
    :nickname="nickname || ''"
    :balance="summary.balance"
    @navigate="currentPage = $event"
    @logout="handleLogout"
    @transaction-added="fetchAll"
  >
    <!-- View Switcher -->
    <DashboardPage
      v-if="currentPage === 'dashboard'"
      :balance="summary.balance"
      :income="summary.income"
      :expense="summary.expense"
      :nickname="nickname || ''"
      @refresh="fetchAll"
    />

    <AddTransactionPage
      v-else-if="currentPage === 'add'"
      :create-transaction="createTransaction"
      @transaction-added="fetchAll"
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
    />


    <SettingsPage
      v-else-if="currentPage === 'settings'"
    />
    
    <BudgetPage
      v-else-if="currentPage === 'budget'"
    />
  </AppShell>
</template>
