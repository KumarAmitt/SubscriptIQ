<template>
  <header class="app-topbar">
    <!-- Left Section: App Logo & Workspace Path -->
    <div class="topbar-left">
      <div
        class="topbar-brand"
        @click="uiStore.setActiveNav('dashboard', 'Dashboard.vue')"
        title="SubscriptIQ - AI Intelligence"
      >
        <div class="brand-logo">
          <span class="logo-glyph">IQ</span>
          <span class="ai-dot"></span>
        </div>
        <div class="brand-text">
          <span class="brand-name">Subscript<span class="brand-highlight">IQ</span></span>
          <span class="brand-badge">AI</span>
        </div>
      </div>

      <button
        class="icon-btn sidebar-toggle-btn"
        @click="uiStore.toggleSidebar"
        :title="uiStore.isSidebarCollapsed ? 'Expand Side Menu (Ctrl+B)' : 'Collapse Side Menu (Ctrl+B)'"
      >
        <Icon name="sidebar-toggle" :size="15" />
      </button>

      <div class="breadcrumb-container">
        <span class="workspace-label">workspace</span>
        <span class="slash">/</span>
        <span class="current-path">subscriptiq.ai</span>
      </div>
    </div>

    <!-- Center Section: Command Palette / Search -->
    <div class="topbar-center">
      <div class="command-search-bar" @click="focusSearch">
        <Icon name="search" :size="13" class="search-icon" />
        <span class="search-placeholder">Search subscriptions, contracts, AI prompts...</span>
        <div class="search-shortcuts">
          <kbd>Ctrl</kbd>
          <kbd>K</kbd>
        </div>
      </div>
    </div>

    <!-- Right Section: Role Switcher, Theme & Copilot Toggle -->
    <div class="topbar-right">
      <!-- Role Toggle Pill (Allows testing admin permissions on the fly) -->
      <button
        class="role-badge-btn"
        :class="{ 'is-admin': authStore.isAdmin }"
        @click="authStore.toggleRole"
        :title="`Current Role: ${authStore.user.role.toUpperCase()} (Click to toggle role)`"
      >
        <span class="role-indicator"></span>
        <span class="role-label">{{ authStore.isAdmin ? 'Role: Admin' : 'Role: User' }}</span>
        <span class="role-switch-tip">toggle</span>
      </button>

      <!-- Theme Switcher -->
      <button
        class="icon-btn theme-toggle-btn"
        @click="uiStore.toggleTheme"
        :title="`Switch to ${uiStore.theme === 'dark' ? 'Light' : 'Dark'} mode`"
      >
        <Icon :name="uiStore.theme === 'dark' ? 'sun' : 'moon'" :size="15" />
      </button>

      <!-- AI Copilot Panel Toggle -->
      <button
        class="copilot-toggle-btn"
        :class="{ 'active': !uiStore.isChatCollapsed }"
        @click="uiStore.toggleChat"
        :title="uiStore.isChatCollapsed ? 'Open AI Agent (Ctrl+J)' : 'Collapse AI Agent'"
      >
        <Icon name="sparkles" :size="14" class="sparkle-icon" />
        <span class="copilot-label">AI Copilot</span>
        <span class="status-pulse"></span>
      </button>
    </div>
  </header>
</template>

<script setup>
import { useUIStore } from '@/stores/ui'
import { useAuthStore } from '@/stores/auth'
import Icon from '@/components/common/Icon.vue'

const uiStore = useUIStore()
const authStore = useAuthStore()

function focusSearch() {
  uiStore.setActiveNav('dashboard')
}
</script>

<style scoped>
.app-topbar {
  height: var(--topbar-height);
  background-color: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 14px;
  user-select: none;
  z-index: 20;
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

/* Left Section */
.topbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.topbar-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  transition: background-color var(--transition-fast);
}

.topbar-brand:hover {
  background-color: var(--bg-hover);
}

.brand-logo {
  width: 24px;
  height: 24px;
  border-radius: var(--radius-sm);
  background: var(--accent-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  box-shadow: var(--accent-glow);
  flex-shrink: 0;
}

.logo-glyph {
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: -0.05em;
}

.ai-dot {
  position: absolute;
  top: -2px;
  right: -2px;
  width: 5px;
  height: 5px;
  background-color: var(--info);
  border-radius: 50%;
  border: 1px solid var(--bg-secondary);
}

.brand-text {
  display: flex;
  align-items: center;
  gap: 5px;
  white-space: nowrap;
}

.brand-name {
  font-size: var(--text-sm);
  font-weight: var(--font-weight-semibold);
  letter-spacing: -0.02em;
  color: var(--text-primary);
}

.brand-highlight {
  color: var(--accent);
}

.brand-badge {
  font-size: 9px;
  font-family: var(--font-mono);
  font-weight: var(--font-weight-medium);
  background: var(--accent-light);
  color: var(--accent);
  padding: 1px 4px;
  border-radius: 3px;
  border: 1px solid rgba(99, 102, 241, 0.2);
}

.icon-btn {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-btn:hover {
  background-color: var(--bg-hover);
  color: var(--text-primary);
}

.breadcrumb-container {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: var(--text-xs);
  color: var(--text-muted);
  font-family: var(--font-mono);
}

.slash {
  opacity: 0.4;
}

.current-path {
  color: var(--text-secondary);
}

/* Center Section */
.topbar-center {
  flex: 2;
  display: flex;
  justify-content: center;
  max-width: 440px;
}

.command-search-bar {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 4px 10px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.command-search-bar:hover {
  border-color: var(--border-highlight);
  background-color: var(--bg-card);
}

.search-icon {
  color: var(--text-muted);
}

.search-placeholder {
  font-size: var(--text-xs);
  color: var(--text-muted);
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.search-shortcuts {
  display: flex;
  gap: 3px;
}

kbd {
  font-family: var(--font-mono);
  font-size: 10px;
  padding: 1px 4px;
  border-radius: 3px;
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-muted);
}

/* Right Section */
.topbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  justify-content: flex-end;
}

.role-badge-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  padding: 3px 9px;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--font-weight-medium);
  transition: all var(--transition-fast);
}

.role-badge-btn:hover {
  border-color: var(--accent);
}

.role-indicator {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: var(--text-muted);
}

.role-badge-btn.is-admin .role-indicator {
  background-color: var(--success);
  box-shadow: 0 0 6px var(--success);
}

.role-badge-btn.is-admin {
  border-color: rgba(16, 185, 129, 0.3);
}

.role-switch-tip {
  font-size: 9px;
  text-transform: uppercase;
  color: var(--text-muted);
  background-color: var(--bg-app);
  padding: 1px 4px;
  border-radius: 3px;
  font-family: var(--font-mono);
}

.copilot-toggle-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: var(--radius-md);
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  font-size: var(--text-xs);
  font-weight: var(--font-weight-medium);
}

.copilot-toggle-btn:hover {
  background-color: var(--bg-hover);
  color: var(--text-primary);
  border-color: var(--border-highlight);
}

.copilot-toggle-btn.active {
  background: var(--accent-light);
  border-color: var(--accent);
  color: var(--text-primary);
  box-shadow: var(--accent-glow);
}

.sparkle-icon {
  color: var(--accent);
}

.status-pulse {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: var(--accent);
  box-shadow: 0 0 6px var(--accent);
  animation: pulse-glow 2s infinite;
}

@keyframes pulse-glow {
  0%, 100% { opacity: 0.6; transform: scale(0.9); }
  50% { opacity: 1; transform: scale(1.1); }
}
</style>
