<template>
  <aside
    class="app-sidebar"
    :class="{ 'is-collapsed': uiStore.isSidebarCollapsed }"
  >
    <!-- Navigation List -->
    <div class="sidebar-nav-container">
      <nav class="nav-section">
        <div class="section-label" v-if="!uiStore.isSidebarCollapsed">
          <span>WORKSPACE</span>
        </div>

        <!-- 1. Dashboard (Main Overview & Text-to-SQL Interface) -->
        <div class="nav-item-wrapper has-tooltip">
          <button
            class="nav-item"
            :class="{ 'active': uiStore.activeNav === 'dashboard' }"
            @click="navigate('dashboard')"
          >
            <div class="icon-container">
              <Icon name="dashboard" :size="15" />
            </div>
            <span class="nav-label" v-if="!uiStore.isSidebarCollapsed">Dashboard</span>
            <span class="nav-badge" v-if="!uiStore.isSidebarCollapsed">Live</span>
          </button>
          <div class="tooltip-box" v-if="uiStore.isSidebarCollapsed">
            <span>Dashboard</span>
          </div>
        </div>

        <!-- 2. Chat Analysis (In-Depth Analysis & Full Dataset) -->
        <div class="nav-item-wrapper has-tooltip">
          <button
            class="nav-item"
            :class="{ 'active': uiStore.activeNav === 'query-analysis' || uiStore.activeTabId === 'query-analysis' }"
            @click="navigate('query-analysis', 'Chat Analysis')"
          >
            <div class="icon-container">
              <Icon name="analytics" :size="15" />
            </div>
            <span class="nav-label" v-if="!uiStore.isSidebarCollapsed">Chat Analysis</span>
            <span
              class="nav-badge count-badge"
              v-if="!uiStore.isSidebarCollapsed && chatStore.activeQueryResult"
            >
              {{ chatStore.activeQueryResult.rowCount }} {{ chatStore.activeQueryResult.rowCount === 1 ? 'row' : 'rows' }}
            </span>
          </button>
          <div class="tooltip-box" v-if="uiStore.isSidebarCollapsed">
            <span>Chat Analysis</span>
          </div>
        </div>

        <!-- 3. About SubscriptIQ (Features, Benefits & FAQ) -->
        <div class="nav-item-wrapper has-tooltip">
          <button
            class="nav-item"
            :class="{ 'active': uiStore.activeNav === 'about' || uiStore.activeTabId === 'about' }"
            @click="navigate('about', 'About SubscriptIQ')"
          >
            <div class="icon-container">
              <Icon name="info" :size="15" />
            </div>
            <span class="nav-label" v-if="!uiStore.isSidebarCollapsed">About Platform</span>
            <span class="nav-badge info-badge" v-if="!uiStore.isSidebarCollapsed">FAQ</span>
          </button>
          <div class="tooltip-box" v-if="uiStore.isSidebarCollapsed">
            <span>About SubscriptIQ &amp; FAQ</span>
          </div>
        </div>
      </nav>

      <!-- 2. Admin Section -->
      <div v-if="authStore.isAdmin" class="admin-group">
        <div class="nav-divider" v-if="!uiStore.isSidebarCollapsed"></div>

        <div
          class="section-label admin-header"
          v-if="!uiStore.isSidebarCollapsed"
          @click="isAdminMenuOpen = !isAdminMenuOpen"
        >
          <div class="admin-tag">
            <Icon name="shield" :size="12" class="shield-icon" />
            <span>ADMIN PORTAL</span>
          </div>
          <Icon
            :name="isAdminMenuOpen ? 'chevron-down' : 'chevron-right'"
            :size="12"
            class="accordion-arrow"
          />
        </div>

        <!-- Admin Submenus: 5 Core Panels -->
        <div
          class="admin-submenus"
          v-show="!uiStore.isSidebarCollapsed ? isAdminMenuOpen : true"
        >
          <!-- Panel 1: Schema Manager -->
          <div class="nav-item-wrapper has-tooltip">
            <button
              class="nav-item sub-item"
              :class="{ 'active': uiStore.activeNav === 'admin-schema' }"
              @click="navigate('admin-schema', 'Schema Manager')"
            >
              <div class="icon-container">
                <Icon name="database" :size="14" />
              </div>
              <span class="nav-label" v-if="!uiStore.isSidebarCollapsed">Schema Manager</span>
            </button>
            <div class="tooltip-box" v-if="uiStore.isSidebarCollapsed">
              <span>Admin: Schema Manager</span>
            </div>
          </div>

          <!-- Panel 2: Examples Manager -->
          <div class="nav-item-wrapper has-tooltip">
            <button
              class="nav-item sub-item"
              :class="{ 'active': uiStore.activeNav === 'admin-examples' }"
              @click="navigate('admin-examples', 'Examples Manager')"
            >
              <div class="icon-container">
                <Icon name="book" :size="14" />
              </div>
              <span class="nav-label" v-if="!uiStore.isSidebarCollapsed">Examples Manager</span>
            </button>
            <div class="tooltip-box" v-if="uiStore.isSidebarCollapsed">
              <span>Admin: Examples Manager</span>
            </div>
          </div>

          <!-- Panel 3: Query Logs -->
          <div class="nav-item-wrapper has-tooltip">
            <button
              class="nav-item sub-item"
              :class="{ 'active': uiStore.activeNav === 'admin-logs' }"
              @click="navigate('admin-logs', 'Query Logs')"
            >
              <div class="icon-container">
                <Icon name="terminal" :size="14" />
              </div>
              <span class="nav-label" v-if="!uiStore.isSidebarCollapsed">Query Logs</span>
            </button>
            <div class="tooltip-box" v-if="uiStore.isSidebarCollapsed">
              <span>Admin: Query Logs</span>
            </div>
          </div>

          <!-- Panel 4: Guardrails Config -->
          <div class="nav-item-wrapper has-tooltip">
            <button
              class="nav-item sub-item"
              :class="{ 'active': uiStore.activeNav === 'admin-guardrails' }"
              @click="navigate('admin-guardrails', 'Guardrails Config')"
            >
              <div class="icon-container">
                <Icon name="lock" :size="14" />
              </div>
              <span class="nav-label" v-if="!uiStore.isSidebarCollapsed">Guardrails Config</span>
            </button>
            <div class="tooltip-box" v-if="uiStore.isSidebarCollapsed">
              <span>Admin: Guardrails Config</span>
            </div>
          </div>

          <!-- Panel 5: Model Config & Settings -->
          <div class="nav-item-wrapper has-tooltip">
            <button
              class="nav-item sub-item"
              :class="{ 'active': uiStore.activeNav === 'admin-models' }"
              @click="navigate('admin-models', 'Model Config & Settings')"
            >
              <div class="icon-container">
                <Icon name="models" :size="14" />
              </div>
              <span class="nav-label" v-if="!uiStore.isSidebarCollapsed">Model Config & Settings</span>
            </button>
            <div class="tooltip-box" v-if="uiStore.isSidebarCollapsed">
              <span>Admin: Model Config & Settings</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Locked Admin Section (Shown for non-admin users) -->
      <div v-else class="admin-locked-group">
        <div class="nav-divider" v-if="!uiStore.isSidebarCollapsed"></div>
        <div class="nav-item-wrapper has-tooltip">
          <button
            class="nav-item locked-item"
            @click="authStore.openLoginModal()"
          >
            <div class="icon-container">
              <Icon name="lock" :size="14" class="lock-icon" />
            </div>
            <span class="nav-label" v-if="!uiStore.isSidebarCollapsed">Admin Portal</span>
            <span class="nav-badge lock-badge" v-if="!uiStore.isSidebarCollapsed">Locked</span>
          </button>
          <div class="tooltip-box" v-if="uiStore.isSidebarCollapsed">
            <span>Admin Portal (Login Required)</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Sidebar Footer / User Profile -->
    <div class="sidebar-footer">
      <div
        class="user-profile-card clickable"
        :class="{ 'compact': uiStore.isSidebarCollapsed, 'is-admin': authStore.isAdmin }"
        @click="authStore.isAdmin ? authStore.logout() : authStore.openLoginModal()"
        :title="authStore.isAdmin ? 'Admin Mode (Click to Log Out)' : 'Standard User (Click to Sign In as Admin)'"
      >
        <div class="user-avatar" :title="authStore.user.name">
          {{ authStore.user.avatar }}
          <span class="status-dot"></span>
        </div>
        <div class="user-meta" v-if="!uiStore.isSidebarCollapsed">
          <div class="user-name">{{ authStore.user.name }}</div>
          <div class="user-role-text">
            {{ authStore.isAdmin ? 'Admin (click to logout)' : 'User (click to login)' }}
          </div>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref } from 'vue'
import { useUIStore } from '@/stores/ui'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import Icon from '@/components/common/Icon.vue'

const uiStore = useUIStore()
const authStore = useAuthStore()
const chatStore = useChatStore()

const isAdminMenuOpen = ref(true)

function navigate(navId, tabName) {
  if (navId.startsWith('admin') && !authStore.isAdmin) {
    authStore.openLoginModal()
    return
  }
  uiStore.setActiveNav(navId, tabName)
}

function handleBrandClick() {
  if (uiStore.isSidebarCollapsed) {
    uiStore.toggleSidebar()
  } else {
    navigate('dashboard')
  }
}
</script>

<style scoped>
.app-sidebar {
  width: var(--sidebar-expanded);
  background-color: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  transition: width var(--transition-normal);
  user-select: none;
  position: relative;
  z-index: 10;
  flex-shrink: 0;
}

.app-sidebar.is-collapsed {
  width: var(--sidebar-collapsed);
}



/* Navigation items */
.sidebar-nav-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 10px 8px;
}

.section-label {
  font-size: 10px;
  font-weight: var(--font-weight-semibold);
  letter-spacing: 0.08em;
  color: var(--text-muted);
  padding: 8px 10px 4px 10px;
  font-family: var(--font-mono);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.nav-item-wrapper {
  margin-bottom: 3px;
  position: relative;
}

.nav-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 10px;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: var(--text-sm);
  font-weight: var(--font-weight-regular);
  transition: all var(--transition-fast);
  position: relative;
}

.is-collapsed .nav-item {
  justify-content: center;
  padding: 7px 0;
}

.nav-item:hover {
  background-color: var(--bg-hover);
  color: var(--text-primary);
}

.nav-item.active {
  background-color: var(--bg-active);
  color: var(--accent);
  font-weight: var(--font-weight-medium);
}

.nav-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 15%;
  height: 70%;
  width: 3px;
  background-color: var(--accent);
  border-radius: 0 2px 2px 0;
}

.icon-container {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  flex-shrink: 0;
}

.nav-label {
  flex: 1;
  text-align: left;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  letter-spacing: -0.01em;
}

.nav-badge {
  font-size: 9px;
  padding: 1px 5px;
  border-radius: var(--radius-full);
  background-color: var(--bg-tertiary);
  color: var(--text-muted);
  font-family: var(--font-mono);
}

.nav-badge.count-badge {
  background-color: var(--accent-light);
  color: var(--accent);
  border: 1px solid rgba(56, 189, 248, 0.25);
  font-weight: 500;
}

.nav-badge.ai {
  background: var(--accent-light);
  color: var(--accent);
}

/* Admin Section */
.nav-divider {
  height: 1px;
  background-color: var(--border-subtle);
  margin: 12px 6px 8px 6px;
}

.admin-header {
  cursor: pointer;
  user-select: none;
  border-radius: var(--radius-sm);
  transition: background-color var(--transition-fast);
}

.admin-header:hover {
  background-color: var(--bg-hover);
  color: var(--text-secondary);
}

.admin-tag {
  display: flex;
  align-items: center;
  gap: 5px;
}

.shield-icon {
  color: var(--warning);
}

.sub-item {
  padding-left: 18px;
}

.is-collapsed .sub-item {
  padding-left: 0;
}

/* Tooltip shortcut */
.tooltip-shortcut {
  font-family: var(--font-mono);
  font-size: 9px;
  opacity: 0.6;
  margin-left: 6px;
}

/* Footer / User card */
.sidebar-footer {
  padding: 10px 8px;
  border-top: 1px solid var(--border-subtle);
  background-color: var(--bg-secondary);
}

.user-profile-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 8px;
  border-radius: var(--radius-md);
  transition: background-color var(--transition-fast);
}

.user-profile-card:hover {
  background-color: var(--bg-hover);
}

.user-profile-card.compact {
  justify-content: center;
  padding: 4px 0;
}

.user-avatar {
  width: 26px;
  height: 26px;
  border-radius: var(--radius-sm);
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  font-size: 10px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  font-family: var(--font-mono);
  flex-shrink: 0;
}

.status-dot {
  position: absolute;
  bottom: -1px;
  right: -1px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: var(--success);
  border: 1px solid var(--bg-secondary);
}

.user-meta {
  overflow: hidden;
  white-space: nowrap;
}

.user-name {
  font-size: var(--text-xs);
  font-weight: var(--font-weight-medium);
  color: var(--text-primary);
}

.user-role-text {
  font-size: 10px;
  color: var(--text-muted);
}

/* Animation */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: opacity var(--transition-fast), transform var(--transition-fast);
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

.user-profile-card.clickable {
  cursor: pointer;
}

.user-profile-card.clickable:hover {
  background-color: var(--bg-hover);
  border: 1px solid var(--border-color);
}

.user-profile-card.is-admin .status-dot {
  background-color: var(--accent);
}

.locked-item {
  opacity: 0.75;
  cursor: pointer;
}

.locked-item:hover {
  opacity: 1;
  background-color: var(--bg-hover);
}

.lock-icon {
  color: var(--warning);
}

.lock-badge {
  background-color: rgba(245, 158, 11, 0.15);
  color: var(--warning);
  border: 1px solid rgba(245, 158, 11, 0.3);
  font-size: 9px;
  padding: 1px 5px;
  border-radius: 3px;
  margin-left: auto;
}
</style>
