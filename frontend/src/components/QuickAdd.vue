<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  createTransaction: {
    type: Function,
    required: true,
  },
  fundSources: {
    type: Array,
    default: () => [],
  }
})

import { useCategories } from '../composables/useCategories'

const { categories: allCategories, fetchCategories } = useCategories()

import { onMounted } from 'vue'
onMounted(() => {
  fetchCategories()
})

const emit = defineEmits({
  'transaction-added': (payload) => payload && typeof payload === 'object',
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
  type: '',
  amount: '',
  category: '',
  fundSourceId: '',
})

const categoryOptions = computed(() => {
  return allCategories.value.filter(c => c.type === type.value).map(c => ({
    label: `${c.icon || '🏷️'} ${c.name}`,
    value: c.name
  }))
})

const categoryPlaceholder = computed(() =>
  type.value === 'income' ? 'Contoh: Gaji' : 'Contoh: Makanan'
)

watch(type, () => {
  category.value = ''
  resetErrors()
})

watch(() => props.fundSources, (sources) => {
  if (sources && sources.length > 0 && !fundSourceId.value) {
    fundSourceId.value = sources[0].id
  }
}, { immediate: true })

function resetErrors() {
  errors.value = {
    type: '',
    amount: '',
    category: '',
    fundSourceId: '',
  }
}

function resetForm() {
  type.value = 'expense'
  amount.value = ''
  category.value = ''
  description.value = ''
  date.value = today
  fundSourceId.value = props.fundSources?.length ? props.fundSources[0].id : ''
}

function validateForm() {
  resetErrors()
  let isValid = true

  if (!type.value) {
    errors.value.type = 'Jenis transaksi wajib dipilih.'
    isValid = false
  }

  if (!amount.value || Number(amount.value) <= 0) {
    errors.value.amount = 'Jumlah wajib diisi dan harus lebih dari 0.'
    isValid = false
  }

  if (!category.value.trim()) {
    errors.value.category = 'Kategori wajib diisi.'
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
      category: category.value.trim(),
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
  <section class="rounded-[2rem] border border-white/70 bg-white/80 p-5 shadow-[0_24px_80px_rgba(15,23,42,0.08)] backdrop-blur sm:p-6">
    <div class="mb-5 flex items-center justify-between gap-4">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.28em] text-emerald-600">
          Quick Add
        </p>
        <h2 class="mt-1 text-xl font-semibold text-slate-900">
          Tambah transaksi manual
        </h2>
      </div>
      <span
        :class="[
          'rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-700 transition-opacity duration-300',
          successVisible ? 'opacity-100' : 'opacity-0',
        ]"
      >
        Transaksi berhasil ditambahkan
      </span>
    </div>

    <form class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-5" @submit.prevent="handleSubmit">
      <label class="space-y-2">
        <span class="text-sm font-medium text-slate-700">Jenis</span>
        <select
          v-model="type"
          class="h-12 w-full rounded-2xl border border-slate-200 bg-white px-4 text-sm text-slate-700 outline-none transition focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100"
        >
          <option value="expense">
            Expense
          </option>
          <option value="income">
            Income
          </option>
        </select>
        <p v-if="errors.type" class="text-xs text-rose-600">
          {{ errors.type }}
        </p>
      </label>

      <label class="space-y-2">
        <span class="text-sm font-medium text-slate-700">Jumlah</span>
        <input
          v-model="amount"
          type="number"
          min="0"
          step="1000"
          placeholder="50000"
          class="h-12 w-full rounded-2xl border border-slate-200 bg-white px-4 text-sm text-slate-700 outline-none transition focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100"
        >
        <p v-if="errors.amount" class="text-xs text-rose-600">
          {{ errors.amount }}
        </p>
      </label>

      <label class="space-y-2">
        <span class="text-sm font-medium text-slate-700">Kategori</span>
        <input
          v-model="category"
          list="quick-add-categories"
          type="text"
          :placeholder="categoryPlaceholder"
          class="h-12 w-full rounded-2xl border border-slate-200 bg-white px-4 text-sm text-slate-700 outline-none transition focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100"
        >
        <datalist id="quick-add-categories">
          <option v-for="cat in categoryOptions" :key="cat.value" :value="cat.value">
            {{ cat.label }}
          </option>
        </datalist>
        <p v-if="errors.category" class="text-xs text-rose-600">
          {{ errors.category }}
        </p>
      </label>

      <label class="space-y-2">
        <span class="text-sm font-medium text-slate-700">Deskripsi</span>
        <input
          v-model="description"
          type="text"
          placeholder="Contoh: makan siang"
          class="h-12 w-full rounded-2xl border border-slate-200 bg-white px-4 text-sm text-slate-700 outline-none transition focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100"
        >
      </label>

      <label class="space-y-2">
        <span class="text-sm font-medium text-slate-700">Tanggal</span>
        <input
          v-model="date"
          type="date"
          class="h-12 w-full rounded-2xl border border-slate-200 bg-white px-4 text-sm text-slate-700 outline-none transition focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100"
        >
      </label>

      <label class="space-y-2">
        <span class="text-sm font-medium text-slate-700">Sumber Uang</span>
        <select
          v-model="fundSourceId"
          class="h-12 w-full rounded-2xl border border-slate-200 bg-white px-4 text-sm text-slate-700 outline-none transition focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100"
        >
          <option value="" disabled>Pilih Sumber Uang</option>
          <option v-for="source in fundSources" :key="source.id" :value="source.id">
            {{ source.icon }} {{ source.name }}
          </option>
        </select>
        <p v-if="errors.fundSourceId" class="text-xs text-rose-600">
          {{ errors.fundSourceId }}
        </p>
      </label>

      <div class="md:col-span-2 xl:col-span-1 flex items-end">
        <button
          type="submit"
          :disabled="submitting"
          class="h-12 w-full inline-flex items-center justify-center rounded-2xl bg-emerald-600 px-5 text-sm font-semibold text-white transition hover:bg-emerald-500 disabled:cursor-not-allowed disabled:bg-emerald-300"
        >
          {{ submitting ? 'Menyimpan...' : 'Tambah' }}
        </button>
      </div>
    </form>
  </section>
</template>
