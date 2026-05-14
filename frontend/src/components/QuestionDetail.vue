<script setup lang="ts">
import { computed } from 'vue'
import {
  Code,
  FileCode,
  Brain,
  Lightbulb,
  Circle,
  Loader2,
  Check,
  X,
} from 'lucide-vue-next'
import type { Question } from '@/stores/session'

const props = defineProps<{
  question: Question | undefined
  codeQuestions: Question[]
}>()

interface TypeConfig {
  label: string
  icon: any
  color: string
  bg: string
}

const typeConfigMap: Record<string, TypeConfig> = {
  'single_choice': { label: '单选题', icon: Circle, color: 'text-sky-400', bg: 'bg-sky-400/10' },
  'multiple_choice': { label: '多选题', icon: Check, color: 'text-violet-400', bg: 'bg-violet-400/10' },
  'fill_blank': { label: '填空题', icon: Circle, color: 'text-amber-400', bg: 'bg-amber-400/10' },
  'code_required': { label: '编程题', icon: Code, color: 'text-emerald-400', bg: 'bg-emerald-400/10' },
  'matching': { label: '匹配题', icon: Circle, color: 'text-rose-400', bg: 'bg-rose-400/10' },
  'essay': { label: '简答题', icon: Circle, color: 'text-cyan-400', bg: 'bg-cyan-400/10' },
  'true_false': { label: '判断题', icon: Circle, color: 'text-orange-400', bg: 'bg-orange-400/10' },
  'unknown': { label: '未知', icon: Circle, color: 'text-muted-foreground', bg: 'bg-muted/50' },
}

const typeConfig = computed<TypeConfig>(() => {
  if (!props.question) return typeConfigMap['unknown']
  return typeConfigMap[props.question.type] || typeConfigMap['unknown']
})

const statusConfig = computed(() => {
  if (!props.question) return null
  switch (props.question.status) {
    case 'solving':
      return { icon: Loader2, label: '解答中', color: 'text-primary', bg: 'bg-primary/10', animate: 'animate-spin' }
    case 'solved':
      return { icon: Check, label: '已生成', color: 'text-emerald-400', bg: 'bg-emerald-400/10', animate: '' }
    case 'filled':
      return { icon: Check, label: '已填入', color: 'text-emerald-400', bg: 'bg-emerald-400/10', animate: '' }
    case 'error':
      return { icon: X, label: '出错', color: 'text-red-400', bg: 'bg-red-400/10', animate: '' }
    default:
      return { icon: Circle, label: '等待中', color: 'text-muted-foreground', bg: 'bg-muted/50', animate: '' }
  }
})

const isCodeQuestion = computed(() => props.question?.type === 'code_required')

const codeAnswerLines = computed<string[]>(() => {
  if (!props.question?.answer) return []
  return props.question.answer.split('\n').filter(Boolean)
})
</script>

<template>
  <div class="h-full">
    <!-- Empty state -->
    <div
      v-if="!question"
      class="flex flex-col items-center justify-center h-full text-center px-6 py-12"
    >
      <Brain class="h-12 w-12 text-muted-foreground/20" />
      <p class="mt-4 text-sm text-muted-foreground">选择左侧题目查看详情</p>
      <p class="mt-1 text-xs text-muted-foreground/50">或等待自动答题开始</p>
    </div>

    <!-- Question detail -->
    <div v-else class="p-5 lg:p-6 space-y-5">
      <!-- Header: type badge + status -->
      <div class="flex items-center gap-3 flex-wrap">
        <!-- Type badge -->
        <span
          class="inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs font-medium ring-1 ring-inset"
          :class="[typeConfig.color, typeConfig.bg, typeConfig.color.replace('text', 'ring') + '/20']"
        >
          <component :is="typeConfig.icon" class="h-3.5 w-3.5" />
          {{ typeConfig.label }}
        </span>

        <!-- Status badge -->
        <span
          v-if="statusConfig"
          class="inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs font-medium"
          :class="[statusConfig.color, statusConfig.bg]"
        >
          <component
            :is="statusConfig.icon"
            class="h-3.5 w-3.5"
            :class="statusConfig.animate"
          />
          {{ statusConfig.label }}
        </span>

        <!-- Question number -->
        <span class="ml-auto tabular-nums text-xs text-muted-foreground font-mono">
          #{{ question.number }}
        </span>
      </div>

      <!-- Question text -->
      <div class="rounded-xl border border-border bg-card/50 px-4 py-3.5">
        <div class="flex items-start gap-3">
          <Lightbulb class="mt-0.5 h-4 w-4 flex-shrink-0 text-amber-400/60" />
          <p class="text-sm leading-relaxed text-foreground">
            {{ question.text || '(题目文本待加载...)' }}
          </p>
        </div>
      </div>

      <!-- LLM Answer section -->
      <div
        v-if="question.answer || question.status === 'solving'"
        class="space-y-3"
      >
        <!-- Section header -->
        <div class="flex items-center gap-2">
          <Brain class="h-4 w-4 text-primary/60" />
          <span class="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            LLM 答案
          </span>
        </div>

        <!-- Answer card -->
        <div
          :class="[
            'rounded-xl border border-emerald-400/20 bg-emerald-400/5',
            isCodeQuestion ? 'overflow-hidden' : '',
          ]"
        >
          <!-- Code answer: dark terminal-style with syntax block -->
          <div v-if="isCodeQuestion && codeAnswerLines.length > 0" class="relative">
            <!-- Terminal title bar -->
            <div class="flex items-center gap-2 px-4 py-2 bg-emerald-400/10 border-b border-emerald-400/15">
              <FileCode class="h-3.5 w-3.5 text-emerald-400/70" />
              <span class="text-[11px] font-medium text-emerald-400/80">代码答案</span>
              <span class="ml-auto tabular-nums text-[10px] text-emerald-400/40 font-mono">
                {{ codeAnswerLines.length }} lines
              </span>
            </div>
            <!-- Code content -->
            <pre class="overflow-x-auto p-4 text-xs leading-relaxed font-mono text-emerald-100/90"><code>{{ question.answer }}</code></pre>
          </div>

          <!-- Non-code answer -->
          <div
            v-else-if="question.answer"
            class="px-4 py-3.5"
          >
            <p class="text-sm leading-relaxed text-emerald-100/80">
              {{ question.answer }}
            </p>
          </div>

          <!-- Solving loader -->
          <div
            v-else-if="question.status === 'solving'"
            class="flex items-center gap-3 px-4 py-5"
          >
            <Loader2 class="h-4 w-4 animate-spin text-primary" />
            <span class="text-sm text-muted-foreground">LLM 正在生成答案...</span>
          </div>
        </div>
      </div>

      <!-- Code Questions Section (manual input required) -->
      <div
        v-if="codeQuestions.length > 0"
        class="space-y-3"
      >
        <div class="flex items-center gap-2">
          <Code class="h-4 w-4 text-amber-400/60" />
          <span class="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            需手动填入的编程题
          </span>
          <span class="tabular-nums text-[10px] text-amber-400/60">
            {{ codeQuestions.length }}
          </span>
        </div>

        <ul class="space-y-2">
          <li
            v-for="cq in codeQuestions"
            :key="cq.number"
            class="rounded-lg border border-amber-400/15 bg-amber-400/5 px-3.5 py-2.5"
          >
            <div class="flex items-center gap-2 mb-1.5">
              <span class="tabular-nums text-[11px] font-mono font-medium text-amber-400/80">
                #{{ cq.number }}
              </span>
              <span class="text-[11px] text-amber-300/70">{{ cq.text }}</span>
            </div>
            <div
              v-if="cq.answer"
              class="rounded bg-background/50 px-3 py-2 text-xs font-mono leading-relaxed text-amber-100/70 overflow-x-auto"
            >
              <code>{{ cq.answer }}</code>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>
