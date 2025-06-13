<template>
  <div class="folder-tree-modal" v-if="visible">
    <div class="folder-tree-content folder-tree-flex">
      <div class="folder-tree-header">
        <span>收藏夹</span>
        <button class="close-btn" @click="close">×</button>
      </div>
      <div class="folder-tree-body folder-tree-body-flex">
        <!-- 左侧目录栏 -->
        <FolderSidebar
          :folders="folders"
          :selected-folder-id="selectedFolderId"
          @update:selectedFolderId="selectedFolderId = $event"
        />
        <!-- 右侧内容区 -->
        <div class="folder-tree-main">
          <FolderActions
            :new-folder-name="newFolderName"
            :creating="creating"
            @createFolder="createFolder"
            @update:newFolderName="val => newFolderName = val"
          />
          <FolderList
            :folders="folders"
            :selected-folder-id="selectedFolderId"
            :conversation-id="conversationId"
            :summaries="summaries"
            @addConvToFolder="addConvToFolder"
            @removeConvFromFolder="removeConvFromFolder"
            @startRename="startRename"
            @deleteFolder="deleteFolder"
            @removeConv="removeConv"
            @selectConversation="handleSelectConversation"
          />
        </div>
      </div>
      <FolderRenameModal
        :renaming-folder="renamingFolder"
        :rename-name="renameName"
        @confirmRename="confirmRename"
        @cancelRename="cancelRename"
        @update:renameName="val => renameName = val"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import FolderSidebar from './FolderSidebar.vue';
import FolderList from './FolderList.vue';
import FolderActions from './FolderActions.vue';
import FolderRenameModal from './FolderRenameModal.vue';

const props = defineProps({
  visible: Boolean,
  conversationId: String // 可选，传入则支持对该会话收藏/移除
});
const emits = defineEmits(['close', 'select-conversation']);

const summaries = ref({});
const selectedFolderId = ref('all');
const folders = ref([]);
const newFolderName = ref('');
const creating = ref(false);
const renamingFolder = ref(null);
const renameName = ref('');

function close() {
  emits('close');
}

function handleSelectConversation(cid) {
  emits('select-conversation', cid);
}

function getSummary(cid) {
  return summaries.value[cid] || cid;
}

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

async function fetchFolders() {
  const res = await fetch('/api/v1/folders/');
  const data = await res.json();
  folders.value = Array.isArray(data.data) ? data.data : [];
  await fetchSummaries();
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
  if (v) selectedFolderId.value = 'all';
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
  min-width: 520px;
  min-height: 340px;
  border-radius: 10px;
  box-shadow: 0 4px 32px 0 #0008;
  overflow: hidden;
  background: none;
  display: flex;
  flex-direction: column;
  height: 90vh;
  max-height: 90vh;
}
.folder-tree-flex {
  display: flex;
  flex-direction: column;
  height: 100%;
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
.folder-tree-body {
  background: #1e1e23;
  color: #e6e6e6;
  flex: 1;
  display: flex;
  flex-direction: row;
  min-height: 0;
  min-width: 0;
  padding: 0;
}
.folder-tree-body-flex {
  display: flex;
  flex-direction: row;
  height: 100%;
  min-height: 0;
  min-width: 0;
}
.folder-tree-main {
  flex: 1;
  padding: 20px 28px;
  min-width: 0;
  min-height: 0;
  overflow-y: auto;
  height: 100%;
  background: #1e1e23;
  display: flex;
  flex-direction: column;
}
.close-btn {
  background: none;
  border: none;
  color: #fff;
  font-size: 22px;
  cursor: pointer;
  padding: 0 8px;
  line-height: 1;
}
</style>
