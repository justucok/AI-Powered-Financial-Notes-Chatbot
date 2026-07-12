<script setup>
import { computed, onMounted, ref, watch } from 'vue'

import { formatRupiah } from '../utils/formatters'
import { useFundSources } from '../composables/useFundSources'
import { useCategories } from '../composables/useCategories'

const props = defineProps({
  createTransaction: {
    type: Function,
    required: true,
  },
})

const emit = defineEmits({
  'transaction-added': (payload) => payload && typeof payload === 'object',
})

const { sources: fundSources, fetchSources } = useFundSources()
const { categories: allCategories, fetchCategories } = useCategories()

onMounted(async () => {
  await Promise.all([
    fetchSources(),
    fetchCategories()
  ])
})

const today = new Date().toISOString().split('T')[0]

const type = ref('expense')
const amount = ref('')
const category = ref('')
const description = ref('')
const date = ref(today)
const fundSourceId = ref('')
const submitting = ref(false)
const successVisible = ref(false)
const errors = ref({
  amount: '',
  category: '',
  fundSourceId: '',
})

const categoryOptions = computed(() =>
  allCategories.value.filter(c => c.type === type.value).map(c => ({
    label: `${c.icon || '🏷️'} ${c.name}`,
    value: c.name
  }))
)

watch(type, () => {
  category.value = ''
  resetErrors()
})

function resetErrors() {
  errors.value = {
    amount: '',
    category: '',
    fundSourceId: '',
  }
}

function resetForm() {
  amount.value = ''
  category.value = ''
  description.value = ''
  date.value = today
  fundSourceId.value = fundSources.value.length ? fundSources.value[0].id : ''
  resetErrors()
}

function validateForm() {
  resetErrors()
  let isValid = true

  if (!amount.value || Number(amount.value) <= 0) {
    errors.value.amount = 'Nominal transaksi wajib diisi dan lebih besar dari 0.'
    isValid = false
  }

  if (!category.value) {
    errors.value.category = 'Pilih salah satu kategori transaksi.'
    isValid = false
  }

  if (!fundSourceId.value) {
    errors.value.fundSourceId = 'Sumber uang wajib dipilih.'
    isValid = false
  }

  return isValid
}

async function handleSubmit() {
  if (!validateForm() || submitting.value) {
    return
  }

  submitting.value = true
  successVisible.value = false

  try {
    const payload = {
      type: type.value,
      amount: Number(amount.value),
      category: category.value,
      description: description.value.trim() || null,
      date: date.value,
      fund_source_id: fundSourceId.value,
    }

    const result = await props.createTransaction(payload)
    emit('transaction-added', result)
    resetForm()
    successVisible.value = true

    window.setTimeout(() => {
      successVisible.value = false
    }, 2200)
  } catch (error) {
    console.error('Failed to create transaction:', error)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="px-4 py-6 md:p-8 space-y-6">
    <header class="flex flex-col gap-1">
      <p class="text-xs font-semibold uppercase tracking-[0.28em] text-emerald-600">Catat Keuangan</p>
      <h1 class="text-2xl font-bold tracking-tight text-slate-900">Tambah Transaksi</h1>
      <p class="text-sm text-slate-500">Catat pemasukan atau pengeluaran Anda secara instan dan manual.</p>
    </header>

    <div class="rounded-3xl border border-white/70 bg-white/80 p-5 shadow-[0_24px_80px_rgba(15,23,42,0.06)] backdrop-blur sm:p-8">
      <!-- Success Banner -->
      <Transition
        enter-active-class="transition duration-300 ease-out"
        enter-from-class="transform scale-95 opacity-0"
        enter-to-class="transform scale-100 opacity-100"
        leave-active-class="transition duration-200 ease-in"
        leave-from-class="transform scale-100 opacity-100"
        leave-to-class="transform scale-95 opacity-0"
      >
        <div v-if="successVisible" class="mb-6 flex items-center justify-center gap-2 rounded-2xl bg-emerald-50 px-4 py-3 text-center text-sm font-semibold text-emerald-800 ring-1 ring-emerald-200">
          <span>✅</span> Transaksi berhasil disimpan!
        </div>
      </Transition>

      <form class="space-y-6" @submit.prevent="handleSubmit">
        <!-- Type Selection (Toggle Buttons) -->
        <div class="space-y-2">
          <label class="text-xs font-semibold uppercase tracking-wider text-slate-400">Jenis Transaksi</label>
          <div class="grid grid-cols-2 gap-3">
            <button
              type="button"
              :class="[
                'h-14 rounded-2xl text-sm font-bold tracking-wide transition-all duration-200 ring-4',
                type === 'expense'
                  ? 'bg-rose-50 text-rose-700 ring-rose-100 border border-rose-200'
                  : 'bg-slate-50 text-slate-600 ring-transparent border border-slate-100 hover:bg-slate-100',
              ]"
              @click="type = 'expense'"
            >
              💸 Pengeluaran
            </button>
            <button
              type="button"
              :class="[
                'h-14 rounded-2xl text-sm font-bold tracking-wide transition-all duration-200 ring-4',
                type === 'income'
                  ? 'bg-emerald-50 text-emerald-700 ring-emerald-100 border border-emerald-200'
                  : 'bg-slate-50 text-slate-600 ring-transparent border border-slate-100 hover:bg-slate-100',
              ]"
              @click="type = 'income'"
            >
              📈 Pemasukan
            </button>
          </div>
        </div>

        <!-- Amount Input with Real-time Formatting Preview -->
        <div class="space-y-2">
          <label for="input-amount" class="text-xs font-semibold uppercase tracking-wider text-slate-400">Nominal Transaksi (Rp)</label>
          <div class="relative">
            <span class="absolute left-4 top-1/2 -translate-y-1/2 text-lg font-semibold text-slate-400">Rp</span>
            <input
              id="input-amount"
              v-model="amount"
              type="number"
              inputmode="numeric"
              pattern="[0-9]*"
              required
              min="1"
              step="1000"
              placeholder="0"
              class="h-14 w-full rounded-2xl border border-slate-200 bg-white pl-12 pr-4 text-lg font-bold text-slate-800 outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10"
            >
          </div>
          <p v-if="amount" class="text-xs font-semibold text-emerald-600 pl-1">
            Format: {{ formatRupiah(amount) }}
          </p>
          <p v-if="errors.amount" class="text-xs text-rose-600 pl-1">
            {{ errors.amount }}
          </p>
        </div>

        <!-- Category Grid (Touch-friendly Pill Grid) -->
        <div class="space-y-2">
          <label class="text-xs font-semibold uppercase tracking-wider text-slate-400">Pilih Kategori</label>
          <div class="grid grid-cols-2 gap-2 sm:grid-cols-4">
            <button
              v-for="cat in categoryOptions"
              :key="cat.value"
              type="button"
              :class="[
                'flex h-12 items-center justify-center rounded-xl text-xs font-semibold transition-all duration-200 border',
                category === cat.value
                  ? 'bg-slate-900 border-slate-900 text-white shadow-md'
                  : 'bg-white border-slate-200 text-slate-600 hover:border-slate-300 hover:bg-slate-50',
              ]"
              @click="category = cat.value"
            >
              {{ cat.label }}
            </button>
          </div>
          <p v-if="errors.category" class="text-xs text-rose-600 pl-1">
            {{ errors.category }}
          </p>
        </div>

        <!-- Description (Optional) -->
        <div class="space-y-2">
          <label for="input-desc" class="text-xs font-semibold uppercase tracking-wider text-slate-400">Deskripsi (Opsional)</label>
          <input
            id="input-desc"
            v-model="description"
            type="text"
            placeholder="Contoh: Makan siang di warung kopi"
            class="h-12 w-full rounded-2xl border border-slate-200 bg-white px-4 text-sm text-slate-700 outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10"
          >
        </div>

        <!-- Date Selection -->
        <div class="space-y-2">
          <label for="input-date" class="text-xs font-semibold uppercase tracking-wider text-slate-400">Tanggal Transaksi</label>
          <input
            id="input-date"
            v-model="date"
            type="date"
            required
            class="h-12 w-full rounded-2xl border border-slate-200 bg-white px-4 text-sm text-slate-700 outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10"
          >
        </div>

        <!-- Fund Source Selection -->
        <div v-if="fundSources.length > 0" class="space-y-2">
          <label for="input-source" class="text-xs font-semibold uppercase tracking-wider text-slate-400">Sumber Uang</label>
          <select
            id="input-source"
            v-model="fundSourceId"
            required
            class="h-12 w-full rounded-2xl border border-slate-200 bg-white px-4 text-sm text-slate-700 outline-none transition focus:border-emerald-500 focus:ring-4 focus:ring-emerald-500/10"
          >
            <option value="" disabled>-- Pilih Sumber Uang --</option>
            <option v-for="source in fundSources" :key="source.id" :value="source.id">
              {{ source.icon || '💰' }} {{ source.name }} ({{ formatRupiah(source.balance) }})
            </option>
          </select>
          <p v-if="errors.fundSourceId" class="text-xs text-rose-600 pl-1">
            {{ errors.fundSourceId }}
          </p>
        </div>

        <!-- Submit Button -->
        <button
          type="submit"
          :disabled="submitting"
          class="flex h-14 w-full items-center justify-center rounded-2xl bg-emerald-600 text-sm font-bold tracking-wide text-white shadow-lg shadow-emerald-600/20 transition hover:bg-emerald-500 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-60"
        >
          <span v-if="submitting" class="flex items-center gap-2">
            <span class="spinner-icon" /> Menyimpan...
          </span>
          <span v-else>Simpan Transaksi</span>
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.spinner-icon {
  display: inline-block;
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 9999px;
  animation: spin 0.7s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
.hide-scrollbar::-webkit-scrollbar {
  display: none;
}
.hide-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
