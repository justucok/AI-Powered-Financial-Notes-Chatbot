<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  show: Boolean
})

const emit = defineEmits(['close'])

const activeTab = ref('navigasi')

const tabs = [
  { id: 'navigasi', icon: '🗂️', title: 'Menu Navigasi' },
  { id: 'chart', icon: '📊', title: 'Grafik & Chart' },
  { id: 'ringkasan', icon: '💳', title: 'Kartu Ringkasan' },
  { id: 'chatbot', icon: '🤖', title: 'Chatbot' },
  { id: 'tambah', icon: '➕', title: 'Cara Menambahkan' },
]

function handleClose() {
  emit('close')
}
</script>

<template>
  <div v-if="show" class="fixed inset-0 z-[70] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
    <div class="bg-white rounded-2xl w-full max-w-4xl shadow-2xl flex flex-col md:flex-row h-[85vh] overflow-hidden relative">
      
      <!-- Close Button (Absolute) -->
      <button @click="handleClose" 
              class="absolute top-4 right-4 z-10 w-8 h-8 flex items-center justify-center rounded-full bg-slate-100 hover:bg-slate-200 text-slate-500 hover:text-slate-700 transition-colors">
        ✕
      </button>

      <!-- Sidebar Tabs -->
      <div class="w-full md:w-64 bg-slate-50 border-r border-slate-200 flex flex-col shrink-0">
        <div class="p-6 border-b border-slate-200 shrink-0">
          <h2 class="text-xl font-bold text-slate-900 flex items-center gap-2">
            <span class="text-2xl">❓</span> Panduan
          </h2>
          <p class="text-xs text-slate-500 mt-1">Cara menggunakan aplikasi</p>
        </div>
        
        <div class="overflow-x-auto md:overflow-y-auto flex md:flex-col p-4 gap-2 flex-1 scrollbar-hide">
          <button v-for="tab in tabs" :key="tab.id"
                  @click="activeTab = tab.id"
                  :class="activeTab === tab.id ? 'bg-sky-100 text-sky-700 font-semibold shadow-sm' : 'hover:bg-slate-100 text-slate-600'"
                  class="flex items-center gap-3 px-4 py-3 rounded-xl transition-colors whitespace-nowrap text-left shrink-0">
            <span class="text-xl">{{ tab.icon }}</span>
            <span class="text-sm">{{ tab.title }}</span>
          </button>
        </div>
      </div>

      <!-- Content Area -->
      <div class="flex-1 overflow-y-auto p-6 md:p-8">
        
        <!-- Tab: Navigasi -->
        <div v-if="activeTab === 'navigasi'" class="space-y-6">
          <h3 class="text-2xl font-bold text-slate-900 mb-6 border-b pb-4">🗂️ Menu Navigasi</h3>
          
          <div class="space-y-4">
            <div class="bg-slate-50 p-4 rounded-xl border border-slate-100">
              <p class="font-bold text-slate-900 mb-1">🏠 Dashboard</p>
              <p class="text-slate-600 text-sm">Halaman utama yang berisi ringkasan keuangan dan fitur Chatbot AI untuk mencatat transaksi.</p>
            </div>
            <div class="bg-slate-50 p-4 rounded-xl border border-slate-100">
              <p class="font-bold text-slate-900 mb-1">➕ Tambah</p>
              <p class="text-slate-600 text-sm">Formulir manual untuk mencatat transaksi pengeluaran atau pemasukan baru jika Anda tidak ingin menggunakan Chatbot.</p>
            </div>
            <div class="bg-slate-50 p-4 rounded-xl border border-slate-100">
              <p class="font-bold text-slate-900 mb-1">📋 Riwayat</p>
              <p class="text-slate-600 text-sm">Daftar semua transaksi yang pernah Anda catat, dikelompokkan berdasarkan bulan. Anda dapat mengubah atau menghapus transaksi di sini.</p>
            </div>
            <div class="bg-slate-50 p-4 rounded-xl border border-slate-100">
              <p class="font-bold text-slate-900 mb-1">📊 Statistik</p>
              <p class="text-slate-600 text-sm">Visualisasi data keuangan Anda dalam bentuk grafik (harian/mingguan/bulanan) dan diagram persentase penggunaan per kategori.</p>
            </div>
            <div class="bg-slate-50 p-4 rounded-xl border border-slate-100">
              <p class="font-bold text-slate-900 mb-1">🎯 Budget</p>
              <p class="text-slate-600 text-sm">Pantau seberapa besar pengeluaran Anda dibandingkan dengan anggaran batas maksimal per bulan.</p>
            </div>
            <div class="bg-slate-50 p-4 rounded-xl border border-slate-100">
              <p class="font-bold text-slate-900 mb-1">⚙️ Pengaturan</p>
              <p class="text-slate-600 text-sm">Atur profil Anda, kelola sumber uang (dompet/bank), dan buat/hapus kategori transaksi kustom.</p>
            </div>
          </div>
        </div>

        <!-- Tab: Chart -->
        <div v-if="activeTab === 'chart'" class="space-y-6">
          <h3 class="text-2xl font-bold text-slate-900 mb-6 border-b pb-4">📊 Grafik & Chart</h3>
          
          <div class="space-y-6">
            <div>
              <h4 class="font-bold text-sky-700 mb-2">Tren Keuangan (Bar Chart)</h4>
              <p class="text-slate-600 text-sm leading-relaxed mb-3">
                Grafik batang ini menunjukkan jumlah pengeluaran atau pemasukan Anda seiring berjalannya waktu. Anda dapat mengubah mode tampilan ke:
              </p>
              <ul class="list-disc pl-5 space-y-2 text-sm text-slate-600">
                <li><strong>Harian:</strong> Menampilkan total per hari dalam bulan yang dipilih.</li>
                <li><strong>Mingguan:</strong> Menampilkan total per minggu (Minggu 1, Minggu 2, dst) dalam bulan yang dipilih.</li>
                <li><strong>Bulanan:</strong> Menampilkan tren total bulanan selama 6 bulan terakhir.</li>
              </ul>
            </div>
            
            <div class="bg-slate-100 h-px w-full my-4"></div>
            
            <div>
              <h4 class="font-bold text-sky-700 mb-2">Penggunaan Kategori (Pie Chart)</h4>
              <p class="text-slate-600 text-sm leading-relaxed">
                Diagram lingkaran (doughnut) ini memvisualisasikan porsi pengeluaran (atau pemasukan) Anda berdasarkan kategorinya di bulan tertentu. Berguna untuk melihat ke mana uang Anda paling banyak dihabiskan (misalnya: Makanan 40%, Transportasi 20%).
              </p>
            </div>
          </div>
        </div>

        <!-- Tab: Ringkasan -->
        <div v-if="activeTab === 'ringkasan'" class="space-y-6">
          <h3 class="text-2xl font-bold text-slate-900 mb-6 border-b pb-4">💳 Kartu Ringkasan</h3>
          
          <p class="text-slate-600 text-sm mb-6">
            Di bagian atas halaman Dashboard, Anda akan melihat tiga kartu utama yang menunjukkan kondisi keuangan Anda saat ini.
          </p>

          <div class="grid grid-cols-1 gap-4">
            <div class="bg-blue-50/50 p-4 rounded-xl border border-blue-100 flex gap-4">
              <div class="text-3xl mt-1">💰</div>
              <div>
                <p class="font-bold text-blue-900">Total Saldo</p>
                <p class="text-slate-600 text-sm mt-1">
                  Selisih antara <strong>seluruh pemasukan</strong> dikurangi <strong>seluruh pengeluaran</strong> dari awal menggunakan aplikasi sampai hari ini. Ini adalah perkiraan total uang yang Anda miliki.
                </p>
              </div>
            </div>
            <div class="bg-emerald-50/50 p-4 rounded-xl border border-emerald-100 flex gap-4">
              <div class="text-3xl mt-1">📈</div>
              <div>
                <p class="font-bold text-emerald-900">Pemasukan Bulan Ini</p>
                <p class="text-slate-600 text-sm mt-1">
                  Total uang yang masuk (gaji, bonus, dll) khusus pada bulan yang sedang berjalan (tanggal 1 sampai saat ini).
                </p>
              </div>
            </div>
            <div class="bg-rose-50/50 p-4 rounded-xl border border-rose-100 flex gap-4">
              <div class="text-3xl mt-1">📉</div>
              <div>
                <p class="font-bold text-rose-900">Pengeluaran Bulan Ini</p>
                <p class="text-slate-600 text-sm mt-1">
                  Total uang yang keluar khusus pada bulan yang sedang berjalan.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Tab: Chatbot -->
        <div v-if="activeTab === 'chatbot'" class="space-y-6">
          <h3 class="text-2xl font-bold text-slate-900 mb-6 border-b pb-4">🤖 Kemampuan Chatbot AI</h3>
          
          <p class="text-slate-600 text-sm mb-6">
            FinanceBot dilengkapi dengan asisten AI pintar (Gemini) yang bisa memahami berbagai jenis perintah dan lampiran.
          </p>

          <div class="space-y-6">
            <div>
              <h4 class="font-bold text-sky-700 mb-2 flex items-center gap-2"><span class="text-xl">⌨️</span> Teks Natural</h4>
              <p class="text-slate-600 text-sm mb-2">
                Ketikkan pengeluaran atau pemasukan dengan bahasa sehari-hari. AI akan otomatis mengekstrak <strong>nominal</strong> dan <strong>kategori</strong>.
              </p>
              <div class="bg-slate-900 text-slate-300 p-3 rounded-lg text-sm font-mono">
                "Hari ini saya beli makan siang habis 35 ribu"
                <br>
                "Baru dapet gaji bulan ini 5.000.000"
              </div>
            </div>

            <div>
              <h4 class="font-bold text-sky-700 mb-2 flex items-center gap-2"><span class="text-xl">📷</span> Foto Struk / Nota</h4>
              <p class="text-slate-600 text-sm mb-2">
                Klik ikon attachment (📎), pilih <strong>Image</strong>, dan unggah foto struk belanja Anda. AI akan membaca struk tersebut dan mencatat total transaksinya otomatis.
              </p>
            </div>

            <div>
              <h4 class="font-bold text-sky-700 mb-2 flex items-center gap-2"><span class="text-xl">📄</span> Dokumen E-Statement (PDF)</h4>
              <p class="text-slate-600 text-sm mb-2">
                Klik ikon attachment (📎), pilih <strong>PDF</strong>, dan unggah mutasi rekening bank Anda. Jika PDF dikunci dengan password, masukkan password Anda di form yang muncul. AI akan memproses semua baris transaksi di dokumen tersebut dan menampilkannya agar bisa Anda pilih mana yang mau disimpan.
              </p>
            </div>
          </div>
        </div>

        <!-- Tab: Tambah -->
        <div v-if="activeTab === 'tambah'" class="space-y-6">
          <h3 class="text-2xl font-bold text-slate-900 mb-6 border-b pb-4">➕ Cara Menambahkan Data</h3>
          
          <div class="space-y-6">
            <div>
              <h4 class="font-bold text-sky-700 mb-2">Kategori Baru</h4>
              <p class="text-slate-600 text-sm">
                Buka menu <strong>Pengaturan</strong> (⚙️), lalu pilih tab <strong>🏷️ Categories</strong>. Masukkan nama kategori baru (misal: "Netflix"), pilih jenisnya (Pengeluaran), dan masukkan emoji sebagai ikon (misal: "🎬").
              </p>
            </div>

            <div>
              <h4 class="font-bold text-sky-700 mb-2">Sumber Uang (Dompet / Bank)</h4>
              <p class="text-slate-600 text-sm">
                Secara default, jika Anda tidak memiliki sumber uang, transaksi akan disimpan tanpa mengurangi dompet tertentu. Untuk membuat dompet/rekening (misal: BCA, OVO, Uang Tunai):
              </p>
              <p class="text-slate-600 text-sm mt-2">
                Buka menu <strong>Pengaturan</strong> (⚙️), pilih tab <strong>💰 Fund Sources</strong>, dan tambahkan sumber baru beserta saldo awalnya. Setelah ini, setiap kali Anda menambah transaksi via Chatbot, Anda akan diminta memilih sumber uang mana yang digunakan.
              </p>
            </div>

            <div>
              <h4 class="font-bold text-sky-700 mb-2">Transaksi Manual</h4>
              <p class="text-slate-600 text-sm">
                Jika AI salah menebak atau Anda sedang offline, Anda selalu bisa memasukkan transaksi secara manual lewat menu <strong>➕ Tambah</strong> di navigasi samping.
              </p>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>
