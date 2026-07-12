<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useCategories } from '../composables/useCategories'

const props = defineProps({
  show: Boolean,
  transaction: Object,
  fundSources: Array,
  isLoading: Boolean
})

const emit = defineEmits(['close', 'confirm'])

const formData = ref({})
const { categories: allCategories, fetchCategories } = useCategories()

onMounted(() => {
  fetchCategories()
})

watch(() => props.show, (isShowing) => {
  if (isShowing && props.transaction) {
    formData.value = { ...props.transaction }
  }
})

watch(() => formData.value.type, (newType, oldType) => {
  if (oldType && newType !== oldType) {
    const isValid = filteredCategories.value.some(c => c.name === formData.value.category)
    if (!isValid) {
      formData.value.category = ''
    }
  }
})

const filteredCategories = computed(() => {
  if (!allCategories.value || allCategories.value.length === 0) {
    if (formData.value.type === 'income') {
      return [{name:'Gaji'},{name:'Freelance'},{name:'Investasi'},{name:'Lainnya'}]
    } else {
      return [{name:'Makanan'},{name:'Transport'},{name:'Belanja'},{name:'Kesehatan'},{name:'Hiburan'},{name:'Lainnya'}]
    }
  }
  return allCategories.value.filter(c => c.type === formData.value.type)
})

function handleSubmit() {
  // Ensure amount is number
  formData.value.amount = Number(formData.value.amount)
  emit('confirm', formData.value)
}
</script>

<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-end justify-center sm:items-center">
    <div class="fixed inset-0 bg-slate-900/50 backdrop-blur-sm transition-opacity" @click="$emit('close')"></div>
    <div class="relative w-full sm:max-w-lg overflow-hidden rounded-t-[2rem] sm:rounded-3xl bg-white shadow-2xl transition-all h-[90vh] sm:h-auto flex flex-col">
      <!-- Header -->
      <div class="bg-slate-50 px-6 py-4 border-b border-slate-100 flex items-center justify-between shrink-0">
        <h3 class="text-lg font-bold text-slate-800">Ubah Transaksi</h3>
        <button @click="$emit('close')" class="text-slate-400 hover:text-slate-600 transition-colors">
          ✕
        </button>
      </div>

      <!-- Content -->
      <div class="p-6 overflow-y-auto flex-1">
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <!-- Type -->
          <div class="grid grid-cols-2 gap-3">
            <label :class="['flex items-center justify-center p-3 rounded-xl border-2 cursor-pointer transition-all', formData.type === 'expense' ? 'border-red-500 bg-red-50 text-red-700 font-bold' : 'border-slate-200 text-slate-500 hover:border-slate-300']">
              <input type="radio" v-model="formData.type" value="expense" class="hidden">
              PENGELUARAN
            </label>
            <label :class="['flex items-center justify-center p-3 rounded-xl border-2 cursor-pointer transition-all', formData.type === 'income' ? 'border-emerald-500 bg-emerald-50 text-emerald-700 font-bold' : 'border-slate-200 text-slate-500 hover:border-slate-300']">
              <input type="radio" v-model="formData.type" value="income" class="hidden">
              PEMASUKAN
            </label>
          </div>

          <!-- Date -->
          <div>
            <label class="block text-xs font-medium text-slate-700 mb-1">Tanggal</label>
            <input type="date" v-model="formData.date" required class="w-full text-sm rounded-lg border-slate-300 shadow-sm focus:border-sky-500 focus:ring-sky-500">
          </div>

          <!-- Amount -->
          <div>
            <label class="block text-xs font-medium text-slate-700 mb-1">Jumlah</label>
            <div class="relative">
              <span class="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-500">Rp</span>
              <input type="number" v-model="formData.amount" required min="0" class="w-full pl-10 text-sm rounded-lg border-slate-300 shadow-sm focus:border-sky-500 focus:ring-sky-500">
            </div>
          </div>

          <!-- Category -->
          <div>
            <label class="block text-xs font-medium text-slate-700 mb-1">Kategori</label>
            <select v-model="formData.category" required class="w-full text-sm rounded-lg border-slate-300 shadow-sm focus:border-sky-500 focus:ring-sky-500">
              <option value="" disabled>Pilih kategori</option>
              <option v-for="cat in filteredCategories" :key="cat.name" :value="cat.name">{{ cat.name }}</option>
            </select>
          </div>

          <!-- Description -->
          <div>
            <label class="block text-xs font-medium text-slate-700 mb-1">Deskripsi</label>
            <input type="text" v-model="formData.description" placeholder="Opsional" class="w-full text-sm rounded-lg border-slate-300 shadow-sm focus:border-sky-500 focus:ring-sky-500">
          </div>

          <!-- Fund Source -->
          <div>
            <label class="block text-xs font-medium text-slate-700 mb-1">Sumber Uang</label>
            <select v-model="formData.fund_source_id" 
                    :disabled="fundSources.length === 0"
                    class="w-full text-sm rounded-lg border-slate-300 shadow-sm focus:border-sky-500 focus:ring-sky-500">
              <option :value="undefined" disabled>-- Pilih Sumber Uang --</option>
              <option v-if="fundSources.length === 0" disabled>Belum ada sumber uang terdaftar</option>
              <option v-for="source in fundSources" :key="source.id" :value="source.id">
                {{ source.icon || '💰' }} {{ source.name }}
              </option>
            </select>
          </div>
        </form>
      </div>

      <!-- Footer -->
      <div class="bg-slate-50 px-6 py-4 border-t border-slate-100 flex justify-end gap-3 shrink-0">
        <button type="button" @click="$emit('close')" :disabled="isLoading" class="px-5 py-2.5 text-sm font-semibold text-slate-700 bg-white border border-slate-300 rounded-xl hover:bg-slate-50 transition-colors disabled:opacity-50">
          Batal
        </button>
        <button type="button" @click="handleSubmit" :disabled="isLoading" class="px-5 py-2.5 text-sm font-semibold text-white bg-sky-600 rounded-xl hover:bg-sky-500 transition-colors shadow-sm disabled:opacity-50">
          {{ isLoading ? 'Menyimpan...' : 'Simpan Perubahan' }}
        </button>
      </div>
    </div>
  </div>
</template>
