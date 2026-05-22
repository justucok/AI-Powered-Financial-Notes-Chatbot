# Backend README

Backend ini adalah API untuk aplikasi **AI-Powered Financial Notes Chatbot**. Stack utamanya menggunakan **FastAPI**, **SQLAlchemy 2.0 Async**, **SQLite**, dan **Google GenAI SDK** untuk integrasi model Gemini.

Backend menangani tiga area utama:
- pencatatan transaksi manual
- ringkasan keuangan bulanan
- chat berbasis AI untuk input transaksi dari teks dan gambar

## Fitur

- FastAPI dengan lifecycle `lifespan`
- Clean Architecture sederhana: `routers`, `services`, `repositories`, `models`, `schemas`
- SQLite async dengan SQLAlchemy 2.0 style
- Validasi data dengan Pydantic v2
- Integrasi Gemini untuk ekstraksi transaksi dari chat dan gambar

## Struktur Folder

```text
backend/
├── main.py
├── config.py
├── database.py
├── requirements.txt
├── README.md
├── models/
│   └── transaction.py
├── schemas/
│   ├── chat.py
│   └── transaction.py
├── repositories/
│   └── transaction_repository.py
├── services/
│   ├── chat_service.py
│   ├── gemini_service.py
│   └── transaction_service.py
└── routers/
    ├── chat.py
    └── transactions.py
```

## Arsitektur

Project ini mengikuti pembagian tanggung jawab berikut:

- `routers/`
  Menangani HTTP request dan response saja. Tidak ada query database dan tidak ada business logic.
- `services/`
  Menangani business logic dan orkestrasi antar komponen.
- `repositories/`
  Menjadi satu-satunya tempat untuk query SQLAlchemy.
- `models/`
  Berisi ORM model SQLAlchemy.
- `schemas/`
  Berisi schema Pydantic untuk request dan response.
- `database.py`
  Menyediakan engine, session factory, inisialisasi database, dan dependency `get_db`.
- `config.py`
  Memuat konfigurasi aplikasi dari environment variable.

## Environment Variable

Backend membutuhkan file `.env` di folder `backend/`.

Contoh:

```env
APP_NAME=AI Financial Notes Chatbot
API_V1_PREFIX=/api/v1
DATABASE_URL=sqlite+aiosqlite:///./financial_notes.db
GEMINI_API_KEY=your-gemini-api-key
```

Keterangan:
- `APP_NAME`: judul aplikasi FastAPI
- `API_V1_PREFIX`: prefix route API
- `DATABASE_URL`: koneksi database SQLite async
- `GEMINI_API_KEY`: API key untuk Google Gemini

## Install Dependency

Jika belum membuat virtual environment:

```bash
cd "Final Project - AI-Powered Financial Notes Chatbot/backend"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Menjalankan Server

Ada dua cara aman untuk menjalankan backend ini.

Jalankan dari dalam folder `backend`:

```bash
cd "Final Project - AI-Powered Financial Notes Chatbot/backend"
./venv/bin/uvicorn main:app --reload
```

Atau jalankan dari root project:

```bash
cd "Final Project - AI-Powered Financial Notes Chatbot"
./backend/venv/bin/uvicorn backend.main:app --reload
```

Setelah server aktif:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Cara Kerja Singkat

- FastAPI membuat app di `main.py`
- Saat startup, `lifespan` akan membuat tabel database jika belum ada
- Router chat dan transaksi didaftarkan dengan prefix dari `API_V1_PREFIX`
- Untuk fitur AI:
  - `chat_service.py` menangani alur bisnis chat
  - `gemini_service.py` menjadi wrapper untuk Google GenAI SDK
  - hasil ekstraksi transaksi akan diteruskan ke repository untuk disimpan ke database

## Endpoint API

Semua endpoint menggunakan prefix default:

```text
/api/v1
```

### 1. POST `/api/v1/chat`

Memproses pesan teks dari user.

Request body:

```json 
{
  "message": "Saya beli makan siang 25000 hari ini",
  "history": [
    {
      "role": "user",
      "content": "Halo"
    }
  ]
}
```

Perilaku:
- jika Gemini mendeteksi transaksi, backend akan menyimpan transaksi
- jika Gemini mendeteksi permintaan summary, backend akan mengembalikan ringkasan bulan terkait
- jika pesan biasa, backend akan mengembalikan balasan chat formal

Response contoh:

```json
{
  "reply": "Transaksi berhasil dicatat.",
  "data": {
    "id": 1,
    "type": "expense",
    "amount": 25000.0,
    "category": "Makanan",
    "description": "Makan siang",
    "date": "2026-05-23",
    "created_at": "2026-05-23T10:00:00"
  }
}
```

### 2. POST `/api/v1/chat/image`

Memproses gambar nota atau bukti transaksi.

Request:
- `multipart/form-data`
- field file: `file`

Aturan:
- hanya menerima file dengan `content-type` `image/*`
- jika file bukan gambar, backend akan mengembalikan `422 Unprocessable Entity`

Response:
- jika gambar berhasil diekstrak sebagai transaksi, data transaksi akan disimpan
- jika gagal diekstrak, backend akan mengembalikan `reply` yang sesuai

### 3. GET `/api/v1/transactions`

Mengambil daftar transaksi.

Query parameter opsional:
- `month=YYYY-MM`

Contoh:

```text
GET /api/v1/transactions?month=2026-05
```

Response:
- array transaksi

### 4. POST `/api/v1/transactions`

Menambahkan transaksi manual.

Request body:

```json
{
  "type": "expense",
  "amount": 50000,
  "category": "Transport",
  "description": "Ojek online",
  "date": "2026-05-23"
}
```

Response:
- object transaksi yang sudah tersimpan

### 5. DELETE `/api/v1/transactions/{id}`

Menghapus transaksi berdasarkan `id`.

Contoh:

```text
DELETE /api/v1/transactions/1
```

Response contoh:

```json
{
  "message": "Transaction deleted successfully.",
  "id": 1
}
```

Jika transaksi tidak ditemukan:
- `404 Not Found`

### 6. GET `/api/v1/summary`

Mengambil ringkasan keuangan bulanan.

Query parameter opsional:
- `month=YYYY-MM`

Contoh:

```text
GET /api/v1/summary?month=2026-05
```

Response contoh:

```json
{
  "total_income": 1000000,
  "total_expense": 250000,
  "balance": 750000
}
```

Jika `month` tidak dikirim:
- service akan menggunakan bulan saat ini

## Dependency Utama

Isi `requirements.txt` saat ini:

- `fastapi`
- `uvicorn[standard]`
- `sqlalchemy`
- `aiosqlite`
- `pydantic`
- `pydantic-settings`
- `python-dotenv`
- `google-genai`
- `python-multipart`
- `pillow`

## Catatan Penting

- Prefix endpoint default adalah `/api/v1`, jadi request ke `/chat` tanpa prefix akan menghasilkan `{"detail":"Not Found"}`
- Database SQLite akan dibuat otomatis saat aplikasi startup
- API key Gemini wajib tersedia agar fitur chat AI dan ekstraksi gambar dapat berjalan
- Import di backend dibuat fleksibel agar bisa dijalankan baik dari root project maupun langsung dari folder `backend`

## Saran Pengembangan Berikutnya

- tambahkan test untuk service dan router
- tambahkan logging request dan error yang lebih terstruktur
- tambahkan CORS middleware jika backend akan diakses langsung dari frontend browser
- tambahkan health check endpoint seperti `GET /health`
