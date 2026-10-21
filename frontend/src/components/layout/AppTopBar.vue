<template>
  <header class="app-topbar">
    <!-- Left Section: App Logo & Sidebar Toggle -->
    <div class="topbar-left">
      <div
        class="topbar-brand"
        @click="uiStore.setActiveNav('dashboard')"
        title="SubscriptIQ - AI Subscription Intelligence"
      >
        <div class="brand-logo-wrap">
          <svg class="brand-logo-svg" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="brandGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#38bdf8" />
                <stop offset="50%" stop-color="#0284c7" />
                <stop offset="100%" stop-color="#0369a1" />
              </linearGradient>
              <linearGradient id="sparkGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#38bdf8" />
                <stop offset="100%" stop-color="#2dd4bf" />
              </linearGradient>
              <filter id="logoGlow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="1.2" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
            </defs>
            <!-- Sleek squircle base with inner glass border -->
            <rect x="2" y="2" width="28" height="28" rx="8" fill="url(#brandGrad)" />
            <rect x="2.6" y="2.6" width="26.8" height="26.8" rx="7.4" stroke="rgba(255,255,255,0.25)" stroke-width="0.8" />
            <!-- Continuous intelligence loop / subscription arc -->
            <path d="M10 16.5C10 13.186 12.686 10.5 16 10.5C19.314 10.5 22 13.186 22 16.5C22 19.814 19.314 22.5 16 22.5" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" />
            <!-- Center neural intelligence beacon -->
            <circle cx="16" cy="16.5" r="2.2" fill="#38bdf8" filter="url(#logoGlow)" />
            <!-- Dynamic AI growth spark vector -->
            <path d="M19 8.5H23.5V13" stroke="url(#sparkGrad)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
            <path d="M23.5 8.5L16.5 15.5" stroke="url(#sparkGrad)" stroke-width="1.8" stroke-linecap="round" />
          </svg>
        </div>
        <div class="brand-text">
          <span class="brand-name">Subscript<span class="brand-highlight">IQ</span></span>
          <span class="brand-badge">
            <span class="badge-sparkle">✦</span>
            <span>AI Powered</span>
          </span>
        </div>
      </div>

      <button
        class="icon-btn sidebar-toggle-btn"
        @click="uiStore.toggleSidebar"
        :title="uiStore.isSidebarCollapsed ? 'Expand Side Menu (Ctrl+B)' : 'Collapse Side Menu (Ctrl+B)'"
      >
        <Icon name="sidebar-toggle" :size="15" />
      </button>
    </div>

    <!-- Right Section: Role Switcher, Theme & Copilot Toggle -->
    <div class="topbar-right">
      <!-- Role & Authentication Badge Button -->
      <button
        class="role-badge-btn"
        :class="{ 'is-admin': authStore.isAdmin }"
        @click="handleRoleAction"
        :title="authStore.isAdmin ? 'Logged in as Administrator (Click to Log Out)' : 'Standard User (Click to Sign In as Admin)'"
      >
        <span class="role-indicator"></span>
        <span class="role-label">{{ authStore.isAdmin ? 'Role: Admin' : 'Role: User' }}</span>
        <span class="role-switch-tip">{{ authStore.isAdmin ? 'logout' : 'login' }}</span>
      </button>

      <!-- About Platform Button -->
      <button
        class="icon-btn about-btn"
        :class="{ 'active': uiStore.activeNav === 'about' || uiStore.activeTabId === 'about' }"
        @click="uiStore.setActiveNav('about', 'About SubscriptIQ')"
        title="About SubscriptIQ Platform &amp; FAQ"
      >
        <Icon name="info" :size="15" />
      </button>

      <!-- Theme Switcher -->
      <button
        class="icon-btn theme-toggle-btn"
        @click="uiStore.toggleTheme"
        :title="`Switch to ${uiStore.theme === 'dark' ? 'Light' : 'Dark'} mode`"
      >
        <Icon :name="uiStore.theme === 'dark' ? 'sun' : 'moon'" :size="15" />
      </button>

      <!-- CHAT Panel Toggle -->
      <button
        class="copilot-toggle-btn"
        :class="{ 'active': !uiStore.isChatCollapsed }"
        @click="uiStore.toggleChat"
        :title="uiStore.isChatCollapsed ? 'Open CHAT (Ctrl+J)' : 'Collapse CHAT'"
      >
        <Icon name="sparkles" :size="14" class="sparkle-icon" />
        <span class="copilot-label">CHAT</span>
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

function handleRoleAction() {
  if (authStore.isAdmin) {
    authStore.logout()
    if (uiStore.activeNav && uiStore.activeNav.startsWith('admin')) {
      uiStore.setActiveNav('dashboard')
    }
  } else {
    authStore.openLoginModal()
  }
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

.brand-logo-wrap {
  width: 25px;
  height: 25px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: transform var(--transition-fast);
}

.topbar-brand:hover .brand-logo-wrap {
  transform: scale(1.06);
}

.brand-logo-svg {
  width: 100%;
  height: 100%;
  display: block;
  filter: drop-shadow(0 2px 6px rgba(56, 189, 248, 0.4));
}

.brand-text {
  display: flex;
  align-items: center;
  gap: 7px;
  white-space: nowrap;
}

.brand-name {
  font-size: var(--text-sm);
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text-primary);
}

.brand-highlight {
  color: var(--accent);
}

.brand-badge {
  font-size: 9.5px;
  font-family: var(--font-sans);
  font-weight: 600;
  background: var(--accent-light);
  color: var(--accent);
  padding: 1.5px 7px;
  border-radius: 9999px;
  border: 1px solid rgba(var(--accent-rgb), 0.3);
  display: inline-flex;
  align-items: center;
  gap: 3.5px;
  letter-spacing: 0.2px;
}

.badge-sparkle {
  font-size: 8px;
  color: var(--accent);
  animation: pulse-sparkle 2.5s infinite ease-in-out;
}

@keyframes pulse-sparkle {
  0%, 100% { opacity: 0.6; transform: scale(0.9); }
  50% { opacity: 1; transform: scale(1.25); }
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
