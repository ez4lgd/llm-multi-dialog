<template>
  <div class="folder-tree-sidebar">
    <div
      class="sidebar-item"
      :class="{ active: selectedFolderId === 'all' }"
      @click="$emit('update:selectedFolderId', 'all')"
    >全部</div>
    <div
      v-for="folder in folders"
      :key="folder.folder_id"
      class="sidebar-item"
      :class="{ active: selectedFolderId === folder.folder_id }"
      @click="$emit('update:selectedFolderId', folder.folder_id)"
    >{{ folder.name }}</div>
  </div>
</template>

<script setup>
defineProps({
  folders: {
    type: Array,
    required: true
  },
  selectedFolderId: {
    type: String,
    required: true
  }
});
defineEmits(['update:selectedFolderId']);
</script>

<style scoped>
.folder-tree-sidebar {
  width: 120px;
  background: #23272f;
  border-right: 1px solid #333a4a;
  padding: 18px 0 0 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-height: 0;
}
.sidebar-item {
  padding: 8px 18px;
  color: #bdbfff;
  font-size: 15px;
  cursor: pointer;
  border-radius: 0 12px 12px 0;
  margin-bottom: 2px;
  transition: background 0.18s, color 0.18s;
  user-select: none;
}
.sidebar-item.active, .sidebar-item:hover {
  background: linear-gradient(90deg, #409EFF22 60%, #7f5fff22 100%);
  color: #7f5fff;
}
</style>
