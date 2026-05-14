<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { Terminal, ChevronDown } from 'lucide-vue-next'

const props = defineProps<{
  logs: string[]
}>()

const containerRef = ref<HTMLElement | null>(null)
const autoScroll = ref(true)
const userScrolled = ref(false)

// Watch for new logs and auto-scroll
watch(
  () => props.logs.length,
  async () => {
    if (autoScroll.value) {
      await nextTick()
      scrollToBottom()
    }
  },
)

function scrollToBottom() {
  if (containerRef.value) {
    containerRef.value.scrollTop = containerRef.value.scrollHeight
  }
}

function onScroll() {
  if (!containerRef.value) return
  const el = containerRef.value
  const threshold = 40 // px from bottom
  autoScroll.value = el.scrollHeight - el.scrollTop - el.clientHeight < threshold
  userScrolled.value = !autoScroll.value
}

function scrollToBottomManual() {
  autoScroll.value = true
  userScrolled.value = false
  scrollToBottom()
}

function isErrorLog(log: string): boolean {
  return log.includes('❌') || log.includes('出错') || log.includes('失败') || log.includes('error')
}

function isSuccessLog(log: string): boolean {
  return log.includes('✓') || log.includes('已填入') || log.includes('成功')
}

function isInfoLog(log: string): boolean {
  return log.includes('解析到') || log.includes('进入第') || log.includes('已连接') || log.includes('会话')
}

function logClass(log: string): string {
  if (isErrorLog(log)) return 'text-red-400'
  if (isSuccessLog(log)) return 'text-emerald-400'
  if (isInfoLog(log)) return 'text-sky-300'
  return 'text-muted-foreground'
}

// Extract timestamp and message for coloring
function splitLog(log: string): { time: string; msg: string } {
  const match = log.match(/^\[([^\]]+)\]\s*(.*)$/)
  if (match) {
    return { time: `[${match[1]}]`, msg: match[2] }
  }
  return { time: '', msg: log }
}
</script>

<template>
  <div class="flex flex-col h-full bg-background/60">
    <!-- Header bar -->
    <div class="flex items-center gap-2 px-4 py-2 border-b border-border/50 bg-card/40 flex-shrink-0">
      <Terminal class="h-3.5 w-3.5 text-muted-foreground" />
      <span class="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
        实时日志
      </span>
      <span
        v-if="logs.length"
        class="ml-auto tabular-nums text-[10px] text-muted-foreground/60 font-mono"
      >
        {{ logs.length }}
      </span>
    </div>

    <!-- Log entries -->
    <div
      ref="containerRef"
      class="flex-1 overflow-y-auto overscroll-contain"
      @scroll="onScroll"
    >
      <div v-if="logs.length === 0" class="flex flex-col items-center justify-center h-full py-6">
        <Terminal class="h-5 w-5 text-muted-foreground/15" />
        <p class="mt-2 text-[11px] text-muted-foreground/30 font-mono">等待日志...</p>
      </div>

      <div v-else class="px-3 py-2">
        <div
          v-for="(log, idx) in logs"
          :key="idx"
          class="flex gap-0 font-mono text-xs leading-relaxed py-[1px]"
          :class="logClass(log)"
        >
          <span class="flex-shrink-0 text-[10px] opacity-60">
            {{ splitLog(log).time }}
          </span>
          <span class="ml-2">{{ splitLog(log).msg }}</span>
        </div>
      </div>
    </div>

    <!-- Scroll-to-bottom button (when user has scrolled up) -->
    <Transition
      enter-active-class="transition-all duration-200 ease-out"
      enter-from-class="opacity-0 translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-150 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 translate-y-2"
    >
      <div
        v-if="userScrolled && logs.length > 0"
        class="absolute bottom-3 left-1/2 -translate-x-1/2"
      >
        <button
          class="flex items-center gap-1 rounded-full bg-card border border-border px-3 py-1.5 text-[11px] text-muted-foreground shadow-lg transition-colors hover:text-foreground hover:border-primary/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30"
          @click="scrollToBottomManual"
        >
          <ChevronDown class="h-3 w-3" />
          回到底部
        </button>
      </div>
    </Transition>
  </div>
</template>
