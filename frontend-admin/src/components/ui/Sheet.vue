<template>
  <div v-if="modelValue" class="fixed inset-0 z-50 flex justify-end">
    <!-- Backdrop -->
    <div class="fixed inset-0 bg-black/50 backdrop-blur-xs transition-opacity" @click="close" />
    <!-- Panel -->
    <div
      :class="cn(
        'relative z-50 flex h-full w-full flex-col border-l bg-background p-6 shadow-2xl transition ease-in-out duration-300 animate-in slide-in-from-right overflow-y-auto',
        widthClass,
        $attrs.class as string
      )"
    >
      <div class="flex items-center justify-between pb-4 border-b">
        <div>
          <h2 v-if="title" class="text-lg font-semibold tracking-tight text-foreground">{{ title }}</h2>
          <p v-if="description" class="text-xs text-muted-foreground mt-0.5">{{ description }}</p>
        </div>
        <button
          class="rounded-md p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground cursor-pointer"
          @click="close"
        >
          <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      <div class="flex-1 py-4">
        <slot />
      </div>
      <div v-if="$slots.footer" class="pt-4 border-t flex justify-end gap-2">
        <slot name="footer" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { cn } from '../../lib/utils'

const props = withDefaults(
  defineProps<{
    modelValue: boolean
    title?: string
    description?: string
    size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  }>(),
  {
    title: '',
    description: '',
    size: 'md',
  }
)

const widthClass = computed(() => {
  switch (props.size) {
    case 'sm':
      return 'max-w-sm'
    case 'lg':
      return 'max-w-2xl'
    case 'xl':
      return 'max-w-4xl'
    case 'full':
      return 'max-w-full'
    case 'md':
    default:
      return 'max-w-lg'
  }
})

const emit = defineEmits<{
  (e: 'update:modelValue', val: boolean): void
}>()

const close = () => {
  emit('update:modelValue', false)
}
</script>
