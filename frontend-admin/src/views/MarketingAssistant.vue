<template>
  <div>
    <el-card shadow="never" style="margin-bottom: 20px;">
      <template #header>
        <span style="font-weight: bold;">出海与涉外法律营销生成器 (Marketing Bundle)</span>
      </template>
      <div style="display: flex; gap: 15px;">
        <el-input v-model="topic" placeholder="输入营销主题，例如: 中国判决在加州/纽约州的承认与执行" style="max-width: 500px;" />
        <el-button type="primary" :loading="generating" @click="generateMarketing">一键生成营销文案</el-button>
      </div>
    </el-card>

    <div v-if="bundle">
      <el-card shadow="never" style="margin-bottom: 20px;">
        <template #header>
          <div style="font-weight: bold; color: #2b6cb0;">微信公众号 / 朋友圈文案 (针对中资出海企业)</div>
        </template>
        <div style="white-space: pre-wrap; line-height: 1.8; color: #2d3748; background: #f7fafc; padding: 15px; border-radius: 6px;">
          {{ bundle.wechat_post }}
        </div>
      </el-card>

      <el-card shadow="never">
        <template #header>
          <div style="font-weight: bold; color: #2b6cb0;">LinkedIn / 海外社交渠道文案 (针对境外投资人)</div>
        </template>
        <div style="white-space: pre-wrap; line-height: 1.8; color: #2d3748; background: #f7fafc; padding: 15px; border-radius: 6px;">
          {{ bundle.linkedin_post }}
        </div>
        <div style="margin-top: 15px;">
          <el-tag v-for="tag in bundle.suggested_tags" :key="tag" style="margin-right: 8px;">{{ tag }}</el-tag>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import api from '../api/client'

const topic = ref('')
const generating = ref(false)
const bundle = ref<any>(null)

const generateMarketing = async () => {
  if (!topic.value) return
  generating.value = true
  try {
    const res: any = await api.get('/admin/api/marketing/generate', { params: { topic: topic.value } })
    bundle.value = res
  } catch (err) {
    console.error(err)
  } finally {
    generating.value = false
  }
}
</script>
