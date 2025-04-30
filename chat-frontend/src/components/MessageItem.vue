<template>
  <div :class="['message-item', roleClass]">
    <div class="avatar">{{ role === 'user' ? '🧑' : '🤖' }}</div>
    <div class="content">
      <div class="bubble markdown-body" v-html="renderedContent"></div>
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

// 假设 highlight.js 已通过 CDN 注入（window.hljs），并引入 github-markdown-css
const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true,
  highlight: function (str, lang) {
    if (window.hljs) {
      if (lang && window.hljs.getLanguage(lang)) {
        try {
          return '<pre class="hljs"><code>' +
            window.hljs.highlight(str, { language: lang, ignoreIllegals: true }).value +
            '</code></pre>';
        } catch (__) {}
      }
      // 未指定语言时自动高亮
      try {
        return '<pre class="hljs"><code>' +
          window.hljs.highlightAuto(str).value +
          '</code></pre>';
      } catch (__) {}
    }
    // 未加载 highlight.js 时降级
    return '<pre class="hljs"><code>' + md.utils.escapeHtml(str) + '</code></pre>';
  }
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
  margin-bottom: 20px;
}
.avatar {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #3a7cff 0%, #7f5fff 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  margin-right: 14px;
  flex-shrink: 0;
  color: #fff;
  box-shadow: 0 2px 8px #3a7cff33;
  border: 2px solid #232a4d;
  transition: box-shadow 0.18s;
}
.user .avatar {
  background: linear-gradient(135deg, #3a7cff 0%, #7f5fff 100%);
  box-shadow: 0 2px 12px #3a7cff55;
}
.assistant .avatar {
  background: linear-gradient(135deg, #232a4d 0%, #3a7cff 100%);
  box-shadow: 0 2px 12px #7f5fff55;
}
.content {
  flex: 1;
  min-width: 0;
}
.bubble.markdown-body {
  /* 继承气泡样式，覆盖 github-markdown-css 的背景和字体色 */
  background: inherit !important;
  color: inherit !important;
  border-radius: 14px;
  padding: 14px 18px;
  font-size: 16px;
  word-break: break-word;
  box-shadow: 0 2px 12px #3a7cff22, 0 1px 2px #7f5fff22;
  margin-bottom: 2px;
  position: relative;
  transition: background 0.18s, color 0.18s;
  line-height: 1.7;
  border: 1.5px solid transparent;
  backdrop-filter: blur(1.5px);
}
.user .bubble {
  background: linear-gradient(90deg, #232a4d 0%, #3a7cff 100%);
  color: #fff;
  border: 1.5px solid #3a7cff;
  text-shadow: 0 0 8px #3a7cff33;
}
.assistant .bubble {
  background: linear-gradient(90deg, #232a4d 0%, #7f5fff 100%);
  color: #fff;
  border: 1.5px solid #7f5fff;
  text-shadow: 0 0 8px #7f5fff33;
}
.timestamp {
  font-size: 12px;
  color: #b2bfff;
  margin-top: 6px;
  text-align: right;
  text-shadow: 0 0 6px #3a7cff33;
  letter-spacing: 0.5px;
}
</style>
