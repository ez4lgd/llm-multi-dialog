<template>
  <div :class="['message-item', roleClass]">
    <div class="avatar">{{ role === 'user' ? '🧑' : '🤖' }}</div>
    <div class="content">
      <div class="bubble" v-html="renderedContent"></div>
      <div class="timestamp">{{ timeStr }}</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

// props: role, content, timestamp
const props = defineProps({
  role: { type: String, required: true }, // 'user' | 'assistant'
  content: { type: String, required: true },
  timestamp: { type: String, required: true }
});

// markdown 渲染
import MarkdownIt from 'markdown-it';
const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true
});
const renderedContent = computed(() => md.render(props.content));

// 角色样式
const roleClass = computed(() => (props.role === 'user' ? 'user' : 'assistant'));

// 时间格式
function formatTime(ts) {
  if (!ts) return '';
  const d = new Date(ts);
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}
const timeStr = computed(() => formatTime(props.timestamp));
</script>

<style scoped>
.message-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 16px;
}
.avatar {
  width: 32px;
  height: 32px;
  background: #dbefff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  margin-right: 12px;
  flex-shrink: 0;
}
.content {
  flex: 1;
  min-width: 0;
}
.bubble {
  background: #f5f5f5;
  border-radius: 8px;
  padding: 10px 14px;
  font-size: 15px;
  color: #222;
  word-break: break-word;
  box-shadow: 0 1px 2px #eee;
}
.user .bubble {
  background: #e6f7ff;
  color: #222;
}
.assistant .bubble {
  background: #fff;
  color: #222;
}
.timestamp {
  font-size: 12px;
  color: #aaa;
  margin-top: 4px;
  text-align: right;
}
</style>
