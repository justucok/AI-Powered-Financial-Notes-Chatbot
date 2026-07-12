<script setup>
import { ref, onMounted } from 'vue'
import ChatBox from './ChatBox.vue'
import FundSourcePickerModal from './FundSourcePickerModal.vue'
import { useGlobalChat } from '../composables/useGlobalChat'
import { useFundSources } from '../composables/useFundSources'
import { confirmTransactions as confirmTransactionsApi } from '../services/api'

const { isChatOpen, toggleChat } = useGlobalChat()
const { sources: fundSources, fetchSources } = useFundSources()
const emit = defineEmits(['transaction-added'])

const showFundSourceModal = ref(false)
const pendingTransactions = ref([])
const isConfirming = ref(false)

onMounted(() => fetchSources())

function handleTransactionAdded(data) {
  fetchSources()
  emit('transaction-added', data)
}

function handleRequiresFundSource(pending) {
  pendingTransactions.value = pending
  showFundSourceModal.value = true
}

async function handleConfirmTransactions(confirmed) {
  isConfirming.value = true
  try {
    await confirmTransactionsApi({ transactions: confirmed })
    handleTransactionAdded()
    showFundSourceModal.value = false
    pendingTransactions.value = []
  } finally {
    isConfirming.value = false
  }
}
</script>

<template>
  <div>
    <!-- Chat Panel -->
    <Transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="transform translate-y-8 opacity-0 scale-95"
      enter-to-class="transform translate-y-0 opacity-100 scale-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="transform translate-y-0 opacity-100 scale-100"
      leave-to-class="transform translate-y-8 opacity-0 scale-95"
    >
      <div 
        v-if="isChatOpen" 
        class="fixed bottom-24 right-4 sm:right-6 z-[60] w-[calc(100vw-2rem)] sm:w-[400px] xl:w-[440px] shadow-2xl rounded-[2rem] bg-white border border-slate-100"
      >
        <ChatBox
          :fund-sources="fundSources"
          @transaction-added="handleTransactionAdded"
          @requires-fund-source="handleRequiresFundSource"
          class="h-[600px] max-h-[calc(100vh-8rem)] flex flex-col !shadow-none !border-0"
        />
      </div>
    </Transition>

    <!-- FAB Bubble Button -->
    <button 
      @click="toggleChat" 
      class="fixed bottom-6 right-4 sm:right-6 z-[61] flex h-14 w-14 items-center justify-center rounded-full bg-sky-600 text-white shadow-lg shadow-sky-600/40 border-4 border-white transition active:scale-95 hover:bg-sky-500"
    >
      <span v-if="!isChatOpen" class="text-2xl">🤖</span>
      <span v-else class="text-2xl">✕</span>
    </button>

    <!-- Fund Source Modal (global) -->
    <FundSourcePickerModal
      :show="showFundSourceModal"
      :pending-transactions="pendingTransactions"
      :fund-sources="fundSources"
      :is-loading="isConfirming"
      @close="showFundSourceModal = false"
      @confirm="handleConfirmTransactions"
    />
  </div>
</template>
