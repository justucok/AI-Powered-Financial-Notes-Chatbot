<script setup>
import { formatRupiah } from '../utils/formatters'

defineProps({
  balance: Number,
  income: Number,
  expense: Number,
})

const cards = [
  {
    key: 'balance',
    label: 'Balance',
    tone: 'from-sky-500 via-blue-500 to-cyan-400',
    ring: 'ring-sky-200/70',
    glow: 'shadow-[0_22px_70px_rgba(14,116,244,0.22)]',
  },
  {
    key: 'income',
    label: 'Income',
    tone: 'from-emerald-500 via-green-500 to-lime-400',
    ring: 'ring-emerald-200/70',
    glow: 'shadow-[0_22px_70px_rgba(16,185,129,0.18)]',
  },
  {
    key: 'expense',
    label: 'Expense',
    tone: 'from-rose-500 via-red-500 to-orange-400',
    ring: 'ring-rose-200/70',
    glow: 'shadow-[0_22px_70px_rgba(244,63,94,0.18)]',
  },
]
</script>

<template>
  <section class="grid grid-cols-2 gap-3 md:gap-5 md:grid-cols-3">
    <article
      v-for="card in cards"
      :key="card.key"
      :class="[
        'group relative overflow-hidden rounded-[1.25rem] md:rounded-[1.75rem] bg-white p-4 md:p-6 ring-1 transition-all duration-300 hover:-translate-y-1',
        card.ring,
        card.glow,
        card.key === 'balance' ? 'col-span-2 md:col-span-1' : 'col-span-1',
        card.key !== 'balance' ? 'cursor-pointer hover:bg-slate-50/50' : ''
      ]"
      @click="card.key !== 'balance' && $emit('card-click', card.key)"
    >
      <div
        :class="[
          'absolute inset-x-0 top-0 h-1.5 bg-gradient-to-r',
          card.tone,
        ]"
      />
      <div class="absolute -right-12 -top-14 h-28 w-28 rounded-full bg-slate-100/80 blur-2xl transition-transform duration-500 group-hover:scale-125" />

      <div class="relative">
        <p class="text-xs md:text-sm font-medium uppercase tracking-widest md:tracking-[0.24em] text-slate-500">
          {{ card.label }}
        </p>
        <p class="mt-2 md:mt-4 text-xl sm:text-2xl md:text-3xl font-semibold tracking-tight text-slate-900">
          {{
            formatRupiah(
              card.key === 'balance'
                ? balance
                : card.key === 'income'
                  ? income
                  : expense
            )
          }}
        </p>
        <p class="mt-3 text-sm leading-6 text-slate-600 hidden md:block">
          {{
            card.key === 'balance'
              ? 'Gambaran posisi keuangan saat ini setelah seluruh transaksi dihitung.'
              : card.key === 'income'
                ? 'Akumulasi pemasukan yang tercatat untuk periode yang sedang dipantau.'
                : 'Total pengeluaran yang sudah diklasifikasikan dari transaksi aktif.'
          }}
        </p>
      </div>
    </article>
  </section>
</template>
