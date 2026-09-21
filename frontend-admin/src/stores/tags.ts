import { defineStore } from 'pinia'
import { ref } from 'vue'
import { RouteLocationNormalized } from 'vue-router'

export interface TagItem {
  title: string
  path: string
  name?: string
}

export const useTagsStore = defineStore('tags', () => {
  const visitedTags = ref<TagItem[]>([
    { title: '经营大盘', path: '/dashboard' },
  ])

  const addTag = (route: RouteLocationNormalized) => {
    if (!route.meta?.title || route.path === '/login') return
    const exists = visitedTags.value.some((t) => t.path === route.path)
    if (!exists) {
      visitedTags.value.push({
        title: (route.meta.title as string) || '未命名',
        path: route.path,
        name: route.name as string,
      })
    }
  }

  const removeTag = (path: string) => {
    if (visitedTags.value.length <= 1) return
    visitedTags.value = visitedTags.value.filter((t) => t.path !== path)
  }

  return {
    visitedTags,
    addTag,
    removeTag,
  }
})
