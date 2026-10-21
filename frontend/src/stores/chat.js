import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useUIStore } from '@/stores/ui'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

export const useChatStore = defineStore('chat', () => {
  const defaultModelId = import.meta.env.VITE_DEFAULT_MODEL || 'openai/gpt-oss-120b'
  const groqPrimary = import.meta.env.VITE_GROQ_MODEL_PRIMARY || 'openai/gpt-oss-120b'
  const groqSecondary = import.meta.env.VITE_GROQ_MODEL_SECONDARY || 'openai/gpt-oss-20b'
  const googlePrimary = import.meta.env.VITE_GOOGLE_MODEL_PRIMARY || 'gemini-3.1-flash-lite'
  const googleSecondary = import.meta.env.VITE_GOOGLE_MODEL_SECONDARY || 'gemma-4-26b-a4b-it'

  const models = ref([
    { id: groqPrimary, name: `Groq · ${groqPrimary.split('/').pop().toUpperCase()}`, provider: 'groq', is_default: defaultModelId === groqPrimary },
    { id: groqSecondary, name: `Groq · ${groqSecondary.split('/').pop().toUpperCase()}`, provider: 'groq', is_default: defaultModelId === groqSecondary },
    { id: googlePrimary, name: `Google · ${googlePrimary.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}`, provider: 'google', is_default: defaultModelId === googlePrimary },
    { id: googleSecondary, name: `Google · ${googleSecondary.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}`, provider: 'google', is_default: defaultModelId === googleSecondary },
  ])
  const selectedModel = ref(defaultModelId)
  const isTyping = ref(false)
  const isEnforcedByAdmin = ref(false)
  const isAgentConnected = ref(false)
  const connectionChecked = ref(false)

  // Active query result for full-screen in-depth workspace analysis
  const activeQueryResult = ref({
    id: 1,
    query: 'Top 5 subscriptions by monthly spend',
    nlSummary: 'AWS Cloud Infrastructure, GitHub Enterprise, and Datadog represent your organization’s highest monthly recurring SaaS expenditures.',
    explanation: 'Filtered active SaaS subscriptions ordered by monthly recurring spend in descending order.',
    columns: ['product_name', 'category', 'monthly_cost', 'annual_contract_value', 'status'],
    rows: [
      { product_name: 'AWS Cloud Infrastructure', category: 'Infrastructure', monthly_cost: 14500, annual_contract_value: 174000, status: 'active' },
      { product_name: 'GitHub Enterprise', category: 'Engineering', monthly_cost: 4200, annual_contract_value: 50400, status: 'active' },
      { product_name: 'Datadog APM & Logs', category: 'DevOps & Monitoring', monthly_cost: 3800, annual_contract_value: 45600, status: 'active' },
      { product_name: 'Salesforce Enterprise CRM', category: 'Sales & CRM', monthly_cost: 3400, annual_contract_value: 40800, status: 'active' },
      { product_name: 'Slack Business Plus', category: 'Productivity', monthly_cost: 2600, annual_contract_value: 31200, status: 'active' },
    ],
    rowCount: 5,
    latency: 38.5,
    execLatency: 2.1,
    queryType: 'SELECT_SIMPLE',
    modelUsed: 'openai/gpt-oss-120b',
    chart: {
      type: 'bar',
      title: 'Monthly Spend by Subscription (Top 5)',
      labels: ['AWS Cloud', 'GitHub Ent.', 'Datadog', 'Salesforce', 'Slack'],
      values: [14500, 4200, 3800, 3400, 2600],
    },
    timestamp: '10:42 AM',
  })

  const messages = ref([
    {
      id: 1,
      sender: 'assistant',
      time: '10:42 AM',
      text: `👋 **Welcome to SubscriptIQ Assistant!**

I help you analyze, monitor, and optimize your organization's software subscriptions, spending, contracts, and software licenses.

### 💡 What You Can Ask
• **Spend & Costs:** Track monthly and annual expenses across departments, vendors, or tools.
• **Renewals & Billing:** Find contracts renewing soon, auto-renewal alerts, and pending invoices.
• **Licenses & Utilization:** Identify unassigned or dormant licenses to reduce wasted spend.
• **Optimizations:** Review automated cost-saving opportunities and seat reclamations.

### 💬 How to Ask
Type naturally in plain conversational English, just like asking a finance or IT analyst. No complex commands or technical syntax needed!

**Try one of these quick prompts below to get started:**`,
      hasActions: true,
      actions: [
        'Top 5 subscriptions by monthly spend',
        'Which subscriptions renew in next 30 days?',
        'Show total monthly spend by category',
        'Find all dormant license seats',
        'Show pending or overdue invoices',
        'Total savings from detected optimizations',
      ],
    },
  ])

  async function fetchModels(userRole = 'user') {
    try {
      const res = await fetch(`${API_BASE}/models?user_role=${userRole}`)
      if (res.ok) {
        const data = await res.json()
        if (data.models && Array.isArray(data.models)) {
          models.value = data.models
        }

        const allowedIds = (data.models || []).map(m => m.id)

        // If only 1 model is available or an enforced model is set, lock to that model
        if (data.admin_enforced_model) {
          selectedModel.value = data.admin_enforced_model
          isEnforcedByAdmin.value = true
        } else if (allowedIds.length === 1) {
          selectedModel.value = allowedIds[0]
          isEnforcedByAdmin.value = true
        } else {
          isEnforcedByAdmin.value = false
        }

        // Always ensure selectedModel is one of the allowed models
        if (allowedIds.length > 0) {
          if (!selectedModel.value || !allowedIds.includes(selectedModel.value)) {
            if (data.default_model && allowedIds.includes(data.default_model)) {
              selectedModel.value = data.default_model
            } else {
              selectedModel.value = allowedIds[0]
            }
          }
        }

        if (data.agent_connected !== undefined) {
          isAgentConnected.value = Boolean(data.agent_connected)
          connectionChecked.value = true
        }
      }
    } catch (e) {
      console.warn('Could not fetch models from backend, using defaults:', e)
    }
  }

  async function sendMessage(text, userRole = 'user', userEmail = 'alex.rivera@subscriptiq.ai') {
    if (!text || !text.trim()) return

    const userMsg = {
      id: Date.now(),
      sender: 'user',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      text: text.trim(),
    }
    messages.value.push(userMsg)

    isTyping.value = true

    // Automatically ensure Chat Analysis tab is open when user submits query
    const uiStore = useUIStore()
    uiStore.openQueryAnalysisTab('Chat Analysis')

    try {
      const res = await fetch(`${API_BASE}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: text.trim(),
          model_id: selectedModel.value,
          user_role: userRole,
          user_email: userEmail,
        }),
      })

      const data = await res.json()
      isTyping.value = false

      if (data.agent_connected !== undefined) {
        isAgentConnected.value = Boolean(data.agent_connected)
        connectionChecked.value = true
      }

      // Always update activeQueryResult so Query Analysis tab shows live results!
      activeQueryResult.value = {
        id: Date.now() + 1,
        query: text.trim(),
        isSuccess: Boolean(data.success),
        error: data.error || null,
        nlSummary: data.nl_summary || (data.error ? `Query Blocked: ${data.error}` : 'No records returned.'),
        explanation: data.explanation || null,
        columns: data.columns || [],
        rows: data.rows || [],
        rowCount: data.row_count !== undefined ? data.row_count : (data.rows ? data.rows.length : 0),
        latency: data.latency_ms || 0,
        execLatency: data.execution_latency_ms || 0,
        queryType: data.query_type || 'SELECT_SIMPLE',
        modelUsed: data.model_used || selectedModel.value,
        chart: data.chart || null,
        sql: data.sql || null,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }

      // Ensure Chat Analysis tab is active in workspace
      uiStore.openQueryAnalysisTab('Chat Analysis')

      if (data.success) {
        messages.value.push({
          id: Date.now() + 1,
          sender: 'assistant',
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          text: data.nl_summary,
          sqlSnippet: data.sql,
          explanation: data.explanation,
          columns: data.columns || [],
          rows: data.rows || [],
          rowCount: data.row_count,
          latency: data.latency_ms,
          execLatency: data.execution_latency_ms,
          queryType: data.query_type,
          modelUsed: data.model_used,
          chart: data.chart,
          transpiled: data.transpiled,
          pipelineSteps: data.pipeline_steps,
        })
      } else {
        messages.value.push({
          id: Date.now() + 1,
          sender: 'assistant',
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          text: `⚠️ **${data.error || 'Query Execution Blocked'}**\n\n${data.nl_summary || ''}`,
          isError: true,
          queryType: data.query_type,
          modelUsed: data.model_used,
          latency: data.latency_ms,
        })
      }
    } catch (err) {
      isTyping.value = false
      activeQueryResult.value = {
        id: Date.now() + 1,
        query: text.trim(),
        isSuccess: false,
        error: err.message,
        nlSummary: `Network Error: Could not connect to SubscriptIQ backend (${err.message})`,
        explanation: 'Check if backend service is running on port 8000.',
        columns: [],
        rows: [],
        rowCount: 0,
        latency: 0,
        queryType: 'ERROR',
        modelUsed: selectedModel.value,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }
      uiStore.openQueryAnalysisTab()
      messages.value.push({
        id: Date.now() + 1,
        sender: 'assistant',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        text: `Network Error: Could not connect to SubscriptIQ FastAPI backend at ${API_BASE}. Details: ${err.message}`,
        isError: true,
      })
    }
  }

  function clearChat() {
    messages.value = [
      {
        id: Date.now(),
        sender: 'assistant',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        text: `👋 **Welcome to SubscriptIQ Assistant!**

I help you analyze, monitor, and optimize your organization's software subscriptions, spending, contracts, and software licenses.

### 💡 What You Can Ask
• **Spend & Costs:** Track monthly and annual expenses across departments, vendors, or tools.
• **Renewals & Billing:** Find contracts renewing soon, auto-renewal alerts, and pending invoices.
• **Licenses & Utilization:** Identify unassigned or dormant licenses to reduce wasted spend.
• **Optimizations:** Review automated cost-saving opportunities and seat reclamations.

### 💬 How to Ask
Type naturally in plain conversational English, just like asking a finance or IT analyst. No complex commands or technical syntax needed!

**Try one of these quick prompts below to get started:**`,
        hasActions: true,
        actions: [
          'Top 5 subscriptions by monthly spend',
          'Which subscriptions renew in next 30 days?',
          'Show total monthly spend by category',
          'Find all dormant license seats',
          'Show pending or overdue invoices',
          'Total savings from detected optimizations',
        ],
      },
    ]
  }

  // Initialize connection state on startup
  fetchModels()

  return {
    models,
    selectedModel,
    isTyping,
    isEnforcedByAdmin,
    isAgentConnected,
    connectionChecked,
    messages,
    activeQueryResult,
    fetchModels,
    sendMessage,
    clearChat,
  }
})
