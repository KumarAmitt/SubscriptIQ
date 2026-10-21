<template>
  <Transition name="confirm-fade">
    <div
      v-if="uiStore.confirmDialog.isOpen"
      class="confirm-modal-backdrop"
      @click.self="uiStore.handleConfirmResult(false)"
      @keydown.esc="uiStore.handleConfirmResult(false)"
      tabindex="-1"
      ref="backdropRef"
    >
      <div class="confirm-modal-card font-sans" role="dialog" aria-modal="true">
        <!-- Header & Action Icon -->
        <div class="confirm-header">
          <div class="icon-beacon-wrapper" :class="uiStore.confirmDialog.type">
            <Icon :name="uiStore.confirmDialog.icon || 'alert-triangle'" :size="20" />
          </div>

          <div class="header-text-block">
            <h3 class="confirm-title">{{ uiStore.confirmDialog.title }}</h3>
            <span class="confirm-badge font-mono" :class="uiStore.confirmDialog.type">
              {{ uiStore.confirmDialog.type.toUpperCase() }} ACTION
            </span>
          </div>

          <button
            class="confirm-close-btn"
            @click="uiStore.handleConfirmResult(false)"
            title="Cancel"
            aria-label="Close dialog"
          >
            ✕
          </button>
        </div>

        <!-- Body Message & Sub-warning -->
        <div class="confirm-body">
          <p class="main-confirm-message">
            {{ uiStore.confirmDialog.message }}
          </p>

          <div v-if="uiStore.confirmDialog.subMessage" class="sub-message-callout" :class="uiStore.confirmDialog.type">
            <Icon name="info" :size="14" class="callout-icon" />
            <span class="callout-text">{{ uiStore.confirmDialog.subMessage }}</span>
          </div>
        </div>

        <!-- Actions Footer -->
        <div class="confirm-footer">
          <button
            type="button"
            class="btn-cancel font-mono"
            @click="uiStore.handleConfirmResult(false)"
          >
            {{ uiStore.confirmDialog.cancelText || 'Cancel' }}
          </button>

          <button
            type="button"
            class="btn-action font-mono"
            :class="uiStore.confirmDialog.type"
            @click="uiStore.handleConfirmResult(true)"
            ref="confirmBtnRef"
          >
            <Icon :name="uiStore.confirmDialog.icon || 'trash'" :size="14" />
            <span>{{ uiStore.confirmDialog.confirmText || 'Confirm' }}</span>
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { useUIStore } from '@/stores/ui'
import Icon from '@/components/common/Icon.vue'

const uiStore = useUIStore()
const backdropRef = ref(null)
const confirmBtnRef = ref(null)

watch(
  () => uiStore.confirmDialog.isOpen,
  (isOpen) => {
    if (isOpen) {
      nextTick(() => {
        backdropRef.value?.focus()
      })
    }
  }
)
</script>

<style scoped>
/* Backdrop & Animations */
.confirm-modal-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgba(10, 14, 20, 0.72);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 16px;
  outline: none;
}

.confirm-fade-enter-active,
.confirm-fade-leave-active {
  transition: opacity 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.confirm-fade-enter-from,
.confirm-fade-leave-to {
  opacity: 0;
}

.confirm-fade-enter-active .confirm-modal-card {
  animation: modalPopIn 0.22s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.confirm-fade-leave-active .confirm-modal-card {
  animation: modalPopOut 0.15s cubic-bezier(0.4, 0, 1, 1) forwards;
}

@keyframes modalPopIn {
  0% {
    opacity: 0;
    transform: scale(0.94) translateY(8px);
  }
  100% {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

@keyframes modalPopOut {
  0% {
    opacity: 1;
    transform: scale(1);
  }
  100% {
    opacity: 0;
    transform: scale(0.95);
  }
}

/* Card Container */
.confirm-modal-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  width: 100%;
  max-width: 460px;
  box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.5), 0 0 1px 1px rgba(255, 255, 255, 0.05);
  padding: 22px 24px;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

/* Header */
.confirm-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 16px;
}

.icon-beacon-wrapper {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.icon-beacon-wrapper.danger {
  background-color: rgba(239, 68, 68, 0.14);
  border: 1px solid rgba(239, 68, 68, 0.35);
  color: #ef4444;
}

.icon-beacon-wrapper.warning {
  background-color: rgba(245, 158, 11, 0.14);
  border: 1px solid rgba(245, 158, 11, 0.35);
  color: #f59e0b;
}

.icon-beacon-wrapper.info,
.icon-beacon-wrapper.primary {
  background-color: rgba(56, 189, 248, 0.14);
  border: 1px solid rgba(56, 189, 248, 0.35);
  color: #38bdf8;
}

.header-text-block {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.confirm-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  letter-spacing: -0.01em;
}

.confirm-badge {
  font-size: 9.5px;
  font-weight: 700;
  letter-spacing: 0.05em;
  padding: 1px 6px;
  border-radius: 3px;
  align-self: flex-start;
}

.confirm-badge.danger {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
}

.confirm-badge.warning {
  background: rgba(245, 158, 11, 0.15);
  color: #fbbf24;
}

.confirm-badge.info,
.confirm-badge.primary {
  background: rgba(56, 189, 248, 0.15);
  color: #38bdf8;
}

.confirm-close-btn {
  color: var(--text-muted);
  cursor: pointer;
  background: transparent;
  border: none;
  padding: 6px;
  font-size: 14px;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.confirm-close-btn:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

/* Body */
.confirm-body {
  margin-bottom: 22px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.main-confirm-message {
  font-size: 13.5px;
  color: var(--text-primary);
  line-height: 1.55;
  margin: 0;
}

.sub-message-callout {
  border-radius: var(--radius-sm);
  padding: 10px 12px;
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 12px;
  line-height: 1.45;
}

.sub-message-callout.danger {
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.22);
  color: #fca5a5;
}

.sub-message-callout.warning {
  background: rgba(245, 158, 11, 0.08);
  border: 1px solid rgba(245, 158, 11, 0.22);
  color: #fde68a;
}

.sub-message-callout.info,
.sub-message-callout.primary {
  background: rgba(56, 189, 248, 0.08);
  border: 1px solid rgba(56, 189, 248, 0.22);
  color: #bae6fd;
}

.callout-icon {
  flex-shrink: 0;
  margin-top: 1px;
}

.callout-text {
  flex: 1;
}

/* Actions Footer */
.confirm-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
}

.btn-cancel {
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  border-radius: var(--radius-sm);
  cursor: pointer;
  padding: 8px 16px;
  font-size: 12px;
  font-weight: 500;
  transition: all var(--transition-fast);
}

.btn-cancel:hover {
  background-color: var(--bg-hover);
  color: var(--text-primary);
  border-color: var(--border-highlight);
}

.btn-action {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 8px 18px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all var(--transition-fast);
}

.btn-action.danger {
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
  color: #ffffff;
  box-shadow: 0 2px 10px rgba(220, 38, 38, 0.35);
  border: 1px solid rgba(248, 113, 113, 0.4);
}

.btn-action.danger:hover {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  box-shadow: 0 4px 14px rgba(220, 38, 38, 0.5);
  transform: translateY(-1px);
}

.btn-action.warning {
  background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
  color: #ffffff;
  box-shadow: 0 2px 10px rgba(217, 119, 6, 0.35);
  border: 1px solid rgba(251, 191, 36, 0.4);
}

.btn-action.warning:hover {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  transform: translateY(-1px);
}

.btn-action.info,
.btn-action.primary {
  background: var(--btn-primary-gradient);
  color: #ffffff;
  box-shadow: 0 2px 10px rgba(2, 132, 199, 0.35);
  border: 1px solid var(--btn-primary-border);
}

.btn-action.info:hover,
.btn-action.primary:hover {
  background: var(--btn-primary-gradient-hover);
  transform: translateY(-1px);
}

/* Light Theme Overrides */
[data-theme="light"] .confirm-modal-backdrop {
  background-color: rgba(15, 23, 42, 0.45);
}

[data-theme="light"] .confirm-modal-card {
  background-color: #ffffff;
  border-color: #e2e8f0;
  box-shadow: 0 20px 40px -10px rgba(15, 23, 42, 0.15), 0 0 1px 1px rgba(0, 0, 0, 0.05);
}

[data-theme="light"] .confirm-title {
  color: #0f172a;
}

[data-theme="light"] .main-confirm-message {
  color: #1e293b;
}

[data-theme="light"] .sub-message-callout.danger {
  background: #fef2f2;
  border-color: #fecaca;
  color: #991b1b;
}

[data-theme="light"] .sub-message-callout.warning {
  background: #fffbeb;
  border-color: #fde68a;
  color: #92400e;
}

[data-theme="light"] .sub-message-callout.info,
[data-theme="light"] .sub-message-callout.primary {
  background: #f0f9ff;
  border-color: #bae6fd;
  color: #075985;
}

[data-theme="light"] .confirm-badge.danger {
  background: #fee2e2;
  color: #b91c1c;
}

[data-theme="light"] .confirm-badge.warning {
  background: #fef3c7;
  color: #b45309;
}

[data-theme="light"] .confirm-badge.info,
[data-theme="light"] .confirm-badge.primary {
  background: #e0f2fe;
  color: #0369a1;
}

[data-theme="light"] .btn-cancel {
  background-color: #f1f5f9;
  border-color: #cbd5e1;
  color: #334155;
}

[data-theme="light"] .btn-cancel:hover {
  background-color: #e2e8f0;
  color: #0f172a;
}
</style>
