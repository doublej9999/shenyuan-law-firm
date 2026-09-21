<template>
  <div class="prose prose-sm dark:prose-invert max-w-none text-xs leading-relaxed" v-html="renderedHtml" />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({
  html: false,
  linkify: true,
  typographer: true,
})

const props = withDefaults(
  defineProps<{
    content?: string
  }>(),
  {
    content: '',
  }
)

const renderedHtml = computed(() => {
  if (!props.content) return '<p class="text-muted-foreground italic">暂无内容，支持 Markdown 语法...</p>'
  return md.render(props.content)
})
</script>
