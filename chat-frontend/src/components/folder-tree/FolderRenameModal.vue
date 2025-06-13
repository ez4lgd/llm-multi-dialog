<template>
  <div v-if="renamingFolder" class="rename-modal">
    <input
      :value="renameName"
      @input="$emit('update:renameName', $event.target.value)"
      placeholder="新名称"
      @keyup.enter="$emit('confirmRename')"
    />
    <button @click="$emit('confirmRename')">确定</button>
    <button @click="$emit('cancelRename')">取消</button>
  </div>
</template>

<script setup>
defineProps({
  renamingFolder: {
    type: Object,
    default: null
  },
  renameName: {
    type: String,
    required: true
  }
});
defineEmits(['confirmRename', 'cancelRename', 'update:renameName']);
</script>

<style scoped>
.rename-modal {
  position: fixed;
  left: 50%; top: 50%;
  transform: translate(-50%, -50%);
  background: #23272f;
  border-radius: 10px;
  box-shadow: 0 2px 24px 0 #0008;
  padding: 28px 38px;
  z-index: 1100;
  display: flex;
  gap: 16px;
  align-items: center;
  border: 1px solid #333a4a;
}
.rename-modal input {
  background: #1e1e23;
  color: #fff;
  border: 1px solid #333a4a;
  border-radius: 5px;
  padding: 6px 10px;
  font-size: 14px;
  outline: none;
  transition: border 0.18s;
}
.rename-modal input:focus {
  border: 1.5px solid #409EFF;
}
.rename-modal button {
  background: linear-gradient(90deg, #409EFF 60%, #7f5fff 100%);
  color: #fff;
  border: none;
  border-radius: 5px;
  padding: 6px 18px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.18s, color 0.18s;
}
</style>
