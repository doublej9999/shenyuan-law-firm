<template>
  <aside
    :class="cn(
      'flex flex-col border-r transition-all duration-300 select-none z-30',
      'bg-[hsl(var(--sidebar-background))] text-[hsl(var(--sidebar-foreground))] border-[hsl(var(--sidebar-border))]',
      appStore.sidebarCollapsed ? 'w-16' : 'w-64'
    )"
  >
    <!-- Brand Header -->
    <div class="flex h-16 items-center px-4 border-b border-[hsl(var(--sidebar-border))] justify-between">
      <div class="flex items-center gap-3 overflow-hidden">
        <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-[hsl(var(--sidebar-primary))] text-white font-bold text-base shadow-sm">
          申
        </div>
        <div v-if="!appStore.sidebarCollapsed" class="flex flex-col truncate">
          <span class="font-bold text-sm tracking-wide text-white">深远涉外律所</span>
          <span class="text-[11px] text-[hsl(var(--sidebar-foreground))]/70 font-medium">业务中台 · Legal Admin</span>
        </div>
      </div>
      <button
        v-if="!appStore.sidebarCollapsed"
        class="text-white/60 hover:text-white p-1 rounded hover:bg-white/10 cursor-pointer"
        @click="appStore.toggleSidebar"
      >
        <ChevronLeft class="h-4 w-4" />
      </button>
    </div>

    <!-- Navigation List -->
    <div class="flex-1 overflow-y-auto py-3 px-2 space-y-1">
      <div v-if="!appStore.sidebarCollapsed" class="px-3 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-white/40">
        核心业务
      </div>
      <router-link
        v-for="item in menuItems"
        :key="item.path"
        :to="item.path"
        :class="cn(
          'flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-colors cursor-pointer group',
          $route.path.startsWith(item.path)
            ? 'bg-[hsl(var(--sidebar-accent))] text-white font-semibold shadow-xs'
            : 'text-[hsl(var(--sidebar-foreground))]/80 hover:bg-white/5 hover:text-white'
        )"
      >
        <component :is="item.icon" class="h-4 w-4 shrink-0" />
        <span v-if="!appStore.sidebarCollapsed" class="truncate">{{ item.label }}</span>
        <span
          v-if="!appStore.sidebarCollapsed && item.badge"
          class="ml-auto rounded-full bg-amber-500/20 text-amber-300 px-1.5 py-0.5 text-[10px]"
        >
          {{ item.badge }}
        </span>
      </router-link>

      <div v-if="!appStore.sidebarCollapsed" class="pt-4 px-3 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-white/40">
        对外与支撑
      </div>
      <a
        href="https://shenyuan-web.vercel.app"
        target="_blank"
        :class="cn(
          'flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium text-[hsl(var(--sidebar-foreground))]/70 hover:bg-white/5 hover:text-white transition-colors cursor-pointer'
        )"
      >
        <ExternalLink class="h-4 w-4 shrink-0" />
        <span v-if="!appStore.sidebarCollapsed" class="truncate">访问官网门户 ↗</span>
      </a>
    </div>

    <!-- Bottom Collapsed Toggle -->
    <div class="p-3 border-t border-[hsl(var(--sidebar-border))] flex items-center justify-between">
      <button
        v-if="appStore.sidebarCollapsed"
        class="w-full flex items-center justify-center p-2 rounded hover:bg-white/10 text-white/70 hover:text-white cursor-pointer"
        @click="appStore.toggleSidebar"
      >
        <ChevronRight class="h-4 w-4" />
      </button>
      <div v-else class="flex items-center gap-2 text-xs text-white/60">
        <div class="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
        <span>Supabase 云端在线</span>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { useAppStore } from '../../stores/app'
import { cn } from '../../lib/utils'
import {
  LayoutDashboard,
  Users,
  FileText,
  Search,
  Sparkles,
  ExternalLink,
  ChevronLeft,
  ChevronRight,
} from 'lucide-vue-next'

const appStore = useAppStore()

const menuItems = [
  { label: '经营概览大盘', path: '/dashboard', icon: LayoutDashboard },
  { label: '涉外线索流转 (CRM)', path: '/crm', icon: Users, badge: 'SLA' },
  { label: '多语言内容中心 (CMS)', path: '/content', icon: FileText },
  { label: '涉外法律调研 (Memo)', path: '/research', icon: Search },
  { label: '出海营销矩阵 (Marketing)', path: '/marketing', icon: Sparkles },
]
</script>
