<template>
  <div v-if="appStore.commandPaletteOpen" class="fixed inset-0 z-50 flex items-start justify-center pt-20 px-4">
    <!-- Backdrop -->
    <div class="fixed inset-0 bg-black/60 backdrop-blur-xs" @click="appStore.toggleCommandPalette" />

    <!-- Command Palette Dialog -->
    <div class="relative w-full max-w-lg rounded-xl border bg-popover shadow-2xl overflow-hidden animate-in fade-in-0 zoom-in-95">
      <div class="flex items-center border-b px-3 h-12">
        <Search class="mr-2 h-4 w-4 shrink-0 text-muted-foreground" />
        <input
          v-model="query"
          type="text"
          placeholder="快速搜索功能、线索或调研知识库..."
          class="flex h-10 w-full rounded-md bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50"
          autofocus
          @keydown.esc="appStore.toggleCommandPalette"
        />
        <kbd class="pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground">
          ESC
        </kbd>
      </div>

      <!-- Quick List -->
      <div class="max-h-80 overflow-y-auto p-2">
        <div class="px-2 py-1.5 text-[11px] font-semibold text-muted-foreground">快捷功能导航</div>
        <div
          v-for="item in filteredActions"
          :key="item.path"
          class="flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium hover:bg-muted cursor-pointer transition-colors"
          @click="navigate(item.path)"
        >
          <div class="flex items-center gap-2.5">
            <component :is="item.icon" class="h-4 w-4 text-primary" />
            <span>{{ item.title }}</span>
          </div>
          <span class="text-[10px] text-muted-foreground">{{ item.desc }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../../stores/app'
import {
  Search,
  LayoutDashboard,
  Users,
  FileText,
  Sparkles,
  BookOpen,
} from 'lucide-vue-next'

const router = useRouter()
const appStore = useAppStore()
const query = ref('')

const actions = [
  { title: '经营分析大盘', desc: '查看咨询概览与国家分析', path: '/dashboard', icon: LayoutDashboard },
  { title: '涉外线索中枢 (CRM)', desc: '跟进处理 24h SLA 涉外商事线索', path: '/crm', icon: Users },
  { title: '多语言 CMS 文章库', desc: '撰写双语文章与发布流', path: '/content', icon: FileText },
  { title: '涉外法律调研 (AI Memo)', desc: '检索知识库并生成案情备忘录', path: '/research', icon: BookOpen },
  { title: '出海营销素材矩阵', desc: '7 渠道出海推文与排期生成', path: '/marketing', icon: Sparkles },
]

const filteredActions = computed(() => {
  if (!query.value) return actions
  const q = query.value.toLowerCase()
  return actions.filter(
    (a) => a.title.toLowerCase().includes(q) || a.desc.toLowerCase().includes(q)
  )
})

const navigate = (path: string) => {
  router.push(path)
  appStore.commandPaletteOpen = false
  query.value = ''
}

const handleKeydown = (e: KeyboardEvent) => {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    appStore.toggleCommandPalette()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>
