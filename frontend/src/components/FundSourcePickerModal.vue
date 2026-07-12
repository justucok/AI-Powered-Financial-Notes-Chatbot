<script setup>
import { computed, ref } from 'vue'
import { formatRupiah } from '../utils/formatters'

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

// Track selected fund source for each transaction index
const selectedSources = ref({})

// Initialize selections based on matched_fund_source_id if available
function initSelections() {
  selectedSources.value = {}
  props.pendingTransactions.forEach((tx, idx) => {
    if (tx.fund_source_id) {
      selectedSources.value[idx] = tx.fund_source_id
    }
  })
}

// Watch for changes in pendingTransactions to re-initialize
import { watch } from 'vue'
watch(() => props.pendingTransactions, () => {
  initSelections()
}, { immediate: true })

const canConfirm = computed(() => {
  return props.pendingTransactions.every((tx, idx) => selectedSources.value[idx] != null)
})

function handleConfirm() {
  const confirmedTransactions = props.pendingTransactions.map((tx, idx) => ({
    ...tx,
    fund_source_id: selectedSources.value[idx],
  }))
  emit('confirm', confirmedTransactions)
}
</script>

<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
    <div class="bg-white rounded-2xl w-full max-w-md shadow-2xl flex flex-col max-h-[90vh]">
      
      <!-- Header -->
      <div class="p-6 border-b border-gray-100">
        <h3 class="text-xl font-bold text-gray-900">Pilih Sumber Uang</h3>
        <p class="text-sm text-gray-500 mt-1">Sistem mendeteksi transaksi, mohon pilih sumber uang yang digunakan.</p>
      </div>

      <!-- Body: Scrollable list of transactions -->
      <div class="p-6 overflow-y-auto flex-1 space-y-6">
        <div v-for="(tx, idx) in pendingTransactions" :key="idx" class="bg-gray-50 p-4 rounded-xl border border-gray-100">
          
          <div class="flex justify-between items-start mb-3">
            <div>
              <span class="inline-block px-2 py-1 text-xs font-medium rounded-full mb-2"
                    :class="tx.type === 'income' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'">
                {{ tx.type === 'income' ? 'Pemasukan' : 'Pengeluaran' }}
              </span>
              <p class="font-medium text-gray-900">{{ tx.description || 'Tanpa deskripsi' }}</p>
              <p class="text-sm text-gray-500">{{ tx.category }}</p>
            </div>
            <p class="font-bold whitespace-nowrap" :class="tx.type === 'income' ? 'text-green-600' : 'text-red-600'">
              {{ tx.type === 'income' ? '+' : '-' }}{{ formatRupiah(tx.amount) }}
            </p>
          </div>

          <!-- Fund Source Selector -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Sumber Uang</label>
            <select v-model="selectedSources[idx]" 
                    class="w-full rounded-lg border-gray-300 bg-white text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500">
              <option :value="undefined" disabled>-- Pilih Sumber Uang --</option>
              <option v-for="source in fundSources" :key="source.id" :value="source.id">
                {{ source.icon || '💰' }} {{ source.name }}
              </option>
            </select>
          </div>

        </div>
      </div>

      <!-- Footer -->
      <div class="p-6 border-t border-gray-100 flex justify-end space-x-3 bg-gray-50 rounded-b-2xl">
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
