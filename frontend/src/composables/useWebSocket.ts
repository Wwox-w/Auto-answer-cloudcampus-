import { ref, onUnmounted } from 'vue'
import { useSessionStore } from '@/stores/session'

export function useWebSocket() {
  const ws = ref<WebSocket | null>(null)
  const connected = ref(false)
  const store = useSessionStore()

  function connect() {
    // 直连后端 WebSocket，绕过 Vite 代理避免协议升级问题
    const url = `ws://localhost:8000/ws/progress`
    ws.value = new WebSocket(url)

    ws.value.onopen = () => {
      connected.value = true
      store.addLog('WebSocket 已连接')
    }

    ws.value.onmessage = (event) => {
      const data = JSON.parse(event.data)
      handleEvent(data)
    }

    ws.value.onclose = () => {
      connected.value = false
      store.addLog('WebSocket 已断开，3秒后重连...')
      setTimeout(connect, 3000)
    }

    ws.value.onerror = () => {
      connected.value = false
    }
  }

  function handleEvent(data: any) {
    switch (data.event) {
      case 'ready':
        store.addLog(data.message)
        break
      case 'page_start':
        store.currentPage = data.page
        store.questions = []
        store.codeQuestions = []
        store.addLog(`进入第 ${data.page} 页`)
        break
      case 'questions_loaded':
        store.addLog(`解析到 ${data.count} 道题`)
        break
      case 'solving':
        updateQuestion(data.number, { status: 'solving', text: data.text, type: data.type })
        store.addLog(`#${data.number} ${data.type} → LLM 求解中...`)
        break
      case 'answer_generated':
        updateQuestion(data.number, { status: 'solved', answer: data.preview, type: data.type })
        store.addLog(`#${data.number} ${data.type} → 答案已生成`)
        if (data.usage) {
          store.usage = data.usage
        }
        break
      case 'filling':
        store.addLog(data.message)
        break
      case 'filled':
        updateQuestion(data.number, { status: 'filled' })
        store.addLog(`#${data.number} ✓ 已填入`)
        break
      case 'code_required':
        store.codeQuestions = data.questions
        store.addLog(`有 ${data.count} 道编程题需要手动填入`)
        break
      case 'error':
        store.addLog(`❌ ${data.message || data.number + ' 出错'}`)
        if (data.number) updateQuestion(data.number, { status: 'error' })
        break
      case 'session_end':
        store.running = false
        store.addLog('答题结束')
        break
    }
  }

  function updateQuestion(number: number, updates: Partial<{ status: string; text: string; answer: string; type: string }>) {
    const q = store.questions.find(q => q.number === number)
    if (q) {
      Object.assign(q, updates)
    } else {
      store.questions.push({
        number,
        type: updates.type || 'unknown',
        text: updates.text || '',
        answer: updates.answer,
        status: (updates.status as any) || 'waiting',
      })
    }
  }

  function disconnect() {
    ws.value?.close()
  }

  onUnmounted(disconnect)

  return { connected, connect, disconnect }
}
