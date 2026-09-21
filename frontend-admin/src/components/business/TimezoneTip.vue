<template>
  <div class="inline-flex items-center gap-1.5 text-xs text-muted-foreground bg-muted/40 px-2 py-1 rounded">
    <Globe class="h-3.5 w-3.5 text-primary" />
    <span>{{ country || '海外地区' }}</span>
    <span class="text-[10px] text-muted-foreground/80 font-mono">({{ tzInfo.offset }})</span>
    <span :class="cn('text-[10px] font-semibold px-1 rounded', tzInfo.isWorking ? 'text-emerald-600 bg-emerald-500/10' : 'text-amber-600 bg-amber-500/10')">
      {{ tzInfo.status }}
    </span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { cn } from '../../lib/utils'
import { Globe } from 'lucide-vue-next'

const props = defineProps<{
  country?: string
}>()

const tzInfo = computed(() => {
  const c = props.country || ''
  if (c.includes('美国') || c.includes('美') || c.includes('US')) {
    return { offset: 'UTC-5 / -8', isWorking: false, status: '注意时差联络' }
  }
  if (c.includes('英国') || c.includes('UK') || c.includes('欧洲')) {
    return { offset: 'UTC+0', isWorking: true, status: '工作时段' }
  }
  if (c.includes('新加坡') || c.includes('香港') || c.includes('马来西亚')) {
    return { offset: 'UTC+8', isWorking: true, status: '同北京时区' }
  }
  if (c.includes('澳洲') || c.includes('澳大利亚')) {
    return { offset: 'UTC+10', isWorking: true, status: '时差+2h' }
  }
  return { offset: '跨国法域', isWorking: true, status: '涉外联络' }
})
</script>
