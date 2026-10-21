<template>
  <footer class="app-statusbar font-mono">
    <!-- Left Section: System Status -->
    <div class="statusbar-left">
      <div class="status-item" title="All analytics services and database connections are healthy">
        <span class="engine-dot"></span>
        <span>System Operational</span>
      </div>
    </div>

    <!-- Center Section: Copyright Notice -->
    <div class="statusbar-center">
      <span class="copyright-text">© 2026 SubscriptIQ AI. All rights reserved.</span>
    </div>

    <!-- Right Section: Current Context & Quick Toggle -->
    <div class="statusbar-right">
      <div class="status-item">
        <span>Active Model: <strong>{{ activeModelShort }}</strong></span>
      </div>

      <div class="status-item">
        <span>Role: <strong :class="{ 'admin-text': authStore.isAdmin }">{{ authStore.user.role.toUpperCase() }}</strong></span>
      </div>

      <button class="status-item toggle-chat-btn" @click="uiStore.toggleChat">
        <Icon name="sparkles" :size="11" />
        <span>{{ uiStore.isChatCollapsed ? 'Open Assistant' : 'Hide Assistant' }}</span>
      </button>
    </div>
  </footer>
</template>

<script setup>
import { computed } from 'vue'
import { useUIStore } from '@/stores/ui'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import Icon from '@/components/common/Icon.vue'

const uiStore = useUIStore()
const authStore = useAuthStore()
const chatStore = useChatStore()

const activeModelShort = computed(() => {
  const m = chatStore.models.find(x => x.id === chatStore.selectedModel)
  return m ? m.name : chatStore.selectedModel
})
</script>

<style scoped>
.app-statusbar {
  height: var(--statusbar-height);
  background-color: var(--bg-secondary);
  border-top: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 12px;
  font-size: 11px;
  color: var(--text-muted);
  user-select: none;
  z-index: 20;
  position: relative;
}

.statusbar-left,
.statusbar-right {
  display: flex;
  align-items: center;
  gap: 14px;
}

/* Centered Copyright Notice */
.statusbar-center {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  color: var(--text-muted);
  font-size: 11px;
  white-space: nowrap;
  pointer-events: none;
  opacity: 0.85;
}

.copyright-text {
  letter-spacing: 0.02em;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.engine-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: var(--success);
  box-shadow: 0 0 6px var(--success);
}

.admin-text {
  color: var(--accent);
}

.toggle-chat-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.toggle-chat-btn:hover {
  background-color: var(--bg-hover);
  color: var(--text-primary);
}
</style>
