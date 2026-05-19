<template>
  <div>
    <label class="text-xs font-medium text-slate-500 uppercase tracking-wide mb-1.5 block">主题</label>
    <select
      :value="selectedId"
      @change="$emit('select', $event.target.value)"
      class="w-full px-3 py-2.5 bg-white border border-slate-200 rounded-lg text-sm text-slate-700 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 transition"
    >
      <option v-for="topic in topics" :key="topic.id" :value="topic.id">
        {{ topic.title }}
      </option>
    </select>
  </div>
</template>

<script setup>
defineProps({ topics: Array, selectedId: String })
defineEmits(['select'])
</script>
