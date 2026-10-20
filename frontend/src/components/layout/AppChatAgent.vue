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
          <span class="copilot-title">AI Copilot</span>
          <div class="model-select-wrapper">
            <select v-model="chatStore.selectedModel" class="model-select">
              <option v-for="m in chatStore.models" :key="m" :value="m">
                {{ m }}
              </option>
            </select>
          </div>
        </div>
      </div>

      <div class="header-actions">
        <button
          class="action-btn"
          @click="chatStore.clearChat"
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
        <div class="message-bubble">
          <div class="message-meta">
            <span class="sender-name">{{ msg.sender === 'assistant' ? 'SubscriptIQ AI' : 'You' }}</span>
            <span class="message-time">{{ msg.time }}</span>
          </div>

          <div class="message-content" v-html="formatMessage(msg.text)"></div>

          <!-- Code Snippet Preview -->
          <div v-if="msg.codeSnippet" class="code-preview-block">
            <div class="code-header">
              <span class="code-lang">json / typescript</span>
              <button class="copy-code-btn" @click="copyCode(msg.codeSnippet)">
                <Icon name="code" :size="11" />
                <span>{{ copiedCode ? 'Copied' : 'Copy' }}</span>
              </button>
            </div>
            <pre><code>{{ msg.codeSnippet }}</code></pre>
          </div>

          <!-- Action Buttons -->
          <div v-if="msg.hasActions && msg.actions" class="message-actions">
            <button
              v-for="act in msg.actions"
              :key="act"
              class="msg-action-btn"
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
          <span class="thinking-text">Analyzing subscription contracts...</span>
        </div>
      </div>
    </div>

    <!-- Chat Input Area -->
    <div class="chat-input-area">
      <div class="input-card">
        <textarea
          v-model="inputQuery"
          rows="2"
          placeholder="Ask SubscriptIQ AI about licenses, renewals, or optimizations..."
          class="chat-textarea"
          @keydown.enter.prevent="handleEnter"
        ></textarea>

        <div class="input-actions-bar">
          <div class="input-meta-tools">
            <span class="context-tag font-mono">
              <Icon name="file" :size="11" />
              <span>Workspace Context</span>
            </span>
          </div>

          <div class="send-action-group">
            <span class="shortcut-hint">↵ Enter</span>
            <button
              class="send-btn"
              :disabled="!inputQuery.trim() || chatStore.isTyping"
              @click="handleSubmit"
            >
              <Icon name="send" :size="12" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { useUIStore } from '@/stores/ui'
import { useChatStore } from '@/stores/chat'
import Icon from '@/components/common/Icon.vue'

const uiStore = useUIStore()
const chatStore = useChatStore()

const inputQuery = ref('')
const copiedCode = ref(false)
const messagesContainer = ref(null)

const quickPrompts = [
  '⚡ Audit overlapping licenses',
  '📅 Next 14 days renewals',
  '📉 Forecast seat reduction',
]

function handleEnter(e) {
  if (!e.shiftKey) {
    handleSubmit()
  }
}

function handleSubmit() {
  if (!inputQuery.value.trim() || chatStore.isTyping) return
  chatStore.sendMessage(inputQuery.value)
  inputQuery.value = ''
  scrollToBottom()
}

function sendQuickPrompt(prompt) {
  chatStore.sendMessage(prompt)
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
  navigator.clipboard.writeText(code)
  copiedCode.value = true
  setTimeout(() => {
    copiedCode.value = false
  }, 2000)
}

function formatMessage(text) {
  if (!text) return ''
  // Basic markdown bold/italic/newlines formatting for crisp rendering
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
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
  overflow: hidden;
}

.copilot-avatar {
  width: 26px;
  height: 26px;
  border-radius: var(--radius-sm);
  background: var(--accent-light);
  border: 1px solid rgba(99, 102, 241, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
}

.sparkle-icon {
  color: var(--accent);
}

.copilot-title-group {
  display: flex;
  flex-direction: column;
}

.copilot-title {
  font-size: var(--text-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  line-height: 1.2;
}

.model-select {
  font-size: 10px;
  font-family: var(--font-mono);
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0;
  margin-top: 1px;
}

.model-select:focus {
  outline: none;
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
  font-size: 10.5px;
  font-family: var(--font-sans);
  font-weight: var(--font-weight-regular);
  white-space: nowrap;
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  padding: 3px 8px;
  border-radius: var(--radius-full);
  color: var(--text-secondary);
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
  max-width: 92%;
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

.message-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 5px;
  font-size: 10px;
  font-family: var(--font-mono);
  color: var(--text-muted);
}

.sender-name {
  font-weight: var(--font-weight-medium);
  color: var(--text-secondary);
}

.message-content {
  font-weight: var(--font-weight-regular);
  font-size: var(--text-sm);
  letter-spacing: -0.01em;
}

/* Code Snippet */
.code-preview-block {
  margin-top: 8px;
  background-color: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.code-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 8px;
  background-color: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-subtle);
  font-size: 10px;
  font-family: var(--font-mono);
  color: var(--text-muted);
}

.copy-code-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 10px;
  color: var(--text-muted);
}

.copy-code-btn:hover {
  color: var(--text-primary);
}

.code-preview-block pre {
  padding: 8px;
  font-size: 11px;
  color: #79c0ff;
  overflow-x: auto;
}

/* Actions in message */
.message-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

.msg-action-btn {
  font-size: 11px;
  padding: 3px 8px;
  border-radius: var(--radius-sm);
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--accent);
  transition: all var(--transition-fast);
}

.msg-action-btn:hover {
  background-color: var(--accent-light);
  border-color: var(--accent);
}

/* Typing Indicator */
.typing-bubble {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
}

.typing-indicator {
  display: flex;
  gap: 3px;
}

.typing-indicator span {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background-color: var(--accent);
  animation: typing-bounce 1.2s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing-bounce {
  0%, 80%, 100% { transform: translateY(0); opacity: 0.4; }
  40% { transform: translateY(-4px); opacity: 1; }
}

.thinking-text {
  font-size: 11px;
  color: var(--text-muted);
  font-family: var(--font-mono);
}

/* Input Area */
.chat-input-area {
  padding: 10px;
  border-top: 1px solid var(--border-subtle);
  background-color: var(--bg-secondary);
}

.input-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  box-shadow: var(--shadow-sm);
  transition: border-color var(--transition-fast);
}

.input-card:focus-within {
  border-color: var(--accent);
}

.chat-textarea {
  width: 100%;
  border: none;
  background: transparent;
  resize: none;
  font-size: var(--text-sm);
  font-weight: var(--font-weight-regular);
  color: var(--text-primary);
  line-height: 1.4;
  outline: none;
}

.input-actions-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.context-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 10px;
  color: var(--text-muted);
  background-color: var(--bg-tertiary);
  padding: 2px 6px;
  border-radius: 3px;
}

.send-action-group {
  display: flex;
  align-items: center;
  gap: 6px;
}

.shortcut-hint {
  font-size: 10px;
  font-family: var(--font-mono);
  color: var(--text-muted);
}

.send-btn {
  width: 26px;
  height: 26px;
  border-radius: var(--radius-sm);
  background: var(--accent);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.send-btn:not(:disabled):hover {
  background: var(--accent-hover);
  box-shadow: var(--accent-glow);
}
</style>
