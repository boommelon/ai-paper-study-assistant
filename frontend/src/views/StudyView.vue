<template>
  <div class="p-8 max-w-4xl mx-auto">
    <!-- 文档标题 -->
    <div class="mb-6">
      <h2 class="text-2xl font-bold text-slate-800">{{ document.title }}</h2>
      <p class="text-sm text-slate-400 mt-1 font-mono">{{ filePath }}</p>
    </div>

    <!-- 主题选择 + 术语卡片 -->
    <div class="grid grid-cols-3 gap-6 mb-6">
      <div class="col-span-1">
        <TopicSelector
          :topics="document.topics"
          :selected-id="selectedTopicId"
          @select="handleTopicSelect"
        />
      </div>
      <div class="col-span-2">
        <TermCards :content="selectedTopic?.content || ''" :title="document.title" />
      </div>
    </div>

    <!-- Tab 切换 -->
    <div class="flex gap-1 mb-6 bg-slate-100 p-1 rounded-xl w-fit">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        @click="activeTab = tab.key"
        class="px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200"
        :class="activeTab === tab.key
          ? 'bg-white text-slate-800 shadow-sm'
          : 'text-slate-500 hover:text-slate-700'"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- 内容区 -->
    <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
      <DocReader v-if="activeTab === 'reader'" :topic="selectedTopic" :pages="document.pages" />
      <AiNotes v-if="activeTab === 'notes'" :file-path="filePath" :topic="selectedTopic" />
      <DocChat v-if="activeTab === 'chat'" :context="selectedTopic?.content || ''" />
      <FolderMap v-if="activeTab === 'folder'" :folder="folder" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import TopicSelector from '../components/TopicSelector.vue'
import TermCards from '../components/TermCards.vue'
import DocReader from '../components/DocReader.vue'
import AiNotes from '../components/AiNotes.vue'
import DocChat from '../components/DocChat.vue'
import FolderMap from '../components/FolderMap.vue'

const props = defineProps({ document: Object, filePath: String, folder: String })

const tabs = [
  { key: 'reader', label: '原文阅读' },
  { key: 'notes', label: 'AI 笔记' },
  { key: 'chat', label: '文档问答' },
  { key: 'folder', label: '学习地图' },
]
const activeTab = ref('reader')
const selectedTopicId = ref(props.document.topics?.[0]?.id || '')

const selectedTopic = computed(() =>
  props.document.topics?.find(t => t.id === selectedTopicId.value) || props.document.topics?.[0]
)

function handleTopicSelect(topicId) { selectedTopicId.value = topicId }
</script>
