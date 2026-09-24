<template>
  <div class="services-view">
    <!-- Top Hero Banner -->
    <section class="services-hero">
      <div class="wrap">
        <div class="eyebrow">{{ isEn ? 'Practice Areas' : '服务范围' }}</div>
        <h1>{{ isEn ? 'Comprehensive Cross-Border Legal Practice' : '三类高频跨境事项，深远专业护航' }}</h1>
        <p>
          {{ isEn 
            ? 'From unpaid trade debts and cross-border commercial litigation to multi-jurisdiction family estate inheritance, we navigate complex legal landscapes in your native language.' 
            : '围绕中国企业与家庭在出海及跨国经济往来中最常遇到的争议，以事实与法理为基石，通过境内专业团队与全球 30+ 法域合作律所网络落地执行。' }}
        </p>
      </div>
    </section>

    <!-- Services Detailed Content -->
    <section class="section">
      <div class="wrap services-container">
        <!-- 01 TRADE -->
        <article class="service-detail-card" id="trade">
          <div class="card-header">
            <span class="num-badge">01 / TRADE</span>
            <h2>{{ isEn ? 'International Trade & Commercial Disputes' : '国际贸易争议与跨国合同' }}</h2>
          </div>
          <p class="summary-text">
            {{ isEn 
              ? 'Providing prompt intervention for export-import contract defaults, non-payment, cargo quality discrepancies, and cross-border commercial fraud.' 
              : '处理货物买卖履行、海外货款拖欠、代理经销违约、跨境合同审查及外贸欺诈识别与反制。' }}
          </p>

          <div class="practice-subgrid">
            <div class="sub-item">
              <h4>{{ isEn ? 'Trade Debt Recovery' : '货款追收与违约索赔' }}</h4>
              <p>{{ isEn ? 'Rapid issuance of attorney demand letters, freezing orders, and CIETAC/HKIAC arbitrations.' : '通过精准律师函、财产线索锁定与诉前保全，督促海外买方尽快履约支付。' }}</p>
            </div>
            <div class="sub-item">
              <h4>{{ isEn ? 'Cross-Border Contract Review' : '涉外合同审查与条款设计' }}</h4>
              <p>{{ isEn ? 'Drafting governing law and jurisdiction clauses to prevent multi-million dispute risks.' : '针对管辖权冲突、适用法律选择及争议解决机制（仲裁/诉讼）进行前置风险防范。' }}</p>
            </div>
            <div class="sub-item">
              <h4>{{ isEn ? 'Customs & Logistics Disputes' : '海关、物流与品质争议' }}</h4>
              <p>{{ isEn ? 'Resolution of maritime bill of lading holds, detention disputes, and quality inspection claims.' : '应对提单滞港、无单放货、海关扣货及第三方质检争议。' }}</p>
            </div>
          </div>

          <div class="card-action">
            <NuxtLink :to="isEn ? '/en#intake' : '/#intake'" class="button button-primary">
              {{ isEn ? 'Consult Trade Disputes →' : '咨询国际贸易纠纷 →' }}
            </NuxtLink>
          </div>
        </article>

        <!-- 02 RECOVERY -->
        <article class="service-detail-card" id="recovery">
          <div class="card-header">
            <span class="num-badge">02 / RECOVERY</span>
            <h2>{{ isEn ? 'Litigation, Asset Tracing & Debt Recovery' : '诉讼、全球资产调查与债务追收' }}</h2>
          </div>
          <p class="summary-text">
            {{ isEn 
              ? 'Bridging judgments into real financial recovery through in-depth asset investigation and cross-border recognition of court judgments and arbitral awards.' 
              : '从欠款事实与资产线索出发，综合运用境内外资产调查、财产保全与跨国承认执行程序，促成实质回款。' }}
          </p>

          <div class="practice-subgrid">
            <div class="sub-item">
              <h4>{{ isEn ? 'Asset Tracing & Investigation' : '境内外财产线索穿透调查' }}</h4>
              <p>{{ isEn ? 'Tracing bank accounts, real properties, equity shares, and concealed debtor transfers.' : '合法排查债务人及关联方银行账户、不动产、企业股权及隐匿资产转移轨迹。' }}</p>
            </div>
            <div class="sub-item">
              <h4>{{ isEn ? 'Cross-Border Judgment Enforcement' : '境外判决与仲裁裁决承认执行' }}</h4>
              <p>{{ isEn ? 'Enforcing judgments between Mainland China, Hong Kong, Singapore, US, and Common Law jurisdictions.' : '依据双边司法协助条约及纽约公约，申请域外裁决在中国或境外各地的承认与强制执行。' }}</p>
            </div>
            <div class="sub-item">
              <h4>{{ isEn ? 'Commercial Debt Settlement' : '商业谈判与执行和解' }}</h4>
              <p>{{ isEn ? 'Strategic negotiations backed by litigation pressure to achieve optimal commercial recoveries.' : '结合法律威慑与商业考量，促成具有实际担保效力的分期还款协议与执行和解。' }}</p>
            </div>
          </div>

          <div class="card-action">
            <NuxtLink :to="isEn ? '/en#intake' : '/#intake'" class="button button-primary">
              {{ isEn ? 'Consult Recovery Matters →' : '咨询债务追收与执行 →' }}
            </NuxtLink>
          </div>
        </article>

        <!-- 03 LEGACY -->
        <article class="service-detail-card" id="legacy">
          <div class="card-header">
            <span class="num-badge">03 / LEGACY</span>
            <h2>{{ isEn ? 'Cross-Border Inheritance & Family Wealth Protection' : '跨国继承、遗嘱检验与家族资产保护' }}</h2>
          </div>
          <p class="summary-text">
            {{ isEn 
              ? 'Guiding overseas Chinese, multinational families, and heirs through probate, property transfers, and estate distribution across borders.' 
              : '协助梳理涉及中国大陆、港澳台及海外多法域的房产、股权、存款继承，办结公证认证与外汇资金合规出境。' }}
          </p>

          <div class="practice-subgrid">
            <div class="sub-item">
              <h4>{{ isEn ? 'Multi-Jurisdiction Probate' : '跨国遗产继承与遗嘱检验' }}</h4>
              <p>{{ isEn ? 'Navigating probate courts in the US, Canada, Australia, Singapore, and China.' : '协助国内继承人办理域外遗嘱检认（Probate），解决不同继承法冲突。' }}</p>
            </div>
            <div class="sub-item">
              <h4>{{ isEn ? 'Apostille & Legalization' : '海牙公约认证（Apostille）' }}</h4>
              <p>{{ isEn ? 'Efficient preparation of kinship affidavits, death certificates, and consular notarizations.' : '高效代办海牙公约附加证明书（Apostille）及亲属关系证明公证。' }}</p>
            </div>
            <div class="sub-item">
              <h4>{{ isEn ? 'Compliant Fund Repatriation' : '合法继承款项外汇合规汇出' }}</h4>
              <p>{{ isEn ? 'SAFE approval and compliance filings for foreign nationals inheriting assets in China.' : '协助海外继承人完成中国外汇管理局财产转移税务合规审批与资金合规出境。' }}</p>
            </div>
          </div>

          <div class="card-action">
            <NuxtLink :to="isEn ? '/en#intake' : '/#intake'" class="button button-primary">
              {{ isEn ? 'Consult Inheritance Matters →' : '咨询涉外继承业务 →' }}
            </NuxtLink>
          </div>
        </article>
      </div>
    </section>

    <!-- Bottom CTA -->
    <section class="cta-band">
      <div class="wrap text-center">
        <h2>{{ isEn ? 'Need tailored advice on your specific matter?' : '不确定案件涉及哪类法律路径？' }}</h2>
        <p>{{ isEn ? 'Contact our cross-border team for an initial factual assessment within 24 hours.' : '提交案情概要或微信沟通，我们的涉外执业团队将为您梳理时效、证据与可行方案。' }}</p>
        <div class="cta-btns">
          <NuxtLink :to="isEn ? '/en#intake' : '/#intake'" class="button button-primary">
            {{ isEn ? 'Free Legal Consultation →' : '开始免费法律咨询 →' }}
          </NuxtLink>
        </div>
      </div>
    </section>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'

const route = useRoute()
const isEn = computed(() => route.path.startsWith('/en'))

// ---- SEO --------------------------------------------------------------
const siteUrl = 'https://shenyuanlegal.com'
const canonical = computed(() => `${siteUrl}${isEn.value ? '/en/services' : '/services'}`)

useSeoMeta({
  title: () => isEn.value
    ? 'Practice Areas | Cross-Border Disputes, Debt Recovery & Inheritance | Shenyuan International'
    : '服务范围 | 跨境争议、债务追收与继承 | 深远(国际)律师事务所',
  description: () => isEn.value
    ? 'Three high-frequency cross-border matters we handle: international trade and commercial disputes, cross-border litigation and debt recovery, and multi-jurisdiction inheritance and family assets.'
    : '围绕中国企业与家庭在出海及跨国经济往来中最常遇到的三类争议：国际贸易争议与跨国合同、诉讼与海外债务追收、继承与家族资产纠纷。',
  ogTitle: () => isEn.value
    ? 'Practice Areas | Shenyuan International'
    : '服务范围 | 深远(国际)律师事务所',
  ogDescription: () => isEn.value
    ? 'Cross-border disputes, debt recovery and inheritance — executed through local counsel.'
    : '跨境争议、债务追收与继承——通过当地合作律所落地执行。',
  ogType: 'website',
  ogUrl: () => canonical.value,
})

useHead({
  link: [
    { rel: 'canonical', href: () => canonical.value },
    { rel: 'alternate', hreflang: 'zh-CN', href: `${siteUrl}/services` },
    { rel: 'alternate', hreflang: 'en', href: `${siteUrl}/en/services` },
    { rel: 'alternate', hreflang: 'x-default', href: `${siteUrl}/services` },
  ],
})
</script>
<style scoped>
.services-view {
  background: var(--paper);
  color: var(--ink);
}

.services-hero {
  padding: 130px 0 60px;
  background: var(--teal-deep);
  color: #fff;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.services-hero .eyebrow {
  color: #f1b68f;
  margin-bottom: 12px;
}
.services-hero .eyebrow::before {
  background: #f1b68f;
}

.services-hero h1 {
  font-family: var(--serif);
  font-size: clamp(30px, 4vw, 48px);
  margin-bottom: 16px;
  line-height: 1.2;
}

.services-hero p {
  max-width: 720px;
  font-size: 16px;
  color: rgba(255,255,255,0.8);
  line-height: 1.7;
}

.services-container {
  display: flex;
  flex-direction: column;
  gap: 36px;
}

.service-detail-card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 36px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.03);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 12px;
}

.num-badge {
  color: var(--gold);
  font-weight: 800;
  font-size: 13px;
  letter-spacing: .08em;
}

.card-header h2 {
  font-family: var(--serif);
  font-size: 24px;
  color: var(--teal-deep);
  margin: 0;
}

.summary-text {
  color: var(--muted);
  font-size: 15px;
  line-height: 1.6;
  margin-bottom: 24px;
}

.practice-subgrid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 28px;
}

.sub-item {
  background: #fdfbf7;
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 20px;
}

.sub-item h4 {
  margin: 0 0 8px;
  font-size: 15px;
  color: var(--teal-deep);
}

.sub-item p {
  margin: 0;
  font-size: 13px;
  color: #435363;
  line-height: 1.6;
}

.card-action {
  border-top: 1px solid var(--line);
  padding-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.cta-band {
  background: var(--teal-deep);
  color: #fff;
  padding: 70px 0;
}

.cta-band .text-center {
  text-align: center;
}

.cta-band h2 {
  font-family: var(--serif);
  font-size: 28px;
  margin-bottom: 12px;
}

.cta-band p {
  color: rgba(255,255,255,0.75);
  margin-bottom: 24px;
  font-size: 15px;
}

.cta-btns {
  display: flex;
  justify-content: center;
}

@media (max-width: 880px) {
  .practice-subgrid {
    grid-template-columns: 1fr;
  }
}
</style>
