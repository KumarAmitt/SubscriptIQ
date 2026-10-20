<template>
  <div class="admin-view">
    <div class="view-header">
      <div class="header-titles">
        <div class="admin-shield-badge">
          <Icon name="shield" :size="12" />
          <span>SECURITY & ACCESS CONTROL</span>
        </div>
        <h1 class="view-title">{{ currentTitle }}</h1>
        <p class="view-subtitle">{{ currentDescription }}</p>
      </div>

      <div class="header-role-indicator">
        <span class="role-pill font-mono">Current Context: ADMIN</span>
      </div>
    </div>

    <!-- Submenu Content 1: Users & Access -->
    <div v-if="uiStore.activeNav === 'admin-users'" class="admin-card">
      <div class="card-header">
        <h3 class="card-title">User Accounts & Role Permissions</h3>
        <button class="small-action-btn font-mono" @click="inviteUser">+ Invite User</button>
      </div>

      <table class="editor-table">
        <thead>
          <tr>
            <th>User</th>
            <th>Role</th>
            <th>Seat Allocation</th>
            <th>MFA Status</th>
            <th>Last Active</th>
            <th class="text-right">Manage</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in usersList" :key="user.email">
            <td class="user-meta-cell">
              <span class="avatar-circle font-mono">{{ user.avatar }}</span>
              <div>
                <div class="user-name">{{ user.name }}</div>
                <div class="user-email font-mono">{{ user.email }}</div>
              </div>
            </td>
            <td>
              <span class="role-chip" :class="user.role.toLowerCase()">{{ user.role }}</span>
            </td>
            <td class="font-mono text-muted">{{ user.seats }} licenses</td>
            <td>
              <span class="status-indicator" :class="{ 'mfa-on': user.mfa }">
                {{ user.mfa ? 'Enabled' : 'Disabled' }}
              </span>
            </td>
            <td class="font-mono text-muted">{{ user.lastActive }}</td>
            <td class="text-right">
              <button class="table-btn font-mono">Edit</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Submenu Content 2: All Subscriptions -->
    <div v-else-if="uiStore.activeNav === 'admin-subscriptions'" class="admin-card">
      <div class="card-header">
        <h3 class="card-title">Corporate Billing & Master Contracts</h3>
        <button class="small-action-btn font-mono">+ Add Contract</button>
      </div>
      <div class="config-code-box">
        <div class="box-bar">
          <span class="font-mono">billing_contracts.json</span>
          <span class="badge font-mono">AUTO-RECONCILE ACTIVE</span>
        </div>
        <pre class="font-mono"><code>{
  "billing_cycle": "annual_consolidated",
  "payment_provider": "Stripe Invoicing / ACH",
  "corporate_cards": [
    { "type": "Amex Corporate", "last4": "8921", "limit": "$50,000" },
    { "type": "Brex Virtual", "last4": "4102", "limit": "$25,000" }
  ],
  "auto_downgrade_dormant_seats": true,
  "telemetry_sync_interval": "hourly"
}</code></pre>
      </div>
    </div>

    <!-- Submenu Content 3: AI Models & Quotas -->
    <div v-else-if="uiStore.activeNav === 'admin-models'" class="admin-card">
      <div class="card-header">
        <h3 class="card-title">AI Provider Allocations & Token Quotas</h3>
        <span class="status-live font-mono">All Endpoints Healthy</span>
      </div>

      <div class="model-quota-grid">
        <div v-for="model in modelQuotas" :key="model.name" class="quota-box">
          <div class="quota-head">
            <span class="model-title">{{ model.name }}</span>
            <span class="status-pill optimal">{{ model.status }}</span>
          </div>
          <div class="font-mono quota-val">{{ model.used }} / {{ model.limit }}</div>
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: model.pct + '%', backgroundColor: 'var(--accent)' }"></div>
          </div>
          <div class="quota-sub text-muted font-mono">{{ model.tokens }} tokens consumed today</div>
        </div>
      </div>
    </div>

    <!-- Submenu Content 4: System Settings -->
    <div v-else class="admin-card">
      <div class="card-header">
        <h3 class="card-title">Workspace Environment Configuration</h3>
        <button class="small-action-btn font-mono" @click="saveEnv">Save Changes</button>
      </div>

      <div class="settings-form">
        <div class="form-row">
          <label>Workspace Domain</label>
          <input type="text" value="subscriptiq.ai" class="font-mono" />
        </div>
        <div class="form-row">
          <label>Audit Log Retention</label>
          <select class="font-mono">
            <option>90 Days (SOC2 Compliant)</option>
            <option>180 Days</option>
            <option>1 Year</option>
          </select>
        </div>
        <div class="form-row">
          <label>AI License Threshold Alert</label>
          <input type="text" value="Under 25% utilization for > 30 days" class="font-mono" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useUIStore } from '@/stores/ui'
import Icon from '@/components/common/Icon.vue'

const uiStore = useUIStore()

const currentTitle = computed(() => {
  switch (uiStore.activeNav) {
    case 'admin-users': return 'Users & Access Management'
    case 'admin-subscriptions': return 'All Corporate Subscriptions'
    case 'admin-models': return 'AI Models & Token Quotas'
    case 'admin-settings': return 'System Settings & Webhooks'
    default: return 'Administration Console'
  }
})

const currentDescription = computed(() => {
  switch (uiStore.activeNav) {
    case 'admin-users': return 'Provision team licenses, configure Single Sign-On, and audit user permissions.'
    case 'admin-subscriptions': return 'Manage corporate billing accounts, direct vendor contracts, and invoicing.'
    case 'admin-models': return 'Configure LLM model routing, API tokens, and workspace compute limits.'
    case 'admin-settings': return 'Global workspace rules, audit compliance, and automated notification hooks.'
    default: return 'Secure administrative controls for enterprise workspaces.'
  }
})

const usersList = ref([
  { name: 'Alex Rivera', email: 'alex.rivera@subscriptiq.ai', avatar: 'AR', role: 'Super Admin', seats: 8, mfa: true, lastActive: 'Just now' },
  { name: 'Elena Rostova', email: 'elena@subscriptiq.ai', avatar: 'ER', role: 'Admin', seats: 6, mfa: true, lastActive: '12m ago' },
  { name: 'Marcus Chen', email: 'marcus.c@subscriptiq.ai', avatar: 'MC', role: 'Finance Lead', seats: 4, mfa: true, lastActive: '1h ago' },
  { name: 'Sarah Miller', email: 'sarah.m@subscriptiq.ai', avatar: 'SM', role: 'Viewer', seats: 1, mfa: false, lastActive: '2d ago' },
])

const modelQuotas = ref([
  { name: 'Claude 3.5 Sonnet', status: 'Healthy', used: '68,400', limit: '100,000', pct: 68, tokens: '1.4M' },
  { name: 'Gemini 1.5 Pro', status: 'Optimal', used: '32,100', limit: '100,000', pct: 32, tokens: '840K' },
  { name: 'GPT-4o', status: 'Normal', used: '54,200', limit: '80,000', pct: 67, tokens: '1.1M' },
])

function inviteUser() {
  alert('Invite link copied to clipboard.')
}

function saveEnv() {
  alert('System settings updated successfully.')
}
</script>

<style scoped>
.admin-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.view-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}

.admin-shield-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 10px;
  font-family: var(--font-mono);
  font-weight: var(--font-weight-semibold);
  color: var(--warning);
  background-color: var(--warning-bg);
  padding: 2px 7px;
  border-radius: var(--radius-full);
  margin-bottom: 4px;
}

.view-title {
  font-size: var(--text-lg);
  font-weight: var(--font-weight-semibold);
  letter-spacing: -0.02em;
  color: var(--text-primary);
}

.view-subtitle {
  font-size: var(--text-xs);
  color: var(--text-muted);
  margin-top: 2px;
}

.role-pill {
  font-size: 10px;
  padding: 4px 10px;
  border-radius: var(--radius-full);
  background: var(--accent-light);
  color: var(--accent);
  border: 1px solid rgba(99, 102, 241, 0.2);
}

.admin-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.card-header {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  font-size: var(--text-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.small-action-btn {
  font-size: 11px;
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  background-color: var(--accent);
  color: #ffffff;
}

.small-action-btn:hover {
  background-color: var(--accent-hover);
}

.editor-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-xs);
}

.editor-table th {
  padding: 8px 16px;
  font-size: 11px;
  color: var(--text-muted);
  background-color: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  text-align: left;
}

.editor-table td {
  padding: 10px 16px;
  border-bottom: 1px solid var(--border-subtle);
  color: var(--text-secondary);
}

.user-meta-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.avatar-circle {
  width: 26px;
  height: 26px;
  border-radius: var(--radius-sm);
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 600;
  color: var(--text-primary);
}

.user-name {
  font-size: var(--text-xs);
  font-weight: var(--font-weight-medium);
  color: var(--text-primary);
}

.user-email {
  font-size: 10px;
  color: var(--text-muted);
}

.role-chip {
  font-size: 10px;
  font-family: var(--font-mono);
  padding: 2px 6px;
  border-radius: 3px;
  background-color: var(--bg-tertiary);
  color: var(--text-secondary);
}

.role-chip.admin, .role-chip.super\ admin {
  background-color: var(--accent-light);
  color: var(--accent);
}

.status-indicator {
  font-size: 10px;
  font-family: var(--font-mono);
  color: var(--danger);
}

.status-indicator.mfa-on {
  color: var(--success);
}

.table-btn {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}

.table-btn:hover {
  color: var(--text-primary);
  border-color: var(--border-highlight);
}

.config-code-box {
  background-color: var(--bg-input);
  border-top: 1px solid var(--border-subtle);
}

.box-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 12px;
  background-color: var(--bg-tertiary);
  font-size: 11px;
  color: var(--text-muted);
  border-bottom: 1px solid var(--border-subtle);
}

.badge {
  font-size: 9px;
  color: var(--success);
}

.config-code-box pre {
  padding: 12px;
  font-size: 11px;
  color: #79c0ff;
  line-height: 1.5;
}

.model-quota-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
  padding: 14px;
}

.quota-box {
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.quota-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.model-title {
  font-size: var(--text-xs);
  font-weight: var(--font-weight-medium);
  color: var(--text-primary);
}

.quota-val {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.quota-sub {
  font-size: 10px;
}

.settings-form {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-row label {
  font-size: var(--text-xs);
  color: var(--text-muted);
}

.form-row input, .form-row select {
  font-size: var(--text-xs);
  padding: 7px 10px;
  max-width: 440px;
}

.text-right {
  text-align: right;
}
</style>
