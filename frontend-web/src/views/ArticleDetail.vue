<template>
  <div class="detail-page">
    <div v-if="loading" style="text-align: center; padding: 40px;">文章加载中...</div>
    <article v-else-if="article" class="article-content">
      <router-link :to="isEn ? '/en/articles' : '/articles'" class="back-link">
        &larr; {{ isEn ? 'Back to Articles' : '返回专业文章列表' }}
      </router-link>
      <h1 class="title">{{ isEn ? (article.title_en || article.title_zh) : article.title_zh }}</h1>
      <div class="meta">
        <span>{{ isEn ? 'Domain:' : '业务类别:' }} {{ article.business }}</span>
        <span>·</span>
        <span>{{ isEn ? 'Published:' : '发布时间:' }} {{ article.published_at ? article.published_at.substring(0, 10) : '' }}</span>
      </div>
      <div class="body markdown-body">
        <p style="white-space: pre-wrap; line-height: 1.8; font-size: 16px; color: #334155;">
          {{ isEn ? (article.body_en || article.body_zh) : article.body_zh }}
        </p>
      </div>

      <div class="disclaimer">
        ⚠️ {{ isEn 
          ? 'Disclaimer: This article is for informational purposes only and does not constitute formal legal advice.' 
          : '免责声明：本文仅供涉外法律学术与实务经验探讨，不构成针对特定个案的正式法律意见。' }}
      </div>
    </article>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

axios.defaults.baseURL = import.meta.env.VITE_API_URL || ''

const route = useRoute()
const isEn = computed(() => route.path.startsWith('/en'))
const article = ref<any>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const slug = route.params.slug
    const res = await axios.get(`/api/articles/${slug}`)
    article.value = res.data
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.detail-page { max-width: 800px; margin: 0 auto; }
.article-content { background: #fff; padding: 36px; border-radius: 8px; border: 1px solid #e2e8f0; }
.back-link { color: #0284c7; text-decoration: none; font-size: 14px; font-weight: 500; margin-bottom: 20px; display: inline-block; }
.title { font-size: 28px; color: #0f172a; margin-bottom: 12px; }
.meta { font-size: 13px; color: #94a3b8; display: flex; gap: 8px; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid #f1f5f9; }
.disclaimer { margin-top: 40px; padding: 16px; background: #fffbeb; border-left: 4px solid #f59e0b; border-radius: 4px; font-size: 13px; color: #b45309; }
</style>
