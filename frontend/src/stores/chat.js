import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useChatStore = defineStore('chat', () => {
  const models = ref(['Gemini 1.5 Pro', 'Claude 3.5 Sonnet', 'GPT-4o', 'DeepSeek R1'])
  const selectedModel = ref('Claude 3.5 Sonnet')
  const isTyping = ref(false)

  const messages = ref([
    {
      id: 1,
      sender: 'assistant',
      time: '10:42 AM',
      text: "Hello! I am your **SubscriptIQ Copilot**. I've scanned your workspace and detected **$340/month in potential SaaS optimization** across 4 overlapping subscription tiers.",
      hasActions: true,
      actions: ['Review overlapping tools', 'Generate cancellation draft'],
      codeSnippet: `// Subscription optimization detected:
const redundantLicenses = [
  { tool: "Figma Pro", unusedSeats: 4, monthlyWaste: "$60" },
  { tool: "Notion AI", unusedSeats: 8, monthlyWaste: "$80" },
  { tool: "Datadog Logs", redundantRetention: "60d", monthlyWaste: "$200" }
];`,
    },
    {
      id: 2,
      sender: 'user',
      time: '10:44 AM',
      text: 'Which subscriptions renew in the next 14 days?',
    },
    {
      id: 3,
      sender: 'assistant',
      time: '10:44 AM',
      text: 'Here are the **2 subscriptions** approaching auto-renewal within 14 days:\n- **GitHub Enterprise**: Renews Oct 28 ($210/mo) - High utilization (96%)\n- **Loom Enterprise**: Renews Nov 01 ($180/mo) - Low utilization (22%)\n\nWould you like me to flag Loom for downgrade before the renewal window closes?',
      hasActions: true,
      actions: ['Flag Loom for Downgrade', 'Export Renewal Calendar'],
    },
  ])

  function sendMessage(text) {
    if (!text || !text.trim()) return

    const userMsg = {
      id: Date.now(),
      sender: 'user',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      text: text.trim(),
    }
    messages.value.push(userMsg)

    isTyping.value = true
    // Simulate intelligent AI copilot response
    setTimeout(() => {
      isTyping.value = false
      let replyText = `I analyzed your query: *"${userMsg.text}"*.\n\nSubscriptIQ AI processed telemetry data from your active integrations. All parameters are within expected limits, and I've cached the latest contract analytics.`
      let codeSnippet = null

      if (userMsg.text.toLowerCase().includes('admin') || userMsg.text.toLowerCase().includes('role')) {
        replyText = `### Role & Access Security Check\nCurrently evaluating permissions against your workspace policies. Admins have access to token allocations, user seat management, and API rate limits.`
      } else if (userMsg.text.toLowerCase().includes('cost') || userMsg.text.toLowerCase().includes('save') || userMsg.text.toLowerCase().includes('spend')) {
        replyText = `### Projected Savings Breakdown\nRunning automated license reconciliation. Here is the suggested adjustment patch:`
        codeSnippet = `{\n  "recommendation": "seat_reduction",\n  "target": "Slack Enterprise Grid",\n  "inactive_accounts": 12,\n  "monthly_reclaim": "$180.00 USD"\n}`
      }

      messages.value.push({
        id: Date.now() + 1,
        sender: 'assistant',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        text: replyText,
        codeSnippet,
      })
    }, 750)
  }

  function clearChat() {
    messages.value = [
      {
        id: Date.now(),
        sender: 'assistant',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        text: "Chat cleared. I'm ready to assist with subscription telemetry, cost audits, or contract intelligence.",
      },
    ]
  }

  return {
    models,
    selectedModel,
    isTyping,
    messages,
    sendMessage,
    clearChat,
  }
})
