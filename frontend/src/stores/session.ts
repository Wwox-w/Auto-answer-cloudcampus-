import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export interface Question {
  number: number
  type: string
  text: string
  answer?: string
  status: 'waiting' | 'solving' | 'solved' | 'filled' | 'error'
}

export const useSessionStore = defineStore('session', () => {
  const running = ref(false)
  const currentPage = ref(0)
  const questions = ref<Question[]>([])
  const logs = ref<string[]>([])
  const codeQuestions = ref<Question[]>([])
  const usage = ref({ prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 })

  const currentQuestion = computed(() =>
    questions.value.find(q => q.status === 'solving') || questions.value[questions.value.length - 1]
  )

  function addLog(msg: string) {
    const time = new Date().toLocaleTimeString()
    logs.value.push(`[${time}] ${msg}`)
  }

  function reset() {
    running.value = false
    currentPage.value = 0
    questions.value = []
    logs.value = []
    codeQuestions.value = []
    usage.value = { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 }
  }

  return { running, currentPage, questions, logs, codeQuestions, usage, currentQuestion, addLog, reset }
})
