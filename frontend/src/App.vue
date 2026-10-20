<template>
  <div class="app-container">
    <!-- Top Bar: Window controls, Command Search, Theme & Role switchers -->
    <AppTopBar />

    <!-- App Body: Left Sidebar + Middle Interaction Area + Right AI Copilot -->
    <div class="app-body">
      <!-- Left: Collapsible Side Menu (collapses to thin rails with hover tooltips) -->
      <AppSidebar />

      <!-- Middle: User Interaction Area with Editor Tabs, Breadcrumbs, Views -->
      <AppMainContent />

      <!-- Right: Collapsible AI Chat Agent Area -->
      <AppChatAgent />
    </div>

    <!-- Bottom: IDE Status Bar -->
    <AppStatusBar />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import AppTopBar from '@/components/layout/AppTopBar.vue'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppMainContent from '@/components/layout/AppMainContent.vue'
import AppChatAgent from '@/components/layout/AppChatAgent.vue'
import AppStatusBar from '@/components/layout/AppStatusBar.vue'
import { useUIStore } from '@/stores/ui'

const uiStore = useUIStore()

onMounted(() => {
  // Support standard modern IDE shortcuts
  window.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + B: Toggle Sidebar
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'b') {
      e.preventDefault()
      uiStore.toggleSidebar()
    }
    // Ctrl/Cmd + J: Toggle Right Chat Agent
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'j') {
      e.preventDefault()
      uiStore.toggleChat()
    }
  })
})
</script>

<style scoped>
/* App layout containers are styled in main.css for global consistency */
</style>
