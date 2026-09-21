<template>
  <div class="services-page">
    <h2>{{ isEn ? 'Our Practice Areas' : '核心涉外法律业务领域' }}</h2>
    <p style="color: #64748b; margin-bottom: 30px;">
      {{ isEn ? 'Comprehensive legal solutions for international commercial matters.' : '聚焦跨法域商事合规与高端争议解决。' }}
    </p>

    <div class="services-list">
      <div class="service-block">
        <h3>⚖️ {{ isEn ? 'Cross-Border Commercial Litigation & Arbitration' : '跨境商事诉讼与商事仲裁' }}</h3>
        <p>{{ isEn ? 'Representation before CIETAC, HKIAC, SIAC, and domestic foreign-related commercial courts.' : '代理涉外大额合同履约纠纷、跨国股权争议，出庭各级涉外商事法庭及国内外主流仲裁委。' }}</p>
      </div>
      <div class="service-block">
        <h3>🏛️ {{ isEn ? 'Foreign Judgments & Arbitral Awards Enforcement' : '境外判决与仲裁裁决承认执行' }}</h3>
        <p>{{ isEn ? 'Specialized in mutual recognition and enforcement under international conventions and bilateral treaties.' : '依据国际条约与互惠原则，代理普通法域判决、海外仲裁在境内的司法审查与财产保全。' }}</p>
      </div>
      <div class="service-block">
        <h3>👨‍👩‍👧 {{ isEn ? 'Cross-Border Inheritance & Estate Probate' : '涉外继承、遗嘱检验与信托规划' }}</h3>
        <p>{{ isEn ? 'Handling complex probate across China, Hong Kong, US, Canada, Australia, and Apostille certifications.' : '办理涉及中港及欧美跨境房产、金融资产的继承公证、海牙附加证明书 Apostille 及遗嘱检验诉讼。' }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const isEn = computed(() => route.path.startsWith('/en'))
</script>

<style scoped>
.services-list { display: flex; flex-direction: column; gap: 20px; }
.service-block { background: #fff; padding: 24px; border-radius: 8px; border: 1px solid #e2e8f0; }
.service-block h3 { margin-top: 0; color: #0f172a; margin-bottom: 8px; }
.service-block p { color: #475569; line-height: 1.6; margin: 0; }
</style>
