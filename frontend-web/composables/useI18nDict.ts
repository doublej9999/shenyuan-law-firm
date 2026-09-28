/**
 * 全站国际化四语轻量字典 (zh, en, ar, es)
 */
export type SupportedLang = 'zh' | 'en' | 'ar' | 'es'

export interface NavDict {
  brandSub: string
  services: string
  cases: string
  global: string
  team: string
  faq: string
  articles: string
  cta: string
  quickConsult: string
  drawerTitle: string
  drawerSub: string
  wechatTitle: string
  wechatDesc: string
  formName: string
  formNamePlaceholder: string
  formPhone: string
  formPhonePlaceholder: string
  formEmail: string
  formEmailPlaceholder: string
  formMatter: string
  formSummary: string
  formSummaryPlaceholder: string
  formConsent: string
  formSubmitting: string
  formSubmit: string
  footerDesc: string
}

export const I18N_DICT: Record<SupportedLang, NavDict> = {
  zh: {
    brandSub: '深远(国际)律师事务所',
    services: '服务范围',
    cases: '成果与案例',
    global: '全球网络',
    team: '团队',
    faq: '常见问题',
    articles: '法律专栏',
    cta: '开始咨询 →',
    quickConsult: '免费法律咨询',
    drawerTitle: '跨境法律咨询与评估',
    drawerSub: '涉外执业团队 24 小时内首响，先评估再行动。',
    wechatTitle: '微信快速咨询',
    wechatDesc: '微信号：ShenyuanLegal',
    formName: '您的称呼 *',
    formNamePlaceholder: '例如：王女士 / 陈先生',
    formPhone: '联系电话 *',
    formPhonePlaceholder: '手机号码，用于及时回访',
    formEmail: '电子邮箱（选填）',
    formEmailPlaceholder: '用于接收材料清单与备忘录',
    formMatter: '事项类型 *',
    formSummary: '一句话描述问题 *',
    formSummaryPlaceholder: '简要说明涉案金额、对方所在地与当前诉求...',
    formConsent: '我已阅读并同意《隐私说明》，同意提交以上信息用于初步咨询评估。',
    formSubmitting: '提交中...',
    formSubmit: '提交，获取下一步建议 →',
    footerDesc: '深远(国际)律师事务所 · 跨境争议解决与家族资产保护',
  },
  en: {
    brandSub: 'Shenyuan International Law Firm',
    services: 'Services',
    cases: 'Results',
    global: 'Global reach',
    team: 'Team',
    faq: 'FAQ',
    articles: 'Insights',
    cta: 'Start consultation →',
    quickConsult: 'Free Consultation',
    drawerTitle: 'Initial Legal Consultation',
    drawerSub: '24h response from licensed cross-border lawyers.',
    wechatTitle: 'WeChat Direct',
    wechatDesc: 'Add ShenyuanLegal for instant contact',
    formName: 'Your Name *',
    formNamePlaceholder: 'e.g. Mr. Zhang',
    formPhone: 'Phone / WhatsApp *',
    formPhonePlaceholder: 'Local number / WhatsApp',
    formEmail: 'Email (Optional)',
    formEmailPlaceholder: 'For document checklist',
    formMatter: 'Matter Type *',
    formSummary: 'Brief Description *',
    formSummaryPlaceholder: 'Briefly describe your situation...',
    formConsent: 'I agree to the privacy statement and authorize consultation.',
    formSubmitting: 'Submitting...',
    formSubmit: 'Submit for Guidance →',
    footerDesc: 'Shenyuan International Law Firm · Cross-border dispute resolution & family asset protection',
  },
  ar: {
    brandSub: 'مكتب شينيوان الدولي للمحاماة',
    services: 'مجالات الخدمة',
    cases: 'النتائج والقضايا',
    global: 'شبكتنا الدولية',
    team: 'فريق العمل',
    faq: 'الأسئلة الشائعة',
    articles: 'الرؤى القانونية',
    cta: 'ابدأ الاستشارة →',
    quickConsult: 'استشارة قانونية مجانية',
    drawerTitle: 'تقييم واستشارة قانونية دولية',
    drawerSub: 'استجابة سريعة خلال 24 ساعة من فريق محامين مرخص.',
    wechatTitle: 'تواصل مباشر عبر WeChat',
    wechatDesc: 'المعرف: ShenyuanLegal',
    formName: 'الاسم الكريم *',
    formNamePlaceholder: 'مثال: السيد / السيدة',
    formPhone: 'رقم الهاتف / واتساب *',
    formPhonePlaceholder: 'رقم الهاتف المحلي أو واتساب',
    formEmail: 'البريد الإلكتروني (اختياري)',
    formEmailPlaceholder: 'لاستلام قائمة المستندات والمذكرة',
    formMatter: 'نوع المسألة القانونية *',
    formSummary: 'وصف مختصر للقضية *',
    formSummaryPlaceholder: 'يرجى ذكر المبلغ والطرف المقابل ومطلبكم الرئيسي...',
    formConsent: 'أوافق على سياسة الخصوصية وتفويض التواصل للاستشارة القانونية.',
    formSubmitting: 'جارٍ الإرسال...',
    formSubmit: 'إرسال للحصول على التوجيه القانوني →',
    footerDesc: 'مكتب شينيوان الدولي للمحاماة · حل النزاعات العابرة للحدود وحماية الأصول العائلية',
  },
  es: {
    brandSub: 'Bufete de Abogados Internacional Shenyuan',
    services: 'Servicios',
    cases: 'Casos y Resultados',
    global: 'Red Global',
    team: 'Equipo',
    faq: 'Preguntas Frecuentes',
    articles: 'Perspectivas',
    cta: 'Iniciar consulta →',
    quickConsult: 'Consulta Legal Gratuita',
    drawerTitle: 'Consulta y Evaluación Legal Inicial',
    drawerSub: 'Respuesta en 24h por abogados especialistas en litigios transfronterizos.',
    wechatTitle: 'Contacto Directo por WeChat',
    wechatDesc: 'ID: ShenyuanLegal',
    formName: 'Su Nombre *',
    formNamePlaceholder: 'Ej: Sra. García / Sr. Rodríguez',
    formPhone: 'Teléfono / WhatsApp *',
    formPhonePlaceholder: 'Número local o WhatsApp',
    formEmail: 'Correo Electrónico (Opcional)',
    formEmailPlaceholder: 'Para lista de verificación de documentos',
    formMatter: 'Tipo de Asunto *',
    formSummary: 'Breve Descripción del Asunto *',
    formSummaryPlaceholder: 'Indique monto en disputa, ubicación de la contraparte y pretensión...',
    formConsent: 'Acepto la declaración de privacidad y autorizo el contacto para evaluación legal.',
    formSubmitting: 'Enviando...',
    formSubmit: 'Enviar para Obtener Orientación →',
    footerDesc: 'Bufete Shenyuan · Resolución de controversias transfronterizas y protección patrimonial',
  },
}
