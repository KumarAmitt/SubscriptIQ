<template>
  <div class="toast-stack-container" aria-live="polite" aria-atomic="true">
    <TransitionGroup name="toast-slide">
      <div
        v-for="toast in uiStore.toasts"
        :key="toast.id"
        class="toast-item font-sans"
        :class="toast.type"
      >
        <div class="toast-icon-wrap" :class="toast.type">
          <Icon :name="getToastIcon(toast.type)" :size="15" />
        </div>

        <div class="toast-content">
          <span class="toast-message">{{ toast.message }}</span>
        </div>

        <button
          class="toast-close-btn"
          @click="uiStore.removeToast(toast.id)"
          title="Dismiss notification"
          aria-label="Dismiss"
        >
          ✕
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { useUIStore } from '@/stores/ui'
import Icon from '@/components/common/Icon.vue'

const uiStore = useUIStore()

function getToastIcon(type) {
  switch (type) {
    case 'error':
    case 'danger':
      return 'alert-triangle'
    case 'warning':
      return 'warning'
    case 'info':
      return 'info'
    case 'success':
    default:
      return 'check-circle'
  }
}
</script>

<style scoped>
.toast-stack-container {
  position: fixed;
  top: 54px;
  right: 20px;
  z-index: 10000;
  display: flex;
  flex-direction: column;
  gap: 8px;
  pointer-events: none;
  max-width: 380px;
  width: calc(100vw - 40px);
}

.toast-item {
  pointer-events: auto;
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 10px 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.4), 0 0 1px 1px rgba(255, 255, 255, 0.05);
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.toast-item.success {
  border-left: 3px solid #10b981;
}

.toast-item.error,
.toast-item.danger {
  border-left: 3px solid #ef4444;
}

.toast-item.warning {
  border-left: 3px solid #f59e0b;
}

.toast-item.info {
  border-left: 3px solid #0284c7;
}

.toast-icon-wrap {
  width: 26px;
  height: 26px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.toast-icon-wrap.success {
  background: rgba(16, 185, 129, 0.12);
  color: #10b981;
}

.toast-icon-wrap.error,
.toast-icon-wrap.danger {
  background: rgba(239, 68, 68, 0.12);
  color: #ef4444;
}

.toast-icon-wrap.warning {
  background: rgba(245, 158, 11, 0.12);
  color: #f59e0b;
}

.toast-icon-wrap.info {
  background: rgba(2, 132, 199, 0.12);
  color: #0284c7;
}

.toast-content {
  flex: 1;
}

.toast-message {
  font-size: 12.5px;
  font-weight: 500;
  color: var(--text-primary);
  line-height: 1.4;
}

.toast-close-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 3px 5px;
  font-size: 11px;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
  line-height: 1;
}

.toast-close-btn:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

/* Animations */
.toast-slide-enter-active {
  animation: toastIn 0.25s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.toast-slide-leave-active {
  animation: toastOut 0.2s cubic-bezier(0.4, 0, 1, 1) forwards;
}

@keyframes toastIn {
  from {
    opacity: 0;
    transform: translateX(40px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateX(0) scale(1);
  }
}

@keyframes toastOut {
  from {
    opacity: 1;
    transform: translateX(0) scale(1);
  }
  to {
    opacity: 0;
    transform: translateX(30px) scale(0.9);
  }
}

/* Light Mode Overrides */
[data-theme="light"] .toast-item {
  background-color: #ffffff;
  border-color: #e2e8f0;
  box-shadow: 0 10px 25px -4px rgba(15, 23, 42, 0.1), 0 0 1px 1px rgba(0, 0, 0, 0.05);
}

[data-theme="light"] .toast-message {
  color: #0f172a;
}
</style>
