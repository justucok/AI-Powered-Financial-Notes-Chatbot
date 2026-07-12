<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import SummaryCards from '../components/SummaryCards.vue'
import ChatBox from '../components/ChatBox.vue'
import { useBudget } from '../composables/useBudget'
import { useStatistics } from '../composables/useStatistics'
import { useFundSources } from '../composables/useFundSources'
import { formatRupiah } from '../utils/formatters'

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  Filler,
} from 'chart.js'
import { Bar, Doughnut } from 'vue-chartjs'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  Filler
)

const props = defineProps({
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
})

const { summary: budgetSummary, fetchBudgetSummary } = useBudget()
const { loading: statsLoading, dailyTransactions, monthlySummaries, allCategories, fetchStatisticsData } = useStatistics()
const { sources: fundSources, fetchSources } = useFundSources()

async function handleTransactionAdded() {
  await fetchSources()
  emit('refresh')
  const today = new Date()
  const currentMonthKey = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`
  await fetchBudgetSummary(currentMonthKey)
}

// Global/Dashboard init
onMounted(async () => {
  await fetchSources()
  const today = new Date()
  const currentMonthKey = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`
  await fetchBudgetSummary(currentMonthKey)
  fetchStatisticsData(selectedStatMonth.value)
})

// === STATISTICS LOGIC ===
const type = ref('expense')
const period = ref('daily')

const todayObj = new Date()
const initialMonthKey = `${todayObj.getFullYear()}-${String(todayObj.getMonth() + 1).padStart(2, '0')}`
const selectedStatMonth = ref(initialMonthKey)

watch(selectedStatMonth, (newVal) => {
  fetchStatisticsData(newVal)
})

const monthName = computed(() => {
  if (!selectedStatMonth.value) return ''
  const [y, m] = selectedStatMonth.value.split('-')
  const d = new Date(parseInt(y), parseInt(m) - 1, 1)
  return d.toLocaleDateString('id-ID', { month: 'long', year: 'numeric' })
})

const dailyData = computed(() => {
  const [y, m] = selectedStatMonth.value.split('-')
  const daysInMonth = new Date(parseInt(y), parseInt(m), 0).getDate()
  const data = Array.from({ length: daysInMonth }, (_, i) => ({
    label: String(i + 1),
    value: 0
  }))

  const filtered = dailyTransactions.value.filter(t => t.type === type.value)
  filtered.forEach(t => {
    const day = parseInt(t.date.split('-')[2], 10)
    if (day >= 1 && day <= daysInMonth) {
      data[day - 1].value += t.amount
    }
  })
  return data
})

const weeklyData = computed(() => {
  const data = [
    { label: 'Minggu 1', value: 0 },
    { label: 'Minggu 2', value: 0 },
    { label: 'Minggu 3', value: 0 },
    { label: 'Minggu 4', value: 0 },
    { label: 'Minggu 5', value: 0 },
  ]

  const filtered = dailyTransactions.value.filter(t => t.type === type.value)
  filtered.forEach(t => {
    const day = parseInt(t.date.split('-')[2], 10)
    const weekIndex = Math.min(Math.floor((day - 1) / 7), 4)
    data[weekIndex].value += t.amount
  })

  if (data[4].value === 0) data.pop()
  return data
})

const monthlyData = computed(() => {
  return monthlySummaries.value.map(s => {
    const d = new Date(s.month + '-01')
    return {
      label: d.toLocaleDateString('id-ID', { month: 'short' }),
      value: type.value === 'expense' ? s.expense : s.income
    }
  })
})

const activeData = computed(() => {
  if (period.value === 'daily') return dailyData.value
  if (period.value === 'weekly') return weeklyData.value
  return monthlyData.value
})

const chartColor = computed(() => type.value === 'expense' ? '#ef4444' : '#10b981')
const barChartData = computed(() => {
  return {
    labels: activeData.value.map(d => d.label),
    datasets: [
      {
        label: type.value === 'expense' ? 'Pengeluaran' : 'Pemasukan',
        backgroundColor: chartColor.value,
        borderRadius: 4,
        data: activeData.value.map(d => d.value),
      }
    ]
  }
})

const barChartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: function(context) {
          let label = context.dataset.label || '';
          if (label) label += ': ';
          if (context.parsed.y !== null) label += formatRupiah(context.parsed.y);
          return label;
        }
      }
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: { color: '#f1f5f9' },
      ticks: {
        callback: function(value) {
          if (value === 0) return '0'
          return 'Rp ' + (value / 1000) + 'k'
        }
      }
    },
    x: { grid: { display: false } }
  }
}))

const categoryData = computed(() => {
  const map = {}
  const filtered = dailyTransactions.value.filter(t => t.type === type.value)
  filtered.forEach(t => {
    map[t.category] = (map[t.category] || 0) + t.amount
  })
  
  const total = Object.values(map).reduce((a,b) => a+b, 0)
  const colors = ['#3b82f6', '#ec4899', '#f59e0b', '#10b981', '#8b5cf6', '#ef4444', '#14b8a6']

  let i = 0
  const arr = Object.keys(map).map(catName => {
    const val = map[catName]
    const percent = total > 0 ? (val / total * 100) : 0
    const catMeta = allCategories.value.find(c => c.name === catName) || {}
    
    return {
      name: catName,
      icon: catMeta.icon || '🏷️',
      value: val,
      percent: percent.toFixed(1),
      color: colors[i++ % colors.length]
    }
  }).sort((a,b) => b.value - a.value)
  
  return { data: arr, total }
})

const doughnutChartData = computed(() => {
  return {
    labels: categoryData.value.data.map(d => d.name),
    datasets: [
      {
        backgroundColor: categoryData.value.data.map(d => d.color),
        data: categoryData.value.data.map(d => d.value),
        borderWidth: 2,
        borderColor: '#ffffff',
        hoverOffset: 4
      }
    ]
  }
})

const doughnutChartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  cutout: '70%',
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: function(context) {
          let label = context.label || '';
          if (label) label += ': ';
          if (context.parsed !== null) label += formatRupiah(context.parsed);
          return label;
        }
      }
    }
  }
}))

const maxActiveValue = computed(() => Math.max(...activeData.value.map(d => d.value), 0))

function handlePrevMonth() {
  const [y, m] = selectedStatMonth.value.split('-')
  let date = new Date(parseInt(y), parseInt(m) - 2, 1)
  selectedStatMonth.value = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
}

function handleNextMonth() {
  const [y, m] = selectedStatMonth.value.split('-')
  let date = new Date(parseInt(y), parseInt(m), 1)
  selectedStatMonth.value = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
}
</script>

<template>
  <div class="px-4 py-6 pb-4 md:p-8 xl:p-10 h-full min-h-[calc(100vh-4rem)] flex flex-col space-y-10">
    
    <!-- Top Section: Summary & Budget -->
    <section class="flex flex-col gap-8">
      <header class="flex flex-col gap-1 shrink-0">
        <p class="text-xs font-semibold uppercase tracking-[0.24em] text-sky-600">Ringkasan Finansial</p>
        <h1 class="text-2xl md:text-3xl font-bold tracking-tight text-slate-900">
          Halo, {{ nickname || 'Pengguna' }}!
        </h1>
        <p class="text-sm md:text-base text-slate-500 max-w-2xl">
          Berikut ringkasan posisi keuangan Anda bulan ini.
        </p>
      </header>

      <SummaryCards
        :balance="balance"
        :income="income"
        :expense="expense"
      />

      <div 
        v-if="budgetSummary.total_budget > 0" 
        class="bg-white rounded-[1.75rem] p-6 md:p-8 border border-slate-100 shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-[0_16px_50px_rgb(0,0,0,0.06)] transition-all duration-300 flex flex-col md:flex-row md:items-center justify-between gap-6 relative overflow-hidden group"
      >
        <div class="absolute inset-0 bg-gradient-to-br from-slate-50/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        <div class="flex items-center space-x-4 relative z-10">
          <span class="text-4xl md:text-5xl drop-shadow-sm transition-transform duration-300 group-hover:scale-110">🎯</span>
          <div>
            <h4 class="font-bold text-slate-800 text-sm tracking-wide">Budget Bulan Ini</h4>
            <div class="flex items-baseline space-x-2 mt-1">
              <span class="text-xl md:text-2xl font-extrabold text-slate-900 tracking-tight">
                {{ formatRupiah(budgetSummary.total_remaining) }}
              </span>
              <span class="text-xs text-slate-500 font-medium">sisa budget</span>
            </div>
          </div>
        </div>
        
        <div class="flex-1 w-full max-w-md mt-4 md:mt-0 relative z-10">
          <div class="relative h-3 w-full overflow-hidden rounded-full bg-slate-100 shadow-inner">
            <div
              class="h-full rounded-full transition-all duration-700 ease-out relative overflow-hidden"
              :class="budgetSummary.total_percent > 100 ? 'bg-rose-500 shadow-[0_0_10px_rgba(244,63,94,0.4)]' : (budgetSummary.total_percent > 80 ? 'bg-amber-400 shadow-[0_0_10px_rgba(251,191,36,0.4)]' : 'bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.4)]')"
              :style="{ width: `${Math.min(budgetSummary.total_percent, 100)}%` }"
            >
              <div class="absolute inset-0 bg-white/20 w-full h-full skew-x-12 translate-x-[-150%] animate-[shimmer_2s_infinite]"></div>
            </div>
          </div>
          <div class="flex justify-between text-[11px] text-slate-500 font-bold uppercase tracking-wider mt-2 px-1">
            <span>Terpakai: {{ formatRupiah(budgetSummary.total_actual) }} ({{ budgetSummary.total_percent }}%)</span>
            <span v-if="budgetSummary.total_percent > 100" class="text-rose-500 animate-pulse">OVER BUDGET</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Middle Section: Mobile Chatbot -->
    <section class="block lg:hidden h-[600px]">
      <ChatBox 
        :fund-sources="fundSources"
        @transaction-added="handleTransactionAdded"
        class="h-full flex flex-col shadow-sm rounded-3xl bg-white border border-slate-100"
      />
    </section>

    <!-- Bottom Section: Statistics -->
    <section class="hidden lg:block rounded-3xl border border-white/70 bg-white/80 p-5 md:p-8 shadow-[0_24px_80px_rgba(15,23,42,0.06)] backdrop-blur space-y-8">
      
      <!-- Statistics Header & Filter -->
      <header class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 class="text-xl font-bold text-slate-900">Statistik Keuangan</h2>
          <p class="text-sm text-slate-500">Analisis pengeluaran dan pemasukan berdasarkan tren dan kategori.</p>
        </div>
        
        <!-- Month Filter -->
        <div class="flex items-center gap-3 bg-white px-3 py-1.5 rounded-xl border border-slate-200 shadow-sm self-start sm:self-auto">
          <button @click="handlePrevMonth" class="p-1 hover:bg-slate-100 rounded-lg text-slate-500">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
          </button>
          <input 
            type="month" 
            v-model="selectedStatMonth" 
            class="font-semibold text-slate-700 bg-transparent outline-none cursor-pointer"
          />
          <button @click="handleNextMonth" class="p-1 hover:bg-slate-100 rounded-lg text-slate-500">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
          </button>
        </div>
      </header>

      <!-- Toggle Income/Expense -->
      <div class="flex p-1 bg-slate-100 rounded-xl w-full max-w-md mx-auto sm:mx-0">
        <button @click="type = 'expense'"
                :class="type === 'expense' ? 'bg-white shadow-sm text-rose-600 ring-1 ring-slate-200/50' : 'text-slate-500 hover:text-slate-700'"
                class="flex-1 py-2 text-sm font-bold rounded-lg transition-all">
          💸 Pengeluaran
        </button>
        <button @click="type = 'income'"
                :class="type === 'income' ? 'bg-white shadow-sm text-emerald-600 ring-1 ring-slate-200/50' : 'text-slate-500 hover:text-slate-700'"
                class="flex-1 py-2 text-sm font-bold rounded-lg transition-all">
          📈 Pemasukan
        </button>
      </div>

      <!-- Graph Section -->
      <div>
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div>
            <h3 class="font-bold text-slate-900 text-lg">Tren Keuangan</h3>
            <p class="text-xs text-slate-500">{{ period === 'monthly' ? '6 Bulan Terakhir' : monthName }}</p>
          </div>
          
          <div class="flex bg-slate-100 rounded-lg p-0.5 self-start sm:self-auto">
            <button @click="period = 'daily'"
                    :class="period === 'daily' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'"
                    class="px-4 py-1.5 text-xs font-semibold rounded-md transition-all">Harian</button>
            <button @click="period = 'weekly'"
                    :class="period === 'weekly' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'"
                    class="px-4 py-1.5 text-xs font-semibold rounded-md transition-all">Mingguan</button>
            <button @click="period = 'monthly'"
                    :class="period === 'monthly' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'"
                    class="px-4 py-1.5 text-xs font-semibold rounded-md transition-all">Bulanan</button>
          </div>
        </div>
        
        <div v-if="statsLoading" class="h-64 flex justify-center items-center">
          <span class="animate-spin h-8 w-8 border-4 border-sky-600 border-t-transparent rounded-full"></span>
        </div>
        <div v-else class="w-full h-64 sm:h-80">
          <Bar :data="barChartData" :options="barChartOptions" />
        </div>
        
        <div class="mt-4 flex justify-between text-sm px-2">
          <span class="text-slate-500">Tertinggi</span>
          <span class="font-bold text-slate-900">{{ formatRupiah(maxActiveValue) }}</span>
        </div>
      </div>

      <hr class="border-slate-100">

      <!-- Category Usage (Pie Chart) -->
      <div>
        <h3 class="font-bold text-slate-900 text-lg mb-6">Penggunaan Kategori ({{ monthName }})</h3>
        <div v-if="statsLoading" class="h-48 flex justify-center items-center">
          <span class="animate-spin h-8 w-8 border-4 border-sky-600 border-t-transparent rounded-full"></span>
        </div>
        <div v-else-if="categoryData.data.length === 0" class="text-center py-8">
          <p class="text-slate-400">Tidak ada data di bulan ini.</p>
        </div>
        <div v-else class="flex flex-col md:flex-row items-center gap-8">
          
          <!-- Chart.js Doughnut -->
          <div class="w-56 h-56 relative flex-shrink-0">
            <Doughnut :data="doughnutChartData" :options="doughnutChartOptions" />
            <!-- Center Text -->
            <div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
              <p class="text-[10px] text-slate-500 font-bold uppercase">Total</p>
              <p class="text-sm font-bold text-slate-900 truncate max-w-[100px]" :title="formatRupiah(categoryData.total)">
                {{ formatRupiah(categoryData.total) }}
              </p>
            </div>
          </div>

          <!-- Legend List -->
          <div class="flex-1 w-full space-y-3">
            <div v-for="item in categoryData.data" :key="item.name"
                  class="flex items-center justify-between p-2 rounded-xl hover:bg-slate-50 transition-colors">
              <div class="flex items-center gap-3">
                <div class="w-3 h-3 rounded-full shadow-sm" :style="{ backgroundColor: item.color }"></div>
                <span class="text-lg">{{ item.icon }}</span>
                <div>
                  <p class="text-sm font-bold text-slate-900">{{ item.name }}</p>
                  <p class="text-xs text-slate-500">{{ item.percent }}%</p>
                </div>
              </div>
              <div class="text-right">
                <p class="text-sm font-bold text-slate-900">{{ formatRupiah(item.value) }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

  </div>
</template>
