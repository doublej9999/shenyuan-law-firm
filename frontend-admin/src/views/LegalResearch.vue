<template>
  <div>
    <el-card shadow="never" style="margin-bottom: 20px;">
      <template #header>
        <span style="font-weight: bold;">涉外法务知识库语义检索 (Legal KB)</span>
      </template>
      <el-input
        v-model="query"
        placeholder="输入法条关键词、跨国继承公证、普通法域判决承认等..."
        style="width: 500px; margin-right: 15px;"
        @keyup.enter="handleSearch"
      />
      <el-button type="primary" :loading="searching" @click="handleSearch">检索知识库</el-button>
    </el-card>

    <el-card v-if="results.length > 0" shadow="never" style="margin-bottom: 20px;">
      <template #header>检索结果 ({{ results.length }} 项)</template>
      <div v-for="(item, idx) in results" :key="idx" style="margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px solid #edf2f7;">
        <div style="font-weight: bold; color: #2b6cb0;">📄 {{ item.title }} <el-tag size="small" style="margin-left: 10px;">{{ item.category }}</el-tag></div>
        <div style="font-size: 13px; color: #4a5568; margin-top: 5px;">{{ item.snippet }}</div>
        <div style="font-size: 12px; color: #a0aec0; margin-top: 4px;">来源文件: {{ item.file_path }}</div>
      </div>
    </el-card>

    <!-- AI 备忘录生成 -->
    <el-card shadow="never">
      <template #header>
        <span style="font-weight: bold;">生成涉外法律评估备忘录 (AI Legal Memo)</span>
      </template>
      <el-form :model="memoForm" label-width="120px">
        <el-form-item label="咨询事项类型">
          <el-input v-model="memoForm.matter" placeholder="例如: 中美跨境商事借款追偿 / 跨境遗嘱检验" />
        </el-form-item>
        <el-form-item label="案件事实摘要">
          <el-input v-model="memoForm.facts" type="textarea" :rows="3" placeholder="录入当事人诉求与争议事实..." />
        </el-form-item>
        <el-form-item>
          <el-button type="success" :loading="generating" @click="generateMemo">生成法律评估意见</el-button>
        </el-form-item>
      </el-form>

      <div v-if="memoResult" style="background: #ebf8ff; padding: 15px; border-radius: 6px; margin-top: 15px;">
        <h4 style="margin: 0 0 10px 0; color: #2b6cb0;">{{ memoResult.title }}</h4>
        <div style="white-space: pre-wrap; font-size: 14px; line-height: 1.6; color: #2d3748; margin-bottom: 10px;">
          {{ memoResult.analysis }}
        </div>
        <div style="white-space: pre-wrap; font-size: 14px; line-height: 1.6; color: #2c5282;">
          {{ memoResult.strategy }}
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import api from '../api/client'

const query = ref('')
const searching = ref(false)
const results = ref<any[]>([])

const memoForm = ref({ matter: '', facts: '' })
const generating = ref(false)
const memoResult = ref<any>(null)

const handleSearch = async () => {
  if (!query.value) return
  searching.value = true
  try {
    const res: any = await api.get('/admin/api/research/search', { params: { q: query.value } })
    results.value = res
  } catch (err) {
    console.error(err)
  } finally {
    searching.value = false
  }
}

const generateMemo = async () => {
  if (!memoForm.value.matter) return
  generating.value = true
  try {
    const res: any = await api.post('/admin/api/research/memo', memoForm.value)
    memoResult.value = res
  } catch (err) {
    console.error(err)
  } finally {
    generating.value = false
  }
}
</script>
