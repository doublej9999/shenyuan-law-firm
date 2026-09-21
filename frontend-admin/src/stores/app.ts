import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const sidebarCollapsed = ref(false)
  const isDarkMode = ref(false)
  const commandPaletteOpen = ref(false)

  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  const toggleDarkMode = () => {
    isDarkMode.value = !isDarkMode.value
    if (isDarkMode.value) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  const toggleCommandPalette = () => {
    commandPaletteOpen.value = !commandPaletteOpen.value
  }

  return {
    sidebarCollapsed,
    isDarkMode,
    commandPaletteOpen,
    toggleSidebar,
    toggleDarkMode,
    toggleCommandPalette,
  }
})
