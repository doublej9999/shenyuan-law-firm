<template>
  <div class="home-container">
    <!-- 01 HERO -->
    <section class="hero">
      <div class="wrap hero-grid">
        <div class="hero-copy">
          <div class="eyebrow">
            {{ isEn ? 'Cross-border dispute resolution & family asset protection' : '跨境争议解决与家族资产保护' }}
          </div>
          <h1>
            <span>{{ isEn ? 'Cross-border disputes, ' : '跨境争议，' }}</span>
            <span class="highlight">{{ isEn ? 'executed globally.' : '全球落地执行。' }}</span>
          </h1>
          <p>
            {{ isEn 
              ? 'Shenyuan International helps Chinese businesses and families resolve international trade disputes, recover cross-border debts, and protect inherited family assets — understood in your language, executed through a global network of local counsel.' 
              : '深远国际律师事务所为中国企业与家庭提供国际贸易争议、跨境债务追收、继承与家族资产法律服务——用中文理解你的处境，用全球合作律所网络在当地落地执行。' }}
          </p>
          <div class="hero-actions">
            <a class="button button-primary" href="#intake" @click.prevent="scrollToIntake">
              {{ isEn ? 'Free legal consultation →' : '免费法律咨询 →' }}
            </a>
            <NuxtLink class="button button-outline" :to="isEn ? '/en/services' : '/services'">
              {{ isEn ? 'Explore services' : '查看服务范围' }}
            </NuxtLink>
          </div>
          <div class="hero-notes">
            <span><i></i><span>{{ isEn ? 'Chinese / English' : '中英双语沟通' }}</span></span>
            <span><i></i><span>{{ isEn ? 'Coverage across 30+ jurisdictions' : '覆盖 30+ 国家与地区' }}</span></span>
            <span><i></i><span>{{ isEn ? 'Assess first, act clearly' : '先评估，再行动' }}</span></span>
          </div>
        </div>

        <form class="intake-card" id="intake" @submit.prevent="handleIntakeSubmit" novalidate>
          <h2>{{ isEn ? 'Tell us what happened' : '先说说发生了什么' }}</h2>
          <p>
            {{ isEn 
              ? 'Share the basics. We will assess the matter type, jurisdiction, and next step, and respond within 24 hours. For urgent matters, message us on WeChat and mark it urgent.' 
              : '留下基本信息，我们会先判断事项类型、地域与下一步，24 小时内回复。紧急情况建议直接微信联系并注明“紧急”。' }}
          </p>
          <div class="contact-options">
            <img class="qr-img" src="/wechat-qrcode.png" alt="WeChat QR code" loading="lazy" decoding="async">
            <div class="wechat-copy">
              <strong>{{ isEn ? 'Quick WeChat consult' : '微信快速咨询' }}</strong>
              <p>{{ isEn ? 'Useful for urgent, time-zone sensitive, or quick first-contact questions.' : '适合紧急、跨时区或希望先简单确认方向的咨询。' }}</p>
              <span class="wechat-id">{{ isEn ? 'WeChat: ShenyuanLegal' : '微信号：ShenyuanLegal' }}</span>
            </div>
          </div>

          <div class="intake-grid">
            <div class="field">
              <label for="name">{{ isEn ? 'Name' : '称呼' }}</label>
              <input id="name" v-model="form.name" required :placeholder="isEn ? 'e.g. Ms. Wang' : '例如：王女士'">
            </div>
            <div class="field">
              <label for="email">{{ isEn ? 'Email (optional)' : '邮箱（选填）' }}</label>
              <input id="email" v-model="form.email" type="email" :placeholder="isEn ? 'Optional, for checklist' : '选填，用于接收材料清单'">
            </div>
            <div class="field">
              <label for="matter">{{ isEn ? 'Matter type' : '事项类型' }}</label>
              <select id="matter" v-model="form.matter" required>
                <option value="国际贸易争议">{{ isEn ? 'International trade dispute' : '国际贸易争议' }}</option>
                <option value="诉讼与债务追收">{{ isEn ? 'Litigation & debt recovery' : '诉讼与债务追收' }}</option>
                <option value="继承与家族资产纠纷">{{ isEn ? 'Inheritance & family assets' : '继承与家族资产纠纷' }}</option>
                <option value="不确定，希望先沟通">{{ isEn ? 'Not sure yet' : '不确定，希望先沟通' }}</option>
              </select>
            </div>
            <div class="field">
              <label for="phone">{{ isEn ? 'Phone' : '联系电话' }}</label>
              <input id="phone" v-model="form.phone" type="tel" required :placeholder="isEn ? 'Phone / WhatsApp' : '手机或固定电话，用于回电联系'">
            </div>
            <div class="field full">
              <label for="summary">{{ isEn ? 'Briefly describe the issue' : '一句话描述问题' }}</label>
              <textarea id="summary" v-model="form.summary" required :placeholder="isEn ? 'e.g. Overseas buyer received goods but has not paid for 4 months.' : '例如：海外客户已收货，但 4 个月未支付尾款。'"></textarea>
            </div>
          </div>

          <label class="consent" for="consent">
            <input type="checkbox" id="consent" v-model="form.consent" required>
            <span>
              <template v-if="isEn">
                I have read and agree to the <a href="#privacy" class="privacy-link" @click.prevent.stop="privacyModalOpen = true">Privacy Notice</a> and consent to this information being used for consultation.
              </template>
              <template v-else>
                我已阅读并同意<a href="#privacy" class="privacy-link" @click.prevent.stop="privacyModalOpen = true">《隐私说明》</a>，同意提交以上信息用于咨询沟通。
              </template>
            </span>
          </label>

          <div class="privacy-trigger-row">
            <button type="button" class="privacy-trigger-btn" @click="privacyModalOpen = true">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="16" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12.01" y2="8"></line>
              </svg>
              <span>{{ isEn ? 'View privacy notice' : '查看隐私说明' }}</span>
            </button>
          </div>

          <button class="button button-primary" type="submit" :disabled="submitting">
            {{ submitting 
              ? (isEn ? 'Submitting...' : '提交中...') 
              : (isEn ? 'Submit for next-step guidance →' : '提交，获取下一步建议 →') }}
          </button>
          <p class="form-note">
            {{ isEn 
              ? 'Submitting does not create an attorney-client relationship. Please do not include sensitive identifiers or bank details.' 
              : '提交不代表建立委托关系。请勿在此处填写身份证号、银行账号等敏感信息。' }}
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
            <strong>{{ isEn ? 'Bilingual team' : '中英双语团队' }}</strong>
            <span>{{ isEn ? 'Facts in Chinese, precision in English' : '中文讲清事实，英文保留法律精度' }}</span>
          </div>
        </div>
        <div class="trust-item">
          <i></i>
          <div>
            <strong>{{ isEn ? 'Global network' : '全球协作网络' }}</strong>
            <span>{{ isEn ? 'Local counsel in 30+ jurisdictions' : '30+ 国家与地区当地执业律所' }}</span>
          </div>
        </div>
        <div class="trust-item">
          <i></i>
          <div>
            <strong>{{ isEn ? '24-hour response' : '24 小时首响承诺' }}</strong>
            <span>{{ isEn ? 'We get back to you quickly' : '收到咨询后尽快安排沟通' }}</span>
          </div>
        </div>
        <div class="trust-item">
          <i></i>
          <div>
            <strong>{{ isEn ? 'Privacy & confidentiality' : '隐私与保密' }}</strong>
            <span>{{ isEn ? 'Information used solely for assessment' : '咨询信息仅用于评估与沟通' }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 03 核心服务 -->
    <section class="section service-section" id="services">
      <div class="wrap">
        <div class="section-head">
          <div class="eyebrow">{{ isEn ? 'Core practice' : '核心业务' }}</div>
          <h2>{{ isEn ? 'Three core practice lines, one clear path forward.' : '三类高频跨境事项，一条清晰的解决路径。' }}</h2>
          <p>{{ isEn 
            ? 'Built around the issues Chinese businesses and families face abroad — we assess the facts and evidence, then map negotiation, recovery, litigation, or enforcement.' 
            : '围绕中国企业与家庭在海外最常遇到的问题，从欠款事实与证据入手，判断协商、追收、诉讼或执行路径。' }}</p>
        </div>
        <div class="service-grid">
          <article class="service-card">
            <div class="service-number">01 / TRADE</div>
            <h3>{{ isEn ? 'International trade disputes' : '国际贸易争议' }}</h3>
            <p>{{ isEn ? 'For disputes involving performance, payment, agencies, distribution, and cross-border contracts.' : '处理交易履行、货款、代理与跨境合同之间的纠纷。' }}</p>
            <ul class="service-list">
              <li>{{ isEn ? 'Unpaid invoices / supplier breach' : '拖欠货款 / 供应商违约' }}</li>
              <li>{{ isEn ? 'Agency, distribution, contract review' : '代理、经销、跨境合同审查' }}</li>
              <li>{{ isEn ? 'Customs, logistics, quality issues' : '海关、物流、质量争议' }}</li>
              <li>{{ isEn ? 'Trade fraud identification & response' : '国际贸易诈骗识别与应对' }}</li>
            </ul>
            <NuxtLink class="service-link" :to="isEn ? '/en/services' : '/services'">
              {{ isEn ? 'Trade dispute services →' : '了解贸易争议服务 →' }}
            </NuxtLink>
          </article>

          <article class="service-card">
            <div class="service-number">02 / RECOVERY</div>
            <h3>{{ isEn ? 'Litigation & debt recovery' : '诉讼与债务追收' }}</h3>
            <p>{{ isEn ? 'Assess recovery, litigation, and enforcement options from the facts and asset trail.' : '从欠款事实与资产线索出发，判断追收、诉讼或执行路径。' }}</p>
            <ul class="service-list">
              <li>{{ isEn ? 'Overseas customer debt recovery' : '海外客户欠款追收' }}</li>
              <li>{{ isEn ? 'Asset tracing in China and abroad' : '中国境内与海外资产调查' }}</li>
              <li>{{ isEn ? 'Cross-border judgment & award enforcement' : '判决、仲裁裁决跨境执行' }}</li>
              <li>{{ isEn ? 'Commercial fraud investigation' : '商业欺诈调查' }}</li>
            </ul>
            <NuxtLink class="service-link" :to="isEn ? '/en/services' : '/services'">
              {{ isEn ? 'Recovery services →' : '了解追收服务 →' }}
            </NuxtLink>
          </article>

          <article class="service-card">
            <div class="service-number">03 / LEGACY</div>
            <h3>{{ isEn ? 'Inheritance & family assets' : '继承与家族资产纠纷' }}</h3>
            <p>{{ isEn ? 'Navigate multi-jurisdiction inheritance, property, equity, deposits, and family conflicts.' : '协助梳理大陆与海外多地的继承、房产、股权与家族争议。' }}</p>
            <ul class="service-list">
              <li>{{ isEn ? 'Mainland China and multi-country inheritance' : '中国大陆与海外多地继承' }}</li>
              <li>{{ isEn ? 'Property, equity, and deposit inheritance' : '房产、股权、存款继承' }}</li>
              <li>{{ isEn ? 'Wills and estate division' : '遗嘱效力与遗产分割' }}</li>
              <li>{{ isEn ? 'Missing or disputed family members' : '家族成员失联或争议' }}</li>
            </ul>
            <NuxtLink class="service-link" :to="isEn ? '/en/services' : '/services'">
              {{ isEn ? 'Legacy services →' : '了解继承服务 →' }}
            </NuxtLink>
          </article>
        </div>

        <div class="service-cta-row">
          <p>{{ isEn ? 'Not sure which category fits? Share your situation and we will help you find the right entry point.' : '不确定属于哪一类？先提交你的情况，我们帮你判断入口。' }}</p>
          <a class="button button-primary" href="#intake" @click.prevent="scrollToIntake">
            {{ isEn ? 'Share your case →' : '提交案件信息 →' }}
          </a>
        </div>
      </div>
    </section>

    <!-- 04 处理路径 -->
    <section class="section process-section" id="process">
      <div class="wrap">
        <div class="section-head">
          <div class="eyebrow">{{ isEn ? 'From consultation to action' : '从咨询到行动' }}</div>
          <h2>{{ isEn ? 'Clarify the matter. Move forward with care.' : '先把问题说清，再把路径走稳。' }}</h2>
          <p>{{ isEn ? 'Built for complex matters across time zones, languages, and jurisdictions.' : '适合需要跨时区、双语沟通，或同时涉及中国大陆与海外法域的复杂事项。' }}</p>
        </div>
        <div class="process-grid">
          <div class="process-step">
            <span>01</span>
            <h3>{{ isEn ? 'Free consultation & intake' : '免费咨询建档' }}</h3>
            <p>{{ isEn ? 'Share the essentials via form or WeChat. We map the parties, amounts, timeline, and goals.' : '提交基本情况或微信联系，我们梳理人物、金额、时间线与目标。' }}</p>
          </div>
          <div class="process-step">
            <span>02</span>
            <h3>{{ isEn ? 'Facts, evidence & jurisdiction review' : '事实、证据与法域评估' }}</h3>
            <p>{{ isEn ? 'Identify timing, evidence, asset location, and potentially relevant jurisdictions.' : '初步识别时效、证据、资产位置与可能涉及的法域，判断可行路径。' }}</p>
          </div>
          <div class="process-step">
            <span>03</span>
            <h3>{{ isEn ? 'Strategy, engagement & execution' : '策略、报价与执行' }}</h3>
            <p>{{ isEn ? 'Define the strategy — negotiation, recovery, or litigation — with clear milestones and risk boundaries.' : '根据事项特点确定谈判、追收或诉讼策略，明确材料、风险与里程碑。' }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 05 数据成果 -->
    <section class="section stats-section" id="results">
      <div class="wrap">
        <div class="stat">
          <div class="num">30<em>+</em></div>
          <div class="label">{{ isEn ? 'jurisdictions covered' : '协作国家与地区' }}</div>
        </div>
        <div class="stat">
          <div class="num">3</div>
          <div class="label">{{ isEn ? 'core practice lines' : '大跨境业务线' }}</div>
        </div>
        <div class="stat">
          <div class="num">24<em>h</em></div>
          <div class="label">{{ isEn ? 'first-response commitment' : '咨询首响承诺' }}</div>
        </div>
        <div class="stat">
          <div class="num">2</div>
          <div class="label">{{ isEn ? 'languages: 中文 / English' : '种语言·中 / EN' }}</div>
        </div>
      </div>
    </section>

    <!-- 06 案例展示 -->
    <section class="section cases-section" id="cases">
      <div class="wrap">
        <div class="section-head">
          <div class="eyebrow">{{ isEn ? 'Cases & outcomes' : '案例与成果' }}</div>
          <h2>{{ isEn ? 'We handle the hard problems of real business.' : '我们处理的，都是真实生意里的难题。' }}</h2>
          <p>{{ isEn 
            ? 'Below are typical scenarios and the pathways we take. Anonymized case walkthroughs will be published as they are finalized. Every engagement starts with a free consultation.' 
            : '以下是典型情形与处理路径示例；脱敏案例复盘（已隐去身份信息）整理完成后将陆续发布。每一件案子，都从一次免费咨询开始。' }}</p>
        </div>
        <div class="cases-grid">
          <article class="case-card">
            <div class="case-tag">TRADE</div>
            <h3>{{ isEn ? 'Buyer received goods, refused final payment' : '海外客户收货后拖欠尾款' }}</h3>
            <p>{{ isEn ? 'Typical scenario: goods delivered, buyer delays payment for months citing quality, FX, or other reasons.' : '典型情形：货已交付，客户以质量问题、汇率波动等理由拖延付款数月。' }}</p>
            <div class="case-path">
              <b>{{ isEn ? 'Pathway' : '处理路径' }}</b>
              <span>{{ isEn ? 'Evidence review → demand & negotiation → litigation / arbitration → enforcement' : '证据梳理 → 律师函与协商 → 诉讼 / 仲裁 → 判决执行' }}</span>
            </div>
            <span class="soon-badge">{{ isEn ? 'Anonymized case study coming soon' : '脱敏案例复盘整理中' }}</span>
            <a class="button button-outline case-btn" href="#intake" @click.prevent="scrollToIntake">
              {{ isEn ? 'Free consultation →' : '类似案件，免费咨询 →' }}
            </a>
          </article>

          <article class="case-card">
            <div class="case-tag">RECOVERY</div>
            <h3>{{ isEn ? 'Won the judgment, still no payment' : '判决赢了，钱却拿不回来' }}</h3>
            <p>{{ isEn ? 'Typical scenario: a judgment or award exists in China or abroad, but the debtor has moved assets or disappeared.' : '典型情形：中国境内或境外已有生效判决 / 仲裁裁决，但债务人转移资产或下落不明。' }}</p>
            <div class="case-path">
              <b>{{ isEn ? 'Pathway' : '处理路径' }}</b>
              <span>{{ isEn ? 'Asset tracing → preservation orders → recognition & enforcement → settlement' : '资产调查 → 财产保全 → 承认与执行申请 → 执行和解' }}</span>
            </div>
            <span class="soon-badge">{{ isEn ? 'Anonymized case study coming soon' : '脱敏案例复盘整理中' }}</span>
            <a class="button button-outline case-btn" href="#intake" @click.prevent="scrollToIntake">
              {{ isEn ? 'Free consultation →' : '类似案件，免费咨询 →' }}
            </a>
          </article>

          <article class="case-card">
            <div class="case-tag">LEGACY</div>
            <h3>{{ isEn ? 'Relative passed away abroad, estate spans two countries' : '亲属在海外去世，遗产横跨两国' }}</h3>
            <p>{{ isEn ? 'Typical scenario: heirs in China must handle overseas property, deposits, and equity — with wills, probate, and FX compliance involved.' : '典型情形：继承人身在国内，需处理海外房产、存款与公司股权，涉及遗嘱、认证与外汇。' }}</p>
            <div class="case-path">
              <b>{{ isEn ? 'Pathway' : '处理路径' }}</b>
              <span>{{ isEn ? 'Notarization → probate → asset list & inheritance → compliant fund transfer' : '亲属关系与文件公证 → 遗嘱认证 → 资产清单与继承 → 资金合规汇回' }}</span>
            </div>
            <span class="soon-badge">{{ isEn ? 'Anonymized case study coming soon' : '脱敏案例复盘整理中' }}</span>
            <a class="button button-outline case-btn" href="#intake" @click.prevent="scrollToIntake">
              {{ isEn ? 'Free consultation →' : '类似案件，免费咨询 →' }}
            </a>
          </article>
        </div>
      </div>
    </section>

    <!-- 07 国家覆盖 -->
    <section class="section global-section" id="global">
      <div class="wrap">
        <div class="section-head">
          <div class="eyebrow">{{ isEn ? 'Global reach' : '全球网络' }}</div>
          <h2>{{ isEn ? 'Where our clients are, our network follows.' : '客户在哪里，协作网络就在哪里。' }}</h2>
          <p>{{ isEn 
            ? 'Through partnerships with locally licensed counsel, we cover the markets where Chinese businesses and overseas Chinese communities are concentrated. Every matter is assessed on its own facts.' 
            : '通过与当地执业律所的合作，覆盖中国企业出海与海外华人集中的主要市场。具体地区以当次评估为准，一案一议。' }}</p>
        </div>
        <div class="global-grid">
          <div class="region">{{ isEn ? 'United States' : '美国' }}</div>
          <div class="region">{{ isEn ? 'Canada' : '加拿大' }}</div>
          <div class="region">{{ isEn ? 'Australia' : '澳大利亚' }}</div>
          <div class="region">{{ isEn ? 'New Zealand' : '新西兰' }}</div>
          <div class="region">{{ isEn ? 'Singapore' : '新加坡' }}</div>
          <div class="region">{{ isEn ? 'United Kingdom' : '英国' }}</div>
          <div class="region">{{ isEn ? 'Germany' : '德国' }}</div>
          <div class="region">{{ isEn ? 'France' : '法国' }}</div>
          <div class="region">{{ isEn ? 'Japan' : '日本' }}</div>
          <div class="region">{{ isEn ? 'South Korea' : '韩国' }}</div>
          <div class="region">{{ isEn ? 'UAE' : '阿联酋' }}</div>
          <div class="region">{{ isEn ? 'Saudi Arabia' : '沙特' }}</div>
          <div class="region">{{ isEn ? 'Thailand' : '泰国' }}</div>
          <div class="region">{{ isEn ? 'Vietnam' : '越南' }}</div>
          <div class="region">{{ isEn ? 'Malaysia' : '马来西亚' }}</div>
          <div class="region">{{ isEn ? 'Indonesia' : '印尼' }}</div>
          <div class="region">{{ isEn ? 'Hong Kong' : '香港' }}</div>
          <div class="region">{{ isEn ? 'Macau' : '澳门' }}</div>
          <div class="region">{{ isEn ? 'Brazil' : '巴西' }}</div>
          <div class="region">{{ isEn ? 'Mexico' : '墨西哥' }}</div>
        </div>
        <div class="global-note">
          <i></i>
          <span>{{ isEn 
            ? 'Our partner network spans 30+ jurisdictions. Not on the list? Submit your matter and we will assess whether a viable local pathway exists.' 
            : '合作律所网络覆盖 30+ 国家与地区。未列出的地区，也欢迎先提交咨询，我们会判断当地是否有可落地路径。' }}</span>
          <a href="#intake" @click.prevent="scrollToIntake">{{ isEn ? 'Consult us →' : '提交咨询 →' }}</a>
        </div>
      </div>
    </section>

    <!-- 08 律师团队 -->
    <section class="section team-section" id="team">
      <div class="wrap">
        <div class="section-head">
          <div class="eyebrow">{{ isEn ? 'Our team' : '律师团队' }}</div>
          <h2>{{ isEn ? 'Trained in Chinese law, fluent in foreign rules.' : '懂中国法律，也懂海外规则。' }}</h2>
          <p>{{ isEn 
            ? 'Our core team consists of mainland China licensed lawyers focused on cross-border matters; foreign procedures are handled with locally licensed counsel to ensure procedural compliance at every step.' 
            : '团队以中国大陆执业律师为核心，专注跨境业务；境外程序通过与当地执业律所协作完成，确保每个环节程序合规。' }}</p>
        </div>
        <div class="team-grid">
          <div class="team-card">
            <div class="team-role">CROSS-BORDER DISPUTES</div>
            <h3>{{ isEn ? 'Cross-border disputes' : '跨境争议解决' }}</h3>
            <p>{{ isEn ? 'International trade and contract disputes, cross-border litigation and arbitration, and dispute resolution clause design.' : '国际贸易与合同争议、跨境诉讼与仲裁、争议解决条款设计。' }}</p>
            <ul class="team-list">
              <li>{{ isEn ? 'Licensed in mainland China' : '中国大陆执业律师' }}</li>
              <li>{{ isEn ? 'Bilingual practice (Chinese / English)' : '中英双语工作' }}</li>
            </ul>
            <p class="team-note">{{ isEn ? 'Team member profiles coming soon.' : '团队成员及详细简历更新中。' }}</p>
          </div>

          <div class="team-card">
            <div class="team-role">RECOVERY & ENFORCEMENT</div>
            <h3>{{ isEn ? 'Recovery & enforcement' : '追收与执行' }}</h3>
            <p>{{ isEn ? 'Cross-border debt recovery, asset tracing at home and abroad, and enforcement of judgments and awards.' : '跨境债务追收、境内与海外资产调查、判决与仲裁裁决执行。' }}</p>
            <ul class="team-list">
              <li>{{ isEn ? 'Specialized in China asset tracing' : '中国境内资产调查专长' }}</li>
              <li>{{ isEn ? 'Collaboration with overseas enforcement counsel' : '与海外执行律师协作' }}</li>
            </ul>
            <p class="team-note">{{ isEn ? 'Team member profiles coming soon.' : '团队成员及详细简历更新中。' }}</p>
          </div>

          <div class="team-card">
            <div class="team-role">INHERITANCE & FAMILY</div>
            <h3>{{ isEn ? 'Inheritance & family assets' : '继承与家族资产' }}</h3>
            <p>{{ isEn ? 'Cross-border inheritance, will planning and validity disputes, and family business succession.' : '跨境继承、遗嘱规划与效力争议、家族企业传承与纠纷。' }}</p>
            <ul class="team-list">
              <li>{{ isEn ? 'Multi-jurisdiction probate coordination' : '多法域继承程序衔接' }}</li>
              <li>{{ isEn ? 'Sensitive to family dynamics' : '照顾家庭沟通场景' }}</li>
            </ul>
            <p class="team-note">{{ isEn ? 'Team member profiles coming soon.' : '团队成员及详细简历更新中。' }}</p>
          </div>

          <div class="team-card">
            <div class="team-role">GLOBAL PARTNERS</div>
            <h3>{{ isEn ? 'Global partner network' : '全球合作律所网络' }}</h3>
            <p>{{ isEn ? 'Locally licensed law firms and collection partners in 30+ jurisdictions, matched by matter type and region.' : '覆盖 30+ 国家与地区的当地执业律所与追收机构，按案件类型与地区匹配。' }}</p>
            <ul class="team-list">
              <li>{{ isEn ? 'Carefully vetted and matched per matter' : '按案件严格筛选与匹配' }}</li>
              <li>{{ isEn ? 'Procedurally compliant, locally executed' : '程序合规与本地化执行' }}</li>
            </ul>
            <p class="team-note">{{ isEn ? 'Partner directory coming soon.' : '合作网络名录更新中。' }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 09 客户信任体系 -->
    <section class="section trust-section" id="trust">
      <div class="wrap">
        <div class="section-head">
          <div class="eyebrow">{{ isEn ? 'Why clients trust us' : '客户信任体系' }}</div>
          <h2>{{ isEn ? 'Professional, trustworthy, secure — the baseline of cross-border legal service.' : '专业、可信、安全——跨境法律服务的底线。' }}</h2>
        </div>
        <div class="trust-grid">
          <div class="trust-card">
            <i>秘</i>
            <h3>{{ isEn ? 'Confidentiality' : '保密承诺' }}</h3>
            <p>{{ isEn 
              ? 'Consultation information is used solely for assessment and follow-up, protected by professional confidentiality and handled in line with PIPL and GDPR expectations.' 
              : '咨询信息仅用于初步评估与后续沟通，受律师保密义务约束；数据处理遵循中国《个人信息保护法》与 GDPR 合规要求。' }}</p>
          </div>
          <div class="trust-card">
            <i>评</i>
            <h3>{{ isEn ? 'Assess first' : '先评估，再行动' }}</h3>
            <p>{{ isEn 
              ? 'Initial consultation assesses matter type, deadlines, evidence, and viable paths — free, non-binding, and never pushing unnecessary proceedings.' 
              : '初步咨询用于判断事项类型、时效、证据与可行路径，不收费、不构成委托关系，也不会劝你做不必要的程序。' }}</p>
          </div>
          <div class="trust-card">
            <i>诚</i>
            <h3>{{ isEn ? 'Honest assessment' : '诚实评估，不承诺结果' }}</h3>
            <p>{{ isEn 
              ? 'We are candid about prospects and risks. Outcomes depend on facts, evidence, and local rules — anyone promising a specific result is not to be trusted.' 
              : '我们如实说明可行性与风险边界。法律程序的结果取决于事实、证据与当地规则，任何承诺办案结果的说法都不可信。' }}</p>
          </div>
          <div class="trust-card">
            <i>规</i>
            <h3>{{ isEn ? 'Cross-border compliance' : '跨境协作规范' }}</h3>
            <p>{{ isEn 
              ? 'Foreign proceedings are handled with locally licensed counsel under local rules — we never step outside our license to give local-law opinions.' 
              : '境外法律程序通过与当地执业律所合作提供，确保在当地执业规则下合规推进，绝不越界出具当地法律意见。' }}</p>
          </div>
        </div>
        <div class="practice-note">
          <b>{{ isEn ? 'Practice statement: ' : '执业声明：' }}</b>
          <span>{{ isEn 
            ? 'Shenyuan International practices in mainland China; foreign legal proceedings are conducted through locally licensed counsel. An initial consultation does not create an attorney-client relationship or formal legal advice.' 
            : '深远(国际)律师事务所在中国大陆执业；境外法律程序通过与当地执业律所合作完成。初步咨询不构成委托关系或正式法律意见。' }}</span>
        </div>
      </div>
    </section>

    <!-- 10 FAQ -->
    <section class="section" id="faq">
      <div class="wrap">
        <div class="section-head">
          <div class="eyebrow">{{ isEn ? 'Before you begin' : '开始之前' }}</div>
          <h2>{{ isEn ? 'Frequently asked questions' : '常见问题' }}</h2>
        </div>
        <div class="faq-grid">
          <details open>
            <summary>{{ isEn ? 'How soon will I hear back?' : '提交咨询后，多久会有回复？' }}</summary>
            <p>{{ isEn 
              ? 'We commit to a first response within 24 hours, then arrange the next conversation based on urgency, region, and document readiness.' 
              : '我们承诺 24 小时内首响。收到信息后，会结合事项紧急程度、所在地区和材料完整度安排后续沟通。' }}</p>
          </details>
          <details>
            <summary>{{ isEn ? 'Can I submit before I have all documents?' : '我还没有整理好全部材料，可以提交吗？' }}</summary>
            <p>{{ isEn 
              ? 'Yes. A timeline, key people, and desired outcome are enough for an initial direction.' 
              : '可以。先提供时间线、人物和你想实现的结果，足够用于初步判断入口。' }}</p>
          </details>
          <details>
            <summary>{{ isEn ? 'Is this formal legal advice?' : '这是正式法律意见吗？' }}</summary>
            <p>{{ isEn 
              ? 'No. Initial consultation is for understanding the matter and identifying next steps; it does not create a retainer or formal legal advice.' 
              : '不是。初步咨询用于了解事项和判断下一步，不构成律师委托或正式法律意见。' }}</p>
          </details>
          <details>
            <summary>{{ isEn ? 'Can I contact you on WeChat?' : '可以直接通过微信联系吗？' }}</summary>
            <p>{{ isEn 
              ? 'Yes. You can first share the matter type and urgency on WeChat. If there are many documents, submitting the form also helps us understand the situation more completely.' 
              : '可以。你可以通过微信先说明事项类型和紧急程度；如果材料较多，也建议同时提交表单，便于我们完整了解情况。' }}</p>
          </details>
        </div>
      </div>
    </section>

    <!-- 11 咨询入口 CTA -->
    <section class="cta-band" id="contact">
      <div class="wrap">
        <div class="eyebrow">{{ isEn ? 'Free consultation' : '免费法律咨询' }}</div>
        <h2>{{ isEn ? 'Your cross-border dispute deserves a starting point in your own language.' : '你的跨境纠纷，值得一个用母语讲清的起点。' }}</h2>
        <p>{{ isEn 
          ? 'Submit the basics or scan our WeChat. We will assess deadlines, evidence, and viable paths — free, honest, and directional.' 
          : '提交基本情况，或扫码添加微信。我们会先判断时效、证据与可行路径——不收费，不承诺结果，只给方向。' }}</p>
        <div class="hero-actions">
          <a class="button button-primary" href="#intake" @click.prevent="scrollToIntake">
            {{ isEn ? 'Free legal consultation →' : '免费法律咨询 →' }}
          </a>
          <NuxtLink class="button button-outline" :to="isEn ? '/en/services' : '/services'">
            {{ isEn ? 'Review our services' : '再看一遍服务范围' }}
          </NuxtLink>
        </div>
      </div>
    </section>

    <!-- 成功提示弹窗 Modal -->
    <div class="modal-backdrop" :class="{ 'is-visible': successModalOpen }" role="dialog" aria-modal="true" @click.self="successModalOpen = false">
      <div class="success-panel">
        <button class="modal-close" type="button" @click="successModalOpen = false" aria-label="关闭">×</button>
        <h3>{{ isEn ? 'We have received your information' : '已收到您的信息' }}</h3>
        <p>{{ isEn 
          ? 'We will first review the matter type, relevant region, and your intended outcome to identify the next discussion points.' 
          : '我们会先查看事项类型、涉及地区和你希望达成的目标，并据此判断后续沟通重点。' }}</p>
        
        <strong class="material-title">{{ isEn ? 'Suggested documents to prepare' : '建议先准备这些材料' }}</strong>
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
      <div class="success-panel privacy-modal-panel">
        <button class="modal-close" type="button" @click="privacyModalOpen = false" aria-label="关闭">×</button>
        <h3>{{ isEn ? 'Privacy Notice & Confidentiality' : '隐私保护与保密说明' }}</h3>
        
        <div class="privacy-modal-body">
          <div class="privacy-point">
            <div class="privacy-point-title">{{ isEn ? 'Information Collection & Usage' : '信息使用范围' }}</div>
            <p>{{ isEn 
              ? 'The information you submit via this consultation form is strictly used for initial matter assessment, conflict-of-interest checks, and follow-up communication by our legal team.' 
              : '您在咨询表单中提交的称呼、联系方式和案件描述，仅供本所涉外律师团队进行初步案情评估、利益冲突检索及后续沟通联系，绝不向任何未经授权的第三方披露。' }}</p>
          </div>

          <div class="privacy-point">
            <div class="privacy-point-title">{{ isEn ? 'Security & Compliance' : '数据安全与合规' }}</div>
            <p>{{ isEn 
              ? 'All data transmission is encrypted (SSL/TLS) in strict accordance with the Personal Information Protection Law (PIPL) and applicable international data protection standards.' 
              : '咨询数据全程通过 SSL/TLS 加密传输并加密存储，遵循《中华人民共和国个人信息保护法》(PIPL) 与相关跨境数据合规要求，确保您的商业与私人信息安全。' }}</p>
          </div>

          <div class="urgent-note" style="margin-top: 14px;">
            {{ isEn 
              ? 'Notice: An initial consultation does not create an attorney-client relationship. Please do not submit sensitive identifiers such as ID numbers, bank card numbers, or passwords.' 
              : '特别提醒：初步咨询沟通不构成正式委托代理关系。请勿在此阶段提供身份证件原件号码、银行卡密码或最高机密等敏感信息。' }}
          </div>
        </div>

        <div class="success-actions" style="margin-top: 20px;">
          <button class="button button-primary" type="button" @click="privacyModalOpen = false">
            {{ isEn ? 'I Understand' : '我已了解' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, computed } from 'vue'
import { getApiClient, parseApiError } from '@/api/client'

const route = useRoute()
const isEn = computed(() => route.path.startsWith('/en'))

// ---- SEO --------------------------------------------------------------
const siteUrl = 'https://shenyuanlegal.com'
const canonical = computed(() => isEn.value ? `${siteUrl}/en` : `${siteUrl}/`)

useSeoMeta({
  title: () => isEn.value
    ? 'Shenyuan International | Cross-Border Dispute Resolution & Family Asset Protection'
    : 'Shenyuan International | 深远(国际)律师事务所',
  description: () => isEn.value
    ? 'Shenyuan International Law Firm helps Chinese businesses and families resolve international trade disputes, recover cross-border debts and protect inherited family assets — bilingual, executed through a global network of local counsel.'
    : 'Shenyuan International 深远(国际)律师事务所：为中国企业与家庭提供跨境商事争议、债务追收、继承与家族资产的国际法律服务，中英双语，覆盖全球 30+ 国家与地区的合作律所网络。',
  ogTitle: () => isEn.value
    ? 'Shenyuan International | Cross-Border Dispute Resolution'
    : 'Shenyuan International | 深远(国际)律师事务所',
  ogDescription: () => isEn.value
    ? 'Cross-border disputes, executed globally. Trade disputes, debt recovery, inheritance and family assets.'
    : '跨境争议，全球落地执行。跨境商事争议、债务追收、继承与家族资产——中英双语，全球协作网络。',
  ogType: 'website',
  ogUrl: () => canonical.value,
})

useHead({
  link: [
    { rel: 'canonical', href: () => canonical.value },
    { rel: 'alternate', hreflang: 'zh-CN', href: `${siteUrl}/` },
    { rel: 'alternate', hreflang: 'en', href: `${siteUrl}/en` },
    { rel: 'alternate', hreflang: 'x-default', href: `${siteUrl}/` },
  ],
  script: [
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
    await getApiClient().post('/api/intakes', {
      name: form.value.name,
      phone: form.value.phone,
      email: form.value.email || undefined,
      matter: form.value.matter,
      summary: form.value.summary,
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
