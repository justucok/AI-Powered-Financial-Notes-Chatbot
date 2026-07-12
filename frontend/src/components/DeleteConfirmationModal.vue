<script setup>
const props = defineProps({
  show: Boolean,
  isLoading: Boolean
})

const emit = defineEmits(['close', 'confirm'])
</script>

<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <div class="fixed inset-0 bg-slate-900/50 backdrop-blur-sm transition-opacity" @click="!isLoading && $emit('close')"></div>
    <div class="relative w-full max-w-sm overflow-hidden rounded-3xl bg-white shadow-2xl transition-all flex flex-col transform">
      <div class="p-6 text-center">
        <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-red-100 mb-4">
          <span class="text-2xl">🗑️</span>
        </div>
        <h3 class="text-lg font-bold text-slate-800 mb-2">Hapus Transaksi?</h3>
        <p class="text-sm text-slate-500">
          Apakah Anda yakin ingin menghapus transaksi ini? Tindakan ini tidak dapat dibatalkan.
        </p>
      </div>
      <div class="bg-slate-50 px-6 py-4 border-t border-slate-100 flex justify-center gap-3 shrink-0">
        <button type="button" @click="$emit('close')" :disabled="isLoading" class="flex-1 px-5 py-2.5 text-sm font-semibold text-slate-700 bg-white border border-slate-300 rounded-xl hover:bg-slate-50 transition-colors disabled:opacity-50">
          Batal
        </button>
        <button type="button" @click="$emit('confirm')" :disabled="isLoading" class="flex-1 px-5 py-2.5 text-sm font-semibold text-white bg-red-600 rounded-xl hover:bg-red-500 transition-colors shadow-sm disabled:opacity-50">
          {{ isLoading ? 'Menghapus...' : 'Ya, Hapus' }}
        </button>
      </div>
    </div>
  </div>
</template>
