<template>
  <div class="calculator-card" :class="{ 'is-rtl': isAr }">
    <div class="calc-header">
      <div class="calc-badge">
        <span class="pulse-dot"></span>
        <span>{{ ui.badge }}</span>
      </div>
      <h3 class="calc-title">{{ ui.title }}</h3>
      <p class="calc-subtitle">{{ ui.subtitle }}</p>
    </div>

    <form class="calc-form" @submit.prevent="calculate">
      <div class="form-row">
        <!-- 业务领域 -->
        <div class="field-col">
          <label>{{ ui.labelType }}</label>
          <select v-model="selectedType" class="calc-select" required>
            <option value="trade">{{ ui.optTrade }}</option>
            <option value="cargo">{{ ui.optCargo }}</option>
            <option value="debt">{{ ui.optDebt }}</option>
            <option value="legacy">{{ ui.optLegacy }}</option>
          </select>
        </div>

        <!-- 管辖法域 -->
        <div class="field-col">
          <label>{{ ui.labelJurisdiction }}</label>
          <select v-model="selectedJurisdiction" class="calc-select" required>
            <option value="cn">{{ ui.jurCn }}</option>
            <option value="us">{{ ui.jurUs }}</option>
            <option value="ae">{{ ui.jurAe }}</option>
            <option value="de">{{ ui.jurDe }}</option>
            <option value="sg">{{ ui.jurSg }}</option>
            <option value="mx">{{ ui.jurMx }}</option>
            <option value="cisg">{{ ui.jurCisg }}</option>
          </select>
        </div>

        <!-- 发生/起算时间 -->
        <div class="field-col">
          <label>{{ ui.labelStartDate }}</label>
          <input 
            v-model="startDate" 
            type="date" 
            class="calc-input" 
            :max="todayStr"
            required 
          />
        </div>
      </div>

      <div class="calc-actions">
        <button type="submit" class="calc-btn">
          {{ ui.btnCalculate }}
        </button>
      </div>
    </form>

    <!-- 测算结果面板 -->
    <div v-if="result" class="calc-result" :class="`status-${result.level}`">
      <div class="result-header">
        <div class="status-indicator">
          <span class="status-icon">{{ result.icon }}</span>
          <span class="status-text">{{ result.statusText }}</span>
        </div>
        <div class="days-remaining">
          <span class="days-number">{{ result.remainingDays }}</span>
          <span class="days-unit">{{ ui.unitDays }}</span>
        </div>
      </div>

      <div class="result-body">
        <div class="detail-row">
          <span class="detail-label">{{ ui.labelRule }}：</span>
          <span class="detail-val"><strong>{{ result.ruleName }}</strong> ({{ result.standardYears }} {{ ui.unitYears }})</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">{{ ui.labelDeadline }}：</span>
          <span class="detail-val text-deadline">{{ result.deadlineStr }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">{{ ui.labelKeyAct }}：</span>
          <span class="detail-val">{{ result.advice }}</span>
        </div>
      </div>

      <div class="result-cta">
        <div class="cta-tip">{{ ui.ctaTip }}</div>
        <a href="#intake" class="cta-button" @click.prevent="applyIntake">
          {{ ui.btnIntake }} →
        </a>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useCurrentLang } from '@/composables/useCurrentLang'

const { currentLang, isAr } = useCurrentLang()

const today = new Date()
const todayStr = today.toISOString().split('T')[0]

// 默认三个月前
const defaultStart = new Date(today.getTime() - 90 * 24 * 3600 * 1000).toISOString().split('T')[0]

const selectedType = ref('trade')
const selectedJurisdiction = ref('cn')
const startDate = ref(defaultStart)
const result = ref<any>(null)

// 多语言 UI 字典
const UI_DICT: Record<string, any> = {
  zh: {
    badge: 'AI 涉外法律引擎',
    title: '跨国商事纠纷 · 诉讼时效红线与灭失预警测算',
    subtitle: '输入争议类型、管辖法域与违约时间，自动匹配各国成文法与公约（CISG/海运公约），测算权利失效倒计时。',
    labelType: '争议与案由类型',
    optTrade: '国际货物买卖合同争议 (贸易违约)',
    optCargo: '国际海运货损 / 提单放货纠纷',
    optDebt: '跨国货款拖欠 / 商事债务追偿',
    optLegacy: '涉外遗产继承与跨境财产确权',
    labelJurisdiction: '约定管辖法域 / 法律适用',
    jurCn: '中国内地法律 (民法典 / 涉外民事关系适用法)',
    jurUs: '美国法律 (UCC 商法典 / 纽约州/加州)',
    jurAe: '阿联酋法律 (DIFC 法院 / 联邦商法典)',
    jurDe: '德国法律 (BGB 德国民法典 § 195)',
    jurSg: '新加坡法律 (新加坡时效法令 Limitation Act)',
    jurMx: '墨西哥法律 (墨西哥联邦商法典 Código de Comercio)',
    jurCisg: '联合国国际货物销售合同公约 (CISG)',
    labelStartDate: '知道或应当知道违约/交付之日',
    btnCalculate: '立即测算时效倒计时',
    unitDays: '天',
    unitYears: '年',
    labelRule: '适用法律依据',
    labelDeadline: '法定最后截止日',
    labelKeyAct: '核心实务建议',
    ctaTip: '时效即将届满或争议复杂？深远国际律师团队可紧急出具正式律师函中断时效。',
    btnIntake: '预约涉外律师紧急中断时效'
  },
  en: {
    badge: 'AI Cross-Border Legal Engine',
    title: 'Statute of Limitations & Expiration Countdown Calculator',
    subtitle: 'Calculate statutory deadlines and prescription time bars across US, China, UAE, Germany, and CISG treaties.',
    labelType: 'Dispute / Claim Type',
    optTrade: 'International Sale of Goods Breach',
    optCargo: 'Maritime Cargo Damage / Bill of Lading Claim',
    optDebt: 'Cross-Border Commercial Debt Collection',
    optLegacy: 'Cross-Border Estate & Inheritance Rights',
    labelJurisdiction: 'Governing Jurisdiction / Applicable Law',
    jurCn: 'PRC Law (Civil Code Art. 188 / 594)',
    jurUs: 'US Law (UCC § 2-725 / State Limitations)',
    jurAe: 'UAE Law (DIFC Courts / Federal Commercial Code)',
    jurDe: 'German Law (BGB § 195 Regular Limitation)',
    jurSg: 'Singapore Law (Limitation Act Cap. 163)',
    jurMx: 'Mexican Law (Federal Commercial Code Art. 1043)',
    jurCisg: 'UN CISG Convention (Art. 39 Notice Period)',
    labelStartDate: 'Date Breach / Delivery Occurred',
    btnCalculate: 'Calculate Expiration Bar',
    unitDays: 'Days Remaining',
    unitYears: 'Years',
    labelRule: 'Statutory Authority',
    labelDeadline: 'Statutory Final Deadline',
    labelKeyAct: 'Immediate Legal Action',
    ctaTip: 'Approaching the deadline? Shenyuan International Law Firm can dispatch formal demand letters to toll prescription.',
    btnIntake: 'Consult International Lawyers Now'
  },
  ar: {
    badge: 'محرك الذكاء الاصطناعي القانوني الدولي',
    title: 'حاسبة مدد التقادم والمهل القانونية للنزاعات التجارية العابرة للحدود',
    subtitle: 'احسب بدقة مهلة سقوط الحق القانوني وفقاً لقوانين الصين، الإمارات (DIFC)، وألمانيا، واتفاقية البيع الدولي (CISG).',
    labelType: 'نوع النزاع التجاري',
    optTrade: 'نزاعات عقود بيع البضائع الدولية',
    optCargo: 'أضرار الشحن البحري ونزاعات بوالص الشحن',
    optDebt: 'تحصيل الديون والمستحقات العابرة للحدود',
    optLegacy: 'قضايا الميراث العائلي وحصر التركات الأجنبية',
    labelJurisdiction: 'الاختصاص القضائي / القانون الواجب التطبيق',
    jurCn: 'القانون الصيني (القانون المدني المواد 188 / 594)',
    jurUs: 'القانون الأمريكي (قانون التجارة الموحد UCC § 2-725)',
    jurAe: 'قانون الإمارات (محاكم مركز دبي المالي DIFC / المعاملات التجارية)',
    jurDe: 'القانون الألماني (القانون المدني BGB § 195)',
    jurSg: 'قانون سنغافورة (قانون التقادم Limitation Act)',
    jurMx: 'القانون المكسيكي (القانون التجاري الفيدرالي)',
    jurCisg: 'اتفاقية الأمم المتحدة لعقود البيع الدولي (CISG)',
    labelStartDate: 'تاريخ وقوع الإخلال أو الاستلام',
    btnCalculate: 'احسب مهلة التقادم القانوني',
    unitDays: 'يوم متبقٍ',
    unitYears: 'سنوات',
    labelRule: 'المرجع القانوني الواجب التطبيق',
    labelDeadline: 'الموعد النهائي لسقوط الحق بالتقادم',
    labelKeyAct: 'الإجراء القانوني الفوري',
    ctaTip: 'هل اقتربت المهلة من الانتهاء؟ يستطيع فريق شينيوان الدولي توجيه إنذار رسمي عاجل لقطع التقادم فوراً.',
    btnIntake: 'استشر محامياً دولياً لقطع التقادم'
  },
  es: {
    badge: 'Motor Legal Transfronterizo con IA',
    title: 'Calculadora de Prescripción y Plazos Legales para Litigios Internacionales',
    subtitle: 'Calcule los plazos de caducidad y prescripción legal según las leyes de China, EE.UU., México, Alemania y la Convención CISG.',
    labelType: 'Tipo de Disputa o Reclamación',
    optTrade: 'Incumplimiento de Contratos de Compraventa Internacional',
    optCargo: 'Daño de Carga Marítima / Reclamación de Conocimiento (B/L)',
    optDebt: 'Cobro de Deudas Comerciales Transfronterizas',
    optLegacy: 'Herencias Transfronterizas y Sucesiones Patrimoniales',
    labelJurisdiction: 'Jurisdicción Aplicable / Ley Rectora',
    jurCn: 'Derecho Chino (Código Civil Art. 188 / 594)',
    jurUs: 'Derecho de EE.UU. (Código de Comercio UCC § 2-725)',
    jurAe: 'Derecho de EAU (Tribunales DIFC / Código Comercial Federal)',
    jurDe: 'Derecho Alemán (Código Civil BGB § 195)',
    jurSg: 'Derecho de Singapur (Limitation Act Cap. 163)',
    jurMx: 'Derecho Mexicano (Código de Comercio Art. 1043)',
    jurCisg: 'Convención de la ONU CISG (Art. 39 Notificación)',
    labelStartDate: 'Fecha de Incumplimiento o Entrega',
    btnCalculate: 'Calcular Plazo de Prescripción',
    unitDays: 'Días Restantes',
    unitYears: 'Años',
    labelRule: 'Fundamento Legal Aplicable',
    labelDeadline: 'Fecha Límite Final de Prescripción',
    labelKeyAct: 'Acción Legal Estratégica',
    ctaTip: '¿El plazo está próximo a vencer? El bufete internacional Shenyuan puede emitir una carta de intimación formal para interrumpir la prescripción.',
    btnIntake: 'Consultar Abogado Internacional'
  }
}

const ui = computed(() => UI_DICT[currentLang.value] || UI_DICT.zh)

// 规则库：各法域与业务时效年限映射
function getLimitationRule(t: string, j: string) {
  // 海运货损特殊规则：全球公约（海牙-维斯比规则）通常为 1 年
  if (t === 'cargo') {
    return {
      years: 1,
      name: currentLang.value === 'zh' ? '《海牙-维斯比规则》/ 中国海商法第257条 (海上货损索赔诉讼时效)' :
            (currentLang.value === 'ar' ? 'قواعد لاهاي-فيسبي / المادة 257 من القانون البحري (سنة واحدة)' :
            (currentLang.value === 'es' ? 'Reglas de La Haya-Visby / Plazo Marítimo de 1 año' : 'Hague-Visby Rules / Maritime Cargo Damage Limitation (1 Year)')),
      advice: currentLang.value === 'zh' ? '海运索赔时效极短（仅1年）且不可仅凭口头协商中断。必须在时效内向承运人取得书面延期声明或直接提诉。' :
              (currentLang.value === 'ar' ? 'مدة التقادم في دعاوى الشحن البحري سنة واحدة حتمية. يلزم الحصول على تمديد خطي رسمي أو رفع الدعوى فوراً.' :
              (currentLang.value === 'es' ? 'El plazo es de solo 1 año improrrogable sin pacto expreso. Se debe obtener extensión escrita o demandar.' : 'Strict 1-year time bar applies. Demand written extension or file action immediately.'))
    }
  }

  // 国际贸易与买卖合同特殊规则
  if (t === 'trade') {
    if (j === 'cn') {
      return {
        years: 4,
        name: currentLang.value === 'zh' ? '《中华人民共和国民法典》第594条 (国际货物买卖合同争议诉讼时效)' : 'PRC Civil Code Art. 594 (4 Years)',
        advice: currentLang.value === 'zh' ? '国际货物买卖合同诉讼时效为 4 年。可通过寄送具有公证效力的涉外律师催款函有效中断时效并重新起算。' : 'Statute of limitations is 4 years. Formal demand letters can effectively toll the prescription clock.'
      }
    }
    if (j === 'us' || j === 'cisg') {
      return {
        years: 4,
        name: currentLang.value === 'zh' ? '美国《统一商法典》(UCC) § 2-725 / 联合国国际货物销售时效公约' : 'US UCC § 2-725 / UN Limitation Convention (4 Years)',
        advice: currentLang.value === 'zh' ? '买卖合同违约自违约发生时起算 4 年，当事人可在合同中约定缩短至不少于 1 年。应核对合同是否有缩短约定。' : 'Default 4 years under UCC § 2-725. Check sales contract for shorter negotiated bar.'
      }
    }
  }

  // 法域基础规则
  if (j === 'de') {
    return {
      years: 3,
      name: currentLang.value === 'zh' ? '德国民法典 (BGB) § 195 一般诉讼时效' : 'German Civil Code (BGB) § 195 (3 Years)',
      advice: currentLang.value === 'zh' ? '德国常规时效为 3 年，且自发生当年的 12 月 31 日才开始统一计算。若未申请催告裁定 (Mahnverfahren) 容易年末失效。' : 'German standard limitation runs 3 years from year-end. File Mahnverfahren prior to Dec 31.'
    }
  }
  if (j === 'ae') {
    return {
      years: 5,
      name: currentLang.value === 'zh' ? '阿联酋商法典 / DIFC 破产与商事法条' : 'UAE Commercial Law / DIFC Courts Code (5 Years)',
      advice: currentLang.value === 'zh' ? '阿联酋商事债务时效一般为 5 年。中东债务人若出现注销或破产前兆，应立刻向 DIFC 申请全球财产冻结令。' : 'Standard 5 years in commercial obligations. Move for worldwide freezing orders if insolvency looms.'
    }
  }
  if (j === 'sg') {
    return {
      years: 6,
      name: currentLang.value === 'zh' ? '新加坡时效法 (Limitation Act) 第6条 (合同争议)' : 'Singapore Limitation Act (6 Years)',
      advice: currentLang.value === 'zh' ? '合同违约诉讼时效为 6 年。新加坡司法效率高，适时结合仲裁或高等法院简易判决（Summary Judgment）高效追偿。' : '6 years for contract claims. Consider summary judgment via Singapore High Court.'
    }
  }
  if (j === 'mx') {
    return {
      years: 1,
      name: currentLang.value === 'zh' ? '墨西哥联邦商法典第1043条 (零售/商品清收)' : 'Mexican Commercial Code Art. 1043 (1 Year)',
      advice: currentLang.value === 'zh' ? '墨西哥商事货物清收时效仅 1 年，拉美外贸中最易因当事人反复协商导致丧失胜诉权。必须在 12 个月内发正式公证催告。' : 'Tight 1-year limit for commercial delivery disputes in Mexico. Issue formal notarized protest.'
    }
  }

  // 默认中国法律一般商事与继承时效
  return {
    years: 3,
    name: currentLang.value === 'zh' ? '《中华人民共和国民法典》第188条 (普通诉讼时效)' : 'PRC Civil Code Art. 188 General Prescription (3 Years)',
    advice: currentLang.value === 'zh' ? '自权利人知道或应当知道权利受到损害及义务人之日起计算 3 年。若曾签署还款计划或书面认账，可发生时效中断。' : '3-year standard bar under PRC law. Interrupted by debtor written acknowledgment.'
  }
}

function calculate() {
  if (!startDate.value) return
  const rule = getLimitationRule(selectedType.value, selectedJurisdiction.value)
  const start = new Date(startDate.value)
  
  // 计算最后截止日期
  const deadline = new Date(start)
  deadline.setFullYear(deadline.getFullYear() + rule.years)
  
  const diffTime = deadline.getTime() - today.getTime()
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

  let level = 'safe'
  let icon = '🛡️'
  let statusText = currentLang.value === 'zh' ? '时效充裕 · 正常维权窗口' : (currentLang.value === 'ar' ? 'مهلة قانونية كافية' : 'Plazo Seguro')

  if (diffDays < 0) {
    level = 'danger'
    icon = '🚨'
    statusText = currentLang.value === 'zh' ? '已超诉讼时效 · 面临抗辩风险！' : (currentLang.value === 'ar' ? 'انتهت المهلة القانونية!' : '¡Plazo Vencido!')
  } else if (diffDays <= 90) {
    level = 'warning'
    icon = '⚠️'
    statusText = currentLang.value === 'zh' ? '极度危险 · 90天内即将失效！' : (currentLang.value === 'ar' ? 'تحذير عاجل: أقل من 90 يوماً!' : '¡Alerta Crítica: Vence en 90 días!')
  } else if (diffDays <= 180) {
    level = 'caution'
    icon = '⏳'
    statusText = currentLang.value === 'zh' ? '预警状态 · 半年内进入倒计时' : (currentLang.value === 'ar' ? 'تنبيه: أقل من 6 أشهر' : 'Atención: Menos de 6 meses')
  }

  result.value = {
    remainingDays: diffDays > 0 ? diffDays : 0,
    deadlineStr: deadline.toISOString().split('T')[0],
    standardYears: rule.years,
    ruleName: rule.name,
    advice: rule.advice,
    level,
    icon,
    statusText
  }
}

function applyIntake() {
  const el = document.getElementById('intake')
  if (el) {
    el.scrollIntoView({ behavior: 'smooth' })
  }
}
</script>

<style scoped>
.calculator-card {
  background: linear-gradient(145deg, #ffffff, #fdfbf7);
  border: 1px solid var(--line, #e2d8c7);
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.04);
  padding: 36px 40px;
  margin: 40px 0;
  transition: border-color 0.2s ease;
}

.calculator-card:hover {
  border-color: var(--teal, #0f766e);
}

.calc-header {
  margin-bottom: 28px;
}

.calc-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: var(--teal-soft, #e6f4f2);
  color: var(--teal-deep, #084d50);
  font-size: 12px;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 999px;
  margin-bottom: 12px;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
}

.calc-title {
  font-family: var(--serif, 'Playfair Display', serif);
  font-size: 24px;
  color: var(--teal-deep, #084d50);
  margin: 0 0 8px;
}

.calc-subtitle {
  color: var(--muted, #64748b);
  font-size: 14.5px;
  line-height: 1.6;
  margin: 0;
}

.calc-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 18px;
  width: 100%;
}

.field-col {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
  max-width: 100%;
  width: 100%;
}

.field-col label {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--ink, #1e293b);
}

.calc-select,
.calc-input {
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
  transition: all 0.2s ease;
}

.calc-select {
  background-image: url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%2364748B%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E");
  background-repeat: no-repeat;
  background-position: right 14px center;
  background-size: 10px;
  padding-right: 34px;
}

.is-rtl .calc-select {
  background-position: left 14px center;
  padding-right: 14px;
  padding-left: 34px;
}

.calc-input::-webkit-date-and-time-value {
  text-align: inherit;
}

.calc-select:focus,
.calc-input:focus {
  outline: none;
  border-color: var(--teal, #0f766e);
  box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.1);
}

.calc-actions {
  display: flex;
  justify-content: flex-end;
}

.calc-btn {
  background: var(--teal-deep, #084d50);
  color: #ffffff;
  border: none;
  padding: 12px 28px;
  font-size: 15px;
  font-weight: 700;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s ease, transform 0.1s ease;
}

.calc-btn:hover {
  background: var(--teal, #0f766e);
  transform: translateY(-1px);
}

/* 结果面板 */
.calc-result {
  margin-top: 30px;
  padding: 24px 28px;
  border-radius: 8px;
  border-left: 5px solid #10b981;
  background: #f8fafc;
  animation: fadeIn 0.3s ease-out;
}

.calc-result.status-danger {
  border-left-color: #ef4444;
  background: #fef2f2;
}

.calc-result.status-warning {
  border-left-color: #f59e0b;
  background: #fffbeb;
}

.calc-result.status-caution {
  border-left-color: #3b82f6;
  background: #eff6ff;
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 14px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-icon {
  font-size: 22px;
}

.status-text {
  font-size: 17px;
  font-weight: 700;
  color: var(--ink, #1e293b);
}

.days-remaining {
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.days-number {
  font-family: var(--serif, serif);
  font-size: 32px;
  font-weight: 700;
  color: var(--teal-deep, #084d50);
}

.status-danger .days-number {
  color: #dc2626;
}

.status-warning .days-number {
  color: #d97706;
}

.days-unit {
  font-size: 13px;
  color: var(--muted, #64748b);
}

.result-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 24px;
}

.detail-row {
  font-size: 14px;
  line-height: 1.6;
  color: #334155;
}

.detail-label {
  font-weight: 600;
  color: var(--ink, #1e293b);
}

.text-deadline {
  color: #dc2626;
  font-weight: 700;
}

.result-cta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.8);
  padding: 16px 20px;
  border-radius: 6px;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.cta-tip {
  font-size: 13.5px;
  color: var(--teal-deep, #084d50);
  font-weight: 500;
}

.cta-button {
  background: var(--gold, #d97706);
  color: #ffffff;
  padding: 8px 18px;
  border-radius: 4px;
  font-size: 13.5px;
  font-weight: 700;
  text-decoration: none;
  transition: opacity 0.2s ease;
  white-space: nowrap;
}

.cta-button:hover {
  opacity: 0.9;
}

/* RTL 适配 */
.is-rtl {
  direction: rtl;
  text-align: right;
}

.is-rtl .calc-result {
  border-left: none;
  border-right: 5px solid #10b981;
}

.is-rtl .calc-result.status-danger {
  border-right-color: #ef4444;
}

.is-rtl .calc-result.status-warning {
  border-right-color: #f59e0b;
}

.is-rtl .calc-result.status-caution {
  border-right-color: #3b82f6;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 768px) {
  .calculator-card {
    padding: 24px 20px;
  }
  .form-row {
    grid-template-columns: 1fr;
    gap: 14px;
  }
  .result-header,
  .result-cta {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  .calc-btn,
  .cta-button {
    width: 100%;
    text-align: center;
  }
}
</style>
