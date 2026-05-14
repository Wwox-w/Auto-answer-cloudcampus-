<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  History,
  Calendar,
  FileText,
  Layers,
  Cpu,
  ChevronRight,
  ChevronDown,
  AlertTriangle,
  RefreshCw,
  Inbox,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Code2,
  ListChecks,
  Clock,
} from 'lucide-vue-next'
import NavBar from '@/components/NavBar.vue'

// ── Types ──────────────────────────────────────────────
interface HistoryItem {
  id: string
  date: string
  total_questions: number
  pages: number
  model: string
}

interface QuestionEntry {
  index: number
  type: string
  question: string
  answer: string
  options?: string[]
}

interface HistoryDetail {
  id: string
  date: string
  total_questions: number
  pages: number
  model: string
  questions: QuestionEntry[]
}

// ── State ──────────────────────────────────────────────
const items = ref<HistoryItem[]>([])
const loading = ref(true)
const error = ref('')
const expandedId = ref<string | null>(null)
const detailLoading = ref(false)
const detail = ref<HistoryDetail | null>(null)

// ── Methods ────────────────────────────────────────────
async function fetchList() {
  loading.value = true
  error.value = ''
  try {
    const res = await fetch('/api/history')
    if (!res.ok) throw new Error(`请求失败 (${res.status})`)
    items.value = await res.json()
  } catch (e) {
    error.value = e instanceof Error ? e.message : '加载失败'
  } finally {
    loading.value = false
  }
}

async function toggleDetail(id: string) {
  if (expandedId.value === id) {
    // Collapse
    expandedId.value = null
    detail.value = null
    return
  }

  expandedId.value = id
  detailLoading.value = true
  detail.value = null
  try {
    const res = await fetch(`/api/history/${id}`)
    if (!res.ok) throw new Error(`请求失败 (${res.status})`)
    detail.value = await res.json()
  } catch (e) {
    error.value = e instanceof Error ? e.message : '加载详情失败'
    expandedId.value = null
  } finally {
    detailLoading.value = false
  }
}

function formatDate(dateStr: string): string {
  try {
    const d = new Date(dateStr)
    const mm = String(d.getMonth() + 1).padStart(2, '0')
    const dd = String(d.getDate()).padStart(2, '0')
    const hh = String(d.getHours()).padStart(2, '0')
    const mi = String(d.getMinutes()).padStart(2, '0')
    return `${mm}-${dd} ${hh}:${mi}`
  } catch {
    return dateStr
  }
}

function formatDateFull(dateStr: string): string {
  try {
    const d = new Date(dateStr)
    const y = d.getFullYear()
    const mm = String(d.getMonth() + 1).padStart(2, '0')
    const dd = String(d.getDate()).padStart(2, '0')
    const hh = String(d.getHours()).padStart(2, '0')
    const mi = String(d.getMinutes()).padStart(2, '0')
    return `${y}年${mm}月${dd}日 ${hh}:${mi}`
  } catch {
    return dateStr
  }
}

function typeIcon(type: string) {
  const t = type.trim()
  if (t.includes('单选')) return 'single'
  if (t.includes('多选')) return 'multi'
  if (t.includes('填空')) return 'fill'
  if (t.includes('编程') || t.includes('代码')) return 'code'
  if (t.includes('判断')) return 'judge'
  if (t.includes('简答') || t.includes('问答')) return 'qa'
  return 'default'
}

function typeLabel(type: string): string {
  const map: Record<string, string> = {
    single: '单选',
    multi: '多选',
    fill: '填空',
    code: '编程',
    judge: '判断',
    qa: '简答',
    default: '题目',
  }
  return map[typeIcon(type)] ?? type
}

function typeBadgeClass(type: string): string {
  const map: Record<string, string> = {
    single: 'bg-blue-400/10 text-blue-400 border-blue-400/20',
    multi: 'bg-purple-400/10 text-purple-400 border-purple-400/20',
    fill: 'bg-emerald-400/10 text-emerald-400 border-emerald-400/20',
    code: 'bg-amber-400/10 text-amber-400 border-amber-400/20',
    judge: 'bg-rose-400/10 text-rose-400 border-rose-400/20',
    qa: 'bg-cyan-400/10 text-cyan-400 border-cyan-400/20',
    default: 'bg-slate-400/10 text-slate-400 border-slate-400/20',
  }
  return map[typeIcon(type)] ?? map.default
}

onMounted(fetchList)
</script>

<template>
  <div class="min-h-screen bg-background">
    <NavBar />

    <main class="mx-auto max-w-4xl px-6 py-8">
      <!-- ── Page Header ──────────────────────────── -->
      <div class="mb-8">
        <div class="flex items-center gap-3">
          <div
            class="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 ring-1 ring-primary/20"
          >
            <History class="h-4.5 w-4.5 text-primary" />
          </div>
          <div>
            <h1 class="text-2xl font-bold tracking-tight text-foreground">
              答题记录
            </h1>
            <p class="mt-0.5 text-sm text-muted-foreground">
              历史答题记录与详细回顾
            </p>
          </div>
        </div>
      </div>

      <!-- ── Loading State ────────────────────────── -->
      <div v-if="loading" class="space-y-3">
        <div
          v-for="i in 4"
          :key="i"
          class="animate-pulse rounded-xl border border-border bg-card p-5"
        >
          <div class="flex items-center gap-4">
            <!-- Date skeleton -->
            <div class="flex items-center gap-2">
              <div class="h-4 w-4 rounded bg-muted" />
              <div class="h-4 w-28 rounded bg-muted" />
            </div>
            <!-- Stats skeleton -->
            <div class="ml-auto flex items-center gap-5">
              <div class="h-3 w-16 rounded bg-muted" />
              <div class="h-3 w-14 rounded bg-muted" />
              <div class="h-3 w-20 rounded bg-muted" />
              <div class="h-4 w-4 rounded bg-muted" />
            </div>
          </div>
        </div>
      </div>

      <!-- ── Error State ──────────────────────────── -->
      <div
        v-else-if="error && items.length === 0"
        class="flex flex-col items-center justify-center py-20 text-center"
      >
        <div
          class="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-destructive/10 ring-1 ring-destructive/20"
        >
          <AlertTriangle class="h-8 w-8 text-destructive/70" />
        </div>
        <h2 class="text-lg font-semibold text-foreground">加载失败</h2>
        <p class="mt-1 max-w-sm text-sm text-muted-foreground">
          {{ error }}
        </p>
        <button
          class="mt-6 inline-flex items-center gap-2 rounded-lg bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground shadow-lg shadow-primary/25 transition-all duration-200 hover:bg-primary/90 hover:shadow-xl hover:shadow-primary/30 active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 focus-visible:ring-offset-2 focus-visible:ring-offset-background"
          @click="fetchList"
        >
          <RefreshCw class="h-4 w-4" />
          重新加载
        </button>
      </div>

      <!-- ── Empty State ──────────────────────────── -->
      <div
        v-else-if="items.length === 0"
        class="flex flex-col items-center justify-center py-20 text-center"
      >
        <div
          class="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-muted ring-1 ring-border"
        >
          <Inbox class="h-8 w-8 text-muted-foreground/50" />
        </div>
        <h2 class="text-lg font-semibold text-foreground">暂无答题记录</h2>
        <p class="mt-1 max-w-sm text-sm text-muted-foreground">
          开始答题后，你的答题记录和详细回顾将会显示在这里
        </p>
      </div>

      <!-- ── History List ──────────────────────────── -->
      <div v-else class="space-y-3">
        <div
          v-for="item in items"
          :key="item.id"
          class="overflow-hidden rounded-xl border transition-colors duration-200"
          :class="
            expandedId === item.id
              ? 'border-primary/30 bg-card'
              : 'border-border bg-card hover:border-primary/15'
          "
        >
          <!-- ── Card Header ──────────────────────── -->
          <button
            class="flex w-full items-center gap-4 px-5 py-4 text-left transition-colors duration-150 hover:bg-accent/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-primary/40"
            @click="toggleDetail(item.id)"
          >
            <!-- Date -->
            <div class="flex items-center gap-2.5 min-w-0">
              <Calendar class="h-4 w-4 flex-shrink-0 text-muted-foreground" />
              <span class="text-sm font-medium text-foreground tabular-nums whitespace-nowrap">
                {{ formatDate(item.date) }}
              </span>
            </div>

            <!-- Stats badges -->
            <div class="ml-auto flex items-center gap-3">
              <span class="inline-flex items-center gap-1.5 text-xs text-muted-foreground">
                <ListChecks class="h-3.5 w-3.5" />
                <span class="tabular-nums font-medium text-foreground">
                  {{ item.total_questions }}
                </span>
                题
              </span>
              <span class="h-4 w-px bg-border" />
              <span class="inline-flex items-center gap-1.5 text-xs text-muted-foreground">
                <FileText class="h-3.5 w-3.5" />
                <span class="tabular-nums font-medium text-foreground">
                  {{ item.pages }}
                </span>
                页
              </span>
              <span class="h-4 w-px bg-border hidden sm:block" />
              <span class="hidden sm:inline-flex items-center gap-1.5 text-xs text-muted-foreground">
                <Cpu class="h-3.5 w-3.5" />
                <span class="font-medium text-foreground truncate max-w-[120px]">
                  {{ item.model || '未知' }}
                </span>
              </span>
              <div
                class="flex h-6 w-6 items-center justify-center rounded-md transition-colors duration-200"
                :class="expandedId === item.id ? 'bg-primary/10 text-primary' : 'text-muted-foreground'"
              >
                <ChevronRight
                  class="h-4 w-4 transition-transform duration-300"
                  :class="{ 'rotate-90': expandedId === item.id }"
                />
              </div>
            </div>
          </button>

          <!-- ── Expanded Detail Panel ────────────── -->
          <Transition
            name="expand"
            @enter="(el: Element) => {
              const h = (el as HTMLElement).scrollHeight
              ;(el as HTMLElement).style.height = '0px'
              requestAnimationFrame(() => { (el as HTMLElement).style.height = h + 'px' })
            }"
            @after-enter="(el: Element) => { (el as HTMLElement).style.height = '' }"
            @leave="(el: Element) => {
              (el as HTMLElement).style.height = (el as HTMLElement).scrollHeight + 'px'
              requestAnimationFrame(() => { (el as HTMLElement).style.height = '0px' })
            }"
          >
            <div
              v-if="expandedId === item.id"
              class="overflow-hidden"
            >
              <!-- Loading detail skeleton -->
              <div v-if="detailLoading" class="border-t border-border px-5 py-6 space-y-4">
                <div class="animate-pulse flex items-center gap-3">
                  <div class="h-4 w-4 rounded bg-muted" />
                  <div class="h-4 w-40 rounded bg-muted" />
                </div>
                <div
                  v-for="j in 3"
                  :key="j"
                  class="animate-pulse rounded-lg border border-border bg-accent/30 p-4 space-y-3"
                >
                  <div class="flex items-center gap-3">
                    <div class="h-5 w-12 rounded bg-muted" />
                    <div class="h-4 w-16 rounded bg-muted" />
                  </div>
                  <div class="h-3 w-full rounded bg-muted" />
                  <div class="h-3 w-3/4 rounded bg-muted" />
                </div>
              </div>

              <!-- Detail content -->
              <div v-else-if="detail" class="border-t border-border">
                <!-- Session meta -->
                <div class="flex flex-wrap items-center gap-3 border-b border-border/50 px-5 py-3">
                  <span class="inline-flex items-center gap-1.5 text-xs text-muted-foreground">
                    <Clock class="h-3.5 w-3.5" />
                    {{ formatDateFull(detail.date) }}
                  </span>
                  <span class="h-3 w-px bg-border" />
                  <span class="inline-flex items-center gap-1.5 text-xs text-muted-foreground">
                    <Layers class="h-3.5 w-3.5" />
                    {{ detail.total_questions }} 题 / {{ detail.pages }} 页
                  </span>
                  <span class="h-3 w-px bg-border" />
                  <span class="inline-flex items-center gap-1.5 text-xs text-muted-foreground">
                    <Cpu class="h-3.5 w-3.5" />
                    {{ detail.model || '未知模型' }}
                  </span>
                </div>

                <!-- Questions list -->
                <div class="divide-y divide-border/50">
                  <div
                    v-for="(q, qi) in detail.questions"
                    :key="qi"
                    class="px-5 py-4 transition-colors duration-100 hover:bg-accent/30"
                  >
                    <!-- Question header -->
                    <div class="mb-3 flex items-start gap-3">
                      <!-- Question number -->
                      <span
                        class="mt-0.5 inline-flex h-6 min-w-[1.5rem] items-center justify-center rounded-md bg-primary/10 text-xs font-bold tabular-nums text-primary"
                      >
                        {{ qi + 1 }}
                      </span>
                      <!-- Question type badge -->
                      <span
                        class="inline-flex items-center gap-1 rounded-md border px-2 py-0.5 text-[11px] font-medium"
                        :class="typeBadgeClass(q.type)"
                      >
                        <CheckCircle2 v-if="typeIcon(q.type) === 'single'" class="h-3 w-3" />
                        <ListChecks v-else-if="typeIcon(q.type) === 'multi'" class="h-3 w-3" />
                        <HelpCircle v-else-if="typeIcon(q.type) === 'judge'" class="h-3 w-3" />
                        <Code2 v-else-if="typeIcon(q.type) === 'code'" class="h-3 w-3" />
                        <XCircle v-else class="h-3 w-3" />
                        {{ typeLabel(q.type) }}
                      </span>
                    </div>

                    <!-- Question text -->
                    <p class="mb-3 text-sm leading-relaxed text-foreground/90 whitespace-pre-wrap break-words">
                      {{ q.question }}
                    </p>

                    <!-- Options if available -->
                    <div
                      v-if="q.options && q.options.length > 0"
                      class="mb-3 grid gap-1.5 sm:grid-cols-2"
                    >
                      <div
                        v-for="(opt, oi) in q.options"
                        :key="oi"
                        class="rounded-md border border-border/60 bg-accent/20 px-3 py-1.5 text-xs text-muted-foreground"
                      >
                        <span class="font-mono font-medium text-foreground/70">
                          {{ String.fromCharCode(65 + oi) }}.
                        </span>
                        {{ opt }}
                      </div>
                    </div>

                    <!-- Answer -->
                    <div
                      class="rounded-lg border border-emerald-400/15 bg-emerald-400/[0.04] px-4 py-3"
                    >
                      <div class="mb-2 flex items-center gap-1.5">
                        <CheckCircle2 class="h-3.5 w-3.5 text-emerald-400" />
                        <span class="text-[11px] font-semibold uppercase tracking-wide text-emerald-400">
                          答案
                        </span>
                      </div>
                      <p class="text-sm leading-relaxed text-foreground/80 whitespace-pre-wrap break-words">
                        {{ q.answer || '（无答案）' }}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* Expand/Collapse transition */
.expand-enter-active,
.expand-leave-active {
  transition: height 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}
.expand-enter-from,
.expand-leave-to {
  height: 0;
}
</style>
