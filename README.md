# AI-Powered Financial Notes Chatbot

**Final Project** — *AI Productivity and AI API Integration for Developers* (Hacktiv8)

Chatbot berbasis AI untuk **pencatatan keuangan pribadi**. Pengguna dapat mencatat transaksi lewat percakapan natural (teks), mengunggah foto nota/bukti transaksi, menambah transaksi manual, serta memantau ringkasan pemasukan, pengeluaran, dan saldo bulanan — dengan gaya bahasa **formal** dalam Bahasa Indonesia.

---

## Konteks Final Project

Sesuai brief kelas, project ini memenuhi kriteria:

| Kriteria | Implementasi di project ini |
|----------|-----------------------------|
| Chatbot berbasis AI (NLP/LLM) | Google **Gemini** memproses pesan teks dan gambar |
| Use case kreatif | Asisten keuangan pribadi (personal productivity) |
| Parameter kreatif | Bahasa formal, domain keuangan, structured JSON output, riwayat chat (memory), integrasi API Gemini |
| Deliverables | URL repositori GitHub + screenshot UI (setelah frontend selesai) |

---

## Fitur Utama

### Dashboard keuangan (UI — direncanakan)

- **Kartu ringkasan** — saldo, total pemasukan, total pengeluaran per bulan
- **Riwayat transaksi** — tabel dengan filter bulan (6 bulan terakhir + bulan berjalan)
- **Quick Add** — input manual: tipe, jumlah, kategori, deskripsi, tanggal

### Asisten AI (chatbot)

- **Input teks natural** — contoh: *"Beli kopi 35 ribu tadi pagi"* → transaksi otomatis tercatat
- **Query ringkasan** — contoh: *"Berapa total pengeluaran bulan ini?"*
- **Percakapan umum** — pertanyaan non-transaksi dijawab formal oleh asisten
- **Upload foto nota** — ekstraksi `type`, `amount`, `category`, `description`, `date` via Gemini Vision
- **Memory percakapan** — riwayat pesan (hingga 10 pesan terakhir) dikirim ke API untuk konteks

### Backend API (sudah tersedia)

- CRUD transaksi manual (`GET`, `POST`, `DELETE`)
- Ringkasan bulanan (`GET /summary`)
- Chat teks dan chat gambar dengan orkestrasi Clean Architecture
- Database **SQLite** otomatis dibuat saat startup
- Dokumentasi interaktif: Swagger UI & ReDoc

---

## Tech Stack

| Layer | Teknologi |
|-------|-----------|
| Backend | Python 3.10+ · **FastAPI** · **SQLAlchemy 2.0** (async) · **Pydantic v2** |
| Database | **SQLite** (`financial_notes.db`) |
| AI | **Google Gemini** (`google-genai` SDK) — model `gemini-3.5-flash` |
| Frontend (rencana) | **Vue 3** · **Vite** · **TailwindCSS** · **Axios** |

Arsitektur mengikuti **Clean Architecture** — detail layer dan aturan engineering ada di [`AGENTS.md`](./AGENTS.md).

---

## Struktur Project

```text
Final Project - AI-Powered Financial Notes Chatbot/
├── README.md                 # Dokumen ini
├── AGENTS.md                 # Spesifikasi engineering & task list
├── Final Project Info.txt    # Brief final project Hacktiv8
├── .gitignore
├── backend/                  # FastAPI API (implementasi selesai)
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   ├── schemas/
│   ├── repositories/
│   ├── services/
│   ├── routers/
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md             # Dokumentasi API detail
└── frontend/                 # Vue 3 + Vite (direncanakan per AGENTS.md)
```

---

## Prerequisites

- **Python** 3.10 atau lebih baru
- **Node.js** 18+ (untuk frontend, saat folder `frontend/` sudah dibuat)
- **Gemini API Key** — daftar di [Google AI Studio](https://aistudio.google.com/app/apikey)

---

## Setup & Menjalankan

### 1. Clone repository

```bash
git clone <url-repositori-github-anda>
cd "Final Project - AI-Powered Financial Notes Chatbot"
```

### 2. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `backend/.env`:

```env
APP_NAME=AI Financial Notes Chatbot
API_V1_PREFIX=/api/v1
DATABASE_URL=sqlite+aiosqlite:///./financial_notes.db
GEMINI_API_KEY=your_gemini_api_key_here
```

Jalankan server:

```bash
# Dari folder backend/
uvicorn main:app --reload
```

Atau dari root project:

```bash
./backend/venv/bin/uvicorn backend.main:app --reload
```

Server aktif di `http://127.0.0.1:8000`

| Resource | URL |
|----------|-----|
| Swagger UI | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |

### 3. Frontend (setelah diimplementasikan)

```bash
cd frontend
npm install
npm run dev
```

Frontend akan mem-proxy request `/api` ke `http://localhost:8000` (konfigurasi di `vite.config.js`).

> **Catatan:** Saat ini hanya folder `backend/` yang tersedia. UI dapat diuji lewat Swagger atau HTTP client sampai frontend selesai.

---

## Cara Penggunaan

### Melalui antarmuka web (setelah frontend siap)

Layout single-page (lihat [`AGENTS.md`](./AGENTS.md)):

1. **Ringkasan** — lihat saldo, income, dan expense bulan yang dipilih.
2. **Chat Asisten Keuangan** — ketik transaksi atau pertanyaan; lampirkan foto nota dengan tombol upload.
3. **Quick Add** — isi form manual lalu tambah transaksi.
4. **Riwayat** — filter bulan, lihat daftar transaksi, hapus jika perlu.

Setelah transaksi ditambah (via chat, foto, atau quick add), kartu ringkasan dan tabel riwayat diperbarui otomatis.

### Melalui API (Swagger / curl)

Semua endpoint memakai prefix **`/api/v1`**.

#### Mencatat transaksi lewat chat (teks)

```http
POST /api/v1/chat
Content-Type: application/json

{
  "message": "Gaji masuk 8 juta tanggal 1 bulan ini",
  "history": []
}
```

Jika Gemini mendeteksi transaksi, backend menyimpan ke database dan mengembalikan `reply` + `data` transaksi.

#### Mencatat transaksi dari foto nota

```http
POST /api/v1/chat/image
Content-Type: multipart/form-data

file: <gambar nota/bukti>
```

Hanya file dengan `Content-Type` `image/*`. Data yang diekstrak disimpan sebagai transaksi baru.

#### Transaksi manual

```http
POST /api/v1/transactions
Content-Type: application/json

{
  "type": "expense",
  "amount": 50000,
  "category": "Transport",
  "description": "Ojek online",
  "date": "2026-05-23"
}
```

#### Lihat ringkasan bulan

```http
GET /api/v1/summary?month=2026-05
```

#### Lihat & hapus riwayat

```http
GET /api/v1/transactions?month=2026-05
DELETE /api/v1/transactions/1
```

Dokumentasi endpoint lengkap: [`backend/README.md`](./backend/README.md).

---

## Contoh Kalimat untuk Chatbot

Gunakan Bahasa Indonesia. Asisten merespons secara **formal**.

### Mencatat pengeluaran / pemasukan

| Kalimat contoh | Hasil yang diharapkan |
|----------------|------------------------|
| Beli makan siang 25 ribu hari ini | Transaksi `expense`, kategori Makanan |
| Bayar parkir 5000 | Transaksi expense |
| Gaji masuk 8 juta tanggal 1 | Transaksi `income`, kategori Gaji |
| Terima freelance 2,5 juta kemarin | Transaksi income |

Jika jumlah tidak jelas, asisten akan **menanyakan kembali** — tidak mengasumsikan nominal.

### Menanyakan ringkasan

| Kalimat contoh |
|----------------|
| Berapa total pengeluaran bulan ini? |
| Tampilkan ringkasan keuangan Mei 2026 |
| Berapa saldo saya bulan lalu? |

### Percakapan umum (bukan transaksi)

| Kalimat contoh |
|----------------|
| Apa kategori yang biasa dipakai? |
| Terima kasih atas bantuannya |

### Upload gambar

Unggah foto struk, nota, atau bukti transfer — sistem mengekstrak nominal, merchant/kategori, dan tanggal jika terbaca di gambar.

### Kategori umum

Makanan · Transport · Belanja · Kesehatan · Hiburan · Gaji · Freelance · Investasi · Lainnya

---

## Alur Data (ringkas)

```text
┌─────────────────┐     HTTP/REST      ┌──────────────────────┐
│   Vue 3 + Vite  │ ◄────────────────► │  FastAPI (Python)    │
│   (Frontend)    │                    │  (Backend)           │
└─────────────────┘                    └──────────┬───────────┘
                                                  │
                              ┌───────────────────┼──────────────────┐
                              │                   │                  │
                    ┌─────────▼──────┐  ┌─────────▼──────┐ ┌────────▼───────┐
                    │  Gemini API    │  │    SQLite       │ │ Gemini Vision  │
                    │ (Text/Chat)    │  │  (Transactions) │ │ (Image/Nota)   │
                    └────────────────┘  └─────────────────┘ └────────────────┘
```

1. User mengirim pesan atau gambar → router `chat` → `chat_service`
2. `gemini_service` memanggil Gemini dengan system prompt keuangan + structured JSON
3. Jika transaksi terdeteksi → `transaction_repository` menyimpan ke SQLite
4. Jika query summary → repository menghitung total → balasan diformat ke user

---

## Environment Variables

| Variable | Wajib | Keterangan |
|----------|-------|------------|
| `GEMINI_API_KEY` | Ya | API key Google Gemini |
| `DATABASE_URL` | Ya | Default: `sqlite+aiosqlite:///./financial_notes.db` |
| `API_V1_PREFIX` | Tidak | Default: `/api/v1` |
| `APP_NAME` | Tidak | Judul di dokumentasi OpenAPI |

Jangan commit file `.env` — gunakan `.env.example` sebagai template.

---

## Deliverables Final Project

- [ ] **URL repositori GitHub** — isi setelah push ke remote
- [ ] **Screenshot UI** — dashboard, chat, quick add, dan riwayat transaksi (setelah frontend selesai)

Saran nama folder screenshot di repo: `docs/screenshots/`.

---

## Dokumentasi Terkait

| File | Isi |
|------|-----|
| [`AGENTS.md`](./AGENTS.md) | Tech stack, Clean Architecture, layout UI, schema DB, system prompt Gemini, task list |
| [`backend/README.md`](./backend/README.md) | Setup backend, daftar endpoint, contoh request/response |
| [`Final Project Info.txt`](./Final%20Project%20Info.txt) | Brief resmi final project Hacktiv8 |

---

## Lisensi & Konteks

Project ini dibuat sebagai **Final Project** kelas Hacktiv8 *Maju Bareng AI* — integrasi produktivitas AI dan API untuk developer.
