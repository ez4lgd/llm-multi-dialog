<template>
  <ul class="folder-list">
    <li
      v-for="folder in foldersToShow"
      :key="folder.folder_id"
      class="folder-item"
    >
      <span class="folder-name" :title="folder.name">{{ folder.name }}</span>
      <template v-if="conversationId">
        <button
          v-if="folder.conversation_ids.includes(conversationId)"
          class="remove-btn"
          @click="$emit('removeConvFromFolder', folder, conversationId)"
        >移除当前会话</button>
        <button
          v-else
          class="add-btn"
          @click="$emit('addConvToFolder', folder, conversationId)"
        >添加当前会话</button>
      </template>
      <button
        v-if="!folder.is_default"
        class="rename-btn"
        @click="$emit('startRename', folder)"
      >重命名</button>
      <button
        v-if="!folder.is_default"
        class="delete-btn"
        @click="$emit('deleteFolder', folder)"
      >删除</button>
      <ul class="conv-list">
        <li
          v-for="cid in folder.conversation_ids"
          :key="cid"
          class="conv-item"
        >
          <span
            class="conv-summary"
            :title="getSummary(cid)"
            @click="$emit('selectConversation', cid)"
          >
            {{ getSummary(cid) }}
          </span>
          <ConversationTags :conversation-id="cid" />
          <button
            class="remove-btn"
            @click="$emit('removeConv', folder, cid)"
          >移除</button>
        </li>
      </ul>
    </li>
  </ul>
  <div v-if="foldersToShow.length === 0" class="empty-tip">暂无收藏夹</div>
</template>

<script setup>
import ConversationTags from '../ConversationTags.vue';
import { computed } from 'vue';

const props = defineProps({
  folders: {
    type: Array,
    required: true
  },
  selectedFolderId: {
    type: String,
    required: true
  },
  conversationId: {
    type: String,
    default: ''
  },
  summaries: {
    type: Object,
    required: true
  }
});

const emits = defineEmits([
  'addConvToFolder',
  'removeConvFromFolder',
  'startRename',
  'deleteFolder',
  'removeConv',
  'selectConversation'
]);

function getSummary(cid) {
  return props.summaries[cid] || cid;
}

const foldersToShow = computed(() => {
  if (props.selectedFolderId === 'all') {
    return props.folders;
  }
  return props.folders.filter(f => f.folder_id === props.selectedFolderId);
});
</script>

<style scoped>
.folder-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.folder-item {
  margin-bottom: 14px;
  background: #23272f;
  border-radius: 7px;
  padding: 10px 14px;
  border: 1px solid #333a4a;
  box-shadow: 0 2px 8px 0 #0002;
}
.folder-name {
  font-weight: 600;
  color: #7f5fff;
  margin-right: 10px;
}
.rename-btn, .delete-btn, .remove-btn, .add-btn {
  margin-left: 8px;
  background: #23272f;
  color: #bdbfff;
  border: 1px solid #333a4a;
  border-radius: 4px;
  padding: 3px 12px;
  cursor: pointer;
  font-size: 13px;
  transition: background 0.18s, color 0.18s, border 0.18s;
}
.rename-btn:hover, .delete-btn:hover, .remove-btn:hover, .add-btn:hover {
  background: linear-gradient(90deg, #409EFF 60%, #7f5fff 100%);
  color: #fff;
  border: 1px solid #409EFF;
}
.conv-list {
  list-style: none;
  padding: 0 0 0 22px;
  margin: 8px 0 0 0;
}
.conv-item {
  margin-bottom: 5px;
  display: flex;
  align-items: center;
}
.empty-tip {
  color: #666;
  margin-top: 28px;
  text-align: center;
  font-size: 15px;
}
.conv-summary {
  cursor: pointer;
  color: #409EFF;
  text-decoration: underline;
  transition: color 0.18s;
  display: inline-block;
  max-width: 720px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  vertical-align: bottom;
}
.conv-summary:hover {
  color: #7f5fff;
  text-shadow: 0 0 2px #7f5fff88;
}
</style>
