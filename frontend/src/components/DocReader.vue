<template>
  <div>
    <div class="prose prose-slate prose-sm max-w-none leading-relaxed whitespace-pre-wrap">{{ topic?.content }}</div>

    <div v-if="pages && pages.length" class="mt-6 pt-5 border-t border-slate-100">
      <div class="flex items-center gap-3 mb-3">
        <span class="text-xs font-medium text-slate-500 uppercase tracking-wide">PDF 页预览</span>
        <select v-model="selectedPage" class="px-2 py-1 text-xs border border-slate-200 rounded-md bg-white">
          <option v-for="page in pages" :key="page.number" :value="page.number">
            第 {{ page.number }} 页
          </option>
        </select>
      </div>
      <pre class="bg-slate-50 border border-slate-100 rounded-lg p-4 text-sm text-slate-600 whitespace-pre-wrap max-h-72 overflow-y-auto">{{ currentPageText }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({ topic: Object, pages: Array })
const selectedPage = ref(props.pages?.[0]?.number || 1)

const currentPageText = computed(() => {
  const page = props.pages?.find(p => p.number === selectedPage.value)
  return page?.text || '这一页没有提取到文字。'
})
</script>
