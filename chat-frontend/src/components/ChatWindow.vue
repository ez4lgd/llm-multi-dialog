<template>
  <div class="chat-window">
    <ModelConfigPanel
      :models="models"
      :config="config"
      @update:config="handleConfigUpdate"
    />
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
      <textarea
        v-model="input"
        :disabled="aiThinking || loading"
        class="input"
        placeholder="请输入内容，回车发送，Shift+Enter换行"
        rows="1"
        ref="inputRef"
        @keydown="handleInputKeydown"
        @input="handleInput"
        style="resize: none;"
      ></textarea>
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
import ModelConfigPanel from './ModelConfigPanel.vue';

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
const inputRef = ref(null);

const models = ref([]);
const config = ref({ model: '' });

async function handleConfigUpdate(newConfig) {
  config.value = { ...newConfig };
  try {
    await fetch(`/api/v1/conversations/${props.conversationId}/set_config`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config.value)
    });
    // 更新后重新拉取会话数据，确保同步
    await fetchConversationAndMessages();
  } catch (e) {
    // 忽略错误
  }
}

async function fetchModels() {
  try {
    const res = await fetch('/api/v1/models');
    const data = await res.json();
    if (Array.isArray(data.data)) {
      models.value = data.data;
    }
  } catch (e) {
    // 忽略错误，保留空列表
  }
}

async function fetchConversationAndMessages() {
  if (!props.conversationId) return;
  loading.value = true;
  errorMsg.value = '';
  try {
    const res = await fetch(`/api/v1/conversations/${props.conversationId}?size=100`);
    const data = await res.json();
    if (data.data) {
      // 兼容老数据
      messages.value = Array.isArray(data.data.messages) ? data.data.messages : [];
      if (data.data.config) {
        config.value = { ...data.data.config };
      } else if (data.data.model) {
        config.value = { model: data.data.model };
      } else if (models.value.length > 0) {
        config.value = { model: models.value[0] };
      }
    } else {
      messages.value = [];
    }
  } catch (e) {
    errorMsg.value = '消息加载失败，请重试';
    messages.value = [];
  } finally {
    loading.value = false;
    await nextTick();
    // 进入会话时不再自动滚动到底部
  }
}

function scrollToBottom() {
  if (messagesArea.value) {
    // 优先使用平滑滚动
    if (typeof messagesArea.value.scrollTo === 'function') {
      messagesArea.value.scrollTo({
        top: messagesArea.value.scrollHeight,
        behavior: 'smooth'
      });
    } else {
      messagesArea.value.scrollTop = messagesArea.value.scrollHeight;
    }
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
      body: JSON.stringify({ 
        content: input.value.trim(),
        model: config.value.model
      })
    });
    const data = await res.json();
    if (data.data && Array.isArray(data.data.messages)) {
      messages.value = data.data.messages;
      input.value = '';
      emits('sent');
      // 发送消息后不再自动滚动
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

/**
 * 输入框自适应高度
 */
function autoResizeInput() {
  const el = inputRef.value;
  if (!el) return;
  el.style.height = 'auto';
  // 最大高度与CSS一致
  const maxHeight = 120;
  el.style.height = Math.min(el.scrollHeight, maxHeight) + 'px';
  el.style.overflowY = el.scrollHeight > maxHeight ? 'auto' : 'hidden';
}

// 处理输入框回车和换行
function handleInputKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    handleSend();
  }
  // Shift+Enter 默认行为即为换行，无需处理
}

/**
 * 输入事件处理，清空错误并自适应高度
 */
function handleInput(e) {
  errorMsg.value = '';
  autoResizeInput();
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

watch(() => props.conversationId, () => {
  fetchModels().then(() => {
    fetchConversationAndMessages();
  });
}, { immediate: true });

onMounted(() => {
  fetchModels().then(() => {
    fetchConversationAndMessages();
  });
  nextTick(() => {
    autoResizeInput();
  });
});
</script>

<style scoped>
.chat-window {
  background: rgba(24,28,47,0.98);
  border-radius: 18px;
  box-shadow: 0 4px 32px #3a7cff22, 0 2px 8px #7f5fff22;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  height: 100%;
  min-width: 0;
  border: 1.5px solid #2e3657;
  overflow: hidden;
  position: relative;
}
.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 28px 28px 0 28px;
  border-bottom: 1.5px solid #2e3657;
  position: relative;
  background: transparent;
  scroll-behavior: smooth;
}
.loading,
.empty,
.ai-thinking,
.error {
  text-align: center;
  color: #b2bfff;
  margin: 36px 0;
  font-size: 16px;
  letter-spacing: 0.5px;
  text-shadow: 0 0 8px #3a7cff33;
}
.ai-thinking {
  color: #7f5fff;
  font-weight: bold;
  text-shadow: 0 0 8px #7f5fff99;
}
.error {
  color: #ff4dff;
  font-weight: bold;
  text-shadow: 0 0 8px #ff4dff99;
}
.input-area {
  display: flex;
  align-items: center;
  padding: 18px 28px;
  background: rgba(36,40,66,0.98);
  border-radius: 0 0 18px 18px;
  gap: 14px;
  box-shadow: 0 -2px 12px #3a7cff11;
}
.input {
  flex: 1;
  border: 1.5px solid #3a7cff55;
  border-radius: 8px;
  padding: 10px 16px;
  font-size: 16px;
  outline: none;
  background: rgba(24,28,47,0.92);
  color: #e0e6ff;
  transition: border 0.18s, background 0.18s;
  box-shadow: 0 2px 8px #3a7cff11;
  min-height: 40px;
  max-height: 120px;
  line-height: 1.6;
  resize: none;
  overflow-y: auto;
  font-family: inherit;
}
.input:focus {
  border: 1.5px solid #7f5fff;
  background: rgba(36,40,66,1);
}
.input:disabled {
  background: #232a4d;
  color: #888;
}
.send-btn {
  background: linear-gradient(90deg, #3a7cff 0%, #7f5fff 100%);
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 10px 22px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  box-shadow: 0 2px 8px #3a7cff33;
  transition: background 0.18s, transform 0.15s, box-shadow 0.15s;
}
.send-btn:hover:enabled {
  background: linear-gradient(90deg, #7f5fff 0%, #3a7cff 100%);
  transform: scale(1.06);
  box-shadow: 0 4px 16px 0 #7f5fff44;
}
.send-btn:disabled {
  background: #2e3657;
  color: #888;
  cursor: not-allowed;
  box-shadow: none;
}
.clear-btn {
  background: transparent;
  color: #7f5fff;
  border: 1.5px solid #7f5fff;
  border-radius: 8px;
  padding: 10px 18px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.18s, color 0.18s, border 0.18s, transform 0.15s;
  box-shadow: 0 2px 8px #7f5fff22;
}
.clear-btn:hover:enabled {
  background: #7f5fff22;
  color: #fff;
  border: 1.5px solid #fff;
  transform: scale(1.04);
}
.clear-btn:disabled {
  color: #888;
  border-color: #2e3657;
  cursor: not-allowed;
  background: transparent;
  box-shadow: none;
}
</style>
