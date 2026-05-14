<script setup lang="ts">
import { computed } from 'vue'
import { CheckCircle2, AlertCircle, Circle } from 'lucide-vue-next'

const props = defineProps<{
  title: string
  status: string
  ok: boolean
}>()

const statusIcon = computed(() => {
  if (props.ok) return CheckCircle2
  return AlertCircle
})

const iconClass = computed(() => {
  if (props.ok) return 'text-emerald-400'
  return 'text-amber-400'
})

const dotClass = computed(() => {
  if (props.ok) return 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.5)]'
  return 'bg-amber-400 shadow-[0_0_8px_rgba(251,191,36,0.4)]'
})
</script>

<template>
  <div
    class="group relative overflow-hidden rounded-xl border border-border bg-card p-5 transition-all duration-200 hover:scale-[1.02] hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5 focus-within:ring-2 focus-within:ring-primary/50 cursor-default"
  >
    <!-- Subtle top accent bar -->
    <div
      class="absolute inset-x-0 top-0 h-0.5 transition-colors duration-200"
      :class="ok ? 'bg-emerald-400/60' : 'bg-amber-400/60'"
    />

    <div class="flex items-start gap-4">
      <!-- Status indicator with icon -->
      <div class="relative mt-0.5 flex-shrink-0">
        <div
          class="absolute inset-0 rounded-full animate-pulse opacity-40"
          :class="ok ? 'bg-emerald-400' : 'bg-amber-400'"
        />
        <component
          :is="statusIcon"
          :class="iconClass"
          class="relative z-10 h-5 w-5"
        />
      </div>

      <!-- Text content -->
      <div class="min-w-0 flex-1">
        <p class="text-xs font-medium uppercase tracking-wider text-muted-foreground">
          {{ title }}
        </p>
        <p
          class="mt-1 text-sm font-medium leading-tight truncate"
          :class="ok ? 'text-foreground' : 'text-muted-foreground'"
        >
          {{ status }}
        </p>
      </div>

      <!-- Status dot -->
      <div class="flex-shrink-0 mt-1.5">
        <div
          class="h-2.5 w-2.5 rounded-full transition-shadow duration-500"
          :class="dotClass"
        />
      </div>
    </div>
  </div>
</template>
