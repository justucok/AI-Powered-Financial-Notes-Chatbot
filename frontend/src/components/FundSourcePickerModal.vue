<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useCategories } from '../composables/useCategories'

const props = defineProps({
  show: Boolean,
  pendingTransactions: {
    type: Array,
    default: () => [],
  },
  fundSources: {
    type: Array,
    default: () => [],
  },
  isLoading: Boolean,
})

const emit = defineEmits(['close', 'confirm'])

const editableTransactions = ref([])
const { categories: allCategories, fetchCategories } = useCategories()

onMounted(() => {
  fetchCategories()
})

const filteredCategories = computed(() => {
  return (type) => {
    if (!allCategories.value || allCategories.value.length === 0) {
      if (type === 'income') {
        return [{name:'Gaji'},{name:'Freelance'},{name:'Investasi'},{name:'Lainnya'}]
      } else {
        return [{name:'Makanan'},{name:'Transport'},{name:'Belanja'},{name:'Kesehatan'},{name:'Hiburan'},{name:'Lainnya'}]
      }
    }
    return allCategories.value.filter(c => c.type === type)
  }
})

function handleTypeChange(tx) {
  const isValid = filteredCategories.value(tx.type).some(c => c.name === tx.category)
  if (!isValid) {
    tx.category = ''
  }
}

function initSelections() {
  editableTransactions.value = props.pendingTransactions.map(tx => ({
    ...tx
  }))
}

watch(() => props.pendingTransactions, () => {
  if (props.show) {
    initSelections()
  }
}, { immediate: true })

watch(() => props.show, (newShow) => {
  if (newShow) {
    initSelections()
  }
})

const canConfirm = computed(() => {
  const needsSource = props.fundSources.length > 0
  return editableTransactions.value.every(tx => {
    const hasBasic = tx.type && tx.amount > 0 && tx.category && tx.date
    if (needsSource) {
      return hasBasic && tx.fund_source_id != null
    }
    return hasBasic
  })
})

function handleConfirm() {
  emit('confirm', editableTransactions.value)
}
</script>

<template>
  <div v-if="show" class="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
    <div class="bg-white rounded-2xl w-full max-w-lg shadow-2xl flex flex-col max-h-[90vh]">
      
      <div class="p-6 border-b border-gray-100 shrink-0">
        <h3 class="text-xl font-bold text-gray-900">Konfirmasi Transaksi</h3>
        <p class="text-sm text-gray-500 mt-1">Pastikan detail transaksi berikut sudah benar sebelum disimpan.</p>
      </div>

      <div class="p-6 overflow-y-auto flex-1 space-y-6">
        <div v-for="(tx, idx) in editableTransactions" :key="idx" class="bg-gray-50 p-4 rounded-xl border border-gray-100 space-y-4">
          
          <div class="flex gap-4">
            <div class="flex-1">
              <label class="block text-xs font-medium text-gray-700 mb-1">Jenis Transaksi</label>
              <select v-model="tx.type" @change="handleTypeChange(tx)" class="w-full text-sm rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
                <option value="expense">Pengeluaran</option>
                <option value="income">Pemasukan</option>
              </select>
            </div>
            <div class="flex-1">
              <label class="block text-xs font-medium text-gray-700 mb-1">Tanggal</label>
              <input type="date" v-model="tx.date" class="w-full text-sm rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
            </div>
          </div>
          
          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">Nominal (Rp)</label>
            <input type="number" v-model="tx.amount" min="1" class="w-full text-sm rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
          </div>

          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">Kategori</label>
            <select v-model="tx.category" class="w-full text-sm rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
              <option value="" disabled>Pilih kategori</option>
              <option v-for="cat in filteredCategories(tx.type)" :key="cat.name" :value="cat.name">{{ cat.name }}</option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">Deskripsi</label>
            <input type="text" v-model="tx.description" placeholder="Opsional" class="w-full text-sm rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
          </div>

          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">Sumber Uang</label>
            <select v-model="tx.fund_source_id" 
                    :disabled="fundSources.length === 0"
                    class="w-full text-sm rounded-lg border-gray-300 bg-white text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500">
              <option :value="undefined" disabled>-- Pilih Sumber Uang --</option>
              <option v-if="fundSources.length === 0" disabled>Belum ada sumber uang terdaftar</option>
              <option v-for="source in fundSources" :key="source.id" :value="source.id">
                {{ source.icon || '💰' }} {{ source.name }}
              </option>
            </select>
          </div>

        </div>
      </div>

      <div class="p-6 border-t border-gray-100 flex justify-end space-x-3 bg-gray-50 rounded-b-2xl shrink-0">
        <button type="button" @click="$emit('close')" :disabled="isLoading"
                class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50">
          Batal
        </button>
        <button type="button" @click="handleConfirm" :disabled="!canConfirm || isLoading"
                class="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-lg shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50">
          <span v-if="isLoading" class="animate-spin mr-2 h-4 w-4 border-2 border-white border-t-transparent rounded-full"></span>
          Simpan Transaksi
        </button>
      </div>

    </div>
  </div>
</template>
