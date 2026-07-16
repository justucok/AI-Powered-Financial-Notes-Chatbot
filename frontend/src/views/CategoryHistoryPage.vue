<script setup>
import { computed } from 'vue'
import { formatRupiah, formatDate } from '../utils/formatters'

const props = defineProps({
  category: String,
  month: String, // format YYYY-MM
  transactions: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['back'])

const totalAmount = computed(() => {
  return props.transactions.reduce((sum, tx) => sum + tx.amount, 0)
})

const monthName = computed(() => {
  if (!props.month) return ''
  const [y, m] = props.month.split('-')
  const d = new Date(parseInt(y), parseInt(m) - 1, 1)
  return d.toLocaleDateString('id-ID', { month: 'long', year: 'numeric' })
})
</script>

<template>
  <div class="h-full bg-slate-50 overflow-y-auto pb-20 md:pb-6">
    <!-- Mobile Sticky Header -->
    <div class="sticky top-0 z-10 bg-white/80 backdrop-blur border-b border-slate-200 px-4 py-3 flex items-center shadow-sm">
      <button @click="$emit('back')" class="mr-3 text-slate-500 hover:text-slate-800 transition-colors p-2 -ml-2 rounded-full hover:bg-slate-100">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
        </svg>
      </button>
      <div>
        <h2 class="text-lg font-bold text-slate-900 leading-tight">Histori Kategori</h2>
        <p class="text-xs text-slate-500">{{ monthName }}</p>
      </div>
    </div>

    <div class="px-4 py-6 max-w-2xl mx-auto space-y-6">
      
      <!-- Category Header & Summary -->
      <div class="bg-gradient-to-r from-sky-600 to-indigo-700 rounded-2xl p-6 text-white shadow-lg relative overflow-hidden">
        <div class="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI4IiBoZWlnaHQ9IjgiPgo8cmVjdCB3aWR0aD0iOCIgaGVpZ2h0PSI4IiBmaWxsPSIjZmZmIiBmaWxsLW9wYWNpdHk9IjAuMDUiLz4KPC9zdmc+')] opacity-20"></div>
        <div class="relative">
          <div class="flex items-center gap-3 mb-4">
            <span class="bg-white/20 p-2 rounded-xl text-2xl backdrop-blur-md">🏷️</span>
            <h3 class="text-2xl font-bold">{{ category }}</h3>
          </div>
          <div>
            <p class="text-sky-100 text-sm mb-1">Total Transaksi</p>
            <p class="text-3xl font-bold">{{ formatRupiah(totalAmount) }}</p>
          </div>
        </div>
      </div>

      <!-- Transaction List -->
      <div>
        <h3 class="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4 px-1">Daftar Transaksi</h3>
        
        <div v-if="transactions.length === 0" class="flex flex-col items-center justify-center py-12 text-center">
          <div class="w-16 h-16 bg-slate-200/50 rounded-full flex items-center justify-center text-2xl mb-3">📭</div>
          <p class="text-slate-500 text-sm">Tidak ada transaksi untuk kategori ini.</p>
        </div>
        
        <div v-else class="space-y-3">
          <div v-for="tx in transactions" :key="tx.id" 
               class="bg-white p-4 rounded-xl border border-slate-200/60 shadow-sm flex items-center justify-between">
            
            <div class="flex items-center gap-4 min-w-0">
              <div class="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center shrink-0 border border-slate-200 text-base">
                📅
              </div>
              <div class="min-w-0">
                <p class="text-sm font-bold text-slate-900 truncate">{{ tx.description || tx.category }}</p>
                <div class="flex items-center gap-2 mt-0.5">
                  <span class="text-xs text-slate-500">{{ formatDate(tx.date) }}</span>
                </div>
              </div>
            </div>
            
            <div class="text-right shrink-0 ml-4">
              <p :class="['text-sm font-bold', tx.type === 'expense' ? 'text-red-600' : 'text-emerald-600']">
                {{ tx.type === 'expense' ? '-' : '+' }}{{ formatRupiah(tx.amount) }}
              </p>
            </div>
            
          </div>
        </div>
      </div>
      
    </div>
  </div>
</template>
