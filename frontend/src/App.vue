<template>
  <div class="flex h-screen bg-slate-50">
    <!-- 侧边栏 -->
    <aside class="w-72 bg-slate-900 text-white flex flex-col">
      <!-- Logo 区 -->
      <div class="px-5 py-5 cursor-pointer hover:bg-slate-800/50 transition" @click="goHome">
        <h1 class="text-base font-bold tracking-tight">AI 论文学习助手</h1>
        <p class="text-xs text-slate-400 mt-0.5">v0.2 · 本地资料 → 学习笔记</p>
      </div>

      <!-- 文件列表 -->
      <FileList
        :files="files"
        :selected-path="selectedFilePath"
        :folder="folder"
        :loading="loadingFiles"
        @select="handleFileSelect"
        @folder-change="handleFolderChange"
        @upload="handleUpload"
      />

      <!-- 底部配置 -->
      <ConfigPanel />
    </aside>

    <!-- 主内容 -->
    <main class="flex-1 overflow-y-auto">
      <StudyView
        v-if="document"
        :document="document"
        :file-path="selectedFilePath"
        :folder="folder"
      />
      <Dashboard v-else :files="files" />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { listFiles, getDocument, uploadFile } from './api.js'
import FileList from './components/FileList.vue'
import ConfigPanel from './components/ConfigPanel.vue'
import StudyView from './views/StudyView.vue'
import Dashboard from './components/Dashboard.vue'

const files = ref([])
const folder = ref('')
const selectedFilePath = ref('')
const document = ref(null)
const loadingFiles = ref(false)

async function loadFiles(dir) {
  loadingFiles.value = true
  try { files.value = await listFiles(dir) }
  catch (e) { console.error('加载文件列表失败', e) }
  finally { loadingFiles.value = false }
}

function handleFolderChange(newFolder) {
  folder.value = newFolder
  document.value = null
  selectedFilePath.value = ''
  loadFiles(newFolder)
}

async function handleFileSelect(file) {
  selectedFilePath.value = file.relative_path
  try { document.value = await getDocument(file.path) }
  catch (e) { console.error('读取文档失败', e) }
}

async function handleUpload(file) {
  try {
    const doc = await uploadFile(file)
    document.value = doc
    selectedFilePath.value = `uploaded/${file.name}`
  } catch (e) { console.error('上传失败', e) }
}

function goHome() {
  document.value = null
  selectedFilePath.value = ''
}

onMounted(() => loadFiles(folder.value))
</script>
