<template>
  <div
    :class="cn(
      'inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-medium border',
      slaState.colorClass
    )"
  >
    <Clock class="h-3 w-3" />
    <span>{{ slaState.label }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { cn } from '../../lib/utils'
import { Clock } from 'lucide-vue-next'

const props = defineProps<{
  createdAt: string
  status: string
}>()

const slaState = computed(() => {
  if (props.status === 'closed') {
    return { label: '已结案', colorClass: 'bg-muted text-muted-foreground border-transparent' }
  }
  if (props.status === 'processing' || props.status === 'contacted') {
    return { label: '推进中', colorClass: 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20' }
  }

  // 新线索 24h SLA 计算
  const createdTime = new Date(props.createdAt).getTime()
  const now = Date.now()
  const elapsedHours = (now - createdTime) / (1000 * 60 * 60)
  const remainingHours = Math.max(0, 24 - elapsedHours)

  if (elapsedHours >= 24) {
    return {
      label: `SLA 逾期 ${Math.floor(elapsedHours - 24)}h`,
      colorClass: 'bg-rose-500/10 text-rose-600 border-rose-500/30 animate-pulse font-semibold',
    }
  }
  if (remainingHours <= 4) {
    return {
      label: `剩余 ${remainingHours.toFixed(1)}h 响应`,
      colorClass: 'bg-amber-500/10 text-amber-600 border-amber-500/30 font-medium',
    }
  }
  return {
    label: `24h SLA (余 ${remainingHours.toFixed(0)}h)`,
    colorClass: 'bg-sky-500/10 text-sky-600 border-sky-500/20',
  }
})
</script>
