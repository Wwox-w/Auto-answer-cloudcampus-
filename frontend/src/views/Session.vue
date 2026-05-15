<script setup lang="ts">
import { ref } from 'vue'
import {
  Play,
  Square,
  Wifi,
  WifiOff,
  Loader2,
  AlertTriangle,
  Sparkles,
  X,
} from 'lucide-vue-next'
import NavBar from '@/components/NavBar.vue'
import QuestionList from '@/components/QuestionList.vue'
import QuestionDetail from '@/components/QuestionDetail.vue'
import LogStream from '@/components/LogStream.vue'
import { useSessionStore } from '@/stores/session'
import { useWebSocket } from '@/composables/useWebSocket'

const store = useSessionStore()
const { connected, connect, disconnect } = useWebSocket()

const starting = ref(false)
const stopping = ref(false)
const showStopConfirm = ref(false)
const error = ref('')

const connectionStatusText = () => {
  if (!store.running) return '未连接'
  if (connected.value) return '已连接'
  return '连接中...'
}

const connectionDotClass = () => {
  if (!store.running) return 'bg-muted-foreground/40'
  if (connected.value) return 'bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.5)]'
  return 'bg-amber-400 shadow-[0_0_6px_rgba(251,191,36,0.5)] animate-pulse'
}

async function handleStart() {
  error.value = ''
  starting.value = true
  store.reset()
  try {
    const res = await fetch('/api/session/start', { method: 'POST' })
    if (!res.ok) {
      const body = await res.json().catch(() => ({}))
      throw new Error(body.detail || '启动失败')
    }
    store.running = true
    store.addLog('会话已启动')
    connect()
  } catch (e) {
    error.value = e instanceof Error ? e.message : '启动失败，请检查配置'
  } finally {
    starting.value = false
  }
}

async function handleStop() {
  showStopConfirm.value = false
  stopping.value = true
  try {
    await fetch('/api/session/stop', { method: 'POST' })
  } catch {
    // Best-effort stop
  }
  disconnect()
  store.running = false
  store.addLog('会话已停止')
  stopping.value = false
}

function cancelStop() {
  showStopConfirm.value = false
}
</script>

<template>
  <div class="min-h-screen bg-background flex flex-col">
    <NavBar />

    <!-- ===== Top Control Bar ===== -->
    <div
      class="sticky top-14 z-40 border-b border-border bg-card/80 backdrop-blur-sm"
    >
      <div class="mx-auto max-w-7xl px-6 h-12 flex items-center justify-between">
        <!-- Left: Status + Page -->
        <div class="flex items-center gap-4">
          <!-- Connection indicator -->
          <div class="flex items-center gap-2">
            <div class="relative flex items-center justify-center">
              <div
                v-if="store.running && !connected"
                class="absolute inset-0 rounded-full animate-ping opacity-30"
                :class="connected ? 'bg-emerald-400' : 'bg-amber-400'"
              />
              <div
                class="relative h-2.5 w-2.5 rounded-full transition-shadow duration-500"
                :class="connectionDotClass()"
              />
            </div>
            <div class="flex items-center gap-1.5">
              <Wifi v-if="connected" class="h-3.5 w-3.5 text-emerald-400" />
              <WifiOff v-else-if="store.running" class="h-3.5 w-3.5 text-amber-400" />
              <WifiOff v-else class="h-3.5 w-3.5 text-muted-foreground/40" />
              <span
                class="text-xs font-medium"
                :class="{
                  'text-emerald-400': connected,
                  'text-amber-400': store.running && !connected,
                  'text-muted-foreground': !store.running,
                }"
              >
                {{ connectionStatusText() }}
              </span>
            </div>
          </div>

          <!-- Separator -->
          <div
            v-if="store.running"
            class="h-4 w-px bg-border"
          />

          <!-- Current page -->
          <div
            v-if="store.running && store.currentPage > 0"
            class="flex items-center gap-1.5 text-xs"
          >
            <span class="text-muted-foreground">第</span>
            <span class="tabular-nums font-mono font-semibold text-foreground">
              {{ store.currentPage }}
            </span>
            <span class="text-muted-foreground">页</span>
          </div>

          <!-- Question count -->
          <div
            v-if="store.running && store.questions.length > 0"
            class="flex items-center gap-1 text-xs text-muted-foreground"
          >
            <span class="text-border">/</span>
            <span class="tabular-nums">{{ store.questions.length }}</span>
            <span>题</span>
          </div>

          <!-- Token usage -->
          <div
            v-if="store.usage.total_tokens > 0"
            class="flex items-center gap-1.5 text-xs text-muted-foreground ml-2 pl-2 border-l border-border"
          >
            <span class="tabular-nums font-mono text-foreground">
              {{ (store.usage.total_tokens / 1000).toFixed(1) }}K
            </span>
            <span>tokens</span>
            <span class="text-emerald-400 font-mono tabular-nums">
              ~¥{{ (store.usage.total_tokens / 1000000 * 2).toFixed(4) }}
            </span>
          </div>
        </div>

        <!-- Right: Actions -->
        <div class="flex items-center gap-3">
          <!-- Start button (not running) -->
          <button
            v-if="!store.running"
            :disabled="starting"
            class="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-1.5 text-sm font-semibold text-primary-foreground shadow-lg shadow-primary/25 transition-all duration-200 hover:bg-primary/90 hover:shadow-xl hover:shadow-primary/30 active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:cursor-not-allowed disabled:opacity-50 disabled:shadow-none"
            @click="handleStart"
          >
            <Loader2 v-if="starting" class="h-4 w-4 animate-spin" />
            <Play v-else class="h-4 w-4 fill-current" />
            {{ starting ? '启动中...' : '开始答题' }}
          </button>

          <!-- Stop button (running) -->
          <template v-else>
            <!-- Confirmation dialog -->
            <div
              v-if="showStopConfirm"
              class="flex items-center gap-2 rounded-lg bg-card border border-border px-3 py-1.5 shadow-lg"
            >
              <AlertTriangle class="h-4 w-4 text-amber-400 flex-shrink-0" />
              <span class="text-xs text-foreground">确定停止答题？</span>
              <button
                :disabled="stopping"
                class="rounded-md bg-destructive px-2.5 py-1 text-xs font-medium text-destructive-foreground transition-colors hover:bg-destructive/80 disabled:opacity-50"
                @click="handleStop"
              >
                {{ stopping ? '停止中...' : '确认' }}
              </button>
              <button
                :disabled="stopping"
                class="rounded-md px-2 py-1 text-xs text-muted-foreground transition-colors hover:text-foreground"
                @click="cancelStop"
              >
                取消
              </button>
            </div>

            <!-- Stop trigger button -->
            <button
              v-if="!showStopConfirm || stopping"
              :disabled="stopping"
              class="inline-flex items-center gap-2 rounded-lg border border-red-400/30 bg-red-400/10 px-4 py-1.5 text-sm font-medium text-red-400 transition-all duration-200 hover:bg-red-400/20 hover:border-red-400/50 active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-400/30 focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:cursor-not-allowed disabled:opacity-50"
              @click="showStopConfirm = true"
            >
              <Loader2 v-if="stopping" class="h-4 w-4 animate-spin" />
              <Square v-else class="h-4 w-4 fill-current" />
              {{ stopping ? '停止中...' : '停止' }}
            </button>
          </template>
        </div>
      </div>
    </div>

    <!-- ===== Main Content ===== -->
    <main class="flex-1 flex flex-col">
      <!-- Error banner -->
      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 -translate-y-2"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-all duration-200 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-2"
      >
        <div
          v-if="error"
          class="mx-6 mt-4 flex items-start gap-3 rounded-xl border border-red-400/20 bg-red-400/10 px-4 py-3"
        >
          <AlertTriangle class="mt-0.5 h-4 w-4 flex-shrink-0 text-red-400" />
          <div class="flex-1">
            <p class="text-sm text-red-300">{{ error }}</p>
          </div>
          <button
            class="text-red-400/70 hover:text-red-400 transition-colors"
            @click="error = ''"
          >
            <X class="h-4 w-4" />
          </button>
        </div>
      </Transition>

      <!-- Empty state (not running, no questions) -->
      <div
        v-if="!store.running && store.questions.length === 0"
        class="flex-1 flex items-center justify-center"
      >
        <div class="flex flex-col items-center gap-4 text-center px-6">
          <div
            class="flex h-20 w-20 items-center justify-center rounded-2xl bg-card border border-border"
          >
            <Sparkles class="h-10 w-10 text-primary/40" />
          </div>
          <div>
            <h2 class="text-lg font-semibold text-foreground">准备就绪</h2>
            <p class="mt-1 max-w-sm text-sm text-muted-foreground">
              点击上方"开始答题"按钮，系统将自动读取题目并通过 LLM 生成答案
            </p>
          </div>
          <button
            :disabled="starting"
            class="mt-2 inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-2.5 text-sm font-semibold text-primary-foreground shadow-lg shadow-primary/25 transition-all duration-200 hover:bg-primary/90 hover:shadow-xl hover:shadow-primary/30 active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:cursor-not-allowed disabled:opacity-50 disabled:shadow-none"
            @click="handleStart"
          >
            <Loader2 v-if="starting" class="h-4 w-4 animate-spin" />
            <Play v-else class="h-4 w-4 fill-current" />
            {{ starting ? '启动中...' : '开始答题' }}
          </button>
        </div>
      </div>

      <!-- Split layout (running or has questions) -->
      <div
        v-else
        class="flex-1 flex flex-col lg:flex-row overflow-hidden"
      >
        <!-- Left: Question List -->
        <aside
          class="w-full lg:w-72 xl:w-80 flex-shrink-0 border-b lg:border-b-0 lg:border-r border-border bg-card/30 overflow-y-auto"
        >
          <QuestionList :questions="store.questions" />
        </aside>

        <!-- Right: Detail + Log -->
        <div class="flex-1 flex flex-col overflow-hidden min-w-0">
          <div class="flex-1 overflow-y-auto">
            <QuestionDetail
              :question="store.currentQuestion"
              :code-questions="store.codeQuestions"
            />
          </div>
          <div
            class="flex-shrink-0 border-t border-border h-52 lg:h-64"
          >
            <LogStream :logs="store.logs" />
          </div>
        </div>
      </div>
    </main>
  </div>
</template>
