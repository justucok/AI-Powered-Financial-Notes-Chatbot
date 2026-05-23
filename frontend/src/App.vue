<script setup>
import { onMounted } from 'vue'

import ChatBox from './components/ChatBox.vue'
import QuickAdd from './components/QuickAdd.vue'
import SummaryCards from './components/SummaryCards.vue'
import TransactionHistory from './components/TransactionHistory.vue'
import { useTransactions } from './composables/useTransactions'

const {
  transactions,
  summary,
  loading,
  selectedMonth,
  fetchAll,
  createTransaction,
  deleteTransaction,
  setMonth,
} = useTransactions()

onMounted(fetchAll)
</script>

<template>
  <main class="min-h-screen bg-gray-50">
    <header class="w-full bg-white shadow-sm">
      <div class="mx-auto max-w-4xl px-4 py-5">
        <h1 class="text-2xl font-semibold tracking-tight text-slate-900">
          💼 AI-Powered Financial Notes Chatbot
        </h1>
        <p class="mt-1 text-sm text-slate-600">
          Asisten keuangan pribadi untuk mencatat transaksi dan memantau ringkasan bulanan.
        </p>
      </div>
    </header>

    <div class="mx-auto max-w-4xl space-y-6 px-4 py-6">
      <SummaryCards
        :balance="summary.balance"
        :income="summary.income"
        :expense="summary.expense"
      />

      <ChatBox @transaction-added="fetchAll" />

      <QuickAdd
        :create-transaction="createTransaction"
        @transaction-added="fetchAll"
      />

      <TransactionHistory
        :transactions="transactions"
        :loading="loading"
        :selected-month="selectedMonth"
        @month-changed="setMonth"
        @delete-transaction="deleteTransaction"
      />
    </div>
  </main>
</template>
