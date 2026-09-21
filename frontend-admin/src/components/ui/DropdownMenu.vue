<template>
  <div class="relative inline-block text-left" ref="dropdownRef">
    <div @click="toggle">
      <slot name="trigger" />
    </div>

    <div
      v-if="isOpen"
      :class="cn(
        'absolute z-50 mt-2 min-w-[8rem] overflow-hidden rounded-md border bg-popover p-1 text-popover-foreground shadow-md animate-in fade-in-80 zoom-in-95',
        align === 'end' ? 'right-0' : 'left-0',
        $attrs.class as string
      )"
    >
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onClickOutside } from '@vueuse/core'
import { cn } from '../../lib/utils'

withDefaults(
  defineProps<{
    align?: 'start' | 'end'
  }>(),
  {
    align: 'end',
  }
)

const isOpen = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)

const toggle = () => {
  isOpen.value = !isOpen.value
}

const close = () => {
  isOpen.value = false
}

onClickOutside(dropdownRef, close)

defineExpose({ close })
</script>
