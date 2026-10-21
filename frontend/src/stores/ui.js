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

  // Pinned tabs storage helper
  const PINNED_TABS_KEY = 'subscriptiq_pinned_tabs'
  const ACTIVE_TAB_KEY = 'subscriptiq_active_tab'

  function formatCleanTabName(name) {
    if (!name) return ''
    return String(name).replace(/\.(vue|sql|qdrant|audit|rules|json|ts|js|py)$/i, '')
  }

  function loadPinnedTabs() {
    try {
      const raw = localStorage.getItem(PINNED_TABS_KEY)
      if (raw) {
        const parsed = JSON.parse(raw)
        if (Array.isArray(parsed)) {
          return parsed
            .filter((t) => t && t.id && t.id !== 'dashboard')
            .map((t) => ({
              id: t.id,
              name: formatCleanTabName(t.name) || t.id,
              icon: t.icon || 'file',
              route: t.route || t.id,
              closable: true,
              isPinned: true,
            }))
        }
      }
    } catch (e) {
      console.warn('Failed to parse pinned tabs from storage:', e)
    }
    return []
  }

  function savePinnedTabs() {
    try {
      const pinned = tabs.value
        .filter((t) => t.isPinned && t.id !== 'dashboard')
        .map((t) => ({
          id: t.id,
          name: t.name,
          icon: t.icon,
          route: t.route,
        }))
      localStorage.setItem(PINNED_TABS_KEY, JSON.stringify(pinned))
    } catch (e) {
      console.warn('Failed to save pinned tabs to storage:', e)
    }
  }

  // Navigation & tabs initialization
  const restoredPinned = loadPinnedTabs()
  const tabs = ref([
    { id: 'dashboard', name: 'Dashboard Overview', icon: 'dashboard', route: 'dashboard', closable: false, isPinned: false },
    ...restoredPinned,
  ])

  const savedActiveTab = localStorage.getItem(ACTIVE_TAB_KEY)
  const initialActiveId = tabs.value.some((t) => t.id === savedActiveTab) ? savedActiveTab : 'dashboard'
  const activeTabId = ref(initialActiveId)
  const activeNav = ref(tabs.value.find((t) => t.id === initialActiveId)?.route || 'dashboard')

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

  function togglePinTab(tabId) {
    if (tabId === 'dashboard') return // Permanent tab
    const tab = tabs.value.find((t) => t.id === tabId)
    if (!tab) return

    tab.isPinned = !tab.isPinned
    savePinnedTabs()
  }

  function openQueryAnalysisTab(queryTitle = 'Chat Analysis') {
    const existing = tabs.value.find((t) => t.id === 'query-analysis' || t.id === 'query-results')

    if (existing) {
      existing.id = 'query-analysis'
      existing.name = 'Chat Analysis'
      existing.route = 'query-analysis'
    } else {
      // Find insertion point right after all pinned tabs, or index 1
      let insertIdx = 1
      for (let i = tabs.value.length - 1; i >= 0; i--) {
        if (tabs.value[i].isPinned) {
          insertIdx = i + 1
          break
        }
      }
      tabs.value.splice(insertIdx, 0, {
        id: 'query-analysis',
        name: 'Chat Analysis',
        icon: 'analytics',
        route: 'query-analysis',
        closable: true,
        isPinned: false,
      })
    }
    activeTabId.value = 'query-analysis'
    activeNav.value = 'query-analysis'
    localStorage.setItem(ACTIVE_TAB_KEY, 'query-analysis')
  }

  function openAboutTab() {
    const existing = tabs.value.find((t) => t.id === 'about')
    if (!existing) {
      tabs.value.push({
        id: 'about',
        name: 'About SubscriptIQ',
        icon: 'info',
        route: 'about',
        closable: true,
        isPinned: false,
      })
    }
    activeTabId.value = 'about'
    activeNav.value = 'about'
    localStorage.setItem(ACTIVE_TAB_KEY, 'about')
  }

  function setActiveNav(navId, tabName = null) {
    if (navId === 'query-analysis' || navId === 'query-results') {
      openQueryAnalysisTab(tabName)
      return
    }

    if (navId === 'about') {
      openAboutTab()
      return
    }

    activeNav.value = navId
    const existing = tabs.value.find((t) => t.id === navId)
    if (existing) {
      activeTabId.value = existing.id
      localStorage.setItem(ACTIVE_TAB_KEY, existing.id)
    } else if (tabName) {
      tabs.value.push({
        id: navId,
        name: formatCleanTabName(tabName),
        icon: navId.startsWith('admin') ? 'shield' : 'file',
        route: navId,
        closable: true,
        isPinned: false,
      })
      activeTabId.value = navId
      localStorage.setItem(ACTIVE_TAB_KEY, navId)
    } else if (navId === 'dashboard') {
      activeTabId.value = 'dashboard'
      localStorage.setItem(ACTIVE_TAB_KEY, 'dashboard')
    }
  }

  function closeTab(tabId) {
    const idx = tabs.value.findIndex((t) => t.id === tabId)
    // Only unpinned, closable tabs can be removed (matching "on unpin it can be removed")
    if (idx !== -1 && tabs.value[idx].closable && !tabs.value[idx].isPinned) {
      tabs.value.splice(idx, 1)
      savePinnedTabs()
      if (activeTabId.value === tabId) {
        activeTabId.value = 'dashboard'
        activeNav.value = 'dashboard'
        localStorage.setItem(ACTIVE_TAB_KEY, 'dashboard')
      }
    }
  }

  function activateTab(tab) {
    activeTabId.value = tab.id
    activeNav.value = tab.route
    localStorage.setItem(ACTIVE_TAB_KEY, tab.id)
  }

  // ==========================================
  // Global Action Confirmation Dialog State
  // ==========================================
  const confirmDialog = ref({
    isOpen: false,
    title: 'Confirm Action',
    message: '',
    subMessage: '',
    confirmText: 'Confirm',
    cancelText: 'Cancel',
    type: 'danger', // 'danger' | 'warning' | 'info' | 'primary'
    icon: 'trash',
    resolve: null,
  })

  function openConfirmModal({
    title = 'Confirm Action',
    message = 'Are you sure you want to proceed?',
    subMessage = '',
    confirmText = 'Confirm',
    cancelText = 'Cancel',
    type = 'danger',
    icon = 'trash',
  } = {}) {
    return new Promise((resolve) => {
      confirmDialog.value = {
        isOpen: true,
        title,
        message,
        subMessage,
        confirmText,
        cancelText,
        type,
        icon,
        resolve,
      }
    })
  }

  function handleConfirmResult(confirmed) {
    if (confirmDialog.value.resolve) {
      confirmDialog.value.resolve(confirmed)
    }
    confirmDialog.value.isOpen = false
    confirmDialog.value.resolve = null
  }

  // ==========================================
  // Global Notification Toast System
  // ==========================================
  const toasts = ref([])

  function showToast(message, type = 'success', duration = 3500) {
    const id = Date.now() + Math.random().toString(36).substring(2, 7)
    toasts.value.push({ id, message, type })
    if (duration > 0) {
      setTimeout(() => {
        removeToast(id)
      }, duration)
    }
  }

  function removeToast(id) {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }

  return {
    isSidebarCollapsed,
    isChatCollapsed,
    theme,
    activeNav,
    tabs,
    activeTabId,
    confirmDialog,
    openConfirmModal,
    handleConfirmResult,
    toasts,
    showToast,
    removeToast,
    toggleSidebar,
    toggleChat,
    toggleTheme,
    togglePinTab,
    setActiveNav,
    openQueryAnalysisTab,
    openQueryResultsTab: openQueryAnalysisTab,
    closeTab,
    activateTab,
  }
})
