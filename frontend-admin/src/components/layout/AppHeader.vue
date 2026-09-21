<template>
  <header class="h-14 border-b bg-card/60 backdrop-blur-md px-4 flex items-center justify-between z-20">
    <!-- Breadcrumbs & Quick Search -->
    <div class="flex items-center gap-4">
      <div class="flex items-center text-xs text-muted-foreground">
        <span>深远业务中台</span>
        <span class="mx-2 text-muted-foreground/40">/</span>
        <span class="font-medium text-foreground">{{ $route.meta.title || '工作区' }}</span>
      </div>

      <!-- Quick Command Bar Trigger -->
      <button
        class="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-md border bg-muted/40 text-xs text-muted-foreground hover:bg-muted transition-colors cursor-pointer"
        @click="appStore.toggleCommandPalette"
      >
        <Search class="h-3.5 w-3.5" />
        <span>搜索功能或法条...</span>
        <kbd class="pointer-events-none inline-flex h-4 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground opacity-100">
          ⌘K
        </kbd>
      </button>
    </div>

    <!-- Right Controls -->
    <div class="flex items-center gap-2">
      <!-- Dark mode switch -->
      <Button variant="ghost" size="icon" class="h-8 w-8 text-muted-foreground hover:text-foreground" @click="appStore.toggleDarkMode">
        <Sun v-if="appStore.isDarkMode" class="h-4 w-4" />
        <Moon v-else class="h-4 w-4" />
      </Button>

      <!-- Status Indicator -->
      <div class="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-[11px] font-medium text-emerald-600 dark:text-emerald-400">
        <span class="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-ping" />
        <span>Postgres WAL 正常</span>
      </div>

      <!-- Logout button -->
      <Button variant="outline" size="sm" class="text-xs h-8 ml-2" @click="handleLogout">
        <LogOut class="mr-1.5 h-3.5 w-3.5" />
        退出
      </Button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAppStore } from '../../stores/app'
import Button from '../ui/Button.vue'
import { Search, Sun, Moon, LogOut } from 'lucide-vue-next'

const router = useRouter()
const appStore = useAppStore()

const handleLogout = () => {
  localStorage.removeItem('shenyuan_admin_token')
  router.push('/login')
}
</script>
