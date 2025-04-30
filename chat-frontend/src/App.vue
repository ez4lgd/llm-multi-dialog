<script setup>
import { ref, onMounted } from 'vue';
import ConversationSidebar from './components/ConversationSidebar.vue';
import ChatWindow from './components/ChatWindow.vue';

const currentId = ref('');
const sidebarKey = ref(0); // 用于强制刷新侧边栏

function handleSelect(id) {
  currentId.value = id;
}
function handleNew(id) {
  if (id) currentId.value = id;
  sidebarKey.value += 1; // 强制刷新
}
function handleDeleted(id) {
  // 删除后自动切换到第一个会话，由侧边栏内部逻辑保证
  sidebarKey.value += 1;
}
function handleCleared() {
  // 清空即删除当前会话，侧边栏会自动新建并切换
  sidebarKey.value += 1;
}
function handleSent() {
  // 发送消息后可刷新侧边栏摘要
  sidebarKey.value += 1;
}

// 首次加载时自动选中第一个会话
onMounted(async () => {
  try {
    const res = await fetch('/api/v1/conversations/');
    const data = await res.json();
    if (Array.isArray(data.data) && data.data.length > 0) {
      currentId.value = data.data[0];
    } else {
      console.log('No conversations found');
    }
  } catch (e) {
    console.error('Fetch conversations error:', e);
  }
});
</script>

<template>
  <div class="app-root">
    <header class="app-header">
      <span class="app-title">多轮对话演示系统</span>
    </header>
    <div class="main-layout">
      <ConversationSidebar
        :key="sidebarKey"
        :activeId="currentId"
        @select="handleSelect"
        @new="handleNew"
        @deleted="handleDeleted"
      />
      <div class="main-content">
        <ChatWindow
          v-if="currentId"
          :conversationId="currentId"
          @cleared="handleCleared"
          @sent="handleSent"
        />
        <div v-else class="no-conv">暂无会话，请新建会话</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.app-root {
  min-height: 100vh;
  background: #f5f5f5;
  display: flex;
  flex-direction: column;
}
.app-header {
  height: 48px;
  background: #409eff;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: bold;
  letter-spacing: 2px;
  box-shadow: 0 2px 4px #e0e0e0;
  z-index: 10;
}
.main-layout {
  flex: 1;
  display: flex;
  min-width: 0;
  min-height: 0;
}
.main-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}
.no-conv {
  color: #888;
  text-align: center;
  margin-top: 120px;
  font-size: 18px;
}
@media (max-width: 700px) {
  .main-layout {
    flex-direction: column;
  }
  .main-content {
    margin: 0;
  }
}
</style>
