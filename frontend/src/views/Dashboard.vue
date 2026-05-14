<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Play, History, ArrowRight, Sparkles, AlertTriangle } from 'lucide-vue-next'
import NavBar from '@/components/NavBar.vue'
import StatusCard from '@/components/StatusCard.vue'
import { useConfigStore } from '@/stores/config'
import { useSessionStore } from '@/stores/session'

const router = useRouter()
const configStore = useConfigStore()
const sessionStore = useSessionStore()

// History state
interface HistoryItem {
  id: number
  date: string
  score?: number
  total?: number
  status: string
}
const historyItems = ref<HistoryItem[]>([])
const historyLoading = ref(false)
const historyError = ref('')
const pageLoading = ref(true)

// Computed statuses
const modelOk = computed(() => !!configStore.llm.llm_model)
const modelStatus = computed(() => (modelOk.value ? '已配置' : '未配置'))

const loginOk = computed(() => configStore.hasAuth)
const loginStatus = computed(() => (loginOk.value ? '已登录' : '未登录'))

const answerOk = computed(() => modelOk.value && loginOk.value)
const answerStatus = computed(() => {
  if (sessionStore.running) return '答题中...'
  if (answerOk.value) return '就绪'
  if (!modelOk.value && !loginOk.value) return '请先配置模型并登录'
  if (!modelOk.value) return '请先配置模型'
  return '请先登录'
})

// Fetch initial data
async function loadData() {
  pageLoading.value = true
  try {
    await configStore.fetchConfig()
  } catch {
    // Config fetch failure is non-blocking; status cards will show "未配置"
  }
  pageLoading.value = false

  // Fetch history in background
  historyLoading.value = true
  try {
    const res = await fetch('/api/history?limit=3')
    if (!res.ok) throw new Error('请求失败')
    historyItems.value = await res.json()
  } catch (e) {
    historyError.value = e instanceof Error ? e.message : '加载失败'
  } finally {
    historyLoading.value = false
  }
}

function goToSession() {
  router.push('/session')
}

function goToHistory() {
  router.push('/history')
}

function formatDate(dateStr: string): string {
  try {
    const d = new Date(dateStr)
    return `${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  } catch {
    return dateStr
  }
}

onMounted(loadData)
</script>

<template>
  <div class="min-h-screen bg-background">
    <NavBar />

    <main class="mx-auto max-w-6xl px-6 py-8">
      <!-- Page header -->
      <div class="mb-8">
        <h1 class="text-2xl font-bold tracking-tight text-foreground">
          仪表盘
        </h1>
        <p class="mt-1 text-sm text-muted-foreground">
          系统状态概览与快捷操作
        </p>
      </div>

      <!-- Status Cards Grid -->
      <div class="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <!-- Skeleton loading for status cards -->
        <template v-if="pageLoading">
          <div
            v-for="i in 3"
            :key="i"
            class="animate-pulse rounded-xl border border-border bg-card p-5"
          >
            <div class="flex items-start gap-4">
              <div class="mt-0.5 h-5 w-5 rounded-full bg-muted" />
              <div class="flex-1 space-y-2">
                <div class="h-3 w-16 rounded bg-muted" />
                <div class="h-4 w-24 rounded bg-muted" />
              </div>
              <div class="mt-1.5 h-2.5 w-2.5 rounded-full bg-muted" />
            </div>
          </div>
        </template>

        <template v-else>
          <StatusCard
            title="模型状态"
            :status="modelStatus"
            :ok="modelOk"
          />
          <StatusCard
            title="登录状态"
            :status="loginStatus"
            :ok="loginOk"
          />
          <StatusCard
            title="答题状态"
            :status="answerStatus"
            :ok="answerOk"
          />
        </template>
      </div>

      <!-- Bottom Section: CTA + History -->
      <div class="grid gap-6 lg:grid-cols-3">
        <!-- CTA Card (takes 2/3 on desktop) -->
        <div
          class="group relative overflow-hidden rounded-xl border border-border bg-card p-6 lg:col-span-2"
        >
          <!-- Background glow effect -->
          <div
            class="pointer-events-none absolute -right-20 -top-20 h-64 w-64 rounded-full bg-primary/5 blur-3xl transition-opacity duration-500 group-hover:opacity-100"
            :class="answerOk ? 'opacity-60' : 'opacity-30'"
          />

          <div class="relative z-10 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 class="flex items-center gap-2 text-lg font-semibold text-foreground">
                <Sparkles class="h-5 w-5 text-primary" />
                开始答题
              </h2>
              <p class="mt-1 max-w-md text-sm text-muted-foreground">
                开始新一轮智能答题，系统将自动读取题目并通过 LLM 生成答案
              </p>

              <!-- Prerequisites warning -->
              <div
                v-if="!answerOk"
                class="mt-3 flex items-start gap-2 rounded-lg bg-amber-400/10 border border-amber-400/20 px-3 py-2 text-sm text-amber-300"
              >
                <AlertTriangle class="mt-0.5 h-4 w-4 flex-shrink-0" />
                <span>{{ answerStatus }}</span>
              </div>
            </div>

            <button
              :disabled="!answerOk"
              class="inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground shadow-lg shadow-primary/25 transition-all duration-200 hover:bg-primary/90 hover:shadow-xl hover:shadow-primary/30 active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:cursor-not-allowed disabled:opacity-40 disabled:shadow-none"
              @click="goToSession"
            >
              <Play class="h-4 w-4 fill-current" />
              开始答题
            </button>
          </div>
        </div>

        <!-- Recent History (takes 1/3 on desktop) -->
        <div class="rounded-xl border border-border bg-card p-5">
          <div class="mb-4 flex items-center justify-between">
            <h3 class="flex items-center gap-2 text-sm font-semibold text-foreground">
              <History class="h-4 w-4 text-muted-foreground" />
              最近记录
            </h3>
            <button
              class="text-xs text-muted-foreground hover:text-primary transition-colors flex items-center gap-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 rounded"
              @click="goToHistory"
            >
              查看全部
              <ArrowRight class="h-3 w-3" />
            </button>
          </div>

          <!-- Loading skeleton -->
          <div v-if="historyLoading" class="space-y-3">
            <div
              v-for="i in 3"
              :key="i"
              class="animate-pulse flex items-center gap-3 rounded-lg px-3 py-2"
            >
              <div class="h-2 w-2 rounded-full bg-muted" />
              <div class="h-3 flex-1 rounded bg-muted" />
              <div class="h-3 w-12 rounded bg-muted" />
            </div>
          </div>

          <!-- Error state -->
          <div
            v-else-if="historyError"
            class="flex flex-col items-center gap-2 py-6 text-center"
          >
            <AlertTriangle class="h-5 w-5 text-muted-foreground" />
            <p class="text-xs text-muted-foreground">{{ historyError }}</p>
          </div>

          <!-- Empty state -->
          <div
            v-else-if="historyItems.length === 0"
            class="flex flex-col items-center gap-2 py-6 text-center"
          >
            <History class="h-8 w-8 text-muted-foreground/40" />
            <p class="text-xs text-muted-foreground">暂无答题记录</p>
            <p class="text-xs text-muted-foreground/60">开始答题后将在此显示</p>
          </div>

          <!-- History list -->
          <ul v-else class="space-y-1">
            <li
              v-for="item in historyItems"
              :key="item.id"
              class="group/item flex items-center gap-3 rounded-lg px-3 py-2 transition-colors hover:bg-accent cursor-pointer"
              @click="goToHistory"
            >
              <!-- Status dot -->
              <div
                class="h-2 w-2 flex-shrink-0 rounded-full"
                :class="item.status === 'completed' ? 'bg-emerald-400' : item.status === 'error' ? 'bg-red-400' : 'bg-amber-400'"
              />
              <!-- Date -->
              <span class="flex-1 text-sm text-foreground tabular-nums">
                {{ formatDate(item.date) }}
              </span>
              <!-- Score if available -->
              <span
                v-if="item.score !== undefined && item.total !== undefined"
                class="text-xs tabular-nums"
                :class="item.status === 'completed' ? 'text-emerald-400' : 'text-muted-foreground'"
              >
                {{ item.score }}/{{ item.total }}
              </span>
              <!-- Status badge -->
              <span
                class="text-xs px-1.5 py-0.5 rounded font-medium"
                :class="{
                  'bg-emerald-400/10 text-emerald-400': item.status === 'completed',
                  'bg-red-400/10 text-red-400': item.status === 'error',
                  'bg-amber-400/10 text-amber-400': item.status === 'running',
                }"
              >
                {{ item.status === 'completed' ? '完成' : item.status === 'error' ? '失败' : '进行中' }}
              </span>
            </li>
          </ul>
        </div>
      </div>
    </main>
  </div>
</template>
