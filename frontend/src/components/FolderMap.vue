<template>
  <div>
    <div class="flex items-center gap-3 mb-5">
      <button
        @click="generate"
        :disabled="loading"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 shadow-sm transition"
      >
        {{ loading ? '生成中...' : '生成学习地图' }}
      </button>
      <span v-if="meta" class="text-xs text-slate-400 bg-slate-100 px-2 py-1 rounded">{{ meta }}</span>
    </div>

    <div v-if="error" class="mb-4 px-4 py-3 bg-red-50 border border-red-100 text-red-600 rounded-lg text-sm">{{ error }}</div>

    <div v-if="content" class="prose prose-sm prose-slate max-w-none" v-html="renderMd(content)"></div>
    <p v-else class="text-sm text-slate-400 italic">点击按钮生成当前目录的学习地图</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { marked } from 'marked'
import { generateFolderMap } from '../api.js'

const props = defineProps({ folder: String })
const content = ref('')
const loading = ref(false)
const error = ref('')
const meta = ref('')

function renderMd(text) { return marked(text) }

async function generate() {
  loading.value = true
  error.value = ''
  try {
    const res = await generateFolderMap(props.folder)
    if (res.ok) {
      content.value = res.content
      meta.value = `${res.read_files} / ${res.total_files} 个文件`
    } else error.value = res.message
  } catch { error.value = '请求失败' }
  finally { loading.value = false }
}
</script>
