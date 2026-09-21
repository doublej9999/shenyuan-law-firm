<template>
  <div
    :class="cn(
      'inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-semibold',
      config.bg,
      config.text
    )"
  >
    <Zap class="h-3 w-3" />
    <span>{{ score }}分 · {{ config.label }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { cn } from '../../lib/utils'
import { Zap } from 'lucide-vue-next'

const props = defineProps<{
  score: number
}>()

const config = computed(() => {
  if (props.score >= 40) {
    return { label: '高价值', bg: 'bg-emerald-500/15', text: 'text-emerald-700 dark:text-emerald-400' }
  }
  if (props.score >= 20) {
    return { label: '重点意向', bg: 'bg-amber-500/15', text: 'text-amber-700 dark:text-amber-400' }
  }
  return { label: '常规线索', bg: 'bg-slate-500/15', text: 'text-slate-600 dark:text-slate-400' }
})
</script>
