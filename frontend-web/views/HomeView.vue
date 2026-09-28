<template>
  <div class="home-container" :class="{ 'is-rtl': isAr }">
    <!-- 01 HERO -->
    <section class="hero">
      <div class="wrap hero-grid">
        <div class="hero-copy">
          <div class="eyebrow">
            {{ t.hero.eyebrow }}
          </div>
          <h1>
            <span>{{ t.hero.title1 }}</span>
            <span class="highlight">{{ t.hero.titleHighlight }}</span>
          </h1>
          <p>
            {{ t.hero.desc }}
          </p>
          <div class="hero-actions">
            <a class="button button-primary" href="#intake" @click.prevent="scrollToIntake">
              {{ t.hero.ctaPrimary }}
            </a>
            <NuxtLink class="button button-outline" :to="isEn ? '/en/services' : '/services'">
              {{ t.hero.ctaSecondary }}
            </NuxtLink>
          </div>
          <div class="hero-notes">
            <span><i></i><span>{{ t.hero.noteLang }}</span></span>
            <span><i></i><span>{{ t.hero.noteJurisdictions }}</span></span>
            <span><i></i><span>{{ t.hero.noteAssess }}</span></span>
          </div>
        </div>

        <form class="intake-card" id="intake" @submit.prevent="handleIntakeSubmit" novalidate>
          <h2>{{ t.intake.title }}</h2>
          <p>
            {{ t.intake.desc }}
          </p>
          <div class="contact-options">
            <img class="qr-img" src="/wechat-qrcode.png" alt="WeChat QR code" loading="lazy" decoding="async">
            <div class="wechat-copy">
              <strong>{{ t.intake.wechatTitle }}</strong>
              <p>{{ t.intake.wechatDesc }}</p>
              <span class="wechat-id">{{ t.intake.wechatId }}</span>
            </div>
          </div>

          <div class="intake-grid">
            <div class="field">
              <label for="name">{{ t.intake.fieldName }}</label>
              <input id="name" v-model="form.name" required :placeholder="t.intake.placeholderName">
            </div>
            <div class="field">
              <label for="email">{{ t.intake.fieldEmail }}</label>
              <input id="email" v-model="form.email" type="email" :placeholder="t.intake.placeholderEmail">
            </div>
            <div class="field">
              <label for="matter">{{ t.intake.fieldMatter }}</label>
              <select id="matter" v-model="form.matter" required>
                <option v-for="opt in t.intake.matterOptions" :key="opt.value" :value="opt.value">
                  {{ opt.label }}
                </option>
              </select>
            </div>
            <div class="field">
              <label for="phone">{{ t.intake.fieldPhone }}</label>
              <div class="home-phone-row">
                <CountryDialSelect
                  v-model="homeCountryDial"
                  :is-en="!isAr && !isEs && isEn"
                />
                <input
                  id="phone"
                  v-model="form.phone"
                  type="tel"
                  required
                  :placeholder="t.intake.placeholderPhone"
                >
              </div>
            </div>
            <div class="field full">
              <label for="summary">{{ t.intake.fieldSummary }}</label>
              <textarea id="summary" v-model="form.summary" required :placeholder="t.intake.placeholderSummary"></textarea>
            </div>
          </div>

          <label class="consent" for="consent">
            <input type="checkbox" id="consent" v-model="form.consent" required>
            <span>
              {{ t.intake.consentPre }}<a href="#privacy" class="privacy-link" @click.prevent.stop="privacyModalOpen = true">{{ t.intake.privacyLink }}</a>{{ t.intake.consentPost }}
            </span>
          </label>

          <div class="privacy-trigger-row">
            <button type="button" class="privacy-trigger-btn" @click="privacyModalOpen = true">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="16" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12.01" y2="8"></line>
              </svg>
              <span>{{ t.intake.viewPrivacy }}</span>
            </button>
          </div>

          <button class="button button-primary" type="submit" :disabled="submitting">
            {{ submitting ? t.intake.btnSubmitting : t.intake.btnSubmit }}
          </button>
          <p class="form-note">
            {{ t.intake.formNote }}
          </p>
        </form>
      </div>
    </section>

    <!-- 02 信任徽章条 -->
    <div class="trust-strip" aria-label="Trust signals">
      <div class="wrap">
        <div class="trust-item">
          <i></i>
          <div>
            <strong>{{ t.trust.bilingualTitle }}</strong>
            <span>{{ t.trust.bilingualDesc }}</span>
          </div>
        </div>
        <div class="trust-item">
          <i></i>
          <div>
            <strong>{{ t.trust.globalTitle }}</strong>
            <span>{{ t.trust.globalDesc }}</span>
          </div>
        </div>
        <div class="trust-item">
          <i></i>
          <div>
            <strong>{{ t.trust.responseTitle }}</strong>
            <span>{{ t.trust.responseDesc }}</span>
          </div>
        </div>
        <div class="trust-item">
          <i></i>
          <div>
            <strong>{{ t.trust.privacyTitle }}</strong>
            <span>{{ t.trust.privacyDesc }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 03 核心服务 -->
    <section class="section service-section" id="services">
      <div class="wrap">
        <div class="section-head">
          <div class="eyebrow">{{ t.services.eyebrow }}</div>
          <h2>{{ t.services.title }}</h2>
          <p>{{ t.services.desc }}</p>
        </div>
        <div class="service-grid">
          <article class="service-card">
            <div class="service-number">{{ t.services.tradeNum }}</div>
            <h3>{{ t.services.tradeTitle }}</h3>
            <p>{{ t.services.tradeDesc }}</p>
            <ul class="service-list">
              <li v-for="(item, idx) in t.services.tradeItems" :key="idx">{{ item }}</li>
            </ul>
            <NuxtLink class="service-link" :to="isEn ? '/en/services' : '/services'">
              {{ t.services.tradeLink }}
            </NuxtLink>
          </article>

          <article class="service-card">
            <div class="service-number">{{ t.services.recoveryNum }}</div>
            <h3>{{ t.services.recoveryTitle }}</h3>
            <p>{{ t.services.recoveryDesc }}</p>
            <ul class="service-list">
              <li v-for="(item, idx) in t.services.recoveryItems" :key="idx">{{ item }}</li>
            </ul>
            <NuxtLink class="service-link" :to="isEn ? '/en/services' : '/services'">
              {{ t.services.recoveryLink }}
            </NuxtLink>
          </article>

          <article class="service-card">
            <div class="service-number">{{ t.services.legacyNum }}</div>
            <h3>{{ t.services.legacyTitle }}</h3>
            <p>{{ t.services.legacyDesc }}</p>
            <ul class="service-list">
              <li v-for="(item, idx) in t.services.legacyItems" :key="idx">{{ item }}</li>
            </ul>
            <NuxtLink class="service-link" :to="isEn ? '/en/services' : '/services'">
              {{ t.services.legacyLink }}
            </NuxtLink>
          </article>
        </div>

        <div class="service-cta-row">
          <p>{{ t.services.ctaText }}</p>
          <a class="button button-primary" href="#intake" @click.prevent="scrollToIntake">
            {{ t.services.ctaBtn }}
          </a>
        </div>
      </div>
    </section>

    <!-- 04 处理路径 -->
    <section class="section process-section" id="process">
      <div class="wrap">
        <div class="section-head">
          <div class="eyebrow">{{ t.process.eyebrow }}</div>
          <h2>{{ t.process.title }}</h2>
          <p>{{ t.process.desc }}</p>
        </div>
        <div class="process-grid">
          <div class="process-step">
            <span>{{ t.process.step1Num }}</span>
            <h3>{{ t.process.step1Title }}</h3>
            <p>{{ t.process.step1Desc }}</p>
          </div>
          <div class="process-step">
            <span>{{ t.process.step2Num }}</span>
            <h3>{{ t.process.step2Title }}</h3>
            <p>{{ t.process.step2Desc }}</p>
          </div>
          <div class="process-step">
            <span>{{ t.process.step3Num }}</span>
            <h3>{{ t.process.step3Title }}</h3>
            <p>{{ t.process.step3Desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 05 数据成果 -->
    <section class="section stats-section" id="results">
      <div class="wrap">
        <div class="stat">
          <div class="num">{{ t.stats.stat1Num }}</div>
          <div class="label">{{ t.stats.stat1Label }}</div>
        </div>
        <div class="stat">
          <div class="num">{{ t.stats.stat2Num }}</div>
          <div class="label">{{ t.stats.stat2Label }}</div>
        </div>
        <div class="stat">
          <div class="num">{{ t.stats.stat3Num }}</div>
          <div class="label">{{ t.stats.stat3Label }}</div>
        </div>
        <div class="stat">
          <div class="num">{{ t.stats.stat4Num }}</div>
          <div class="label">{{ t.stats.stat4Label }}</div>
        </div>
      </div>
    </section>

    <!-- 06 案例展示 -->
    <section class="section cases-section" id="cases">
      <div class="wrap">
        <div class="section-head">
          <div class="eyebrow">{{ t.cases.eyebrow }}</div>
          <h2>{{ t.cases.title }}</h2>
          <p>{{ t.cases.desc }}</p>
        </div>
        <div class="cases-grid">
          <article class="case-card">
            <div class="case-tag">{{ t.cases.card1Tag }}</div>
            <h3>{{ t.cases.card1Title }}</h3>
            <p>{{ t.cases.card1Desc }}</p>
            <div class="case-path">
              <b>{{ t.cases.pathLabel }}</b>
              <span>{{ t.cases.card1Path }}</span>
            </div>
            <span class="soon-badge">{{ t.cases.soonBadge }}</span>
            <a class="button button-outline case-btn" href="#intake" @click.prevent="scrollToIntake">
              {{ t.cases.btnConsult }}
            </a>
          </article>

          <article class="case-card">
            <div class="case-tag">{{ t.cases.card2Tag }}</div>
            <h3>{{ t.cases.card2Title }}</h3>
            <p>{{ t.cases.card2Desc }}</p>
            <div class="case-path">
              <b>{{ t.cases.pathLabel }}</b>
              <span>{{ t.cases.card2Path }}</span>
            </div>
            <span class="soon-badge">{{ t.cases.soonBadge }}</span>
            <a class="button button-outline case-btn" href="#intake" @click.prevent="scrollToIntake">
              {{ t.cases.btnConsult }}
            </a>
          </article>

          <article class="case-card">
            <div class="case-tag">{{ t.cases.card3Tag }}</div>
            <h3>{{ t.cases.card3Title }}</h3>
            <p>{{ t.cases.card3Desc }}</p>
            <div class="case-path">
              <b>{{ t.cases.pathLabel }}</b>
              <span>{{ t.cases.card3Path }}</span>
            </div>
            <span class="soon-badge">{{ t.cases.soonBadge }}</span>
            <a class="button button-outline case-btn" href="#intake" @click.prevent="scrollToIntake">
              {{ t.cases.btnConsult }}
            </a>
          </article>
        </div>
      </div>
    </section>

    <!-- 07 国家覆盖 -->
    <section class="section global-section" id="global">
      <div class="wrap">
        <div class="section-head">
          <div class="eyebrow">{{ t.global.eyebrow }}</div>
          <h2>{{ t.global.title }}</h2>
          <p>{{ t.global.desc }}</p>
        </div>
        <div class="global-grid">
          <div v-for="(reg, i) in t.global.regions" :key="i" class="region">{{ reg }}</div>
        </div>
        <div class="global-note">
          <i></i>
          <span>{{ t.global.note }}</span>
          <a href="#intake" @click.prevent="scrollToIntake">{{ t.global.consultBtn }}</a>
        </div>
      </div>
    </section>

    <!-- 08 律师团队 -->
    <section class="section team-section" id="team">
      <div class="wrap">
        <div class="section-head">
          <div class="eyebrow">{{ t.team.eyebrow }}</div>
          <h2>{{ t.team.title }}</h2>
          <p>{{ t.team.desc }}</p>
        </div>
        <div class="team-grid">
          <div class="team-card">
            <div class="team-role">{{ t.team.card1Role }}</div>
            <h3>{{ t.team.card1Title }}</h3>
            <p>{{ t.team.card1Desc }}</p>
            <ul class="team-list">
              <li v-for="(li, i) in t.team.card1List" :key="i">{{ li }}</li>
            </ul>
            <p class="team-note">{{ t.team.card1Note }}</p>
          </div>

          <div class="team-card">
            <div class="team-role">{{ t.team.card2Role }}</div>
            <h3>{{ t.team.card2Title }}</h3>
            <p>{{ t.team.card2Desc }}</p>
            <ul class="team-list">
              <li v-for="(li, i) in t.team.card2List" :key="i">{{ li }}</li>
            </ul>
            <p class="team-note">{{ t.team.card2Note }}</p>
          </div>

          <div class="team-card">
            <div class="team-role">{{ t.team.card3Role }}</div>
            <h3>{{ t.team.card3Title }}</h3>
            <p>{{ t.team.card3Desc }}</p>
            <ul class="team-list">
              <li v-for="(li, i) in t.team.card3List" :key="i">{{ li }}</li>
            </ul>
            <p class="team-note">{{ t.team.card3Note }}</p>
          </div>

          <div class="team-card">
            <div class="team-role">{{ t.team.card4Role }}</div>
            <h3>{{ t.team.card4Title }}</h3>
            <p>{{ t.team.card4Desc }}</p>
            <ul class="team-list">
              <li v-for="(li, i) in t.team.card4List" :key="i">{{ li }}</li>
            </ul>
            <p class="team-note">{{ t.team.card4Note }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 09 客户信任体系 -->
    <section class="section trust-section" id="trust">
      <div class="wrap">
        <div class="section-head">
          <div class="eyebrow">{{ t.whyTrust.eyebrow }}</div>
          <h2>{{ t.whyTrust.title }}</h2>
        </div>
        <div class="trust-grid">
          <div class="trust-card">
            <i>秘</i>
            <h3>{{ t.whyTrust.card1Title }}</h3>
            <p>{{ t.whyTrust.card1Desc }}</p>
          </div>
          <div class="trust-card">
            <i>评</i>
            <h3>{{ t.whyTrust.card2Title }}</h3>
            <p>{{ t.whyTrust.card2Desc }}</p>
          </div>
          <div class="trust-card">
            <i>诚</i>
            <h3>{{ t.whyTrust.card3Title }}</h3>
            <p>{{ t.whyTrust.card3Desc }}</p>
          </div>
          <div class="trust-card">
            <i>规</i>
            <h3>{{ t.whyTrust.card4Title }}</h3>
            <p>{{ t.whyTrust.card4Desc }}</p>
          </div>
        </div>
        <div class="practice-note">
          <b>{{ t.whyTrust.statementLabel }}</b>
          <span>{{ t.whyTrust.statementText }}</span>
        </div>
      </div>
    </section>

    <!-- 10 FAQ -->
    <section class="section" id="faq">
      <div class="wrap">
        <div class="section-head">
          <div class="eyebrow">{{ t.faq.eyebrow }}</div>
          <h2>{{ t.faq.title }}</h2>
        </div>
        <div class="faq-grid">
          <details v-for="(f, i) in t.faq.items" :key="i" :open="i === 0">
            <summary>{{ f.q }}</summary>
            <p>{{ f.a }}</p>
          </details>
        </div>
      </div>
    </section>

    <!-- 11 咨询入口 CTA -->
    <section class="cta-band" id="contact">
      <div class="wrap">
        <div class="eyebrow">{{ isEn ? 'Free consultation' : (isAr ? 'استشارة مجانية' : (isEs ? 'Consulta Gratuita' : '免费法律咨询')) }}</div>
        <h2>{{ t.faq.ctaTitle }}</h2>
        <p>{{ t.faq.ctaDesc }}</p>
        <div class="hero-actions">
          <a class="button button-primary" href="#intake" @click.prevent="scrollToIntake">
            {{ t.faq.ctaBtn }}
          </a>
          <NuxtLink class="button button-outline" :to="isEn ? '/en/services' : '/services'">
            {{ isEn ? 'Review our services' : (isAr ? 'مراجعة خدماتنا' : (isEs ? 'Revisar servicios' : '再看一遍服务范围')) }}
          </NuxtLink>
        </div>
      </div>
    </section>

    <!-- 成功提示弹窗 Modal -->
    <div class="modal-backdrop" :class="{ 'is-visible': successModalOpen }" role="dialog" aria-modal="true" @click.self="successModalOpen = false">
      <div class="success-panel" :class="{ 'is-rtl': isAr }">
        <button class="modal-close" type="button" @click="successModalOpen = false" aria-label="关闭">×</button>
        <h3>{{ isEn ? 'We have received your information' : (isAr ? 'تم استلام بيانات استفساركم بنجاح' : (isEs ? 'Hemos recibido su información' : '已收到您的信息')) }}</h3>
        <p>{{ isEn 
          ? 'We will first review the matter type, relevant region, and your intended outcome to identify the next discussion points.' 
          : (isAr
            ? 'سنقوم أولاً بمراجعة نوع النزاع والدولة المعنية ومطالبكم لتحديد خطوات المتابعة القانونية.'
            : (isEs
              ? 'Revisaremos el tipo de conflicto, la jurisdicción y sus objetivos para establecer la estrategia de contacto.'
              : '我们会先查看事项类型、涉及地区和你希望达成的目标，并据此判断后续沟通重点。')) }}</p>
        
        <strong class="material-title">{{ isEn ? 'Suggested documents to prepare' : (isAr ? 'المستندات المقترح تجهيزها' : (isEs ? 'Documentación sugerida a preparar' : '建议先准备这些材料')) }}</strong>
        <ul class="material-list">
          <li v-for="(item, idx) in currentMaterialList" :key="idx">{{ item }}</li>
        </ul>

        <div class="urgent-note">
          {{ isEn 
            ? 'If there is asset transfer, a litigation or arbitration deadline, customs detention, disappearing evidence, or a missing family member, please mark the WeChat message as urgent.' 
            : '如存在财产转移、诉讼或仲裁期限、海关扣货、证据灭失、家族成员失联等紧急情况，请在微信中注明“紧急”。' }}
        </div>

        <div class="modal-wechat">
          <img class="qr-img-large" src="/wechat-qrcode.png" alt="WeChat QR code" loading="lazy" decoding="async">
          <div>
            <strong>{{ isEn ? 'Scan WeChat to share documents' : '扫码添加微信，补充材料' }}</strong>
            <p>{{ isEn ? 'Please send Submitted + your name + matter type so we can match your consultation information faster.' : '建议发送“已提交 + 称呼 + 事项类型”，便于我们更快对应你的咨询信息。' }}</p>
          </div>
        </div>

        <div class="success-actions">
          <button class="button button-primary" type="button" @click="successModalOpen = false">
            {{ isEn ? 'Got it' : '我已了解' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 隐私政策与保密说明弹窗 Modal -->
    <div class="modal-backdrop" :class="{ 'is-visible': privacyModalOpen }" role="dialog" aria-modal="true" @click.self="privacyModalOpen = false">
      <div class="success-panel privacy-modal-panel" :class="{ 'is-rtl': isAr }">
        <button class="modal-close" type="button" @click="privacyModalOpen = false" aria-label="关闭">×</button>
        <h3>{{ isEn ? 'Privacy Notice & Confidentiality' : (isAr ? 'سياسة الخصوصية والسرية المهنية' : (isEs ? 'Aviso de Privacidad y Confidencialidad' : '隐私保护与保密说明')) }}</h3>
        
        <div class="privacy-modal-body">
          <div class="privacy-point">
            <div class="privacy-point-title">{{ isEn ? 'Information Collection & Usage' : (isAr ? 'نطاق استخدام البيانات' : (isEs ? 'Uso de la Información' : '信息使用范围')) }}</div>
            <p>{{ isEn 
              ? 'The information you submit via this consultation form is strictly used for initial matter assessment, conflict-of-interest checks, and follow-up communication by our legal team.' 
              : (isAr
                ? 'تُستخدم البيانات المرسلة عبر نموذج الاستشارة حصراً لإجراء التقييم القانوني الأولي والتحقق من عدم تضارب المصالح والمتابعة، ولا يتم الإفصاح عنها لأي طرف ثالث.'
                : (isEs
                  ? 'La información enviada se utiliza exclusivamente para la evaluación inicial del caso, verificación de conflictos de interés y seguimiento legal sin divulgarse a terceros.'
                  : '您在咨询表单中提交的称呼、联系方式和案件描述，仅供本所涉外律师团队进行初步案情评估、利益冲突检索及后续沟通联系，绝不向任何未经授权的第三方披露。')) }}</p>
          </div>

          <div class="privacy-point">
            <div class="privacy-point-title">{{ isEn ? 'Security & Compliance' : (isAr ? 'أمان البيانات والامتثال القانوني' : (isEs ? 'Seguridad y Cumplimiento' : '数据安全与合规')) }}</div>
            <p>{{ isEn 
              ? 'All data transmission is encrypted (SSL/TLS) in strict accordance with the Personal Information Protection Law (PIPL) and applicable international data protection standards.' 
              : (isAr
                ? 'يتم تشفير كافة البيانات عبر بروتوكول SSL/TLS وفقاً لقوانين حماية البيانات الشخصية والمعايير الدولية لحماية سرية الموكلين.'
                : (isEs
                  ? 'Toda la transmisión está cifrada vía SSL/TLS en cumplimiento estricto con las normativas internacionales de protección de datos personales.'
                  : '咨询数据全程通过 SSL/TLS 加密传输并加密存储，遵循《中华人民共和国个人信息保护法》(PIPL) 与相关跨境数据合规要求，确保您的商业与私人信息安全。')) }}</p>
          </div>

          <div class="urgent-note" style="margin-top: 14px;">
            {{ isEn 
              ? 'Notice: An initial consultation does not create an attorney-client relationship. Please do not submit sensitive identifiers such as ID numbers, bank card numbers, or passwords.' 
              : (isAr
                ? 'تنبيه هام: الاستشارة الأولية لا تُنشئ علاقة توكيل محامي رسمية. يُرجى عدم إرسال أرقام الهوية السرية أو أرقام الحسابات البنكية في هذه المرحلة.'
                : (isEs
                  ? 'Aviso: La consulta inicial no constituye una relación formal abogado-cliente. Rogamos no ingresar datos bancarios o documentos confidenciales de identidad.'
                  : '特别提醒：初步咨询沟通不构成正式委托代理关系。请勿在此阶段提供身份证件原件号码、银行卡密码或最高机密等敏感信息。')) }}
          </div>
        </div>

        <div class="success-actions" style="margin-top: 20px;">
          <button class="button button-primary" type="button" @click="privacyModalOpen = false">
            {{ isEn ? 'I Understand' : (isAr ? 'فهمت ذلك' : (isEs ? 'Entendido' : '我已了解')) }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, computed } from 'vue'
import { getApiClient, parseApiError } from '@/api/client'
import { useUserGeo } from '@/composables/useUserGeo'
import { useHomeTranslation } from '@/composables/useHomeTranslation'

const { currentLang, isAr, isEs, isEn, t } = useHomeTranslation()
const { countryInfo } = useUserGeo()

// 首页表单国家区号，默认跟随 IP 侦测
const homeCountryDial = ref(countryInfo.value?.dialCode || '+86')
watch(
  () => countryInfo.value?.dialCode,
  (code) => {
    if (code && !homeCountryDial.value) {
      homeCountryDial.value = code
    }
  }
)

// ---- SEO --------------------------------------------------------------
const siteUrl = 'https://shenyuanlegal.com'
const canonical = computed(() => {
  if (isAr.value) return `${siteUrl}/ar`
  if (isEs.value) return `${siteUrl}/es`
  if (isEn.value) return `${siteUrl}/en`
  return `${siteUrl}/`
})

useSeoMeta({
  title: () => isAr.value
    ? 'مكتب شينيوان الدولي للمحاماة | حل النزاعات العابرة للحدود وحماية الأصول'
    : (isEs.value
      ? 'Bufete Shenyuan Internacional | Resolución de Disputas Transfronterizas y Protección Patrimonial'
      : (isEn.value
        ? 'Shenyuan International | Cross-Border Dispute Resolution & Family Asset Protection'
        : 'Shenyuan International | 深远(国际)律师事务所')),
  description: () => isAr.value
    ? 'مكتب شينيوان الدولي للمحاماة يقدم خدمات التقاضي في النزاعات التجارية الدولية، وتحصيل الديون العابرة للحدود، وحماية الميراث والأصول العائلية.'
    : (isEs.value
      ? 'El Bufete Internacional Shenyuan asiste en la resolución de disputas comerciales internacionales, recuperación de deudas transfronterizas y protección patrimonial.'
      : (isEn.value
        ? 'Shenyuan International Law Firm helps Chinese businesses and families resolve international trade disputes, recover cross-border debts and protect inherited family assets — bilingual, executed through a global network of local counsel.'
        : 'Shenyuan International 深远(国际)律师事务所：为中国企业与家庭提供跨境商事争议、债务追收、继承与家族资产的国际法律服务，中英双语，覆盖全球 30+ 国家与地区的合作律所网络。')),
  ogTitle: () => isAr.value
    ? 'مكتب شينيوان الدولي للمحاماة | حل النزاعات الدولية'
    : (isEs.value
      ? 'Bufete Shenyuan Internacional | Disputas Transfronterizas'
      : (isEn.value
        ? 'Shenyuan International | Cross-Border Dispute Resolution'
        : 'Shenyuan International | 深远(国际)律师事务所')),
  ogDescription: () => isAr.value
    ? 'نزاعات تجارية دولية، تحصيل ديون، وتنفيذ قضائي عالمي.'
    : (isEs.value
      ? 'Disputas comerciales internacionales, recuperación de deudas y ejecución global.'
      : (isEn.value
        ? 'Cross-border disputes, executed globally. Trade disputes, debt recovery, inheritance and family assets.'
        : '跨境争议，全球落地执行。跨境商事争议、债务追收、继承与家族资产——中英双语，全球协作网络。')),
  ogType: 'website',
  ogUrl: () => canonical.value,
  ogImage: () => `${siteUrl}/og-image.png`,
  twitterCard: 'summary_large_image',
  twitterTitle: () => isEn.value ? 'Shenyuan International | Cross-Border Dispute Resolution' : 'Shenyuan International | 深远(国际)律师事务所',
  twitterDescription: () => isEn.value ? 'Cross-border disputes, executed globally.' : '跨境争议，全球落地执行。',
  twitterImage: () => `${siteUrl}/og-image.png`,
})

useHead({
  htmlAttrs: {
    lang: () => currentLang.value === 'zh' ? 'zh-CN' : currentLang.value,
    dir: () => isAr.value ? 'rtl' : 'ltr',
  },
  link: [
    { rel: 'canonical', href: () => canonical.value },
    { rel: 'alternate', hreflang: 'zh-CN', href: `${siteUrl}/` },
    { rel: 'alternate', hreflang: 'en', href: `${siteUrl}/en` },
    { rel: 'alternate', hreflang: 'ar', href: `${siteUrl}/ar` },
    { rel: 'alternate', hreflang: 'es', href: `${siteUrl}/es` },
    { rel: 'alternate', hreflang: 'x-default', href: `${siteUrl}/` },
    { rel: 'alternate', type: 'application/rss+xml', title: 'Shenyuan Legal RSS Feed', href: `${siteUrl}/feed.xml` },
  ],
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        'name': 'Shenyuan International Law Firm 深远(国际)律师事务所',
        'url': siteUrl,
        'potentialAction': {
          '@type': 'SearchAction',
          'target': `${siteUrl}/articles?q={search_term_string}`,
          'query-input': 'required name=search_term_string',
        },
      }),
    },
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'LegalService',
        'name': 'Shenyuan International 深远(国际)律师事务所',
        'url': `${siteUrl}/`,
        'logo': `${siteUrl}/favicon.svg`,
        'description': '面向中国企业与家庭的跨境法律服务：国际贸易争议、诉讼与债务追收、继承与家族资产。中英双语，覆盖 30+ 国家与地区的合作律所网络。',
        'knowsLanguage': ['zh', 'en'],
        'areaServed': 'Worldwide',
        'serviceType': [
          'International Trade & Commercial Disputes',
          'Cross-border Litigation & Debt Recovery',
          'Inheritance & Family Asset Protection',
        ],
        'priceRange': '$$$',
        'sameAs': [
          'https://lawyers.justia.com',
          'https://www.martindale.com',
          'https://www.avvo.com',
          'https://www.linkedin.com/company/shenyuan-legal'
        ],
        'address': {
          '@type': 'PostalAddress',
          'addressCountry': 'CN'
        }
      }),
    },
  ],
})

const form = ref({
  name: '',
  phone: '',
  email: '',
  matter: '国际贸易争议',
  summary: '',
  consent: true
})

const submitting = ref(false)
const successModalOpen = ref(false)
const privacyModalOpen = ref(false)

const materialGuides = {
  trade: {
    zh: ["合同、订单、发票、付款记录", "提单、物流、报关、质检文件", "与对方的邮件、微信、WhatsApp 记录", "对方公司名称、地址、联系人信息"],
    en: ["Contracts, purchase orders, invoices, and payment records", "Bills of lading, logistics, customs, and quality inspection documents", "Emails, WeChat, WhatsApp, or other communications", "Counterparty company name, address, and contact details"]
  },
  recovery: {
    zh: ["欠款金额和到期时间", "债务人公司或个人信息", "合同、账单、催款记录", "已有判决、仲裁裁决或资产线索"],
    en: ["Debt amount and due date", "Debtor company or individual information", "Contracts, statements, and demand records", "Existing judgments, arbitral awards, or asset clues"]
  },
  legacy: {
    zh: ["亲属关系证明", "死亡证明、遗嘱或遗产文件", "房产、股权、存款等资产线索", "涉及国家或地区、家族成员联系方式"],
    en: ["Proof of family relationship", "Death certificate, will, or estate documents", "Property, equity, deposit, or other asset clues", "Relevant countries or regions and family member contact details"]
  },
  unsure: {
    zh: ["简要时间线", "相关人员、公司或家族成员信息", "合同、沟通记录、资产线索或已有文件", "你希望解决的问题和理想结果"],
    en: ["A brief timeline", "Relevant people, companies, or family members", "Contracts, communications, asset clues, or existing documents", "The issue you want to resolve and your preferred outcome"]
  }
}

const currentMaterialList = computed(() => {
  const m = form.value.matter
  const langKey = isEn.value ? 'en' : 'zh'
  if (m.includes('贸易') || m.includes('Trade')) return materialGuides.trade[langKey]
  if (m.includes('追收') || m.includes('诉讼') || m.includes('Recovery') || m.includes('Litigation')) return materialGuides.recovery[langKey]
  if (m.includes('继承') || m.includes('家族') || m.includes('Legacy') || m.includes('Inheritance')) return materialGuides.legacy[langKey]
  return materialGuides.unsure[langKey]
})

const scrollToIntake = () => {
  const el = document.getElementById('intake')
  if (el) el.scrollIntoView({ behavior: 'smooth' })
}

const handleIntakeSubmit = async () => {
  if (!form.value.name || !form.value.phone || !form.value.summary) {
    alert(isEn.value ? 'Please fill in the required fields (Name, Phone, Description).' : '请填写必要字段（称呼、电话、问题描述）。')
    return
  }
  if (!form.value.consent) {
    alert(isEn.value ? 'Please agree to the privacy statement.' : '请勾选同意隐私说明。')
    return
  }

  submitting.value = true
  try {
    let normalizedPhone = form.value.phone.trim()
    const activeDial = homeCountryDial.value || countryInfo.value?.dialCode || '+86'
    if (!normalizedPhone.startsWith('+')) {
      normalizedPhone = `${activeDial} ${normalizedPhone}`
    }

    const geoMeta = countryInfo.value && countryInfo.value.code !== 'CN'
      ? ` [访客法域: ${countryInfo.value.nameZh} (${countryInfo.value.code})]`
      : ''

    await getApiClient().post('/api/intakes', {
      name: form.value.name,
      phone: normalizedPhone,
      email: form.value.email || undefined,
      matter: form.value.matter,
      summary: `${form.value.summary}${geoMeta}`,
      consent: form.value.consent,
      language: isEn.value ? 'en' : 'zh'
    })
    successModalOpen.value = true
  } catch (err: any) {
    const errorMsg = parseApiError(err, isEn.value)
    alert(errorMsg)
  } finally {
    submitting.value = false
  }
}
</script>
<style scoped>
.home-container {
  color: var(--ink);
  background: var(--paper);
}

/* RTL 镜像适配 */
.home-container.is-rtl {
  direction: rtl;
  text-align: right;
}

.home-container.is-rtl .eyebrow {
  flex-direction: row-reverse;
}

.home-container.is-rtl .eyebrow::before {
  margin-left: 8px;
  margin-right: 0;
}

.home-container.is-rtl .hero-notes {
  flex-direction: row-reverse;
}

.home-container.is-rtl .hero-notes span {
  flex-direction: row-reverse;
}

.home-container.is-rtl .service-list li {
  padding-left: 0;
  padding-right: 20px;
}

.home-container.is-rtl .service-list li::before {
  left: auto;
  right: 0;
}

.home-container.is-rtl .case-path {
  border-left: none;
  border-right: 3px solid var(--gold);
  padding-left: 0;
  padding-right: 12px;
}

.home-container.is-rtl .global-note {
  flex-direction: row-reverse;
  text-align: right;
}

.home-container.is-rtl .practice-note {
  border-left: none;
  border-right: 3px solid var(--gold);
  padding-left: 0;
  padding-right: 16px;
}

.home-container.is-rtl .contact-options {
  flex-direction: row-reverse;
}

.home-container.is-rtl .wechat-copy {
  text-align: right;
}

.home-container.is-rtl .success-panel {
  text-align: right;
  direction: rtl;
}

.home-container.is-rtl .modal-close {
  left: 20px;
  right: auto;
}

.eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--gold);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: .13em;
  text-transform: uppercase;
}
.eyebrow::before {
  content: "";
  width: 24px;
  height: 2px;
  background: var(--gold);
}

h1, h2, h3, p { margin: 0; }
h1, h2, h3 { font-family: var(--serif); }
h1 { font-size: clamp(38px, 5vw, 64px); line-height: 1.15; letter-spacing: -.01em; }
h2 { font-size: clamp(28px, 4vw, 44px); line-height: 1.2; letter-spacing: -.01em; }
h3 { font-size: 20px; line-height: 1.3; }

.section { padding: 96px 0; }
.section-head { max-width: 720px; margin-bottom: 44px; }
.section-head h2 { margin-top: 15px; }
.section-head p { margin-top: 16px; color: var(--muted); font-size: 17px; }

/* 01 HERO */
.hero {
  position: relative;
  min-height: 760px;
  padding: 160px 0 96px;
  color: #fff;
  background-color: #18383a;
  background-image: url("https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?auto=format&fit=crop&w=1800&q=85");
  background-position: center top;
  background-size: cover;
  isolation: isolate;
}
.hero::before {
  content: "";
  position: absolute;
  inset: 0;
  z-index: -1;
  background: rgba(7, 31, 38, .84);
}
.hero::after {
  content: "";
  position: absolute;
  inset: auto 0 0;
  height: 100px;
  z-index: -1;
  background: var(--paper);
  clip-path: polygon(0 80%, 100% 0, 100% 100%, 0 100%);
}
.hero-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.08fr) minmax(370px, .92fr);
  align-items: center;
  gap: 64px;
}
.hero-copy { max-width: 680px; }
.hero-copy .eyebrow { color: #f1b68f; }
.hero-copy .eyebrow::before { background: #f1b68f; }
.hero-copy h1 { margin-top: 18px; max-width: 700px; }
.hero-copy h1 .highlight { color: #f1b68f; }
.hero-copy p { max-width: 620px; margin-top: 24px; color: rgba(255,255,255,.8); font-size: 17px; line-height: 1.7; }
.hero-actions { display: flex; flex-wrap: wrap; gap: 14px; margin-top: 32px; }

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
  transition: transform .2s ease, background .2s ease, border-color .2s ease;
  cursor: pointer;
}
.button:hover { transform: translateY(-2px); }
.button-primary { color: #fff; background: var(--orange); }
.button-primary:hover { background: #c85d2e; }
.button-outline { color: #fff; border-color: rgba(255,255,255,.38); background: transparent; }
.button-outline:hover { background: rgba(255,255,255,.08); }

.hero-notes { display: flex; flex-wrap: wrap; gap: 20px; margin-top: 36px; color: rgba(255,255,255,.75); font-size: 13px; }
.hero-notes span { display: inline-flex; align-items: center; gap: 7px; }
.hero-notes i { width: 6px; height: 6px; background: #f1b68f; border-radius: 50%; }

/* Intake Card */
.intake-card {
  padding: 30px;
  color: var(--ink);
  background: rgba(255,253,249,.98);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  border: 1px solid rgba(255,255,255,0.4);
}
.intake-card h2 { font-size: 26px; color: var(--teal-deep); }
.intake-card > p { margin-top: 10px; color: var(--muted); font-size: 13px; line-height: 1.55; }
.contact-options {
  display: grid;
  grid-template-columns: 96px 1fr;
  gap: 16px;
  align-items: center;
  margin-top: 20px;
  padding: 14px;
  background: #f4eee4;
  border: 1px solid #e1d8c9;
  border-radius: 8px;
}
.qr-img {
  width: 90px;
  height: 90px;
  object-fit: contain;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 4px;
}
.wechat-copy strong { display: block; font-size: 14px; color: var(--teal-deep); }
.wechat-copy p { margin-top: 4px; color: var(--muted); font-size: 12px; line-height: 1.45; }
.wechat-copy .wechat-id {
  display: inline-flex;
  margin-top: 8px;
  padding: 3px 8px;
  color: var(--teal-deep);
  background: #deefea;
  border-radius: 5px;
  font-size: 12px;
  font-weight: 700;
}
.intake-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 20px; }
.field { display: grid; gap: 5px; }
.field.full { grid-column: 1 / -1; }
.field label { color: var(--muted); font-size: 12px; font-weight: 700; }

.home-phone-row {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.country-dial-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 10px 10px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  color: var(--teal-deep);
  white-space: nowrap;
  user-select: none;
  flex-shrink: 0;
}

.field input, .field select, .field textarea {
  width: 100%;
  padding: 10px 12px;
  color: var(--ink);
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 6px;
  outline: none;
  font-size: 13.5px;
}
.field textarea { min-height: 84px; resize: vertical; }
.field input:focus, .field select:focus, .field textarea:focus { border-color: var(--teal); box-shadow: 0 0 0 3px rgba(13,108,107,.12); }
.intake-card .button { width: 100%; margin-top: 16px; }
.form-note { margin-top: 10px; color: var(--muted); font-size: 11px; line-height: 1.5; }
.consent {
  display: flex;
  gap: 8px;
  align-items: flex-start;
  margin-top: 14px;
  color: var(--muted);
  font-size: 12px;
  line-height: 1.5;
}
.consent input { margin-top: 2px; flex: none; }
.privacy-link {
  color: var(--teal);
  font-weight: 600;
  text-decoration: underline;
  text-underline-offset: 2px;
  cursor: pointer;
}
.privacy-link:hover {
  color: var(--teal-deep);
}
.privacy-trigger-row {
  margin-top: 6px;
  display: flex;
}
.privacy-trigger-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 2px 0;
  background: transparent;
  border: none;
  color: var(--teal);
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: color 0.15s ease;
}
.privacy-trigger-btn:hover {
  color: var(--teal-deep);
}
.privacy-modal-panel {
  max-width: 560px;
}
.privacy-modal-body {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.privacy-point {
  padding: 12px 14px;
  background: #fbf9f4;
  border: 1px solid #ebdccb;
  border-radius: 8px;
}
.privacy-point-title {
  font-weight: 700;
  font-size: 13px;
  color: var(--teal-deep);
  margin-bottom: 4px;
}
.privacy-point p {
  font-size: 12px;
  color: var(--ink);
  line-height: 1.6;
}

/* 02 信任徽章条 */
.trust-strip { border-bottom: 1px solid var(--line); background: var(--surface); }
.trust-strip .wrap { display: grid; grid-template-columns: repeat(4, 1fr); }
.trust-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 22px 18px;
  border-left: 1px solid var(--line);
}
.trust-item:first-child { border-left: 0; }
.trust-item i {
  flex: none;
  width: 9px;
  height: 9px;
  background: var(--gold);
  border-radius: 50%;
}
.trust-item strong { display: block; font-size: 14px; color: var(--teal-deep); }
.trust-item span { display: block; margin-top: 1px; color: var(--muted); font-size: 12px; }

/* 03 核心服务 */
.service-section { background: var(--paper); }
.service-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.service-card {
  position: relative;
  display: flex;
  flex-direction: column;
  min-height: 380px;
  padding: 30px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  transition: transform .2s ease, box-shadow .2s ease;
}
.service-card:hover { transform: translateY(-5px); box-shadow: var(--shadow); }
.service-number { color: var(--gold); font-size: 13px; font-weight: 800; letter-spacing: .08em; }
.service-card h3 { margin-top: 18px; color: var(--teal-deep); }
.service-card > p { margin-top: 12px; color: var(--muted); font-size: 14px; }
.service-list { display: grid; gap: 8px; margin: 20px 0 0; padding: 0; list-style: none; color: #435363; font-size: 13px; }
.service-list li { position: relative; padding-left: 16px; }
.service-list li::before { content: ""; position: absolute; top: 9px; left: 0; width: 5px; height: 5px; background: var(--gold); border-radius: 50%; }
.service-link { display: inline-flex; align-items: center; gap: 8px; margin-top: auto; padding-top: 24px; color: var(--teal); font-size: 13px; font-weight: 800; }
.service-cta-row { margin-top: 36px; text-align: center; }
.service-cta-row p { color: var(--muted); font-size: 14px; }
.service-cta-row .button { margin-top: 14px; }

/* 04 处理路径 */
.process-section { color: #f5f2ec; background: var(--teal-deep); }
.process-section .eyebrow { color: #f1b68f; }
.process-section .eyebrow::before { background: #f1b68f; }
.process-section .section-head p { color: rgba(255,255,255,.72); }
.process-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0; }
.process-step { min-height: 220px; padding: 26px 32px 10px 0; border-top: 1px solid rgba(255,255,255,.23); }
.process-step + .process-step { padding-left: 32px; border-left: 1px solid rgba(255,255,255,.23); }
.process-step span { display: block; color: #f1b68f; font-size: 15px; font-weight: 800; }
.process-step h3 { margin-top: 20px; font-size: 19px; }
.process-step p { margin-top: 11px; color: rgba(255,255,255,.72); font-size: 14px; }

/* 05 数据成果 */
.stats-section { color: #f5f2ec; background: #10282e; border-bottom: 1px solid rgba(255,255,255,.1); }
.stats-section .wrap { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; }
.stat { text-align: center; padding: 14px 8px; }
.stat .num { font-family: var(--serif); font-size: clamp(38px, 4.5vw, 56px); font-weight: 700; line-height: 1; color: #f1b68f; }
.stat .num em { font-style: normal; font-size: .55em; margin-left: 2px; color: rgba(255,255,255,.65); }
.stat .label { margin-top: 12px; color: rgba(255,255,255,.72); font-size: 13px; }

/* 06 案例展示 */
.cases-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.case-card {
  display: flex;
  flex-direction: column;
  padding: 28px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius);
}
.case-tag { color: var(--orange); font-size: 12px; font-weight: 800; letter-spacing: .08em; }
.case-card h3 { margin-top: 16px; font-size: 19px; color: var(--teal-deep); }
.case-card p { margin-top: 10px; color: var(--muted); font-size: 13px; line-height: 1.6; }
.case-path {
  display: grid;
  gap: 6px;
  margin: 18px 0 0;
  padding: 14px 15px;
  background: #f4eee4;
  border-radius: 8px;
  font-size: 12px;
  color: #435363;
  line-height: 1.5;
}
.case-path b { color: var(--teal-deep); }
.soon-badge {
  display: inline-block;
  align-self: flex-start;
  margin-top: 16px;
  padding: 3px 10px;
  color: var(--teal-deep);
  background: #deefea;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 700;
}
.case-btn {
  margin-top: auto;
  align-self: flex-start;
  margin-top: 18px;
  color: var(--teal);
  border-color: rgba(13,108,107,.35);
}
.case-btn:hover { background: #f4eee4; }

/* 07 国家覆盖 */
.global-section { background: var(--cream); }
.global-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.region {
  padding: 14px 16px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
  font-size: 14px;
  font-weight: 700;
  text-align: center;
  color: var(--ink);
}
.global-note {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 26px;
  padding: 16px 20px;
  color: var(--muted);
  background: var(--surface);
  border: 1px dashed #c9b98f;
  border-radius: 8px;
  font-size: 13px;
}
.global-note i { flex: none; width: 8px; height: 8px; background: var(--gold); border-radius: 50%; }
.global-note a { color: var(--teal); font-weight: 800; white-space: nowrap; }

/* 08 律师团队 */
.team-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
.team-card {
  display: flex;
  flex-direction: column;
  padding: 28px;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius);
}
.team-role { color: var(--gold); font-size: 12px; font-weight: 800; letter-spacing: .08em; }
.team-card h3 { margin-top: 15px; color: var(--teal-deep); }
.team-card > p { margin-top: 10px; color: var(--muted); font-size: 13px; line-height: 1.6; }
.team-list { display: grid; gap: 7px; margin: 18px 0 0; padding: 0; list-style: none; color: #435363; font-size: 13px; }
.team-list li { position: relative; padding-left: 16px; }
.team-list li::before { content: ""; position: absolute; top: 9px; left: 0; width: 5px; height: 5px; background: var(--teal); border-radius: 50%; }
.team-note { margin-top: 16px; color: var(--muted); font-size: 12px; }

/* 09 客户信任体系 */
.trust-section { background: var(--surface); }
.trust-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; }
.trust-card { padding: 26px; background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius); }
.trust-card i {
  display: block;
  width: 36px;
  height: 36px;
  color: var(--gold);
  border: 1px solid #d8c9a8;
  border-radius: 50%;
  font-family: var(--serif);
  font-size: 18px;
  font-weight: 700;
  line-height: 34px;
  text-align: center;
}
.trust-card h3 { margin-top: 16px; font-size: 17px; color: var(--teal-deep); }
.trust-card p { margin-top: 9px; color: var(--muted); font-size: 13px; line-height: 1.6; }
.practice-note {
  margin-top: 30px;
  padding: 16px 20px;
  color: var(--muted);
  background: var(--cream);
  border-radius: 8px;
  font-size: 12px;
  line-height: 1.7;
}
.practice-note b { color: var(--teal-deep); }

/* 10 FAQ */
.faq-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px 48px; }
details { padding: 18px 0; border-top: 1px solid var(--line); }
details:last-child, details:nth-last-child(2) { border-bottom: 1px solid var(--line); }
summary { display: flex; align-items: center; justify-content: space-between; gap: 18px; cursor: pointer; list-style: none; font-weight: 700; color: var(--ink); }
summary::-webkit-details-marker { display: none; }
summary::after { content: "+"; color: var(--gold); font-size: 22px; font-weight: 400; }
details[open] summary::after { content: "–"; }
details p { max-width: 490px; margin-top: 13px; color: var(--muted); font-size: 14px; }

/* 11 CTA Band */
.cta-band { padding: 96px 0; color: #f8f5ef; background: var(--teal-deep); }
.cta-band .wrap { text-align: center; }
.cta-band .eyebrow { color: #f1b68f; }
.cta-band .eyebrow::before { background: #f1b68f; }
.cta-band h2 { max-width: 760px; margin: 18px auto 0; }
.cta-band p { max-width: 560px; margin: 18px auto 0; color: rgba(255,255,255,.72); font-size: 16px; }
.cta-band .hero-actions { justify-content: center; }

/* Modal Backdrop & Panel */
.modal-backdrop {
  display: none;
  position: fixed;
  inset: 0;
  z-index: 2000;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: rgba(9, 27, 35, .75);
}
.modal-backdrop.is-visible { display: flex; }
.success-panel {
  position: relative;
  width: min(100%, 620px);
  max-height: min(86vh, 720px);
  overflow: auto;
  padding: 28px;
  color: var(--ink);
  background: var(--surface);
  border: 1px solid #b9d8d0;
  border-radius: 10px;
  box-shadow: var(--shadow);
  font-size: 13.5px;
}
.success-panel h3 { font-size: 20px; color: var(--teal-deep); }
.success-panel p { margin-top: 8px; color: #435363; line-height: 1.55; }
.modal-close {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 34px;
  height: 34px;
  color: var(--muted);
  background: transparent;
  border: 1px solid var(--line);
  border-radius: 7px;
  font-size: 20px;
  line-height: 1;
}
.modal-close:hover { color: var(--ink); background: #f4eee4; }
.material-title { display: block; margin-top: 16px; color: var(--teal-deep); font-size: 13px; font-weight: 800; }
.material-list { display: grid; gap: 7px; margin: 10px 0 0; padding: 0; list-style: none; }
.material-list li { position: relative; padding-left: 16px; color: #334454; }
.material-list li::before { content: ""; position: absolute; left: 0; top: 9px; width: 5px; height: 5px; background: var(--teal); border-radius: 50%; }
.urgent-note {
  margin-top: 14px;
  padding: 10px 14px;
  color: #6b341d;
  background: #f7e5d6;
  border-radius: 6px;
  line-height: 1.5;
}
.modal-wechat {
  display: grid;
  grid-template-columns: 112px 1fr;
  gap: 16px;
  align-items: center;
  margin-top: 16px;
  padding: 14px;
  background: #f4eee4;
  border: 1px solid #e1d8c9;
  border-radius: 8px;
}
.qr-img-large {
  width: 104px;
  height: 104px;
  object-fit: contain;
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 6px;
}
.modal-wechat strong { display: block; color: var(--teal-deep); font-size: 14px; }
.modal-wechat p { margin-top: 5px; color: var(--muted); font-size: 12px; }
.success-actions { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 18px; }
.success-actions .button { width: auto; min-height: 40px; margin-top: 0; }

@media (max-width: 980px) {
  .trust-strip .wrap { grid-template-columns: repeat(2, 1fr); }
  .trust-item:nth-child(3) { border-left: 0; }
  .trust-item:nth-child(1), .trust-item:nth-child(2) { border-bottom: 1px solid var(--line); }
  .stats-section .wrap { grid-template-columns: repeat(2, 1fr); gap: 18px; }
  .global-grid { grid-template-columns: repeat(3, 1fr); }
  .team-grid, .trust-grid { grid-template-columns: 1fr 1fr; }
}

@media (max-width: 880px) {
  .hero { min-height: auto; padding-top: 130px; }
  .hero-grid { grid-template-columns: 1fr; gap: 40px; }
  .hero-copy { max-width: 760px; }
  .intake-card { max-width: 640px; }
  .service-grid, .process-grid { grid-template-columns: 1fr; }
  .service-card { min-height: 0; }
  .process-step, .process-step + .process-step { min-height: 0; padding: 24px 0; border-left: 0; border-top: 1px solid rgba(255,255,255,.23); }
  .process-step:first-child { border-top: 1px solid rgba(255,255,255,.23); }
  .cases-grid { grid-template-columns: 1fr; }
  .global-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 600px) {
  .section { padding: 64px 0; }
  .hero { padding: 112px 0 62px; }
  .hero::after { height: 60px; }
  .hero-copy p { font-size: 15px; }
  .hero-actions { flex-direction: column; align-items: stretch; }
  .button { width: 100%; }
  .hero-notes { display: grid; gap: 9px; margin-top: 24px; }
  .intake-card { padding: 20px; }
  .contact-options { grid-template-columns: 78px 1fr; gap: 10px; padding: 10px; }
  .qr-img { width: 74px; height: 74px; }
  .intake-grid { grid-template-columns: 1fr; }
  .trust-strip .wrap { grid-template-columns: 1fr; }
  .trust-item { border-left: 0; border-bottom: 1px solid var(--line); }
  .trust-item:last-child { border-bottom: 0; }
  .stats-section .wrap { grid-template-columns: 1fr 1fr; }
  .global-grid { grid-template-columns: 1fr 1fr; }
  .team-grid, .trust-grid { grid-template-columns: 1fr; }
  .faq-grid { grid-template-columns: 1fr; gap: 0; }
  .modal-wechat { grid-template-columns: 84px 1fr; gap: 10px; }
  .qr-img-large { width: 80px; height: 80px; }
}
</style>
