<template>
  <div v-if="modelValue" class="fixed inset-0 z-50 flex items-center justify-center">
    <!-- Backdrop -->
    <div class="fixed inset-0 bg-black/60 backdrop-blur-xs transition-opacity" @click="closeOnBackdrop && close()" />
    <!-- Content Modal -->
    <div
      :class="cn(
        'relative z-50 grid w-full max-w-lg gap-4 border bg-background p-6 shadow-lg duration-200 sm:rounded-lg animate-in fade-in-0 zoom-in-95',
        $attrs.class as string
      )"
    >
      <div v-if="title || description" class="flex flex-col space-y-1.5 text-center sm:text-left">
        <h2 v-if="title" class="text-lg font-semibold leading-none tracking-tight">{{ title }}</h2>
        <p v-if="description" class="text-sm text-muted-foreground">{{ description }}</p>
      </div>
      <slot />
      <button
        class="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none disabled:pointer-events-none cursor-pointer"
        @click="close"
      >
        <span class="sr-only">Close</span>
        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { cn } from '../../lib/utils'

withDefaults(
  defineProps<{
    modelValue: boolean
    title?: string
    description?: string
    closeOnBackdrop?: boolean
  }>(),
  {
    title: '',
    description: '',
    closeOnBackdrop: true,
  }
)

const emit = defineEmits<{
  (e: 'update:modelValue', val: boolean): void
}>()

const close = () => {
  emit('update:modelValue', false)
}
</script>
