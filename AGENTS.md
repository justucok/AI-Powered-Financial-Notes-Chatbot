# AGENTS.md — AI Financial Notes Chatbot

## Project Overview

Aplikasi pencatatan keuangan berbasis AI dengan chatbot untuk input transaksi via teks natural dan foto nota/bukti transaksi. Single-page application dengan gaya bahasa formal.

---

## Tech Stack

| Layer | Tech |
|---|---|
| Backend | Python + FastAPI |
| AI Model | Gemini 2.5 Pro (Google AI Studio) |
| Database | PostgreSQL (Supabase) / SQLite (Dev) + SQLAlchemy 2.0 |
| Frontend | Vue 3 + Vite + TailwindCSS |
| HTTP Client | Axios |

---

## Engineering Rules

Seluruh kode yang dihasilkan dalam project ini **wajib** mengikuti aturan berikut. Aturan ini bersifat non-negotiable dan harus diterapkan di setiap task tanpa terkecuali.

---

### 1. Best Practice per Stack

Setiap kode harus mengacu pada **dokumentasi resmi** masing-masing teknologi berikut:

| Stack | Referensi Resmi | Poin Utama |
|---|---|---|
| **FastAPI** | https://fastapi.tiangolo.com | Gunakan `APIRouter`, dependency injection via `Depends()`, Pydantic v2 untuk validasi, `HTTPException` untuk error handling, lifespan events untuk startup/shutdown |
| **SQLAlchemy** | https://docs.sqlalchemy.org/en/20/ | Gunakan SQLAlchemy 2.0 style (`select()` statement, tidak pakai `Query` legacy), session scoping yang benar dengan context manager |
| **Pydantic** | https://docs.pydantic.dev/latest/ | Gunakan `model_validator`, `field_validator`, `ConfigDict`, `model_config` — bukan `class Config` (deprecated) |
| **Google GenAI SDK** | https://ai.google.dev/gemini-api/docs | Gunakan `genai.Client`, `google.genai.types`, structured output dengan `response_mime_type: application/json` |
| **Vue 3** | https://vuejs.org/guide/ | Wajib Composition API dengan `<script setup>`, gunakan `defineProps`, `defineEmits`, `defineExpose` — bukan Options API |
| **Vite** | https://vitejs.dev/config/ | Konfigurasi proxy di `vite.config.js`, gunakan `import.meta.env` untuk environment variables |
| **TailwindCSS** | https://tailwindcss.com/docs | Gunakan utility classes langsung, tidak membuat custom CSS kecuali sangat diperlukan, manfaatkan `@apply` hanya di base layer |
| **Axios** | https://axios-http.com/docs/intro | Buat single instance dengan `axios.create()`, gunakan interceptors untuk error handling global |

**Aturan tambahan:**
- Tidak boleh menggunakan pattern yang sudah deprecated menurut doc resmi
- Jika ada dua cara melakukan sesuatu, pilih cara yang direkomendasikan doc terbaru
- Versi library harus eksplisit di `requirements.txt` dan `package.json`

---

### 2. Clean Architecture

Project ini menerapkan **Clean Architecture** dengan pemisahan tanggung jawab yang jelas. Setiap layer hanya boleh berkomunikasi ke layer di bawahnya.

```
┌─────────────────────────────────────────────────┐
│               PRESENTATION LAYER                │
│   routers/ (FastAPI routes, request/response)   │
│   components/ (Vue components, UI only)         │
├─────────────────────────────────────────────────┤
│               APPLICATION LAYER                 │
│   services/ (business logic, orchestration)     │
│   use_cases/ (jika diperlukan per fitur)        │
├─────────────────────────────────────────────────┤
│                 DOMAIN LAYER                    │
│   models/ (entities, business rules)            │
│   schemas/ (data contracts / DTOs)              │
├─────────────────────────────────────────────────┤
│              INFRASTRUCTURE LAYER               │
│   database/ (SQLAlchemy session, connection)    │
│   repositories/ (query logic ke DB)             │
│   external/ (Gemini API client wrapper)         │
└─────────────────────────────────────────────────┘
```

**Aturan per layer:**

**Routers (Presentation)**
- Hanya boleh menerima request dan mengembalikan response
- Tidak boleh ada logika bisnis di dalam router
- Tidak boleh langsung query ke database — delegasikan ke service
- Hanya boleh import dari layer `services/` dan `schemas/`

**Services (Application)**
- Tempat semua business logic dan orkestrasi
- Boleh memanggil repository dan external service (Gemini)
- Tidak boleh tahu detail implementasi DB (tidak import SQLAlchemy query langsung)
- Setiap service harus bisa di-test secara independen (dependency injection)

**Repositories (Infrastructure)**
- Satu-satunya tempat yang boleh menulis SQLAlchemy query
- Hanya menerima dan mengembalikan domain model / schema
- Tidak boleh ada logika bisnis

**Models / Schemas (Domain)**
- `models.py` = SQLAlchemy ORM model (representasi tabel)
- `schemas.py` = Pydantic schema (DTO untuk request/response)
- Tidak boleh ada logika bisnis di sini, hanya definisi struktur

**Aturan tambahan:**
- Dependency injection wajib digunakan — tidak boleh ada hardcoded dependency
- Tidak ada circular import antar module
- Setiap fungsi memiliki satu tanggung jawab (Single Responsibility Principle)
- Nama fungsi dan variabel harus deskriptif dan konsisten (snake_case untuk Python, camelCase untuk JS/Vue)

---

### 3. Updated Folder Structure (dengan Clean Architecture)

```
project-root/
├── backend/
│   ├── main.py                     # Entry point, app factory
│   ├── config.py                   # Settings via pydantic-settings
│   ├── database.py                 # Engine, session factory, get_db()
│   ├── models/
│   │   └── transaction.py          # SQLAlchemy ORM model
│   ├── schemas/
│   │   └── transaction.py          # Pydantic DTOs (Request/Response)
│   ├── repositories/
│   │   └── transaction_repository.py  # Query logic ke DB
│   ├── services/
│   │   ├── transaction_service.py  # Business logic transaksi
│   │   └── gemini_service.py       # Wrapper Gemini API
│   ├── routers/
│   │   ├── transactions.py         # Endpoint /transactions
│   │   └── chat.py                 # Endpoint /chat
│   ├── .env
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/             # UI components (presentational only)
    │   │   ├── SummaryCards.vue
    │   │   ├── ChatBox.vue
    │   │   ├── QuickAdd.vue
    │   │   └── TransactionHistory.vue
    │   ├── composables/            # Reusable Vue logic (hooks)
    │   │   ├── useTransactions.js  # State + logic untuk transaksi
    │   │   └── useChat.js          # State + logic untuk chatbot
    │   ├── services/
    │   │   └── api.js              # Axios instance + API calls
    │   ├── utils/
    │   │   └── formatters.js       # Format Rupiah, tanggal, dll
    │   └── App.vue                 # Root component, orchestration only
    ├── index.html
    └── vite.config.js
```

**Catatan struktur frontend:**
- `components/` = murni presentational, tidak ada API call langsung
- `composables/` = semua state dan logic, dipanggil dari komponen
- `services/api.js` = satu-satunya file yang tahu tentang HTTP / Axios
- `utils/` = pure functions, tidak ada side effect

---

### 4. Code Quality Rules

Terapkan aturan ini di setiap baris kode:

- **Typing wajib di Python** — semua fungsi harus punya type hints (parameter dan return type)
- **Async/await konsisten** — jika fungsi melakukan I/O (DB, HTTP), harus `async`
- **Error handling eksplisit** — tidak boleh ada `except: pass` atau exception yang diabaikan
- **Environment variable** — tidak ada hardcoded value (API key, URL, dsb) di dalam kode
- **Komentar kode** — tambahkan docstring untuk setiap fungsi di layer service dan repository
- **Tidak ada dead code** — tidak ada fungsi atau import yang tidak digunakan

---

### 5. Git Version Control Rules

Terapkan konvensi Git berikut ini pada setiap perubahan kode:

- **Penamaan Branch**: 
  - Untuk fitur baru, wajib menggunakan format `feature_{urutan-fitur}_{DDMMYYYY}` (contoh: `feature_1_12072026`).
  - Untuk perbaikan bug/error, wajib menggunakan format `fix_{perbaikan_tentang_apa}_{DDMMYYYY}` (contoh: `fix_missing_chat_decorator_12072026`).
- **Pesan Commit**: Selalu gunakan Conventional Commits format dengan jelas (contoh: `feat: [deskripsi fitur]`, `fix: [deskripsi perbaikan]`, `refactor: [deskripsi refactor]`).

---

## Architecture

```
┌─────────────────┐     HTTP/REST      ┌──────────────────────┐
│   Vue 3 + Vite  │ ◄────────────────► │  FastAPI (Python)    │
│   (Frontend)    │                    │  (Backend)           │
└─────────────────┘                    └──────────┬───────────┘
                                                  │
                              ┌───────────────────┼──────────────────┐
                              │                   │                  │
                    ┌─────────▼──────┐  ┌─────────▼──────┐ ┌────────▼───────┐
                    │  Gemini API    │  │ PostgreSQL/SQLite│ │ Gemini Vision  │
                    │ (Text/Chat)    │  │  (Transactions) │ │ (Image/Nota)   │
                    └────────────────┘  └─────────────────┘ └────────────────┘
```

---

## Page Layout (Single Page)

```
┌─────────────────────────────────────────┐
│           FINANCIAL DASHBOARD           │
├─────────────────────────────────────────┤
│  💰 Balance  │  📈 Income  │  📉 Expense │  ← Section 1: Summary Cards
├─────────────────────────────────────────┤
│  🤖 AI Chat Assistant                   │
│  [chat bubbles area]                    │  ← Section 2: Chatbot
│  [📎 foto] [input pesan      ] [Kirim]  │
├─────────────────────────────────────────┤
│  ⚡ Quick Add                            │  ← Section 3: Manual Input
│  [Type][Amount][Category][Desc][+ Add]  │
├─────────────────────────────────────────┤
│  📋 Transaction History  [Filter: Bulan]│  ← Section 4: History Table
│  Date | Description | Category | Amount │
└─────────────────────────────────────────┘
```

---

## Folder Structure

> Struktur lengkap dengan Clean Architecture — lihat detail di section **Engineering Rules** di atas.

```
project-root/
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   └── transaction.py
│   ├── schemas/
│   │   └── transaction.py
│   ├── repositories/
│   │   └── transaction_repository.py
│   ├── services/
│   │   ├── transaction_service.py
│   │   └── gemini_service.py
│   ├── routers/
│   │   ├── transactions.py
│   │   └── chat.py
│   ├── .env
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── SummaryCards.vue
    │   │   ├── ChatBox.vue
    │   │   ├── QuickAdd.vue
    │   │   └── TransactionHistory.vue
    │   ├── composables/
    │   │   ├── useTransactions.js
    │   │   └── useChat.js
    │   ├── services/
    │   │   └── api.js
    │   ├── utils/
    │   │   └── formatters.js
    │   └── App.vue
    ├── index.html
    └── vite.config.js
```

---

## Database Schema

```sql
CREATE TABLE transactions (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  type        TEXT NOT NULL CHECK(type IN ('income', 'expense')),
  amount      REAL NOT NULL,
  category    TEXT NOT NULL,
  description TEXT,
  date        TEXT NOT NULL,
  created_at  TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Schema telah dikonsolidasi. Tabel lain (budgets, categories, fund_sources) juga memiliki user_id foreign key untuk isolasi data per user.
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/transactions?month=YYYY-MM` | List transaksi, filter by bulan |
| POST | `/transactions` | Tambah transaksi manual |
| DELETE | `/transactions/{id}` | Hapus transaksi |
| GET | `/summary?month=YYYY-MM` | Total balance, income, expense |
| POST | `/chat` | Proses pesan user via Gemini |
| POST | `/chat/image` | Upload foto nota, ekstrak via Gemini Vision |

---

## Gemini System Prompt

```
Kamu adalah asisten keuangan pribadi yang profesional dan formal.
Tugasmu adalah membantu pengguna mencatat dan memantau keuangan pribadi mereka.

INSTRUKSI UTAMA:
1. Jika pengguna menyebutkan transaksi keuangan, ekstrak data dan kembalikan dalam format JSON berikut:
{
  "is_transaction": true,
  "type": "income" atau "expense",
  "amount": <angka tanpa titik/koma>,
  "category": <string, contoh: Makanan, Transport, Gaji, dll>,
  "description": <string deskripsi singkat>,
  "date": <"YYYY-MM-DD" atau null jika tidak disebutkan>
}

2. Jika pengguna bertanya tentang saldo atau ringkasan bulan tertentu, kembalikan:
{
  "is_transaction": false,
  "action": "query_summary",
  "month": <"YYYY-MM" atau null>
}

3. Jika bukan transaksi dan bukan query keuangan, balas secara natural:
{
  "is_transaction": false,
  "action": "chat",
  "reply": <string balasan formal>
}

ATURAN:
- Selalu gunakan Bahasa Indonesia yang formal dan sopan
- Jika amount tidak jelas, tanyakan kembali kepada pengguna
- Kategori umum: Makanan, Transport, Belanja, Kesehatan, Hiburan, Gaji, Freelance, Investasi, Lainnya
- Jangan pernah mengasumsikan amount jika tidak disebutkan secara eksplisit
```

---

## Task List — Phase 1

### TASK-01: Backend Setup & Database
**Prompt untuk AI:**
```
Buatkan setup awal project FastAPI dengan menerapkan Clean Architecture dan best practice
sesuai dokumentasi resmi FastAPI (https://fastapi.tiangolo.com) dan SQLAlchemy 2.0
(https://docs.sqlalchemy.org/en/20/).

Struktur layer yang wajib diikuti:
- Presentation  : routers/ (hanya handle request/response, tidak ada logic bisnis)
- Application   : services/ (semua business logic)
- Infrastructure: repositories/ (semua query DB), database.py (koneksi)
- Domain        : models/, schemas/ (definisi struktur, tidak ada logic)

File yang dibuat:
- config.py: gunakan pydantic-settings (BaseSettings) untuk load GEMINI_API_KEY dari .env
- database.py: SQLAlchemy 2.0 style — engine, sessionmaker, AsyncSession jika memungkinkan,
  get_db() sebagai Depends() bukan global variable
- models/transaction.py: SQLAlchemy ORM model Transaction (id, type, amount, category,
  description, date, created_at). Gunakan DeclarativeBase dari sqlalchemy.orm
- schemas/transaction.py: Pydantic v2 dengan model_config = ConfigDict(from_attributes=True).
  Buat TransactionCreate, TransactionResponse, SummaryResponse
- requirements.txt: sertakan versi eksplisit semua library (fastapi>=0.111, uvicorn,
  sqlalchemy>=2.0, pydantic-settings, python-dotenv, google-genai, python-multipart, pillow)

Aturan wajib:
- SQLAlchemy 2.0 style select() — tidak boleh pakai session.query() (legacy)
- Pydantic v2 — tidak boleh pakai class Config (deprecated), gunakan model_config
- Type hints wajib di semua fungsi (parameter + return type)
- Inisialisasi DB via lifespan context manager — tidak boleh pakai @app.on_event (deprecated)
- Tidak ada hardcoded value — semua config dari environment variable via config.py
```

---

### TASK-02: Repository & Transaction Endpoints
**Prompt untuk AI:**
```
Buatkan dua file dengan pemisahan layer Clean Architecture yang ketat:

FILE 1 — repositories/transaction_repository.py:
Semua query SQLAlchemy ada di sini, tidak boleh ada di tempat lain.
Gunakan SQLAlchemy 2.0 style (select(), not session.query()).
Fungsi yang dibuat (semua dengan type hints lengkap):
- get_all(db, month: str | None) -> list[Transaction]
- create(db, data: TransactionCreate) -> Transaction
- delete(db, id: int) -> Transaction | None
- get_summary(db, month: str) -> dict (total_income, total_expense, balance)

FILE 2 — services/transaction_service.py:
Business logic dan orkestrasi. Tidak ada SQLAlchemy query di sini.
Hanya memanggil fungsi dari transaction_repository.
Fungsi yang dibuat:
- get_transactions(db, month) -> list[TransactionResponse]
- create_transaction(db, data: TransactionCreate) -> TransactionResponse
- delete_transaction(db, id: int) -> dict
- get_summary(db, month: str | None) -> SummaryResponse

FILE 3 — routers/transactions.py:
Hanya handle HTTP request/response. Tidak ada logic bisnis, tidak ada query DB.
Endpoint:
- GET /transactions?month=YYYY-MM -> panggil transaction_service.get_transactions()
- POST /transactions -> panggil transaction_service.create_transaction()
- DELETE /transactions/{id} -> panggil transaction_service.delete_transaction()
- GET /summary?month=YYYY-MM -> panggil transaction_service.get_summary()
Semua endpoint gunakan Depends(get_db) dan raise HTTPException yang sesuai.

Aturan wajib:
- Router hanya import dari services/ dan schemas/
- Service hanya import dari repositories/ dan schemas/
- Repository hanya import dari models/ dan database
- Type hints wajib di semua fungsi
- Docstring wajib di setiap fungsi service dan repository
```

---

### TASK-03: Gemini AI Service
**Prompt untuk AI:**
```
Buatkan file services/gemini_service.py mengikuti best practice dari dokumentasi resmi
Google Generative AI Python SDK (https://ai.google.dev/gemini-api/docs).

Layer ini adalah Infrastructure layer — tugasnya hanya sebagai wrapper Gemini API.
Tidak ada business logic di sini. Semua logic ada di chat_service.py (dibuat di TASK-04).

Implementasi:
- Inisialisasi client dari config (GEMINI_API_KEY via config.py dari TASK-01)
- Gunakan response_mime_type: "application/json" di generation_config untuk structured output
  agar tidak perlu manual JSON parsing (referensi: https://ai.google.dev/gemini-api/docs/structured-output)

Fungsi yang dibuat (semua dengan type hints dan docstring):

1. async def process_chat(message: str, history: list[dict]) -> dict:
   - Model: gemini-2.5-pro
   - Kirim system prompt keuangan (lihat AGENTS.md) + history (last 10 messages) + message
   - Gunakan generation_config dengan response_mime_type="application/json"
   - Return dict hasil parse langsung (tidak perlu json.loads manual jika pakai structured output)
   - Handle GenerativeAIException dan JSONDecodeError — return error dict yang aman

2. async def process_image(image_bytes: bytes, mime_type: str) -> dict:
   - Model: gemini-2.5-pro (mendukung vision)
   - Kirim image sebagai inline_data dengan mime_type yang diberikan
   - Prompt instruksikan ekstrak: type, amount, category, description, date
   - Gunakan generation_config dengan response_mime_type="application/json"
   - Return dict hasil ekstrak atau error dict jika gagal

Error fallback dict:
{"is_transaction": False, "action": "chat", "reply": "Maaf, terjadi kesalahan teknis."}

Aturan wajib:
- API key tidak boleh hardcoded — ambil dari config.py
- Semua exception harus di-catch dan di-log, tidak boleh propagate mentah ke router
- Type hints lengkap di semua fungsi
```

---

### TASK-04: Chat Service & Endpoints
**Prompt untuk AI:**
```
Buatkan dua file untuk fitur chat, dengan pemisahan layer Clean Architecture:

FILE 1 — services/chat_service.py (Application Layer):
Semua business logic untuk chat ada di sini. Boleh memanggil gemini_service dan
transaction_repository. Tidak ada HTTP-specific code di sini.

Fungsi yang dibuat:
- async def handle_text_message(db, message: str, history: list[dict]) -> dict:
  * Panggil gemini_service.process_chat()
  * Jika is_transaction: panggil transaction_repository.create() dan return reply + data
  * Jika action == "query_summary": panggil transaction_repository.get_summary() dan format reply
  * Jika action == "chat": return reply langsung
  * Semua dengan type hints dan docstring

- async def handle_image_message(db, image_bytes: bytes, mime_type: str) -> dict:
  * Panggil gemini_service.process_image()
  * Jika berhasil ekstrak transaksi, panggil transaction_repository.create()
  * Return reply + transaction data jika ada

FILE 2 — routers/chat.py (Presentation Layer):
Hanya handle HTTP. Tidak ada logic bisnis di sini.
Endpoint:
- POST /chat: body { message: str, history: list = [] }
  -> delegasikan ke chat_service.handle_text_message()
- POST /chat/image: UploadFile via Form
  -> baca bytes + mime_type, delegasikan ke chat_service.handle_image_message()

Semua endpoint gunakan Depends(get_db), return JSONResponse yang sesuai.
Gunakan HTTPException 422 jika file bukan gambar (validasi mime_type di router).

Aturan wajib:
- Router tidak import dari repository secara langsung
- Service tidak import dari routers
- Tidak ada SQLAlchemy query di service atau router
- Type hints dan docstring wajib di semua fungsi service
```

---

### TASK-05: Frontend Setup & Summary Cards
**Prompt untuk AI:**
```
Buatkan setup Vue 3 + Vite project dengan menerapkan separation of concerns yang ketat.
Referensi: Vue 3 docs (https://vuejs.org/guide/), Vite docs (https://vitejs.dev/config/),
Axios docs (https://axios-http.com/docs/intro).

FILE 1 — vite.config.js:
- Proxy /api ke http://localhost:8000
- Gunakan defineConfig dari vite (bukan object literal biasa)

FILE 2 — src/services/api.js (Infrastructure Layer):
- Buat single axios instance dengan axios.create({ baseURL: "/api" })
- Tambahkan response interceptor untuk handle error global (log + re-throw)
- Export named functions (bukan default object):
  * getTransactions(month?: string)
  * createTransaction(data: object)
  * deleteTransaction(id: number)
  * getSummary(month?: string)
  * sendChat(message: string, history: array)
  * sendChatImage(file: File) — gunakan FormData
- Tidak ada state management di file ini, murni HTTP calls

FILE 3 — src/utils/formatters.js:
- formatRupiah(amount: number): string — format ke "Rp 1.250.000"
- formatDate(dateStr: string): string — format ke "12 Jan 2025"
- formatMonth(monthStr: string): string — format ke "Januari 2025"
Pure functions, tidak ada side effect, mudah di-test.

FILE 4 — src/components/SummaryCards.vue:
- Gunakan <script setup> (Composition API, wajib — bukan Options API)
- Props: defineProps({ balance: Number, income: Number, expense: Number })
- Import formatRupiah dari utils/formatters.js
- Tampilkan 3 kartu dengan TailwindCSS: Balance (biru), Income (hijau), Expense (merah)
- Responsive: grid-cols-3 desktop, grid-cols-1 mobile
- Komponen ini murni presentational — tidak ada API call

Install: npm install axios, setup TailwindCSS via @tailwindcss/vite plugin (Tailwind v4 style
jika tersedia, referensi: https://tailwindcss.com/docs/installation/vite)
```

---

### TASK-06: ChatBox Composable & Component
**Prompt untuk AI:**
```
Buatkan dua file dengan pemisahan logic dan UI sesuai best practice Vue 3
(https://vuejs.org/guide/reusability/composables.html):

FILE 1 — src/composables/useChat.js (Application Logic):
Semua state dan logic chat ada di sini. Komponen tidak boleh punya logic sendiri.
Gunakan Composition API: ref, computed dari vue.
Export fungsi useChat() yang return:
- messages: ref([]) — array { role: "user"|"bot", text: string, hasTransaction: boolean }
- history: computed — format untuk dikirim ke API (last 10 messages)
- isLoading: ref(false)
- imagePreview: ref(null)
- sendTextMessage(message: string): async — panggil api.sendChat(), update messages
- sendImageMessage(file: File): async — panggil api.sendChatImage(), update messages
- selectImage(file: File) — set preview
- clearImage() — clear preview
- emit "transaction-added" via parameter callback onTransactionAdded

FILE 2 — src/components/ChatBox.vue (Presentation Only):
- Gunakan <script setup>
- defineEmits(["transaction-added"])
- Import dan gunakan useChat() composable
- UI murni: chat bubbles, input, tombol upload, loading indicator, image preview
- Auto scroll ke bawah dengan watchEffect + template ref pada container
- Komponen tidak boleh punya logic bisnis — semua delegasi ke composable

UI requirements:
- Bubble user: kanan, biru. Bubble bot: kiri, abu-abu, label "Asisten Keuangan"
- Badge "✅ Transaksi Dicatat" jika hasTransaction: true
- Loading: animated dots (CSS animation, bukan library)
- Input area: tombol 📎 upload foto, text input, tombol kirim
- Image preview thumbnail dengan tombol cancel (X)

Aturan wajib:
- Wajib <script setup> — tidak boleh Options API
- defineProps dan defineEmits harus eksplisit dengan tipe
- Tidak ada API call langsung di komponen
```

---

### TASK-07: QuickAdd Composable & TransactionHistory Components
**Prompt untuk AI:**
```
Buatkan tiga file dengan pola yang sama seperti TASK-06 (composable + component):

FILE 1 — src/composables/useTransactions.js (Application Logic):
Export fungsi useTransactions() yang return:
- transactions: ref([])
- summary: ref({ balance: 0, income: 0, expense: 0 })
- loading: ref(false)
- selectedMonth: ref(format bulan ini "YYYY-MM")
- fetchTransactions(): async — panggil api.getTransactions(selectedMonth)
- fetchSummary(): async — panggil api.getSummary(selectedMonth)
- fetchAll(): async — panggil keduanya secara parallel (Promise.all)
- createTransaction(data): async — panggil api.createTransaction(), lalu fetchAll()
- deleteTransaction(id): async — panggil api.deleteTransaction(), lalu fetchAll()
- setMonth(month: string) — update selectedMonth, panggil fetchAll()

FILE 2 — src/components/QuickAdd.vue (Presentational):
- <script setup>, defineEmits(["transaction-added"])
- Local form state dengan ref: type, amount, category, description, date
- Validasi: type, amount, category wajib — tampilkan pesan error inline
- Date default: new Date().toISOString().split("T")[0]
- Submit: panggil api.createTransaction() langsung (atau terima sebagai prop function)
- Emit "transaction-added" setelah sukses, reset semua field
- Tampilkan success feedback (class transisi opacity, bukan alert)
- Import formatRupiah dari utils/formatters.js jika diperlukan

FILE 3 — src/components/TransactionHistory.vue (Presentational):
- <script setup>
- defineProps({ transactions: Array, loading: Boolean, selectedMonth: String })
- defineEmits(["month-changed", "delete-transaction"])
- Dropdown bulan: generate 6 bulan terakhir + bulan ini dari computed
- Import formatRupiah dan formatDate dari utils/formatters.js
- Tabel: Tanggal | Deskripsi | Kategori | Jumlah | Aksi
- Jumlah: text-green-600 income (+Rp...), text-red-600 expense (-Rp...)
- Hapus: emit "delete-transaction" dengan id (konfirmasi window.confirm)
- Empty state dan loading state (skeleton rows dengan animate-pulse TailwindCSS)

Aturan wajib:
- Komponen tidak boleh punya state logic — gunakan props dan emit
- Semua formatting via utils/formatters.js
- Wajib <script setup> dengan defineProps dan defineEmits eksplisit
```

---

### TASK-08: App.vue Integration & Final Polish
**Prompt untuk AI:**
```
Buatkan src/App.vue sebagai root orchestration component.
App.vue hanya bertugas: menyambungkan composable dengan komponen, tidak ada logic sendiri.

Referensi pattern: https://vuejs.org/guide/components/events.html

Setup:
- <script setup>
- Import useTransactions() dari composables/useTransactions.js
- Destructure: transactions, summary, loading, selectedMonth, fetchAll,
  createTransaction, deleteTransaction, setMonth
- Panggil fetchAll() saat onMounted (import dari vue)

Template layout (single page, scroll vertikal):
- Header: "💼 FinanceBot" + tagline, full width, background putih, shadow
- Max-width container: max-w-4xl mx-auto px-4 py-6
- Section 1: <SummaryCards :balance :income :expense />
- Section 2: <ChatBox @transaction-added="fetchAll" />
- Section 3: <QuickAdd @transaction-added="fetchAll" />
- Section 4: <TransactionHistory
    :transactions :loading :selectedMonth
    @month-changed="setMonth"
    @delete-transaction="deleteTransaction" />
- Spacing antar section: space-y-6
- Background body: bg-gray-50

Aturan wajib:
- App.vue tidak boleh punya local state sendiri — semua dari composable
- Tidak ada API call langsung di App.vue
- Tidak ada logic kondisional yang kompleks di App.vue
- Semua komponen harus di-import eksplisit (tidak pakai auto-import)
```

---

### TASK-09: README & Environment Setup
**Prompt untuk AI:**
```
Buatkan README.md untuk project ini dengan section:

1. Overview: deskripsi singkat aplikasi
2. Prerequisites: Python 3.10+, Node.js 18+, Gemini API Key
3. Setup Backend:
   - cd backend
   - python -m venv venv && source venv/bin/activate
   - pip install -r requirements.txt
   - cp .env.example .env (isi GEMINI_API_KEY)
   - uvicorn main:app --reload
4. Setup Frontend:
   - cd frontend
   - npm install
   - npm run dev
5. Environment Variables: GEMINI_API_KEY
6. API Documentation: list semua endpoint
7. Cara Penggunaan Chatbot: contoh kalimat yang bisa digunakan

Juga buatkan file backend/.env.example:
GEMINI_API_KEY=your_gemini_api_key_here

Dan buatkan file backend/main.py final yang import semua router dan setup aplikasi lengkap.
```

---

## Execution Order

| # | Task | File Target | Est. |
|---|---|---|---|
| 1 | TASK-01 | backend/database.py, models.py, schemas.py | 30 mnt |
| 2 | TASK-02 | backend/routers/transactions.py | 30 mnt |
| 3 | TASK-03 | backend/services/gemini_service.py | 30 mnt |
| 4 | TASK-04 | backend/routers/chat.py | 30 mnt |
| 5 | TASK-05 | frontend setup + SummaryCards.vue | 45 mnt |
| 6 | TASK-06 | frontend/ChatBox.vue | 60 mnt |
| 7 | TASK-07 | QuickAdd.vue + TransactionHistory.vue | 45 mnt |
| 8 | TASK-08 | App.vue (integration) | 30 mnt |
| 9 | TASK-09 | README.md + .env.example + main.py | 20 mnt |

**Total Estimasi: ~6 jam kerja efektif**

---

## Notes

- Jalankan backend dulu sebelum frontend
- Untuk development, CORS di FastAPI di-set allow all origins
- Gemini API Key bisa didapat di: https://aistudio.google.com/app/apikey
- Model yang digunakan: `gemini-2.5-pro` (untuk text dan vision)
- SQLite file `db.sqlite3` akan ter-generate otomatis saat pertama run

---

## Last Work

- **Tanggal**: 17 Juli 2026
- **Branch**: `fix_category_and_settings_UI_17072026`
- **Pekerjaan**:
  - Memperbaiki sinkronisasi data kategori pada komponen Quick Add dengan mengubah sumber data (dari _hardcoded_ menjadi dinamis dari backend).
  - Menambahkan _sorting_ otomatis untuk list Kategori berdasarkan tipe pemasukan/pengeluaran dan urutan abjad, dengan "Lainnya" diposisikan di baris akhir.
  - Menyesuaikan UI di halaman Settings: form Tambah Sumber Uang Baru dan Tambah Kategori Baru dipindahkan posisinya agar berada tepat di atas list data masing-masing.
