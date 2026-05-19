<template>
  <div class="flex flex-col h-[500px]">
    <!-- 消息列表 -->
    <div ref="chatBox" class="flex-1 overflow-y-auto space-y-3 mb-4 pr-1">
      <div v-if="messages.length === 0" class="flex items-center justify-center h-full">
        <p class="text-sm text-slate-400 italic">针对当前文档提问，AI 会基于内容回答</p>
      </div>
      <div
        v-for="(msg, i) in messages"
        :key="i"
        class="flex"
        :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
      >
        <div
          class="max-w-[80%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed"
          :class="msg.role === 'user'
            ? 'bg-blue-600 text-white rounded-br-md'
            : 'bg-slate-100 text-slate-700 rounded-bl-md'"
        >
          <div v-if="msg.role === 'assistant'" class="prose prose-sm prose-slate max-w-none" v-html="renderMd(msg.content)"></div>
          <span v-else>{{ msg.content }}</span>
        </div>
      </div>
      <div v-if="loading" class="flex justify-start">
        <div class="bg-slate-100 px-4 py-2.5 rounded-2xl rounded-bl-md">
          <span class="text-sm text-slate-400 animate-pulse">思考中...</span>
        </div>
      </div>
    </div>

    <!-- 输入框 -->
    <div class="flex gap-2">
      <input
        v-model="input"
        @keydown.enter="send"
        :disabled="loading"
        placeholder="输入你的问题..."
        class="flex-1 px-4 py-2.5 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 transition"
      />
      <button
        @click="send"
        :disabled="loading || !input.trim()"
        class="px-4 py-2.5 bg-blue-600 text-white rounded-xl text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition"
      >
        发送
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { marked } from 'marked'
import { chatWithDoc } from '../api.js'

const props = defineProps({ context: String })

const messages = ref([])
const input = ref('')
const loading = ref(false)
const chatBox = ref(null)

function renderMd(text) { return marked(text) }

async function send() {
  const question = input.value.trim()
  if (!question) return

  messages.value.push({ role: 'user', content: question })
  input.value = ''
  loading.value = true
  await scrollToBottom()

  try {
    const res = await chatWithDoc(question, props.context, messages.value.slice(0, -1))
    if (res.ok) {
      messages.value.push({ role: 'assistant', content: res.answer })
    } else {
      messages.value.push({ role: 'assistant', content: `出错了：${res.message}` })
    }
  } catch {
    messages.value.push({ role: 'assistant', content: '请求失败，请检查后端是否运行' })
  } finally {
    loading.value = false
    await scrollToBottom()
  }
}

async function scrollToBottom() {
  await nextTick()
  if (chatBox.value) chatBox.value.scrollTop = chatBox.value.scrollHeight
}
</script>
