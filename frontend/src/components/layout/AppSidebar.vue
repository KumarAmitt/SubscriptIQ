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

        <!-- 1. Dashboard (First Nav Item) -->
        <div class="nav-item-wrapper has-tooltip">
          <button
            class="nav-item"
            :class="{ 'active': uiStore.activeNav === 'dashboard' }"
            @click="navigate('dashboard', 'Dashboard.vue')"
          >
            <div class="icon-container">
              <Icon name="dashboard" :size="15" />
            </div>
            <span class="nav-label" v-if="!uiStore.isSidebarCollapsed">Dashboard</span>
            <span class="nav-badge" v-if="!uiStore.isSidebarCollapsed">Live</span>
          </button>
          <!-- Hover Tooltip for Collapsed Rail -->
          <div class="tooltip-box" v-if="uiStore.isSidebarCollapsed">
            <span>Dashboard</span>
            <span class="tooltip-shortcut">⌘1</span>
          </div>
        </div>

        <!-- Analytics -->
        <div class="nav-item-wrapper has-tooltip">
          <button
            class="nav-item"
            :class="{ 'active': uiStore.activeNav === 'analytics' }"
            @click="navigate('analytics', 'Analytics.ts')"
          >
            <div class="icon-container">
              <Icon name="analytics" :size="15" />
            </div>
            <span class="nav-label" v-if="!uiStore.isSidebarCollapsed">Spend Analytics</span>
          </button>
          <div class="tooltip-box" v-if="uiStore.isSidebarCollapsed">
            <span>Spend Analytics</span>
          </div>
        </div>

        <!-- AI Agents / Copilot -->
        <div class="nav-item-wrapper has-tooltip">
          <button
            class="nav-item"
            :class="{ 'active': uiStore.activeNav === 'intelligence' }"
            @click="navigate('intelligence', 'CopilotInsight.ts')"
          >
            <div class="icon-container">
              <Icon name="sparkles" :size="15" />
            </div>
            <span class="nav-label" v-if="!uiStore.isSidebarCollapsed">AI Intelligence</span>
            <span class="nav-badge ai" v-if="!uiStore.isSidebarCollapsed">PRO</span>
          </button>
          <div class="tooltip-box" v-if="uiStore.isSidebarCollapsed">
            <span>AI Intelligence</span>
          </div>
        </div>
      </nav>

      <!-- 2. Admin Section (Visible ONLY when user has Admin role) -->
      <transition name="fade-slide">
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

          <!-- Admin Submenus -->
          <div
            class="admin-submenus"
            v-show="!uiStore.isSidebarCollapsed ? isAdminMenuOpen : true"
          >
            <!-- Submenu 1: Users & Access -->
            <div class="nav-item-wrapper has-tooltip">
              <button
                class="nav-item sub-item"
                :class="{ 'active': uiStore.activeNav === 'admin-users' }"
                @click="navigate('admin-users', 'AdminUsers.vue')"
              >
                <div class="icon-container">
                  <Icon name="users" :size="14" />
                </div>
                <span class="nav-label" v-if="!uiStore.isSidebarCollapsed">Users & Access</span>
              </button>
              <div class="tooltip-box" v-if="uiStore.isSidebarCollapsed">
                <span>Admin: Users & Access</span>
              </div>
            </div>

            <!-- Submenu 2: Subscriptions -->
            <div class="nav-item-wrapper has-tooltip">
              <button
                class="nav-item sub-item"
                :class="{ 'active': uiStore.activeNav === 'admin-subscriptions' }"
                @click="navigate('admin-subscriptions', 'AdminSubscriptions.vue')"
              >
                <div class="icon-container">
                  <Icon name="subscriptions" :size="14" />
                </div>
                <span class="nav-label" v-if="!uiStore.isSidebarCollapsed">All Subscriptions</span>
              </button>
              <div class="tooltip-box" v-if="uiStore.isSidebarCollapsed">
                <span>Admin: All Subscriptions</span>
              </div>
            </div>

            <!-- Submenu 3: AI Models & Limits -->
            <div class="nav-item-wrapper has-tooltip">
              <button
                class="nav-item sub-item"
                :class="{ 'active': uiStore.activeNav === 'admin-models' }"
                @click="navigate('admin-models', 'AdminModels.config.json')"
              >
                <div class="icon-container">
                  <Icon name="models" :size="14" />
                </div>
                <span class="nav-label" v-if="!uiStore.isSidebarCollapsed">AI Models & Quotas</span>
              </button>
              <div class="tooltip-box" v-if="uiStore.isSidebarCollapsed">
                <span>Admin: AI Models & Quotas</span>
              </div>
            </div>

            <!-- Submenu 4: System Settings -->
            <div class="nav-item-wrapper has-tooltip">
              <button
                class="nav-item sub-item"
                :class="{ 'active': uiStore.activeNav === 'admin-settings' }"
                @click="navigate('admin-settings', 'SystemSettings.env')"
              >
                <div class="icon-container">
                  <Icon name="settings" :size="14" />
                </div>
                <span class="nav-label" v-if="!uiStore.isSidebarCollapsed">System Settings</span>
              </button>
              <div class="tooltip-box" v-if="uiStore.isSidebarCollapsed">
                <span>Admin: System Settings</span>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </div>

    <!-- Sidebar Footer / User Profile -->
    <div class="sidebar-footer">
      <div class="user-profile-card" :class="{ 'compact': uiStore.isSidebarCollapsed }">
        <div class="user-avatar" :title="authStore.user.name">
          {{ authStore.user.avatar }}
          <span class="status-dot"></span>
        </div>
        <div class="user-meta" v-if="!uiStore.isSidebarCollapsed">
          <div class="user-name">{{ authStore.user.name }}</div>
          <div class="user-role-text">
            {{ authStore.isAdmin ? 'Admin' : 'Standard User' }}
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
import Icon from '@/components/common/Icon.vue'

const uiStore = useUIStore()
const authStore = useAuthStore()

const isAdminMenuOpen = ref(true)

function navigate(navId, tabName) {
  uiStore.setActiveNav(navId, tabName)
}

function handleBrandClick() {
  if (uiStore.isSidebarCollapsed) {
    uiStore.toggleSidebar()
  } else {
    navigate('dashboard', 'Dashboard.vue')
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
</style>
