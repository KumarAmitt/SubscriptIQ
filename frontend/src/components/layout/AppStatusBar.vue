<template>
  <footer class="app-statusbar">
    <!-- Left Section -->
    <div class="statusbar-left">
      <div class="status-item branch-item">
        <Icon name="code" :size="12" />
        <span>main*</span>
      </div>

      <div class="status-item ai-status">
        <span class="engine-dot"></span>
        <span>AI Engine: Online (24ms)</span>
      </div>

      <div class="status-item sync-status">
        <span>Telemetry Synced</span>
      </div>
    </div>

    <!-- Right Section -->
    <div class="statusbar-right">
      <div class="status-item role-item">
        <span>Role: <strong>{{ authStore.user.role.toUpperCase() }}</strong></span>
      </div>

      <div class="status-item">
        <span>UTF-8</span>
      </div>

      <div class="status-item">
        <span>Vue 3.5</span>
      </div>

      <button class="status-item toggle-chat-btn" @click="uiStore.toggleChat">
        <Icon name="chat-toggle" :size="11" />
        <span>{{ uiStore.isChatCollapsed ? 'Show Copilot' : 'Hide Copilot' }}</span>
      </button>
    </div>
  </footer>
</template>

<script setup>
import { useUIStore } from '@/stores/ui'
import { useAuthStore } from '@/stores/auth'
import Icon from '@/components/common/Icon.vue'

const uiStore = useUIStore()
const authStore = useAuthStore()
</script>

<style scoped>
.app-statusbar {
  height: var(--statusbar-height);
  background-color: var(--bg-tertiary);
  border-top: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 10px;
  font-size: 11px;
  font-family: var(--font-mono);
  color: var(--text-muted);
  user-select: none;
  z-index: 20;
}

.statusbar-left,
.statusbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.branch-item {
  color: var(--text-secondary);
}

.engine-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background-color: var(--success);
  box-shadow: 0 0 5px var(--success);
}

.ai-status {
  color: var(--text-secondary);
}

.role-item strong {
  color: var(--accent);
}

.toggle-chat-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.toggle-chat-btn:hover {
  background-color: var(--bg-hover);
  color: var(--text-primary);
}
</style>
