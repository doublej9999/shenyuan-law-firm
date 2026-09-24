<template>
  <div class="error-page">
    <div class="wrap">
      <div class="code">{{ error?.statusCode || 500 }}</div>
      <h1>{{ heading }}</h1>
      <p>{{ message }}</p>
      <div class="actions">
        <NuxtLink :to="isEn ? '/en' : '/'" class="button button-primary">
          {{ isEn ? 'Back to homepage' : '返回首页' }}
        </NuxtLink>
        <NuxtLink :to="isEn ? '/en/services' : '/services'" class="button button-outline">
          {{ isEn ? 'View practice areas' : '查看服务范围' }}
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ error: { statusCode?: number; statusMessage?: string; message?: string } }>()

const route = useRoute()
const isEn = computed(() => route.path.startsWith('/en'))

const heading = computed(() => {
  if (props.error?.statusCode === 404) {
    return isEn.value ? 'Page not found' : '页面未找到'
  }
  return isEn.value ? 'Something went wrong' : '页面出现异常'
})

const message = computed(() => {
  if (props.error?.statusCode === 404) {
    return isEn.value
      ? 'The page you requested does not exist or has been moved. Try the practice areas or the legal insights index.'
      : '您访问的页面不存在或已被移动。您可以查看服务范围或法律专栏。'
  }
  return isEn.value
    ? 'An unexpected error occurred. Please try again, or contact us if the problem persists.'
    : '页面发生意外错误，请重试；若问题持续，请联系我们。'
})

useHead({
  title: () => `${heading.value} | ${isEn.value ? 'Shenyuan International' : '深远(国际)律师事务所'}`,
  meta: [{ name: 'robots', content: 'noindex, follow' }],
})
</script>

<style scoped>
.error-page {
  min-height: 70vh;
  display: flex;
  align-items: center;
  padding: 160px 0 120px;
  background: var(--paper);
  color: var(--ink);
}

.code {
  font-family: var(--serif);
  font-size: 72px;
  line-height: 1;
  color: var(--gold);
  margin-bottom: 12px;
}

.error-page h1 {
  font-family: var(--serif);
  font-size: clamp(28px, 3.4vw, 40px);
  color: var(--teal-deep);
  margin: 0 0 14px;
}

.error-page p {
  max-width: 620px;
  color: var(--muted);
  font-size: 16px;
  line-height: 1.7;
  margin: 0 0 28px;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 9px;
  min-height: 46px;
  padding: 0 20px;
  border: 1px solid transparent;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 700;
  transition: transform 0.2s ease, background 0.2s ease, border-color 0.2s ease;
}
.button:hover { transform: translateY(-2px); }
.button-primary { color: #fff; background: var(--orange); }
.button-primary:hover { background: #c85d2e; }
.button-outline {
  color: var(--teal-deep);
  background: transparent;
  border-color: var(--line);
}
.button-outline:hover { background: var(--cream); }
</style>
