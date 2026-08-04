# Google Ads 小额测试投放包（国家页落地）

> 版本：v1.0 · 2026-08-04 · 用途：用素材包 Ads 组合验证跨境法律关键词的商业价值
> 落地页：5 个国家专页（中英双语，均已在生产验证 200）

## 0. 目标与预算

- **测试目标**：验证「国家 + 业务」高意图词的点击与转化成本，找出值得加码的 1-2 个国家/业务线
- **预算**：$10/天 × 14 天 ≈ $140（约 ¥1000）；日预算**不超 $15**
- **出价**：手动 CPC，最高 $2.00；先跑 3 天积累数据再决定是否切智能出价
- **衡量**：GA4 `generate_lead` 事件（表单/AI 聊天提交成功即上报，本次已上线）作为转化
- **判定门槛**：单线索成本（CPL）≤ ¥300 为及格，≤ ¥150 为优秀；CTR ≥ 2%

## 1. 账户准备（20 分钟，一次性）

1. [ads.google.com](https://ads.google.com) 注册/登录 Google Ads 账户（用能收验证码的邮箱）
2. 与 GA4 关联：Google Ads → 工具 → 关联 → Google Analytics（用 G-MC8LWZH6TH 所在账户）
3. GA4 里把事件标记为转化：GA4 → 管理 → 事件 → `generate_lead` → 标记为转化
4. 若 Google Ads 里导入 GA4 转化：工具 → 转化 → 新建 → 导入 → GA4 → 勾选 `generate_lead`

## 2. 广告系列结构（照抄）

```
广告系列：Shenyuan-Country-Test（搜索网络，无展示联盟）
├── 广告组 1：US 美国（落地页 /en/countries/united-states）
├── 广告组 2：CA 加拿大（落地页 /en/countries/canada）
├── 广告组 3：AU 澳大利亚（落地页 /en/countries/australia）
├── 广告组 4：SG 新加坡（落地页 /en/countries/singapore）
└── 广告组 5：UK 英国（落地页 /en/countries/united-kingdom）
```

- **设置**：搜索网络；地域 = 该国 + 中国大陆（出海企业主在国内搜）；语言 = 英语 + 简体中文
- **预算**：$10/天；**出价**：手动 CPC 上限 $2.00
- **轮播**：广告轮播优化（测试阶段用"无限制轮播"收集数据）

## 3. 每国广告组物料（关键词 + 否定词 + 广告文案）

> 全部可用素材包「Google Ads」区的标题/描述结构，这里按国家定制。
> 标题 ≤30 字符、描述 ≤90 字符（已校验）。ZH 广告投给中文搜索（海外华人/国内出海企业）。

### 3.1 US 美国 → /en/countries/united-states

**关键词（词组匹配）**
```
enforce chinese judgment in us
collect debt from us buyer
us debt collection for chinese company
international debt collection china
```
**否定词**：free · jobs · salary · visa · immigration · how to become a lawyer

**英文广告（RSA）**
- 标题：`Enforce Chinese Judgments in US` / `US Buyer Debt Recovery` / `Collect US Debts from China` / `Bilingual + Local US Counsel` / `Free Initial Assessment`
- 描述：`Owed money by a US buyer? Bilingual lawyers + local US counsel. Free initial assessment.`（86 ✓）
- 描述2：`Chinese judgments enforced in the US, asset tracing, probate for Chinese heirs.`（86 ✓）

**中文广告（RSA）**
- 标题：`美国客户欠款追收` / `中国判决美国执行` / `美国房产继承律师`
- 描述：`美国客户拖欠货款？中国律师+美国本地律所协作，免费初步评估，不承诺结果。`（33 ✓）
- 描述2：`中国判决在美国执行、资产调查、跨境继承，中英双语服务。`（27 ✓）

### 3.2 CA 加拿大 → /en/countries/canada

**关键词**：`enforce chinese judgment in canada` / `canada debt collection for chinese company` / `inherit property in canada from china` / `canadian buyer not paying supplier`

**否定词**：free · jobs · visa · immigration · salary

**英文广告**
- 标题：`Enforce Judgments in Canada` / `Canada Debt Recovery` / `Chinese Heirs: Canada Property` / `Free Initial Assessment`
- 描述：`Money owed in Canada? Bilingual lawyers + local Canadian counsel. Free initial assessment.`（87 ✓）
- 描述2：`Judgment enforcement, asset tracing and inheritance in Canada for Chinese clients.`（87 ✓）

**中文广告**
- 标题：`加拿大欠款追收` / `中国判决加拿大执行` / `温哥华房产继承`
- 描述：`加拿大客户欠款？中国律师+当地律所协作，免费初步评估，不承诺结果。`（31 ✓）
- 描述2：`加拿大房产继承、资产调查、判决执行，中英双语服务。`（24 ✓）

### 3.3 AU 澳大利亚 → /en/countries/australia

**关键词**：`enforce chinese judgment in australia` / `australia debt collection chinese supplier` / `inherit property in australia from china` / `australian buyer not paying`

**否定词**：free · jobs · visa · immigration · salary

**英文广告**
- 标题：`Enforce Judgments in Australia` / `Australia Debt Recovery` / `Inherit Australia Property` / `Free Initial Assessment`
- 描述：`Unpaid invoices in Australia? Bilingual lawyers + local counsel. Free initial assessment.`（86 ✓）
- 描述2：`Judgment enforcement, asset tracing and probate in Australia for Chinese clients.`（88 ✓）

**中文广告**
- 标题：`澳洲欠款追收` / `中国判决澳洲执行` / `澳洲房产继承`
- 描述：`澳洲客户拖欠货款？中国律师+当地律所协作，免费初步评估，不承诺结果。`（31 ✓）
- 描述2：`澳洲房产继承、资产调查、判决执行，中英双语服务。`（24 ✓）

### 3.4 SG 新加坡 → /en/countries/singapore

**关键词**：`enforce chinese judgment in singapore` / `singapore debt collection for chinese company` / `enforce arbitral award singapore` / `singapore trust inheritance chinese`

**否定词**：free · jobs · visa · salary · casino

**英文广告**
- 标题：`Enforce Awards in Singapore` / `Singapore Debt Recovery` / `Judgment & Award Enforcement` / `Free Initial Assessment`
- 描述：`Owed by a Singapore counterparty? Bilingual lawyers + local counsel. Free assessment.`（84 ✓）
- 描述2：`New York Convention award enforcement, asset tracing, family wealth planning.`（83 ✓）

**中文广告**
- 标题：`新加坡欠款追收` / `仲裁裁决新加坡执行` / `家族资产规划`
- 描述：`新加坡客户/中间商欠款？中国律师+当地律所协作，免费初步评估。`（28 ✓）
- 描述2：`裁决执行、资产调查、家族信托与继承规划，中英双语。`（23 ✓）

### 3.5 UK 英国 → /en/countries/united-kingdom

**关键词**：`enforce chinese judgment in uk` / `uk debt collection for chinese company` / `uk inheritance tax chinese heirs` / `london property inheritance chinese`

**否定词**：free · jobs · visa · immigration · salary

**英文广告**
- 标题：`Enforce Judgments in the UK` / `UK Debt Recovery` / `UK Inheritance & IHT Planning` / `Free Initial Assessment`
- 描述：`Owed money in the UK? Bilingual lawyers + local UK counsel. Free initial assessment.`（86 ✓）
- 描述2：`Judgment enforcement, asset tracing, probate and IHT planning for Chinese clients.`（86 ✓）

**中文广告**
- 标题：`英国欠款追收` / `中国判决英国执行` / `英国遗产税规划`
- 描述：`英国客户拖欠货款？中国律师+当地律所协作，免费初步评估，不承诺结果。`（31 ✓）
- 描述2：`伦敦房产继承、遗嘱认证与遗产税规划，中英双语服务。`（25 ✓）

## 4. 附加信息（系列级，全部广告组共用）

- **附加链接**：/services/trade · /services/recovery · /services/legacy · /articles（素材包 sitelinks）
- **宣传信息**：免费初步评估 · 中英双语 · 24 小时响应 · 30+ 国家协作网络
- **结构化摘要**：国际贸易争议 / 债务追收 / 判决执行 / 跨境继承

## 5. UTM 链接（广告最终 URL 一律带追踪参数）

格式：`{落地页}?utm_source=google&utm_medium=cpc&utm_campaign=country-test&utm_content={adgroup}`
例：`https://shenyuanlegal.com/en/countries/united-states?utm_source=google&utm_medium=cpc&utm_campaign=country-test&utm_content=us`
- GA4 默认渠道分组会自动归因到 Google / CPC，后台可看落地页维度的线索数
- 落地页语言与广告语言对应：英文广告 → /en/countries/*，中文广告 → /countries/*

## 6. 上线后节奏（照这个看）

| 时间 | 动作 |
|------|------|
| 第 1 天 | 上线；检查落地页打开、GA4 实时能看到页面浏览 |
| 第 3 天 | 看**搜索词报告**：把不相关搜索（free/jobs/visa 等）加否定词；暂停烧钱无转化的词 |
| 第 7 天 | 按广告组看 CTR/CPC：CTR<1% 的词降级或暂停；保留 CTR≥2% 的词 |
| 第 14 天 | 汇总：每国每词的展示/点击/转化/CPL；决定加码（预算翻倍）或收缩到最佳 1-2 国 |

**判断指标**：CTR ≥ 2% · CPC ≤ $2 · CPL ≤ ¥300 及格 / ¥150 优秀 · 转化率（点击→线索）≥ 5%

## 7. 合规红线（法律行业广告）

1. **不承诺结果**：文案统一用「免费初步评估/不承诺结果」——Google 政策 + 中国律师执业规范双红线
2. **境外执业边界**：文案写「与当地律所合作」，不暗示持有当地执业资格（国家页已含该声明）
3. **不夸大**：不用「最好的律师」「100% 追回」等绝对化用语
4. **隐私**：落地页含《隐私说明》与 PIPL 同意条款（表单/AI 聊天均已强制 consent）
5. 若投美国市场，注意各州律师广告规则与 FDCPA 对债务催收广告的限制——文案已规避

## 8. 素材包联动

- 每个广告组的文案就是素材包「Google Ads」区按国家定制的版本，后台 `/admin/marketing` 可随时重新生成
- 广告落地页转化事件（generate_lead）已随本次上线，GA4 里标记为转化后即可在 Google Ads 看到线索成本
