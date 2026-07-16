<script setup>
import { computed } from 'vue'
import { formatRupiah, formatDate } from '../utils/formatters'

const props = defineProps({
  visible: Boolean,
  category: String,
  month: String, // format YYYY-MM
  transactions: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close'])

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
  <div v-if="visible" class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-0">
    <div class="fixed inset-0 bg-slate-900/50 backdrop-blur-sm transition-opacity" @click="$emit('close')"></div>
    
    <div class="relative w-full max-w-lg overflow-hidden rounded-2xl bg-white shadow-2xl transition-all h-full max-h-[85vh] flex flex-col scale-100">
      
      <!-- Header -->
      <div class="bg-gradient-to-r from-sky-600 to-indigo-700 px-6 py-5 shrink-0 relative overflow-hidden">
        <div class="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI4IiBoZWlnaHQ9IjgiPgo8cmVjdCB3aWR0aD0iOCIgaGVpZ2h0PSI4IiBmaWxsPSIjZmZmIiBmaWxsLW9wYWNpdHk9IjAuMDUiLz4KPC9zdmc+')] opacity-20"></div>
        <div class="relative flex items-start justify-between">
          <div>
            <div class="flex items-center gap-2 text-sky-100 mb-1">
              <span class="text-xs font-semibold uppercase tracking-wider">{{ monthName }}</span>
            </div>
            <h3 class="text-xl font-bold text-white flex items-center gap-2">
              <span class="bg-white/20 p-1.5 rounded-lg text-xl backdrop-blur-md">🏷️</span>
              {{ category }}
            </h3>
          </div>
          <button @click="$emit('close')" class="text-white/70 hover:text-white transition-colors bg-white/10 hover:bg-white/20 p-2 rounded-full backdrop-blur-sm">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
        </div>
      </div>
      
      <!-- Summary Card -->
      <div class="bg-slate-50 border-b border-slate-100 px-6 py-4 shrink-0 flex items-center justify-between">
        <span class="text-sm font-semibold text-slate-500">Total Transaksi</span>
        <span class="text-lg font-bold text-slate-900">{{ formatRupiah(totalAmount) }}</span>
      </div>

      <!-- Transaction List -->
      <div class="p-6 overflow-y-auto flex-1 bg-slate-50/50">
        <div v-if="transactions.length === 0" class="flex flex-col items-center justify-center h-full text-center space-y-3">
          <div class="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center text-2xl">📭</div>
          <p class="text-slate-500 text-sm">Tidak ada transaksi untuk kategori ini di bulan yang dipilih.</p>
        </div>
        
        <div v-else class="space-y-3">
          <div v-for="tx in transactions" :key="tx.id" 
               class="bg-white p-4 rounded-xl border border-slate-200/60 shadow-sm hover:shadow-md transition-shadow flex items-center justify-between group">
            
            <div class="flex items-center gap-4 min-w-0">
              <div class="w-12 h-12 rounded-xl bg-slate-100 flex items-center justify-center shrink-0 border border-slate-200 text-lg group-hover:scale-105 transition-transform">
                📅
              </div>
              <div class="min-w-0">
                <p class="text-sm font-bold text-slate-900 truncate">{{ tx.description || tx.category }}</p>
                <div class="flex items-center gap-2 mt-1">
                  <span class="text-[11px] font-medium px-2 py-0.5 rounded-full bg-slate-100 text-slate-500 border border-slate-200">
                    {{ formatDate(tx.date) }}
                  </span>
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
