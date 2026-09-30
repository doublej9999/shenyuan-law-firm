<template>
  <div class="recovery-estimator-card" :class="{ 'is-rtl': isAr }">
    <div class="estimator-header">
      <div class="estimator-badge">
        <span class="pulse-dot-gold"></span>
        <span>{{ ui.badge }}</span>
      </div>
      <h3 class="estimator-title">{{ ui.title }}</h3>
      <p class="estimator-subtitle">{{ ui.subtitle }}</p>
    </div>

    <form class="estimator-form" @submit.prevent="evaluate">
      <!-- 维度输入网格 -->
      <div class="estimator-grid">
        <!-- 欠款金额区间 -->
        <div class="est-col">
          <label>{{ ui.labelAmount }}</label>
          <select v-model="amountRange" class="est-select" required>
            <option value="micro">{{ ui.optAmountMicro }}</option>
            <option value="medium">{{ ui.optAmountMed }}</option>
            <option value="large">{{ ui.optAmountLarge }}</option>
            <option value="mega">{{ ui.optAmountMega }}</option>
          </select>
        </div>

        <!-- 债务人所在区域 -->
        <div class="est-col">
          <label>{{ ui.labelRegion }}</label>
          <select v-model="targetRegion" class="est-select" required>
            <option value="na">{{ ui.regNa }}</option>
            <option value="eu">{{ ui.regEu }}</option>
            <option value="me">{{ ui.regMe }}</option>
            <option value="sea">{{ ui.regSea }}</option>
            <option value="latam">{{ ui.regLatam }}</option>
            <option value="cis">{{ ui.regCis }}</option>
            <option value="afr">{{ ui.regAfr }}</option>
          </select>
        </div>

        <!-- 核心单证完备度 -->
        <div class="est-col">
          <label>{{ ui.labelDocs }}</label>
          <select v-model="docsLevel" class="est-select" required>
            <option value="complete">{{ ui.docsComplete }}</option>
            <option value="partial">{{ ui.docsPartial }}</option>
            <option value="weak">{{ ui.docsWeak }}</option>
          </select>
        </div>

        <!-- 对方当前经营与沟通状态 -->
        <div class="est-col">
          <label>{{ ui.labelDebtorStatus }}</label>
          <select v-model="debtorStatus" class="est-select" required>
            <option value="operating_deliberate">{{ ui.statOperating }}</option>
            <option value="dispute_quality">{{ ui.statQualityDispute }}</option>
            <option value="slow_pay">{{ ui.statSlowPay }}</option>
            <option value="ghosting">{{ ui.statGhosting }}</option>
            <option value="insolvency">{{ ui.statInsolvent }}</option>
          </select>
        </div>
      </div>

      <div class="estimator-actions">
        <button type="submit" class="est-btn">
          {{ ui.btnEvaluate }}
        </button>
      </div>
    </form>

    <!-- 评估报告面板 -->
    <div v-if="report" class="est-report" :class="`tier-${report.tier}`">
      <div class="report-top">
        <div class="score-box">
          <div class="score-circle">
            <span class="score-val">{{ report.probabilityScore }}%</span>
            <span class="score-sub">{{ ui.probLabel }}</span>
          </div>
          <div class="score-meta">
            <div class="tier-tag">{{ report.tierTitle }}</div>
            <div class="tier-lead">{{ report.tierDesc }}</div>
          </div>
        </div>

        <div class="cost-eta-card">
          <div class="cost-item">
            <span class="item-title">{{ ui.labelEstTimeline }}：</span>
            <span class="item-val highlight-time">{{ report.timeline }}</span>
          </div>
          <div class="cost-item">
            <span class="item-title">{{ ui.labelRecommendedAction }}：</span>
            <span class="item-val font-semibold">{{ report.actionRoute }}</span>
          </div>
        </div>
      </div>

      <div class="report-details">
        <div class="dim-block">
          <h4 class="dim-title">📌 {{ ui.titleFeasibility }}</h4>
          <p class="dim-text">{{ report.feasibilityAnalysis }}</p>
        </div>
        <div class="dim-block">
          <h4 class="dim-title">⚖️ {{ ui.titleLegalTool }}</h4>
          <p class="dim-text">{{ report.legalMechanisms }}</p>
        </div>
      </div>

      <div class="report-cta-box">
        <div class="cta-message">
          <strong>{{ ui.ctaStrong }}</strong>
          <span>{{ ui.ctaNotice }}</span>
        </div>
        <a href="#intake" class="cta-action-btn" @click.prevent="scrollToIntake">
          {{ ui.btnIntakeDispatch }} →
        </a>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useCurrentLang } from '@/composables/useCurrentLang'

const { currentLang, isAr } = useCurrentLang()

const amountRange = ref('medium')
const targetRegion = ref('na')
const docsLevel = ref('complete')
const debtorStatus = ref('operating_deliberate')
const report = ref<any>(null)

const UI_DICT: Record<string, any> = {
  zh: {
    badge: 'AI 涉外商事清收评估',
    title: '海外欠款追回概率与维权综合成本评估',
    subtitle: '综合买方法域征信与司法环境、单据完备性（合同/提单/报关）、违约形态测算实际回款胜率与策略通道。',
    labelAmount: '涉案争议标的金额',
    optAmountMicro: '5万美元以下 (小额商事拖欠)',
    optAmountMed: '5万 ~ 20万美元 (中等标的清收)',
    optAmountLarge: '20万 ~ 100万美元 (重大货款纠纷)',
    optAmountMega: '100万美元以上 (特重大跨国债务/批量索赔)',
    labelRegion: '债务人/买家所在法域',
    regNa: '北美地区 (美国 / 加拿大)',
    regEu: '欧盟 / 英国 (德国/法国/英国等)',
    regMe: '中东地区 (阿联酋/沙特/卡塔尔)',
    regSea: '东南亚 (新加坡/越南/印尼/马来西亚)',
    regLatam: '拉美地区 (墨西哥/巴西/智利)',
    regCis: '独联体 / 俄罗斯 / 中亚',
    regAfr: '非洲地区 (南非/尼日利亚/埃及/肯尼亚)',
    labelDocs: '履约证据链完备度',
    docsComplete: '全链闭环 (正本签字合同 + 提单B/L + 报关单 + 催款对账记录)',
    docsPartial: '常规留存 (仅有形式发票PI + 提单复印件 + 微信/邮件沟通记述)',
    docsWeak: '证据存在瑕疵 (无盖章书面合同/电放无凭/主体名称不完全一致)',
    labelDebtorStatus: '对方当前经营与沟通状态',
    statOperating: '正常存续经营 · 无故拖延或恶意拒绝付款',
    statQualityDispute: '借故产品质量 / 规格或外包装瑕疵主张巨额扣款',
    statSlowPay: '资金周转困难 · 承诺分期但未实质履约',
    statGhosting: '完全失联 · 邮件拒收 / 电话停机 / 疑似倒闭跑路',
    statInsolvent: '已被申请重整破产 / 进入法定清算程序',
    btnEvaluate: '测算追回概率与维权方案',
    probLabel: '综合预估胜率/回款率',
    labelEstTimeline: '预计全案周期',
    labelRecommendedAction: '优先推荐应对路径',
    titleFeasibility: '法律可行性与成本效益诊断',
    titleLegalTool: '涉外法律清收工具矩阵',
    ctaStrong: '线索已被初审。',
    ctaNotice: '可进一步预约涉外清收专案组，获取定制化涉外律师函与海外财产保全规划。',
    btnIntakeDispatch: '对接涉外清收专案律师'
  },
  en: {
    badge: 'AI Cross-Border Debt Recovery Engine',
    title: 'Cross-Border Commercial Debt Recovery & Feasibility Estimator',
    subtitle: 'Assess recovery odds, litigation costs, and legal pathways based on debtor jurisdiction, evidence completeness, and breach behavior.',
    labelAmount: 'Claim Amount',
    optAmountMicro: 'Under $50,000 USD (Minor commercial debt)',
    optAmountMed: '$50,000 - $200,000 USD (Mid-size claim)',
    optAmountLarge: '$200,000 - $1,000,000 USD (Major trade dispute)',
    optAmountMega: 'Over $1,000,000 USD (Complex corporate debt)',
    labelRegion: 'Debtor / Buyer Jurisdiction',
    regNa: 'North America (US / Canada)',
    regEu: 'European Union / UK (Germany/France/UK)',
    regMe: 'Middle East (UAE / Saudi Arabia / Qatar)',
    regSea: 'Southeast Asia (Singapore/Vietnam/Indonesia)',
    regLatam: 'Latin America (Mexico / Brazil / Chile)',
    regCis: 'CIS / Central Asia',
    regAfr: 'Africa (South Africa/Nigeria/Egypt)',
    labelDocs: 'Evidence Chain Completeness',
    docsComplete: 'Solid (Signed Sales Contract + B/L + Customs Slip + Acknowledgment)',
    docsPartial: 'Moderate (Proforma Invoice + B/L Copy + Email trail)',
    docsWeak: 'Imperfect (No formal contract / Discrepant buyer legal names)',
    labelDebtorStatus: 'Debtor Operational & Response Status',
    statOperating: 'Active Business · Unjustified refusal to pay',
    statQualityDispute: 'Alleging quality discrepancy to justify unilateral deduction',
    statSlowPay: 'Liquidity issues · Promises installment but fails to remit',
    statGhosting: 'Completely uncontactable / Ghosting / Shutting down',
    statInsolvent: 'Formally filed for bankruptcy / Judicial receivership',
    btnEvaluate: 'Analyze Recovery Probability',
    probLabel: 'Estimated Recovery Probability',
    labelEstTimeline: 'Estimated Case Timeline',
    labelRecommendedAction: 'Recommended Legal Pathway',
    titleFeasibility: 'Legal Feasibility & Cost-Benefit Analysis',
    titleLegalTool: 'Jurisdictional Enforcement Mechanisms',
    ctaStrong: 'Preliminary profile completed.',
    ctaNotice: 'Engage our cross-border litigation team for worldwide asset freezes and demand dispatch.',
    btnIntakeDispatch: 'Engage Cross-Border Counsel'
  },
  ar: {
    badge: 'محرك تقييم تحصيل الديون العابرة للحدود بالذكاء الاصطناعي',
    title: 'حاسبة احتمالية تحصيل الديون التجارية الدولية وتقدير تكاليف التقاضي',
    subtitle: 'تقييم دقيق لفرص استرداد الأموال وتكاليف الملاحقة وفقاً للاختصاص القضائي للمدين، واكتمال المستندات، والوضع المالي.',
    labelAmount: 'قيمة النزاع المالي',
    optAmountMicro: 'أقل من 50 ألف دولار (ديون تجارية محدودة)',
    optAmountMed: '50 ألف - 200 ألف دولار (مبالغ تجارية متوسطة)',
    optAmountLarge: '200 ألف - 1 مليون دولار (نزاع شحن وتجارة كبير)',
    optAmountMega: 'أكثر من 1 مليون دولار (نزاعات كبرى وتحصيل مؤسسي)',
    labelRegion: 'دولة المشتري / المدين',
    regNa: 'أمريكا الشمالية (الولايات المتحدة / كندا)',
    regEu: 'الاتحاد الأوروبي والمملكة المتحدة',
    regMe: 'الشرق الأوسط (الإمارات / السعودية / قطر)',
    regSea: 'جنوب شرق آسيا (سنغافورة / ماليزيا / فيتنام)',
    regLatam: 'أمريكا اللاتينية (المكسيك / البرازيل / تشيلي)',
    regCis: 'رابطة الدول المستقلة وآسيا الوسطى',
    regAfr: 'أفريقيا (جنوب أفريقيا / مصر / نيجيريا)',
    labelDocs: 'سلامة واكتمال سلسلة الأدلة',
    docsComplete: 'سلسلة متكاملة (عقد رسمي موقع + بوليصة B/L + بيانات جمركية + إقرار)',
    docsPartial: 'متوسطة (فاتورة شكلية PI + نسخ بوالص + مراسلات إلكترونية)',
    docsWeak: 'ناقصة (غياب العقد الرسمي / تباين في أسماء الكيانات التجارية)',
    labelDebtorStatus: 'حالة المدين التشغيلية والتواصل',
    statOperating: 'نشاط تجاري قائم · مماطلة أو امتناع غير مبرر عن السداد',
    statQualityDispute: 'الادعاء بوجود عيوب في البضاعة لفرض خصم تعسفي',
    statSlowPay: 'صعوبات سيولة مالية · وعود بالتقسيط دون تحويل فعلي',
    statGhosting: 'انقطاع تام عن التواصل / إغلاق المقرات وتجنب الرد',
    statInsolvent: 'إعلان الإفلاس رسمياً أو الخضوع للتصفية القضائية',
    btnEvaluate: 'تقييم احتمالية التحصيل والخطة القانونية',
    probLabel: 'نسبة النجاح والاسترداد المتوقعة',
    labelEstTimeline: 'الجدول الزمني التقديري',
    labelRecommendedAction: 'المسار القانوني الموصى به',
    titleFeasibility: 'الجدوى القانونية وتحليل العائد مقابل التكلفة',
    titleLegalTool: 'آليات التنفيذ والحجز المتاحة',
    ctaStrong: 'تم فحص أبعاد النزاع.',
    ctaNotice: 'احجز استشارة فورية مع فريق شينيوان لتوجيه إنذار رسمي وتجميد أصول المدين دولياً.',
    btnIntakeDispatch: 'تواصل مع محامي التحصيل الدولي'
  },
  es: {
    badge: 'Motor IA de Recuperación de Deudas Transfronterizas',
    title: 'Estimador de Probabilidad de Cobro Internacional y Viabilidad Legal',
    subtitle: 'Calcule la tasa de éxito de recuperación y costos de litigio según jurisdicción del deudor, solidez documental y conducta.',
    labelAmount: 'Cuantía del Litigio Comercial',
    optAmountMicro: 'Menos de 50.000 USD (Deuda comercial menor)',
    optAmountMed: '50.000 - 200.000 USD (Reclamación media)',
    optAmountLarge: '200.000 - 1.000.000 USD (Litigio de gran envergadura)',
    optAmountMega: 'Más de 1.000.000 USD (Macrodeuda corporativa internacional)',
    labelRegion: 'Jurisdicción del Deudor / Comprador',
    regNa: 'Norteamérica (Estados Unidos / Canadá)',
    regEu: 'Unión Europea / Reino Unido (Alemania/Francia/UK)',
    regMe: 'Oriente Medio (EAU / Arabia Saudita / Qatar)',
    regSea: 'Sudeste Asiático (Singapur/Vietnam/Indonesia)',
    regLatam: 'Latinoamérica (México / Brasil / Chile)',
    regCis: 'CEI / Asia Central',
    regAfr: 'África (Sudáfrica/Egipto/Nigeria)',
    labelDocs: 'Solidez de la Cadena Documental',
    docsComplete: 'Cadena Robusta (Contrato firmado + B/L + Despacho Aduanero + Convalidación)',
    docsPartial: 'Moderada (Factura Proforma + Copia B/L + Correos electrónicos)',
    docsWeak: 'Deficiente (Sin contrato formal / Discrepancias en razón social)',
    labelDebtorStatus: 'Estado Operativo y Disposición del Deudor',
    statOperating: 'En funcionamiento activo · Negativa deliberada a transferir',
    statQualityDispute: 'Alega disconformidad de calidad para aplicar deducción arbitraria',
    statSlowPay: 'Problemas de liquidez · Promesas de pago aplazado incumplidas',
    statGhosting: 'Incomunicado totalmente / Desaparición / Sospecha de quiebra',
    statInsolvent: 'Procedimiento concursal formal / Concurso de acreedores',
    btnEvaluate: 'Calcular Viabilidad y Vía de Cobro',
    probLabel: 'Probabilidad Estimada de Cobro',
    labelEstTimeline: 'Plazo Estimado de Recuperación',
    labelRecommendedAction: 'Ruta Estratégica Sugerida',
    titleFeasibility: 'Diagnóstico de Viabilidad y Coste-Beneficio',
    titleLegalTool: 'Mecanismos de Ejecución y Medidas Cautelares',
    ctaStrong: 'Análisis preliminar generado.',
    ctaNotice: 'Programe una consulta para despachar un requerimiento notarial formal y solicitar embargo preventivo.',
    btnIntakeDispatch: 'Contactar Abogado Especialista'
  }
}

const ui = computed(() => UI_DICT[currentLang.value] || UI_DICT.zh)

function evaluate() {
  // 基础概率分测算 (0 - 100)
  let score = 50

  // 1. 证据维度 (+30 ~ -20)
  if (docsLevel.value === 'complete') score += 25
  else if (docsLevel.value === 'partial') score += 5
  else if (docsLevel.value === 'weak') score -= 20

  // 2. 债务人经营现状 (+15 ~ -40)
  if (debtorStatus.value === 'operating_deliberate') score += 15
  else if (debtorStatus.value === 'dispute_quality') score += 5
  else if (debtorStatus.value === 'slow_pay') score += 0
  else if (debtorStatus.value === 'ghosting') score -= 25
  else if (debtorStatus.value === 'insolvency') score -= 35

  // 3. 标的额修正（标的过小跨国诉讼成本不经济，超大标的具备保全价值）
  if (amountRange.value === 'micro') score -= 10
  else if (amountRange.value === 'large' || amountRange.value === 'mega') score += 5

  // 4. 法域司法执行效率调整
  if (['eu', 'na', 'sea'].includes(targetRegion.value)) score += 5
  else if (['latam', 'afr'].includes(targetRegion.value)) score -= 5

  // 限制边界
  if (score > 92) score = 92
  if (score < 15) score = 15

  let tier = 'high'
  let tierTitle = currentLang.value === 'zh' ? '优选通道 · 高追偿概率' : (currentLang.value === 'ar' ? 'مسار ممتاز: احتمالية استرداد مرتفعة' : 'Alta Viabilidad de Cobro')
  let tierDesc = currentLang.value === 'zh' ? '债务人具备实际偿付资质且法律凭证清晰，适宜通过“涉外律师函 + 财产线索查控 + 仲裁/诉讼”形成高压威慑。' : 'Debtor possesses active solvency and documentary proof is robust.'

  let timeline = currentLang.value === 'zh' ? '1 ~ 3 个月 (非诉催告 / 破产重组前置和解)' : '1 - 3 Months (Pre-litigation / Demand)'
  let actionRoute = currentLang.value === 'zh' ? '涉外正式律师催款函 + 当地商业征信查控' : 'Formal Demand Letter + Local Asset Investigation'

  if (score < 40) {
    tier = 'low'
    tierTitle = currentLang.value === 'zh' ? '高阻碍预警 · 低直接回款率' : (currentLang.value === 'ar' ? 'تنبيه: عوائق قانونية وتجارية جسيمة' : 'Baja Probabilidad / Alerta Crítica')
    tierDesc = currentLang.value === 'zh' ? '债务人可能已进入破产前夜或证据存在严重脱节。直接诉讼成本可能倒挂，需优先进行法人穿透或向债权人委员会申报。' : 'High insolvency risk or severe evidentiary defect detected.'
    timeline = currentLang.value === 'zh' ? '6 ~ 18 个月以上 (视海外破产清算进程)' : '6 - 18+ Months'
    actionRoute = currentLang.value === 'zh' ? '跨境破产债权申报 / 穿透股东责任' : 'Bankruptcy Proof of Claim / Piercing Corporate Veil'
  } else if (score < 70) {
    tier = 'medium'
    tierTitle = currentLang.value === 'zh' ? '中等难度 · 需强化法律博弈' : (currentLang.value === 'ar' ? 'صعوبة متوسطة: تتطلب تفاوضاً قانونياً حازماً' : 'Viabilidad Media / Requiere Presión')
    tierDesc = currentLang.value === 'zh' ? '存在以“质量瑕疵”或“履约抗辩”为由的恶意抗辩，建议迅速锁定货损证据链并切断其海外抗辩借口。' : 'Debtor employs quality disputes or delayed payment tactics.'
    timeline = currentLang.value === 'zh' ? '3 ~ 6 个月 (涉外调解 / 简易判决/仲裁)' : '3 - 6 Months'
    actionRoute = currentLang.value === 'zh' ? '锁定反驳抗辩证据 + 申请境外紧急诉前保全' : 'Pre-action Injunction / Freeze + Evidence Clarification'
  }

  // 可行性诊断分析
  let feasibilityAnalysis = ''
  if (amountRange.value === 'micro') {
    feasibilityAnalysis = currentLang.value === 'zh' ? '标的在 5 万美元以下时，直接在海外聘请出庭律师发起跨国全流程诉讼成本畸高（境外小时费率常在 400~800 美元）。建议优先采取【非诉催告、黑名单通报、商会函件施压】低成本杠杆方案。' : 'For claims under $50K USD, direct cross-border trial entails disproportionate legal hourly rates. Non-litigation settlement and institutional pressure are highly recommended.'
  } else {
    feasibilityAnalysis = currentLang.value === 'zh' ? '标的充足，完全覆盖跨境诉讼与法域保全的边际成本。只要债务人主体名下存在银行授信、保税仓库存或不动产，司法介入具备显著的投入产出正向预期。' : 'Sufficient claim size comfortably offsets cross-border enforcement costs. Asset arrest or freezing orders yield positive ROI.'
  }

  // 法律机制匹配
  let legalMechanisms = ''
  if (targetRegion.value === 'na') {
    legalMechanisms = currentLang.value === 'zh' ? '美国/加拿大商事法：利用 UCC § 2-709 支付全部货款之诉；若买方恶意转移资产，可向联邦/州法院申请诉前暂扣令（Preliminary Injunction）与信用局违约登记。' : 'US UCC § 2-709 Action for the Price; pre-judgment attachment and credit agency reporting.'
  } else if (targetRegion.value === 'me') {
    legalMechanisms = currentLang.value === 'zh' ? '中东法域：依托迪拜国际金融中心（DIFC）简易程序或沙特商业法院执行法；若签发支票跳票，在阿联酋可直接触发强力商事民事连带制裁。' : 'DIFC Courts summary proceedings and UAE commercial travel ban / asset freeze applications.'
  } else if (targetRegion.value === 'eu') {
    legalMechanisms = currentLang.value === 'zh' ? '欧盟/英国法域：运用欧洲支付令（European Payment Order, EPO）或英格兰高等法院债务简易判决（Summary Judgment）；无实质抗辩时可极速冻结其清算账户。' : 'European Payment Order (EPO) or UK High Court Summary Judgment.'
  } else {
    legalMechanisms = currentLang.value === 'zh' ? '公约与多边机制：适用《联合国国际货物销售合同公约》(CISG) 根本违约条款；取得中国或国际仲裁裁决后，依据《纽约公约》在债务人所在地法院全额强制执行。' : 'UN CISG fundamental breach provisions + New York Convention 1958 worldwide enforcement.'
  }

  report.value = {
    probabilityScore: score,
    tier,
    tierTitle,
    tierDesc,
    timeline,
    actionRoute,
    feasibilityAnalysis,
    legalMechanisms
  }
}

function scrollToIntake() {
  const el = document.getElementById('intake')
  if (el) {
    el.scrollIntoView({ behavior: 'smooth' })
  }
}
</script>

<style scoped>
.recovery-estimator-card {
  background: linear-gradient(145deg, #ffffff, #faf9f6);
  border: 1px solid var(--line, #e2d8c7);
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.04);
  padding: 36px 40px;
  margin: 36px 0;
  transition: border-color 0.2s ease;
}

.recovery-estimator-card:hover {
  border-color: var(--gold, #d97706);
}

.estimator-header {
  margin-bottom: 26px;
}

.estimator-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #fef3c7;
  color: #92400e;
  font-size: 12px;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 999px;
  margin-bottom: 12px;
}

.pulse-dot-gold {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #d97706;
  box-shadow: 0 0 0 2px rgba(217, 119, 6, 0.25);
}

.estimator-title {
  font-family: var(--serif, 'Playfair Display', serif);
  font-size: 24px;
  color: var(--teal-deep, #084d50);
  margin: 0 0 8px;
}

.estimator-subtitle {
  color: var(--muted, #64748b);
  font-size: 14.5px;
  line-height: 1.6;
  margin: 0;
}

.estimator-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.estimator-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 18px;
  width: 100%;
}

.est-col {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
  max-width: 100%;
  width: 100%;
}

.est-col label {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--ink, #1e293b);
}

.est-select {
  box-sizing: border-box;
  display: block;
  width: 100%;
  max-width: 100%;
  min-width: 0;
  padding: 12px 14px;
  border: 1px solid var(--line, #cbd5e1);
  border-radius: 6px;
  background: #ffffff;
  color: #1e293b;
  font-size: 14px;
  line-height: 1.4;
  height: 46px;
  -webkit-appearance: none;
  appearance: none;
  background-image: url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%2364748B%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E");
  background-repeat: no-repeat;
  background-position: right 14px center;
  background-size: 10px;
  padding-right: 34px;
  transition: all 0.2s ease;
}

.is-rtl .est-select {
  background-position: left 14px center;
  padding-right: 14px;
  padding-left: 34px;
}

.est-select:focus {
  outline: none;
  border-color: var(--gold, #d97706);
  box-shadow: 0 0 0 3px rgba(217, 119, 6, 0.1);
}

.estimator-actions {
  display: flex;
  justify-content: flex-end;
}

.est-btn {
  background: var(--gold, #d97706);
  color: #ffffff;
  border: none;
  padding: 12px 28px;
  font-size: 15px;
  font-weight: 700;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s ease, transform 0.1s ease;
}

.est-btn:hover {
  background: #b45309;
  transform: translateY(-1px);
}

/* 评估报告 */
.est-report {
  margin-top: 30px;
  padding: 26px 28px;
  border-radius: 8px;
  border-left: 5px solid #10b981;
  background: #f8fafc;
  animation: fadeIn 0.3s ease-out;
}

.est-report.tier-low {
  border-left-color: #ef4444;
  background: #fef2f2;
}

.est-report.tier-medium {
  border-left-color: #f59e0b;
  background: #fffbeb;
}

.report-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 22px;
  padding-bottom: 18px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.score-box {
  display: flex;
  align-items: center;
  gap: 18px;
}

.score-circle {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 90px;
  height: 90px;
  border-radius: 50%;
  background: #ffffff;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.06);
  border: 3px solid #10b981;
}

.tier-low .score-circle {
  border-color: #ef4444;
}

.tier-medium .score-circle {
  border-color: #f59e0b;
}

.score-val {
  font-size: 24px;
  font-weight: 800;
  color: var(--teal-deep, #084d50);
}

.tier-low .score-val {
  color: #dc2626;
}

.tier-medium .score-val {
  color: #d97706;
}

.score-sub {
  font-size: 10px;
  color: var(--muted, #64748b);
  text-align: center;
}

.score-meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-width: 380px;
}

.tier-tag {
  font-size: 18px;
  font-weight: 700;
  color: var(--ink, #1e293b);
}

.tier-lead {
  font-size: 13.5px;
  line-height: 1.5;
  color: #475569;
}

.cost-eta-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: rgba(255, 255, 255, 0.85);
  padding: 14px 18px;
  border-radius: 6px;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.cost-item {
  font-size: 13.5px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.item-title {
  color: #64748b;
  font-weight: 600;
}

.highlight-time {
  color: var(--teal-deep, #084d50);
  font-weight: 700;
}

.report-details {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 22px;
}

.dim-block {
  background: #ffffff;
  padding: 16px 20px;
  border-radius: 6px;
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.dim-title {
  margin: 0 0 6px;
  font-size: 14.5px;
  font-weight: 700;
  color: var(--ink, #1e293b);
}

.dim-text {
  margin: 0;
  font-size: 13.5px;
  line-height: 1.6;
  color: #475569;
}

.report-cta-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--teal-soft, #e6f4f2);
  padding: 16px 20px;
  border-radius: 6px;
  border: 1px solid rgba(15, 118, 110, 0.15);
}

.cta-message {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 13.5px;
  color: var(--teal-deep, #084d50);
}

.cta-action-btn {
  background: var(--teal-deep, #084d50);
  color: #ffffff;
  padding: 10px 20px;
  border-radius: 4px;
  font-size: 13.5px;
  font-weight: 700;
  text-decoration: none;
  transition: background 0.2s ease;
  white-space: nowrap;
}

.cta-action-btn:hover {
  background: var(--teal, #0f766e);
}

/* RTL 支持 */
.is-rtl {
  direction: rtl;
  text-align: right;
}

.is-rtl .est-report {
  border-left: none;
  border-right: 5px solid #10b981;
}

.is-rtl .est-report.tier-low {
  border-right-color: #ef4444;
}

.is-rtl .est-report.tier-medium {
  border-right-color: #f59e0b;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 768px) {
  .recovery-estimator-card {
    padding: 24px 20px;
  }
  .estimator-grid {
    grid-template-columns: 1fr;
    gap: 14px;
  }
  .report-top,
  .report-cta-box {
    flex-direction: column;
    align-items: flex-start;
    gap: 14px;
  }
  .score-box {
    width: 100%;
  }
  .cost-eta-card {
    width: 100%;
  }
  .est-btn,
  .cta-action-btn {
    width: 100%;
    text-align: center;
  }
}
</style>
