import { ref } from 'vue'
import { defineStore } from 'pinia'

export interface LLMConfig {
  llm_api_base: string
  llm_api_key: string
  llm_model: string
}

export interface BrowserConfig {
  headless: boolean
  slow_mo: number
  page_timeout: number
}

export const useConfigStore = defineStore('config', () => {
  const llm = ref<LLMConfig>({ llm_api_base: '', llm_api_key: '', llm_model: '' })
  const browser = ref<BrowserConfig>({ headless: false, slow_mo: 300, page_timeout: 30000 })
  const hasAuth = ref(false)
  const loading = ref(false)

  async function fetchConfig() {
    const res = await fetch('/api/config')
    const data = await res.json()
    llm.value = data.llm
    browser.value = data.browser
    hasAuth.value = data.has_auth
  }

  async function saveConfig() {
    loading.value = true
    await fetch('/api/config', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ llm: llm.value, browser: browser.value, answer: {} }),
    })
    loading.value = false
  }

  return { llm, browser, hasAuth, loading, fetchConfig, saveConfig }
})
