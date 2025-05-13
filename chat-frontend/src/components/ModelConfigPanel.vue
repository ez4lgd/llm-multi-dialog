<template>
  <div class="model-config-panel">
    <label for="model-select">选择模型：</label>
    <select id="model-select" v-model="localConfig.model" @change="emitConfig">
      <option v-for="m in models" :key="m" :value="m">{{ m }}</option>
    </select>
    <!-- 预留：后续可扩展更多参数 -->
    <!--
    <div class="param-row">
      <label for="temperature">温度：</label>
      <input id="temperature" type="number" step="0.01" min="0" max="2" v-model.number="localConfig.temperature" @change="emitConfig" />
    </div>
    <div class="param-row">
      <label for="systemPrompt">System Prompt：</label>
      <input id="systemPrompt" type="text" v-model="localConfig.systemPrompt" @change="emitConfig" />
    </div>
    -->
  </div>
</template>

<script setup>
import { reactive, watch, toRefs } from 'vue';

const props = defineProps({
  models: { type: Array, required: true },
  config: { type: Object, required: true }
});
const emits = defineEmits(['update:config']);

const localConfig = reactive({ ...props.config });

watch(
  () => props.config,
  (newConfig) => {
    Object.assign(localConfig, newConfig);
  }
);

function emitConfig() {
  emits('update:config', { ...localConfig });
}
</script>

<style scoped>
.model-config-panel {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 12px;
}
label {
  color: #b2bfff;
  font-size: 15px;
  margin-right: 6px;
}
select, input[type="number"], input[type="text"] {
  padding: 4px 10px;
  border-radius: 6px;
  border: 1px solid #3a7cff55;
  background: #232a4d;
  color: #e0e6ff;
  font-size: 15px;
}
.param-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 18px;
}
</style>
