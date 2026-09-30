<template>
  <div class="article-detail-view" :class="{ 'is-rtl': isAr }">
    <div class="wrap detail-container">
      <div v-if="loading" class="loading-box">
        {{ isAr ? 'جارٍ تحميل تفاصيل المقال القانوني...' : (isEs ? 'Cargando artículo legal...' : (isEn ? 'Loading article details...' : '正在加载文章内容...')) }}
      </div>

      <article v-else-if="article" class="detail-paper" :class="{ 'is-rtl': isAr }">
        <NuxtLink :to="isAr ? '/ar/articles' : (isEs ? '/es/articles' : (isEn ? '/en/articles' : '/articles'))" class="back-nav">
          <span v-if="isAr">&rarr; العودة إلى الرؤى القانونية</span>
          <span v-else-if="isEs">&larr; Volver a Artículos Jurídicos</span>
          <span v-else>&larr; {{ isEn ? 'Back to legal insights' : '返回法律专栏' }}</span>
        </NuxtLink>

        <header class="article-header">
          <div class="meta-row">
            <span class="category-tag">{{ getBusinessLabel(article.business) }}</span>
            <span class="date">{{ article.published_at ? article.published_at.substring(0, 10) : '' }}</span>
          </div>
          <h1 class="article-title">{{ title }}</h1>
        </header>

        <!-- GEO & Key Takeaways / Executive Summary Card -->
        <section v-if="keyTakeaways.length" class="geo-takeaways-card" itemscope itemtype="https://schema.org/Answer">
          <div class="takeaways-header">
            <span class="takeaways-icon">⚡</span>
            <h4>{{ isEn ? 'GEO Direct Answer & Key Action Points' : (isAr ? 'إجابة مباشرة وأهم نقاط العمل (GEO)' : (isEs ? 'Respuesta Directa y Puntos Clave de Acción (GEO)' : 'GEO 权威实务快览与核心结论（Direct Answer）')) }}</h4>
            <span class="geo-pill">AI Citation / 核心事实</span>
          </div>
          <ul class="takeaways-list" itemprop="text">
            <li v-for="(item, idx) in keyTakeaways" :key="idx">{{ item }}</li>
          </ul>
        </section>

        <div class="article-body">
          <div class="content-html" v-html="renderedBody"></div>
        </div>

        <!-- Article FAQ & Rich Snippet Module -->
        <div v-if="articleFaqs.length" class="article-faq-section">
          <h3 class="faq-head-title">{{ isEn ? 'Frequently Asked Questions' : (isAr ? 'الأسئلة الشائعة والنقاط القانونية' : (isEs ? 'Preguntas Frecuentes y Aspectos Prácticos' : '常见问题解答与实务要点')) }}</h3>
          <div class="faq-accordion">
            <details v-for="(f, i) in articleFaqs" :key="i" class="art-faq-item">
              <summary>{{ f.question }}</summary>
              <p>{{ f.answer }}</p>
            </details>
          </div>
        </div>

        <div class="article-disclaimer">
          <strong>{{ isEn ? 'Legal Disclaimer & Author' : (isAr ? 'إخلاء المسؤولية وفريق العمل' : (isEs ? 'Aviso Legal y Autoría' : '免责声明与团队主笔')) }}：</strong>
          <span v-if="isAr">
            أُعدت هذه المادة بواسطة <NuxtLink to="/ar" class="disclaimer-link"><strong>فريق المحامين الدوليين شينيوان</strong></NuxtLink> للأغراض الأكاديمية والاطلاع العام ولا تشكل استشارة قانونية رسمية. يُنصح بالتواصل المباشر مع <NuxtLink to="/ar" class="disclaimer-link"><strong>محامٍ دولي</strong></NuxtLink> متخصص لتقييم ظروف وأدلة كل قضية.
          </span>
          <span v-else-if="isEs">
            Este artículo ha sido elaborado por el equipo de <NuxtLink to="/es" class="disclaimer-link"><strong>abogados internacionales Shenyuan</strong></NuxtLink> con fines informativos y de análisis práctico; no constituye dictamen legal vinculante. Se recomienda consultar a un <NuxtLink to="/es" class="disclaimer-link"><strong>abogado internacional</strong></NuxtLink> colegiado para evaluar las pruebas y plazos de su caso.
          </span>
          <span v-else-if="isEn">
            This guide is prepared by the <NuxtLink to="/en" class="disclaimer-link"><strong>Shenyuan International Lawyers</strong></NuxtLink> team for informational and practice analysis purposes and does not constitute formal legal opinion. For cross-border dispute assessment, please consult a qualified <NuxtLink to="/en" class="disclaimer-link"><strong>international lawyer</strong></NuxtLink>.
          </span>
          <span v-else>
            本文由<NuxtLink to="/" class="disclaimer-link"><strong>深远涉外国际律师团队</strong></NuxtLink>主笔，仅供涉外法律实务研讨与一般信息参考，不构成针对任何具体案件的正式法律意见。具体法律程序须结合案件全部证据、事实及相关管辖区时效一案一议，建议在采取行动前咨询执业<NuxtLink to="/" class="disclaimer-link"><strong>国际律师</strong></NuxtLink>。
          </span>
        </div>

        <!-- Pillar Hubs Interlinking Matrix (Topic Cluster Anchor) -->
        <div v-if="matchedService || matchedCountry" class="pillar-hubs-matrix">
          <div v-if="matchedService" class="pillar-hub-card">
            <span class="hub-label">{{ isEn ? 'Core Practice Area Hub' : (isAr ? 'مجال الممارسة الرئيسي' : (isEs ? 'Área Principal de Práctica' : '核心业务支柱专区')) }}</span>
            <NuxtLink :to="isAr ? `/ar/services/${matchedService.slug}` : (isEs ? `/es/services/${matchedService.slug}` : (isEn ? `/en/services/${matchedService.slug}` : `/services/${matchedService.slug}`))" class="hub-link">
              <h4>{{ matchedService.name }} &rarr;</h4>
              <p>{{ matchedService.desc }}</p>
            </NuxtLink>
          </div>
          <div v-if="matchedCountry" class="pillar-hub-card country-hub">
            <span class="hub-label">{{ isEn ? 'Relevant Jurisdiction Hub' : (isAr ? 'المركز الإقليمي للاختصاص القضائي' : (isEs ? 'Centro Jurisdiccional Relacionado' : '关联国别法域专区')) }}</span>
            <NuxtLink :to="isAr ? `/ar/countries/${matchedCountry.slug}` : (isEs ? `/es/countries/${matchedCountry.slug}` : (isEn ? `/en/countries/${matchedCountry.slug}` : `/countries/${matchedCountry.slug}`))" class="hub-link">
              <h4>{{ matchedCountry.name }} {{ isEn ? 'Cross-Border Legal Hub' : (isAr ? 'المركز القانوني' : (isEs ? 'Portal Legal' : '跨境法律专区')) }} &rarr;</h4>
              <p>{{ isEn ? `Explore dispute resolution procedures, limitation periods, and local enforcement rules for ${matchedCountry.name}.` : (isAr ? `تعرف على إجراءات التقاضي، مدد التقادم، وقواعد التنفيذ المتبعة في ${matchedCountry.name}.` : (isEs ? `Conozca los procedimientos judiciales, plazos de prescripción y normas de ejecución en ${matchedCountry.name}.` : `查看针对${matchedCountry.name}的涉外诉讼管辖、判决承认执行与实务要点`)) }}</p>
            </NuxtLink>
          </div>
        </div>

        <!-- Related Articles / Topic Cluster -->
        <div v-if="relatedArticles.length" class="related-articles-section">
          <div class="related-head">
            <h3>{{ isEn ? 'Related Legal Insights' : (isAr ? 'رؤى قانونية ذات صلة ومقالات مقترحة' : (isEs ? 'Artículos Jurídicos Relacionados' : '相关法律实务与推荐阅读')) }}</h3>
            <NuxtLink :to="isAr ? '/ar/articles' : (isEs ? '/es/articles' : (isEn ? '/en/articles' : '/articles'))" class="more-link">
              {{ isEn ? 'View all' : (isAr ? 'عرض الكل' : (isEs ? 'Ver todos' : '查看全部')) }} &rarr;
            </NuxtLink>
          </div>
          <div class="related-grid">
            <NuxtLink
              v-for="rel in relatedArticles"
              :key="rel.id"
              :to="isAr ? `/ar/articles/${rel.slug}` : (isEs ? `/es/articles/${rel.slug}` : (isEn ? `/en/articles/${rel.slug}` : `/articles/${rel.slug}`))"
              class="related-card"
            >
              <span class="rel-badge">{{ getBusinessLabel(rel.business) }}</span>
              <h4 class="rel-title">{{ isAr ? (rel.translations?.ar?.title || rel.title_en || rel.title_zh) : (isEs ? (rel.translations?.es?.title || rel.title_en || rel.title_zh) : (isEn ? (rel.title_en || rel.title_zh) : rel.title_zh)) }}</h4>
              <p class="rel-desc">{{ isAr ? (rel.translations?.ar?.description || rel.description_en || rel.description_zh) : (isEs ? (rel.translations?.es?.description || rel.description_en || rel.description_zh) : (isEn ? (rel.description_en || rel.description_zh) : rel.description_zh)) }}</p>
            </NuxtLink>
          </div>
        </div>

        <!-- Article Bottom Consultation Box -->
        <div class="bottom-consult-box">
          <div class="consult-copy">
            <h3>{{ isEn ? 'Facing a similar cross-border legal issue?' : (isAr ? 'هل تواجه نزاعاً تجارياً عابراً للحدود أو تحتاج دعماً قانونياً؟' : (isEs ? '¿Enfrenta una disputa transfronteriza similar o requiere asistencia legal?' : '遇到涉外纠纷？预约国际律师一对一专业评估')) }}</h3>
            <p>{{ isEn 
              ? 'Our bilingual international lawyers provide strategic cross-border dispute assessment and asset recovery within 24 hours.' 
              : (isAr
                ? 'فريقنا من المحامين الدوليين مستعد لتقييم موقفكم القانوني وتنفيذ إجراءات الحجز والتحصيل العابرة للحدود.'
                : (isEs
                  ? 'Nuestro equipo de abogados internacionales evalúa su caso y diseña rutas de embargo y cobro transfronterizo en 24 horas.'
                  : '深远涉外国际律师团队深度联动全球 30+ 国执业法务网络，24 小时内为您出具诉讼时效、管辖权异议与财产冻结初步策略。')) }}</p>
          </div>
          <NuxtLink :to="isAr ? '/ar#intake' : (isEs ? '/es#intake' : (isEn ? '/en#intake' : '/#intake'))" class="button button-primary">
            {{ isEn ? 'Consult International Lawyers →' : (isAr ? 'استشارة محامٍ دولي ←' : (isEs ? 'Consultar Abogado Internacional →' : '预约国际律师评估 →')) }}
          </NuxtLink>
        </div>
      </article>

      <div v-else class="not-found">
        <p>{{ isEn ? 'Article not found.' : (isAr ? 'لم يتم العثور على المقال المطلوب.' : (isEs ? 'Artículo no encontrado.' : '未找到相关文章。')) }}</p>
        <NuxtLink :to="isAr ? '/ar/articles' : (isEs ? '/es/articles' : (isEn ? '/en/articles' : '/articles'))" class="button button-outline">
          {{ isEn ? 'Return to Articles' : (isAr ? 'العودة إلى قائمة المقالات' : (isEs ? 'Volver a Artículos' : '返回专栏列表')) }}
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { getApiClient } from '@/api/client'

import { useCurrentLang } from '@/composables/useCurrentLang'

const { route, currentLang, isAr, isEs, isEn } = useCurrentLang()

function getBusinessLabel(b?: string): string {
  const code = (b || 'trade').toLowerCase()
  if (code.includes('trade') || code.includes('贸易')) {
    if (isAr.value) return 'التجارة الدولية'
    if (isEs.value) return 'Comercio Internacional'
    if (isEn.value) return 'Trade Disputes'
    return '国际贸易争议'
  }
  if (code.includes('recovery') || code.includes('追收') || code.includes('诉讼') || code.includes('债')) {
    if (isAr.value) return 'تحصيل الديون'
    if (isEs.value) return 'Recobro de Deudas'
    if (isEn.value) return 'Debt Recovery'
    return '诉讼与债务追收'
  }
  if (code.includes('legacy') || code.includes('继承') || code.includes('家事') || code.includes('资产')) {
    if (isAr.value) return 'الميراث العائلي'
    if (isEs.value) return 'Herencias Familiares'
    if (isEn.value) return 'Inheritance'
    return '继承与家族资产'
  }
  if (isAr.value) return 'قانون دولي'
  if (isEs.value) return 'Práctica Legal'
  if (isEn.value) return 'Cross-Border'
  return '涉外法律实务'
}

// Article bodies are fetched during SSR so crawlers receive the full text,
// title, canonical, hreflang and JSON-LD in the initial HTML response.
// Load all articles to derive related recommendations within the same topic cluster
const { data: allArticles } = await useAsyncData(
  'all-articles-cluster',
  async () => {
    try {
      const res = await getApiClient().get('/api/articles')
      if (Array.isArray(res.data) && res.data.length > 0) return res.data
    } catch (e) {
      // fallback to direct $fetch
    }
    try {
      const data: any = await $fetch('https://shenyuan-backend.vercel.app/api/articles')
      return Array.isArray(data) ? data : []
    } catch (e) {
      return []
    }
  }
)

// FAQ dataset mapped by business category for on-page Q&A and FAQPage JSON-LD
// Extract structured key takeaways / executive summary for GEO & rapid answer engines
const keyTakeaways = computed(() => {
  const art: any = article.value
  if (!art) return []
  const b = art.business || 'trade'

  if (isAr.value) {
    if (b === 'trade') {
      return [
        'تثبيت سلسلة الأدلة التجارية: الاحتفاظ بأصول العقود، الفواتير، بوالص الشحن (B/L)، ومحاضر الفحص الجمركي قبل إرسال أي إنذار رسمي.',
        'تدقيق مدة التقادم القانوني: تتراوح مدد التقادم في النزاعات التجارية العابرة للحدود بين سنتين و 6 سنوات، مع إمكانية قطع التقادم بالمطالبة الخطية.',
        'إجراءات الحماية المتدرجة: توجيه إنذار قانوني رسمي يحدد مهلة سداد حتمية، يليه استصدار أوامر قضائية بالحجز التحفظي أو اللجوء للتحكيم الدولي.'
      ]
    } else if (b === 'recovery') {
      return [
        'التحري المالي وتتبع الأصول: فحص الأصول العقارية والحسابات المصرفية والشركات التابعة للمدين داخل الصين وخارجها قبل تحريك الإجراءات العلنية.',
        'طلب الحجز التحفظي الفوري: استصدار أوامر تجميد الأصول المصرفية لمنع المدين من تهريب أمواله إلى ولايات قضائية أخرى.',
        'إنفاذ الأحكام عبر الحدود: تنفيذ قرارات التحكيم الدولي بموجب اتفاقية نيويورك 1958، والاعتراف بالأحكام وفق مبدأ المعاملة بالمثل والاتفاقيات الثنائية.'
      ]
    } else {
      return [
        'تحديد القانون الواجب التطبيق: تخضع العقارات لقانون موقع العقار (Lex Situs)، وتتطلب التركات العقارية إجراءات حصر إرث قضائية محلية.',
        'حزمة التوثيق والتصديق الدولي: استخراج شهادات القرابة والوفاة والوصايا وتصديقها بأبوستيل (Apostille) لضمان حجيتها القانونية.',
        'تسوية الالتزامات والضرائب: إنهاء الإقرارات الضريبية العقارية وتصفية ديون التركة قبل تحويل وتوزيع الحصص الإرثية بين الورثة.'
      ]
    }
  }

  if (isEs.value) {
    if (b === 'trade') {
      return [
        'Aseguramiento de la Cadena Probatoria: Preservar contratos firmados, órdenes de compra, conocimientos de embarque (B/L) y despachos aduaneros antes de intimar al deudor.',
        'Auditoría de Prescripción Extintiva: Verificar los plazos legales de reclamación (habitualmente entre 2 y 6 años según la ley aplicable del contrato).',
        'Estrategia Escalonada de Cobro: Emisión de requerimiento notarial/burofax con plazo perentorio; en caso de falta de pago, instar medidas cautelares o arbitraje.'
      ]
    } else if (b === 'recovery') {
      return [
        'Investigación Patrimonial Previa: Localización forense de inmuebles, participaciones societarias y cuentas bancarias del deudor antes de alertarlo.',
        'Embargo Preventivo de Activos: Solicitud judicial de medidas cautelares urgentes para congelar bienes y evitar el vaciamiento patrimonial.',
        'Ejecución Transfronteriza de Resoluciones: Ejecución de laudos bajo la Convención de Nueva York de 1958 y homologación de sentencias foráneas vía exequátur.'
      ]
    } else {
      return [
        'Régimen Sucesorio de Bienes Inmuebles: Los inmuebles se rigen por la ley de su situación (Lex Rei Sitae); los testamentos foráneos exigen apertura judicial local.',
        'Cadena Notarial y Apostilla de La Haya: Certificados de defunción, actas de parentesco y poderes deben contar con Apostilla de La Haya para surtir efectos legales.',
        'Liquidación Fiscal y Reparto Hereditario: Tramitar la declaración del Impuesto sobre Sucesiones y cancelación de cargas antes de adjudicar los bienes.'
      ]
    }
  }

  if (isEn.value) {
    if (b === 'trade') {
      return [
        'Document Trail: Secure contracts, invoices, bills of lading, customs clearances, and bank slips before formal notice.',
        'Limitation Audit: Confirm the applicable limitation window (commonly 2–6 years depending on foreign or PRC law).',
        'Structured Notice: Issue a formal bilingual attorney demand letter to set firm cure deadlines and preserve rights.'
      ]
    } else if (b === 'recovery') {
      return [
        'Asset Tracing: Verify corporate registry, property, bank, and transaction records prior to alerting the debtor.',
        'Preservation Orders: Apply for freezing injunctions or interim measures to safeguard enforceable assets.',
        'Cross-Border Enforcement: Enforce arbitral awards via New York Convention or money judgments via bilateral reciprocity.'
      ]
    } else {
      return [
        'Jurisdiction Mapping: Real property is strictly governed by the lex situs; cross-border wills require local probate.',
        'Notarisation & Apostille: Kinship, wills, and death certificates must be apostilled/legalised for local admissibility.',
        'Estate Inventory: Account for tax filings, foreign exchange regulations, and creditor liabilities before distribution.'
      ]
    }
  } else {
    if (b === 'trade') {
      return [
        '锁定证据底牌：在正式发函前，集中保存合同、订单、发票、提单、报关单及微信邮件对账凭单原件。',
        '核实诉讼时效：跨境商事时效常见为 2~6 年，若客户曾书面认账，可重新起算或中断，务必尽早确权。',
        '阶梯维权策略：先发正式涉外律师函设定限期和解窗口；谈判无果时果断衔接仲裁或涉外诉讼。'
      ]
    } else if (b === 'recovery') {
      return [
        '境内外财产调查：重点核查债务人名下房产、股权、银行存款及关联交易，摸清真实执行能力。',
        '同步申请财产保全：在债务人转移或隐匿资产前取得法院冻结令，确保护城河与执行标的安全。',
        '判决/裁决跨国兑现：仲裁裁决依托《纽约公约》在160多国直接申请执行，涉外判决依互惠/条约推进。'
      ]
    } else {
      return [
        '区分不动产与动产属地：跨境不动产继承适用遗产所在地法，国内遗嘱通常需经当地遗嘱认证（Probate）。',
        '一揽子公证与海牙认证：亲属关系证明、死亡证明及授权委托书需一次性做足公证与海牙附加证明书（Apostille）。',
        '统筹税费与外汇合规：兼顾境外遗产税申报与合法继承资金合规结汇汇回，避免程序返工与合规风险。'
      ]
    }
  }
})

const articleFaqs = computed(() => {
  const art: any = article.value
  if (!art) return []
  const b = art.business || 'trade'

  if (isAr.value) {
    if (b === 'trade') {
      return [
        {
          question: 'ما هي الخطوة الأكثر أهمية عند نشوء نزاع حول سداد قيمة صفقة تجارية دولية؟',
          answer: 'التثبيت الفوري لكامل سلسلة الأدلة الكتابية والإلكترونية (العقود، بوالص الشحن، مستندات الإفراج الجمركي، إقرارات المطابقة، والمراسلات المؤكدة للمديونية)، والتحقق العاجل من مدة التقادم لتفادي سقوط الحق القانوني.'
        },
        {
          question: 'هل يمكن حل النزاعات التجارية العابرة للحدود دون اللجوء المباشر إلى المحاكم الأجنبية؟',
          answer: 'نعم. يمكن من خلال توجيه إنذار قانوني رسمي عبر محامٍ معتمد، مدعوماً بنتائج التحري المالي عن أصول المدين وتجميد المعاملات، الضغط بفعالية للتوصل إلى تسوية ودية موثقة قبل التقاضي.'
        }
      ]
    } else if (b === 'recovery') {
      return [
        {
          question: 'هل يمكن تنفيذ أحكام المحاكم وقرارات التحكيم الصادرة في الصين داخل دول الشرق الأوسط؟',
          answer: 'نعم. تنفذ قرارات التحكيم التجاري بسهولة بموجب اتفاقية نيويورك 1958. كما تنفذ الأحكام القضائية بالاستناد إلى اتفاقيات المساعدة القضائية الثنائية (مثل اتفاقية الصين والإمارات لعام 2004) أو مبدأ المعاملة بالمثل.'
        },
        {
          question: 'ما الإجراء القانوني الواجب اتخاذه إذا شرع المدين في تحويل أو إخفاء أصوله في الخارج؟',
          answer: 'يجب تقديم طلب عاجل إلى القضاء المختص لاستصدار أمر حجز تحفظي وتجميد حسابات مصرفية لمنع تبديد الأصول بانتظار صدور الحكم النهائي القابل للتنفيذ.'
        }
      ]
    } else {
      return [
        {
          question: 'هل تسري الوصية المحررة في الصين بصورة تلقائية على العقارات والحسابات في الخارج؟',
          answer: 'لا تسري تلقائياً. تخضع العقارات لقانون موقعها الجغرافي، وغالباً ما تتطلب إجراءات اعتماد قضائية خاصة بالتركات (Probate) والتأكد من مطابقتها للنظام القانوني المحلي.'
        },
        {
          question: 'ما هي المستندات الأساسية المطلوبة لمباشرة إجراءات حصر الإرث للأصول الدولية؟',
          answer: 'يلزم تقديم شهادات الوفاة، وإثبات صلة القرابة الرسمي، وأصول الوصايا موثقة ومصدقة بخاتم الأبوستيل (Apostille)، وتوكيل محامٍ معتمد لمباشرة الإجراءات أمام محكمة التركات.'
        }
      ]
    }
  }

  if (isEs.value) {
    if (b === 'trade') {
      return [
        {
          question: '¿Cuál es el primer paso indispensable ante un impago en operaciones de comercio exterior?',
          answer: 'Preservar de forma inmediata toda la prueba documental y electrónica (contratos, B/L, facturas comerciales, despachos aduaneros y reconocimientos de deuda) y auditar el plazo de prescripción extintiva de la acción.'
        },
        {
          question: '¿Es obligatorio acudir a juicio en el extranjero para resolver una controversia mercantil?',
          answer: 'No necesariamente. La remisión de un requerimiento notarial o burofax letrado, combinado con un informe de solvencia patrimonial, permite alcanzar acuerdos transaccionales en un alto porcentaje de reclamaciones de cantidad.'
        }
      ]
    } else if (b === 'recovery') {
      return [
        {
          question: '¿Se puede ejecutar una sentencia o laudo arbitral chino en España o Latinoamérica?',
          answer: 'Sí. Los laudos arbitrales se ejecutan mediante la Convención de Nueva York de 1958 en más de 160 países. Las sentencias judiciales se homologan mediante procedimiento de exequátur al amparo de tratados bilaterales o reciprocidad.'
        },
        {
          question: '¿Cómo actuar si el deudor transfiere o disimula activos en el extranjero?',
          answer: 'Debe interponerse con carácter de urgencia una solicitud de medidas cautelares previas de embargo preventivo de cuentas bancarias y bienes inmuebles para salvaguardar la eficacia del cobro.'
        }
      ]
    } else {
      return [
        {
          question: '¿Surte efectos directos un testamento otorgado en China sobre inmuebles radicados en el exterior?',
          answer: 'No de manera automática. La transmisión de bienes inmuebles se somete al derecho sucesorio del lugar de su situación (Lex Situs), exigiendo la legalización del título sucesorio ante el Notario o Juzgado competente.'
        },
        {
          question: '¿Qué documentación se precisa para tramitar una herencia internacional?',
          answer: 'Se precisa el certificado de defunción internacional, actas notariales de declaración de herederos debidamente apostilladas bajo el Convenio de La Haya y la representación letrada en la jurisdicción donde radiquen los bienes.'
        }
      ]
    }
  }

  if (b === 'trade') {
    return isEn.value ? [
      {
        question: 'What is the most critical first step in an international trade payment dispute?',
        answer: 'Immediately preserve all documentary evidence (contracts, bills of lading, customs declarations, communication trails, and acknowledged statements of account) and verify whether the statute of limitations is at risk.'
      },
      {
        question: 'Can cross-border trade disputes be resolved without going to court?',
        answer: 'Yes. A structured bilingual attorney demand letter combined with staged commercial negotiation and asset-tracing pressure resolves a substantial portion of cross-border debt defaults.'
      }
    ] : [
      {
        question: '发生跨境贸易货款拖欠时，第一步最关键的动作是什么？',
        answer: '第一时间固定全部书面与电子证据链（合同、提单、报关单、对账单与邮件微信记录），并立即核实涉外法律适用的诉讼时效，避免权利因拖延而灭失。'
      },
      {
        question: '涉外贸易纠纷必须到境外打官司吗？是否有更高效的解决途径？',
        answer: '不一定。大部分跨国商事欠款可通过专业涉外律师函、针对性调查财产线索施加谈判压力、以及分期担保协议在诉讼前达成和解，大幅节约境外诉讼周期与成本。'
      }
    ]
  } else if (b === 'recovery') {
    return isEn.value ? [
      {
        question: 'Can a Chinese court judgment or arbitral award be enforced overseas?',
        answer: 'Yes. Arbitral awards are widely enforceable under the New York Convention across 160+ jurisdictions. Court judgments can be enforced in jurisdictions recognizing reciprocity or bilateral treaties.'
      },
      {
        question: 'What should creditors do if a debtor attempts to hide or transfer assets abroad?',
        answer: 'Initiate lawful cross-border asset tracing promptly and apply for freezing orders or interim preservation relief before the competent local court to secure enforceable assets.'
      }
    ] : [
      {
        question: '中国法院的胜诉判决或仲裁裁决能否在境外申请执行？',
        answer: '可以。仲裁裁决可通过《纽约公约》在 160 多个缔约国申请承认与执行；法院判决可依据双边司法协助条约或互惠原则在境外目标法院申请承认后执行。'
      },
      {
        question: '如果债务人将资金或房产转移至海外，债权人该如何应对？',
        answer: '应尽早通过合法途径开展境内外资产线索调查，并在具备管辖权的法域申请临时财产保全、冻结令或撤销恶意转移之诉，防止最终执行落空。'
      }
    ]
  } else {
    // legacy
    return isEn.value ? [
      {
        question: 'Does a will made in China automatically govern overseas properties and accounts?',
        answer: 'Not necessarily. Real estate typically follows the lex situs (law of the jurisdiction where the property is located). Cross-border inheritance often requires local probate or estate administration.'
      },
      {
        question: 'What documents are required for heirs in China to claim an overseas inheritance?',
        answer: 'Heirs usually need notarized and legalized/apostilled proof of kinship, local death certificates, wills (if any), and estate inventories to initiate formal local probate proceedings.'
      }
    ] : [
      {
        question: '在中国立的遗嘱能否直接处分海外的不动产和银行存款？',
        answer: '不一定。涉外继承中不动产通常适用不动产所在地法律，中国遗嘱在海外普通法系国家常需通过当地遗嘱认证（Probate）程序并检验形式合规性。'
      },
      {
        question: '国内继承人办理海外亲属遗产继承通常需要准备哪些公证认证文件？',
        answer: '一般需要办理死亡证明、亲属关系证明、法定遗嘱（如有）及海牙认证（Apostille）或领事认证，并委托当地具有执业资质的律师向遗产所在地法院申请遗产清点与过户。'
      }
    ]
  }
})

const relatedArticles = computed(() => {
  const current = article.value
  if (!current || !allArticles.value) return []
  return allArticles.value
    .filter((a: any) => {
      if (a.slug === current.slug) return false
      if (current.business && a.business !== current.business) return false
      if (isAr.value) {
        const ar = a.translations?.ar
        return Boolean(ar && ar.title && ar.title !== '...' && ar.title.trim().length > 3)
      }
      if (isEs.value) {
        const es = a.translations?.es
        return Boolean(es && es.title && es.title !== '...' && es.title.trim().length > 3)
      }
      if (isEn.value) {
        return Boolean(a.title_en || a.translations?.en?.title)
      }
      return true
    })
    .slice(0, 3)
})

const { data: article, pending: loading } = await useAsyncData(
  `article-${currentLang.value}-${route.params.slug}`,
  async () => {
    const slug = route.params.slug
    try {
      const res = await getApiClient().get(`/api/articles/${slug}`)
      if (res?.data?.slug) return res.data
    } catch (err) {
      // fallback to direct $fetch
    }
    try {
      const data: any = await $fetch(`https://shenyuan-backend.vercel.app/api/articles/${slug}`)
      if (data?.slug) return data
    } catch (err) {
      console.error('Failed to load article detail', err)
    }
    return null
  }
)

// 轻量级安全 Markdown 语义解析器（增强 SEO 语义、表格解析与阅读排版）
function parseMarkdownToHtml(md: string): string {
  if (!md) return ''
  const lines = md.replace(/\r\n/g, '\n').split('\n')
  const htmlParts: string[] = []
  let inList = false
  let inTable = false
  let tableHeaders: string[] = []
  let tableRows: string[][] = []

  const flushTable = () => {
    if (!inTable) return
    let tHtml = '<div class="article-table-wrap"><table class="article-table">'
    if (tableHeaders.length) {
      tHtml += '<thead><tr>'
      for (const h of tableHeaders) {
        tHtml += `<th>${formatInline(h)}</th>`
      }
      tHtml += '</tr></thead>'
    }
    if (tableRows.length) {
      tHtml += '<tbody>'
      for (const row of tableRows) {
        tHtml += '<tr>'
        for (const cell of row) {
          tHtml += `<td>${formatInline(cell)}</td>`
        }
        tHtml += '</tr>'
      }
      tHtml += '</tbody>'
    }
    tHtml += '</table></div>'
    htmlParts.push(tHtml)
    inTable = false
    tableHeaders = []
    tableRows = []
  }

  for (let i = 0; i < lines.length; i++) {
    let line = lines[i].trimEnd()
    const trimmed = line.trim()

    // 表格解析：行以 | 开头并以 | 结尾且含有分割管道
    const isTableRow = trimmed.startsWith('|') && trimmed.endsWith('|') && trimmed.includes('|')

    if (isTableRow) {
      if (inList) {
        htmlParts.push('</ul>')
        inList = false
      }
      const rawCells = trimmed.split('|').slice(1, -1).map(c => c.trim())
      // 检查是否为分隔行，例如 |---|---|---|
      const isSeparator = rawCells.length > 0 && rawCells.every(c => /^:?-+:?$/.test(c))
      if (isSeparator) {
        continue
      }
      if (!inTable) {
        inTable = true
        tableHeaders = rawCells
      } else {
        tableRows.push(rawCells)
      }
      continue
    } else if (inTable) {
      flushTable()
    }

    // 列表处理
    if (/^[-*]\s+/.test(line)) {
      if (!inList) {
        htmlParts.push('<ul class="article-list">')
        inList = true
      }
      const itemText = formatInline(line.replace(/^[-*]\s+/, ''))
      htmlParts.push(`<li>${itemText}</li>`)
      continue
    } else if (inList) {
      htmlParts.push('</ul>')
      inList = false
    }

    if (!line.trim()) {
      continue
    }

    // 标题处理
    if (line.startsWith('#### ')) {
      htmlParts.push(`<h4>${formatInline(line.slice(5))}</h4>`)
    } else if (line.startsWith('### ')) {
      htmlParts.push(`<h3>${formatInline(line.slice(4))}</h3>`)
    } else if (line.startsWith('## ')) {
      htmlParts.push(`<h2>${formatInline(line.slice(3))}</h2>`)
    } else if (line.startsWith('# ')) {
      // 避免正文中重复大标题，转为 h2
      htmlParts.push(`<h2>${formatInline(line.slice(2))}</h2>`)
    } else if (line.startsWith('> ')) {
      htmlParts.push(`<blockquote><p>${formatInline(line.slice(2))}</p></blockquote>`)
    } else {
      htmlParts.push(`<p>${formatInline(line)}</p>`)
    }
  }

  if (inList) {
    htmlParts.push('</ul>')
  }
  if (inTable) {
    flushTable()
  }

  return htmlParts.join('\n')
}

function formatInline(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, text, url) => `<a href="${url}" class="article-link">${text}</a>`)
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
}

const arTrans = computed(() => {
  const trans = (article.value as any)?.translations
  return (trans && typeof trans === 'object') ? trans.ar : null
})

const esTrans = computed(() => {
  const trans = (article.value as any)?.translations
  return (trans && typeof trans === 'object') ? trans.es : null
})

const renderedBody = computed(() => {
  if (!article.value) return ''
  if (isAr.value) {
    if (arTrans.value?.body) {
      return parseMarkdownToHtml(arTrans.value.body)
    }
    const fallbackText = `> ⚠️ **ملاحظة:** الترجمة العربية لهذا الدليل قيد الاعتماد والمراجعة القانونية.\n\n` +
      (article.value.body_en || article.value.body_zh)
    return parseMarkdownToHtml(fallbackText)
  }
  if (isEs.value) {
    if (esTrans.value?.body) {
      return parseMarkdownToHtml(esTrans.value.body)
    }
    const fallbackText = `> ⚠️ **Nota:** La versión oficial en español de esta guía jurídica está en proceso de revisión legal.\n\n` +
      (article.value.body_en || article.value.body_zh)
    return parseMarkdownToHtml(fallbackText)
  }
  const raw = isEn.value
    ? (article.value.body_en || article.value.body_zh)
    : (article.value.body_zh || article.value.body_en)
  return parseMarkdownToHtml(raw)
})

// ---- SEO --------------------------------------------------------------
const siteUrl = 'https://shenyuanlegal.com'

const title = computed(() => {
  const art: any = article.value
  if (!art) return ''
  if (isAr.value) {
    if (arTrans.value?.title && arTrans.value.title !== '...' && arTrans.value.title.trim().length > 3) {
      return arTrans.value.title
    }
    if (art.title_en) return art.title_en
    return 'دليل الممارسة القانونية والنزاعات الدولية (قيد الترجمة والاعتماد)'
  }
  if (isEs.value) {
    if (esTrans.value?.title && esTrans.value.title !== '...' && esTrans.value.title.trim().length > 3) {
      return esTrans.value.title
    }
    if (art.title_en) return art.title_en
    return 'Guía de Práctica Jurídica Internacional (En proceso de traducción)'
  }
  return isEn.value ? (art.title_en || art.title_zh) : art.title_zh
})

const description = computed(() => {
  const art: any = article.value
  if (!art) return ''
  if (isAr.value && arTrans.value?.description) return arTrans.value.description
  if (isEs.value && esTrans.value?.description) return esTrans.value.description
  return isEn.value ? (art.description_en || art.description_zh) : art.description_zh
})

const zhPath = computed(() => `/articles/${route.params.slug}`)
const enPath = computed(() => `/en/articles/${route.params.slug}`)
const arPath = computed(() => `/ar/articles/${route.params.slug}`)
const esPath = computed(() => `/es/articles/${route.params.slug}`)

const canonical = computed(() => {
  if (isAr.value) return `${siteUrl}${arPath.value}`
  if (isEs.value) return `${siteUrl}${esPath.value}`
  if (isEn.value) return `${siteUrl}${enPath.value}`
  return `${siteUrl}${zhPath.value}`
})

const siteName = computed(() => {
  if (isAr.value) return 'مكتب شينيوان الدولي للمحاماة (Shenyuan International)'
  if (isEs.value) return 'Bufete de Abogados Internacional Shenyuan'
  return isEn.value ? 'Shenyuan International Law Firm' : '深远(国际)律师事务所'
})

const hasArabic = computed(() => {
  const trans = (article.value as any)?.translations
  return Boolean(trans && trans.ar && (trans.ar.title || trans.ar.body))
})

const hasSpanish = computed(() => {
  const trans = (article.value as any)?.translations
  return Boolean(trans && trans.es && (trans.es.title || trans.es.body))
})

const alternateLinks = computed(() => {
  const links = [
    { rel: 'canonical', href: () => canonical.value },
    { rel: 'alternate', hreflang: 'zh-CN', href: () => `${siteUrl}${zhPath.value}` },
    { rel: 'alternate', hreflang: 'en', href: () => `${siteUrl}${enPath.value}` },
  ]
  // 严格遵守 SEO 原则：当且仅当存在真实阿语/西语内容时，向搜索引擎声明 hreflang
  if (hasArabic.value || isAr.value) {
    links.push({ rel: 'alternate', hreflang: 'ar', href: () => `${siteUrl}${arPath.value}` })
  }
  if (hasSpanish.value || isEs.value) {
    links.push({ rel: 'alternate', hreflang: 'es', href: () => `${siteUrl}${esPath.value}` })
  }
  links.push({ rel: 'alternate', hreflang: 'x-default', href: () => `${siteUrl}${zhPath.value}` })
  return links
})

useSeoMeta({
  title: () => title.value ? `${title.value} | ${siteName.value}` : siteName.value,
  description: () => description.value,
  ogTitle: () => title.value || siteName.value,
  ogDescription: () => description.value,
  ogType: 'article',
  ogUrl: () => canonical.value,
  ogImage: () => `${siteUrl}/og-image.png`,
  twitterCard: 'summary_large_image',
  twitterTitle: () => title.value || siteName.value,
  twitterDescription: () => description.value,
  twitterImage: () => `${siteUrl}/og-image.png`,
})

// ---- Pillar-Cluster Hub Interlinking ----------------------------------
const COUNTRY_SLUGS = [
  { slug: 'united-arab-emirates', zh: '阿联酋', en: 'UAE (Dubai)', ar: 'الإمارات (دبي)', es: 'EAU (Dubái)', aliases: ['阿联酋', '迪拜', 'dubai', 'uae', 'emirates'] },
  { slug: 'spain', zh: '西班牙', en: 'Spain', ar: 'إسبانيا', es: 'España', aliases: ['西班牙', 'spain', 'madrid', 'barcelona', '马德里'] },
  { slug: 'united-states', zh: '美国', en: 'United States', ar: 'الولايات المتحدة', es: 'Estados Unidos', aliases: ['美国', '美方', 'us', 'usa', 'united states', '加州', '纽约'] },
  { slug: 'united-kingdom', zh: '英国', en: 'United Kingdom', ar: 'المملكة المتحدة', es: 'Reino Unido', aliases: ['英国', 'uk', 'london', 'united kingdom'] },
  { slug: 'singapore', zh: '新加坡', en: 'Singapore', ar: 'سنغافورة', es: 'Singapur', aliases: ['新加坡', 'singapore'] },
  { slug: 'germany', zh: '德国', en: 'Germany', ar: 'ألمانيا', es: 'Alemania', aliases: ['德国', 'germany'] },
  { slug: 'canada', zh: '加拿大', en: 'Canada', ar: 'كندا', es: 'Canadá', aliases: ['加拿大', 'canada'] },
  { slug: 'australia', zh: '澳大利亚', en: 'Australia', ar: 'أستراليا', es: 'Australia', aliases: ['澳大利亚', '澳洲', 'australia'] },
  { slug: 'hong-kong', zh: '中国香港', en: 'Hong Kong', ar: 'هونغ كونغ', es: 'Hong Kong', aliases: ['香港', 'hong kong'] },
  { slug: 'brazil', zh: '巴西', en: 'Brazil', ar: 'البرازيل', es: 'Brasil', aliases: ['巴西', 'brazil'] },
  { slug: 'france', zh: '法国', en: 'France', ar: 'فرنسا', es: 'Francia', aliases: ['法国', 'france'] },
  { slug: 'italy', zh: '意大利', en: 'Italy', ar: 'إيطاليا', es: 'Italia', aliases: ['意大利', 'italy'] },
  { slug: 'japan', zh: '日本', en: 'Japan', ar: 'اليابان', es: 'Japón', aliases: ['日本', 'japan'] },
  { slug: 'south-korea', zh: '韩国', en: 'South Korea', ar: 'كوريا الجنوبية', es: 'Corea del Sur', aliases: ['韩国', 'korea'] },
  { slug: 'netherlands', zh: '荷兰', en: 'Netherlands', ar: 'هولندا', es: 'Países Bajos', aliases: ['荷兰', 'netherlands'] },
  { slug: 'switzerland', zh: '瑞士', en: 'Switzerland', ar: 'سويسرا', es: 'Suiza', aliases: ['瑞士', 'switzerland'] },
  { slug: 'thailand', zh: '泰国', en: 'Thailand', ar: 'تايلاند', es: 'Tailandia', aliases: ['泰国', 'thailand'] },
  { slug: 'vietnam', zh: '越南', en: 'Vietnam', ar: 'فيتنام', es: 'Vietnam', aliases: ['越南', 'vietnam'] },
  { slug: 'malaysia', zh: '马来西亚', en: 'Malaysia', ar: 'ماليزيا', es: 'Malasia', aliases: ['马来西亚', 'malaysia'] },
  { slug: 'new-zealand', zh: '新西兰', en: 'New Zealand', ar: 'نيوزيلندا', es: 'Nueva Zelanda', aliases: ['新西兰', 'new zealand'] },
  { slug: 'india', zh: '印度', en: 'India', ar: 'الهند', es: 'India', aliases: ['印度', 'india'] },
  { slug: 'ireland', zh: '爱尔兰', en: 'Ireland', ar: 'أيرلندا', es: 'Irlanda', aliases: ['爱尔兰', 'ireland'] }
]

const matchedService = computed(() => {
  const art: any = article.value
  if (!art) return null
  const b = (art.business || '').toLowerCase()
  if (b.includes('trade') || b.includes('贸易')) {
    return {
      slug: 'trade',
      name: isEn.value ? 'International Trade Disputes' : (isAr.value ? 'النزاعات التجارية الدولية' : (isEs.value ? 'Disputas de Comercio Internacional' : '国际贸易争议')),
      desc: isEn.value ? 'Specialized dispute resolution for foreign trade contracts, invoices, and customs.' : (isAr.value ? 'حل النزاعات المتخصصة لعقود التجارة الخارجية والفواتير والجمارك.' : (isEs.value ? 'Resolución especializada de disputas en contratos de comercio exterior y aduanas.' : '涉外合同违约、货款拖欠、信用证及海关质量争议专业处置')),
    }
  }
  if (b.includes('recovery') || b.includes('追收') || b.includes('诉讼') || b.includes('债')) {
    return {
      slug: 'recovery',
      name: isEn.value ? 'Cross-Border Litigation & Debt Recovery' : (isAr.value ? 'التقاضي وتحصيل الديون عبر الحدود' : (isEs.value ? 'Litigios y Recobro Transfronterizo' : '诉讼与债务追收')),
      desc: isEn.value ? 'Commercial debt collection, asset tracing, and cross-border enforcement of judgments.' : (isAr.value ? 'تحصيل الديون التجارية وتتبع الأصول وتنفيذ الأحكام القضائية عبر الحدود.' : (isEs.value ? 'Cobro de créditos comerciales, rastreo de activos y ejecución de sentencias extranjeras.' : '海外客户欠款追收、境内外资产穿透调查与判决仲裁跨国执行')),
    }
  }
  if (b.includes('legacy') || b.includes('继承') || b.includes('家事') || b.includes('资产')) {
    return {
      slug: 'legacy',
      name: isEn.value ? 'Inheritance & Family Wealth Protection' : (isAr.value ? 'الميراث ونزاعات الأصول العائلية' : (isEs.value ? 'Herencias y Protección Patrimonial' : '继承与家族资产纠纷')),
      desc: isEn.value ? 'Multi-jurisdictional inheritance, property transmission, and wealth succession.' : (isAr.value ? 'التركات عبر الحدود ونقل الملكيات العقارية وتسوية النزاعات العائلية.' : (isEs.value ? 'Herencias multijurisdiccionales, transmisión de bienes y planificación sucesoria.' : '跨境多地房产、股权、存款继承，遗嘱执行与涉外遗产纠纷')),
    }
  }
  return {
    slug: 'trade',
    name: isEn.value ? 'Cross-Border Legal Practice' : (isAr.value ? 'الممارسات القانونية عبر الحدود' : (isEs.value ? 'Práctica Jurídica Transfronteriza' : '涉外法律实务总览')),
    desc: isEn.value ? 'Full-spectrum cross-border dispute resolution and legal counsel.' : (isAr.value ? 'خدمات شاملة لحل النزاعات القانونية الدولية.' : (isEs.value ? 'Servicios integrales de resolución de disputas transfronterizas.' : '涵盖贸易纠纷、债务追收与涉外资产全流程争议解决')),
  }
})

const matchedCountry = computed(() => {
  const art: any = article.value
  if (!art) return null
  const haystack = ((art.title_zh || '') + ' ' + (art.description_zh || '') + ' ' + (art.body_zh || '') + ' ' + (art.slug || '')).toLowerCase()
  for (const c of COUNTRY_SLUGS) {
    if (c.aliases.some(alias => haystack.includes(alias.toLowerCase()))) {
      return {
        slug: c.slug,
        name: isEn.value ? c.en : (isAr.value ? c.ar : (isEs.value ? c.es : c.zh)),
      }
    }
  }
  return null
})

// ---- Schema.org 4-Language Structured Data ----------------------------
const langCode = computed(() => isEn.value ? 'en' : (isAr.value ? 'ar' : (isEs.value ? 'es' : 'zh-CN')))

const articleJsonLd = computed(() => {
  const art: any = article.value
  if (!art) return null
  return {
    '@context': 'https://schema.org',
    '@type': 'Article',
    'headline': title.value,
    'description': description.value,
    'abstract': keyTakeaways.value.join('; '),
    'keywords': isAr.value 
      ? 'محامي دولي, نزاعات تجارية دولية, تحصيل ديون عابرة للحدود' 
      : (isEs.value 
        ? 'abogado internacional, litigio comercial transfronterizo, recobro de deudas' 
        : (isEn.value 
          ? 'international lawyer, cross-border disputes, international trade litigation, asset recovery' 
          : '国际律师, 涉外律师, 跨境争议解决, 海外欠款追收, 涉外商事诉讼')),
    'datePublished': art.published_at || art.created_at,
    'dateModified': art.updated_at || art.published_at,
    'inLanguage': langCode.value,
    'author': {
      '@type': 'Organization',
      'name': 'Shenyuan International Legal Team',
      'url': siteUrl,
    },
    'publisher': {
      '@type': 'Organization',
      'name': 'Shenyuan International Law Firm',
      'logo': {
        '@type': 'ImageObject',
        'url': `${siteUrl}/favicon.svg`,
      },
    },
    'mainEntityOfPage': {
      '@type': 'WebPage',
      '@id': canonical.value,
    },
  }
})

const faqJsonLd = computed(() => {
  if (!articleFaqs.value.length) return null
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    'inLanguage': langCode.value,
    'mainEntity': articleFaqs.value.map((f: any) => ({
      '@type': 'Question',
      'name': f.question,
      'acceptedAnswer': {
        '@type': 'Answer',
        'text': f.answer,
      },
    })),
  }
})

const breadcrumbJsonLd = computed(() => {
  if (!article.value) return null
  const homeName = isEn.value ? 'Home' : (isAr.value ? 'الرئيسية' : (isEs.value ? 'Inicio' : '首页'))
  const homeUrl = isEn.value ? `${siteUrl}/en` : (isAr.value ? `${siteUrl}/ar` : (isEs.value ? `${siteUrl}/es` : siteUrl))
  const articlesName = isEn.value ? 'Legal Insights' : (isAr.value ? 'المقالات القانونية' : (isEs.value ? 'Artículos Jurídicos' : '涉外法律专栏'))
  const articlesUrl = isEn.value ? `${siteUrl}/en/articles` : (isAr.value ? `${siteUrl}/ar/articles` : (isEs.value ? `${siteUrl}/es/articles` : `${siteUrl}/articles`))

  const items = [
    {
      '@type': 'ListItem',
      'position': 1,
      'name': homeName,
      'item': homeUrl,
    },
    {
      '@type': 'ListItem',
      'position': 2,
      'name': articlesName,
      'item': articlesUrl,
    },
  ]

  let pos = 3
  if (matchedService.value) {
    const sSlug = matchedService.value.slug
    const sUrl = isEn.value ? `${siteUrl}/en/services/${sSlug}` : (isAr.value ? `${siteUrl}/ar/services/${sSlug}` : (isEs.value ? `${siteUrl}/es/services/${sSlug}` : `${siteUrl}/services/${sSlug}`))
    items.push({
      '@type': 'ListItem',
      'position': pos++,
      'name': matchedService.value.name,
      'item': sUrl,
    })
  }

  items.push({
    '@type': 'ListItem',
    'position': pos,
    'name': title.value,
    'item': canonical.value,
  })

  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    'itemListElement': items,
  }
})

useHead({
  htmlAttrs: computed(() => ({
    lang: isAr.value ? 'ar' : (isEs.value ? 'es' : (isEn.value ? 'en' : 'zh-CN')),
    dir: isAr.value ? 'rtl' : 'ltr',
  })),
  link: alternateLinks,
  script: computed(() => {
    const scripts: any[] = []
    if (articleJsonLd.value) {
      scripts.push({ type: 'application/ld+json', innerHTML: JSON.stringify(articleJsonLd.value) })
    }
    if (breadcrumbJsonLd.value) {
      scripts.push({ type: 'application/ld+json', innerHTML: JSON.stringify(breadcrumbJsonLd.value) })
    }
    if (faqJsonLd.value) {
      scripts.push({ type: 'application/ld+json', innerHTML: JSON.stringify(faqJsonLd.value) })
    }
    return scripts
  }),
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

.geo-takeaways-card {
  background: #fbf9f4;
  border: 1px solid #e2d8c7;
  border-left: 4px solid var(--teal);
  border-radius: 8px;
  padding: 20px 24px;
  margin-bottom: 32px;
}

.takeaways-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.takeaways-icon {
  font-size: 16px;
  color: var(--orange);
}

.takeaways-header h4 {
  font-family: var(--serif);
  font-size: 16.5px;
  color: var(--teal-deep);
  margin: 0;
}

.geo-pill {
  margin-left: auto;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: var(--teal-deep);
  background: var(--teal-soft);
  border: 1px solid rgba(8, 77, 80, 0.2);
  padding: 2px 8px;
  border-radius: 999px;
  text-transform: uppercase;
}

.disclaimer-link {
  color: var(--teal-deep);
  text-decoration: underline;
  text-underline-offset: 3px;
  transition: color 0.15s ease;
}

.disclaimer-link:hover {
  color: var(--gold);
}

.takeaways-list {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 8px;
}

.takeaways-list li {
  position: relative;
  padding-left: 20px;
  font-size: 13.5px;
  line-height: 1.6;
  color: #3b4b59;
}

.takeaways-list li::before {
  content: "•";
  position: absolute;
  left: 6px;
  top: 0;
  color: var(--gold);
  font-size: 18px;
  line-height: 1.4;
}

.article-body {
  font-size: 16px;
  line-height: 1.85;
  color: #2c3e50;
  margin-bottom: 40px;
}

/* 语义化排版增强 */
.content-html {
  font-size: 16px;
  line-height: 1.8;
  color: #2c3e50;
}

:deep(.content-html h2) {
  font-family: var(--serif);
  font-size: 22px;
  color: var(--teal-deep);
  margin: 32px 0 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}

:deep(.content-html h3) {
  font-size: 18px;
  color: #1f2937;
  margin: 24px 0 12px;
}

:deep(.content-html p) {
  margin: 0 0 18px;
  text-align: left;
  letter-spacing: normal;
  word-spacing: normal;
  word-break: break-word;
}

:deep(.content-html a.article-link) {
  color: var(--teal);
  font-weight: 500;
  text-decoration: underline;
  text-underline-offset: 3px;
  transition: color 0.15s ease;
}
:deep(.content-html a.article-link:hover) {
  color: var(--gold);
}

/* 规范化法务表格（严格向左对齐，字间距自然） */
:deep(.article-table-wrap) {
  width: 100%;
  overflow-x: auto;
  margin: 24px 0 28px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: #ffffff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

:deep(.article-table) {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
  line-height: 1.6;
  text-align: left;
  letter-spacing: normal;
  word-spacing: normal;
}

:deep(.article-table th) {
  background: #f8fafc;
  color: var(--teal-deep);
  font-weight: 700;
  padding: 12px 16px;
  text-align: left;
  border-bottom: 2px solid #e2e8f0;
  border-right: 1px solid #f1f5f9;
  white-space: nowrap;
  letter-spacing: normal;
  word-spacing: normal;
}

:deep(.article-table th:last-child) {
  border-right: none;
}

:deep(.article-table td) {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #f1f5f9;
  border-right: 1px solid #f8fafc;
  color: #334155;
  vertical-align: top;
  letter-spacing: normal;
  word-spacing: normal;
}

:deep(.article-table td:last-child) {
  border-right: none;
}

:deep(.article-table tbody tr:nth-child(even)) {
  background: rgba(248, 250, 252, 0.6);
}

:deep(.article-table tbody tr:hover) {
  background: rgba(241, 245, 249, 0.8);
}

:deep(.article-table tbody tr:last-child td) {
  border-bottom: none;
}

:deep(.content-html strong) {
  color: #111827;
  font-weight: 600;
}

:deep(.content-html ul.article-list) {
  margin: 0 0 20px 20px;
  padding-left: 10px;
}

:deep(.content-html ul.article-list li) {
  margin-bottom: 8px;
}

:deep(.content-html blockquote) {
  margin: 20px 0;
  padding: 14px 20px;
  background: #f8fafc;
  border-left: 4px solid var(--teal);
  color: #475569;
  font-style: italic;
  border-radius: 0 4px 4px 0;
}

:deep(.content-html code) {
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 14px;
  color: #0f172a;
}

.article-faq-section {
  margin: 36px 0 28px;
  padding-top: 24px;
  border-top: 1px solid var(--line);
}

.faq-head-title {
  font-family: var(--serif);
  font-size: 19px;
  color: var(--teal-deep);
  margin: 0 0 16px;
}

.faq-accordion {
  display: grid;
  gap: 12px;
}

.art-faq-item {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 16px 20px;
}

.art-faq-item summary {
  font-size: 15px;
  font-weight: 700;
  color: var(--teal-deep);
  cursor: pointer;
  list-style: none;
}
.art-faq-item summary::-webkit-details-marker { display: none; }
.art-faq-item summary::after {
  content: "+";
  float: right;
  color: var(--gold);
  font-weight: 700;
}
.art-faq-item[open] summary::after { content: "−"; }

.art-faq-item p {
  margin: 12px 0 0;
  font-size: 14px;
  line-height: 1.7;
  color: #3b4b59;
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

.pillar-hubs-matrix {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
  margin: 28px 0 36px;
}

.pillar-hub-card {
  background: linear-gradient(135deg, #f8f6f0 0%, #f4efe4 100%);
  border: 1px solid var(--line);
  border-left: 4px solid var(--teal-deep);
  border-radius: 8px;
  padding: 18px 22px;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.pillar-hub-card.country-hub {
  border-left-color: var(--gold);
}

.pillar-hub-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.06);
  border-color: var(--teal);
}

.hub-label {
  display: inline-block;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--teal-deep);
  margin-bottom: 6px;
}

.pillar-hub-card.country-hub .hub-label {
  color: #8b6b23;
}

.hub-link {
  text-decoration: none;
  display: block;
}

.hub-link h4 {
  font-family: var(--serif);
  font-size: 16px;
  color: var(--teal-deep);
  margin: 0 0 6px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.hub-link p {
  font-size: 13px;
  line-height: 1.5;
  color: var(--muted);
  margin: 0;
}

/* RTL 适配 */
.article-detail-view.is-rtl .pillar-hub-card {
  border-left: 1px solid var(--line);
  border-right: 4px solid var(--teal-deep);
  text-align: right;
}

.article-detail-view.is-rtl .pillar-hub-card.country-hub {
  border-right-color: var(--gold);
}

.related-articles-section {
  margin: 40px 0 36px;
  padding-top: 32px;
  border-top: 1px solid var(--line);
}

.related-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.related-head h3 {
  font-family: var(--serif);
  font-size: 20px;
  color: var(--teal-deep);
  margin: 0;
}

.related-head .more-link {
  font-size: 13px;
  color: var(--teal);
  font-weight: 700;
}
.related-head .more-link:hover {
  color: var(--teal-deep);
}

.related-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.related-card {
  background: var(--paper-card);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 18px 16px;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.related-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.04);
}

.rel-badge {
  align-self: flex-start;
  font-size: 11px;
  font-weight: 700;
  color: var(--teal-deep);
  background: var(--teal-soft);
  padding: 2px 8px;
  border-radius: 4px;
  text-transform: uppercase;
  margin-bottom: 10px;
}

.rel-title {
  font-size: 14.5px;
  color: var(--ink);
  line-height: 1.4;
  margin: 0 0 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.rel-desc {
  font-size: 12.5px;
  color: var(--muted);
  line-height: 1.5;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

@media (max-width: 768px) {
  .related-grid {
    grid-template-columns: 1fr;
  }
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

/* 阿拉伯语（RTL）文字与排版适配 */
.is-rtl {
  direction: rtl;
  text-align: right;
}

.is-rtl .back-nav {
  display: inline-block;
  text-align: right;
}

.is-rtl :deep(.content-html p),
.is-rtl :deep(.content-html h2),
.is-rtl :deep(.content-html h3),
.is-rtl :deep(.content-html h4),
.is-rtl :deep(.content-html ul) {
  direction: rtl;
  text-align: right;
}

.is-rtl :deep(.article-table th),
.is-rtl :deep(.article-table td) {
  text-align: right;
  direction: rtl;
}

.is-rtl :deep(.content-html blockquote) {
  border-left: none;
  border-right: 4px solid var(--teal);
  border-radius: 4px 0 0 4px;
}

.is-rtl .geo-pill {
  margin-left: 0;
  margin-right: auto;
}
</style>
