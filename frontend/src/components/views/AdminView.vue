<template>
  <div class="admin-view">
    <!-- Header -->
    <div class="view-header">
      <div class="header-titles">
        <div class="admin-shield-badge">
          <Icon name="shield" :size="12" />
          <span>ADMINISTRATION CONSOLE</span>
        </div>
        <h1 class="view-title">{{ currentTitle }}</h1>
        <p class="view-subtitle">{{ currentDescription }}</p>
      </div>

      <div class="header-actions-group">
        <span
          class="role-pill font-mono"
          :class="{ 'is-admin': authStore.isAdmin }"
        >
          {{ authStore.isAdmin ? 'Role: ADMIN (Full Privileges)' : 'Role: USER (Admin Locked)' }}
        </span>
      </div>
    </div>

    <!-- Notification Toast -->
    <div v-if="toastMessage" class="admin-toast font-mono" :class="toastType">
      <span>{{ toastMessage }}</span>
    </div>

    <!-- Unlocked Admin Panels -->
    <template v-if="authStore.isAdmin">
    <!-- ========================================================================= -->
    <!-- PANEL 1: SCHEMA MANAGER -->
    <!-- ========================================================================= -->
    <div v-if="uiStore.activeNav === 'admin-schema'" class="admin-panel">
      <div class="admin-card">
        <div class="card-header">
          <div class="card-title-group">
            <h3 class="card-title">Database Tables & Semantic Dictionary</h3>
            <span class="badge font-mono">{{ schemaTables.length }} PostgreSQL Tables</span>
          </div>
          <button class="small-action-btn font-mono" @click="fetchSchema">
            Refresh Schema
          </button>
        </div>

        <div v-if="loadingSchema" class="loading-state font-mono">
          Loading PostgreSQL schema metadata...
        </div>

        <div v-else class="tables-accordion">
          <div
            v-for="table in schemaTables"
            :key="table.name"
            class="table-accordion-item"
            :class="{ 'is-open': expandedTables[table.name] }"
          >
            <div class="table-accordion-header" @click="toggleTable(table.name)">
              <div class="table-name-group font-mono">
                <Icon :name="expandedTables[table.name] ? 'chevron-down' : 'chevron-right'" :size="12" />
                <span class="table-sql-name">{{ table.name }}</span>
                <span class="table-row-tag">{{ table.row_count.toLocaleString() }} rows</span>
              </div>
              <span class="column-count-tag font-mono">{{ table.columns.length }} columns</span>
            </div>

            <div v-if="expandedTables[table.name]" class="table-accordion-body">
              <table class="editor-table font-mono">
                <thead>
                  <tr>
                    <th>Column Name</th>
                    <th>Type</th>
                    <th>Human-Readable Description</th>
                    <th>Synonyms & Aliases</th>
                    <th>Sensitive (Mask)</th>
                    <th class="text-right">Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="col in table.columns" :key="col.column_name">
                    <td class="col-name-cell">
                      <span class="col-pill">{{ col.column_name }}</span>
                    </td>
                    <td class="text-muted">{{ col.data_type }}</td>
                    <td>
                      <input
                        v-model="col.description"
                        class="table-inline-input"
                        placeholder="Add column description..."
                      />
                    </td>
                    <td>
                      <input
                        v-model="col.synonyms"
                        class="table-inline-input"
                        placeholder="synonyms, aliases..."
                      />
                    </td>
                    <td>
                      <label class="toggle-switch">
                        <input
                          type="checkbox"
                          v-model="col.is_sensitive"
                        />
                        <span class="toggle-slider"></span>
                        <span class="toggle-label">{{ col.is_sensitive ? 'PII / Masked' : 'Normal' }}</span>
                      </label>
                    </td>
                    <td class="text-right">
                      <button class="save-row-btn" @click="saveColumnMeta(table.name, col)">
                        Save
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- PANEL 2: EXAMPLES MANAGER (QDRANT VECTOR STORE) -->
    <!-- ========================================================================= -->
    <div v-else-if="uiStore.activeNav === 'admin-examples'" class="admin-panel">
      <div class="admin-card">
        <div class="card-header">
          <div class="card-title-group">
            <h3 class="card-title">Curated Few-Shot Library (Qdrant Vector DB)</h3>
            <span class="badge font-mono">{{ examplesList.length }} Few-Shot Pairs</span>
          </div>
          <div class="header-buttons-row">
            <button class="small-action-btn primary font-mono" @click="showAddExampleModal = true">
              + Add Example
            </button>
          </div>
        </div>

        <!-- Semantic Search & Query Type Filter Bar -->
        <div class="examples-filter-bar">
          <div class="search-box-wrapper font-mono">
            <Icon name="search" :size="13" />
            <input
              v-model="examplesSearchQuery"
              @input="onSearchExamples"
              placeholder="Semantic vector search across few-shot queries (Qdrant)..."
              class="examples-search-input"
            />
          </div>

          <div class="filter-pills-row font-mono">
            <button
              v-for="qt in ['ALL', 'SELECT_SIMPLE', 'SELECT_AGGREGATE', 'SELECT_JOIN', 'SELECT_TEMPORAL']"
              :key="qt"
              class="filter-type-pill"
              :class="{ 'active': selectedQueryTypeFilter === qt }"
              @click="filterExamplesByType(qt)"
            >
              {{ qt }}
            </button>
          </div>
        </div>

        <!-- Add/Edit Example Modal / Inline Drawer -->
        <div v-if="showAddExampleModal" class="add-example-card">
          <div class="card-header-inner font-mono">
            <span>{{ newExample.id ? 'Edit Few-Shot Example' : 'Add New Few-Shot Example to Qdrant' }}</span>
            <button class="close-card-btn" @click="showAddExampleModal = false">✕</button>
          </div>
          <div class="example-form-grid">
            <div class="form-group">
              <label class="font-mono">User Question (Natural Language)</label>
              <input
                v-model="newExample.question"
                placeholder="e.g. Which subscriptions renew in the next 30 days?"
                class="form-input font-mono"
              />
            </div>
            <div class="form-group">
              <label class="font-mono">Query Type Classification</label>
              <select v-model="newExample.query_type" class="form-input font-mono">
                <option value="SELECT_SIMPLE">SELECT_SIMPLE</option>
                <option value="SELECT_AGGREGATE">SELECT_AGGREGATE</option>
                <option value="SELECT_JOIN">SELECT_JOIN</option>
                <option value="SELECT_TEMPORAL">SELECT_TEMPORAL</option>
              </select>
            </div>
            <div class="form-group full-width">
              <label class="font-mono">Ground-Truth PostgreSQL Statement</label>
              <textarea
                v-model="newExample.sql"
                rows="3"
                placeholder="SELECT ... FROM ...;"
                class="form-input font-mono sql-textarea"
              ></textarea>
            </div>
            <div class="form-group full-width">
              <label class="font-mono">Explanation / Semantic Notes</label>
              <input
                v-model="newExample.explanation"
                placeholder="Brief explanation for prompt context..."
                class="form-input font-mono"
              />
            </div>
          </div>
          <div class="form-actions-row">
            <button class="small-action-btn font-mono" @click="showAddExampleModal = false">Cancel</button>
            <button class="small-action-btn primary font-mono" @click="saveNewExample">Save & Index in Qdrant</button>
          </div>
        </div>

        <!-- Examples List Cards -->
        <div class="examples-list-grid">
          <div v-for="ex in filteredExamples" :key="ex.id" class="example-item-card">
            <div class="example-card-head">
              <div class="head-left">
                <span class="ex-id-tag font-mono">#{{ ex.id }}</span>
                <span class="ex-type-pill font-mono" :class="ex.query_type.toLowerCase()">
                  {{ ex.query_type }}
                </span>
                <span v-if="ex.score" class="qdrant-score-tag font-mono">
                  Similarity: {{ (ex.score * 100).toFixed(1) }}%
                </span>
              </div>
              <button class="delete-icon-btn" @click="removeExample(ex.id)" title="Delete from Qdrant">
                <Icon name="trash" :size="12" />
              </button>
            </div>

            <div class="example-question">
              "{{ ex.question }}"
            </div>

            <div class="example-sql-box font-mono">
              <code>{{ ex.sql }}</code>
            </div>

            <div v-if="ex.explanation" class="example-explanation text-muted">
              {{ ex.explanation }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- PANEL 3: QUERY LOGS & AUDIT TRAIL -->
    <!-- ========================================================================= -->
    <div v-else-if="uiStore.activeNav === 'admin-logs'" class="admin-panel">
      <div class="admin-card">
        <div class="card-header">
          <div class="card-title-group">
            <h3 class="card-title">Query Execution & Safety Logs</h3>
            <span class="badge font-mono">{{ queryLogs.length }} Records</span>
          </div>
          <div class="header-buttons-row">
            <button class="small-action-btn font-mono" @click="exportLogsCSV">
              Export CSV
            </button>
            <button class="small-action-btn danger font-mono" @click="clearAllLogs">
              Clear Logs
            </button>
          </div>
        </div>

        <!-- Filter bar -->
        <div class="logs-filter-bar font-mono">
          <div class="search-box-wrapper font-mono">
            <Icon name="search" :size="13" />
            <input
              v-model="logsSearchQuery"
              @input="fetchLogs"
              placeholder="Filter by question, SQL snippet, or user..."
              class="examples-search-input"
            />
          </div>
          <select v-model="selectedLogsStatus" @change="fetchLogs" class="filter-select font-mono">
            <option value="">All Statuses</option>
            <option value="success">Success</option>
            <option value="blocked">Blocked (Guardrail)</option>
            <option value="error">Execution Error</option>
          </select>
        </div>

        <div class="table-responsive">
          <table class="editor-table font-mono">
            <thead>
              <tr>
                <th>Status</th>
                <th>Query Intent</th>
                <th>User Question</th>
                <th>Generated SQL</th>
                <th>Rows</th>
                <th>Latency</th>
                <th>Model</th>
                <th>Time</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="log in queryLogs" :key="log.id">
                <td>
                  <span class="status-indicator" :class="log.status">
                    {{ log.status }}
                  </span>
                </td>
                <td>
                  <span class="query-type-tag">{{ log.query_type || 'N/A' }}</span>
                </td>
                <td class="log-query-cell" :title="log.query_text">
                  {{ log.query_text }}
                </td>
                <td class="log-sql-cell" :title="log.generated_sql || log.error_message">
                  <code>{{ log.generated_sql || log.error_message }}</code>
                </td>
                <td class="text-muted">{{ log.row_count }}</td>
                <td class="latency-cell">{{ log.latency_ms }}ms</td>
                <td class="text-muted">{{ formatModelShort(log.model_used) }}</td>
                <td class="text-muted">{{ formatTimestamp(log.created_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- PANEL 4: GUARDRAILS CONFIGURATION -->
    <!-- ========================================================================= -->
    <div v-else-if="uiStore.activeNav === 'admin-guardrails'" class="admin-panel">
      <div class="admin-card">
        <div class="card-header">
          <div class="card-title-group">
            <h3 class="card-title">SQL Guardrails & AST Safety Enforcement</h3>
            <span class="status-live font-mono">100% Policy Enforced</span>
          </div>
          <button class="small-action-btn primary font-mono" @click="saveGuardrailsConfig">
            Save Guardrails
          </button>
        </div>

        <div class="guardrails-body">
          <!-- Blocked operations tags -->
          <div class="guard-section">
            <h4 class="guard-section-title font-mono">Prohibited Operations (AST Check)</h4>
            <p class="guard-desc">
              Any query containing these statements is automatically intercepted and rejected before execution.
            </p>
            <div class="operations-tag-cloud font-mono">
              <span
                v-for="op in allPossibleOperations"
                :key="op"
                class="op-tag"
                :class="{ 'blocked': guardrails.blocked_operations.includes(op) }"
                @click="toggleOperation(op)"
              >
                {{ op }} {{ guardrails.blocked_operations.includes(op) ? '✕ BLOCKED' : '✓ ALLOWED' }}
              </span>
            </div>
          </div>

          <!-- Limits & Toggles -->
          <div class="guard-form-grid">
            <div class="guard-form-box">
              <label class="font-mono">Default Row Return Limit</label>
              <input
                type="number"
                v-model.number="guardrails.default_row_limit"
                class="form-input font-mono"
              />
              <span class="sub-hint">Automatically appended to queries without explicit LIMIT.</span>
            </div>

            <div class="guard-form-box">
              <label class="font-mono">Maximum Row Hard Cap</label>
              <input
                type="number"
                v-model.number="guardrails.max_row_limit"
                class="form-input font-mono"
              />
              <span class="sub-hint">Upper ceiling on rows returned to prevent client memory overload.</span>
            </div>
          </div>

          <!-- Permitted Tables Checklist -->
          <div class="guard-section">
            <h4 class="guard-section-title font-mono">Permitted Schema Tables (Whitelist)</h4>
            <div class="tables-checkbox-grid font-mono">
              <label v-for="tbl in validTablesList" :key="tbl" class="table-chk-label">
                <input
                  type="checkbox"
                  :value="tbl"
                  v-model="guardrails.allowed_tables"
                />
                <span>{{ tbl }}</span>
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- PANEL 5: MODEL CONFIG & SETTINGS -->
    <!-- ========================================================================= -->
    <div v-else class="admin-panel">
      <!-- 1. AI Model Selection & Default for Users -->
      <div class="admin-card">
        <div class="card-header">
          <div class="card-title-group">
            <h3 class="card-title">LLM Provider Routing & User Defaults</h3>
            <span class="status-live font-mono">Groq & Google Active</span>
          </div>
          <button class="small-action-btn primary font-mono" @click="saveModelConfig">
            Save Model Settings
          </button>
        </div>

        <div class="model-settings-body">
          <div class="model-choice-cards">
            <!-- Groq 120B -->
            <div
              class="model-option-card"
              :class="{ 'is-default': modelConfig.default_model === 'openai/gpt-oss-120b' }"
              @click="modelConfig.default_model = 'openai/gpt-oss-120b'"
            >
              <div class="model-card-top">
                <span class="provider-pill groq font-mono">GROQ CLOUD</span>
                <span v-if="modelConfig.default_model === 'openai/gpt-oss-120b'" class="default-badge font-mono">
                  ★ Default
                </span>
              </div>
              <div class="model-name">Groq · GPT-OSS 120B</div>
              <div class="model-specs font-mono text-muted">
                Context: 128K tokens • Speed: Ultra-Fast
              </div>
              <label class="user-allow-label" @click.stop>
                <input
                  type="checkbox"
                  value="openai/gpt-oss-120b"
                  v-model="modelConfig.allowed_models_for_users"
                />
                <span class="font-mono">Allow for Users</span>
              </label>
            </div>

            <!-- Groq 20B -->
            <div
              class="model-option-card"
              :class="{ 'is-default': modelConfig.default_model === 'openai/gpt-oss-20b' }"
              @click="modelConfig.default_model = 'openai/gpt-oss-20b'"
            >
              <div class="model-card-top">
                <span class="provider-pill groq font-mono">GROQ CLOUD</span>
                <span v-if="modelConfig.default_model === 'openai/gpt-oss-20b'" class="default-badge font-mono">
                  ★ Default
                </span>
              </div>
              <div class="model-name">Groq · GPT-OSS 20B</div>
              <div class="model-specs font-mono text-muted">
                Context: 64K tokens • Speed: Hyper-Fast
              </div>
              <label class="user-allow-label" @click.stop>
                <input
                  type="checkbox"
                  value="openai/gpt-oss-20b"
                  v-model="modelConfig.allowed_models_for_users"
                />
                <span class="font-mono">Allow for Users</span>
              </label>
            </div>

            <!-- Google Gemini 3.1 Flash Lite -->
            <div
              class="model-option-card"
              :class="{ 'is-default': modelConfig.default_model === 'gemini-3.1-flash-lite' }"
              @click="modelConfig.default_model = 'gemini-3.1-flash-lite'"
            >
              <div class="model-card-top">
                <span class="provider-pill google font-mono">GOOGLE DEEPMIND</span>
                <span v-if="modelConfig.default_model === 'gemini-3.1-flash-lite'" class="default-badge font-mono">
                  ★ Default
                </span>
              </div>
              <div class="model-name">Google · Gemini 3.1 Flash Lite</div>
              <div class="model-specs font-mono text-muted">
                Context: 1M tokens • Speed: Sub-Second
              </div>
              <label class="user-allow-label" @click.stop>
                <input
                  type="checkbox"
                  value="gemini-3.1-flash-lite"
                  v-model="modelConfig.allowed_models_for_users"
                />
                <span class="font-mono">Allow for Users</span>
              </label>
            </div>

            <!-- Google Gemma 4 26B -->
            <div
              class="model-option-card"
              :class="{ 'is-default': modelConfig.default_model === 'gemma-4-26b-a4b-it' }"
              @click="modelConfig.default_model = 'gemma-4-26b-a4b-it'"
            >
              <div class="model-card-top">
                <span class="provider-pill google font-mono">GOOGLE DEEPMIND</span>
                <span v-if="modelConfig.default_model === 'gemma-4-26b-a4b-it'" class="default-badge font-mono">
                  ★ Default
                </span>
              </div>
              <div class="model-name">Google · Gemma 4 26B A4B IT</div>
              <div class="model-specs font-mono text-muted">
                Context: 128K tokens • Speed: Fast
              </div>
              <label class="user-allow-label" @click.stop>
                <input
                  type="checkbox"
                  value="gemma-4-26b-a4b-it"
                  v-model="modelConfig.allowed_models_for_users"
                />
                <span class="font-mono">Allow for Users</span>
              </label>
            </div>
          </div>

          <!-- Admin Model Enforcement Option -->
          <div class="enforce-banner">
            <label class="enforce-chk">
              <input
                type="checkbox"
                v-model="isModelEnforced"
              />
              <span class="font-mono">
                <strong>Admin Enforcement:</strong> Lock all standard workspace users to the Default Model (disables user model switching)
              </span>
            </label>
          </div>

          <!-- Database & Hyperparameters -->
          <div class="settings-form-grid font-mono">
            <div class="form-row">
              <label>Database Engine</label>
              <div class="fixed-engine-pill">
                <Icon name="database" :size="13" />
                <span>PostgreSQL (Dedicated)</span>
              </div>
            </div>

            <div class="form-row">
              <label>Model Temperature: {{ modelConfig.temperature }}</label>
              <input
                type="range"
                min="0.0"
                max="0.8"
                step="0.05"
                v-model.number="modelConfig.temperature"
                class="slider-input"
              />
            </div>

            <div class="form-row">
              <label>Max Output Token Budget</label>
              <input
                type="number"
                v-model.number="modelConfig.max_tokens"
                class="form-input"
              />
            </div>
          </div>

          <!-- API Credentials Configuration -->
          <div class="api-keys-box font-mono">
            <h4 class="guard-section-title">API Key Configuration (Optional for Live External Model Invocations)</h4>
            <div class="keys-grid">
              <div class="form-row">
                <label class="key-label-row">
                  <span>GROQ_API_KEY</span>
                  <span v-if="groqApiKeySet" class="key-status-badge configured">● Configured</span>
                  <span v-else class="key-status-badge missing">Not Configured</span>
                </label>
                <input
                  type="password"
                  v-model="groqApiKeyInput"
                  :placeholder="groqApiKeySet ? 'Enter new key to update...' : 'gsk_...'"
                  class="form-input"
                />
              </div>
              <div class="form-row">
                <label class="key-label-row">
                  <span>GEMINI_API_KEY</span>
                  <span v-if="geminiApiKeySet" class="key-status-badge configured">● Configured</span>
                  <span v-else class="key-status-badge missing">Not Configured</span>
                </label>
                <input
                  type="password"
                  v-model="geminiApiKeyInput"
                  :placeholder="geminiApiKeySet ? 'Enter new key to update...' : 'AIzaSy...'"
                  class="form-input"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 2. Evaluation Harness Benchmark Card -->
      <div class="admin-card">
        <div class="card-header">
          <div class="card-title-group">
            <h3 class="card-title">SQL Evaluation Benchmark Harness (25 Ground-Truth Queries)</h3>
            <span class="badge font-mono">Automated Test Suite</span>
          </div>
          <button
            class="small-action-btn primary font-mono"
            :disabled="isRunningEval"
            @click="runEvaluationBenchmark"
          >
            <Icon name="play" :size="12" />
            <span>{{ isRunningEval ? 'Running Benchmark (25 queries)...' : 'Run 25-Query Eval Harness' }}</span>
          </button>
        </div>

        <div v-if="isRunningEval" class="eval-loading-state font-mono">
          <div class="status-pulse-dot"></div>
          <span>Executing 25-query benchmark against live LangGraph pipeline &amp; PostgreSQL... (~15-20s)</span>
        </div>

        <div v-if="evalReport" class="eval-results-container">
          <div class="eval-metrics-grid font-mono">
            <div class="eval-metric-box">
              <span class="m-label">Execution Accuracy</span>
              <span class="m-val" :class="{ 'pass': evalReport.summary.execution_accuracy_pct >= 50 }">
                {{ evalReport.summary.execution_accuracy_pct }}%
              </span>
              <span class="m-sub">Target: ≥ 50%</span>
            </div>

            <div class="eval-metric-box">
              <span class="m-label">Exact Match Rate</span>
              <span class="m-val">{{ evalReport.summary.exact_match_pct }}%</span>
              <span class="m-sub">sqlglot diff check</span>
            </div>

            <div class="eval-metric-box">
              <span class="m-label">Guardrails Compliance</span>
              <span class="m-val pass">{{ evalReport.summary.guardrails_compliance_pct }}%</span>
              <span class="m-sub">100% Destructive Blocked</span>
            </div>

            <div class="eval-metric-box">
              <span class="m-label">Overall Weighted Score</span>
              <span class="m-val highlight">{{ evalReport.summary.overall_weighted_score }}%</span>
              <span class="m-sub">Threshold: 65% (PASS)</span>
            </div>
          </div>

          <!-- Breakdown per Query Type -->
          <div class="type-breakdown-card font-mono">
            <h4 class="guard-section-title">Accuracy Breakdown by Query Type:</h4>
            <div class="breakdown-pills">
              <span v-for="(v, k) in evalReport.per_type_breakdown" :key="k" class="type-result-pill">
                <strong>{{ k }}:</strong> {{ v.passed }}/{{ v.total }} ({{ v.accuracy_pct }}%)
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
    </template>

    <!-- Access Denied Card (Shown when standard user accesses admin views) -->
    <div v-else class="access-denied-container">
      <div class="access-denied-card">
        <div class="denied-icon-wrap">
          <Icon name="lock" :size="38" class="denied-lock-icon" />
        </div>
        <h2 class="denied-title">Administrator Authentication Required</h2>
        <p class="denied-desc">
          The Administration Console provides privileged management over the PostgreSQL database schema dictionary,
          few-shot vector embeddings stored in Qdrant, query execution audit trails, AST guardrails, and LLM model orchestration settings.
          Only authenticated users with the <span class="admin-tag font-mono">admin</span> role may access these controls.
        </p>

        <div class="denied-actions">
          <button class="primary-login-btn" @click="authStore.openLoginModal()">
            <Icon name="shield" :size="15" />
            <span>Sign In as Administrator</span>
          </button>
          <button class="secondary-return-btn" @click="uiStore.setActiveNav('dashboard')">
            <span>Return to Dashboard</span>
          </button>
        </div>

        <div class="denied-demo-box font-mono">
          <div class="demo-box-label">Evaluation Demo Credentials:</div>
          <div class="demo-cred-row">
            <span>Admin: <code>admin@subscriptiq.ai</code> / <code>admin123</code></span>
          </div>
          <div class="demo-cred-row">
            <span>Standard User: <code>user@subscriptiq.ai</code> / <code>user123</code></span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useUIStore } from '@/stores/ui'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import Icon from '@/components/common/Icon.vue'

const uiStore = useUIStore()
const authStore = useAuthStore()
const chatStore = useChatStore()

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

const toastMessage = ref('')
const toastType = ref('success')

function showToast(msg, type = 'success') {
  uiStore.showToast(msg, type)
  toastMessage.value = msg
  toastType.value = type
  setTimeout(() => {
    toastMessage.value = ''
  }, 3500)
}

const currentTitle = computed(() => {
  switch (uiStore.activeNav) {
    case 'admin-schema': return 'Schema Manager & Data Dictionary'
    case 'admin-examples': return 'Curated Few-Shot Examples (Qdrant)'
    case 'admin-logs': return 'Query Execution Audit Logs'
    case 'admin-guardrails': return 'SQL Guardrails & Security Policies'
    case 'admin-models': return 'Model Configuration & Evaluation Harness'
    default: return 'Administration Console'
  }
})

const currentDescription = computed(() => {
  switch (uiStore.activeNav) {
    case 'admin-schema': return 'Browse tables, customize column descriptions, and flag sensitive PII columns.'
    case 'admin-examples': return 'Semantic vector retrieval across few-shot queries stored in Qdrant.'
    case 'admin-logs': return 'Audit trail of natural language questions, generated SQL, latency, and status.'
    case 'admin-guardrails': return 'AST parsing rules to reject destructive operations and enforce row limits.'
    case 'admin-models': return 'Configure Groq and Google AI models, set user defaults, and run the 25-query evaluation benchmark.'
    default: return 'Production Text-to-SQL management console.'
  }
})

// ==========================================
// 1. Schema Manager
// ==========================================
const schemaTables = ref([])
const loadingSchema = ref(false)
const expandedTables = ref({ subscriptions: true, license_allocations: true })

async function fetchSchema() {
  if (!authStore.isAdmin) return
  loadingSchema.value = true
  try {
    const res = await fetch(`${API_BASE}/admin/schema`, {
      headers: authStore.getAuthHeaders()
    })
    if (res.status === 403 || res.status === 401) {
      showToast('Admin authorization required to access schema.', 'error')
      return
    }
    if (res.ok) {
      const data = await res.json()
      schemaTables.value = data.tables || []
    }
  } catch (err) {
    showToast('Could not load schema from backend: ' + err.message, 'error')
  } finally {
    loadingSchema.value = false
  }
}

function toggleTable(tblName) {
  expandedTables.value[tblName] = !expandedTables.value[tblName]
}

async function saveColumnMeta(tableName, col) {
  try {
    const res = await fetch(`${API_BASE}/admin/schema/column`, {
      method: 'POST',
      headers: authStore.getAuthHeaders(),
      body: JSON.stringify({
        table_name: tableName,
        column_name: col.column_name,
        description: col.description,
        is_sensitive: col.is_sensitive,
        synonyms: col.synonyms
      })
    })
    if (res.status === 403) {
      showToast('Admin access required to edit schema metadata.', 'error')
      return
    }
    if (res.ok) {
      showToast(`Saved metadata for ${tableName}.${col.column_name}`)
    }
  } catch (err) {
    showToast('Failed to save column metadata: ' + err.message, 'error')
  }
}

// ==========================================
// 2. Examples Manager (Qdrant)
// ==========================================
const examplesList = ref([])
const examplesSearchQuery = ref('')
const selectedQueryTypeFilter = ref('ALL')
const showAddExampleModal = ref(false)

const newExample = ref({
  question: '',
  sql: '',
  query_type: 'SELECT_SIMPLE',
  explanation: ''
})

async function fetchExamples(search = null, queryType = null) {
  if (!authStore.isAdmin) return
  try {
    let url = `${API_BASE}/admin/examples`
    const params = []
    if (search) params.push(`search=${encodeURIComponent(search)}`)
    if (queryType && queryType !== 'ALL') params.push(`query_type=${queryType}`)
    if (params.length) url += '?' + params.join('&')

    const res = await fetch(url, { headers: authStore.getAuthHeaders() })
    if (res.ok) {
      const data = await res.json()
      examplesList.value = data.examples || []
    }
  } catch (err) {
    console.warn('Examples fetch notice:', err)
  }
}

let searchDebounce = null
function onSearchExamples() {
  clearTimeout(searchDebounce)
  searchDebounce = setTimeout(() => {
    fetchExamples(examplesSearchQuery.value, selectedQueryTypeFilter.value)
  }, 250)
}

function filterExamplesByType(qt) {
  selectedQueryTypeFilter.value = qt
  fetchExamples(examplesSearchQuery.value, qt)
}

const filteredExamples = computed(() => examplesList.value)

async function saveNewExample() {
  if (!newExample.value.question || !newExample.value.sql) {
    showToast('Question and SQL statement are required.', 'error')
    return
  }
  try {
    const res = await fetch(`${API_BASE}/admin/examples`, {
      method: 'POST',
      headers: authStore.getAuthHeaders(),
      body: JSON.stringify(newExample.value)
    })
    if (res.status === 403) {
      showToast('Admin privilege required to add few-shot examples.', 'error')
      return
    }
    if (res.ok) {
      showToast('Example indexed into Qdrant vector database!')
      showAddExampleModal.value = false
      newExample.value = { question: '', sql: '', query_type: 'SELECT_SIMPLE', explanation: '' }
      fetchExamples()
    }
  } catch (err) {
    showToast('Error saving example: ' + err.message, 'error')
  }
}

async function removeExample(id) {
  const confirmed = await uiStore.openConfirmModal({
    title: 'Remove Few-Shot Example',
    message: `Remove few-shot training example #${id} from Qdrant?`,
    subMessage: 'This query-SQL training pair will be permanently removed from vector semantic search.',
    confirmText: 'Remove Example',
    cancelText: 'Cancel',
    type: 'danger',
    icon: 'trash'
  })
  if (!confirmed) return

  try {
    const res = await fetch(`${API_BASE}/admin/examples/${id}`, {
      method: 'DELETE',
      headers: authStore.getAuthHeaders()
    })
    if (res.ok) {
      showToast(`Example #${id} removed from Qdrant.`, 'success')
      fetchExamples()
    }
  } catch (err) {
    showToast('Error removing example: ' + err.message, 'error')
  }
}

// ==========================================
// 3. Query Logs
// ==========================================
const queryLogs = ref([])
const logsSearchQuery = ref('')
const selectedLogsStatus = ref('')

async function fetchLogs() {
  if (!authStore.isAdmin) return
  try {
    let url = `${API_BASE}/admin/logs?limit=50`
    if (selectedLogsStatus.value) url += `&status=${selectedLogsStatus.value}`
    if (logsSearchQuery.value) url += `&search=${encodeURIComponent(logsSearchQuery.value)}`

    const res = await fetch(url, { headers: authStore.getAuthHeaders() })
    if (res.ok) {
      const data = await res.json()
      queryLogs.value = data.logs || []
    }
  } catch (err) {
    console.warn('Logs fetch notice:', err)
  }
}

async function clearAllLogs() {
  const confirmed = await uiStore.openConfirmModal({
    title: 'Clear Audit Logs',
    message: 'Are you sure you want to clear all audit logs from the database?',
    subMessage: 'This will permanently remove all logged SQL queries, latency metrics, and user audit trails. This action cannot be undone.',
    confirmText: 'Clear All Logs',
    cancelText: 'Cancel',
    type: 'danger',
    icon: 'trash'
  })
  if (!confirmed) return

  try {
    const res = await fetch(`${API_BASE}/admin/logs`, {
      method: 'DELETE',
      headers: authStore.getAuthHeaders()
    })
    if (res.ok) {
      showToast('Query audit logs cleared successfully.', 'success')
      fetchLogs()
    }
  } catch (err) {
    showToast('Failed to clear logs: ' + err.message, 'error')
  }
}

async function exportLogsCSV() {
  try {
    const res = await fetch(`${API_BASE}/admin/logs/export`, {
      headers: authStore.getAuthHeaders()
    })
    if (!res.ok) throw new Error('Unauthorized or failed to export')
    const blob = await res.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `subscriptiq_query_logs_${new Date().toISOString().slice(0, 10)}.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  } catch (err) {
    showToast('Failed to export CSV: ' + err.message, 'error')
  }
}

function formatModelShort(modelStr) {
  if (!modelStr) return 'default'
  if (modelStr.includes('120b')) return 'Groq 120B'
  if (modelStr.includes('20b')) return 'Groq 20B'
  if (modelStr.includes('flash')) return 'Gemini Flash'
  if (modelStr.includes('gemma')) return 'Gemma 26B'
  return modelStr.split('/').pop()
}

function formatTimestamp(ts) {
  if (!ts) return ''
  try {
    const d = new Date(ts)
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } catch {
    return ts
  }
}

// ==========================================
// 4. Guardrails Config
// ==========================================
const allPossibleOperations = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'TRUNCATE', 'ALTER', 'GRANT', 'REVOKE', 'CREATE']
const validTablesList = [
  'organizations', 'departments', 'users', 'vendors',
  'subscriptions', 'license_allocations', 'invoices',
  'usage_telemetry', 'optimization_recommendations'
]

const guardrails = ref({
  blocked_operations: ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'TRUNCATE', 'ALTER', 'GRANT', 'REVOKE', 'CREATE'],
  allow_dml_override: false,
  default_row_limit: 50,
  max_row_limit: 500,
  enforce_row_limit: true,
  allowed_tables: [...validTablesList]
})

async function fetchGuardrailsConfig() {
  if (!authStore.isAdmin) return
  try {
    const res = await fetch(`${API_BASE}/admin/guardrails`, {
      headers: authStore.getAuthHeaders()
    })
    if (res.ok) {
      const data = await res.json()
      guardrails.value = { ...guardrails.value, ...data }
    }
  } catch (err) {
    console.warn('Guardrails fetch notice:', err)
  }
}

function toggleOperation(op) {
  const idx = guardrails.value.blocked_operations.indexOf(op)
  if (idx !== -1) {
    guardrails.value.blocked_operations.splice(idx, 1)
  } else {
    guardrails.value.blocked_operations.push(op)
  }
}

async function saveGuardrailsConfig() {
  try {
    const res = await fetch(`${API_BASE}/admin/guardrails`, {
      method: 'POST',
      headers: authStore.getAuthHeaders(),
      body: JSON.stringify(guardrails.value)
    })
    if (res.status === 403) {
      showToast('Admin privilege required to modify guardrails.', 'error')
      return
    }
    if (res.ok) {
      showToast('Guardrails configuration saved & active!')
    }
  } catch (err) {
    showToast('Failed to save guardrails: ' + err.message, 'error')
  }
}

// ==========================================
// 5. Model Config & Evaluation Benchmark
// ==========================================
const modelConfig = ref({
  default_model: 'openai/gpt-oss-120b',
  allowed_models_for_users: [
    'openai/gpt-oss-120b',
    'openai/gpt-oss-20b',
    'gemini-3.1-flash-lite',
    'gemma-4-26b-a4b-it'
  ],
  admin_enforced_model: null,
  temperature: 0.1,
  max_tokens: 1024
})

const isModelEnforced = ref(false)
const groqApiKeyInput = ref('')
const geminiApiKeyInput = ref('')
const groqApiKeySet = ref(false)
const geminiApiKeySet = ref(false)

async function fetchModelConfig() {
  if (!authStore.isAdmin) return
  try {
    const res = await fetch(`${API_BASE}/admin/config`, {
      headers: authStore.getAuthHeaders()
    })
    if (res.ok) {
      const data = await res.json()
      modelConfig.value = {
        default_model: data.default_model || 'openai/gpt-oss-120b',
        allowed_models_for_users: data.allowed_models_for_users || [],
        admin_enforced_model: data.admin_enforced_model || null,
        temperature: data.temperature || 0.1,
        max_tokens: data.max_tokens || 1024
      }
      isModelEnforced.value = Boolean(data.admin_enforced_model)
      groqApiKeySet.value = Boolean(data.groq_api_key_set)
      geminiApiKeySet.value = Boolean(data.gemini_api_key_set)
    }
  } catch (err) {
    console.warn('Model config fetch notice:', err)
  }
}

async function saveModelConfig() {
  try {
    // Ensure allowed_models_for_users has at least default_model
    if (!modelConfig.value.allowed_models_for_users || modelConfig.value.allowed_models_for_users.length === 0) {
      modelConfig.value.allowed_models_for_users = [modelConfig.value.default_model]
    }
    // Ensure default_model is among the allowed models
    if (!modelConfig.value.allowed_models_for_users.includes(modelConfig.value.default_model)) {
      modelConfig.value.default_model = modelConfig.value.allowed_models_for_users[0]
    }

    const payload = {
      ...modelConfig.value,
      admin_enforced_model: isModelEnforced.value ? modelConfig.value.default_model : null,
      groq_api_key: groqApiKeyInput.value || null,
      gemini_api_key: geminiApiKeyInput.value || null
    }

    const res = await fetch(`${API_BASE}/admin/config`, {
      method: 'POST',
      headers: authStore.getAuthHeaders(),
      body: JSON.stringify(payload)
    })
    if (res.status === 403) {
      showToast('Admin privilege required to update model configuration.', 'error')
      return
    }
    if (res.ok) {
      showToast('Model settings and API keys successfully saved!')
      groqApiKeyInput.value = ''
      geminiApiKeyInput.value = ''
      await fetchModelConfig()
      await chatStore.fetchModels(authStore.user.role)
    }
  } catch (err) {
    showToast('Failed to save model config: ' + err.message, 'error')
  }
}

// Evaluation Benchmark
const isRunningEval = ref(false)
const evalReport = ref(null)

async function runEvaluationBenchmark() {
  isRunningEval.value = true
  evalReport.value = null
  try {
    const selectedModel = modelConfig.value.default_model || 'openai/gpt-oss-120b'
    const res = await fetch(`${API_BASE}/eval?model_id=${encodeURIComponent(selectedModel)}`, {
      method: 'POST',
      headers: authStore.getAuthHeaders(),
      body: JSON.stringify({ model_id: selectedModel })
    })
    if (res.status === 403) {
      showToast('Admin privilege required to execute evaluation harness.', 'error')
      return
    }
    if (res.ok) {
      const data = await res.json()
      evalReport.value = data
      showToast(`Evaluation complete! Score: ${data.summary?.overall_weighted_score}%`)
    } else {
      const errData = await res.json().catch(() => ({}))
      showToast(`Evaluation failed (${res.status}): ${errData.detail || res.statusText || 'Server error'}`, 'error')
    }
  } catch (err) {
    showToast('Evaluation run error: ' + err.message, 'error')
  } finally {
    isRunningEval.value = false
  }
}

function loadAllAdminData() {
  if (!authStore.isAdmin) return
  fetchSchema()
  fetchExamples()
  fetchLogs()
  fetchGuardrailsConfig()
  fetchModelConfig()
}

watch(() => authStore.isAdmin, (isAdm) => {
  if (isAdm) {
    loadAllAdminData()
  }
})

onMounted(() => {
  if (authStore.isAdmin) {
    loadAllAdminData()
  }
})
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
  gap: 6px;
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--accent);
  padding: 3px 8px;
  border-radius: var(--radius-full);
  font-size: 10px;
  font-family: var(--font-mono);
  margin-bottom: 4px;
}

.role-pill {
  font-size: 11px;
  background-color: var(--accent-light);
  color: var(--accent);
  border: 1px solid rgba(var(--accent-rgb), 0.3);
  padding: 4px 10px;
  border-radius: var(--radius-sm);
}

.admin-toast {
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  display: flex;
  align-items: center;
}

.admin-toast.success {
  background-color: var(--success-bg);
  border: 1px solid var(--success);
  color: var(--success);
}

.admin-toast.error {
  background-color: var(--danger-bg);
  border: 1px solid var(--danger);
  color: var(--danger);
}

.admin-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-subtle);
  margin-bottom: 14px;
}

.card-title-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.card-title {
  font-size: var(--text-md);
  font-weight: var(--font-weight-medium);
  color: var(--text-primary);
  margin: 0;
}

.small-action-btn {
  font-size: 11.5px;
  padding: 5px 12px;
  border-radius: var(--radius-sm);
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.small-action-btn:hover {
  background-color: var(--bg-hover);
  border-color: var(--accent);
}

.small-action-btn.primary {
  background: var(--btn-primary-gradient);
  border: 1px solid var(--btn-primary-border);
  color: #ffffff;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(2, 132, 199, 0.3);
}

.small-action-btn.primary:hover:not(:disabled) {
  background: var(--btn-primary-gradient-hover);
  border-color: rgba(56, 189, 248, 0.5);
  box-shadow: 0 4px 12px rgba(2, 132, 199, 0.4);
}

.small-action-btn.danger {
  color: var(--danger);
  border-color: rgba(239, 68, 68, 0.3);
}

/* Schema Manager Accordion */
.tables-accordion {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.table-accordion-item {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  background-color: var(--bg-primary);
  overflow: hidden;
}

.table-accordion-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  cursor: pointer;
  background-color: var(--bg-secondary);
}

.table-accordion-header:hover {
  background-color: var(--bg-tertiary);
}

.table-name-group {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12.5px;
}

.table-sql-name {
  color: var(--accent);
  font-weight: var(--font-weight-medium);
}

.table-row-tag {
  font-size: 10px;
  color: var(--text-muted);
  background-color: var(--bg-app);
  padding: 1px 6px;
  border-radius: 3px;
}

.column-count-tag {
  font-size: 11px;
  color: var(--text-muted);
}

.table-inline-input {
  width: 100%;
  background-color: var(--bg-input);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  padding: 4px 6px;
  border-radius: var(--radius-sm);
  font-size: 11px;
}

.table-inline-input:focus {
  border-color: var(--accent);
  outline: none;
}

.toggle-switch {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-size: 10px;
}

.save-row-btn {
  font-size: 10px;
  font-family: var(--font-mono);
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  cursor: pointer;
}

.save-row-btn:hover {
  background-color: var(--accent-light);
  color: var(--accent);
  border-color: var(--accent);
}

/* Examples Manager */
.examples-filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 14px;
}

.search-box-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  padding: 6px 10px;
  flex: 1;
  min-width: 280px;
}

.examples-search-input {
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-size: 12px;
  width: 100%;
  outline: none;
}

.filter-pills-row {
  display: flex;
  gap: 4px;
}

.filter-type-pill {
  font-size: 10px;
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  cursor: pointer;
}

.filter-type-pill.active {
  background-color: var(--bg-active);
  color: var(--accent);
  border-color: var(--accent);
}

.examples-list-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.example-item-card {
  background-color: var(--bg-primary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 10px 12px;
}

.example-card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.head-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ex-id-tag {
  font-size: 10px;
  color: var(--text-muted);
}

.ex-type-pill {
  font-size: 9px;
  padding: 1px 5px;
  border-radius: 3px;
  background-color: var(--bg-tertiary);
  color: var(--accent);
}

.qdrant-score-tag {
  font-size: 9px;
  color: var(--success);
}

.delete-icon-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
}

.delete-icon-btn:hover {
  color: var(--danger);
}

.example-question {
  font-size: 13px;
  color: var(--text-primary);
  font-weight: var(--font-weight-medium);
  margin-bottom: 6px;
}

.example-sql-box {
  background-color: var(--bg-app);
  padding: 6px 8px;
  border-radius: 3px;
  font-size: 11px;
  color: #79c0ff;
  overflow-x: auto;
}

.example-explanation {
  font-size: 11px;
  margin-top: 4px;
}

/* Add example form */
.add-example-card {
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  padding: 14px;
  margin-bottom: 14px;
}

.card-header-inner {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  font-weight: var(--font-weight-medium);
}

.close-card-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
}

.example-form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.form-group.full-width {
  grid-column: span 2;
}

.form-group label {
  display: block;
  font-size: 10.5px;
  color: var(--text-muted);
  margin-bottom: 4px;
}

.form-input {
  width: 100%;
  background-color: var(--bg-input);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  padding: 6px 8px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  outline: none;
}

.form-input:focus {
  border-color: var(--accent);
}

.sql-textarea {
  resize: vertical;
  color: #79c0ff;
}

.form-actions-row {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 10px;
}

/* Query Logs */
.logs-filter-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
}

.filter-select {
  background-color: var(--bg-input);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  padding: 6px 8px;
  border-radius: var(--radius-sm);
  font-size: 11px;
}

.log-query-cell {
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.log-sql-cell {
  max-width: 240px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #79c0ff;
}

.status-indicator.success { color: var(--success); }
.status-indicator.blocked { color: var(--warning); }
.status-indicator.error { color: var(--danger); }

/* Guardrails */
.guardrails-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.guard-section-title {
  font-size: 12px;
  font-weight: var(--font-weight-medium);
  color: var(--text-primary);
  margin: 0 0 4px 0;
}

.guard-desc {
  font-size: 11px;
  color: var(--text-muted);
  margin: 0 0 10px 0;
}

.operations-tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.op-tag {
  font-size: 11px;
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  cursor: pointer;
  user-select: none;
}

.op-tag.blocked {
  background-color: var(--danger-bg);
  color: var(--danger);
  border-color: rgba(239, 68, 68, 0.4);
}

.guard-form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.guard-form-box label {
  display: block;
  font-size: 11px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.sub-hint {
  display: block;
  font-size: 10px;
  color: var(--text-muted);
  margin-top: 3px;
}

.tables-checkbox-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 8px;
  background-color: var(--bg-primary);
  padding: 10px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-subtle);
}

.table-chk-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: var(--text-secondary);
  cursor: pointer;
}

/* Model Config */
.model-settings-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.model-choice-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 10px;
}

.model-option-card {
  background-color: var(--bg-primary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 12px;
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.model-option-card:hover {
  border-color: var(--accent);
}

.model-option-card.is-default {
  border-color: var(--accent);
  background-color: var(--bg-active);
}

.model-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.provider-pill {
  font-size: 9px;
  padding: 1px 5px;
  border-radius: 3px;
}

.provider-pill.groq { background: #f59e0b22; color: #f59e0b; }
.provider-pill.google { background: #38bdf822; color: #38bdf8; }

.default-badge {
  font-size: 10px;
  color: var(--accent);
  font-weight: var(--font-weight-medium);
}

.model-name {
  font-size: 13px;
  font-weight: var(--font-weight-medium);
  color: var(--text-primary);
}

.model-specs {
  font-size: 10.5px;
}

.user-allow-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 10.5px;
  color: var(--text-secondary);
  margin-top: 6px;
  padding-top: 6px;
  border-top: 1px dashed var(--border-subtle);
  cursor: pointer;
}

.enforce-banner {
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  padding: 10px 12px;
  border-radius: var(--radius-sm);
}

.enforce-chk {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  cursor: pointer;
}

.settings-form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 12px;
}

.settings-form-grid .form-row label {
  display: block;
  font-size: 11px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.slider-input {
  width: 100%;
  accent-color: var(--accent);
}

.api-keys-box {
  background-color: var(--bg-primary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 12px;
}

.keys-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 8px;
}

.key-label-row {
  display: flex !important;
  align-items: center;
  justify-content: space-between;
}

.key-status-badge {
  font-size: 9px;
  padding: 1px 5px;
  border-radius: 4px;
  font-weight: 600;
}

.key-status-badge.configured {
  background-color: rgba(16, 185, 129, 0.12);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.key-status-badge.missing {
  background-color: rgba(148, 163, 184, 0.1);
  color: var(--text-muted);
  border: 1px solid var(--border-subtle);
}

/* Evaluation Benchmark */
.eval-loading-state {
  display: flex;
  align-items: center;
  gap: 10px;
  background-color: rgba(56, 189, 248, 0.08);
  border: 1px solid rgba(56, 189, 248, 0.25);
  border-radius: var(--radius-sm);
  padding: 12px 16px;
  color: var(--accent);
  font-size: 12px;
  margin-bottom: 12px;
}

.eval-results-container {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.eval-metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}

.eval-metric-box {
  background-color: var(--bg-primary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.m-label {
  font-size: 10px;
  color: var(--text-muted);
  text-transform: uppercase;
}

.m-val {
  font-size: 20px;
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.m-val.pass { color: var(--success); }
.m-val.highlight { color: var(--accent); }

.m-sub {
  font-size: 10px;
  color: var(--text-muted);
}

.type-breakdown-card {
  background-color: var(--bg-primary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 10px;
}

.breakdown-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 6px;
}

.type-result-pill {
  font-size: 11px;
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  padding: 3px 8px;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
}

/* Table styles */
.table-responsive {
  overflow-x: auto;
}

.editor-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11.5px;
}

.editor-table th, .editor-table td {
  padding: 8px 10px;
  border-bottom: 1px solid var(--border-subtle);
  text-align: left;
}

.editor-table th {
  background-color: var(--bg-tertiary);
  color: var(--text-muted);
  font-size: 10.5px;
  text-transform: uppercase;
}

.text-right { text-align: right; }
.text-muted { color: var(--text-muted); }
.font-mono { font-family: var(--font-mono); }

/* Role pill styles */
.role-pill {
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  font-size: 11px;
  color: var(--text-muted);
}

.role-pill.is-admin {
  background-color: rgba(16, 185, 129, 0.12);
  border-color: rgba(16, 185, 129, 0.4);
  color: var(--success);
}

/* Access Denied Container */
.access-denied-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 480px;
  padding: 30px 16px;
}

.access-denied-card {
  max-width: 580px;
  width: 100%;
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 36px 32px;
  text-align: center;
  box-shadow: var(--shadow-md);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.denied-icon-wrap {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: rgba(245, 158, 11, 0.12);
  border: 1px solid rgba(245, 158, 11, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
}

.denied-lock-icon {
  color: var(--warning);
}

.denied-title {
  font-size: var(--text-lg);
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  margin: 0;
}

.denied-desc {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0;
}

.denied-desc .admin-tag {
  color: var(--accent);
  background-color: var(--bg-tertiary);
  padding: 2px 6px;
  border-radius: var(--radius-xs);
  border: 1px solid var(--border-color);
}

.denied-actions {
  display: flex;
  gap: 12px;
  margin-top: 8px;
  width: 100%;
  justify-content: center;
  flex-wrap: wrap;
}

.primary-login-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: var(--btn-primary-gradient);
  border: 1px solid var(--btn-primary-border);
  color: #ffffff;
  padding: 9px 20px;
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(2, 132, 199, 0.35);
  transition: all var(--transition-fast);
}

.primary-login-btn:hover {
  background: var(--btn-primary-gradient-hover);
  border-color: rgba(56, 189, 248, 0.5);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(2, 132, 199, 0.45);
}

.secondary-return-btn {
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  padding: 9px 16px;
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.secondary-return-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.denied-demo-box {
  margin-top: 10px;
  padding: 12px;
  background-color: var(--bg-app);
  border: 1px dashed var(--border-color);
  border-radius: var(--radius-md);
  font-size: 11px;
  text-align: left;
  width: 100%;
  color: var(--text-secondary);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.demo-box-label {
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  font-size: 10px;
  letter-spacing: 0.5px;
  margin-bottom: 2px;
}

.demo-cred-row code {
  color: var(--accent);
  background-color: var(--bg-tertiary);
  padding: 1px 5px;
  border-radius: 3px;
}

.fixed-engine-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background-color: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  color: var(--accent);
  font-weight: 500;
  font-size: 12px;
  width: fit-content;
}
</style>
