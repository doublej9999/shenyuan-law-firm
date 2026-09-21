<template>
  <div class="grid grid-cols-1 md:grid-cols-4 gap-4 pb-4 select-none">
    <!-- Col: New -->
    <div
      v-for="col in columns"
      :key="col.key"
      class="flex flex-col rounded-xl border bg-muted/30 p-3 min-h-[500px]"
    >
      <!-- Col Header -->
      <div class="flex items-center justify-between pb-3 border-b border-border/60">
        <div class="flex items-center gap-2">
          <span :class="cn('h-2.5 w-2.5 rounded-full', col.dotClass)" />
          <span class="text-xs font-bold text-foreground">{{ col.title }}</span>
        </div>
        <span class="rounded-full bg-background px-2 py-0.5 text-[11px] font-semibold border text-muted-foreground">
          {{ getColumnList(col.key).length }}
        </span>
      </div>

      <!-- Cards Container -->
      <div class="flex-1 space-y-3 pt-3 overflow-y-auto max-h-[72vh]">
        <div
          v-for="item in getColumnList(col.key)"
          :key="item.id"
          class="rounded-lg border bg-card p-3 shadow-xs hover:shadow-md transition-shadow cursor-pointer space-y-2.5"
          @click="$emit('select', item)"
        >
          <!-- Card Header -->
          <div class="flex items-start justify-between gap-1">
            <span class="font-bold text-xs text-foreground truncate">
              #{{ item.id }} {{ item.name }}
            </span>
            <ScoreBadge :score="item.score || 0" />
          </div>

          <!-- Tags & Country -->
          <div class="flex items-center gap-1.5 flex-wrap">
            <Badge variant="outline" class="text-[10px] py-0">
              {{ item.matter }}
            </Badge>
            <span v-if="item.country_or_region" class="text-[10px] text-muted-foreground bg-muted px-1.5 py-0.5 rounded">
              🌍 {{ item.country_or_region }}
            </span>
          </div>

          <!-- Summary Snippet -->
          <p class="text-[11px] text-muted-foreground line-clamp-2 leading-relaxed">
            {{ item.summary }}
          </p>

          <!-- Footer with SLA -->
          <div class="pt-2 border-t border-border/40 flex items-center justify-between text-[10px]">
            <SlaBadge :created-at="item.created_at" :status="item.status" />
            <span class="text-muted-foreground/60 font-mono">{{ formatDate(item.created_at) }}</span>
          </div>
        </div>

        <div
          v-if="getColumnList(col.key).length === 0"
          class="flex flex-col items-center justify-center h-32 text-center text-muted-foreground/50 text-xs border border-dashed rounded-lg"
        >
          暂无此阶段线索
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { cn } from '../../lib/utils'
import Badge from '../ui/Badge.vue'
import SlaBadge from './SlaBadge.vue'
import ScoreBadge from './ScoreBadge.vue'

const props = defineProps<{
  list: any[]
}>()

defineEmits<{
  (e: 'select', item: any): void
}>()

const columns = [
  { key: 'new', title: '待初审新线索', dotClass: 'bg-rose-500' },
  { key: 'contacted', title: '已建立初联', dotClass: 'bg-amber-500' },
  { key: 'processing', title: '方案推进中', dotClass: 'bg-sky-500' },
  { key: 'closed', title: '已结案 / 转化', dotClass: 'bg-emerald-500' },
]

const getColumnList = (key: string) => {
  return props.list.filter((item) => (item.status || 'new') === key)
}

const formatDate = (iso: string) => {
  if (!iso) return ''
  const d = new Date(iso)
  return `${d.getMonth() + 1}-${d.getDate()} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
}
</script>
