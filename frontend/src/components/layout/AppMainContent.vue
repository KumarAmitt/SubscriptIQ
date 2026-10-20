<template>
  <main class="app-main-content">
    <!-- Editor Tabs Bar -->
    <div class="tabs-bar">
      <div class="tabs-scroll">
        <div
          v-for="tab in uiStore.tabs"
          :key="tab.id"
          class="editor-tab"
          :class="{ 'active': uiStore.activeTabId === tab.id }"
          @click="uiStore.activateTab(tab)"
        >
          <Icon :name="tab.icon" :size="13" class="tab-icon" />
          <span class="tab-title font-mono">{{ tab.name }}</span>
          <button
            v-if="tab.closable"
            class="tab-close-btn"
            @click.stop="uiStore.closeTab(tab.id)"
            title="Close tab"
          >
            <Icon name="close" :size="10" />
          </button>
        </div>
      </div>

      <div class="tabs-right-actions">
        <span class="view-indicator font-mono">IDE Editor Mode</span>
      </div>
    </div>

    <!-- Breadcrumb Path Bar -->
    <div class="editor-breadcrumb">
      <div class="breadcrumb-trail font-mono">
        <span class="crumb-root">SubscriptIQ</span>
        <span class="crumb-separator">&gt;</span>
        <span class="crumb-folder">views</span>
        <span class="crumb-separator">&gt;</span>
        <span class="crumb-file">{{ activeFileName }}</span>
      </div>
    </div>

    <!-- Dynamic Viewport Body -->
    <div class="viewport-body">
      <!-- Admin Submenu Views -->
      <AdminView v-if="uiStore.activeNav.startsWith('admin')" />

      <!-- Default / Dashboard View -->
      <DashboardView v-else />
    </div>
  </main>
</template>

<script setup>
import { computed } from 'vue'
import { useUIStore } from '@/stores/ui'
import Icon from '@/components/common/Icon.vue'
import DashboardView from '@/components/views/DashboardView.vue'
import AdminView from '@/components/views/AdminView.vue'

const uiStore = useUIStore()

const activeFileName = computed(() => {
  const current = uiStore.tabs.find((t) => t.id === uiStore.activeTabId)
  return current ? current.name : 'Dashboard.vue'
})
</script>

<style scoped>
.app-main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-app);
  min-width: 0; /* Crucial for inner scrolling and flex shrinkage */
  overflow: hidden;
}

/* Tabs Bar */
.tabs-bar {
  height: 36px;
  background-color: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 4px;
  user-select: none;
  overflow: hidden;
}

.tabs-scroll {
  display: flex;
  height: 100%;
  overflow-x: auto;
  align-items: flex-end;
}

.editor-tab {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 0 12px;
  height: 32px;
  background-color: var(--bg-tertiary);
  border-right: 1px solid var(--border-color);
  border-top: 2px solid transparent;
  color: var(--text-muted);
  font-size: 11.5px;
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.editor-tab:hover {
  background-color: var(--bg-card);
  color: var(--text-secondary);
}

.editor-tab.active {
  background-color: var(--bg-app);
  border-top-color: var(--accent);
  color: var(--text-primary);
  font-weight: var(--font-weight-medium);
}

.tab-icon {
  opacity: 0.8;
}

.editor-tab.active .tab-icon {
  color: var(--accent);
  opacity: 1;
}

.tab-title {
  letter-spacing: -0.01em;
}

.tab-close-btn {
  width: 16px;
  height: 16px;
  border-radius: 2px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  margin-left: 2px;
}

.tab-close-btn:hover {
  background-color: var(--bg-hover);
  color: var(--text-primary);
}

.tabs-right-actions {
  padding-right: 8px;
}

.view-indicator {
  font-size: 10px;
  color: var(--text-muted);
  opacity: 0.7;
}

/* Breadcrumb Bar */
.editor-breadcrumb {
  height: 24px;
  background-color: var(--bg-primary);
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  padding: 0 16px;
  font-size: 11px;
}

.breadcrumb-trail {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-muted);
}

.crumb-separator {
  opacity: 0.4;
}

.crumb-file {
  color: var(--text-secondary);
  font-weight: var(--font-weight-medium);
}

/* Viewport Body */
.viewport-body {
  flex: 1;
  overflow-y: auto;
  padding: 18px 24px 30px 24px;
}
</style>
