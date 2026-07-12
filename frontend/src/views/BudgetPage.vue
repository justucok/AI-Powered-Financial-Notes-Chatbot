<script setup>
import { onMounted, ref, watch, computed } from 'vue'
import { formatRupiah } from '../utils/formatters'
import { useBudget } from '../composables/useBudget'

const { loading, error, summary, fetchBudgetSummary } = useBudget()

const today = new Date()
const currentMonthKey = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`
const selectedMonth = ref(currentMonthKey)

onMounted(() => {
  fetchBudgetSummary(selectedMonth.value)
})

watch(selectedMonth, (newVal) => {
  fetchBudgetSummary(newVal)
})

const monthName = computed(() => {
  if (!selectedMonth.value) return ''
  const [y, m] = selectedMonth.value.split('-')
  const d = new Date(parseInt(y), parseInt(m) - 1, 1)
  return d.toLocaleDateString('id-ID', { month: 'long', year: 'numeric' })
})

function handlePrevMonth() {
  const [y, m] = selectedMonth.value.split('-')
  let date = new Date(parseInt(y), parseInt(m) - 2, 1)
  selectedMonth.value = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
}

function handleNextMonth() {
  const [y, m] = selectedMonth.value.split('-')
  let date = new Date(parseInt(y), parseInt(m), 1)
  selectedMonth.value = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
}
</script>

<template>
  <div class="px-4 py-6 md:p-8 space-y-6 pb-24">
    <!-- Header -->
    <header class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div class="flex flex-col gap-1">
        <p class="text-xs font-semibold uppercase tracking-[0.24em] text-emerald-600">Budget</p>
        <h1 class="text-2xl font-bold tracking-tight text-slate-900">Anggaran Bulanan</h1>
        <p class="text-sm text-slate-500">Pantau batas pengeluaran Anda agar keuangan tetap stabil.</p>
      </div>

      <!-- Month Filter -->
      <div class="flex items-center gap-3 bg-white px-3 py-1.5 rounded-xl border border-slate-200 shadow-sm self-start sm:self-auto">
        <button @click="handlePrevMonth" class="p-1 hover:bg-slate-100 rounded-lg text-slate-500">
          <span class="text-lg">◀</span>
        </button>
        <input 
          type="month" 
          v-model="selectedMonth" 
          class="font-semibold text-slate-700 bg-transparent outline-none cursor-pointer"
        />
        <button @click="handleNextMonth" class="p-1 hover:bg-slate-100 rounded-lg text-slate-500">
          <span class="text-lg">▶</span>
        </button>
      </div>
    </header>

    <div v-if="loading" class="flex justify-center py-12">
      <span class="animate-spin h-8 w-8 border-4 border-emerald-600 border-t-transparent rounded-full"></span>
    </div>

    <div v-else-if="error" class="rounded-2xl bg-rose-50 p-4 text-center text-rose-600">
      {{ error }}
    </div>

    <div v-else class="space-y-6">
      
      <!-- Total Budget Card -->
      <div class="rounded-3xl bg-white p-6 md:p-8 shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-slate-100">
        <div class="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-6">
          <div>
            <h2 class="text-lg font-bold text-slate-800">Total Anggaran ({{ monthName }})</h2>
            <p class="text-sm text-slate-500">Sisa dari keseluruhan anggaran</p>
          </div>
          <div class="text-left md:text-right">
            <p class="text-3xl font-extrabold tracking-tight text-slate-900">
              {{ formatRupiah(summary.total_remaining) }}
            </p>
            <p class="text-sm font-medium text-slate-500">
              dari {{ formatRupiah(summary.total_budget) }}
            </p>
          </div>
        </div>

        <!-- Progress Bar -->
        <div class="relative h-4 w-full overflow-hidden rounded-full bg-slate-100">
          <div
            class="h-full transition-all duration-500 ease-out rounded-full"
            :class="summary.total_percent > 100 ? 'bg-rose-500' : (summary.total_percent > 80 ? 'bg-amber-400' : 'bg-emerald-500')"
            :style="{ width: `${Math.min(summary.total_percent, 100)}%` }"
          ></div>
        </div>
        <div class="mt-2 flex justify-between text-xs font-semibold text-slate-500">
          <span>Terpakai: {{ formatRupiah(summary.total_actual) }} ({{ summary.total_percent }}%)</span>
          <span v-if="summary.total_percent > 100" class="text-rose-600">OVER BUDGET</span>
        </div>
      </div>

      <!-- Categories Budget Grid -->
      <div>
        <h3 class="text-sm font-bold uppercase tracking-wider text-slate-400 mb-4 px-2">Alokasi Kategori</h3>
        
        <div v-if="summary.category_budgets.length === 0" class="text-center py-10 bg-white rounded-3xl border border-slate-100 shadow-[0_8px_30px_rgb(0,0,0,0.04)]">
          <span class="text-4xl mb-3 block">⚙️</span>
          <p class="text-slate-600 font-medium">Anggaran belum diatur.</p>
          <p class="text-sm text-slate-400 mt-1">Buka menu Settings > Budget untuk mengatur anggaran.</p>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div 
            v-for="cat in summary.category_budgets" 
            :key="cat.category_name"
            class="rounded-2xl bg-white p-5 shadow-[0_4px_20px_rgb(0,0,0,0.03)] border border-slate-100 transition hover:-translate-y-1 hover:shadow-md"
          >
            <div class="flex justify-between items-start mb-3">
              <span class="font-bold text-slate-800">{{ cat.category_name }}</span>
              <span 
                class="px-2 py-1 text-xs font-bold rounded-lg"
                :class="cat.percent > 100 ? 'bg-rose-100 text-rose-700' : 'bg-emerald-50 text-emerald-700'"
              >
                Sisa {{ formatRupiah(cat.remaining_amount) }}
              </span>
            </div>
            
            <div class="relative h-2.5 w-full overflow-hidden rounded-full bg-slate-100 mb-2">
              <div
                class="h-full transition-all duration-500 ease-out rounded-full"
                :class="cat.percent > 100 ? 'bg-rose-500' : (cat.percent > 80 ? 'bg-amber-400' : 'bg-emerald-400')"
                :style="{ width: `${Math.min(cat.percent, 100)}%` }"
              ></div>
            </div>
            
            <div class="flex justify-between text-xs text-slate-500">
              <span>{{ formatRupiah(cat.actual_amount) }} ({{ cat.percent }}%)</span>
              <span>Batas: {{ formatRupiah(cat.budget_amount) }}</span>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>
