<template>
  <main class="app-main-content">
    <!-- Code-Editor Style Tab Bar -->
    <div class="editor-tabs-bar">
      <div class="tabs-scroll-area">
        <div
          v-for="tab in uiStore.tabs"
          :key="tab.id"
          class="editor-tab font-mono"
          :class="{
            'is-active': uiStore.activeTabId === tab.id,
            'is-pinned': tab.isPinned
          }"
          @click="uiStore.activateTab(tab)"
        >
          <div class="tab-icon">
            <Icon :name="tab.icon" :size="12" />
          </div>
          <span class="tab-name" :title="cleanTabName(tab.name)">{{ cleanTabName(tab.name) }}</span>

          <!-- Tab Action Controls (for all tabs except Dashboard) -->
          <div v-if="tab.id !== 'dashboard'" class="tab-actions">
            <!-- Pin / Unpin Button -->
            <button
              class="tab-action-btn tab-pin-btn"
              :class="{ 'is-pinned': tab.isPinned }"
              @click.stop="uiStore.togglePinTab(tab.id)"
              :title="tab.isPinned ? 'Pinned (saved across page refresh). Click to unpin' : 'Pin tab (keep after page refresh)'"
            >
              <Icon :name="tab.isPinned ? 'pin-filled' : 'pin'" :size="11" />
            </button>

            <!-- Cross / Close Button (shown only when unpinned, matching 'on unpin it can be removed') -->
            <button
              v-if="!tab.isPinned && tab.closable"
              class="tab-action-btn tab-close-btn"
              @click.stop="uiStore.closeTab(tab.id)"
              title="Close tab"
            >
              <Icon name="close" :size="10" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Middle Workspace Viewport Body -->
    <div class="viewport-body">
      <!-- 1. Admin Submenu Views (Schema, Examples, Logs, Guardrails, Models) -->
      <AdminView v-if="uiStore.activeNav.startsWith('admin')" />

      <!-- 2. Detailed In-Depth Query Analysis View -->
      <QueryAnalysisView v-else-if="uiStore.activeNav === 'query-analysis' || uiStore.activeTabId === 'query-analysis' || uiStore.activeNav === 'query-results'" />

      <!-- 3. About SubscriptIQ Platform & FAQ View -->
      <AboutView v-else-if="uiStore.activeNav === 'about' || uiStore.activeTabId === 'about'" />

      <!-- 4. Default / Dashboard View (Always available on dashboard tab) -->
      <DashboardView v-else />
    </div>
  </main>
</template>

<script setup>
import { useUIStore } from '@/stores/ui'
import DashboardView from '@/components/views/DashboardView.vue'
import AdminView from '@/components/views/AdminView.vue'
import QueryAnalysisView from '@/components/views/QueryAnalysisView.vue'
import AboutView from '@/components/views/AboutView.vue'
import Icon from '@/components/common/Icon.vue'

const uiStore = useUIStore()

function cleanTabName(name) {
  if (!name) return ''
  return String(name).replace(/\.(vue|sql|qdrant|audit|rules|json|ts|js|py)$/i, '')
}
</script>

<style scoped>
.app-main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-app);
  min-width: 0;
  overflow: hidden;
}

/* Code-Editor Style Tab Bar */
.editor-tabs-bar {
  height: 36px;
  background-color: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  padding: 0 8px;
  user-select: none;
  overflow-x: auto;
  overflow-y: hidden;
  flex-shrink: 0;
}

.tabs-scroll-area {
  display: flex;
  align-items: center;
  gap: 2px;
  height: 100%;
}

.editor-tab {
  height: 100%;
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 0 12px;
  font-size: 12px;
  color: var(--text-muted);
  background-color: transparent;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
  position: relative;
}

.editor-tab:hover {
  color: var(--text-primary);
  background-color: var(--bg-hover);
}

.editor-tab.is-active {
  color: var(--accent);
  background-color: var(--bg-app);
  border-bottom-color: var(--accent);
  font-weight: 500;
}

.tab-icon {
  display: flex;
  align-items: center;
  color: inherit;
}

.tab-name {
  max-width: 220px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.editor-tab.is-pinned {
  border-left: 1px solid rgba(14, 165, 233, 0.25);
}

.editor-tab.is-pinned .tab-icon {
  color: var(--accent);
}

.tab-actions {
  display: flex;
  align-items: center;
  gap: 3px;
  margin-left: 4px;
}

.tab-action-btn {
  width: 17px;
  height: 17px;
  border-radius: 4px;
  background: transparent;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
  color: var(--text-muted);
}

.tab-pin-btn {
  opacity: 0;
}

.editor-tab:hover .tab-pin-btn,
.editor-tab.is-active .tab-pin-btn {
  opacity: 0.65;
}

.tab-pin-btn:hover {
  opacity: 1 !important;
  color: var(--accent);
  background-color: var(--bg-hover);
  transform: scale(1.08);
}

.tab-pin-btn.is-pinned {
  opacity: 1 !important;
  color: var(--accent);
  background-color: rgba(14, 165, 233, 0.12);
}

.tab-pin-btn.is-pinned:hover {
  background-color: rgba(14, 165, 233, 0.22);
}

.tab-close-btn {
  opacity: 0.7;
}

.editor-tab:hover .tab-close-btn {
  opacity: 1;
}

.tab-close-btn:hover {
  background-color: rgba(239, 68, 68, 0.15);
  color: var(--danger);
  transform: scale(1.08);
}

.viewport-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
}
</style>
