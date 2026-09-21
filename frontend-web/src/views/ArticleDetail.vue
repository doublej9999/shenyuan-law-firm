<template>
  <div class="article-detail-view">
    <div class="wrap detail-container">
      <div v-if="loading" class="loading-box">
        {{ isEn ? 'Loading article details...' : '正在加载文章内容...' }}
      </div>

      <article v-else-if="article" class="detail-paper">
        <router-link :to="isEn ? '/en/articles' : '/articles'" class="back-nav">
          &larr; {{ isEn ? 'Back to legal insights' : '返回法律专栏' }}
        </router-link>

        <header class="article-header">
          <div class="meta-row">
            <span class="category-tag">{{ article.business }}</span>
            <span class="date">{{ article.published_at ? article.published_at.substring(0, 10) : '' }}</span>
          </div>
          <h1 class="article-title">{{ isEn ? (article.title_en || article.title_zh) : article.title_zh }}</h1>
        </header>

        <div class="article-body">
          <div class="content-text">{{ isEn ? (article.body_en || article.body_zh) : article.body_zh }}</div>
        </div>

        <div class="article-disclaimer">
          <strong>{{ isEn ? 'Legal Disclaimer' : '免责声明' }}：</strong>
          <span>{{ isEn 
            ? 'The content of this article represents academic analysis and practice observations of Shenyuan International and does not constitute formal legal opinion or attorney-client relationship for any specific matter. For actionable counsel, please arrange a formal case review.' 
            : '本文内容仅供涉外法律实务研讨与一般信息参考，不构成针对任何具体案件的正式法律意见或委托关系。具体法律程序须结合案件全部证据、事实及相关管辖区法规一案一议。' }}</span>
        </div>

        <!-- Article Bottom Consultation Box -->
        <div class="bottom-consult-box">
          <div class="consult-copy">
            <h3>{{ isEn ? 'Facing a similar cross-border legal issue?' : '遇到类似跨境纠纷或需要法律协助？' }}</h3>
            <p>{{ isEn 
              ? 'Our bilingual dispute resolution team can provide an initial case review within 24 hours.' 
              : '提交您的案情简述或扫码微信沟通，我们将在 24 小时内为您出具初步分析建议。' }}</p>
          </div>
          <router-link :to="isEn ? '/en#intake' : '/#intake'" class="button button-primary">
            {{ isEn ? 'Free Legal Consultation →' : '免费法律咨询评估 →' }}
          </router-link>
        </div>
      </article>

      <div v-else class="not-found">
        <p>{{ isEn ? 'Article not found.' : '未找到相关文章。' }}</p>
        <router-link :to="isEn ? '/en/articles' : '/articles'" class="button button-outline">
          {{ isEn ? 'Return to Articles' : '返回专栏列表' }}
        </router-link>
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

const article = ref<any>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const slug = route.params.slug
    const res = await axios.get(`/api/articles/${slug}`)
    article.value = res.data
  } catch (err) {
    console.error('Failed to load article detail', err)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.article-detail-view {
  background: var(--paper);
  color: var(--ink);
  padding: 130px 0 80px;
  min-height: 85vh;
}

.detail-container {
  max-width: 860px;
}

.loading-box,
.not-found {
  text-align: center;
  padding: 60px 20px;
  color: var(--muted);
}

.detail-paper {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 44px 48px;
  box-shadow: 0 4px 25px rgba(0,0,0,0.03);
}

.back-nav {
  display: inline-block;
  color: var(--teal);
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 24px;
  transition: color 0.2s;
}

.back-nav:hover {
  color: var(--teal-deep);
}

.article-header {
  border-bottom: 1px solid var(--line);
  padding-bottom: 24px;
  margin-bottom: 32px;
}

.meta-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}

.category-tag {
  background: var(--teal-soft);
  color: var(--teal-deep);
  font-size: 11.5px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 12px;
  text-transform: uppercase;
}

.date {
  color: var(--muted);
  font-size: 13px;
}

.article-title {
  font-family: var(--serif);
  font-size: clamp(26px, 3.5vw, 36px);
  color: var(--ink);
  line-height: 1.25;
  margin: 0;
}

.article-body {
  font-size: 16px;
  line-height: 1.85;
  color: #2c3e50;
  margin-bottom: 40px;
}

.content-text {
  white-space: pre-wrap;
  word-break: break-word;
}

.article-disclaimer {
  background: #fdfbf7;
  border: 1px solid #e1d8c9;
  border-left: 4px solid var(--gold);
  border-radius: 6px;
  padding: 16px 20px;
  font-size: 12.5px;
  line-height: 1.7;
  color: #5c6873;
  margin-bottom: 36px;
}

.article-disclaimer strong {
  color: var(--teal-deep);
}

.bottom-consult-box {
  background: #f4eee4;
  border: 1px solid #e1d8c9;
  border-radius: 8px;
  padding: 24px 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

.consult-copy h3 {
  font-family: var(--serif);
  font-size: 18px;
  color: var(--teal-deep);
  margin: 0 0 6px;
}

.consult-copy p {
  margin: 0;
  font-size: 13px;
  color: var(--muted);
  line-height: 1.5;
}

.bottom-consult-box .button {
  flex-shrink: 0;
}

@media (max-width: 680px) {
  .detail-paper {
    padding: 28px 20px;
  }
  .bottom-consult-box {
    flex-direction: column;
    align-items: stretch;
  }
  .bottom-consult-box .button {
    width: 100%;
  }
}
</style>
