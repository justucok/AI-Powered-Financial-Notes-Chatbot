<script setup>
import { onMounted, ref, watch, computed } from 'vue'
import { formatRupiah } from '../utils/formatters'
import { useAuth } from '../composables/useAuth'
import { useSettings } from '../composables/useSettings'
import { useFundSources } from '../composables/useFundSources'
import { useCategories } from '../composables/useCategories'
import { useBudget } from '../composables/useBudget'

const { logout } = useAuth()
const { profile, loading: profileLoading, error: profileError, successMessage, fetchProfile, updatePassword, updateProfileDetails, removeAccount, clearMessages } = useSettings()
const { sources, loading: sourceLoading, error: sourceError, fetchSources, addSource, removeSource, adjustBalance } = useFundSources()
const { categories, loading: categoryLoading, fetchCategories, createCategory, deleteCategory } = useCategories()
const { summary: budgetSummary, fetchBudgetSummary, updateBudget, updateCategoryBudget, loading: budgetLoading } = useBudget()

const activeTab = ref('profile') // 'profile', 'sources', 'categories', 'security', 'budget'

const today = new Date()
const currentMonthKey = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`
const budgetMonth = ref(currentMonthKey)

const tempTotalBudget = ref(0)
const tempCategoryBudgets = ref({})

// Sync temp values with fetched summary
watch(budgetSummary, (newSummary) => {
  tempTotalBudget.value = newSummary.total_budget || 0
  
  const temps = {}
  newSummary.category_budgets.forEach(cb => {
    temps[cb.category_name] = cb.budget_amount
  })
  tempCategoryBudgets.value = temps
}, { deep: true })

watch([activeTab, budgetMonth], async () => {
  if (activeTab.value === 'budget') {
    await fetchBudgetSummary(budgetMonth.value)
  }
})

const expenseCategories = computed(() => {
  return categories.value.filter(c => c.type === 'expense')
})

function getCategoryBudgetAmount(categoryName) {
  const cb = budgetSummary.value.category_budgets.find(item => item.category_name === categoryName)
  return cb ? cb.budget_amount : 0
}

function updateTempCategoryBudget(categoryName, value) {
  tempCategoryBudgets.value[categoryName] = parseFloat(value) || 0
}

async function handleSaveTotalBudget() {
  await updateBudget(budgetMonth.value, tempTotalBudget.value)
}

async function handleSaveCategoryBudget(categoryName) {
  const amt = tempCategoryBudgets.value[categoryName] !== undefined 
    ? tempCategoryBudgets.value[categoryName] 
    : getCategoryBudgetAmount(categoryName)
  await updateCategoryBudget(budgetMonth.value, categoryName, amt)
}

// Form states
const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')

const showCurrentPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)
const showDeletePassword = ref(false)

const deletePassword = ref('')
const showDeleteConfirm = ref(false)

const newSource = ref({
  name: '',
  type: 'bank',
  icon: '',
  initial_balance: 0,
})

const isEditingProfile = ref(false)
const editProfileForm = ref({ full_name: '', nickname: '' })

function startEditProfile() {
  editProfileForm.value.full_name = profile.value.full_name
  editProfileForm.value.nickname = profile.value.nickname
  isEditingProfile.value = true
}

async function handleSaveProfile() {
  const success = await updateProfileDetails(editProfileForm.value.full_name, editProfileForm.value.nickname)
  if (success) {
    isEditingProfile.value = false
    window.dispatchEvent(new Event('storage')) // Simple way to trigger updates if components listen, otherwise reload is needed.
    setTimeout(() => {
      window.location.reload()
    }, 1500)
  }
}

onMounted(async () => {
  await Promise.all([
    fetchProfile(),
    fetchSources(),
    fetchCategories()
  ])
})

async function handlePasswordSubmit() {
  if (newPassword.value !== confirmPassword.value) {
    alert('Konfirmasi password baru tidak cocok!')
    return
  }
  await updatePassword(currentPassword.value, newPassword.value)
  if (successMessage.value) {
    currentPassword.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
  }
}

async function handleDeleteAccount() {
  if (!deletePassword.value) {
    alert('Masukkan password untuk menghapus akun.')
    return
  }
  try {
    await removeAccount(deletePassword.value)
    alert('Akun berhasil dihapus.')
    logout()
  } catch (err) {
    // Error is handled by composable
  }
}

async function handleAddSource() {
  if (!newSource.value.name) {
    alert('Nama sumber uang wajib diisi.')
    return
  }
  await addSource({ ...newSource.value })
  if (!sourceError.value) {
    newSource.value = { name: '', type: 'bank', icon: '', initial_balance: 0 }
  }
}

const newCategory = ref({
  name: '',
  type: 'expense',
  icon: '',
})

async function handleAddCategory() {
  if (!newCategory.value.name) {
    alert('Nama kategori wajib diisi.')
    return
  }
  await createCategory({ ...newCategory.value })
  newCategory.value = { name: '', type: 'expense', icon: '' }
}

const editingSourceId = ref(null)
const editTargetBalance = ref(0)

const currentEditSource = computed(() =>
  sources.value.find(s => s.id === editingSourceId.value)
)
const balanceDelta = computed(() => {
  if (!currentEditSource.value) return 0
  return editTargetBalance.value - currentEditSource.value.balance
})

function startEditBalance(source) {
  editingSourceId.value = source.id
  editTargetBalance.value = source.balance
}

async function handleAdjustBalance() {
  const result = await adjustBalance(editingSourceId.value, editTargetBalance.value)
  if (!sourceError.value) {
    editingSourceId.value = null
    successMessage.value = result.message || 'Saldo berhasil disesuaikan.'
  }
}

</script>

<template>
  <div class="px-4 py-6 md:p-8 space-y-6 pb-24">
    <!-- Header -->
    <header class="flex flex-col gap-1">
      <p class="text-xs font-semibold uppercase tracking-[0.24em] text-sky-600">Pengaturan</p>
      <h1 class="text-2xl font-bold tracking-tight text-slate-900">Konfigurasi Akun</h1>
      <p class="text-sm text-slate-500">Kelola profil, sumber uang, dan keamanan akun Anda.</p>
    </header>

    <div class="rounded-3xl border border-white/70 bg-white/80 p-5 shadow-[0_24px_80px_rgba(15,23,42,0.06)] backdrop-blur sm:p-8">
        
        <!-- Tabs -->
        <div class="flex border-b border-gray-100 overflow-x-auto">
          <button @click="activeTab = 'profile'; clearMessages()" 
                  class="flex-1 py-4 px-6 text-sm font-medium border-b-2 whitespace-nowrap transition-colors"
                  :class="activeTab === 'profile' ? 'border-blue-600 text-blue-600 bg-blue-50/50' : 'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50'">
            👤 Profile
          </button>
          <button @click="activeTab = 'sources'; clearMessages()" 
                  class="flex-1 py-4 px-6 text-sm font-medium border-b-2 whitespace-nowrap transition-colors"
                  :class="activeTab === 'sources' ? 'border-blue-600 text-blue-600 bg-blue-50/50' : 'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50'">
            💰 Fund Sources
          </button>
          <button @click="activeTab = 'categories'; clearMessages()" 
                  class="flex-1 py-4 px-6 text-sm font-medium border-b-2 whitespace-nowrap transition-colors"
                  :class="activeTab === 'categories' ? 'border-blue-600 text-blue-600 bg-blue-50/50' : 'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50'">
            🏷️ Categories
          </button>
          <button @click="activeTab = 'budget'; clearMessages()" 
                  class="flex-1 py-4 px-6 text-sm font-medium border-b-2 whitespace-nowrap transition-colors"
                  :class="activeTab === 'budget' ? 'border-blue-600 text-blue-600 bg-blue-50/50' : 'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50'">
            🎯 Budget
          </button>
        </div>

        <div class="p-6">
          
          <!-- Alerts -->
          <div v-if="profileError || sourceError" class="mb-6 p-4 bg-red-50 text-red-700 rounded-xl border border-red-100 flex items-start">
            <span>⚠️</span>
            <p class="ml-2 text-sm">{{ profileError || sourceError }}</p>
          </div>
          <div v-if="successMessage" class="mb-6 p-4 bg-green-50 text-green-700 rounded-xl border border-green-100 flex items-start">
            <span>✅</span>
            <p class="ml-2 text-sm">{{ successMessage }}</p>
          </div>

          <!-- TAB: PROFIL -->
          <div v-show="activeTab === 'profile'" class="space-y-6">
            <div v-if="profileLoading" class="flex justify-center p-8">
              <span class="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full"></span>
            </div>
            <div v-else-if="profile" class="space-y-6">
              <div class="flex flex-col sm:flex-row items-center sm:items-start gap-6 bg-slate-50 p-6 rounded-2xl border border-slate-100">
                <div class="flex h-24 w-24 shrink-0 items-center justify-center rounded-2xl bg-sky-600 text-4xl font-bold text-white shadow-lg shadow-sky-600/30">
                  {{ profile.nickname ? profile.nickname[0].toUpperCase() : '?' }}
                </div>
                <div class="flex-1 w-full text-center sm:text-left">
                  <h3 class="text-2xl font-bold text-slate-900">{{ profile.full_name }}</h3>
                  <p class="text-slate-500 mb-6">{{ profile.email }}</p>
                  
                  
                  <div v-if="!isEditingProfile">
                    <div class="grid grid-cols-2 gap-4 pt-6 border-t border-slate-200 text-left">
                      <div>
                        <p class="text-xs text-slate-400 uppercase tracking-wider mb-1 font-semibold">Nama Panggilan</p>
                        <p class="font-medium text-slate-800">{{ profile.nickname }}</p>
                      </div>
                      <div>
                        <p class="text-xs text-slate-400 uppercase tracking-wider mb-1 font-semibold">Status</p>
                        <p class="font-medium text-emerald-600 flex items-center gap-1.5 sm:justify-start">
                          <span class="relative flex h-2.5 w-2.5 shrink-0">
                            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                            <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
                          </span>
                          Aktif
                        </p>
                      </div>
                    </div>
                  </div>
                  
                  <div v-else class="mt-4 pt-4 border-t border-slate-200">
                    <div class="space-y-4">
                      <div>
                        <label class="block text-sm font-medium text-slate-700 mb-1">Nama Lengkap</label>
                        <input v-model="editProfileForm.full_name" type="text" required
                               class="w-full rounded-lg border-slate-300 bg-white text-slate-900 shadow-sm focus:border-sky-500 focus:ring-sky-500 px-4 py-2">
                      </div>
                      <div>
                        <label class="block text-sm font-medium text-slate-700 mb-1">Nama Panggilan</label>
                        <input v-model="editProfileForm.nickname" type="text" required
                               class="w-full rounded-lg border-slate-300 bg-white text-slate-900 shadow-sm focus:border-sky-500 focus:ring-sky-500 px-4 py-2">
                      </div>
                      <div class="flex gap-3 pt-2">
                        <button @click="handleSaveProfile" :disabled="profileLoading"
                                class="px-5 py-2 bg-sky-600 text-white text-sm font-medium rounded-xl hover:bg-sky-700 transition-colors disabled:opacity-50">
                          Simpan
                        </button>
                        <button @click="isEditingProfile = false" 
                                class="px-5 py-2 bg-slate-200 text-slate-700 text-sm font-medium rounded-xl hover:bg-slate-300 transition-colors">
                          Batal
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div class="flex justify-between items-center gap-2 mt-4">
                <button v-if="!isEditingProfile" @click="startEditProfile" class="flex items-center justify-center gap-1.5 px-3 py-2 sm:px-5 sm:py-2.5 text-xs sm:text-sm font-semibold text-sky-600 bg-sky-50 hover:bg-sky-100 rounded-xl transition-colors">
                  <span>✏️</span> Edit Profil
                </button>
                <div v-else></div> <!-- Spacer -->
                
                <button @click="logout" class="flex items-center justify-center gap-1.5 px-3 py-2 sm:px-5 sm:py-2.5 text-xs sm:text-sm font-semibold text-rose-600 bg-rose-50 hover:bg-rose-100 rounded-xl transition-colors">
                  <span class="text-base sm:text-lg leading-none">↩</span> Keluar
                </button>
              </div>

              <hr class="border-gray-100 my-8">

              <!-- Ubah Password -->
              <div class="space-y-4 w-full">
                <h3 class="text-lg font-bold text-gray-900">Ubah Password</h3>
                <form @submit.prevent="handlePasswordSubmit" class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Password Saat Ini</label>
                    <div class="relative">
                      <input v-model="currentPassword" :type="showCurrentPassword ? 'text' : 'password'" required
                             class="w-full rounded-lg border-gray-300 bg-white text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2 pr-10">
                      <button type="button" @click="showCurrentPassword = !showCurrentPassword"
                              class="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600 focus:outline-none">
                        <span v-if="showCurrentPassword">👁️‍🗨️</span><span v-else>👁️</span>
                      </button>
                    </div>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Password Baru</label>
                    <div class="relative">
                      <input v-model="newPassword" :type="showNewPassword ? 'text' : 'password'" required minlength="6"
                             class="w-full rounded-lg border-gray-300 bg-white text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2 pr-10">
                      <button type="button" @click="showNewPassword = !showNewPassword"
                              class="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600 focus:outline-none">
                        <span v-if="showNewPassword">👁️‍🗨️</span><span v-else>👁️</span>
                      </button>
                    </div>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Konfirmasi Password Baru</label>
                    <div class="relative">
                      <input v-model="confirmPassword" :type="showConfirmPassword ? 'text' : 'password'" required minlength="6"
                             class="w-full rounded-lg border-gray-300 bg-white text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2 pr-10">
                      <button type="button" @click="showConfirmPassword = !showConfirmPassword"
                              class="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600 focus:outline-none">
                        <span v-if="showConfirmPassword">👁️‍🗨️</span><span v-else>👁️</span>
                      </button>
                    </div>
                  </div>
                  <button type="submit" :disabled="profileLoading"
                          class="w-full sm:w-auto px-6 py-2.5 bg-gray-900 text-white font-medium rounded-xl hover:bg-gray-800 transition-colors disabled:opacity-50">
                    Simpan Password Baru
                  </button>
                </form>
              </div>

              <hr class="border-gray-100 my-8">

              <!-- Hapus Akun -->
              <div class="bg-red-50 p-4 sm:p-6 rounded-2xl border border-red-100">
                <h3 class="text-base sm:text-lg font-bold text-red-700 mb-1 sm:mb-2">Hapus Akun Permanen</h3>
                <p class="text-xs sm:text-sm text-red-600/80 mb-4">
                  Tindakan ini tidak dapat dibatalkan. Semua data transaksi dan profil Anda akan dihapus selamanya dari sistem.
                </p>
                
                <div v-if="!showDeleteConfirm">
                  <button @click="showDeleteConfirm = true" 
                          class="w-full sm:w-auto px-4 py-2 sm:px-6 sm:py-2.5 text-sm sm:text-base bg-red-600 text-white font-medium rounded-xl hover:bg-red-700 transition-colors shadow-sm shadow-red-200">
                    Hapus Akun Saya
                  </button>
                </div>
                <div v-else class="space-y-3 sm:space-y-4 max-w-md bg-white p-3 sm:p-4 rounded-xl border border-red-200 shadow-sm">
                  <p class="text-sm sm:text-base font-bold text-red-600">Peringatan Terakhir!</p>
                  <p class="text-xs sm:text-sm text-gray-600">Masukkan password Anda untuk mengonfirmasi penghapusan akun.</p>
                  <div class="relative">
                    <input v-model="deletePassword" :type="showDeletePassword ? 'text' : 'password'" placeholder="Password Anda"
                           class="w-full text-sm sm:text-base rounded-lg border-red-300 focus:border-red-500 focus:ring-red-500 px-3 py-2 sm:px-4 sm:py-2 bg-white text-gray-900 pr-10">
                    <button type="button" @click="showDeletePassword = !showDeletePassword"
                            class="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600 focus:outline-none">
                      <span v-if="showDeletePassword">👁️‍🗨️</span><span v-else>👁️</span>
                    </button>
                  </div>
                  <div class="flex flex-col sm:flex-row gap-2 sm:gap-3 sm:space-x-0">
                    <button @click="handleDeleteAccount" :disabled="profileLoading || !deletePassword"
                            class="w-full sm:flex-1 px-4 py-2 text-sm sm:text-base bg-red-600 text-white font-medium rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50">
                      Konfirmasi Hapus
                    </button>
                    <button @click="showDeleteConfirm = false; deletePassword = ''" 
                            class="w-full sm:flex-1 px-4 py-2 text-sm sm:text-base bg-gray-100 text-gray-700 font-medium rounded-lg hover:bg-gray-200 transition-colors">
                      Batal
                    </button>
                  </div>
                </div>
              </div>

            </div>
          </div>

          <!-- TAB: SUMBER UANG -->
          <div v-show="activeTab === 'sources'" class="space-y-8">
            
            <!-- List Sources -->
            <div>
              <h3 class="text-lg font-bold text-gray-900 mb-4">Sumber Uang Anda</h3>
              <div v-if="sourceLoading && !sources.length" class="flex justify-center p-4">
                <span class="animate-spin h-6 w-6 border-2 border-blue-600 border-t-transparent rounded-full"></span>
              </div>
              <div v-else-if="sources.length === 0" class="text-center p-8 bg-gray-50 rounded-xl border border-dashed border-gray-300">
                <p class="text-gray-500">Belum ada sumber uang.</p>
              </div>
              <div v-else class="space-y-3">
                <div v-for="source in sources" :key="source.id" 
                     class="bg-gray-50 rounded-xl border border-gray-100 overflow-hidden">
                  
                  <!-- Normal View -->
                  <div v-if="editingSourceId !== source.id" class="flex items-center justify-between p-4">
                    <div class="flex items-center space-x-3">
                      <span class="text-2xl">{{ source.icon || '💰' }}</span>
                      <div>
                        <p class="font-bold text-gray-900">{{ source.name }}</p>
                        <p class="text-xs text-gray-500 capitalize">{{ source.type }}</p>
                      </div>
                    </div>
                    <div class="flex items-center space-x-4">
                      <div class="text-right">
                        <p class="text-xs text-gray-500">Saldo</p>
                        <p class="font-bold text-blue-600">{{ formatRupiah(source.balance) }}</p>
                      </div>
                      <div class="flex items-center border-l border-gray-200 pl-4 space-x-1">
                        <button @click="startEditBalance(source)" 
                                class="p-2 text-blue-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                                title="Ubah Saldo">
                          ✏️
                        </button>
                        <button @click="removeSource(source.id)" 
                                class="p-2 text-red-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                title="Hapus Sumber Uang">
                          🗑️
                        </button>
                      </div>
                    </div>
                  </div>

                  <!-- Edit View -->
                  <div v-else class="p-4 bg-white border-b-2 border-blue-500">
                    <div class="flex items-center space-x-3 mb-4 pb-4 border-b border-gray-100">
                      <span class="text-2xl">{{ source.icon || '💰' }}</span>
                      <div>
                        <p class="font-bold text-gray-900">{{ source.name }}</p>
                        <p class="text-xs text-gray-500 capitalize">Saldo Saat Ini: {{ formatRupiah(source.balance) }}</p>
                      </div>
                    </div>
                    
                    <div class="mb-4">
                      <label class="block text-sm font-medium text-gray-700 mb-1">Ubah Saldo Menjadi</label>
                      <input v-model.number="editTargetBalance" type="number" step="1" required
                             class="w-full rounded-lg border-gray-300 bg-gray-50 text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2 font-mono text-lg">
                    </div>

                    <div class="p-3 rounded-lg text-sm mb-4"
                         :class="{
                           'bg-gray-50 text-gray-600': balanceDelta === 0,
                           'bg-green-50 text-green-700': balanceDelta > 0,
                           'bg-red-50 text-red-700': balanceDelta < 0
                         }">
                      <div v-if="balanceDelta === 0">ℹ️ Tidak ada perubahan saldo diperlukan.</div>
                      <div v-else-if="balanceDelta > 0">
                        ⬆️ Selisih: <strong>+{{ formatRupiah(balanceDelta) }}</strong><br>
                        <span class="text-xs opacity-90">Akan dibuat transaksi <strong>INCOME</strong> secara otomatis (Adjustment).</span>
                      </div>
                      <div v-else>
                        ⬇️ Selisih: <strong>-{{ formatRupiah(Math.abs(balanceDelta)) }}</strong><br>
                        <span class="text-xs opacity-90">Akan dibuat transaksi <strong>EXPENSE</strong> secara otomatis (Adjustment).</span>
                      </div>
                    </div>

                    <div class="flex gap-2 justify-end">
                      <button @click="editingSourceId = null" 
                              class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors">
                        Batal
                      </button>
                      <button @click="handleAdjustBalance" :disabled="sourceLoading"
                              class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50">
                        Simpan Perubahan
                      </button>
                    </div>
                  </div>

                </div>
              </div>
            </div>

            <!-- Add Source Form -->
            <div class="bg-blue-50 p-5 rounded-2xl border border-blue-100">
              <h4 class="font-bold text-blue-900 mb-4">Tambah Sumber Baru</h4>
              <form @submit.prevent="handleAddSource" class="space-y-4">
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Nama</label>
                    <input v-model="newSource.name" type="text" placeholder="Misal: Bank Mandiri" required
                           class="w-full rounded-lg border-gray-300 bg-white text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2">
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Tipe</label>
                    <select v-model="newSource.type"
                            class="w-full rounded-lg border-gray-300 bg-white text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2">
                      <option value="bank">Bank</option>
                      <option value="ewallet">E-Wallet</option>
                      <option value="cash">Uang Tunai</option>
                      <option value="other">Lainnya</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Ikon (Emoji)</label>
                    <input v-model="newSource.icon" type="text" placeholder="🏦"
                           class="w-full rounded-lg border-gray-300 bg-white text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2">
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Saldo Awal (Rp)</label>
                    <input v-model.number="newSource.initial_balance" type="number" min="0" required
                           class="w-full rounded-lg border-gray-300 bg-white text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2">
                  </div>
                </div>
                <button type="submit" :disabled="sourceLoading"
                        class="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-xl shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50">
                  + Tambah Sumber Uang
                </button>
              </form>
            </div>
          </div>

          <!-- TAB: KATEGORI -->
          <div v-show="activeTab === 'categories'" class="space-y-8">
            
            <!-- List Categories -->
            <div>
              <h3 class="text-lg font-bold text-gray-900 mb-4">Kategori Transaksi</h3>
              <div v-if="categoryLoading && !categories.length" class="flex justify-center p-4">
                <span class="animate-spin h-6 w-6 border-2 border-blue-600 border-t-transparent rounded-full"></span>
              </div>
              <div v-else-if="categories.length === 0" class="text-center p-8 bg-gray-50 rounded-xl border border-dashed border-gray-300">
                <p class="text-gray-500">Belum ada kategori.</p>
              </div>
              <div v-else class="space-y-3">
                <div v-for="category in categories" :key="category.id" 
                     class="flex items-center justify-between p-4 bg-gray-50 rounded-xl border border-gray-100">
                  <div class="flex items-center space-x-3">
                    <span class="text-2xl">{{ category.icon || '🏷️' }}</span>
                    <div>
                      <p class="font-bold text-gray-900">{{ category.name }}</p>
                      <p class="text-xs text-gray-500 capitalize">
                        <span :class="category.type === 'income' ? 'text-emerald-600' : 'text-rose-600'">
                          {{ category.type === 'income' ? 'Pemasukan' : 'Pengeluaran' }}
                        </span>
                      </p>
                    </div>
                  </div>
                  <button @click="deleteCategory(category.id)" 
                          class="p-2 text-red-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                          title="Hapus Kategori">
                    🗑️
                  </button>
                </div>
              </div>
            </div>

            <!-- Add Category Form -->
            <div class="bg-blue-50 p-5 rounded-2xl border border-blue-100">
              <h4 class="font-bold text-blue-900 mb-4">Tambah Kategori Baru</h4>
              <form @submit.prevent="handleAddCategory" class="space-y-4">
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Nama Kategori</label>
                    <input v-model="newCategory.name" type="text" placeholder="Misal: Peliharaan" required
                           class="w-full rounded-lg border-gray-300 bg-white text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2">
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Tipe</label>
                    <select v-model="newCategory.type"
                            class="w-full rounded-lg border-gray-300 bg-white text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2">
                      <option value="expense">Pengeluaran</option>
                      <option value="income">Pemasukan</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Ikon (Emoji)</label>
                    <input v-model="newCategory.icon" type="text" placeholder="🐶"
                           class="w-full rounded-lg border-gray-300 bg-white text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 px-4 py-2">
                  </div>
                </div>
                <button type="submit" :disabled="categoryLoading"
                        class="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-xl shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50">
                  + Tambah Kategori
                </button>
              </form>
            </div>
          </div>

          <!-- TAB: ANGGARAN (BUDGET) -->
          <div v-show="activeTab === 'budget'" class="space-y-8">
            <!-- Month Selector Removed -->
            <!-- Set Total Monthly Budget -->
            <div class="bg-blue-50/50 p-5 rounded-2xl border border-blue-100">
              <h4 class="font-bold text-blue-900 mb-2">Total Anggaran Bulanan</h4>
              <p class="text-xs text-blue-700 mb-4">Batas maksimal pengeluaran gabungan untuk semua bulan.</p>
              
              <div class="flex flex-col sm:flex-row gap-3">
                <div class="relative flex-1">
                  <span class="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400 text-sm font-semibold">Rp</span>
                  <input 
                    type="number" 
                    v-model.number="tempTotalBudget" 
                    placeholder="Batas Anggaran Total"
                    class="w-full rounded-lg border-gray-300 bg-white text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 pl-10 pr-4 py-2"
                  />
                </div>
                <button 
                  @click="handleSaveTotalBudget" 
                  :disabled="budgetLoading"
                  class="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl transition disabled:opacity-50"
                >
                  Simpan
                </button>
              </div>
            </div>

            <!-- Set Category Budget -->
            <div>
              <h4 class="font-bold text-slate-800 mb-2">Alokasi Anggaran per Kategori</h4>
              <p class="text-xs text-slate-500 mb-4">Bagikan total anggaran ke masing-masing kategori pengeluaran.</p>

              <div v-if="expenseCategories.length === 0" class="text-center p-8 bg-gray-50 rounded-xl border border-dashed border-gray-300 text-gray-500">
                Belum ada kategori pengeluaran. Tambahkan kategori pengeluaran terlebih dahulu pada tab "Kategori".
              </div>

              <div v-else class="space-y-4">
                <div 
                  v-for="cat in expenseCategories" 
                  :key="cat.id" 
                  class="flex flex-col sm:flex-row sm:items-center justify-between p-4 bg-slate-50 border border-slate-100 rounded-xl gap-3"
                >
                  <div class="flex items-center space-x-3">
                    <span class="text-2xl">{{ cat.icon || '🏷️' }}</span>
                    <div>
                      <p class="font-bold text-slate-800">{{ cat.name }}</p>
                      <p class="text-xs text-slate-500">
                        Anggaran Saat Ini: {{ formatRupiah(getCategoryBudgetAmount(cat.name)) }}
                      </p>
                    </div>
                  </div>
                  
                  <div class="flex items-center gap-2">
                    <div class="relative w-36">
                      <span class="absolute inset-y-0 left-0 flex items-center pl-2.5 text-slate-400 text-xs font-semibold">Rp</span>
                      <input 
                        type="number" 
                        :value="tempCategoryBudgets[cat.name] !== undefined ? tempCategoryBudgets[cat.name] : getCategoryBudgetAmount(cat.name)"
                        @input="e => updateTempCategoryBudget(cat.name, e.target.value)"
                        class="w-full text-sm rounded-lg border-gray-300 bg-white text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 pl-8 pr-2 py-1.5"
                      />
                    </div>
                    <button 
                      @click="handleSaveCategoryBudget(cat.name)" 
                      :disabled="budgetLoading"
                      class="px-4 py-1.5 bg-slate-800 hover:bg-slate-900 text-white text-sm font-medium rounded-lg transition disabled:opacity-50"
                    >
                      Set
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

      </div>
    </div>
  </div>
</template>
