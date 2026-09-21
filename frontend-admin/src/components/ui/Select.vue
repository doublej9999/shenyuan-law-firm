<template>
  <div class="relative w-full">
    <select
      :value="modelValue"
      :disabled="disabled"
      :class="cn(
        'flex h-9 w-full items-center justify-between rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring disabled:cursor-not-allowed disabled:opacity-50 appearance-none pr-8 cursor-pointer',
        $attrs.class as string
      )"
      @change="$emit('update:modelValue', ($event.target as HTMLSelectElement).value)"
    >
      <slot />
    </select>
    <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-muted-foreground">
      <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </div>
  </div>
</template>

<script setup lang="ts">
import { cn } from '../../lib/utils'

defineProps<{
  modelValue?: string | number
  disabled?: boolean
}>()

defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()
</script>
