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
