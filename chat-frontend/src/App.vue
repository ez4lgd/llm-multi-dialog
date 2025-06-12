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
    <!-- <header class="app-header">
      <span class="app-title">MyChat</span>
    </header> -->
  </div>
</template>

<style scoped>
.app-root {
  height: 100vh;
  background: linear-gradient(120deg, #181c2f 60%, #232a4d 100%);
  display: flex;
  flex-direction: row;
  overflow: hidden;
  position: relative;
}
.app-header {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 40px;
  background: transparent;
  color: #ececec;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  font-size: 18px;
  font-weight: 500;
  letter-spacing: 0.5px;
  box-shadow: none;
  z-index: 20;
  border-bottom: 1px solid #232323;
  text-shadow: none;
  user-select: none;
  padding: 0 0 0 28px;
  pointer-events: none; /* 允许内容覆盖header */
}
.main-layout {
  height: 100vh;
  width: 100vw;
  display: flex;
  min-width: 0;
  min-height: 0;
  background: transparent;
  position: relative;
  z-index: 1;
}
.main-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  background: rgba(24,28,47,0.92);
  border-radius: 0;
  margin: 0;
  padding: 0;
  box-shadow: none;
  overflow: hidden;
  position: relative;
}
.no-conv {
  color: #b2bfff;
  text-align: center;
  margin-top: 120px;
  font-size: 20px;
  letter-spacing: 1px;
  text-shadow: 0 0 8px #3a7cff99;
}
@media (max-width: 700px) {
  .main-layout {
    flex-direction: column;
  }
  .main-content {
    margin: 0;
    border-radius: 0;
  }
}
</style>
