<template>
  <div>
    <!-- 操作栏 -->
    <div class="flex gap-2 mb-6 flex-wrap">
      <button
        @click="handleGenerateAll"
        :disabled="loading"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 shadow-sm transition"
      >
        {{ loading ? '生成中...' : '一键生成全部' }}
      </button>
      <button
        v-for="(label, task) in taskLabels"
        :key="task"
        @click="handleGenerate(task)"
        :disabled="loading"
        class="px-3 py-2 bg-slate-100 text-slate-600 rounded-lg text-sm hover:bg-slate-200 disabled:opacity-50 transition"
      >
        {{ notes[task] ? '重新生成' : '生成' }}{{ label }}
      </button>
    </div>

    <!-- 错误 -->
    <div v-if="error" class="mb-4 px-4 py-3 bg-red-50 border border-red-100 text-red-600 rounded-lg text-sm">
      {{ error }}
    </div>

    <!-- 笔记卡片 -->
    <div class="space-y-5">
      <div v-for="(label, task) in taskLabels" :key="task" class="rounded-lg border border-slate-100 overflow-hidden">
        <div class="px-4 py-2.5 bg-slate-50 border-b border-slate-100">
          <h3 class="text-sm font-semibold text-slate-700">{{ label }}</h3>
        </div>
        <div v-if="notes[task]" class="p-4 prose prose-sm prose-slate max-w-none" v-html="renderMd(notes[task])"></div>
        <div v-else class="p-4 text-sm text-slate-400 italic">还没有生成</div>
      </div>
    </div>

    <!-- 导出 -->
    <div v-if="hasNotes" class="mt-6 pt-5 border-t border-slate-100">
      <button @click="exportMarkdown" class="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm font-medium hover:bg-emerald-700 shadow-sm transition">
        导出 Markdown
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { marked } from 'marked'
import { generateNote, generateAll } from '../api.js'

const props = defineProps({ filePath: String, topic: Object })
const taskLabels = { summary: '总结', beginner: '初学者解释', questions: '复习问题' }
const notes = ref({})
const loading = ref(false)
const error = ref('')
const hasNotes = computed(() => Object.values(notes.value).some(v => v))

function renderMd(text) { return marked(text) }

async function handleGenerate(task) {
  loading.value = true
  error.value = ''
  try {
    const res = await generateNote({
      file_path: props.filePath, topic_id: props.topic.id,
      topic_title: props.topic.title, topic_content: props.topic.content, task,
    })
    if (res.ok) notes.value[task] = res.content
    else error.value = res.message
  } catch { error.value = '请求失败' }
  finally { loading.value = false }
}

async function handleGenerateAll() {
  loading.value = true
  error.value = ''
  try {
    const res = await generateAll({
      file_path: props.filePath, topic_id: props.topic.id,
      topic_title: props.topic.title, topic_content: props.topic.content,
    })
    if (res.ok) {
      for (const [task, data] of Object.entries(res.results))
        notes.value[task] = data.content
    } else error.value = res.message
  } catch { error.value = '请求失败' }
  finally { loading.value = false }
}

function exportMarkdown() {
  const lines = [`# ${props.filePath}`, '', `- 主题：${props.topic.title}`, '']
  for (const [task, label] of Object.entries(taskLabels)) {
    if (notes.value[task]) lines.push(`## ${label}`, '', notes.value[task], '')
  }
  const blob = new Blob([lines.join('\n')], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${props.topic.title}_学习笔记.md`
  a.click()
  URL.revokeObjectURL(url)
}
</script>
