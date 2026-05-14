<script setup lang="ts">
import { computed } from 'vue'
import {
  Circle,
  Check,
  X,
  Loader2,
  Code,
  ListChecks,
} from 'lucide-vue-next'
import type { Question } from '@/stores/session'

const props = defineProps<{
  questions: Question[]
}>()

const emit = defineEmits<{
  (e: 'select', question: Question): void
}>()

interface QuestionTypeConfig {
  label: string
  short: string
  color: string
}

const typeConfigMap: Record<string, QuestionTypeConfig> = {
  'single_choice': { label: '单选', short: '单选', color: 'text-sky-400' },
  'multiple_choice': { label: '多选', short: '多选', color: 'text-violet-400' },
  'fill_blank': { label: '填空', short: '填空', color: 'text-amber-400' },
  'code_required': { label: '编程', short: '编程', color: 'text-emerald-400' },
  'matching': { label: '匹配', short: '匹配', color: 'text-rose-400' },
  'essay': { label: '简答', short: '简答', color: 'text-cyan-400' },
  'true_false': { label: '判断', short: '判断', color: 'text-orange-400' },
  'unknown': { label: '未知', short: '未知', color: 'text-muted-foreground' },
}

function getTypeConfig(type: string): QuestionTypeConfig {
  return typeConfigMap[type] || typeConfigMap['unknown']
}

function isActive(q: Question): boolean {
  return q.status === 'solving'
}

function statusIcon(q: Question) {
  switch (q.status) {
    case 'solving':
      return Loader2
    case 'solved':
      return Circle
    case 'filled':
      return Check
    case 'error':
      return X
    default:
      return Circle
  }
}

function statusClass(q: Question): string {
  switch (q.status) {
    case 'solving':
      return 'text-primary animate-spin'
    case 'solved':
      return 'text-emerald-400'
    case 'filled':
      return 'text-emerald-400'
    case 'error':
      return 'text-red-400'
    default:
      return 'text-muted-foreground/30'
  }
}

function statusDotClass(q: Question): string {
  switch (q.status) {
    case 'solving':
      return 'bg-primary shadow-[0_0_6px_rgba(59,130,246,0.5)]'
    case 'solved':
      return 'bg-emerald-400 shadow-[0_0_4px_rgba(52,211,153,0.4)]'
    case 'filled':
      return 'bg-emerald-400'
    case 'error':
      return 'bg-red-400 shadow-[0_0_4px_rgba(248,113,113,0.4)]'
    default:
      return 'bg-muted-foreground/20'
  }
}

const computedQuestions = computed(() => props.questions)
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- Section header -->
    <div class="flex items-center gap-2 px-4 py-3 border-b border-border/60">
      <ListChecks class="h-4 w-4 text-muted-foreground" />
      <span class="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
        题目清单
      </span>
      <span
        v-if="computedQuestions.length"
        class="ml-auto tabular-nums text-xs text-muted-foreground"
      >
        {{ computedQuestions.length }} 题
      </span>
    </div>

    <!-- Question items -->
    <div class="flex-1 overflow-y-auto">
      <div v-if="computedQuestions.length === 0" class="px-4 py-8 text-center">
        <Circle class="mx-auto h-6 w-6 text-muted-foreground/25" />
        <p class="mt-2 text-xs text-muted-foreground/50">暂无题目</p>
      </div>

      <ul v-else class="divide-y divide-border/40">
        <li
          v-for="q in computedQuestions"
          :key="q.number"
          class="group relative cursor-pointer transition-colors duration-150 hover:bg-accent/50"
          :class="isActive(q) ? 'bg-accent/60' : ''"
          @click="emit('select', q)"
        >
          <!-- Left accent bar for active question -->
          <div
            v-if="isActive(q)"
            class="absolute inset-y-0 left-0 w-0.5 bg-primary shadow-[0_0_8px_rgba(59,130,246,0.4)]"
          />

          <div class="flex items-center gap-3 px-4 py-2.5">
            <!-- Number -->
            <span
              class="w-7 flex-shrink-0 tabular-nums text-xs font-mono font-medium"
              :class="isActive(q) ? 'text-primary' : 'text-muted-foreground'"
            >
              #{{ q.number }}
            </span>

            <!-- Type badge -->
            <span
              class="flex-shrink-0 inline-flex items-center rounded px-1.5 py-0.5 text-[10px] font-medium tracking-wide"
              :class="[
                getTypeConfig(q.type).color,
                isActive(q)
                  ? 'bg-primary/10'
                  : 'bg-muted/50',
              ]"
            >
              <Code v-if="q.type === 'code_required'" class="mr-0.5 h-2.5 w-2.5" />
              {{ getTypeConfig(q.type).short }}
            </span>

            <!-- Spacer -->
            <div class="flex-1 min-w-0">
              <p
                class="truncate text-xs"
                :class="isActive(q) ? 'text-foreground font-medium' : 'text-muted-foreground'"
              >
                {{ q.text || '...' }}
              </p>
            </div>

            <!-- Status icon -->
            <div class="flex-shrink-0 flex items-center gap-1.5">
              <!-- Status dot -->
              <div
                class="h-2 w-2 rounded-full transition-shadow duration-500"
                :class="statusDotClass(q)"
              />
              <!-- Status icon -->
              <component
                :is="statusIcon(q)"
                class="h-3.5 w-3.5 transition-all duration-300"
                :class="statusClass(q)"
                :stroke-width="q.status === 'filled' ? 2.5 : 2"
              />
            </div>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>
