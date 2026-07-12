<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { formatRupiah } from '../utils/formatters'
import { useStatistics } from '../composables/useStatistics'

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
  initialType: {
    type: String,
    default: 'expense' // 'expense' or 'income'
  }
})

const { loading, dailyTransactions, monthlySummaries, allCategories, fetchStatisticsData } = useStatistics()

const type = ref(props.initialType)
const period = ref('daily') // 'daily', 'weekly', 'monthly'

const today = new Date()
const currentMonthKey = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`
const selectedMonth = ref(currentMonthKey)

onMounted(() => {
  fetchStatisticsData(selectedMonth.value)
})

watch(selectedMonth, (newVal) => {
  fetchStatisticsData(newVal)
})

watch(() => props.initialType, (newVal) => {
  type.value = newVal
})

const monthName = computed(() => {
  if (!selectedMonth.value) return ''
  const [y, m] = selectedMonth.value.split('-')
  const d = new Date(parseInt(y), parseInt(m) - 1, 1)
  return d.toLocaleDateString('id-ID', { month: 'long', year: 'numeric' })
})

// === DATA AGGREGATION ===

// 1. Daily Data (Selected Month)
const dailyData = computed(() => {
  const [y, m] = selectedMonth.value.split('-')
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

// 2. Weekly Data (Selected Month)
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

  if (data[4].value === 0) {
    data.pop()
  }

  return data
})

// 3. Monthly Data (Last 6 Months relative to selected month)
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

// === CHART.JS COMPUTED CONFIG ===

const chartColor = computed(() => type.value === 'expense' ? '#ef4444' : '#10b981')
const chartBgColor = computed(() => type.value === 'expense' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(16, 185, 129, 0.2)')

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
    legend: {
      display: false
    },
    tooltip: {
      callbacks: {
        label: function(context) {
          let label = context.dataset.label || '';
          if (label) {
            label += ': ';
          }
          if (context.parsed.y !== null) {
            label += formatRupiah(context.parsed.y);
          }
          return label;
        }
      }
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: {
        color: '#f1f5f9'
      },
      ticks: {
        callback: function(value) {
          if (value === 0) return '0'
          return 'Rp ' + (value / 1000) + 'k'
        }
      }
    },
    x: {
      grid: {
        display: false
      }
    }
  }
}))

// 4. Category Pie Chart (Selected Month)
const categoryData = computed(() => {
  const map = {}
  const filtered = dailyTransactions.value.filter(t => t.type === type.value)
  filtered.forEach(t => {
    map[t.category] = (map[t.category] || 0) + t.amount
  })
  
  const total = Object.values(map).reduce((a,b) => a+b, 0)
  
  const colors = [
    '#3b82f6', '#ec4899', '#f59e0b', '#10b981', '#8b5cf6', '#ef4444', '#14b8a6'
  ]

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
    legend: {
      display: false
    },
    tooltip: {
      callbacks: {
        label: function(context) {
          let label = context.label || '';
          if (label) {
            label += ': ';
          }
          if (context.parsed !== null) {
            label += formatRupiah(context.parsed);
          }
          return label;
        }
      }
    }
  }
}))

const maxActiveValue = computed(() => Math.max(...activeData.value.map(d => d.value), 0))

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
        <p class="text-xs font-semibold uppercase tracking-[0.24em] text-sky-600">Statistik</p>
        <h1 class="text-2xl font-bold tracking-tight text-slate-900">Analisis Keuangan</h1>
        <p class="text-sm text-slate-500">Analisis pengeluaran dan pemasukan Anda secara detail.</p>
      </div>

      <!-- Month Filter -->
      <div class="flex items-center gap-3 bg-white px-3 py-1.5 rounded-xl border border-slate-200 shadow-sm self-start sm:self-auto">
        <button @click="handlePrevMonth" class="p-1 hover:bg-slate-100 rounded-lg text-slate-500">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
        </button>
        <input 
          type="month" 
          v-model="selectedMonth" 
          class="font-semibold text-slate-700 bg-transparent outline-none cursor-pointer"
        />
        <button @click="handleNextMonth" class="p-1 hover:bg-slate-100 rounded-lg text-slate-500">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
        </button>
      </div>
    </header>

    <div class="rounded-3xl border border-white/70 bg-white/80 p-5 shadow-[0_24px_80px_rgba(15,23,42,0.06)] backdrop-blur sm:p-8 space-y-8">
        
        <!-- Toggle Income/Expense -->
        <div class="flex p-1 bg-slate-100 rounded-xl">
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
          
          <div v-if="loading" class="h-64 flex justify-center items-center">
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
          <div v-if="loading" class="h-48 flex justify-center items-center">
            <span class="animate-spin h-8 w-8 border-4 border-sky-600 border-t-transparent rounded-full"></span>
          </div>
          <div v-else-if="categoryData.data.length === 0" class="text-center py-8">
            <p class="text-slate-400">Tidak ada data di bulan ini.</p>
          </div>
          <div v-else class="flex flex-col sm:flex-row items-center gap-8">
            
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
    </div>
  </div>
</template>
