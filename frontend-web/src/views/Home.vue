<template>
  <div class="home-page">
    <section class="hero-section">
      <h1 class="hero-title">
        {{ isEn ? 'Cross-Border Legal Experts & Commercial Litigators' : '专注涉外商事合规与跨境争议解决的精英律师团队' }}
      </h1>
      <p class="hero-subtitle">
        {{ isEn 
          ? 'Providing specialized legal counsel for multinational corporations, foreign investors, and cross-border families.' 
          : '为出海中资企业、外商在华投资机构及跨境高净值家庭，提供贯通中外法域的端到端法律护航。' }}
      </p>
      <div class="hero-actions">
        <router-link :to="isEn ? '/en/services' : '/services'" class="btn-primary">
          {{ isEn ? 'Our Practice Areas' : '查看涉外业务领域' }}
        </router-link>
        <router-link :to="isEn ? '/en/articles' : '/articles'" class="btn-outline">
          {{ isEn ? 'Legal Insights' : '阅览 85+ 涉外专业法评' }}
        </router-link>
      </div>
    </section>

    <!-- 优势展示 -->
    <section class="features-grid">
      <div class="feature-card">
        <div class="feature-icon">🌐</div>
        <h3>{{ isEn ? 'Global Jurisdiction Capability' : '双法域跨国穿透' }}</h3>
        <p>{{ isEn ? 'Seamless coordination across mainland China, Hong Kong, and Common Law jurisdictions.' : '深谙大陆法系与普通法系规则，提供横跨中国内地、香港及海外离岸地的一站式方案。' }}</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon">🛡️</div>
        <h3>{{ isEn ? 'Enforcement & Asset Tracing' : '判决承认与跨境执行' }}</h3>
        <p>{{ isEn ? 'Extensive experience in enforcing foreign judgments and CIETAC/HKIAC arbitral awards.' : '在海牙公约框架下协助域外判决、CIETAC/HKIAC 仲裁裁决在国内法院的承认与资产查控执行。' }}</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon">📜</div>
        <h3>{{ isEn ? 'Probate & Wealth Succession' : '涉外继承与家族公证' }}</h3>
        <p>{{ isEn ? 'Handling complex cross-border estates, Apostille authentications, and foreign probate.' : '协助海外华人与跨境家庭办理跨国遗产继承、涉外遗嘱检认及领事附加证明书（Apostille）。' }}</p>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const isEn = computed(() => route.path.startsWith('/en'))
</script>

<style scoped>
.hero-section { text-align: center; padding: 60px 20px; background: #fff; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 40px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
.hero-title { font-size: 36px; font-weight: 800; color: #0f172a; margin-bottom: 16px; letter-spacing: -0.5px; }
.hero-subtitle { font-size: 17px; color: #475569; max-width: 750px; margin: 0 auto 30px auto; line-height: 1.6; }
.hero-actions { display: flex; justify-content: center; gap: 16px; }
.btn-primary { background: #0284c7; color: #fff; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: bold; }
.btn-outline { background: transparent; color: #0284c7; border: 1px solid #0284c7; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: bold; }
.features-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; }
.feature-card { background: #fff; padding: 28px; border-radius: 8px; border: 1px solid #e2e8f0; }
.feature-icon { font-size: 32px; margin-bottom: 12px; }
.feature-card h3 { font-size: 18px; color: #1e293b; margin-bottom: 10px; }
.feature-card p { font-size: 14px; color: #64748b; line-height: 1.6; }
</style>
