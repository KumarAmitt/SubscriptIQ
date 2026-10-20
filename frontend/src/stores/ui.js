import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUIStore = defineStore('ui', () => {
  // Sidebar state (thin rail when collapsed)
  const isSidebarCollapsed = ref(false)

  // AI Chat Agent area (collapsible)
  const isChatCollapsed = ref(false)

  // Theme mode: 'dark' or 'light'
  const savedTheme = localStorage.getItem('subscriptiq_theme') || 'dark'
  const theme = ref(savedTheme)
  document.documentElement.setAttribute('data-theme', theme.value)

  // Navigation & tabs
  const activeNav = ref('dashboard')
  const tabs = ref([
    { id: 'dashboard', name: 'Dashboard.vue', icon: 'dashboard', route: 'dashboard', closable: false },
    { id: 'intelligence', name: 'CopilotInsight.ts', icon: 'sparkles', route: 'intelligence', closable: true },
  ])
  const activeTabId = ref('dashboard')

  function toggleSidebar() {
    isSidebarCollapsed.value = !isSidebarCollapsed.value
  }

  function toggleChat() {
    isChatCollapsed.value = !isChatCollapsed.value
  }

  function toggleTheme() {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
    document.documentElement.setAttribute('data-theme', theme.value)
    localStorage.setItem('subscriptiq_theme', theme.value)
  }

  function setActiveNav(navId, tabName = null) {
    activeNav.value = navId
    // If there's an associated tab, activate or open it
    const existing = tabs.value.find((t) => t.id === navId)
    if (existing) {
      activeTabId.value = existing.id
    } else if (tabName) {
      tabs.value.push({
        id: navId,
        name: tabName,
        icon: navId.startsWith('admin') ? 'shield' : 'file',
        route: navId,
        closable: true,
      })
      activeTabId.value = navId
    }
  }

  function closeTab(tabId) {
    const idx = tabs.value.findIndex((t) => t.id === tabId)
    if (idx !== -1) {
      tabs.value.splice(idx, 1)
      if (activeTabId.value === tabId && tabs.value.length > 0) {
        const nextTab = tabs.value[Math.max(0, idx - 1)]
        activeTabId.value = nextTab.id
        activeNav.value = nextTab.route
      }
    }
  }

  function activateTab(tab) {
    activeTabId.value = tab.id
    activeNav.value = tab.route
  }

  return {
    isSidebarCollapsed,
    isChatCollapsed,
    theme,
    activeNav,
    tabs,
    activeTabId,
    toggleSidebar,
    toggleChat,
    toggleTheme,
    setActiveNav,
    closeTab,
    activateTab,
  }
})
