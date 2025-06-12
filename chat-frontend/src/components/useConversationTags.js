import { ref } from 'vue';

/**
 * useConversationTags
 * 封装会话标签的加载、添加、删除、编辑 API 逻辑
 * @param {String} conversationId
 * @returns {Object} { tags, loadTags, addTag, deleteTag, updateTag }
 */
export function useConversationTags(conversationId) {
  const tags = ref([]);
  const loading = ref(false);

  // 加载标签
  async function loadTags() {
    if (!conversationId) {
      tags.value = [];
      return;
    }
    loading.value = true;
    try {
      const res = await fetch(`/api/v1/conversation_tags/?conversation_id=${conversationId}`);
      const data = await res.json();
      tags.value = Array.isArray(data.tags) ? data.tags : [];
    } catch {
      tags.value = [];
    }
    loading.value = false;
  }

  // 添加标签
  async function addTag(tagText) {
    const text = (tagText || '').trim();
    if (!text) return;
    try {
      const res = await fetch('/api/v1/conversation_tags/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ conversation_id: conversationId, tag: text })
      });
      const tagObj = await res.json();
      tags.value.push(tagObj);
      return tagObj;
    } catch (e) {
      throw new Error('添加标签失败: ' + (e?.message || ''));
    }
  }

  // 删除标签
  async function deleteTag(tagId) {
    try {
      await fetch(`/api/v1/conversation_tags/${tagId}`, { method: 'DELETE' });
      tags.value = tags.value.filter(t => t.id !== tagId);
    } catch (e) {
      throw new Error('删除标签失败: ' + (e?.message || ''));
    }
  }

  // 修改标签
  async function updateTag(tagObj, newText) {
    const text = (newText || '').trim();
    if (!text || text === tagObj.tag) return;
    try {
      const res = await fetch(`/api/v1/conversation_tags/${tagObj.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tag: text })
      });
      const updated = await res.json();
      const idx = tags.value.findIndex(t => t.id === tagObj.id);
      if (idx !== -1) tags.value[idx] = updated;
      return updated;
    } catch (e) {
      throw new Error('修改标签失败: ' + (e?.message || ''));
    }
  }

  return {
    tags,
    loading,
    loadTags,
    addTag,
    deleteTag,
    updateTag
  };
}
