# AI-Powered Financial Notes Chatbot

## Overview

AI-Powered Financial Notes Chatbot adalah aplikasi pencatatan keuangan pribadi yang menggabungkan FastAPI, Vue 3, SQLite, dan Google Gemini. Pengguna dapat mencatat transaksi lewat chat teks, mengunggah foto nota, menambahkan transaksi manual, serta melihat ringkasan pemasukan, pengeluaran, dan saldo bulanan.

## Prerequisites

- Python 3.10+
- Node.js 18+
- Gemini API Key
- PostgreSQL (Supabase) Database URL (untuk production)

## Setup Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Isi `GEMINI_API_KEY` di file `.env`, lalu jalankan:

```bash
uvicorn main:app --reload
```

Backend akan berjalan di `http://127.0.0.1:8000`.

Dokumentasi interaktif:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Setup Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend Vite akan berjalan secara lokal dan mem-proxy request `/api` ke backend `http://localhost:8000`.

## Environment Variables

File `backend/.env` minimal perlu berisi:

```env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=sqlite+aiosqlite:///data/db.sqlite3 # Untuk development lokal
# DATABASE_URL=postgresql+asyncpg://user:password@host/dbname # Untuk production (Supabase)
ALLOWED_ORIGINS=http://localhost:5173,https://your-frontend-domain.vercel.app
```

## API Documentation

Semua endpoint backend memakai prefix:

```text
/api/v1
```

### Chat

- `POST /api/v1/chat`
  Mengirim pesan teks ke chatbot AI.
- `POST /api/v1/chat/image`
  Mengirim gambar nota atau bukti transaksi.

### Transactions

- `GET /api/v1/transactions?month=YYYY-MM`
  Mengambil daftar transaksi untuk bulan tertentu.
- `POST /api/v1/transactions`
  Menambahkan transaksi manual.
- `DELETE /api/v1/transactions/{id}`
  Menghapus transaksi berdasarkan id.

### Summary

- `GET /api/v1/summary?month=YYYY-MM`
  Mengambil ringkasan pemasukan, pengeluaran, dan saldo untuk bulan tertentu.

## Cara Penggunaan Chatbot

Anda dapat berinteraksi dengan **AI Chat Assistant** melalui kotak obrolan di *Dashboard* (versi *mobile*) atau menggunakan **Global Chat Bubble** yang mengambang di pojok kanan bawah (khusus versi *desktop*).

Berikut adalah contoh kalimat yang bisa digunakan:

### Mencatat Pengeluaran

Anda dapat menyebutkan nominal, barang, dan juga **sumber uang** yang digunakan.
- `Saya beli makan siang 25000 hari ini pakai BCA`
- `Bayar ojek online 18000 dari Gopay`
- `Belanja bulanan 450000 kemarin pakai Uang Tunai`

### Mencatat Pemasukan

- `Gaji masuk 8000000 tanggal 1 ke Bank Mandiri`
- `Dapat freelance 1500000 hari ini`
- `Saya menerima bonus 500000 masuk ke Dana`

### Mengatur Anggaran (Budget)

Anda bisa langsung mengatur budget bulanan melalui chat!
- `Tolong set budget bulan ini sebesar 5000000`
- `Atur budget untuk bulan depan (Agustus 2026) jadi 6000000`
- `Set budget kategori Makanan sebesar 1500000 untuk bulan ini`

### Menambahkan Sumber Uang

- `Tambahkan sumber uang baru Bank Mandiri dengan saldo awal 2000000`
- `Buat sumber uang E-Wallet OVO saldonya 500000`

### Menanyakan Ringkasan & Sisa Budget

- `Berapa total pengeluaran bulan ini?`
- `Tampilkan ringkasan keuangan Mei 2026`
- `Berapa sisa budget saya bulan ini?`

### Mengunggah Nota / Struk (Image Vision)

- Klik ikon klip (📎) untuk mengunggah foto struk makan, parkir, atau belanja Anda.
- Chatbot akan otomatis menganalisa gambar tersebut dan mengekstrak *nominal*, *kategori*, dan *tanggal*, lalu mencatatnya untuk Anda!

## Fitur Aplikasi (Features)

Aplikasi ini memiliki berbagai fitur unggulan untuk membantu mencatat dan mengelola keuangan Anda:

1. **AI Chat Assistant (Text)**: Anda bisa mencatat transaksi atau menanyakan ringkasan keuangan hanya dengan mengobrol secara natural. AI akan mengekstrak nominal, tipe (pemasukan/pengeluaran), kategori, dan tanggal secara otomatis.
2. **Ekstraksi Nota (Image Vision)**: Cukup unggah foto struk/nota belanja, AI akan secara otomatis mengenali dan mencatat rincian transaksi tersebut.
3. **Pencatatan Manual**: Fitur *Quick Add* untuk menambah transaksi secara manual dengan *form* yang mudah digunakan.
4. **Riwayat Transaksi**: Tabel riwayat transaksi dengan fitur filter per bulan.
5. **Sumber Uang (Fund Sources)**: Kelola berbagai sumber dana (Bank, E-Wallet, Tunai) beserta saldo real-time yang terhubung ke setiap transaksi.
6. **Kategori Dinamis**: Tambah, ubah, dan hapus kategori pemasukan maupun pengeluaran.
7. **Pengaturan Anggaran (Budgeting)**: Atur batas anggaran bulanan secara global atau rinci per-kategori pengeluaran. Anda akan mendapat peringatan (OVER BUDGET) jika pengeluaran melewati batas.
8. **Statistik Interaktif**: Lacak tren pengeluaran, perbandingan pemasukan dan pengeluaran dalam bentuk visual chart.
9. **Desain Responsif**: Antarmuka yang bersih dan ramah pengguna di perangkat desktop maupun *mobile*.

## Last Update (Terbaru)

**Update 12 Juli 2026 (feature_2_12072026)**
- Memperbaiki tata letak (layout) *Dashboard* pada versi *mobile* (jarak batas bawah dan ukuran kotak obrolan diperbaiki).
- Mengimplementasikan fitur *Global Chat Bubble* khusus untuk versi *desktop* agar *AI Chat Assistant* dapat diakses secara mengambang dari mana saja.
- Menghapus tulisan "Rp Rp" ganda yang muncul akibat konflik pembentukan format Rupiah di halaman *Dashboard* dan *Pengaturan* (Sumber Uang & Anggaran).
- Menyatukan informasi *Statistics* dan *Dashboard* pada mode layar *desktop*.

## Deployment ke Production

Proyek ini telah dikonfigurasi agar siap di-deploy dengan arsitektur berikut:
1. **Frontend**: Vercel
2. **Backend**: Render (Web Service gratis)
3. **Database**: Supabase (PostgreSQL)

### Link Production

Aplikasi production dapat diakses melalui:

```text
https://ai-powered-financial-notes-chatbot-k6omdwoj0-justucoks-projects.vercel.app/
```

### Persiapan Variabel Environment (Secrets)
Pastikan Anda menambahkan Environment Variables ini di Dashboard Render dan Vercel. **Penting: Jangan pernah mengekspos API Keys atau Database URL di dalam kode sumber / repository.**
- Render: Tambahkan `GEMINI_API_KEY`, `DATABASE_URL` (dari Supabase dengan format `postgresql+asyncpg://...`), dan `ALLOWED_ORIGINS` (URL dari Vercel).
- Vercel: Tambahkan `VITE_API_BASE_URL` mengarah ke URL layanan Render Anda.

### Branch Management
Proyek ini menggunakan dua branch utama:
- `develop`: Untuk pengembangan lokal menggunakan SQLite (set `DATABASE_URL` ke `sqlite+aiosqlite:///...`).
- `main`: Branch stabil yang terhubung otomatis ke Render dan Vercel untuk production menggunakan PostgreSQL Supabase.

## Fitur Aplikasi (Features)

Aplikasi ini memiliki berbagai fitur unggulan untuk membantu mencatat dan mengelola keuangan Anda:

1. **AI Chat Assistant (Text)**: Anda bisa mencatat transaksi atau menanyakan ringkasan keuangan hanya dengan mengobrol secara natural. AI akan mengekstrak nominal, tipe (pemasukan/pengeluaran), kategori, dan tanggal secara otomatis.
2. **Ekstraksi Nota (Image Vision)**: Cukup unggah foto struk/nota belanja, AI akan secara otomatis mengenali dan mencatat rincian transaksi tersebut.
3. **Pencatatan Manual**: Fitur *Quick Add* untuk menambah transaksi secara manual dengan *form* yang mudah digunakan.
4. **Riwayat Transaksi**: Tabel riwayat transaksi dengan fitur filter per bulan.
5. **Sumber Uang (Fund Sources)**: Kelola berbagai sumber dana (Bank, E-Wallet, Tunai) beserta saldo real-time yang terhubung ke setiap transaksi.
6. **Kategori Dinamis**: Tambah, ubah, dan hapus kategori pemasukan maupun pengeluaran.
7. **Pengaturan Anggaran (Budgeting)**: Atur batas anggaran bulanan secara global atau rinci per-kategori pengeluaran. Anda akan mendapat peringatan (OVER BUDGET) jika pengeluaran melewati batas.
8. **Statistik Interaktif**: Lacak tren pengeluaran, perbandingan pemasukan dan pengeluaran dalam bentuk visual chart.
9. **Desain Responsif**: Antarmuka yang bersih dan ramah pengguna di perangkat desktop maupun *mobile*.

## Last Update (Terbaru)

**Update 19 Juli 2026 (fix_external_statistics_refresh_19072026)**
- Memperbaiki refresh statistik untuk transaksi yang ditambahkan dari Global Chat Bubble dan event eksternal lain dengan menyatukan handler refresh di `App.vue`.
- Mengekspos `triggerUpdate()` dari `useTransactions()` agar perubahan transaksi di luar form utama tetap memicu pembaruan chart tren dan histori kategori.

**Update 19 Juli 2026 (fix_statistics_category_history_19072026)**
- Memperbaiki sinkronisasi data Statistik agar chart tren bulanan dan histori kategori ikut ter-refresh setelah transaksi ditambahkan, diedit, atau dihapus.
- Memperbaiki urutan data chart tren bulanan agar tampil kronologis dari bulan terlama ke terbaru.
- Memperkuat re-render Bar Chart dan Pie Chart saat filter tipe, periode, bulan, atau data transaksi berubah.
- Memperbaiki race condition loading pada pengambilan data statistik agar request lama yang dibatalkan tidak mengganggu request terbaru.

**Update 18 Juli 2026 (fix_workflow_rules_17072026)**
- Memperbaiki normalisasi path SQLite pada `backend/database.py` agar database tetap dapat dibuka saat backend dijalankan dari folder root project maupun folder `backend`.
- Menambahkan pembuatan parent directory database secara otomatis sebelum SQLAlchemy engine dibuat untuk mencegah error `sqlite3.OperationalError: unable to open database file`.
- Menambahkan link production Vercel ke dokumentasi deployment.

**Update 17 Juli 2026 (fix_workflow_rules_17072026)**
- Menambahkan aturan workflow otomatis ke `AGENTS.md` terkait kewajiban memperbarui `README.md` dan `AGENTS.md` setiap ada penambahan fitur atau perbaikan *bug* sebelum melakukan *push* ke Git.

**Update 17 Juli 2026 (fix_category_and_settings_UI_17072026)**
- Memperbaiki sinkronisasi kategori dinamis pada formulir *Quick Add* (Tambah Cepat).
- Menambahkan pengurutan kategori secara otomatis berdasarkan tipe (pengeluaran/pemasukan), lalu berdasarkan abjad, serta memposisikan kategori "Lainnya" selalu di urutan paling bawah.
- Memindahkan form penambahan Sumber Uang Baru dan Kategori Baru ke bagian paling atas pada halaman *Settings* (Pengaturan).

**Update 12 Juli 2026 (feature_2_12072026)**
- Memperbaiki tata letak (layout) *Dashboard* pada versi *mobile* (jarak batas bawah dan ukuran kotak obrolan diperbaiki).
- Mengimplementasikan fitur *Global Chat Bubble* khusus untuk versi *desktop* agar *AI Chat Assistant* dapat diakses secara mengambang dari mana saja.
- Menghapus tulisan "Rp Rp" ganda yang muncul akibat konflik pembentukan format Rupiah di halaman *Dashboard* dan *Pengaturan* (Sumber Uang & Anggaran).
- Menyatukan informasi *Statistics* dan *Dashboard* pada mode layar *desktop*.

## Project Structure

```text
Final Project - AI-Powered Financial Notes Chatbot/
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   ├── repositories/
│   ├── routers/
│   ├── schemas/
│   ├── services/
│   ├── requirements.txt
│   └── README.md
└── frontend/
    ├── src/
    │   ├── components/
    │   ├── composables/
    │   ├── services/
    │   └── utils/
    ├── package.json
    └── vite.config.js
```
