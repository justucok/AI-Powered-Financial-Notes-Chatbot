# Frontend README

Frontend ini adalah antarmuka web untuk aplikasi **AI-Powered Financial Notes Chatbot**. Stack utamanya menggunakan **Vue 3**, **Vite**, **Tailwind CSS**, dan **Axios** untuk berkomunikasi dengan backend FastAPI.

Frontend menangani empat area utama:
- ringkasan keuangan bulanan
- chat AI untuk input transaksi teks dan gambar
- input transaksi manual
- riwayat transaksi dengan filter bulan

## Fitur

- Vue 3 dengan Composition API dan `<script setup>`
- Vite sebagai dev server dan bundler
- Tailwind CSS untuk styling utility-first
- Axios service layer terpusat
- Composable terpisah untuk logic chat dan transaksi
- Komponen presentational yang fokus pada UI

## Struktur Folder

```text
frontend/
├── index.html
├── package.json
├── vite.config.js
├── README.md
└── src/
    ├── App.vue
    ├── main.js
    ├── style.css
    ├── components/
    │   ├── ChatBox.vue
    │   ├── QuickAdd.vue
    │   ├── SummaryCards.vue
    │   └── TransactionHistory.vue
    ├── composables/
    │   ├── useChat.js
    │   └── useTransactions.js
    ├── services/
    │   └── api.js
    └── utils/
        └── formatters.js
```

## Arsitektur

Frontend ini mengikuti pemisahan tanggung jawab berikut:

- `components/`
  Komponen UI presentational. Fokus pada tampilan, props, dan emit.
- `composables/`
  Tempat state dan application logic reusable dengan Composition API.
- `services/`
  Tempat HTTP client dan semua API calls ke backend.
- `utils/`
  Pure utility functions seperti formatter tanggal dan Rupiah.
- `App.vue`
  Root orchestration component yang hanya menghubungkan composable dan komponen.

## Install Dependency

Jika belum meng-install dependency:

```bash
cd "Final Project - AI-Powered Financial Notes Chatbot/frontend"
npm install
```

## Menjalankan Frontend

Jalankan dev server:

```bash
cd "Final Project - AI-Powered Financial Notes Chatbot/frontend"
npm run dev
```

Setelah server aktif, Vite biasanya berjalan di:

- `http://localhost:5173`

## Konfigurasi Dev Server

File `vite.config.js` sudah dikonfigurasi dengan:

- `defineConfig`
- plugin Vue
- plugin Tailwind CSS untuk Vite
- proxy `/api` ke `http://localhost:8000`

Artinya request frontend seperti `/api/v1/chat` akan diteruskan ke backend FastAPI lokal.

## Cara Kerja Singkat

- `App.vue` memanggil `useTransactions()` saat `onMounted()`
- `SummaryCards.vue` menampilkan balance, income, dan expense
- `ChatBox.vue` memakai `useChat()` untuk mengirim chat teks dan gambar
- `QuickAdd.vue` dipakai untuk input transaksi manual
- `TransactionHistory.vue` menampilkan transaksi berdasarkan bulan yang dipilih
- saat transaksi baru ditambahkan atau dihapus, `fetchAll()` dipanggil ulang agar data tetap sinkron

## Integrasi API

Semua komunikasi API frontend dipusatkan di:

- `src/services/api.js`

Named functions yang tersedia:

- `getTransactions(month)`
- `createTransaction(data)`
- `deleteTransaction(id)`
- `getSummary(month)`
- `sendChat(message, history)`
- `sendChatImage(file)`

Base URL yang digunakan:

```text
/api
```

Dengan demikian endpoint backend yang dipanggil akan menjadi:

- `/api/v1/chat`
- `/api/v1/chat/image`
- `/api/v1/transactions`
- `/api/v1/summary`

## Komponen Utama

### `SummaryCards.vue`

Menampilkan tiga kartu:
- balance
- income
- expense

Komponen ini murni presentational dan hanya menerima props.

### `ChatBox.vue`

Menampilkan:
- bubble chat user dan bot
- input teks
- upload gambar
- image preview
- loading indicator

Logic chat seluruhnya berada di `useChat.js`.

### `QuickAdd.vue`

Form untuk menambahkan transaksi manual:
- type
- amount
- category
- description
- date

Komponen ini menerima function `createTransaction` dari parent dan emit `transaction-added` setelah sukses.

### `TransactionHistory.vue`

Menampilkan:
- dropdown bulan
- tabel transaksi
- loading skeleton
- empty state
- tombol hapus transaksi

## Composables

### `useChat.js`

Menangani:
- state pesan
- history untuk API
- loading state
- preview gambar
- kirim pesan teks
- kirim gambar

### `useTransactions.js`

Menangani:
- daftar transaksi
- ringkasan keuangan
- selected month
- fetch transaksi
- fetch summary
- create transaction
- delete transaction

## Utility Functions

File `src/utils/formatters.js` menyediakan:

- `formatRupiah(amount)`
- `formatDate(dateStr)`
- `formatMonth(monthStr)`

Semua fungsi bersifat pure dan tidak memiliki side effect.

## Dependency Utama

Isi `package.json` saat ini:

- `vue`
- `axios`
- `vite`
- `@vitejs/plugin-vue`
- `tailwindcss`
- `@tailwindcss/vite`

## Catatan Penting

- Backend harus berjalan terlebih dahulu di `http://localhost:8000`
- Proxy frontend mengandalkan path `/api`, jadi backend dan frontend perlu konsisten dengan prefix endpoint
- `App.vue` tidak menyimpan business logic, hanya orchestration
- Komponen chat dan transaksi bergantung pada backend yang sudah aktif agar data bisa dimuat

## Saran Pengembangan Berikutnya

- tambahkan halaman atau layout navigation jika aplikasi berkembang
- tambahkan error state UI yang lebih eksplisit untuk request gagal
- tambahkan test untuk composables dan komponen penting
- tambahkan filter kategori dan pencarian transaksi di history
