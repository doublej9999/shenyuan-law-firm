<template>
  <div :class="cn(badgeVariants({ variant }), $attrs.class as string)">
    <slot />
  </div>
</template>

<script setup lang="ts">
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '../../lib/utils'

const badgeVariants = cva(
  'inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
  {
    variants: {
      variant: {
        default: 'border-transparent bg-primary text-primary-foreground shadow',
        secondary: 'border-transparent bg-secondary text-secondary-foreground',
        destructive: 'border-transparent bg-destructive/15 text-destructive border-destructive/20',
        outline: 'text-foreground',
        success: 'border-emerald-500/20 bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300',
        warning: 'border-amber-500/20 bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300',
        info: 'border-sky-500/20 bg-sky-50 text-sky-700 dark:bg-sky-950/40 dark:text-sky-300',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
)

type BadgeVariants = VariantProps<typeof badgeVariants>

defineProps<{
  variant?: BadgeVariants['variant']
}>()
</script>
