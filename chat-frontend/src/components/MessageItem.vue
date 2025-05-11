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
import { computed, onMounted, nextTick } from 'vue';

// props: role, content, timestamp
const props = defineProps({
  role: { type: String, required: true }, // 'user' | 'assistant'
  content: { type: String, required: true },
  timestamp: { type: String, required: true }
});

// markdown 渲染
import MarkdownIt from 'markdown-it';
import markdownItMathjax3 from 'markdown-it-mathjax3';

// 假设 highlight.js 已通过 CDN 注入（window.hljs），并引入 github-markdown-css
const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: false,
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
md.use(markdownItMathjax3);

// 对消息内容中的 LaTeX 公式进行标准化处理
function normalizeLatex(content) {
  // 块级公式：\[\s*([\s\S]+?)\s*\] => $$ $1 $$
  content = content.replace(/\\\[\s*([\s\S]+?)\s*\\\]/g, (match, p1) => `$$\n${p1}\n$$`);
  // 行内公式：\(\s*([^\)]+?)\s*\) => $ $1 $
  content = content.replace(/\\\(\s*([^\)]+?)\s*\\\)/g, (match, p1) => `$${p1}$`);
  // 保证每个块级公式 $$...$$ 前后有空行，避免与列表/标题等混淆
  content = content.replace(/([^\n])(\$\$[\s\S]+?\$\$)/g, '$1\n$2'); // 前补空行
  content = content.replace(/(\$\$[\s\S]+?\$\$)([^\n])/g, '$1\n$2'); // 后补空行
  // 合并多余空行
  content = content.replace(/\n{3,}/g, '\n\n');
  return content;
}

const renderedContent = computed(() => md.render(normalizeLatex(props.content)));

// 代码块一键复制
onMounted(() => {
  nextTick(() => {
    const bubble = document.querySelectorAll('.bubble.markdown-body');
    bubble.forEach(bub => {
      // 只处理当前消息节点
      // 由于组件复用，需限定作用域
      const codes = bub.querySelectorAll('pre.hljs');
      codes.forEach(pre => {
        // 避免重复插入
        if (pre.querySelector('.copy-btn')) return;
        // 创建按钮
        const btn = document.createElement('button');
        btn.innerText = '复制代码';
        btn.className = 'copy-btn';
        btn.style.position = 'absolute';
        btn.style.top = '8px';
        btn.style.right = '12px';
        btn.style.zIndex = '10';
        btn.style.fontSize = '12px';
        btn.style.padding = '2px 10px';
        btn.style.background = '#3a7cff';
        btn.style.color = '#fff';
        btn.style.border = 'none';
        btn.style.borderRadius = '6px';
        btn.style.cursor = 'pointer';
        btn.style.opacity = '0.85';
        btn.style.transition = 'opacity 0.18s';
        btn.onmouseenter = () => btn.style.opacity = '1';
        btn.onmouseleave = () => btn.style.opacity = '0.85';
        btn.onclick = async (e) => {
          e.stopPropagation();
          const code = pre.querySelector('code');
          if (!code) return;
          try {
            await navigator.clipboard.writeText(code.innerText);
            btn.innerText = '已复制!';
            setTimeout(() => { btn.innerText = '复制代码'; }, 1200);
          } catch {
            btn.innerText = '复制失败';
            setTimeout(() => { btn.innerText = '复制代码'; }, 1200);
          }
        };
        pre.style.position = 'relative';
        pre.appendChild(btn);
      });
    });
  });
});

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
