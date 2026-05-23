<script setup>
import { computed } from 'vue'

import { formatDate, formatMonth, formatRupiah } from '../utils/formatters'

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
})

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

function handleMonthChange(event) {
  emit('month-changed', event.target.value)
}

function handleDelete(id) {
  if (window.confirm('Apakah Anda yakin ingin menghapus transaksi ini?')) {
    emit('delete-transaction', id)
  }
}

function formatAmount(transaction) {
  const sign = transaction.type === 'income' ? '+' : '-'
  return `${sign}${formatRupiah(transaction.amount)}`
}
</script>

<template>
  <section class="rounded-[2rem] border border-white/70 bg-white/80 p-5 shadow-[0_24px_80px_rgba(15,23,42,0.08)] backdrop-blur sm:p-6">
    <div class="mb-5 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.28em] text-slate-500">
          Transaction History
        </p>
        <h2 class="mt-1 text-xl font-semibold text-slate-900">
          Riwayat transaksi per bulan
        </h2>
      </div>

      <label class="space-y-2">
        <span class="text-sm font-medium text-slate-700">Filter bulan</span>
        <select
          :value="selectedMonth"
          class="h-12 rounded-2xl border border-slate-200 bg-white px-4 text-sm text-slate-700 outline-none transition focus:border-slate-400 focus:ring-4 focus:ring-slate-100"
          @change="handleMonthChange"
        >
          <option v-for="month in monthOptions" :key="month" :value="month">
            {{ formatMonth(month) }}
          </option>
        </select>
      </label>
    </div>

    <div class="overflow-hidden rounded-[1.5rem] border border-slate-200">
      <table class="min-w-full divide-y divide-slate-200">
        <thead class="bg-slate-50">
          <tr class="text-left text-sm font-semibold text-slate-600">
            <th class="px-4 py-3">
              Tanggal
            </th>
            <th class="px-4 py-3">
              Deskripsi
            </th>
            <th class="px-4 py-3">
              Kategori
            </th>
            <th class="px-4 py-3">
              Jumlah
            </th>
            <th class="px-4 py-3">
              Aksi
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100 bg-white text-sm text-slate-700">
          <tr v-if="loading" v-for="index in 5" :key="`skeleton-${index}`">
            <td class="px-4 py-4">
              <div class="h-4 w-20 animate-pulse rounded bg-slate-200" />
            </td>
            <td class="px-4 py-4">
              <div class="h-4 w-40 animate-pulse rounded bg-slate-200" />
            </td>
            <td class="px-4 py-4">
              <div class="h-4 w-24 animate-pulse rounded bg-slate-200" />
            </td>
            <td class="px-4 py-4">
              <div class="h-4 w-28 animate-pulse rounded bg-slate-200" />
            </td>
            <td class="px-4 py-4">
              <div class="h-4 w-16 animate-pulse rounded bg-slate-200" />
            </td>
          </tr>

          <tr v-else-if="transactions.length === 0">
            <td colspan="5" class="px-4 py-10 text-center text-slate-500">
              Belum ada transaksi untuk periode {{ formatMonth(selectedMonth) }}.
            </td>
          </tr>

          <tr v-for="transaction in transactions" v-else :key="transaction.id">
            <td class="px-4 py-4">
              {{ formatDate(transaction.date) }}
            </td>
            <td class="px-4 py-4">
              {{ transaction.description || '-' }}
            </td>
            <td class="px-4 py-4">
              {{ transaction.category }}
            </td>
            <td
              class="px-4 py-4 font-semibold"
              :class="transaction.type === 'income' ? 'text-green-600' : 'text-red-600'"
            >
              {{ formatAmount(transaction) }}
            </td>
            <td class="px-4 py-4">
              <button
                type="button"
                class="text-sm font-medium text-rose-600 transition hover:text-rose-500"
                @click="handleDelete(transaction.id)"
              >
                Hapus
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
