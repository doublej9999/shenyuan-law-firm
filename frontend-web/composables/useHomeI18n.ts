/**
 * 首页四语全量数据字典 (zh, en, ar, es)
 * 覆盖：Hero、Intake 表单、Trust 徽章、三大业务线、工作流程、数据成果、案例展示、全球网络、团队、FAQ
 */
import type { SupportedLang } from '@/composables/useI18nDict'

export interface HomeTranslation {
  hero: {
    eyebrow: string
    title1: string
    titleHighlight: string
    desc: string
    ctaPrimary: string
    ctaSecondary: string
    noteLang: string
    noteJurisdictions: string
    noteAssess: string
  }
  intake: {
    title: string
    desc: string
    wechatTitle: string
    wechatDesc: string
    wechatId: string
    fieldName: string
    placeholderName: string
    fieldEmail: string
    placeholderEmail: string
    fieldMatter: string
    matterOptions: { value: string; label: string }[]
    fieldPhone: string
    placeholderPhone: string
    fieldSummary: string
    placeholderSummary: string
    consentPre: string
    privacyLink: string
    consentPost: string
    viewPrivacy: string
    btnSubmitting: string
    btnSubmit: string
    formNote: string
  }
  trust: {
    bilingualTitle: string
    bilingualDesc: string
    globalTitle: string
    globalDesc: string
    responseTitle: string
    responseDesc: string
    privacyTitle: string
    privacyDesc: string
  }
  services: {
    eyebrow: string
    title: string
    desc: string
    tradeNum: string
    tradeTitle: string
    tradeDesc: string
    tradeItems: string[]
    tradeLink: string
    recoveryNum: string
    recoveryTitle: string
    recoveryDesc: string
    recoveryItems: string[]
    recoveryLink: string
    legacyNum: string
    legacyTitle: string
    legacyDesc: string
    legacyItems: string[]
    legacyLink: string
    ctaText: string
    ctaBtn: string
  }
  process: {
    eyebrow: string
    title: string
    desc: string
    step1Num: string
    step1Title: string
    step1Desc: string
    step2Num: string
    step2Title: string
    step2Desc: string
    step3Num: string
    step3Title: string
    step3Desc: string
  }
  stats: {
    stat1Num: string
    stat1Label: string
    stat2Num: string
    stat2Label: string
    stat3Num: string
    stat3Label: string
    stat4Num: string
    stat4Label: string
  }
  cases: {
    eyebrow: string
    title: string
    desc: string
    pathLabel: string
    soonBadge: string
    btnConsult: string
    card1Tag: string
    card1Title: string
    card1Desc: string
    card1Path: string
    card2Tag: string
    card2Title: string
    card2Desc: string
    card2Path: string
    card3Tag: string
    card3Title: string
    card3Desc: string
    card3Path: string
  }
  global: {
    eyebrow: string
    title: string
    desc: string
    regions: string[]
    note: string
    consultBtn: string
  }
  team: {
    eyebrow: string
    title: string
    desc: string
    card1Role: string
    card1Title: string
    card1Desc: string
    card1List: string[]
    card1Note: string
    card2Role: string
    card2Title: string
    card2Desc: string
    card2List: string[]
    card2Note: string
    card3Role: string
    card3Title: string
    card3Desc: string
    card3List: string[]
    card3Note: string
    card4Role: string
    card4Title: string
    card4Desc: string
    card4List: string[]
    card4Note: string
  }
  whyTrust: {
    eyebrow: string
    title: string
    card1Title: string
    card1Desc: string
    card2Title: string
    card2Desc: string
    card3Title: string
    card3Desc: string
    card4Title: string
    card4Desc: string
    statementLabel: string
    statementText: string
  }
  faq: {
    eyebrow: string
    title: string
    desc: string
    items: { q: string; a: string }[]
    ctaTitle: string
    ctaDesc: string
    ctaBtn: string
  }
}

export const HOME_I18N: Record<SupportedLang, HomeTranslation> = {
  zh: {
    hero: {
      eyebrow: '跨境争议解决与家族资产保护',
      title1: '跨境争议，',
      titleHighlight: '全球落地执行。',
      desc: '深远国际律师事务所为中国企业与家庭提供国际贸易争议、跨境债务追收、继承与家族资产法律服务——用中文理解你的处境，用全球合作律所网络在当地落地执行。',
      ctaPrimary: '免费法律咨询 →',
      ctaSecondary: '查看服务范围',
      noteLang: '中英双语沟通',
      noteJurisdictions: '覆盖 30+ 国家与地区',
      noteAssess: '先评估，再行动',
    },
    intake: {
      title: '先说说发生了什么',
      desc: '留下基本信息，我们会先判断事项类型、地域与下一步，24 小时内回复。紧急情况建议直接微信联系并注明“紧急”。',
      wechatTitle: '微信快速咨询',
      wechatDesc: '适合紧急、跨时区或希望先简单确认方向的咨询。',
      wechatId: '微信号：ShenyuanLegal',
      fieldName: '称呼',
      placeholderName: '例如：王女士',
      fieldEmail: '邮箱（选填）',
      placeholderEmail: '选填，用于接收材料清单',
      fieldMatter: '事项类型',
      matterOptions: [
        { value: '国际贸易争议', label: '国际贸易争议' },
        { value: '诉讼与债务追收', label: '诉讼与债务追收' },
        { value: '继承与家族资产纠纷', label: '继承与家族资产纠纷' },
        { value: '不确定，希望先沟通', label: '不确定，希望先沟通' },
      ],
      fieldPhone: '联系电话',
      placeholderPhone: '手机或固定电话，用于回电联系',
      fieldSummary: '一句话描述问题',
      placeholderSummary: '例如：海外客户已收货，但 4 个月未支付尾款。',
      consentPre: '我已阅读并同意',
      privacyLink: '《隐私说明》',
      consentPost: '，同意提交以上信息用于咨询沟通。',
      viewPrivacy: '查看隐私说明',
      btnSubmitting: '提交中...',
      btnSubmit: '提交，获取下一步建议 →',
      formNote: '提交不代表建立委托关系。请勿在此处填写身份证号、银行账号等敏感信息。',
    },
    trust: {
      bilingualTitle: '中英双语团队',
      bilingualDesc: '中文讲清事实，英文保留法律精度',
      globalTitle: '全球协作网络',
      globalDesc: '30+ 国家与地区当地执业律所',
      responseTitle: '24 小时首响承诺',
      responseDesc: '收到咨询后尽快安排沟通',
      privacyTitle: '隐私与保密',
      privacyDesc: '咨询信息仅用于评估与沟通',
    },
    services: {
      eyebrow: '核心业务',
      title: '三类高频跨境事项，一条清晰的解决路径。',
      desc: '围绕中国企业与家庭在海外最常遇到的问题，从欠款事实与证据入手，判断协商、追收、诉讼或执行路径。',
      tradeNum: '01 / TRADE',
      tradeTitle: '国际贸易争议',
      tradeDesc: '处理交易履行、货款、代理与跨境合同之间的纠纷。',
      tradeItems: [
        '拖欠货款 / 供应商违约',
        '代理、经销、跨境合同审查',
        '海关、物流、质量争议',
        '国际贸易诈骗识别与应对',
      ],
      tradeLink: '了解贸易争议服务 →',
      recoveryNum: '02 / RECOVERY',
      recoveryTitle: '诉讼与债务追收',
      recoveryDesc: '从欠款事实与资产线索出发，判断追收、诉讼或执行路径。',
      recoveryItems: [
        '海外客户欠款追收',
        '中国境内与海外资产调查',
        '判决、仲裁裁决跨境执行',
        '商业欺诈调查',
      ],
      recoveryLink: '了解追收服务 →',
      legacyNum: '03 / LEGACY',
      legacyTitle: '继承与家族资产纠纷',
      legacyDesc: '协助梳理大陆与海外多地的继承、房产、股权与家族争议。',
      legacyItems: [
        '中国大陆与海外多地继承',
        '房产、股权、存款继承',
        '遗嘱效力与遗产分割',
        '家族成员失联或争议',
      ],
      legacyLink: '了解继承服务 →',
      ctaText: '不确定属于哪一类？先提交你的情况，我们帮你判断入口。',
      ctaBtn: '提交案件信息 →',
    },
    process: {
      eyebrow: '从咨询到行动',
      title: '先把问题说清，再把路径走稳。',
      desc: '适合需要跨时区、双语沟通，或同时涉及中国大陆与海外法域的复杂事项。',
      step1Num: '01',
      step1Title: '免费咨询建档',
      step1Desc: '提交基本情况或微信联系，我们梳理人物、金额、时间线与目标。',
      step2Num: '02',
      step2Title: '事实、证据与法域评估',
      step2Desc: '初步识别时效、证据、资产位置与可能涉及的法域，判断可行路径。',
      step3Num: '03',
      step3Title: '策略、报价与执行',
      step3Desc: '根据事项特点确定谈判、追收或诉讼策略，明确材料、风险与里程碑。',
    },
    stats: {
      stat1Num: '30+',
      stat1Label: '协作国家与地区',
      stat2Num: '3',
      stat2Label: '大跨境业务线',
      stat3Num: '24h',
      stat3Label: '咨询首响承诺',
      stat4Num: '4',
      stat4Label: '种语言服务 (中/EN/AR/ES)',
    },
    cases: {
      eyebrow: '案例与成果',
      title: '我们处理的，都是真实生意里的难题。',
      desc: '以下是典型情形与处理路径示例；脱敏案例复盘（已隐去身份信息）整理完成后将陆续发布。每一件案子，都从一次免费咨询开始。',
      pathLabel: '处理路径',
      soonBadge: '脱敏案例复盘整理中',
      btnConsult: '类似案件，免费咨询 →',
      card1Tag: 'TRADE',
      card1Title: '海外客户收货后拖欠尾款',
      card1Desc: '典型情形：货已交付，客户以质量问题、汇率波动等理由拖延付款数月。',
      card1Path: '证据梳理 → 律师函与协商 → 诉讼 / 仲裁 → 判决执行',
      card2Tag: 'RECOVERY',
      card2Title: '判决赢了，钱却拿不回来',
      card2Desc: '典型情形：中国境内或境外已有生效判决 / 仲裁裁决，但债务人转移资产或下落不明。',
      card2Path: '资产调查 → 财产保全 → 承认与执行申请 → 执行和解',
      card3Tag: 'LEGACY',
      card3Title: '亲属在海外去世，遗产横跨两国',
      card3Desc: '典型情形：继承人身在国内，需处理海外房产、存款与公司股权，涉及遗嘱、认证与外汇。',
      card3Path: '境外公证认证 → 遗产管理人指定 → 涉税与外汇合规 → 权属变更',
    },
    global: {
      eyebrow: '全球网络',
      title: '客户在哪里，协作网络就在哪里。',
      desc: '通过与当地执业律所的合作，覆盖中国企业出海与海外华人集中的主要市场。具体地区以当次评估为准，一案一议。',
      regions: ['美国', '加拿大', '澳大利亚', '新西兰', '新加坡', '英国', '德国', '法国', '日本', '韩国', '阿联酋', '沙特', '泰国', '越南', '马来西亚', '印尼', '中国香港', '中国澳门', '巴西', '墨西哥'],
      note: '合作律所网络覆盖 30+ 国家与地区。未列出的地区，也欢迎先提交咨询，我们会判断当地是否有可落地路径。',
      consultBtn: '提交咨询 →',
    },
    team: {
      eyebrow: '律师团队',
      title: '懂中国法律，也懂海外规则。',
      desc: '团队以中国大陆执业律师为核心，专注跨境业务；境外程序通过与当地执业律所协作完成，确保每个环节程序合规。',
      card1Role: 'CROSS-BORDER DISPUTES',
      card1Title: '跨境争议解决',
      card1Desc: '国际贸易与合同争议、跨境诉讼与仲裁、争议解决条款设计。',
      card1List: ['中国大陆执业律师', '中英双语工作'],
      card1Note: '团队成员及详细简历更新中。',
      card2Role: 'RECOVERY & ENFORCEMENT',
      card2Title: '追收与执行',
      card2Desc: '跨境债务追收、境内与海外资产调查、判决与仲裁裁决执行。',
      card2List: ['中国境内资产调查专长', '与海外执行律师协作'],
      card2Note: '团队成员及详细简历更新中。',
      card3Role: 'INHERITANCE & FAMILY',
      card3Title: '继承与家族资产',
      card3Desc: '跨境继承、遗嘱规划与效力争议、家族企业传承与纠纷。',
      card3List: ['多法域继承程序衔接', '照顾家庭沟通场景'],
      card3Note: '团队成员及详细简历更新中。',
      card4Role: 'GLOBAL PARTNERS',
      card4Title: '全球合作律所网络',
      card4Desc: '覆盖 30+ 国家与地区的当地执业律所与追收机构，按案件类型与地区匹配。',
      card4List: ['按案件严格筛选与匹配', '程序合规与本地化执行'],
      card4Note: '合作网络名录更新中。',
    },
    whyTrust: {
      eyebrow: '客户信任体系',
      title: '专业、可信、安全——跨境法律服务的底线。',
      card1Title: '保密承诺',
      card1Desc: '咨询信息仅用于初步评估与后续沟通，受律师保密义务约束；数据处理遵循中国《个人信息保护法》与 GDPR 合规要求。',
      card2Title: '先评估，再行动',
      card2Desc: '初步咨询用于判断事项类型、时效、证据与可行路径，不收费、不构成委托关系，也不会劝你做不必要的程序。',
      card3Title: '诚实评估，不承诺结果',
      card3Desc: '我们如实说明可行性与风险边界。法律程序的结果取决于事实、证据与当地规则，任何承诺办案结果的说法都不可信。',
      card4Title: '跨境协作规范',
      card4Desc: '境外法律程序通过与当地执业律所合作提供，确保在当地执业规则下合规推进，绝不越界出具当地法律意见。',
      statementLabel: '执业声明：',
      statementText: '深远(国际)律师事务所在中国大陆执业；境外法律程序通过与当地执业律所合作完成。初步咨询不构成委托关系或正式法律意见。',
    },
    faq: {
      eyebrow: '开始之前',
      title: '常见问题',
      desc: '针对涉外商事咨询的常见疑虑解答。',
      items: [
        { q: '提交咨询后，多久会有回复？', a: '我们承诺 24 小时内首响。收到信息后，会结合事项紧急程度、所在地区和材料完整度安排后续沟通。' },
        { q: '我还没有整理好全部材料，可以提交吗？', a: '可以。先提供时间线、人物和你想实现的结果，足够用于初步判断入口。' },
        { q: '这是正式法律意见吗？', a: '不是。初步咨询用于了解事项和判断下一步，不构成律师委托或正式法律意见。' },
        { q: '可以直接通过微信联系吗？', a: '可以。你可以通过微信先说明事项类型和紧急程度；如果材料较多，也建议同时提交表单，便于我们完整了解情况。' },
      ],
      ctaTitle: '你的跨境纠纷，值得一个用母语讲清的起点。',
      ctaDesc: '提交基本情况，或扫码添加微信。我们会先判断时效、证据与可行路径——不收费，不承诺结果，只给方向。',
      ctaBtn: '免费法律咨询 →',
    },
  },

  en: {
    hero: {
      eyebrow: 'Cross-border dispute resolution & family asset protection',
      title1: 'Cross-border disputes, ',
      titleHighlight: 'executed globally.',
      desc: 'Shenyuan International helps businesses and families resolve trade disputes, recover cross-border debts, and protect inherited assets — bilingual, executed through a global network of local counsel.',
      ctaPrimary: 'Free legal consultation →',
      ctaSecondary: 'Explore services',
      noteLang: 'Bilingual English / Chinese',
      noteJurisdictions: 'Coverage across 30+ jurisdictions',
      noteAssess: 'Assess first, act clearly',
    },
    intake: {
      title: 'Tell us what happened',
      desc: 'Share the basics. We assess jurisdiction, evidence, and next steps within 24 hours. For urgent matters, message us on WeChat and mark urgent.',
      wechatTitle: 'Quick WeChat consult',
      wechatDesc: 'Useful for urgent, time-zone sensitive questions.',
      wechatId: 'WeChat: ShenyuanLegal',
      fieldName: 'Name',
      placeholderName: 'e.g. Mr. Zhang',
      fieldEmail: 'Email (optional)',
      placeholderEmail: 'For document checklist',
      fieldMatter: 'Matter type',
      matterOptions: [
        { value: '国际贸易争议', label: 'International trade dispute' },
        { value: '诉讼与债务追收', label: 'Litigation & debt recovery' },
        { value: '继承与家族资产纠纷', label: 'Inheritance & family assets' },
        { value: '不确定，希望先沟通', label: 'Not sure yet' },
      ],
      fieldPhone: 'Phone',
      placeholderPhone: 'Local number / WhatsApp',
      fieldSummary: 'Briefly describe the issue',
      placeholderSummary: 'e.g. Overseas buyer received goods but has not paid for 4 months.',
      consentPre: 'I have read and agree to the',
      privacyLink: 'Privacy Notice',
      consentPost: ' and consent to this information being used for consultation.',
      viewPrivacy: 'View privacy notice',
      btnSubmitting: 'Submitting...',
      btnSubmit: 'Submit for next-step guidance →',
      formNote: 'Submission does not establish an attorney-client relationship. Please do not submit confidential banking details.',
    },
    trust: {
      bilingualTitle: 'Bilingual Team',
      bilingualDesc: 'Facts in your language, precision in local legal terms',
      globalTitle: 'Global Network',
      globalDesc: 'Locally licensed counsel across 30+ jurisdictions',
      responseTitle: '24-Hour Response',
      responseDesc: 'Rapid case evaluation and direct counsel callback',
      privacyTitle: 'Privacy & Discretion',
      privacyDesc: 'All intake details are strictly confidential',
    },
    services: {
      eyebrow: 'Core Practice',
      title: 'Three core practice lines, one clear path forward.',
      desc: 'Focused on the most frequent cross-border challenges, mapping negotiation, asset tracing, litigation, or judicial enforcement.',
      tradeNum: '01 / TRADE',
      tradeTitle: 'International trade disputes',
      tradeDesc: 'Breach of contract, non-performance, letters of credit, and commercial disputes.',
      tradeItems: [
        'Unpaid invoices / supplier breach',
        'Agency, distribution, and cross-border contracts',
        'Customs, shipping, and cargo damage claims',
        'Trade fraud detection and emergency response',
      ],
      tradeLink: 'Trade dispute services →',
      recoveryNum: '02 / RECOVERY',
      recoveryTitle: 'Litigation & debt recovery',
      recoveryDesc: 'Asset tracing, debt recovery, and cross-border judgment recognition.',
      recoveryItems: [
        'Overseas customer unpaid invoice recovery',
        'Cross-border asset investigation & tracing',
        'Recognition & enforcement of arbitral awards',
        'Corporate fraud and insolvency proceedings',
      ],
      recoveryLink: 'Recovery services →',
      legacyNum: '03 / LEGACY',
      legacyTitle: 'Inheritance & family assets',
      legacyDesc: 'Multi-jurisdictional inheritance, overseas probate, real estate, and trust matters.',
      legacyItems: [
        'Multi-country probate and estate division',
        'Cross-border real estate and equity succession',
        'Will validity and international notarization',
        'Foreign exchange and estate compliance',
      ],
      legacyLink: 'Legacy services →',
      ctaText: 'Not sure which category fits? Submit your situation and we will help you identify the entry point.',
      ctaBtn: 'Share your case →',
    },
    process: {
      eyebrow: 'From consultation to action',
      title: 'Clarify the matter. Move forward with care.',
      desc: 'Designed for matters spanning time zones, legal traditions, and multi-country assets.',
      step1Num: '01',
      step1Title: 'Free Consultation & Intake',
      step1Desc: 'Submit case details. We identify the parties, timeline, claim amounts, and immediate risks.',
      step2Num: '02',
      step2Title: 'Evidence & Jurisdiction Review',
      step2Desc: 'Assess statute of limitations, asset trace feasibility, and optimal forums for action.',
      step3Num: '03',
      step3Title: 'Strategy & Direct Execution',
      step3Desc: 'Deploy demand letters, interim asset freezes, or formal court proceedings with clear fee milestones.',
    },
    stats: {
      stat1Num: '30+',
      stat1Label: 'jurisdictions covered',
      stat2Num: '3',
      stat2Label: 'core practice lines',
      stat3Num: '24h',
      stat3Label: 'first-response commitment',
      stat4Num: '4',
      stat4Label: 'languages: ZH / EN / AR / ES',
    },
    cases: {
      eyebrow: 'Cases & outcomes',
      title: 'We handle the hard problems of real business.',
      desc: 'Typical scenarios and the pathways we deploy. All consultations begin with a confidential case assessment.',
      pathLabel: 'Pathway',
      soonBadge: 'Anonymized case study coming soon',
      btnConsult: 'Free Consultation →',
      card1Tag: 'TRADE',
      card1Title: 'Buyer received goods, refused final payment',
      card1Desc: 'Goods delivered, but the foreign buyer withholds balance citing currency rules or specious defects.',
      card1Path: 'Evidence audit → Formal demand & freezing → Court litigation → Asset recovery',
      card2Tag: 'RECOVERY',
      card2Title: 'Won the judgment, debtor moved assets',
      card2Desc: 'Enforceable award obtained, but debtor claims insolvency while holding offshore entity assets.',
      card2Path: 'International asset tracing → Cross-border recognition → Judicial auction',
      card3Tag: 'LEGACY',
      card3Title: 'Deceased estate spans multiple countries',
      card3Desc: 'Heirs need to transfer overseas real estate, equities, and offshore deposits across divergent probate laws.',
      card3Path: 'Apostille certification → Estate administrator grant → Tax clearing → Asset transfer',
    },
    global: {
      eyebrow: 'Global Reach',
      title: 'Where our clients are, our network follows.',
      desc: 'Through partnerships with locally licensed counsel, we cover the markets where cross-border businesses are concentrated.',
      regions: ['United States', 'Canada', 'Australia', 'New Zealand', 'Singapore', 'United Kingdom', 'Germany', 'France', 'Japan', 'South Korea', 'UAE', 'Saudi Arabia', 'Thailand', 'Vietnam', 'Malaysia', 'Indonesia', 'Hong Kong', 'Macau', 'Brazil', 'Mexico'],
      note: 'Our partner network spans 30+ jurisdictions. If your region is not listed, submit your inquiry for a custom route evaluation.',
      consultBtn: 'Consult Us →',
    },
    team: {
      eyebrow: 'Our Team',
      title: 'Trained in Chinese law, fluent in foreign rules.',
      desc: 'Core team consists of licensed lawyers focused on cross-border disputes, executed with local counsel abroad.',
      card1Role: 'CROSS-BORDER DISPUTES',
      card1Title: 'Cross-Border Disputes',
      card1Desc: 'International trade, commercial contracts, cross-border litigation, and arbitration.',
      card1List: ['Licensed in mainland China', 'Bilingual practice (Chinese / English)'],
      card1Note: 'Team profiles updating.',
      card2Role: 'RECOVERY & ENFORCEMENT',
      card2Title: 'Recovery & Enforcement',
      card2Desc: 'Cross-border debt collection, domestic/overseas asset tracing, and award execution.',
      card2List: ['Specialized in asset tracing', 'Collaboration with overseas enforcement counsel'],
      card2Note: 'Team profiles updating.',
      card3Role: 'INHERITANCE & FAMILY',
      card3Title: 'Inheritance & Family Assets',
      card3Desc: 'Cross-border estates, will validity disputes, and family business succession.',
      card3List: ['Multi-jurisdiction probate coordination', 'Discreet handling of family dynamics'],
      card3Note: 'Team profiles updating.',
      card4Role: 'GLOBAL PARTNERS',
      card4Title: 'Global Partner Network',
      card4Desc: 'Network of local law firms across 30+ countries matched per case requirement.',
      card4List: ['Vetted by case complexity', 'Strict compliance and local enforcement'],
      card4Note: 'Directory updating.',
    },
    whyTrust: {
      eyebrow: 'Why Clients Trust Us',
      title: 'Professional, trustworthy, secure — the baseline of cross-border legal service.',
      card1Title: 'Confidentiality Commitment',
      card1Desc: 'Consultation information is used solely for initial assessment, protected under attorney confidentiality rules.',
      card2Title: 'Assess First, Act Clearly',
      card2Desc: 'Initial intake clarifies viable legal pathways and evidentiary burdens without pushing unnecessary procedures.',
      card3Title: 'Honest Assessment',
      card3Desc: 'We provide objective probability analysis. Outcomes depend strictly on evidence, procedural timing, and local law.',
      card4Title: 'Cross-Border Compliance',
      card4Desc: 'Foreign proceedings are handled strictly with locally licensed counsel in compliance with jurisdiction boundaries.',
      statementLabel: 'Practice Statement: ',
      statementText: 'Shenyuan International practices in mainland China; foreign proceedings are conducted through locally licensed counsel.',
    },
    faq: {
      eyebrow: 'Before You Begin',
      title: 'Frequently Asked Questions',
      desc: 'Direct answers to frequent inquiries regarding cross-border legal engagement.',
      items: [
        { q: 'How soon will I hear back?', a: 'We commit to a first response within 24 hours to schedule an initial consultation.' },
        { q: 'Can I submit before I have all documents?', a: 'Yes. Basic timelines and claimant amounts are sufficient to determine initial legal viable options.' },
        { q: 'Is this formal legal advice?', a: 'No. Initial evaluation is for feasibility diagnosis and does not constitute a formal attorney retainer.' },
        { q: 'Can I contact you on WeChat?', a: 'Yes. You can message ShenyuanLegal directly for time-sensitive questions.' },
      ],
      ctaTitle: 'Your cross-border dispute deserves a clear starting point.',
      ctaDesc: 'Submit your situation. We assess deadlines, evidence, and viable enforcement options — directional and objective.',
      ctaBtn: 'Free Consultation →',
    },
  },

  ar: {
    hero: {
      eyebrow: 'تسوية النزاعات العابرة للحدود وحماية الأصول العائلية',
      title1: 'نزاعات دولية، ',
      titleHighlight: 'تنفيذ قضائي عالمي.',
      desc: 'يقدم مكتب شينيوان الدولي للمحاماة خدمات قانونية رفيعة في نزاعات التجارة الدولية، وتحصيل الديون العابرة للحدود، وحماية الميراث والأصول العائلية — عبر شبكة دولية واسعة من مكاتب المحاماة المرخصة محلياً.',
      ctaPrimary: 'استشارة قانونية مجانية ←',
      ctaSecondary: 'استكشاف مجالات الخدمة',
      noteLang: 'تواصل متعدد اللغات (عربي / صيني / إنجليزي)',
      noteJurisdictions: 'تغطية تشمل أكثر من 30 دولة ومنطقة',
      noteAssess: 'التقييم القانوني أولاً، ثم التنفيذ',
    },
    intake: {
      title: 'أخبرنا بتفاصيل قضيتك',
      desc: 'شاركنا المعلومات الأساسية. سنقوم بتقييم نوع القضية والاختصاص القضائي والخطوات العملية خلال 24 ساعة.',
      wechatTitle: 'استشارة فورية عبر WeChat',
      wechatDesc: 'مناسبة للاستفسارات العاجلة وفروق التوقيت السريعة.',
      wechatId: 'المعرف: ShenyuanLegal',
      fieldName: 'الاسم الكريم',
      placeholderName: 'مثال: السيد / السيدة',
      fieldEmail: 'البريد الإلكتروني (اختياري)',
      placeholderEmail: 'لاستلام قائمة المستندات والمذكرة',
      fieldMatter: 'نوع المسألة القانونية',
      matterOptions: [
        { value: '国际贸易争议', label: 'نزاع في التجارة الدولية والجمارك' },
        { value: '诉讼与债务追收', label: 'التقاضي وتحصيل الديون والتعويضات' },
        { value: '继承与家族资产纠纷', label: 'الميراث وقضايا الأصول والتركات' },
        { value: '不确定，希望先沟通', label: 'غير محدد، أرغب في تقييم أولي' },
      ],
      fieldPhone: 'رقم الهاتف / واتساب',
      placeholderPhone: 'رقم الهاتف المحلي أو واتساب',
      fieldSummary: 'وصف مختصر للقضية',
      placeholderSummary: 'مثال: المشتري استلم البضائع لكنه امتنع عن سداد الدفعة النهائية منذ 4 أشهر.',
      consentPre: 'لقد قرأت ووافقت على',
      privacyLink: 'إشعار الخصوصية',
      consentPost: ' وأوافق على استخدام هذه البيانات لغرض الاستشارة القانونية.',
      viewPrivacy: 'عرض سياسة الخصوصية',
      btnSubmitting: 'جارٍ الإرسال...',
      btnSubmit: 'إرسال للحصول على التوجيه القانوني ←',
      formNote: 'إرسال هذا النموذج لا ينشئ علاقة محامٍ وموكل رسمية. يُرجى عدم مشاركة أرقام الحسابات البنكية السرية هنا.',
    },
    trust: {
      bilingualTitle: 'فريق عمل متعدد اللغات',
      bilingualDesc: 'تواصل واضح بلغتك مع الحفاظ التام على الدقة القانونية',
      globalTitle: 'شبكة محاماة دولية',
      globalDesc: 'محامون مرخصون في أكثر من 30 دولة ومنطقة حول العالم',
      responseTitle: 'التزام بالرد خلال 24 ساعة',
      responseDesc: 'تقييم فوري للوقائع وإفادة أولية بخطوات العمل',
      privacyTitle: 'السرية المهنية وحماية البيانات',
      privacyDesc: 'جميع المعلومات المقدمة تخضع لسرية المهنة القانونية',
    },
    services: {
      eyebrow: 'مجالات الخدمة الرئيسية',
      title: 'ثلاثة مسارات قانونية محورية، وطريق واضح للحل.',
      desc: 'معالجة النزاعات الدولية الأكثر شيوعاً: تدقيق المستندات، وتتبع الأصول، والتفاوض الحازم، والتقاضي أو التنفيذ الجبري.',
      tradeNum: '01 / التجارة الدولية',
      tradeTitle: 'نزاعات التجارة الدولية والعقود',
      tradeDesc: 'معالجة نزاعات الشحن، وخطابات الاعتماد، والتخلف عن السداد، والإخلال بعقود التوريد.',
      tradeItems: [
        'تأخر أو امتناع المشترين عن سداد الفواتير',
        'مراجعة عقود التوزيع والوكالات التجارية الدولية',
        'نزاعات الجمارك، وأضرار الشحن البحري، ومشاكل الجودة',
        'كشف الاحتيال التجاري والتدابير الاحترازية العاجلة',
      ],
      tradeLink: 'خدمات نزاعات التجارة ←',
      recoveryNum: '02 / التحصيل والتقاضي',
      recoveryTitle: 'التقاضي وتحصيل الديون والإنفاذ',
      recoveryDesc: 'تتبع أموال المدينين بالخارج، وتنفيذ الأحكام القضائية وقرارات التحكيم الأجنبية.',
      recoveryItems: [
        'تحصيل مستحقات الشركات لدى العملاء الأجانب',
        'التحري عن الأصول وتتبع الحسابات في الخارج',
        'الاعتراف بالأحكام وقرارات التحكيم وإنفاذها دولياً',
        'إجراءات الحجز التحفظي والإفلاس التجاري',
      ],
      recoveryLink: 'خدمات التحصيل القضائي ←',
      legacyNum: '03 / التركات وحماية الأصول',
      legacyTitle: 'الميراث والتركات الدولية والأصول',
      legacyDesc: 'إدارة التركات العابرة للحدود، وتسجيل العقارات وتوزيع الحصص والأسهم المصرفية.',
      legacyItems: [
        'حصر التركات الدولية وتقسيم الأموال عبر عدة دول',
        'نقل ملكية العقارات والأسهم والودائع في الخارج',
        'التصديق الدبلوماسي وصحة الوصايا الأجنبية',
        'الامتثال لضوابط الصرف الأجنبي والضرائب العقارية',
      ],
      legacyLink: 'خدمات التركات والأصول ←',
      ctaText: 'لست متأكداً من المسار المناسب؟ شاركنا وقائع نزاعك وسنحدد لك المنفذ القانوني الملائم.',
      ctaBtn: 'إرسال بيانات النزاع ←',
    },
    process: {
      eyebrow: 'من الاستشارة إلى التنفيذ',
      title: 'توضيح الوقائع أولاً، ثم المضي قدماً بخطى ثابتة.',
      desc: 'مصمم خصيصاً للقضايا المعقدة عبر الحدود وفروق التوقيت والقوانين الأجنبية.',
      step1Num: '01',
      step1Title: 'الاستشارة والتقييم الأولي',
      step1Desc: 'إرسال التفاصيل الأساسية لحصر الأطراف، والمبالغ، والمخاطر المباشرة.',
      step2Num: '02',
      step2Title: 'فحص الأدلة والاختصاص القضائي',
      step2Desc: 'تحديد مدد التقادم، وأماكن الأصول، وأفضل المحاكم أو مراكز التحكيم الملائمة.',
      step3Num: '03',
      step3Title: 'وضع الاستراتيجية والبدء بالتنفيذ',
      step3Desc: 'إرسال الإخطارات القانونية، أو طلب الحجز التحفظي، أو رفع الدعوى القضائية مع وضوح كامل للتكاليف.',
    },
    stats: {
      stat1Num: '30+',
      stat1Label: 'دولة ومنطقة مغطاة',
      stat2Num: '3',
      stat2Label: 'مجالات قانونية متخصصة',
      stat3Num: '24 ساعة',
      stat3Label: 'التزام بالرد والتقييم',
      stat4Num: '4',
      stat4Label: 'لغات عمل: عربي / صيني / إنجليزي / إسباني',
    },
    cases: {
      eyebrow: 'نماذج وقضايا',
      title: 'نتعامل مع التحديات الحقيقية للأعمال الدولية.',
      desc: 'سيناريوهات عملية توضح مسارات التحرك القانوني. تبدأ كل قضية بتقييم سري وشامل.',
      pathLabel: 'مسار الإجراءات',
      soonBadge: 'ملخص دراسة الحالة قريباً',
      btnConsult: 'استشارة لقضية مماثلة ←',
      card1Tag: 'تجارة دولية',
      card1Title: 'المشتري الأجنبي استلم البضاعة ورفض سداد المستحقات',
      card1Desc: 'تم شحن وتسليم البضائع بالكامل، لكن المشتري يماطل بحجج تقلب العملة أو عيوب غير حقيقية.',
      card1Path: 'تدقيق المستندات → إنذار قانوني وتفاوض → تحكيم أو تقاضٍ محلي → حجز وتنفيذ',
      card2Tag: 'تحصيل ديون',
      card2Title: 'صدور حكم لصالحنا والمدين قام بتهريب أمواله',
      card2Desc: 'وجود حكم قضائي أو قرار تحكيم سارٍ، بينما المدين ينقل أصوله لشركات أوفشور أو يختفي.',
      card2Path: 'تحري وتتبع دولي للأصول → حجز تحفظي → دعوى نفاذ الحكم → سداد المستحقات',
      card3Tag: 'تركات وميراث',
      card3Title: 'وفاة المورث بالخارج وتوزع التركة بين بلدين',
      card3Desc: 'الورثة بحاجة لنقل ملكية عقارات وأسهم وأرصدة بنكية خارجية وفق أنظمة قضائية متباينة.',
      card3Path: 'تصديق الوثائق الدولية → تعيين مدير للتركة → تسوية الضرائب → تحويل الحصص للورثة',
    },
    global: {
      eyebrow: 'شبكتنا الدولية',
      title: 'حيثما تكون مصالح موكلينا، تمتد شبكتنا القانونية.',
      desc: 'من خلال الشراكات مع مكاتب المحاماة المرخصة محلياً، نغطي أهم الأسواق والمراكز المالية والتجارية الدولية.',
      regions: ['الولايات المتحدة', 'كندا', 'أستراليا', 'نيوزيلندا', 'سنغافورة', 'المملكة المتحدة', 'ألمانيا', 'فرنسا', 'اليابان', 'كوريا الجنوبية', 'الإمارات', 'السعودية', 'تايلاند', 'فيتنام', 'ماليزيا', 'إندونيسيا', 'هونغ كونغ', 'ماكاو', 'البرازيل', 'المكسيك'],
      note: 'تغطي شبكتنا أكثر من 30 دولة ومنطقة. إذا لم تكن دولتك مدرجة، تفضل بطلب استشارة لتقييم المسار القانوني المتاح.',
      consultBtn: 'طلب استشارة ←',
    },
    team: {
      eyebrow: 'فريق العمل',
      title: 'خبرة عميقة في القوانين الصينية والأنظمة الدولية.',
      desc: 'يتألف فريقنا الأساسي من محامين مرخصين متخصصين في النزاعات العابرة للحدود، بالتنسيق مع شركائنا المرخصين بالخارج.',
      card1Role: 'النزاعات التجارية الدولية',
      card1Title: 'تسوية النزاعات العابرة للحدود',
      card1Desc: 'عقود التجارة الدولية، والتقاضي والتحكيم التجاري، وصياغة شروط تسوية المنازعات.',
      card1List: ['محامون مرخصون', 'عمل احترافي متعدد اللغات'],
      card1Note: 'السير الذاتية قيد التحديث.',
      card2Role: 'التحصيل والتنفيذ القضائي',
      card2Title: 'التحصيل والإنفاذ',
      card2Desc: 'تحصيل الديون الدولية، وتتبع الأصول في الصين والخارج، وتنفيذ الأحكام القضائية.',
      card2List: ['خبرة متقدمة في تتبع الأصول', 'تعاون مع محامي التنفيذ الأجانب'],
      card2Note: 'السير الذاتية قيد التحديث.',
      card3Role: 'الميراث والتركات العائلية',
      card3Title: 'التركات والأصول',
      card3Desc: 'حصر الميراث الدولي، وصحة الوصايا، وتسوية نزاعات الشركات العائلية.',
      card3List: ['إدارة التركات متعددة الاختصاصات', 'مراعاة الخصوصية العائلية'],
      card3Note: 'السير الذاتية قيد التحديث.',
      card4Role: 'الشركاء الدوليون',
      card4Title: 'شبكة الشركاء القانونيين عالمياً',
      card4Desc: 'مكاتب محاماة مرخصة في أكثر من 30 دولة يتم تعيينها وفقاً لمتطلبات كل نزاع.',
      card4List: ['معايير اختيار ومطابقة صارمة', 'امتثال كامل للقوانين المحلية والتنفيذ المباشر'],
      card4Note: 'دليل الشركاء قيد التحديث.',
    },
    whyTrust: {
      eyebrow: 'لماذا يثق بنا الموكلون',
      title: 'المهنية، الشفافية، والأمان — الركائز الأساسية لخدماتنا القانونية الدولية.',
      card1Title: 'السرية التامة',
      card1Desc: 'المعلومات المقدمة محمية بموجب واجب السرية المهنية وتخضع لأعلى معايير حماية البيانات.',
      card2Title: 'التقييم أولاً، ثم التنفيذ',
      card2Desc: 'نوضح الخيارات المتاحة والأدلة المطلوبة مسبقاً دون دفع الموكل لإجراءات غير مجدية.',
      card3Title: 'شفافية ومصداقية التقييم',
      card3Desc: 'نقدم تحليلاً موضوعياً للفرص والمخاطر. النتائج تعتمد على الأدلة والقوانين، ولا نطلق وعوداً غير مسؤولة.',
      card4Title: 'الامتثال القانوني العابر للحدود',
      card4Desc: 'تتم الإجراءات الخارجية بالتنسيق الصارم مع مكاتب المحاماة المرخصة محلياً داخل اختصاصها.',
      statementLabel: 'إفادة ممارسة المهنة: ',
      statementText: 'يمارس مكتب شينيوان المحاماة في الصين؛ وتتم الإجراءات بالخارج بالتعاون مع محامين مرخصين محلياً.',
    },
    faq: {
      eyebrow: 'الأسئلة الشائعة',
      title: 'إجابات على استفساراتكم',
      desc: 'إجابات مباشرة على أكثر الأسئلة شيوعاً حول قضايا النزاعات الدولية.',
      items: [
        { q: 'متى سأتلقى رداً بعد إرسال القضية؟', a: 'نلتزم بتقديم الإفادة الأولى وتحديد موعد الاستشارة خلال 24 ساعة.' },
        { q: 'هل يمكنني إرسال استفساري قبل اكتمال كافة الوثائق؟', a: 'نعم. يكفي تقديم ملخص الوقائع والمبالغ المطالب بها لتقييم المسار القانوني المبدئي.' },
        { q: 'هل هذه الاستشارة تمثل مشورة قانونية نهائية؟', a: 'لا. التقييم المبدئي يهدف لتشخيص الموقف وتحديد المسار ولا ينشئ عقد توكيل رسمي.' },
        { q: 'هل يمكنني التواصل المباشر عبر WeChat؟', a: 'نعم. يمكنكم مراسلة ShenyuanLegal عبر ويشات للأمور العاجلة.' },
      ],
      ctaTitle: 'نزاعك التجاري الدولي يستحق بداية واضحة وموثوقة.',
      ctaDesc: 'أرسل تفاصيل نزاعك وسنقيم المدد القانونية، والأدلة، وفرص التنفيذ بمهنية وموضوعية.',
      ctaBtn: 'استشارة قانونية مجانية ←',
    },
  },

  es: {
    hero: {
      eyebrow: 'Resolución de disputas transfronterizas y protección de activos familiares',
      title1: 'Disputas transfronterizas, ',
      titleHighlight: 'ejecución global.',
      desc: 'El Bufete de Abogados Internacional Shenyuan asiste a empresas y familias en litigios comerciales, recuperación de créditos y gestión de herencias internacionales — comunicándonos en su idioma y ejecutando localmente a través de nuestra red de firmas asociadas.',
      ctaPrimary: 'Consulta legal gratuita →',
      ctaSecondary: 'Ver áreas de práctica',
      noteLang: 'Comunicación multilingüe (Español / Chino / Inglés)',
      noteJurisdictions: 'Cobertura en más de 30 países y regiones',
      noteAssess: 'Evaluar primero, actuar con certeza',
    },
    intake: {
      title: 'Cuéntenos su caso',
      desc: 'Envíe los detalles esenciales. Evaluaremos el tipo de asunto, la jurisdicción y las acciones recomendadas en 24 horas.',
      wechatTitle: 'Contacto por WeChat',
      wechatDesc: 'Ideal para consultas urgentes o coordinación en tiempo real.',
      wechatId: 'ID: ShenyuanLegal',
      fieldName: 'Su Nombre',
      placeholderName: 'Ej: Sra. García / Sr. Rodríguez',
      fieldEmail: 'Correo electrónico (opcional)',
      placeholderEmail: 'Para lista de verificación y notas legales',
      fieldMatter: 'Tipo de Asunto',
      matterOptions: [
        { value: '国际贸易争议', label: 'Disputas de Comercio Internacional' },
        { value: '诉讼与债务追收', label: 'Litigios y Cobranza de Créditos' },
        { value: '继承与家族资产纠纷', label: 'Herencias y Patrimonio Familiar' },
        { value: '不确定，希望先沟通', label: 'No estoy seguro, requiero evaluación' },
      ],
      fieldPhone: 'Teléfono / WhatsApp',
      placeholderPhone: 'Número local o WhatsApp',
      fieldSummary: 'Breve descripción de los hechos',
      placeholderSummary: 'Ej: El comprador extranjero recibió la mercancía pero retiene el pago final desde hace 4 meses.',
      consentPre: 'He leído y acepto el',
      privacyLink: 'Aviso de Privacidad',
      consentPost: ' y autorizo el uso de estos datos para la consulta legal.',
      viewPrivacy: 'Ver aviso de privacidad',
      btnSubmitting: 'Enviando...',
      btnSubmit: 'Enviar para obtener orientación legal →',
      formNote: 'El envío de este formulario no constituye por sí mismo una relación abogado-cliente formal. Por favor no incluya datos bancarios confidenciales aquí.',
    },
    trust: {
      bilingualTitle: 'Equipo Multilingüe',
      bilingualDesc: 'Los hechos explicados con claridad, con rigurosa precisión legal',
      globalTitle: 'Red Global de Litigio',
      globalDesc: 'Abogados locales habilitados en más de 30 países',
      responseTitle: 'Compromiso de Respuesta en 24h',
      responseDesc: 'Evaluación rápida de viabilidad procesal y contacto directo',
      privacyTitle: 'Confidencialidad Absoluta',
      privacyDesc: 'La información enviada está protegida bajo secreto profesional',
    },
    services: {
      eyebrow: 'Práctica Principal',
      title: 'Tres áreas estratégicas, un camino claro hacia la resolución.',
      desc: 'Enfocados en los desafíos comerciales y patrimoniales más frecuentes, evaluando la vía de negociación, embargo preventivo, litigio o ejecución judicial.',
      tradeNum: '01 / COMERCIO',
      tradeTitle: 'Disputas de comercio internacional',
      tradeDesc: 'Incumplimiento de contratos de compraventa, cartas de crédito y controversias aduaneras.',
      tradeItems: [
        'Facturas impagadas e incumplimiento de proveedores',
        'Contratos internacionales de distribución y agencia comercial',
        'Disputas de flete, daños a la carga y calidad de producto',
        'Detección de fraude comercial y medidas cautelares urgentes',
      ],
      tradeLink: 'Servicios de comercio internacional →',
      recoveryNum: '02 / COBRANZA',
      recoveryTitle: 'Litigios y cobranza de deudas',
      recoveryDesc: 'Localización de activos deudores y homologación judicial de sentencias extranjeras.',
      recoveryItems: [
        'Recuperación de deudas comerciales en el extranjero',
        'Investigación y rastreo patrimonial transfronterizo',
        'Exequátur y ejecución de laudos arbitrales y sentencias',
        'Procedimientos concursales y fraudes corporativos',
      ],
      recoveryLink: 'Servicios de litigio y cobranza →',
      legacyNum: '03 / PATRIMONIO',
      legacyTitle: 'Herencias y patrimonio familiar',
      legacyDesc: 'Sucesiones internacionales, partición de bienes raíces, cuentas offshore y empresas.',
      legacyItems: [
        'Juicios sucesorios y partición de herencias en múltiples países',
        'Transmisión de inmuebles, acciones y depósitos bancarios',
        'Validez de testamentos otorgados en el extranjero y apostilla',
        'Cumplimiento tributario sucesorio y control cambiario',
      ],
      legacyLink: 'Servicios de sucesiones y patrimonio →',
      ctaText: '¿No está seguro de qué categoría corresponde? Envíenos su caso y le indicaremos la ruta adecuada.',
      ctaBtn: 'Enviar información de su caso →',
    },
    process: {
      eyebrow: 'De la consulta a la acción',
      title: 'Aclarar los hechos primero, avanzar con firmeza procesal.',
      desc: 'Estructurado para asuntos transfronterizos complejos con diferentes zonas horarias y sistemas jurídicos.',
      step1Num: '01',
      step1Title: 'Consulta Inicial y Registro',
      step1Desc: 'Evaluamos las partes involucradas, importes reclamados, cronología y riesgos inmediatos.',
      step2Num: '02',
      step2Title: 'Auditoría de Pruebas y Jurisdicción',
      step2Desc: 'Identificamos plazos de prescripción, solvencia del deudor y los tribunales más convenientes.',
      step3Num: '03',
      step3Title: 'Estrategia y Ejecución Directa',
      step3Desc: 'Requerimientos notariales, embargos precautorios o demandas formales con honorarios transparentes.',
    },
    stats: {
      stat1Num: '30+',
      stat1Label: 'países y regiones cubiertas',
      stat2Num: '3',
      stat2Label: 'líneas de práctica legal',
      stat3Num: '24h',
      stat3Label: 'tiempo de primera respuesta',
      stat4Num: '4',
      stat4Label: 'idiomas: Español / Chino / Inglés / Árabe',
    },
    cases: {
      eyebrow: 'Casos y resultados',
      title: 'Resolvemos los problemas reales de los negocios internacionales.',
      desc: 'Escenarios habituales y estrategias implementadas. Cada asunto comienza con un diagnóstico confidencial.',
      pathLabel: 'Ruta procesal',
      soonBadge: 'Estudio de caso anonimizado en preparación',
      btnConsult: 'Consulta para un caso similar →',
      card1Tag: 'COMERCIO',
      card1Title: 'Comprador recibió la mercancía pero rehúsa el pago final',
      card1Desc: 'Bienes entregados conforme a contrato, pero el cliente alega fluctuaciones de tipo de cambio o defectos inexistentes.',
      card1Path: 'Revisión de pruebas → Requerimiento y negociación → Litigio / Arbitraje → Ejecución forzosa',
      card2Tag: 'COBRANZA',
      card2Title: 'Sentencia favorable obtenida, pero el deudor ocultó bienes',
      card2Desc: 'Sentencia o laudo firme dictado, pero el demandado desvió activos a entidades interpuestas.',
      card2Path: 'Rastreo internacional de activos → Medida cautelar de embargo → Exequátur → Cobro efectivo',
      card3Tag: 'HERENCIAS',
      card3Title: 'Fallecimiento en el extranjero con herencia en dos países',
      card3Desc: 'Los herederos deben adjudicarse inmuebles, participaciones sociales y cuentas en bancos extranjeros.',
      card3Path: 'Apostilla y traducción jurada → Declaratoria de herederos → Liquidación fiscal → Adjudicación',
    },
    global: {
      eyebrow: 'Red Global de Litigio',
      title: 'Donde están nuestros clientes, está nuestra red procesal.',
      desc: 'A través de asociaciones con firmas jurídicas locales habilitadas, cubrimos los principales mercados donde operan empresas multinacionales.',
      regions: ['Estados Unidos', 'Canadá', 'Australia', 'Nueva Zelanda', 'Singapur', 'Reino Unido', 'Alemania', 'Francia', 'Japón', 'Corea del Sur', 'Emiratos Árabes', 'Arabia Saudita', 'Tailandia', 'Vietnam', 'Malasia', 'Indonesia', 'Hong Kong', 'Macao', 'Brasil', 'México'],
      note: 'Nuestra red cubre más de 30 países y regiones. Si su país no figura, envíe su caso para una evaluación de viabilidad local.',
      consultBtn: 'Consultar →',
    },
    team: {
      eyebrow: 'Equipo de Abogados',
      title: 'Dominio de las leyes chinas y solidez en normativas internacionales.',
      desc: 'Nuestro núcleo directivo está compuesto por abogados habilitados en China especializados en litigio internacional, actuando en conjunto con firmas locales en destino.',
      card1Role: 'DISPUTAS TRANSFRONTERIZAS',
      card1Title: 'Litigios y Arbitraje Comercial',
      card1Desc: 'Controversias de comercio internacional, litigios multijurisdiccionales y redacción de cláusulas arbitrales.',
      card1List: ['Abogados habilitados en China', 'Práctica bilingüe y multilingüe'],
      card1Note: 'Perfiles de abogados en actualización.',
      card2Role: 'COBRANZA Y EJECUCIÓN',
      card2Title: 'Recuperación y Ejecución',
      card2Desc: 'Cobro judicial internacional, rastreo de activos en origen y destino, y ejecución forzosa de fallos.',
      card2List: ['Especialistas en auditoría patrimonial', 'Coordinación con procuradores locales'],
      card2Note: 'Perfiles de abogados en actualización.',
      card3Role: 'HERENCIAS Y FAMILIA',
      card3Title: 'Sucesiones y Patrimonio Familiar',
      card3Desc: 'Herencias internacionales, impugnación de testamentos y sucesión de empresas familiares.',
      card3List: ['Articulación de trámites en múltiples países', 'Gestión cercana y confidencial'],
      card3Note: 'Perfiles de abogados en actualización.',
      card4Role: 'SOCIOS GLOBALES',
      card4Title: 'Red Internacional de Despachos',
      card4Desc: 'Firmas locales en más de 30 países seleccionadas según la materia jurídica requerida.',
      card4List: ['Filtro riguroso caso por caso', 'Ejecución conforme al derecho procesal local'],
      card4Note: 'Directorio de despachos en actualización.',
    },
    whyTrust: {
      eyebrow: 'Por Qué Confiar en Nosotros',
      title: 'Rigor técnico, certidumbre y confidencialidad en litigios internacionales.',
      card1Title: 'Compromiso de Confidencialidad',
      card1Desc: 'La información del caso está blindada bajo secreto profesional conforme a las normas de privacidad PIPL y RGPD.',
      card2Title: 'Diagnóstico Previo Sin Compromiso',
      card2Desc: 'Evaluamos plazos, solvencia y solidez probatoria sin inducir a procedimientos judiciales innecesarios.',
      card3Title: 'Evaluación Objetiva y Rigurosa',
      card3Desc: 'Exponemos con honestidad las probabilidades y riesgos. Los resultados procesales dependen de los hechos y la ley.',
      card4Title: 'Cumplimiento Normativo Transfronterizo',
      card4Desc: 'Las actuaciones judiciales en el extranjero se canalizan exclusivamente a través de abogados locales colegiados.',
      statementLabel: 'Declaración Profesional: ',
      statementText: 'Bufete Shenyuan ejerce la abogacía en China continental; los procedimientos en el extranjero se tramitan con firmas asociadas locales.',
    },
    faq: {
      eyebrow: 'Antes de Comenzar',
      title: 'Preguntas Frecuentes',
      desc: 'Aclaraciones directas sobre el inicio de una reclamación o defensa jurídica internacional.',
      items: [
        { q: '¿Cuánto tardan en responder?', a: 'Nos comprometemos a una primera valoración y contacto en un plazo máximo de 24 horas.' },
        { q: '¿Puedo enviar mi caso antes de reunir todos los documentos?', a: 'Sí. Una relación cronológica y los importes adeudados son suficientes para el diagnóstico legal inicial.' },
        { q: '¿Esta consulta inicial constituye un dictamen formal?', a: 'No. El análisis preliminar determina la viabilidad y próximos pasos, sin constituir formalmente una relación cliente-abogado.' },
        { q: '¿Es posible contactar por WeChat?', a: 'Sí. Puede contactar directamente con ShenyuanLegal para temas urgentes.' },
      ],
      ctaTitle: 'Su conflicto internacional merece un punto de partida claro y en su idioma.',
      ctaDesc: 'Envíenos los antecedentes. Evaluaremos plazos de prescripción, solvencia del deudor y vías de cobro con total objetividad.',
      ctaBtn: 'Consulta Legal Gratuita →',
    },
  },
}
