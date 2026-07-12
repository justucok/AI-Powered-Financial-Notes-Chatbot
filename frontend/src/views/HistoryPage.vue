<script setup>
import { computed, ref, onMounted } from 'vue'

import { formatDate, formatMonth, formatRupiah } from '../utils/formatters'
import { useFundSources } from '../composables/useFundSources'
import EditTransactionModal from '../components/EditTransactionModal.vue'
import DeleteConfirmationModal from '../components/DeleteConfirmationModal.vue'

const props = defineProps({
  transactions: {
    type: Array,
    required: true,
  },
  loading: {
    type: Boolean,
    required: true,
  },
  selectedMonth: {
    type: String,
    required: true,
  },
})

const emit = defineEmits({
  'month-changed': (month) => typeof month === 'string',
  'delete-transaction': (id) => Number.isInteger(id),
  'edit-transaction': (payload) => payload && typeof payload === 'object',
})

const { sources: fundSources, fetchSources } = useFundSources()

onMounted(async () => {
  await fetchSources()
})

const selectedFundSourceId = ref(null)

function formatMonthKey(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  return `${year}-${month}`
}

const monthOptions = computed(() => {
  const options = []
  const baseDate = new Date()
  baseDate.setDate(1)

  for (let offset = 0; offset < 7; offset += 1) {
    const date = new Date(baseDate.getFullYear(), baseDate.getMonth() - offset, 1)
    options.push(formatMonthKey(date))
  }

  return options
})

const filteredTransactions = computed(() => {
  if (selectedFundSourceId.value) {
    return props.transactions.filter(tx => tx.fund_source_id === selectedFundSourceId.value)
  }
  return props.transactions
})

// Calculate monthly stats based on current month's transactions
const monthlyStats = computed(() => {
  let income = 0
  let expense = 0
  filteredTransactions.value.forEach((tx) => {
    if (tx.type === 'income') {
      income += tx.amount
    } else {
      expense += tx.amount
    }
  })
  return {
    income,
    expense,
    balance: income - expense,
  }
})

function handleMonthSelect(month) {
  emit('month-changed', month)
}

const showDeleteModal = ref(false)
const transactionToDeleteId = ref(null)

const showEditModal = ref(false)
const transactionToEdit = ref(null)

function confirmDelete(id) {
  transactionToDeleteId.value = id
  showDeleteModal.value = true
}

function executeDelete() {
  if (transactionToDeleteId.value !== null) {
    emit('delete-transaction', transactionToDeleteId.value)
    showDeleteModal.value = false
    transactionToDeleteId.value = null
  }
}

function openEdit(tx) {
  transactionToEdit.value = { ...tx }
  showEditModal.value = true
}

function executeEdit(updatedData) {
  emit('edit-transaction', updatedData)
  showEditModal.value = false
  transactionToEdit.value = null
}

function getFundSourceDisplay(id) {
  if (!id) return '-'
  const source = fundSources.value.find(s => s.id === id)
  return source ? `${source.icon || '💰'} ${source.name}` : '-'
}
</script>

<template>
  <div class="px-4 py-6 md:p-8 space-y-6">
    <header class="flex flex-col gap-1">
      <p class="text-xs font-semibold uppercase tracking-[0.28em] text-sky-600">Arsip Transaksi</p>
      <h1 class="text-2xl font-bold tracking-tight text-slate-900">Riwayat Transaksi</h1>
      <p class="text-sm text-slate-500">Lihat, cari, dan kelola semua catatan finansial Anda.</p>
    </header>

    <!-- Fund Source Balances Widget -->
    <div v-if="fundSources.length > 0" class="mb-4">
      <p class="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Filter Berdasarkan Sumber Uang</p>
      <div class="flex gap-4 overflow-x-auto pb-4 snap-x hide-scrollbar">
        <div
          v-for="source in fundSources"
          :key="source.id"
          @click="selectedFundSourceId = selectedFundSourceId === source.id ? null : source.id"
          class="snap-start shrink-0 w-[140px] p-3 rounded-2xl border cursor-pointer flex flex-col items-start gap-2 transition-all duration-200"
          :class="selectedFundSourceId === source.id ? 'border-sky-500 bg-sky-50 ring-2 ring-sky-500/20' : 'border-emerald-100 bg-gradient-to-br from-emerald-50/50 to-emerald-100/30 hover:border-emerald-300'"
        >
          <div class="flex items-center gap-2">
            <span class="text-xl">{{ source.icon || '💰' }}</span>
            <span class="text-xs font-semibold text-slate-700 truncate w-full">{{ source.name }}</span>
          </div>
          <p class="text-sm font-bold truncate w-full" :class="selectedFundSourceId === source.id ? 'text-sky-700' : 'text-emerald-700'">{{ formatRupiah(source.balance) }}</p>
        </div>
      </div>
    </div>

    <!-- Monthly Stats Widget (Mini Summary for Filtered Month) -->
    <div class="grid grid-cols-3 gap-2.5 rounded-2xl bg-white border border-slate-200 p-3.5 shadow-sm">
      <div class="text-center border-r border-slate-100">
        <p class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Pemasukan</p>
        <p class="mt-1 text-xs font-bold text-emerald-600 truncate">{{ formatRupiah(monthlyStats.income) }}</p>
      </div>
      <div class="text-center border-r border-slate-100">
        <p class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Pengeluaran</p>
        <p class="mt-1 text-xs font-bold text-rose-600 truncate">{{ formatRupiah(monthlyStats.expense) }}</p>
      </div>
      <div class="text-center">
        <p class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Selisih</p>
        <p
          class="mt-1 text-xs font-bold truncate"
          :class="monthlyStats.balance >= 0 ? 'text-sky-600' : 'text-slate-800'"
        >
          {{ formatRupiah(monthlyStats.balance) }}
        </p>
      </div>
    </div>

    <!-- Month Filter (Horizontal Scrollbar on Mobile, Clean Pills on Desktop) -->
    <div class="space-y-2">
      <label class="text-xs font-semibold uppercase tracking-wider text-slate-400">Pilih Bulan</label>
      <div class="no-scrollbar -mx-4 flex gap-2 overflow-x-auto px-4 pb-2">
        <button
          v-for="month in monthOptions"
          :key="month"
          type="button"
          :class="[
            'h-10 shrink-0 rounded-full px-4 text-xs font-semibold tracking-wide transition border',
            selectedMonth === month
              ? 'bg-slate-900 border-slate-900 text-white shadow-sm'
              : 'bg-white border-slate-200 text-slate-600 hover:border-slate-300',
          ]"
          @click="handleMonthSelect(month)"
        >
          {{ formatMonth(month) }}
        </button>
      </div>
    </div>

    <!-- Transactions List Container -->
    <div class="rounded-3xl border border-white/70 bg-white/80 p-5 shadow-[0_24px_80px_rgba(15,23,42,0.06)] backdrop-blur sm:p-6">
      <div v-if="loading" class="space-y-4 py-4">
        <!-- Skeleton Loaders -->
        <div v-for="index in 4" :key="`skeleton-${index}`" class="flex items-center justify-between border-b border-slate-100 pb-4">
          <div class="space-y-2">
            <div class="h-4 w-28 animate-pulse rounded bg-slate-200" />
            <div class="h-3 w-40 animate-pulse rounded bg-slate-200" />
          </div>
          <div class="h-4 w-20 animate-pulse rounded bg-slate-200" />
        </div>
      </div>

      <div v-else-if="filteredTransactions.length === 0" class="py-12 text-center">
        <span class="text-3xl">📭</span>
        <h3 class="mt-3 text-sm font-semibold text-slate-700">Tidak Ada Transaksi</h3>
        <p class="mt-1 text-xs text-slate-500">Belum ada transaksi terdaftar untuk bulan {{ formatMonth(selectedMonth) }}.</p>
      </div>

      <!-- Mobile List View (hidden on Desktop/Tablet md+) -->
      <div v-else class="block md:hidden space-y-3.5">
        <div
          v-for="tx in filteredTransactions"
          :key="tx.id"
          class="flex items-center justify-between rounded-2xl border border-slate-100 bg-white p-4 shadow-sm"
        >
          <div class="space-y-1 min-w-0">
            <div class="flex items-center gap-2">
              <span
                :class="[
                  'inline-block h-2 w-2 rounded-full',
                  tx.type === 'income' ? 'bg-emerald-500' : 'bg-rose-500',
                ]"
              />
              <span class="text-xs font-semibold text-slate-500">{{ tx.category }}</span>
            </div>
            <p class="truncate text-sm font-bold text-slate-800">{{ tx.description || '-' }}</p>
            <div class="flex items-center gap-1.5 text-[10px] text-slate-400 mt-1">
              <span>{{ formatDate(tx.date) }}</span>
              <span v-if="tx.fund_source_id" class="px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">
                {{ getFundSourceDisplay(tx.fund_source_id) }}
              </span>
            </div>
          </div>

          <div class="text-right flex flex-col items-end gap-1.5 shrink-0 pl-4">
            <p
              class="text-sm font-bold"
              :class="tx.type === 'income' ? 'text-green-600' : 'text-red-600'"
            >
              {{ tx.type === 'income' ? '+' : '-' }}{{ formatRupiah(tx.amount) }}
            </p>
            <div class="flex gap-2">
              <button
                type="button"
                class="text-xs font-semibold text-sky-600 active:text-sky-800"
                @click="openEdit(tx)"
              >
                Ubah
              </button>
              <button
                type="button"
                class="text-xs font-semibold text-rose-500 active:text-rose-700"
                @click="confirmDelete(tx.id)"
              >
                Hapus
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Desktop Table View (hidden on Mobile) -->
      <div v-if="filteredTransactions.length > 0" class="hidden md:block overflow-hidden rounded-2xl border border-slate-200">
        <table class="min-w-full divide-y divide-slate-200">
          <thead class="bg-slate-50">
            <tr class="text-left text-xs font-bold uppercase tracking-wider text-slate-500">
              <th class="px-6 py-3.5">Tanggal</th>
              <th class="px-6 py-3.5">Kategori</th>
              <th class="px-6 py-3.5">Deskripsi</th>
              <th class="px-6 py-3.5">Sumber Uang</th>
              <th class="px-6 py-3.5">Jumlah</th>
              <th class="px-6 py-3.5 text-right">Aksi</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 bg-white text-sm text-slate-700">
            <tr v-for="tx in filteredTransactions" :key="tx.id" class="hover:bg-slate-50/50">
              <td class="whitespace-nowrap px-6 py-4">{{ formatDate(tx.date) }}</td>
              <td class="whitespace-nowrap px-6 py-4">
                <span class="inline-flex rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-800">
                  {{ tx.category }}
                </span>
              </td>
              <td class="px-6 py-4 truncate max-w-[200px]">{{ tx.description || '-' }}</td>
              <td class="whitespace-nowrap px-6 py-4 text-xs text-slate-600">
                {{ getFundSourceDisplay(tx.fund_source_id) }}
              </td>
              <td
                class="whitespace-nowrap px-6 py-4 font-semibold"
                :class="tx.type === 'income' ? 'text-green-600' : 'text-red-600'"
              >
                {{ tx.type === 'income' ? '+' : '-' }}{{ formatRupiah(tx.amount) }}
              </td>
              <td class="whitespace-nowrap px-6 py-4">
                <div class="flex justify-end gap-3">
                  <button
                    type="button"
                    class="text-xs font-bold text-sky-600 hover:text-sky-500"
                    @click="openEdit(tx)"
                  >
                    Ubah
                  </button>
                  <button
                    type="button"
                    class="text-xs font-bold text-rose-600 hover:text-rose-500"
                    @click="confirmDelete(tx.id)"
                  >
                    Hapus
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modals -->
    <EditTransactionModal
      :show="showEditModal"
      :transaction="transactionToEdit"
      :fund-sources="fundSources"
      :is-loading="loading"
      @close="showEditModal = false"
      @confirm="executeEdit"
    />

    <DeleteConfirmationModal
      :show="showDeleteModal"
      :is-loading="loading"
      @close="showDeleteModal = false"
      @confirm="executeDelete"
    />
  </div>
</template>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
.hide-scrollbar::-webkit-scrollbar {
  display: none;
}
.hide-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
