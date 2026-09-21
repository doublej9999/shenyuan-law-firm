<template>
  <div class="flex h-screen w-screen overflow-hidden bg-background text-foreground">
    <!-- Sidebar -->
    <AppSidebar />

    <!-- Main Viewport -->
    <div class="flex flex-1 flex-col overflow-hidden">
      <!-- Top Header -->
      <AppHeader />

      <!-- Tab View -->
      <AppTagsView />

      <!-- Router Content Page -->
      <main class="flex-1 overflow-y-auto p-4 md:p-6 bg-muted/20">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>

    <!-- Command Palette Modal -->
    <AppCommandPalette />
  </div>
</template>

<script setup lang="ts">
import { watch } from 'vue'
import { useRoute } from 'vue-router'
import { useTagsStore } from '../stores/tags'
import AppSidebar from '../components/layout/AppSidebar.vue'
import AppHeader from '../components/layout/AppHeader.vue'
import AppTagsView from '../components/layout/AppTagsView.vue'
import AppCommandPalette from '../components/layout/AppCommandPalette.vue'

const route = useRoute()
const tagsStore = useTagsStore()

watch(
  () => route.path,
  () => {
    tagsStore.addTag(route)
  },
  { immediate: true }
)
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
