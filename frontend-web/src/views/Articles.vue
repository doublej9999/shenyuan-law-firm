<template>
  <div class="articles-page">
    <div class="header-box">
      <h2>{{ isEn ? 'Cross-Border Legal Insights & Articles' : '涉外法律研究与实务文章' }}</h2>
      <p style="color: #64748b;">
        {{ isEn 
          ? 'Deep analysis from our cross-border litigation and compliance partners.' 
          : '汇聚申远合伙人团队针对涉外审判前沿、跨境经贸合规与出海风险防控的原创洞见。' }}
      </p>
    </div>

    <div v-if="loading" style="text-align: center; padding: 40px; color: #64748b;">加载文章中...</div>
    
    <div v-else class="articles-list">
      <div v-for="item in articles" :key="item.id" class="article-item">
        <router-link :to="isEn ? `/en/articles/${item.slug}` : `/articles/${item.slug}`" class="article-title">
          {{ isEn ? (item.title_en || item.title_zh) : item.title_zh }}
        </router-link>
        <p class="article-desc">
          {{ isEn ? (item.description_en || item.description_zh) : item.description_zh }}
        </p>
        <div class="article-meta">
          <span class="badge">{{ item.business }}</span>
          <span style="color: #94a3b8; font-size: 13px;">{{ item.published_at ? item.published_at.substring(0, 10) : '' }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

axios.defaults.baseURL = import.meta.env.VITE_API_URL || ''

const route = useRoute()
const isEn = computed(() => route.path.startsWith('/en'))
const articles = ref<any[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await axios.get('/api/articles')
    articles.value = res.data
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.header-box { margin-bottom: 30px; }
.header-box h2 { font-size: 26px; color: #0f172a; margin-bottom: 8px; }
.articles-list { display: flex; flex-direction: column; gap: 20px; }
.article-item { background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 24px; transition: border-color 0.2s; }
.article-item:hover { border-color: #38bdf8; }
.article-title { font-size: 19px; font-weight: bold; color: #0f172a; text-decoration: none; margin-bottom: 10px; display: block; }
.article-title:hover { color: #0284c7; }
.article-desc { font-size: 14px; color: #475569; line-height: 1.6; margin-bottom: 16px; }
.article-meta { display: flex; justify-content: space-between; align-items: center; }
.badge { background: #f1f5f9; color: #475569; font-size: 12px; padding: 4px 10px; border-radius: 4px; text-transform: uppercase; }
</style>
