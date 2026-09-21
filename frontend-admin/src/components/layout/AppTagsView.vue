<template>
  <div class="h-9 border-b bg-card/40 px-3 flex items-center gap-1 overflow-x-auto select-none no-scrollbar">
    <router-link
      v-for="tag in tagsStore.visitedTags"
      :key="tag.path"
      :to="tag.path"
      :class="cn(
        'group flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium transition-colors border cursor-pointer shrink-0',
        $route.path === tag.path
          ? 'bg-primary/10 border-primary/30 text-primary font-semibold'
          : 'bg-background/80 border-border text-muted-foreground hover:bg-muted/80 hover:text-foreground'
      )"
    >
      <span>{{ tag.title }}</span>
      <span
        v-if="tagsStore.visitedTags.length > 1"
        class="rounded-full p-0.5 opacity-60 group-hover:opacity-100 hover:bg-muted-foreground/20 cursor-pointer"
        @click.prevent.stop="tagsStore.removeTag(tag.path)"
      >
        <X class="h-3 w-3" />
      </span>
    </router-link>
  </div>
</template>

<script setup lang="ts">
import { useTagsStore } from '../../stores/tags'
import { cn } from '../../lib/utils'
import { X } from 'lucide-vue-next'

const tagsStore = useTagsStore()
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
