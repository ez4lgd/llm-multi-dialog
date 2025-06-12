<template>
  <div class="conversation-tags">
    <span
      v-for="tag in tags"
      :key="tag.id"
      class="tag-chip"
      @dblclick="startEdit(tag)"
      :style="tag._editing ? 'background:#fffbe6; color:#409EFF;' : 'background:#409EFF22; color:#409EFF;'"
    >
      <template v-if="!tag._editing">
        {{ tag.tag }}
        <span class="tag-delete" @click.stop="handleDelete(tag)">×</span>
      </template>
      <template v-else>
        <input
          v-model="tag._editText"
          @keyup.enter="handleUpdate(tag)"
          @blur="handleUpdate(tag)"
          class="tag-edit-input"
        />
      </template>
    </span>
    <input
      v-model="newTagInput"
      @keyup.enter="handleAdd"
      class="tag-input"
      placeholder="添加标签，回车确认"
    />
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue';
import { useConversationTags } from './useConversationTags.js';

const props = defineProps({
  conversationId: { type: String, required: true }
});

const { tags, loadTags, addTag, deleteTag, updateTag } = useConversationTags(props.conversationId);
const newTagInput = ref('');

watch(() => props.conversationId, (v) => {
  if (v) loadTags();
}, { immediate: true });

// 编辑状态管理
function startEdit(tag) {
  tags.value.forEach(t => { t._editing = false; });
  tag._editing = true;
  tag._editText = tag.tag;
  nextTick(() => {
    // 自动聚焦
    const inputs = document.getElementsByClassName('tag-edit-input');
    if (inputs.length) inputs[inputs.length - 1].focus();
  });
}

async function handleAdd() {
  const text = newTagInput.value.trim();
  if (!text) return;
  try {
    await addTag(text);
    newTagInput.value = '';
  } catch (e) {
    alert(e.message);
  }
}

async function handleDelete(tag) {
  if (!confirm('确定要删除该标签吗？')) return;
  try {
    await deleteTag(tag.id);
  } catch (e) {
    alert(e.message);
  }
}

async function handleUpdate(tag) {
  if (!tag._editing) return;
  try {
    await updateTag(tag, tag._editText);
  } catch (e) {
    alert(e.message);
  }
  tag._editing = false;
}
</script>

<style scoped>
.conversation-tags {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
  min-height: 28px;
}
.tag-chip {
  display: inline-flex;
  align-items: center;
  border-radius: 4px;
  padding: 2px 8px;
  margin-right: 2px;
  font-size: 12px;
  cursor: pointer;
  user-select: none;
  transition: background 0.18s, color 0.18s;
  position: relative;
}
.tag-delete {
  margin-left: 4px;
  cursor: pointer;
  color: #ff5c5c;
  font-weight: bold;
  font-size: 13px;
}
.tag-edit-input {
  width: 60px;
  font-size: 12px;
  border: 1px solid #409EFF;
  border-radius: 3px;
  padding: 1px 4px;
}
.tag-input {
  width: 90px;
  font-size: 12px;
  background: #23272f;
  color: #409EFF;
  border: 1px solid #333a4a;
  border-radius: 4px;
  padding: 3px 8px;
  outline: none;
  transition: border 0.18s;
}
.tag-input:focus {
  border: 1.5px solid #409EFF;
}
</style>
