<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
const links = [
  { path: '/', label: '仪表盘' },
  { path: '/session', label: '答题' },
  { path: '/config', label: '配置' },
  { path: '/history', label: '历史' },
]
</script>

<template>
  <nav class="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
    <div class="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
      <div class="flex items-center gap-2">
        <span class="text-primary font-bold text-lg">Auto-Answer</span>
      </div>
      <div class="flex items-center gap-1">
        <router-link
          v-for="link in links"
          :key="link.path"
          :to="link.path"
          class="px-3 py-1.5 rounded-md text-sm transition-colors"
          :class="route.path === link.path
            ? 'bg-primary/10 text-primary font-medium'
            : 'text-muted-foreground hover:text-foreground hover:bg-accent'"
        >
          {{ link.label }}
        </router-link>
      </div>
    </div>
  </nav>
</template>
