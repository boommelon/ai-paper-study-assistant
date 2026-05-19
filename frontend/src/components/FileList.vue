<template>
  <div class="flex-1 flex flex-col overflow-hidden">
    <!-- 目录输入 -->
    <div class="px-4 py-3 border-b border-slate-700/50">
      <input
        type="text"
        :value="folder"
        @change="$emit('folder-change', $event.target.value)"
        class="w-full px-3 py-1.5 text-xs bg-slate-800 border border-slate-700 rounded-md text-slate-300 placeholder-slate-500 focus:outline-none focus:border-blue-500"
        placeholder="资料目录路径（留空用默认）"
      />
      <label class="mt-2 flex items-center gap-2 cursor-pointer">
        <input
          type="file"
          accept=".md,.markdown,.txt,.pdf,.docx"
          @change="handleFileUpload"
          class="hidden"
        />
        <span class="text-xs text-slate-400 hover:text-blue-400 transition">+ 上传文件</span>
      </label>
    </div>

    <!-- 文件列表 -->
    <div class="flex-1 overflow-y-auto px-2 py-2">
      <div v-if="loading" class="px-3 py-4 text-xs text-slate-500 text-center">加载中...</div>
      <div v-else-if="files.length === 0" class="px-3 py-4 text-xs text-slate-500 text-center">
        目录为空或路径无效
      </div>
      <ul v-else class="space-y-0.5">
        <li
          v-for="file in files"
          :key="file.path"
          @click="$emit('select', file)"
          class="px-3 py-2 rounded-lg cursor-pointer transition-all duration-150"
          :class="file.relative_path === selectedPath
            ? 'bg-blue-600/20 text-blue-300'
            : 'text-slate-300 hover:bg-slate-800'"
        >
          <div class="text-sm truncate leading-tight">{{ file.title }}</div>
          <div class="text-xs text-slate-500 truncate mt-0.5">{{ file.relative_path }}</div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
defineProps({ files: Array, selectedPath: String, folder: String, loading: Boolean })
const emit = defineEmits(['select', 'folder-change', 'upload'])
function handleFileUpload(e) {
  const file = e.target.files[0]
  if (file) emit('upload', file)
}
</script>
