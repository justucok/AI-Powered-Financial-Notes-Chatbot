const rupiahFormatter = new Intl.NumberFormat('id-ID')
const dateFormatter = new Intl.DateTimeFormat('id-ID', {
  day: 'numeric',
  month: 'short',
  year: 'numeric',
})
const monthFormatter = new Intl.DateTimeFormat('id-ID', {
  month: 'long',
  year: 'numeric',
})

export function formatRupiah(amount) {
  const numericAmount = Number(amount || 0)
  return `Rp ${rupiahFormatter.format(numericAmount)}`
}

export function formatDate(dateStr) {
  if (!dateStr) {
    return '-'
  }

  const date = new Date(dateStr)
  if (Number.isNaN(date.getTime())) {
    return '-'
  }

  return dateFormatter.format(date)
}

export function formatMonth(monthStr) {
  if (!monthStr) {
    return '-'
  }

  const date = new Date(`${monthStr}-01`)
  if (Number.isNaN(date.getTime())) {
    return '-'
  }

  return monthFormatter.format(date)
}
