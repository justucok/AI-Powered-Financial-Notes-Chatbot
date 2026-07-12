<script setup>
import { onMounted, ref } from 'vue'
import ChatBox from '../components/ChatBox.vue'
import SummaryCards from '../components/SummaryCards.vue'
import FundSourcePickerModal from '../components/FundSourcePickerModal.vue'
import { useFundSources } from '../composables/useFundSources'
import { confirmTransactions as confirmTransactionsApi } from '../services/api'
import { useBudget } from '../composables/useBudget'
import { formatRupiah } from '../utils/formatters'

defineProps({
  balance: {
    type: Number,
    required: true,
  },
  income: {
    type: Number,
    required: true,
  },
  expense: {
    type: Number,
    required: true,
  },
  nickname: {
    type: String,
    required: true,
  },
})

const emit = defineEmits({
  'refresh': () => true,
  'navigate-stats': (type) => typeof type === 'string',
})

const { sources: fundSources, fetchSources } = useFundSources()
const { summary: budgetSummary, fetchBudgetSummary } = useBudget()

const showFundSourceModal = ref(false)
const currentPendingTransactions = ref([])
const isConfirming = ref(false)

onMounted(async () => {
  await fetchSources()
  const today = new Date()
  const currentMonthKey = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`
  await fetchBudgetSummary(currentMonthKey)
})

async function handleTransactionAdded() {
  await fetchSources()
  emit('refresh')
  const today = new Date()
  const currentMonthKey = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`
  await fetchBudgetSummary(currentMonthKey)
}

function handleRequiresFundSource(pending, reply) {
  currentPendingTransactions.value = pending
  showFundSourceModal.value = true
}

async function handleConfirmTransactions(confirmedTransactions) {
  isConfirming.value = true
  try {
    await confirmTransactionsApi({ transactions: confirmedTransactions })
    await handleTransactionAdded()
    showFundSourceModal.value = false
    currentPendingTransactions.value = []
  } catch (error) {
    console.error('Failed to confirm transactions:', error)
    alert('Gagal menyimpan transaksi: ' + (error.response?.data?.detail || error.message))
  } finally {
    isConfirming.value = false
  }
}
</script>

<template>
  <div class="space-y-6 px-4 py-6 md:p-8">
    <header class="flex flex-col gap-1">
      <p class="text-xs font-semibold uppercase tracking-[0.24em] text-sky-600">Ringkasan Finansial</p>
      <h1 class="text-2xl font-bold tracking-tight text-slate-900">
        Halo, {{ nickname || 'Pengguna' }}!
      </h1>
      <p class="text-sm text-slate-500">
        Berikut ringkasan posisi keuangan dan asisten chat Anda hari ini.
      </p>
    </header>

    <!-- Summary Cards -->
    <SummaryCards
      :balance="balance"
      :income="income"
      :expense="expense"
      @card-click="emit('navigate-stats', $event)"
    />

    <!-- Budget Summary Widget (only show if total_budget > 0) -->
    <div 
      v-if="budgetSummary.total_budget > 0" 
      class="bg-white rounded-3xl p-5 border border-slate-100 shadow-[0_8px_30px_rgb(0,0,0,0.03)] flex flex-col md:flex-row md:items-center justify-between gap-4"
    >
      <div class="flex items-center space-x-3">
        <span class="text-3xl">🎯</span>
        <div>
          <h4 class="font-bold text-slate-800 text-sm">Budget Bulan Ini</h4>
          <div class="flex items-baseline space-x-1.5 mt-0.5">
            <span class="text-lg font-extrabold text-slate-900">
              Rp {{ formatRupiah(budgetSummary.total_remaining) }}
            </span>
            <span class="text-xs text-slate-500 font-medium">sisa budget</span>
          </div>
        </div>
      </div>
      
      <div class="flex-1 max-w-md">
        <div class="relative h-2.5 w-full overflow-hidden rounded-full bg-slate-100">
          <div
            class="h-full rounded-full transition-all duration-500 ease-out"
            :class="budgetSummary.total_percent > 100 ? 'bg-rose-500' : (budgetSummary.total_percent > 80 ? 'bg-amber-400' : 'bg-emerald-500')"
            :style="{ width: `${Math.min(budgetSummary.total_percent, 100)}%` }"
          ></div>
        </div>
        <div class="flex justify-between text-[10px] text-slate-500 font-bold uppercase tracking-wider mt-1 px-0.5">
          <span>Terpakai: Rp {{ formatRupiah(budgetSummary.total_actual) }} ({{ budgetSummary.total_percent }}%)</span>
          <span v-if="budgetSummary.total_percent > 100" class="text-rose-500 animate-pulse">OVER BUDGET</span>
        </div>
      </div>
    </div>

    <!-- AI Chatbot -->
    <ChatBox 
      :fundSources="fundSources"
      @transaction-added="handleTransactionAdded" 
      @requires-fund-source="handleRequiresFundSource" 
    />

    <!-- Fund Source Picker Modal -->
    <FundSourcePickerModal
      :show="showFundSourceModal"
      :pending-transactions="currentPendingTransactions"
      :fund-sources="fundSources"
      :is-loading="isConfirming"
      @close="showFundSourceModal = false; currentPendingTransactions = []"
      @confirm="handleConfirmTransactions"
    />
  </div>
</template>
