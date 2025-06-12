<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <span class="sidebar-title">会话列表</span>
      <button class="new-btn" @click="handleNewConversation">新建会话</button>
      <button class="folder-btn" @click="showFolderTree = true" title="收藏夹">📁 收藏夹</button>
    </div>
    <div class="sidebar-list" ref="sidebarListRef" @scroll="handleScroll">
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
      <div
        v-if="!loading && conversations.length > 0 && hasMore && showLoadMoreBtn"
        class="sidebar-load-more sticky-load-more"
      >
        <button class="load-more-btn" :disabled="isLoadingMore" @click="loadMoreConversations">
          {{ isLoadingMore ? '加载中...' : '加载更多' }}
        </button>
        
      </div>
    </div>
<FolderTree
  v-if="showFolderTree"
  :visible="showFolderTree"
  @close="showFolderTree = false"
  @select-conversation="handleSelect"
/>
  </aside>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { v4 as uuidv4 } from 'uuid';
import FolderTree from './FolderTree.vue';

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

const allConversations = ref([]);
const conversations = ref([]);
const loading = ref(false);
const isLoadingMore = ref(false);
const page = ref(1);
const pageSize = 20;
const hasMore = ref(true);
const sidebarListRef = ref(null);
const showLoadMoreBtn = ref(false);

const showFolderTree = ref(false);

async function fetchConversations(reset = false) {
  if (loading.value || isLoadingMore.value) return;
  if (reset) {
    page.value = 1;
    allConversations.value = [];
    conversations.value = [];
    hasMore.value = true;
  }
  if (!hasMore.value) return;
  if (page.value === 1) loading.value = true;
  else isLoadingMore.value = true;
  try {
    const res = await fetch(`/api/v1/conversations/?page=${page.value}&size=${pageSize}`);
    const data = await res.json();
    if (Array.isArray(data.data)) {
      // 批量获取详情
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
      const filtered = detailList.filter(Boolean);
      if (reset) {
        allConversations.value = filtered;
      } else {
        allConversations.value = allConversations.value.concat(filtered);
      }
      conversations.value = allConversations.value.slice();
      // 判断是否还有更多
      if (
        !data.meta ||
        !data.meta.total ||
        allConversations.value.length >= data.meta.total ||
        filtered.length < pageSize
      ) {
        hasMore.value = false;
      } else {
        hasMore.value = true;
      }
      page.value += 1;
    }
  } catch (e) {
    console.error('[fetchConversations] error:', e);
    if (reset) {
      allConversations.value = [];
      conversations.value = [];
    }
    hasMore.value = false;
  } finally {
    loading.value = false;
    isLoadingMore.value = false;
    // 调试：打印实际会话数量
    console.log('[debug] allConversations.length:', allConversations.value.length);
  }
}

function loadMoreConversations() {
  fetchConversations(false);
}

function handleScroll() {
  const el = sidebarListRef.value;
  if (!el) return;
  // 距底部小于30px时自动加载
  const atBottom = el.scrollTop + el.clientHeight >= el.scrollHeight - 30;
  showLoadMoreBtn.value = atBottom && hasMore.value && !loading.value && !isLoadingMore.value;
  if (
    atBottom &&
    !loading.value &&
    !isLoadingMore.value &&
    hasMore.value
  ) {
    loadMoreConversations();
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

onMounted(() => {
  fetchConversations(true);
  setTimeout(() => {
    handleScroll();
  }, 0);
});
</script>

<style scoped>
.sidebar {
  width: 240px;
  background: linear-gradient(135deg, #181c2f 60%, #232a4d 100%);
  border-right: 1.5px solid #2e3657;
  height: 100%;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 16px 0 rgba(0,0,0,0.18);
}
.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 18px 10px 18px;
  border-bottom: 1.5px solid #2e3657;
  background: rgba(24,28,47,0.95);
  box-shadow: 0 2px 8px 0 rgba(0,0,0,0.08);
}
.sidebar-title {
  font-size: 19px;
  font-weight: bold;
  color: #fff;
  letter-spacing: 1px;
  text-shadow: 0 0 8px #3a7cff99;
}
.new-btn {
  background: linear-gradient(90deg, #3a7cff 0%, #7f5fff 100%);
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 6px 16px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 500;
  box-shadow: 0 2px 8px 0 #3a7cff33;
  transition: transform 0.15s, box-shadow 0.15s, background 0.2s;
}
.new-btn:hover {
  background: linear-gradient(90deg, #7f5fff 0%, #3a7cff 100%);
  transform: scale(1.06);
  box-shadow: 0 4px 16px 0 #7f5fff44;
}
.new-btn:active {
  background: #3a7cff;
}
.sidebar-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px 0;
  background: transparent;
}
.sidebar-loading,
.sidebar-empty {
  color: #7f8fa6;
  text-align: center;
  margin-top: 40px;
  font-size: 15px;
  letter-spacing: 1px;
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
  padding: 12px 18px;
  border-radius: 12px;
  margin: 6px 10px;
  cursor: pointer;
  background: rgba(255,255,255,0.04);
  box-shadow: 0 2px 8px 0 rgba(58,124,255,0.04);
  transition: background 0.18s, box-shadow 0.18s;
  border: 1.5px solid transparent;
  position: relative;
  backdrop-filter: blur(2px);
}
.sidebar-item.active {
  background: linear-gradient(90deg, #3a7cff 0%, #7f5fff 100%);
  border: 1.5px solid #7f5fff;
  box-shadow: 0 0 16px 0 #3a7cff55, 0 2px 8px 0 #7f5fff33;
  color: #fff;
}
.sidebar-item.active .item-title {
  color: #fff;
  text-shadow: 0 0 8px #fff8, 0 0 2px #7f5fff;
}
.sidebar-item:hover {
  background: linear-gradient(90deg, #232a4d 0%, #3a7cff 100%);
  box-shadow: 0 0 12px 0 #3a7cff33;
}
.sidebar-item:hover .item-title {
  color: #fff;
  text-shadow: 0 0 8px #3a7cff99;
}
.sidebar-item:hover .delete-btn {
  display: inline-block;
}
.item-main {
  flex: 1;
  min-width: 0;
}
.item-title {
  font-size: 16px;
  font-weight: 600;
  color: #e0e6ff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  letter-spacing: 0.5px;
  transition: color 0.18s, text-shadow 0.18s;
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
  color: #ff4dff;
  font-size: 18px;
  margin-left: 10px;
  cursor: pointer;
  border-radius: 50%;
  padding: 3px 8px;
  transition: background 0.18s, color 0.18s, box-shadow 0.18s;
  box-shadow: 0 0 0 0 transparent;
}
.delete-btn:hover {
  background: #2e3657;
  color: #fff;
  box-shadow: 0 0 8px 0 #ff4dff99;
}

.sidebar-load-more {
  display: flex;
  justify-content: center;
  margin: 10px 0 0 0;
}
/* 固定加载更多按钮在底部 */
.sticky-load-more {
  position: sticky;
  bottom: 0;
  background: linear-gradient(0deg, #181c2f 90%, transparent 100%);
  z-index: 2;
  padding-bottom: 10px;
}
.load-more-btn {
  background: linear-gradient(90deg, #3a7cff 0%, #7f5fff 100%);
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 6px 24px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 500;
  box-shadow: 0 2px 8px 0 #3a7cff33;
  transition: transform 0.15s, box-shadow 0.15s, background 0.2s;
}
.load-more-btn:hover {
  background: linear-gradient(90deg, #7f5fff 0%, #3a7cff 100%);
  transform: scale(1.06);
  box-shadow: 0 4px 16px 0 #7f5fff44;
}
.load-more-btn:active {
  background: #3a7cff;
}
.folder-btn {
  background: linear-gradient(90deg, #f7b731 0%, #f5cd79 100%);
  color: #232a4d;
  border: none;
  border-radius: 8px;
  padding: 6px 12px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 500;
  margin-left: 8px;
  box-shadow: 0 2px 8px 0 #f7b73133;
  transition: transform 0.15s, box-shadow 0.15s, background 0.2s;
}
.folder-btn:hover {
  background: linear-gradient(90deg, #f5cd79 0%, #f7b731 100%);
  transform: scale(1.06);
  box-shadow: 0 4px 16px 0 #f7b73144;
}
.folder-btn:active {
  background: #f7b731;
}
</style>
