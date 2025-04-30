<template>
  <div class="chat-window">
    <div class="messages-area" ref="messagesArea">
      <template v-if="loading">
        <div class="loading">消息加载中...</div>
      </template>
      <template v-else-if="messages.length === 0">
        <div class="empty">暂无消息，快来提问吧！</div>
      </template>
      <div v-else>
        <MessageItem
          v-for="(msg, idx) in messages"
          :key="idx"
          :role="msg.role"
          :content="msg.content"
          :timestamp="msg.timestamp"
        />
      </div>
      <div v-if="aiThinking" class="ai-thinking">AI 正在思考...</div>
      <div v-if="errorMsg" class="error">{{ errorMsg }}</div>
    </div>
    <div class="input-area">
      <input
        v-model="input"
        :disabled="aiThinking || loading"
        class="input"
        type="text"
        placeholder="请输入内容，回车发送"
        @keydown.enter="handleSend"
        @input="errorMsg = ''"
      />
      <button
        class="send-btn"
        :disabled="!input.trim() || aiThinking || loading"
        @click="handleSend"
      >发送</button>
      <button
        class="clear-btn"
        :disabled="messages.length === 0 || aiThinking || loading"
        @click="handleClear"
      >清空</button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick } from 'vue';
import MessageItem from './MessageItem.vue';

const props = defineProps({
  conversationId: { type: String, required: true }
});
const emits = defineEmits(['cleared', 'sent']);

const messages = ref([]);
const input = ref('');
const loading = ref(false);
const aiThinking = ref(false);
const errorMsg = ref('');
const messagesArea = ref(null);

async function fetchMessages() {
  if (!props.conversationId) return;
  loading.value = true;
  errorMsg.value = '';
  try {
    const res = await fetch(`/api/v1/conversations/${props.conversationId}?size=100`);
    const data = await res.json();
    if (data.data && Array.isArray(data.data.messages)) {
      messages.value = data.data.messages;
    } else {
      messages.value = [];
    }
  } catch (e) {
    errorMsg.value = '消息加载失败，请重试';
    messages.value = [];
  } finally {
    loading.value = false;
    await nextTick();
    scrollToBottom();
  }
}

function scrollToBottom() {
  if (messagesArea.value) {
    messagesArea.value.scrollTop = messagesArea.value.scrollHeight;
  }
}

async function handleSend() {
  if (!input.value.trim() || aiThinking.value || loading.value) return;
  aiThinking.value = true;
  errorMsg.value = '';
  try {
    const res = await fetch(`/api/v1/conversations/${props.conversationId}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: input.value.trim() })
    });
    const data = await res.json();
    if (data.data && Array.isArray(data.data.messages)) {
      messages.value = data.data.messages;
      input.value = '';
      emits('sent');
      await nextTick();
      scrollToBottom();
    } else if (data.data && data.data.error) {
      errorMsg.value = data.data.error;
    } else {
      errorMsg.value = 'AI 回复失败，请重试';
    }
  } catch (e) {
    errorMsg.value = '消息发送失败，请重试';
  } finally {
    aiThinking.value = false;
  }
}

async function handleClear() {
  if (!props.conversationId) return;
  loading.value = true;
  errorMsg.value = '';
  try {
    // 直接删除会话再新建
    await fetch(`/api/v1/conversations/${props.conversationId}`, { method: 'DELETE' });
    emits('cleared');
    messages.value = [];
    input.value = '';
  } catch (e) {
    errorMsg.value = '清空失败，请重试';
  } finally {
    loading.value = false;
  }
}

watch(() => props.conversationId, fetchMessages, { immediate: true });
onMounted(fetchMessages);
</script>

<style scoped>
.chat-window {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px #eee;
  margin: 24px 24px 24px 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 48px - 48px);
  min-width: 0;
}
.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 24px 24px 0 24px;
  border-bottom: 1px solid #eee;
  position: relative;
}
.loading,
.empty,
.ai-thinking,
.error {
  text-align: center;
  color: #888;
  margin: 32px 0;
}
.ai-thinking {
  color: #409eff;
  font-weight: bold;
}
.error {
  color: #ff4d4f;
  font-weight: bold;
}
.input-area {
  display: flex;
  align-items: center;
  padding: 16px 24px;
  background: #f5f5f5;
  border-radius: 0 0 8px 8px;
  gap: 12px;
}
.input {
  flex: 1;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 8px 12px;
  font-size: 15px;
  outline: none;
  background: #fff;
}
.input:disabled {
  background: #f7faff;
}
.send-btn {
  background: #409eff;
  color: #fff;
  border: none;
  border-radius: 4px;
  padding: 8px 18px;
  font-size: 15px;
  cursor: pointer;
  transition: background 0.2s;
}
.send-btn:disabled {
  background: #b3d8ff;
  cursor: not-allowed;
}
.clear-btn {
  background: #fff;
  color: #409eff;
  border: 1px solid #409eff;
  border-radius: 4px;
  padding: 8px 14px;
  font-size: 15px;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}
.clear-btn:disabled {
  color: #b3d8ff;
  border-color: #b3d8ff;
  cursor: not-allowed;
}
</style>
