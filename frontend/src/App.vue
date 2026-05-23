<script setup>
import SummaryCards from './components/SummaryCards.vue'
</script>

<template>
  <main class="min-h-screen px-4 py-8 sm:px-6 lg:px-10">
    <section class="mx-auto max-w-6xl">
      <div class="mb-8 rounded-[2rem] border border-white/70 bg-white/70 p-6 shadow-[0_24px_80px_rgba(15,23,42,0.08)] backdrop-blur">
        <p class="mb-2 text-xs font-semibold uppercase tracking-[0.3em] text-sky-600">
          AI Financial Notes
        </p>
        <h1 class="text-3xl font-semibold tracking-tight text-slate-900 sm:text-4xl">
          Dashboard ringkas untuk memantau saldo, pemasukan, dan pengeluaran.
        </h1>
        <p class="mt-3 max-w-2xl text-sm leading-6 text-slate-600 sm:text-base">
          Frontend Vue 3 + Vite ini disusun dengan separation of concerns yang ketat:
          komponen presentational tetap bersih, logic API berada di service layer, dan utilitas
          formatter dipisahkan agar mudah dirawat.
        </p>
      </div>

      <SummaryCards :balance="4750000" :income="7200000" :expense="2450000" />
    </section>
  </main>
</template>
