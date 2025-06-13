<template>
  <div class="folder-tree-actions">
    <input
      :value="newFolderName"
      @input="$emit('update:newFolderName', $event.target.value)"
      placeholder="新建收藏夹名称"
      @keyup.enter="$emit('createFolder')"
    />
    <button @click="$emit('createFolder')" :disabled="creating">新建</button>
  </div>
</template>

<script setup>
defineProps({
  newFolderName: {
    type: String,
    required: true
  },
  creating: {
    type: Boolean,
    required: true
  }
});
defineEmits(['createFolder', 'update:newFolderName']);
</script>

<style scoped>
.folder-tree-actions {
  margin-bottom: 14px;
  display: flex;
  gap: 10px;
}
.folder-tree-actions input {
  background: #23272f;
  color: #fff;
  border: 1px solid #333a4a;
  border-radius: 5px;
  padding: 6px 10px;
  font-size: 14px;
  outline: none;
  transition: border 0.18s;
}
.folder-tree-actions input:focus {
  border: 1.5px solid #409EFF;
}
.folder-tree-actions button {
  background: linear-gradient(90deg, #409EFF 60%, #7f5fff 100%);
  color: #fff;
  border: none;
  border-radius: 5px;
  padding: 6px 18px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.18s, color 0.18s;
}
.folder-tree-actions button:disabled {
  background: #444a;
  color: #aaa;
  cursor: not-allowed;
}
</style>
