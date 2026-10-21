<template>
  <aside
    class="chat-agent-panel"
    :class="{ 'is-collapsed': uiStore.isChatCollapsed }"
  >
    <!-- Chat Header -->
    <div class="chat-header">
      <div class="header-left">
        <div class="copilot-avatar">
          <Icon name="sparkles" :size="14" class="sparkle-icon" />
        </div>
        <div class="copilot-title-group">
          <div class="title-with-status">
            <span class="copilot-title">CHAT ASSISTANT</span>
            <!-- Live Agent Connection Status Badge -->
            <span
              class="agent-status-tag font-mono"
              :class="chatStore.isAgentConnected ? 'is-connected' : 'is-disconnected'"
              :title="chatStore.isAgentConnected ? 'AI Agent Connected (Live LLM active)' : 'AI Agent Not Connected (Running in offline fallback mode)'"
            >
              <span class="status-pulse-dot"></span>
              <span>{{ chatStore.isAgentConnected ? 'Connected' : 'Disconnected' }}</span>
            </span>
          </div>
          <span class="copilot-subtitle">SaaS Spend &amp; License Intelligence</span>
        </div>
      </div>

      <div class="header-actions">
        <button
          class="action-btn"
          @click="handleClearChat"
          title="Clear conversation"
        >
          <Icon name="trash" :size="13" />
        </button>
        <button
          class="action-btn close-btn"
          @click="uiStore.toggleChat"
          title="Collapse AI panel"
        >
          <Icon name="close" :size="13" />
        </button>
      </div>
    </div>

    <!-- Agent Not Connected Warning Banner -->
    <div v-if="!chatStore.isAgentConnected" class="agent-offline-banner font-mono">
      <div class="warning-banner-inner">
        <span class="warning-badge-icon">⚠️</span>
        <div class="warning-banner-text">
          <span class="warning-title">Agent Not Connected</span>
          <span class="warning-sub">Operating in offline mode. Responses are generated using local rules.</span>
        </div>
      </div>
    </div>

    <!-- Suggested Quick Prompts -->
    <div class="quick-prompts-bar">
      <div class="prompts-scroll">
        <button
          v-for="(prompt, index) in quickPrompts"
          :key="index"
          class="prompt-chip"
          @click="sendQuickPrompt(prompt)"
        >
          {{ prompt }}
        </button>
      </div>
    </div>

    <!-- Messages List -->
    <div class="chat-messages-container" ref="messagesContainer">
      <div
        v-for="msg in chatStore.messages"
        :key="msg.id"
        class="message-row"
        :class="msg.sender"
      >
        <div class="message-bubble" :class="{ 'error-bubble': msg.isError }">
          <div class="message-meta">
            <span class="sender-name">{{ msg.sender === 'assistant' ? 'SubscriptIQ AI' : 'You' }}</span>
            <div class="meta-right font-mono">
              <span v-if="msg.queryType" class="query-type-tag">{{ msg.queryType }}</span>
              <span v-if="msg.latency" class="latency-tag">⚡ {{ msg.latency }}ms</span>
              <span class="message-time">{{ msg.time }}</span>
            </div>
          </div>

          <!-- Natural Language Text Content -->
          <div class="message-content" v-html="formatMessage(msg.text)"></div>

          <!-- Auto-generated Chart Preview (Bonus) -->
          <div v-if="msg.chart && msg.chart.labels && msg.chart.labels.length" class="chart-preview-card">
            <div class="chart-card-header font-mono">
              <div class="chart-title-group">
                <Icon name="analytics" :size="11" />
                <span>{{ msg.chart.title }}</span>
              </div>
              <span v-if="msg.chart.type === 'doughnut' || msg.chart.type === 'pie'" class="chart-type-pill-chat font-mono">DONUT</span>
            </div>

            <div class="chart-content-wrapper" :class="{ 'with-donut': (msg.chart.type === 'doughnut' || msg.chart.type === 'pie') && getDonutSegments(msg.chart).length > 0 }">
              <!-- Mini SVG Donut Ring in Chat Preview -->
              <div v-if="(msg.chart.type === 'doughnut' || msg.chart.type === 'pie') && getDonutSegments(msg.chart).length > 0" class="mini-donut-wrapper">
                <svg class="mini-donut-svg" viewBox="0 0 100 100">
                  <circle
                    class="mini-donut-bg"
                    cx="50"
                    cy="50"
                    r="34"
                    fill="transparent"
                    stroke-width="12"
                  />
                  <circle
                    v-for="(seg, sIdx) in getDonutSegments(msg.chart)"
                    :key="sIdx"
                    class="mini-donut-seg"
                    cx="50"
                    cy="50"
                    r="34"
                    fill="transparent"
                    stroke-width="12"
                    :stroke="seg.color"
                    :stroke-dasharray="seg.strokeDasharray"
                    :stroke-dashoffset="seg.strokeDashoffset"
                  />
                </svg>
                <div class="mini-donut-center font-mono">
                  <span>{{ getDonutSegments(msg.chart)[1]?.pct || getDonutSegments(msg.chart)[0]?.pct || 0 }}%</span>
                </div>
              </div>

              <div class="chart-bars-list">
                <div
                  v-for="(label, lIdx) in msg.chart.labels.slice(0, 5)"
                  :key="lIdx"
                  class="chart-bar-row font-mono"
                >
                  <span class="bar-label" :title="label">
                    <span class="chat-dot" :style="{ backgroundColor: getBarColor(lIdx) }"></span>
                    {{ label }}
                  </span>
                  <div class="bar-track">
                    <div
                      class="bar-fill"
                      :style="{
                        width: calculateBarWidth(msg.chart.values[lIdx], msg.chart.values) + '%',
                        backgroundColor: getBarColor(lIdx)
                      }"
                    ></div>
                  </div>
                  <span class="bar-val">{{ currencySymbol }}{{ formatNumber(msg.chart.values[lIdx]) }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Collapsed Technical Query (Hidden from business view by default) -->
          <details v-if="msg.sqlSnippet" class="query-details-accordion font-mono">
            <summary class="query-details-summary">
              <span class="summary-left">
                <Icon name="code" :size="10" />
                <span>Technical Query Details</span>
              </span>
              <span v-if="msg.rowCount !== undefined" class="row-count-badge">
                {{ msg.rowCount }} {{ msg.rowCount === 1 ? 'row' : 'rows' }}
              </span>
            </summary>
            <div class="code-preview-block">
              <div class="code-header">
                <span class="code-lang">Query Statement</span>
                <button class="copy-code-btn" @click="copyCode(msg.sqlSnippet)">
                  <Icon name="code" :size="11" />
                  <span>{{ copiedCode ? 'Copied' : 'Copy' }}</span>
                </button>
              </div>
              <pre class="font-mono"><code>{{ msg.sqlSnippet }}</code></pre>
            </div>
          </details>

          <!-- Compact Data Table Preview -->
          <div v-if="msg.rows && msg.rows.length > 0" class="mini-table-box">
            <div class="mini-table-header font-mono" @click="toggleTableExpand(msg.id)">
              <span class="table-toggle-title">
                <Icon name="database" :size="11" />
                <span>Result Dataset ({{ msg.rows.length }} rows)</span>
              </span>
              <span class="toggle-link">{{ expandedTables[msg.id] ? 'Hide Table' : 'View Table' }}</span>
            </div>

            <div v-if="expandedTables[msg.id]" class="mini-table-scroll">
              <table class="mini-data-table font-mono">
                <thead>
                  <tr>
                    <th v-for="col in msg.columns" :key="col">{{ col }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, rIdx) in msg.rows.slice(0, 10)" :key="rIdx">
                    <td v-for="col in msg.columns" :key="col">
                      {{ formatCellValue(row[col]) }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Action Buttons -->
          <div v-if="msg.hasActions && msg.actions" class="message-actions">
            <button
              v-for="act in msg.actions"
              :key="act"
              class="msg-action-btn font-mono"
              @click="sendQuickPrompt(act)"
            >
              {{ act }}
            </button>
          </div>
        </div>
      </div>

      <!-- Typing Indicator -->
      <div v-if="chatStore.isTyping" class="message-row assistant typing-row">
        <div class="message-bubble typing-bubble">
          <div class="typing-indicator">
            <span></span><span></span><span></span>
          </div>
          <span class="thinking-text font-mono">
            Generating SQL with {{ getSelectedModelName() }}...
          </span>
        </div>
      </div>
    </div>

    <!-- Chat Input Area (Antigravity-Inspired Modern Design) -->
    <div class="chat-input-area">
      <div class="input-card" :class="{ 'is-focused': isInputFocused }">
        <!-- Generous, Auto-expanding Textarea -->
        <textarea
          ref="chatTextarea"
          v-model="inputQuery"
          placeholder="Ask anything about SaaS spend, contracts, renewals, or licenses..."
          class="chat-textarea"
          rows="3"
          @focus="isInputFocused = true"
          @blur="isInputFocused = false"
          @input="adjustTextareaHeight"
          @keydown.enter.exact.prevent="handleSubmit"
        ></textarea>

        <!-- Bottom Controls Row -->
        <div class="input-card-bottom">
          <!-- Left: Plus action & Model Selector Pill -->
          <div class="bottom-left-controls">
            <!-- Plus Quick Menu -->
            <div class="plus-menu-container">
              <button
                type="button"
                class="ctrl-icon-btn plus-btn"
                :class="{ active: showQuickMenu }"
                @click.stop="toggleQuickMenu"
                title="Suggested queries"
              >
                <Icon name="plus" :size="15" />
              </button>

              <!-- Quick Queries Popover Menu -->
              <div v-if="showQuickMenu" class="dropdown-popover quick-menu-popover" @click.stop>
                <div class="popover-header font-mono">Suggested Queries</div>
                <div class="popover-list">
                  <button
                    v-for="(p, pIdx) in quickPrompts"
                    :key="pIdx"
                    type="button"
                    class="popover-item"
                    @click="applyQuickPrompt(p)"
                  >
                    <Icon name="sparkles" :size="12" class="popover-icon" />
                    <span class="popover-item-text">{{ p }}</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- Model Selector Pill (matches Antigravity design) -->
            <div class="model-pill-container">
              <button
                type="button"
                class="model-pill-btn"
                :class="{ active: showModelMenu, disabled: isModelSwitchDisabled }"
                @click.stop="toggleModelMenu"
                :disabled="isModelSwitchDisabled"
                :title="isModelSwitchDisabled ? 'Model locked by administrator' : 'Select AI Model'"
              >
                <span class="model-pill-text">{{ getSelectedModelShortName() }}</span>
                <Icon v-if="!isModelSwitchDisabled" :name="showModelMenu ? 'chevron-up' : 'chevron-down'" :size="12" class="pill-chevron" />
                <Icon v-else name="lock" :size="10" class="lock-icon" />
              </button>

              <!-- Model Selector Popover Menu -->
              <div v-if="showModelMenu && !isModelSwitchDisabled" class="dropdown-popover model-menu-popover" @click.stop>
                <div class="popover-header font-mono">Available Models ({{ chatStore.models.length }})</div>
                <template v-for="group in modelGroups" :key="group.provider">
                  <div class="popover-section-label font-mono">{{ group.providerName }}</div>
                  <button
                    v-for="model in group.models"
                    :key="model.id"
                    type="button"
                    class="popover-item model-item"
                    :class="{ selected: chatStore.selectedModel === model.id }"
                    @click="selectModel(model.id)"
                  >
                    <span class="model-item-title">{{ model.name }}</span>
                    <span v-if="model.is_default" class="model-badge">Default</span>
                    <span v-else-if="model.badge" class="model-badge speed">{{ model.badge }}</span>
                  </button>
                </template>
              </div>
            </div>
          </div>

          <!-- Right: Circular Arrow Send button -->
          <div class="bottom-right-controls">
            <button
              type="button"
              class="circular-send-btn"
              :disabled="!inputQuery.trim() || chatStore.isTyping"
              @click="handleSubmit"
              title="Send query (Enter)"
            >
              <Icon name="arrow-right" :size="16" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useUIStore } from '@/stores/ui'
import { useChatStore } from '@/stores/chat'
import { useAuthStore } from '@/stores/auth'
import Icon from '@/components/common/Icon.vue'

const uiStore = useUIStore()
const chatStore = useChatStore()
const authStore = useAuthStore()

const currencySymbol = ref(import.meta.env.VITE_CURRENCY_SYMBOL || '₹')

const inputQuery = ref('')
const isInputFocused = ref(false)
const copiedCode = ref(false)
const messagesContainer = ref(null)
const chatTextarea = ref(null)
const expandedTables = ref({})

const showModelMenu = ref(false)
const showQuickMenu = ref(false)

const quickPrompts = [
  'Top 5 subscriptions by monthly spend',
  'Which subscriptions renew in next 30 days?',
  'Show total monthly spend by category',
  'Find all dormant license seats',
  'Total savings from detected optimizations',
]

async function handleClearChat() {
  if (!chatStore.messages || chatStore.messages.length <= 1) {
    chatStore.clearChat()
    return
  }
  const confirmed = await uiStore.openConfirmModal({
    title: 'Clear Conversation',
    message: 'Are you sure you want to clear the entire conversation?',
    subMessage: 'Your query history, interactive visualizations, and generated SQL for this session will be reset.',
    confirmText: 'Clear Chat',
    cancelText: 'Keep Chat',
    type: 'danger',
    icon: 'trash',
  })
  if (confirmed) {
    chatStore.clearChat()
    uiStore.showToast('Chat conversation cleared.', 'info')
  }
}

onMounted(() => {
  chatStore.fetchModels(authStore.user.role)
  window.addEventListener('click', closePopovers)
  adjustTextareaHeight()
})

onUnmounted(() => {
  window.removeEventListener('click', closePopovers)
})

const isModelSwitchDisabled = computed(() => {
  return chatStore.isEnforcedByAdmin || chatStore.models.length <= 1
})

const modelGroups = computed(() => {
  const groups = []
  const groq = chatStore.models.filter(m => m.provider === 'groq')
  if (groq.length > 0) {
    groups.push({
      provider: 'groq',
      providerName: 'Groq Cloud Models',
      models: groq
    })
  }
  const google = chatStore.models.filter(m => m.provider === 'google')
  if (google.length > 0) {
    groups.push({
      provider: 'google',
      providerName: 'Google DeepMind Models',
      models: google
    })
  }
  const other = chatStore.models.filter(m => m.provider !== 'groq' && m.provider !== 'google')
  if (other.length > 0) {
    groups.push({
      provider: 'other',
      providerName: 'Other AI Models',
      models: other
    })
  }
  return groups
})

function closePopovers() {
  showModelMenu.value = false
  showQuickMenu.value = false
}

function toggleModelMenu() {
  if (isModelSwitchDisabled.value) return
  showModelMenu.value = !showModelMenu.value
  showQuickMenu.value = false
}

function toggleQuickMenu() {
  showQuickMenu.value = !showQuickMenu.value
  showModelMenu.value = false
}

function selectModel(modelId) {
  chatStore.selectedModel = modelId
  showModelMenu.value = false
}

function applyQuickPrompt(prompt) {
  inputQuery.value = prompt
  showQuickMenu.value = false
  adjustTextareaHeight()
  if (chatTextarea.value) {
    chatTextarea.value.focus()
  }
}

function getSelectedModelName() {
  const m = chatStore.models.find(x => x.id === chatStore.selectedModel) || chatStore.models[0]
  return m ? m.name : 'AI Model'
}

function getSelectedModelShortName() {
  const m = chatStore.models.find(x => x.id === chatStore.selectedModel) || chatStore.models[0]
  if (!m) return 'Select Model'
  return m.name.replace('Google · ', '').replace('Groq · ', '')
}

function adjustTextareaHeight() {
  nextTick(() => {
    if (!chatTextarea.value) return
    chatTextarea.value.style.height = 'auto'
    const newHeight = Math.min(Math.max(chatTextarea.value.scrollHeight, 72), 220)
    chatTextarea.value.style.height = `${newHeight}px`
  })
}

function handleSubmit() {
  if (!inputQuery.value.trim() || chatStore.isTyping) return
  const text = inputQuery.value
  inputQuery.value = ''
  adjustTextareaHeight()
  chatStore.sendMessage(text, authStore.user.role, authStore.user.email)
  scrollToBottom()
}

function sendQuickPrompt(prompt) {
  chatStore.sendMessage(prompt, authStore.user.role, authStore.user.email)
  scrollToBottom()
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

function copyCode(code) {
  if (!code) return
  navigator.clipboard.writeText(code)
  copiedCode.value = true
  setTimeout(() => {
    copiedCode.value = false
  }, 2000)
}

function toggleTableExpand(msgId) {
  expandedTables.value[msgId] = !expandedTables.value[msgId]
}

function calculateBarWidth(val, allVals) {
  const max = Math.max(...allVals, 1)
  return Math.max(12, Math.round((Number(val || 0) / max) * 100))
}

function getBarColor(idx) {
  const colors = ['#0ea5e9', '#10b981', '#f59e0b', '#ec4899', '#38bdf8']
  return colors[idx % colors.length]
}

function getDonutSegments(chart) {
  if (!chart || !chart.values || !chart.values.length) return []
  const values = chart.values.map(v => Math.max(0, Number(v) || 0))
  const total = values.reduce((sum, v) => sum + v, 0)
  if (total <= 0) return []

  const radius = 34
  const circumference = 2 * Math.PI * radius // ~213.63
  let accumulatedFraction = 0

  return values.map((val, idx) => {
    const fraction = val / total
    const strokeDasharray = `${(fraction * circumference).toFixed(2)} ${circumference.toFixed(2)}`
    const strokeDashoffset = `${(-accumulatedFraction * circumference).toFixed(2)}`
    accumulatedFraction += fraction
    return {
      color: getBarColor(idx),
      strokeDasharray,
      strokeDashoffset,
      pct: Math.round(fraction * 100),
      label: chart.labels ? chart.labels[idx] : ''
    }
  })
}

function formatNumber(val) {
  const num = Number(val)
  return isNaN(num) ? val : num.toLocaleString('en-IN')
}

function formatCellValue(val) {
  if (val === null || val === undefined) return '-'
  if (typeof val === 'number') return val.toLocaleString('en-IN')
  return String(val)
}

function formatMessage(text) {
  if (!text) return ''
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/### (.*?)(<br>|\n|$)/g, '<div class="msg-subhead">$1</div>')
    .replace(/\n/g, '<br>')
}
</script>

<style scoped>
.chat-agent-panel {
  width: var(--chat-expanded);
  background-color: var(--bg-secondary);
  border-left: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  transition: width var(--transition-normal), opacity var(--transition-normal);
  overflow: hidden;
  position: relative;
  z-index: 10;
  flex-shrink: 0;
}

.chat-agent-panel.is-collapsed {
  width: 0;
  border-left: none;
  opacity: 0;
  pointer-events: none;
}

/* Header */
.chat-header {
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 12px;
  border-bottom: 1px solid var(--border-subtle);
  background-color: var(--bg-secondary);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  overflow: visible;
  flex: 1;
}

.copilot-avatar {
  width: 26px;
  height: 26px;
  border-radius: var(--radius-sm);
  background: var(--accent-light);
  border: 1px solid rgba(var(--accent-rgb), 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.sparkle-icon {
  color: var(--accent);
}

.copilot-title-group {
  display: flex;
  flex-direction: column;
  justify-content: center;
  flex: 1;
  min-width: 0;
  gap: 1px;
}

.title-with-badge {
  display: flex;
  align-items: center;
  gap: 6px;
}

.copilot-title {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: var(--text-primary);
  line-height: 1.2;
}

.copilot-subtitle {
  font-size: 10.5px;
  color: var(--text-muted);
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.title-with-status {
  display: flex;
  align-items: center;
  gap: 7px;
}

.agent-status-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 9.5px;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 10px;
  letter-spacing: 0.02em;
  user-select: none;
  transition: all var(--transition-fast);
}

.agent-status-tag.is-connected {
  background-color: rgba(16, 185, 129, 0.12);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.agent-status-tag.is-disconnected {
  background-color: rgba(245, 158, 11, 0.12);
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.35);
}

.status-pulse-dot {
  width: 5.5px;
  height: 5.5px;
  border-radius: 50%;
  display: inline-block;
}

.agent-status-tag.is-connected .status-pulse-dot {
  background-color: #10b981;
  box-shadow: 0 0 5px rgba(16, 185, 129, 0.8);
  animation: pulse-green 2s infinite ease-in-out;
}

.agent-status-tag.is-disconnected .status-pulse-dot {
  background-color: #f59e0b;
  box-shadow: 0 0 5px rgba(245, 158, 11, 0.7);
  animation: pulse-amber 2s infinite ease-in-out;
}

@keyframes pulse-green {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.85); }
}

@keyframes pulse-amber {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.85); }
}

/* Offline Banner Notice */
.agent-offline-banner {
  padding: 8px 14px;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.09), rgba(239, 68, 68, 0.05));
  border-bottom: 1px solid rgba(245, 158, 11, 0.2);
  user-select: none;
}

.warning-banner-inner {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.warning-badge-icon {
  font-size: 13px;
  line-height: 1;
  flex-shrink: 0;
  margin-top: 1px;
}

.warning-banner-text {
  display: flex;
  flex-direction: column;
  gap: 1px;
  min-width: 0;
}

.warning-title {
  color: #f59e0b;
  font-weight: 600;
  font-size: 11px;
}

.warning-sub {
  color: var(--text-muted);
  font-size: 10px;
  line-height: 1.3;
}

.enforced-badge {
  font-size: 9px;
  background-color: var(--warning-bg);
  color: var(--warning);
  padding: 1px 4px;
  border-radius: 3px;
  display: flex;
  align-items: center;
  gap: 3px;
}

.model-select-wrapper {
  display: flex;
  align-items: center;
  margin-top: 2px;
}

.model-select {
  font-size: 10px;
  font-family: var(--font-mono);
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  cursor: pointer;
  padding: 2px 22px 2px 6px;
  min-width: 225px;
  max-width: 265px;
  width: auto;
  line-height: 1.35;
  white-space: nowrap;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='10' viewBox='0 0 24 24' fill='none' stroke='%239aa4b2' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 6px center;
  transition: all var(--transition-fast);
}

.model-select:hover {
  border-color: var(--border-highlight);
  color: var(--text-primary);
}

.model-select:focus {
  outline: none;
  border-color: var(--accent);
  color: var(--accent);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.action-btn {
  width: 26px;
  height: 26px;
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  background: transparent;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-btn:hover {
  background-color: var(--bg-hover);
  color: var(--text-primary);
}

/* Quick Prompts */
.quick-prompts-bar {
  padding: 8px 10px;
  border-bottom: 1px solid var(--border-subtle);
  background-color: var(--bg-primary);
}

.prompts-scroll {
  display: flex;
  gap: 6px;
  overflow-x: auto;
  padding-bottom: 2px;
}

.prompt-chip {
  font-size: 10px;
  white-space: nowrap;
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  padding: 3px 8px;
  border-radius: var(--radius-full);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.prompt-chip:hover {
  background-color: var(--bg-active);
  border-color: var(--accent);
  color: var(--accent);
}

/* Messages List */
.chat-messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.message-row {
  display: flex;
  flex-direction: column;
}

.message-row.user {
  align-items: flex-end;
}

.message-row.assistant {
  align-items: flex-start;
}

.message-bubble {
  max-width: 95%;
  padding: 10px 12px;
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  line-height: 1.5;
  box-shadow: var(--shadow-sm);
}

.message-row.user .message-bubble {
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}

.message-row.assistant .message-bubble {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}

.message-bubble.error-bubble {
  border-color: rgba(239, 68, 68, 0.4);
  background-color: rgba(239, 68, 68, 0.05);
}

.message-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 6px;
  font-size: 10px;
  color: var(--text-muted);
}

.meta-right {
  display: flex;
  align-items: center;
  gap: 6px;
}

.query-type-tag {
  background-color: var(--bg-active);
  color: var(--accent);
  padding: 1px 4px;
  border-radius: 3px;
  font-size: 9px;
}

.latency-tag {
  color: var(--success);
  font-size: 9px;
}

.sender-name {
  font-weight: var(--font-weight-medium);
  color: var(--text-secondary);
}

.message-content {
  margin-bottom: 8px;
  word-break: break-word;
}

/* Auto-generated Chart */
.chart-preview-card {
  margin: 8px 0;
  background-color: var(--bg-primary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 8px 10px;
}

.chart-card-header {
  font-size: 10px;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 5px;
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.chart-title-group {
  display: flex;
  align-items: center;
  gap: 5px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chart-type-pill-chat {
  font-size: 8.5px;
  font-weight: 700;
  padding: 1px 5px;
  border-radius: 3px;
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
  flex-shrink: 0;
}

.chart-content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.chart-content-wrapper.with-donut {
  display: grid;
  grid-template-columns: 68px 1fr;
  align-items: center;
  gap: 10px;
}

.mini-donut-wrapper {
  position: relative;
  width: 68px;
  height: 68px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mini-donut-svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
  overflow: visible;
}

.mini-donut-bg {
  stroke: var(--bg-tertiary);
  opacity: 0.5;
}

.mini-donut-seg {
  stroke-linecap: round;
  transition: stroke-dasharray 0.5s ease;
}

.mini-donut-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 10.5px;
  font-weight: 700;
  color: #10b981;
}

.chat-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  margin-right: 4px;
}

.chart-bars-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.chart-bar-row {
  display: grid;
  grid-template-columns: 85px 1fr 65px;
  align-items: center;
  gap: 8px;
  font-size: 10px;
}

.bar-label {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text-secondary);
}

.bar-track {
  height: 6px;
  background-color: var(--bg-tertiary);
  border-radius: 3px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.4s ease;
}

.bar-val {
  text-align: right;
  color: var(--text-primary);
}

.msg-subhead {
  font-size: 11.5px;
  font-weight: 700;
  color: var(--accent);
  margin-top: 10px;
  margin-bottom: 3px;
  letter-spacing: 0.02em;
}

/* Collapsible Technical Query Accordion */
.query-details-accordion {
  margin: 6px 0;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  background-color: var(--bg-primary);
  overflow: hidden;
}

.query-details-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 5px 8px;
  font-size: 10px;
  color: var(--text-muted);
  cursor: pointer;
  background-color: var(--bg-secondary);
  user-select: none;
  transition: color var(--transition-fast), background-color var(--transition-fast);
}

.query-details-summary:hover {
  color: var(--text-primary);
  background-color: var(--bg-hover);
}

.summary-left {
  display: flex;
  align-items: center;
  gap: 5px;
}

/* SQL Code Block */
.code-preview-block {
  margin: 0;
  background-color: var(--bg-app);
  border: none;
  border-top: 1px solid var(--border-subtle);
  border-radius: 0;
  overflow: hidden;
}

.code-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 8px;
  background-color: var(--bg-secondary);
  border-bottom: 1px solid var(--border-subtle);
  font-size: 10px;
}

.dialect-tabs {
  display: flex;
  align-items: center;
  gap: 6px;
}

.code-lang {
  color: var(--accent);
}

.row-count-badge {
  background-color: var(--bg-tertiary);
  color: var(--text-muted);
  padding: 0 4px;
  border-radius: 3px;
}

.copy-code-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 10px;
}

.copy-code-btn:hover {
  color: var(--text-primary);
}

.code-preview-block pre {
  margin: 0;
  padding: 8px;
  font-size: 11px;
  line-height: 1.4;
  overflow-x: auto;
  color: #79c0ff;
}

/* Mini Table Preview */
.mini-table-box {
  margin: 6px 0;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  background-color: var(--bg-primary);
  overflow: hidden;
}

.mini-table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 8px;
  font-size: 10.5px;
  cursor: pointer;
  background-color: var(--bg-secondary);
}

.table-toggle-title {
  display: flex;
  align-items: center;
  gap: 5px;
  color: var(--text-secondary);
}

.toggle-link {
  color: var(--accent);
}

.mini-table-scroll {
  max-height: 140px;
  overflow: auto;
}

.mini-data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 10px;
}

.mini-data-table th, .mini-data-table td {
  padding: 4px 8px;
  border-bottom: 1px solid var(--border-subtle);
  text-align: left;
  white-space: nowrap;
}

.mini-data-table th {
  background-color: var(--bg-tertiary);
  color: var(--text-muted);
}

/* Pipeline Trace */
.pipeline-trace {
  font-size: 10px;
  color: var(--text-muted);
  margin-top: 6px;
  padding-top: 4px;
  border-top: 1px dashed var(--border-subtle);
}

.pipeline-trace summary {
  cursor: pointer;
  color: var(--accent);
}

.trace-content {
  padding: 4px 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

/* Message Actions */
.message-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

.msg-action-btn {
  font-size: 10.5px;
  padding: 3px 8px;
  border-radius: var(--radius-sm);
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.msg-action-btn:hover {
  background-color: var(--bg-active);
  color: var(--accent);
  border-color: var(--accent);
}

/* Typing Indicator */
.typing-bubble {
  display: flex;
  align-items: center;
  gap: 10px;
}

.typing-indicator {
  display: flex;
  gap: 3px;
}

.typing-indicator span {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background-color: var(--accent);
  animation: bounce 1.2s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes bounce {
  0%, 80%, 100% { transform: translateY(0); opacity: 0.4; }
  40% { transform: translateY(-4px); opacity: 1; }
}

.thinking-text {
  font-size: 10.5px;
  color: var(--text-muted);
}

/* Input Area (Antigravity-Inspired Modern Style) */
.chat-input-area {
  padding: 12px 14px 14px 14px;
  background-color: var(--bg-secondary);
  border-top: 1px solid var(--border-subtle);
  position: relative;
}

.input-card {
  background-color: var(--bg-card);
  border: 1px solid rgba(255, 255, 255, 0.09);
  border-radius: 16px;
  padding: 12px 14px 10px 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  transition: all var(--transition-fast);
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.25);
  position: relative;
}

.input-card:focus-within,
.input-card.is-focused {
  border-color: rgba(56, 189, 248, 0.45);
  box-shadow: 0 4px 22px rgba(56, 189, 248, 0.12), 0 0 0 1px rgba(56, 189, 248, 0.2);
}

.chat-textarea {
  width: 100%;
  min-height: 72px;
  max-height: 220px;
  background: transparent !important;
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
  color: var(--text-primary);
  font-size: 13px;
  line-height: 1.55;
  font-family: var(--font-sans);
  resize: none;
  padding: 0;
  margin: 0;
  overflow-y: auto;
}

.chat-textarea::placeholder {
  color: var(--text-muted);
  opacity: 0.85;
}

.input-card-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 4px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.bottom-left-controls {
  display: flex;
  align-items: center;
  gap: 6px;
  position: relative;
}

.ctrl-icon-btn {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.ctrl-icon-btn:hover {
  background-color: var(--bg-hover);
  color: var(--text-primary);
}

.ctrl-icon-btn.active {
  background-color: var(--bg-active);
  color: var(--accent);
}

.model-pill-container {
  position: relative;
}

.model-pill-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 10px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: var(--text-secondary);
  font-size: 12px;
  font-family: var(--font-sans);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.model-pill-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.09);
  color: var(--text-primary);
  border-color: rgba(255, 255, 255, 0.16);
}

.model-pill-btn.active {
  border-color: var(--accent);
  color: var(--text-primary);
}

.model-pill-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.model-pill-text {
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.pill-chevron {
  color: var(--text-muted);
}

.lock-icon {
  color: var(--warning);
}

.bottom-right-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}


.circular-send-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--accent-gradient);
  border: none;
  color: #ffffff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
  box-shadow: 0 2px 10px rgba(56, 189, 248, 0.35);
  flex-shrink: 0;
}

.circular-send-btn:hover:not(:disabled) {
  transform: scale(1.06);
  box-shadow: 0 4px 14px rgba(56, 189, 248, 0.55);
}

.circular-send-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* Popover Dropdowns */
.dropdown-popover {
  position: absolute;
  bottom: calc(100% + 10px);
  left: 0;
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 6px;
  z-index: 60;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(16px);
  animation: popoverFadeIn 0.15s ease-out;
}

@keyframes popoverFadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}

.model-menu-popover {
  width: 250px;
}

.quick-menu-popover {
  width: 280px;
}

.popover-header {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  padding: 6px 8px 4px 8px;
}

.popover-section-label {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--text-muted);
  padding: 8px 8px 4px 8px;
  border-top: 1px solid var(--border-subtle);
  margin-top: 4px;
}

.popover-section-label:first-of-type {
  border-top: none;
  margin-top: 0;
}

.popover-item {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 7px 10px;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: var(--text-primary);
  font-size: 12px;
  cursor: pointer;
  text-align: left;
  transition: all var(--transition-fast);
}

.popover-item:hover {
  background-color: var(--bg-hover);
  color: var(--accent);
}

.popover-item.selected {
  background-color: var(--bg-active);
  color: var(--accent);
  font-weight: 500;
}

.model-item-title {
  flex: 1;
}

.model-badge {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(56, 189, 248, 0.15);
  color: var(--accent);
}

.model-badge.speed {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success);
}

.popover-icon {
  color: var(--accent);
  flex-shrink: 0;
}

.popover-item-text {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
