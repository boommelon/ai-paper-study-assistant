<template>
  <div class="p-8 max-w-4xl mx-auto">
    <div class="mb-8">
      <h2 class="text-2xl font-bold text-slate-800">学习仪表盘</h2>
      <p class="text-sm text-slate-400 mt-1">你的学习概览</p>
    </div>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-3 gap-4 mb-8">
      <div class="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
        <div class="text-2xl font-bold text-blue-600">{{ stats.totalFiles }}</div>
        <div class="text-xs text-slate-500 mt-1">资料文件</div>
      </div>
      <div class="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
        <div class="text-2xl font-bold text-emerald-600">{{ stats.formats }}</div>
        <div class="text-xs text-slate-500 mt-1">文件格式</div>
      </div>
      <div class="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
        <div class="text-2xl font-bold text-purple-600">{{ stats.totalSize }}</div>
        <div class="text-xs text-slate-500 mt-1">总大小</div>
      </div>
    </div>

    <!-- 快速开始 -->
    <div class="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
      <h3 class="text-sm font-semibold text-slate-700 mb-3">快速开始</h3>
      <div class="space-y-2">
        <div class="flex items-center gap-3 text-sm text-slate-600">
          <span class="w-6 h-6 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-xs font-bold">1</span>
          从左侧选择一个资料文件
        </div>
        <div class="flex items-center gap-3 text-sm text-slate-600">
          <span class="w-6 h-6 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-xs font-bold">2</span>
          选择主题，阅读原文
        </div>
        <div class="flex items-center gap-3 text-sm text-slate-600">
          <span class="w-6 h-6 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-xs font-bold">3</span>
          生成 AI 学习笔记或直接提问
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ files: Array })

const stats = computed(() => {
  const files = props.files || []
  const formats = new Set(files.map(f => f.extension)).size
  const totalBytes = files.reduce((sum, f) => sum + f.size, 0)
  const totalSize = totalBytes > 1024 * 1024
    ? `${(totalBytes / 1024 / 1024).toFixed(1)} MB`
    : `${(totalBytes / 1024).toFixed(0)} KB`
  return { totalFiles: files.length, formats, totalSize }
})
</script>
