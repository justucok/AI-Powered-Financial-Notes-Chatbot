# AI-Powered Financial Notes Chatbot

## Overview

AI-Powered Financial Notes Chatbot adalah aplikasi pencatatan keuangan pribadi yang menggabungkan FastAPI, Vue 3, SQLite, dan Google Gemini. Pengguna dapat mencatat transaksi lewat chat teks, mengunggah foto nota, menambahkan transaksi manual, serta melihat ringkasan pemasukan, pengeluaran, dan saldo bulanan.

## Prerequisites

- Python 3.10+
- Node.js 18+
- Gemini API Key

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

Contoh kalimat yang bisa digunakan:

### Mencatat pengeluaran

- `Saya beli makan siang 25000 hari ini`
- `Bayar ojek online 18000`
- `Belanja bulanan 450000 kemarin`

### Mencatat pemasukan

- `Gaji masuk 8000000 tanggal 1`
- `Dapat freelance 1500000 hari ini`
- `Saya menerima bonus 500000`

### Menanyakan ringkasan

- `Berapa total pengeluaran bulan ini?`
- `Tampilkan ringkasan keuangan Mei 2026`
- `Berapa saldo saya bulan ini?`

### Upload nota

- Unggah foto struk makan, parkir, transportasi, atau belanja
- Chatbot akan mencoba mengekstrak `type`, `amount`, `category`, `description`, dan `date`

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
