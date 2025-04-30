<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <span class="sidebar-title">会话列表</span>
      <button class="new-btn" @click="handleNewConversation">新建会话</button>
    </div>
    <div class="sidebar-list">
      <template v-if="loading">
        <div class="sidebar-loading">加载中...</div>
      </template>
      <template v-else-if="conversations.length === 0">
        <div class="sidebar-empty">暂无会话</div>
      </template>
      <ul v-else>
        <li
          v-for="conv in conversations"
          :key="conv.conversation_id"
          :class="['sidebar-item', { active: conv.conversation_id === activeId }]"
          @click="handleSelect(conv.conversation_id)"
        >
          <div class="item-main">
            <div class="item-title">{{ summaryTitle(conv.summary) }}</div>
            <!-- <div class="item-summary">{{ conv.summary }}</div> -->
          </div>
          <button
            class="delete-btn"
            @click.stop="handleDelete(conv.conversation_id)"
            title="删除会话"
          >🗑️</button>
        </li>
      </ul>
    </div>
  </aside>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { v4 as uuidv4 } from 'uuid';

/**
 * 获取 summary 前 10 个字作为标题，若为空则返回“无摘要”
 */
function summaryTitle(summary) {
  if (!summary) return '无摘要';
  return summary.length > 10 ? summary.slice(0, 10) : summary;
}

const props = defineProps({
  activeId: String
});
const emits = defineEmits(['select', 'new', 'deleted']);

const conversations = ref([]);
const loading = ref(false);

async function fetchConversations() {
  loading.value = true;
  console.log('[fetchConversations] start');
  try {
    const res = await fetch('/api/v1/conversations/');
    const data = await res.json();
    if (Array.isArray(data.data)) {
      // 需批量获取详情
      const detailList = await Promise.all(
        data.data.map(async (id) => {
          const dRes = await fetch(`/api/v1/conversations/${id}?size=1`);
          const dData = await dRes.json();
         return dData.data
            ? {
                conversation_id: dData.data.conversation_id,
                name: dData.data.name,
                summary: dData.data.summary || '',
              }
            : null;
        })
      );
      conversations.value = detailList.filter(Boolean);
    }
  } catch (e) {
    console.error('[fetchConversations] error:', e);
    conversations.value = [];
  } finally {
    loading.value = false;
  }
}

function handleSelect(id) {
  emits('select', id);
}
async function handleNewConversation() {
  // 生成唯一 id，结合 uuid 和时间戳
  const newId = `${uuidv4()}-${Date.now()}`;
  emits('new', newId);
  // 不需要立即 fetchConversations，等发送消息后自动创建
}
async function handleDelete(id) {
  await fetch(`/api/v1/conversations/${id}`, { method: 'DELETE' });
  emits('deleted', id);
  await fetchConversations();
}

onMounted(fetchConversations);
watch(() => props.activeId, fetchConversations);
</script>

<style scoped>
.sidebar {
  width: 240px;
  background: #f7faff;
  border-right: 1px solid #e0e0e0;
  height: 100vh;
  display: flex;
  flex-direction: column;
}
.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 16px 8px 16px;
  border-bottom: 1px solid #e0e0e0;
  background: #f7faff;
}
.sidebar-title {
  font-size: 18px;
  font-weight: bold;
}
.new-btn {
  background: #409eff;
  color: #fff;
  border: none;
  border-radius: 4px;
  padding: 4px 12px;
  cursor: pointer;
  font-size: 14px;
}
.new-btn:active {
  background: #337ecc;
}
.sidebar-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}
.sidebar-loading,
.sidebar-empty {
  color: #999;
  text-align: center;
  margin-top: 32px;
}
ul {
  list-style: none;
  margin: 0;
  padding: 0;
}
.sidebar-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  border-radius: 8px;
  margin: 4px 8px;
  cursor: pointer;
  transition: background 0.2s;
}
.sidebar-item.active {
  background: #dbefff;
}
.sidebar-item:hover .delete-btn {
  display: inline-block;
}
.item-main {
  flex: 1;
  min-width: 0;
}
.item-title {
  font-size: 15px;
  font-weight: 500;
  color: #222;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.item-summary {
  font-size: 13px;
  color: #888;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.delete-btn {
  display: none;
  background: none;
  border: none;
  color: #ff4d4f;
  font-size: 16px;
  margin-left: 8px;
  cursor: pointer;
  border-radius: 50%;
  padding: 2px 6px;
  transition: background 0.2s;
}
.delete-btn:hover {
  background: #ffeaea;
}
</style>
