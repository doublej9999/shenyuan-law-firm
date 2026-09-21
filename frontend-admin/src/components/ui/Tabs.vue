<template>
  <div class="flex items-center space-x-1 rounded-lg bg-muted p-1 text-muted-foreground">
    <button
      v-for="item in items"
      :key="item.value"
      :class="cn(
        'inline-flex items-center justify-center whitespace-nowrap rounded-md px-3 py-1.5 text-xs font-medium ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 cursor-pointer',
        modelValue === item.value
          ? 'bg-background text-foreground shadow-xs font-semibold'
          : 'hover:bg-background/50 hover:text-foreground'
      )"
      @click="$emit('update:modelValue', item.value)"
    >
      <component :is="item.icon" v-if="item.icon" class="mr-1.5 h-3.5 w-3.5" />
      {{ item.label }}
      <span
        v-if="item.count !== undefined"
        class="ml-1.5 rounded-full bg-muted-foreground/15 px-1.5 py-0.2 text-[10px]"
      >
        {{ item.count }}
      </span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { cn } from '../../lib/utils'

export interface TabItem {
  label: string
  value: string
  icon?: any
  count?: number
}

defineProps<{
  modelValue: string
  items: TabItem[]
}>()

defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()
</script>
