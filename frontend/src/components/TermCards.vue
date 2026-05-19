<template>
  <div>
    <div class="flex items-center gap-3 mb-4">
      <h3 class="text-sm font-semibold text-slate-700">关键术语</h3>
      <button
        v-if="terms.length === 0"
        @click="extract"
        :disabled="loading"
        class="px-3 py-1 bg-slate-100 text-slate-600 rounded-lg text-xs hover:bg-slate-200 disabled:opacity-50 transition"
      >
        {{ loading ? '提取中...' : '提取术语' }}
      </button>
    </div>

    <div v-if="terms.length" class="grid grid-cols-2 gap-2">
      <div
        v-for="(term, i) in terms"
        :key="i"
        class="px-3 py-2.5 bg-gradient-to-br from-slate-50 to-slate-100/50 border border-slate-200/80 rounded-lg"
      >
        <div class="text-sm font-medium text-slate-700">{{ term.term }}</div>
        <div class="text-xs text-slate-500 mt-0.5 leading-relaxed">{{ term.explanation }}</div>
      </div>
    </div>

    <p v-else-if="!loading" class="text-xs text-slate-400 italic">点击提取按钮自动识别文档中的关键术语</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { extractTerms } from '../api.js'

const props = defineProps({ content: String, title: String })

const terms = ref([])
const loading = ref(false)

async function extract() {
  loading.value = true
  try {
    const res = await extractTerms(props.content, props.title)
    if (res.ok) terms.value = res.terms
  } catch { /* ignore */ }
  finally { loading.value = false }
}
</script>
