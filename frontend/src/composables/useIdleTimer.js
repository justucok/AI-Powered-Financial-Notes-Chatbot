import { onBeforeUnmount, onMounted } from 'vue'

const IDLE_MS = 30 * 60 * 1000 // 30 minutes

export function useIdleTimer(onTimeout) {
  let timer = null
  const events = ['mousedown', 'keydown', 'scroll', 'touchstart']

  function resetTimer() {
    clearTimeout(timer)
    timer = setTimeout(onTimeout, IDLE_MS)
  }

  onMounted(() => {
    events.forEach(e => window.addEventListener(e, resetTimer, { passive: true }))
    resetTimer()
  })

  onBeforeUnmount(() => {
    events.forEach(e => window.removeEventListener(e, resetTimer))
    clearTimeout(timer)
  })
}
