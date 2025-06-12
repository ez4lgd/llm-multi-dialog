<template>
  <div class="folder-tree-modal" v-if="visible">
    <div class="folder-tree-content">
      <div class="folder-tree-header">
        <span>收藏夹</span>
        <button class="close-btn" @click="close">×</button>
      </div>
      <div class="folder-tree-body">
      <div class="folder-tree-actions">
        <input v-model="newFolderName" placeholder="新建收藏夹名称" @keyup.enter="createFolder" />
        <button @click="createFolder" :disabled="creating">新建</button>
      </div>
      <ul class="folder-list">
        <li v-for="folder in folders" :key="folder.folder_id" class="folder-item">
          <span class="folder-name" :title="folder.name">{{ folder.name }}</span>
          <template v-if="conversationId">
            <button
              v-if="folder.conversation_ids.includes(conversationId)"
              class="remove-btn"
              @click="removeConvFromFolder(folder, conversationId)"
            >移除当前会话</button>
            <button
              v-else
              class="add-btn"
              @click="addConvToFolder(folder, conversationId)"
            >添加当前会话</button>
          </template>
          <button v-if="!folder.is_default" class="rename-btn" @click="startRename(folder)">重命名</button>
          <button v-if="!folder.is_default" class="delete-btn" @click="deleteFolder(folder)">删除</button>
<ul class="conv-list">
  <li v-for="cid in folder.conversation_ids" :key="cid" class="conv-item">
    <span class="conv-summary" @click="handleSelectConversation(cid)" style="cursor:pointer; color:#409EFF; text-decoration:underline;">
      {{ getSummary(cid) }}
    </span>
    <input
      v-model="tags[cid]"
      @change="saveTag(cid)"
      class="tag-input"
      placeholder="自定义标签"
      style="margin-left:8px; width:90px; font-size:12px;"
    />
    <button class="remove-btn" @click="removeConv(folder, cid)">移除</button>
  </li>
</ul>
        </li>
      </ul>
      <div v-if="folders.length === 0" class="empty-tip">暂无收藏夹</div>
    </div>
    <div v-if="renamingFolder" class="rename-modal">
      <input v-model="renameName" placeholder="新名称" @keyup.enter="confirmRename" />
      <button @click="confirmRename">确定</button>
      <button @click="cancelRename">取消</button>
    </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';

const props = defineProps({
  visible: Boolean,
  conversationId: String // 可选，传入则支持对该会话收藏/移除
});
const emits = defineEmits(['close', 'select-conversation']);

// 会话摘要和标签
const summaries = ref({});
const tags = ref({});

// 获取 summary
function getSummary(cid) {
  return summaries.value[cid] || cid;
}

// 标签持久化
function loadTags() {
  tags.value = {};
  Object.keys(localStorage)
    .filter(k => k.startsWith('conv_tag_'))
    .forEach(k => {
      const cid = k.replace('conv_tag_', '');
      tags.value[cid] = localStorage.getItem(k) || '';
    });
}
function saveTag(cid) {
  if (tags.value[cid]) {
    localStorage.setItem('conv_tag_' + cid, tags.value[cid]);
  } else {
    localStorage.removeItem('conv_tag_' + cid);
  }
}

// 选中会话
function handleSelectConversation(cid) {
  emits('select-conversation', cid);
}

// 批量获取 summary
async function fetchSummaries() {
  const cids = [];
  folders.value.forEach(f => {
    f.conversation_ids.forEach(cid => {
      if (!cids.includes(cid)) cids.push(cid);
    });
  });
  const summaryMap = {};
  await Promise.all(
    cids.map(async (cid) => {
      try {
        const res = await fetch(`/api/v1/conversations/${cid}?size=1`);
        const data = await res.json();
        summaryMap[cid] = data?.data?.summary || cid;
      } catch {
        summaryMap[cid] = cid;
      }
    })
  );
  summaries.value = summaryMap;
}

const folders = ref([]);
const newFolderName = ref('');
const creating = ref(false);

const renamingFolder = ref(null);
const renameName = ref('');

function close() {
  emits('close');
}

async function fetchFolders() {
  const res = await fetch('/api/v1/folders/');
  const data = await res.json();
  folders.value = Array.isArray(data.data) ? data.data : [];
  await fetchSummaries();
  loadTags();
}

async function createFolder() {
  if (!newFolderName.value.trim()) return;
  creating.value = true;
  try {
    await fetch('/api/v1/folders/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: newFolderName.value.trim() })
    });
    newFolderName.value = '';
    await fetchFolders();
  } catch (e) {
    alert('新建失败：' + (e?.message || ''));
  }
  creating.value = false;
}

function startRename(folder) {
  renamingFolder.value = folder;
  renameName.value = folder.name;
}
async function confirmRename() {
  if (!renamingFolder.value || !renameName.value.trim()) return;
  try {
    await fetch(`/api/v1/folders/${renamingFolder.value.folder_id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: renameName.value.trim() })
    });
    renamingFolder.value = null;
    renameName.value = '';
    await fetchFolders();
  } catch (e) {
    alert('重命名失败：' + (e?.message || ''));
  }
}
function cancelRename() {
  renamingFolder.value = null;
  renameName.value = '';
}
async function deleteFolder(folder) {
  if (!confirm('确定要删除该收藏夹吗？')) return;
  try {
    await fetch(`/api/v1/folders/${folder.folder_id}`, { method: 'DELETE' });
    await fetchFolders();
  } catch (e) {
    alert('删除失败：' + (e?.message || ''));
  }
}
async function removeConv(folder, cid) {
  try {
    await fetch(`/api/v1/folders/${folder.folder_id}/remove`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ conversation_id: cid })
    });
    await fetchFolders();
  } catch (e) {
    alert('移除失败：' + (e?.message || ''));
  }
}

// 添加/移除当前会话到收藏夹
async function addConvToFolder(folder, cid) {
  try {
    await fetch(`/api/v1/folders/${folder.folder_id}/add`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ conversation_id: cid })
    });
    await fetchFolders();
  } catch (e) {
    alert('添加失败：' + (e?.message || ''));
  }
}
async function removeConvFromFolder(folder, cid) {
  try {
    await fetch(`/api/v1/folders/${folder.folder_id}/remove`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ conversation_id: cid })
    });
    await fetchFolders();
  } catch (e) {
    alert('移除失败：' + (e?.message || ''));
  }
}

watch(() => props.visible, (v) => {
  if (v) fetchFolders();
});
onMounted(() => {
  if (props.visible) fetchFolders();
});
</script>

<style scoped>
.folder-tree-modal {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(20,22,30,0.85);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}
.folder-tree-content {
  display: flex;
  flex-direction: column;
  min-width: 420px;
  min-height: 320px;
  border-radius: 10px;
  box-shadow: 0 4px 32px 0 #0008;
  overflow: hidden;
  background: none;
}
.folder-tree-header {
  background: #23272f;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  padding: 12px 24px;
  border-top-left-radius: 10px;
  border-top-right-radius: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #333a4a;
}
.close-btn {
  background: none;
  border: none;
  color: #fff;
  font-size: 22px;
  cursor: pointer;
  transition: color 0.18s;
}
.close-btn:hover {
  color: #ff5c5c;
}
.folder-tree-body {
  background: #1e1e23;
  padding: 20px 28px;
  color: #e6e6e6;
}
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
.rename-modal {
  position: fixed;
  left: 50%; top: 50%;
  transform: translate(-50%, -50%);
  background: #23272f;
  border-radius: 10px;
  box-shadow: 0 2px 24px 0 #0008;
  padding: 28px 38px;
  z-index: 1100;
  display: flex;
  gap: 16px;
  align-items: center;
  border: 1px solid #333a4a;
}
.rename-modal input {
  background: #1e1e23;
  color: #fff;
  border: 1px solid #333a4a;
  border-radius: 5px;
  padding: 6px 10px;
  font-size: 14px;
  outline: none;
  transition: border 0.18s;
}
.rename-modal input:focus {
  border: 1.5px solid #409EFF;
}
.rename-modal button {
  background: linear-gradient(90deg, #409EFF 60%, #7f5fff 100%);
  color: #fff;
  border: none;
  border-radius: 5px;
  padding: 6px 18px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.18s, color 0.18s;
}
.tag-input {
  background: #23272f;
  color: #fff;
  border: 1px solid #333a4a;
  border-radius: 4px;
  padding: 3px 8px;
  outline: none;
  font-size: 13px;
  transition: border 0.18s;
}
.tag-input:focus {
  border: 1.5px solid #409EFF;
}
.conv-summary {
  cursor: pointer;
  color: #409EFF;
  text-decoration: underline;
  transition: color 0.18s;
}
.conv-summary:hover {
  color: #7f5fff;
  text-shadow: 0 0 2px #7f5fff88;
}
</style>
