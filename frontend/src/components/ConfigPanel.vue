<template>
  <div class="border-t border-slate-700/50 px-4 py-3">
    <button
      @click="expanded = !expanded"
      class="text-xs text-slate-400 hover:text-slate-200 flex items-center gap-1.5 transition"
    >
      <svg class="w-3 h-3 transition-transform" :class="expanded && 'rotate-90'" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z" clip-rule="evenodd" />
      </svg>
      AI 配置
    </button>
    <div v-if="expanded" class="mt-2 space-y-1.5 text-xs text-slate-400">
      <div>模型: <span class="text-slate-200">{{ config.model || '...' }}</span></div>
      <div>接口: <span class="text-slate-200 break-all">{{ config.base_url || '...' }}</span></div>
      <div>
        Key:
        <span :class="config.has_key ? 'text-green-400' : 'text-red-400'">
          {{ config.has_key ? '已配置' : '未配置' }}
        </span>
      </div>
      <button
        @click="testConn"
        :disabled="testing"
        class="mt-1 px-2.5 py-1 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded text-xs transition disabled:opacity-50"
      >
        {{ testing ? '测试中...' : '测试连接' }}
      </button>
      <div v-if="testResult" :class="testResult.ok ? 'text-green-400' : 'text-red-400'" class="text-xs">
        {{ testResult.message }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getConfig, testConnection } from '../api.js'

const expanded = ref(false)
const config = ref({})
const testing = ref(false)
const testResult = ref(null)

async function testConn() {
  testing.value = true
  testResult.value = null
  try { testResult.value = await testConnection() }
  catch { testResult.value = { ok: false, message: '请求失败' } }
  finally { testing.value = false }
}

onMounted(async () => { config.value = await getConfig() })
</script>
