# 深远涉外律师事务所 · 管理中台 (frontend-admin) 重构与功能扩展方案

> **基础模板**：[Whbbit1999/shadcn-vue-admin](https://github.com/Whbbit1999/shadcn-vue-admin)  
> **核心技术栈**：Vue 3 + Vite 5 + TypeScript + Tailwind CSS + shadcn-vue (Radix Vue) + Pinia + Lucide Icons  
> **目标定位**：面向跨境债权追收、外贸争议仲裁诉讼、跨国继承的高品质、高扩展性涉外法律业务中台

---

## 一、 重构背景与核心痛点

当前 `frontend-admin` 采用 Element Plus 快速搭建，虽然打通了基本的线索与文章增删改查，但随着涉外业务深入，暴露出以下明显短板：

1. **视觉调性与品牌定位不符**：
   - 标准通用组件库缺乏质感，难以契合高端涉外商事与跨国高净值客户服务的专业形象。
   - 缺少对深色模式（Dark Mode）、高对比度法律文书阅读体验的支持。
2. **交互体验与桌面工作流单一**：
   - 缺少快捷指令面板（`Cmd+K / Ctrl+K` Command Palette）、多标签页（TagsView）、侧边栏可折叠折叠等现代化桌面管理体验。
   - 线索处理仅有单向的静态表格，缺乏涉外商事线索常用的看板流转（Kanban Board）和自定义列过滤（Faceted Filters）。
3. **涉外业务纵深能力不足**：
   - **CRM 维度**：缺少 24h 首次响应与 7d 跟进推进的 **SLA 倒计时预警**；缺少目标客户所在国家/法域的时区时差计算提示（避免北京时间深夜外呼骚扰客户）；缺乏证据材料审核清单（Checklist）。
   - **CMS 维度**：仅支持简陋的 textarea 输入，缺少中英双语分栏并排对照、实时 Markdown 渲染预览、SEO 长度校验。
   - **营销与调研维度**：未能完整承载后端已具备的 7 大海外渠道素材包、UTM 渠道追踪排期以及涉外备忘录格式化输出。

---

## 二、 系统功能架构全景设计

```
┌────────────────────────────────────────────────────────────────────────┐
│             深远涉外律师事务所 · 业务中台 (Shenyuan Legal Admin)        │
└────────────────────────────────────────────────────────────────────────┘
  │
  ├── 1. 经营概览大盘 (Dashboard & Insights)
  │    ├── 关键经营指标 (总线索、待响应 SLA、转化率、高价值案源)
  │    ├── 22 个重点出海国家/地区客户分布图谱 (Geo Distribution)
  │    ├── 业务线构成 (跨境债权追收 / 外贸争议仲裁 / 跨国继承)
  │    └── 获客转化漏斗 (访客 -> 留资 -> 初审评估 -> 签约立案)
  │
  ├── 2. 涉外商事与家事线索中枢 (Intakes & Case CRM)
  │    ├── 双视图模式：TanStack 风格高级数据表格 / Kanban 阶段流转看板
  │    ├── SLA 履约监控：24h 首次响应倒计时、7d 推进逾期红标预警
  │    ├── 客户 360° 档案详情抽屉 (时区与国家提示、跟进时间轴、线索评分)
  │    ├── 案件证据与材料清单 (Checklist 审核、历史附件下载、海牙认证提示)
  │    └── 数据安全与导出 (敏感手机号/邮箱脱敏、UTF-8 BOM CSV 导出)
  │
  ├── 3. 多语言法律内容工厂 (Content CMS Studio)
  │    ├── 双语文章中心 (按业务领域、搜索意图、发布状态多维过滤)
  │    ├── 分栏双语 Markdown 编辑器 (中英文左右对照、实时双向滚动预览)
  │    ├── SEO 元数据检测面板 (Slug 格式校验、Title/Desc 字符长度与富摘要评分)
  │    └── 版本快照与发布工作流 (历史版本快照、一键发布上线/撤回)
  │
  ├── 4. 出海营销与获客传播矩阵 (Marketing Command Center)
  │    ├── 7 大渠道素材工厂 (微信公号、LinkedIn、X/Twitter、小红书、Facebook、TikTok、朋友圈)
  │    ├── UTM 链接追踪生成器 (自动附加来源、媒介与业务参数)
  │    ├── 40 周内容日历排期看板 (按周/月规划主题、发布状态勾选、负责人标记)
  │    └── 一键分发剪贴板与整包 Markdown 导出
  │
  ├── 5. 涉外法律智能调研与备忘录 (Legal Research Studio)
  │    ├── 涉外法律知识库语义检索 (中国法涉外篇、跨国执行实务、文书模板全文索引)
  │    ├── 涉外案情评估备忘录生成器 (Legal Memo：事实梳理、管辖与适用法、实务策略)
  │    ├── 常用涉外文书模板库 (Demand Letter 催告函、涉外 POA 授权委托书)
  │    └── 调研审计日志 (历史检索词频、热点法条分析)
  │
  └── 6. 系统配置与安全合规 (Settings & Compliance)
       ├── 客户隐私安全策略 (脱敏权限、导出审计记录)
       ├── 通知通道监控 (企业微信机器人 Webhook、Resend 邮件连通性自测)
       └── 认证与凭据管理 (Admin Token 续期、Supabase 存储状态监控)
```

---

## 三、 核心模块功能重构与扩展细则

### 1. 经营概览大盘 (Dashboard)
- **经营指标卡片（Metric Cards）**：
  - **总咨询线索**：累计留资量及环比增长。
  - **待跟进 SLA 紧急件**：红/黄警报展示距 24h 超时不足 4 小时或已逾期的线索。
  - **推进中案件**：处于证据收集与律师接洽阶段的在办案。
  - **已转化结案**：完成律师签约或成功办结案源。
- **涉外客源分布分析**：
  - 基于 22 个出海落地页（美、加、澳、新、英、阿联酋等）统计线索国别来源排行榜。
- **业务结构与转化漏斗**：
  - 环形图展示跨境追收（Recovery）、外贸纠纷（Trade）、涉外继承（Legacy）分布。
  - 转化漏斗：留资线索 -> 已联系 -> 方案评估 -> 签约立案。

### 2. 线索中枢 CRM (Intakes Hub - 深度强化)
- **双模操作视图**：
  - **高级数据表格模式 (Data Table)**：
    - 支持按状态、意向评分（高/中/低）、业务类型、创建日期区间复合筛选。
    - 自定义列显示控制（Hide/Show Columns）。
    - 快速批量操作与数据导出（UTF-8 BOM CSV）。
  - **阶段看板模式 (Kanban Board)**：
    - 四列流转：`新线索 (New)` -> `已联系 (Contacted)` -> `方案评估中 (Processing)` -> `已办结 (Closed)`。
    - 支持卡片拖拽式流转状态，并在拖拽时弹窗快捷补录沟通纪要。
- **SLA 履约预警机制**：
  - **24h 响应 SLA**：计算 `created_at` 到当前时间差，展示倒计时胶囊（绿色正常、橙色紧迫 <4h、红色逾期）。
  - **7d 推进 SLA**：已联系线索超过 7 天无状态或备注更新，打上“停滞线索”标签。
- **客户 360° 档案抽屉 (Sheet)**：
  - **时区与跨国联络提醒**：根据客户所在国家（如美国东部 UTC-5、英国 UTC+0）实时换算当地时间，并提示“当前对方处于工作时间/休息时间”。
  - **智能意向分拆解**：展示评分构成（联系方式完整度 + 案情详尽度 + 涉外法域明确度）。
  - **跟进时间轴 (Timeline)**：记录每次跟进时间、操作人、状态变更与跟进备注。
  - **证据材料清单 (Checklist)**：按案件类型自动预设必备文件清单（如：涉外借款合同、跨境转账水单、公证认证文件），支持勾选与已上传历史文件直接预览/下载。

### 3. 多语言内容工厂 (CMS Studio)
- **多维文章列表管理**：
  - 支持按业务领域（trade/recovery/legacy/general）、搜索意图（I/C/T）、发布状态筛选。
  - 快速查看当前文章的中英文双语完整度。
- **双语分栏 Markdown 编辑器**：
  - 左侧为中文 Markdown 编辑 + 实时渲染预览；右侧为英文 Markdown 编辑 + 实时渲染预览。
  - 支持插入法条引用样式块、律师团队警示提示框等涉外专属排版。
- **SEO 质量检测与版本控制**：
  - URL Slug 自动规范校验（仅允许小写英文、数字与中划线）。
  - SEO 标题与 Description 字符数健康指标条（中文推荐 80-120 字，英文推荐 120-160 字符）。
  - 版本快照 Diff：每次保存自动留存版本记录，支持快速回滚。

### 4. 出海营销与获客传播矩阵 (Marketing Center)
- **全渠道素材生成器**：
  - 选择已发布文章或输入热点主题，一键调用后端生成 7 大渠道针对性内容：
    1. **微信公众号**：3 组备选标题 + 摘要导语 + 核心实务精炼排版。
    2. **LinkedIn 领英**：面向海外法务总监与出海创始人的专业商业洞察（英文）。
    3. **X / Twitter**：精炼短推文（≤280 字符） + 线程推文（Thread）。
    4. **小红书**：干货指南、踩坑避雷、真实诉讼故事 3 种差异化角度文案。
    5. **Facebook**：商业社群帖文 + Meta 广告投放受众定向参数建议。
    6. **TikTok / 视频号**：中英双语口播脚本、分镜与视觉画面指引、BGM 建议。
    7. **律师朋友圈**：适合境内外高净值客户群体的专业轻度文案。
- **营销日历与 UTM 追踪**：
  - 对应 40 周排期表的可视化周历/月历。
  - 一键生成包含 `utm_source`、`utm_medium`、`utm_campaign` 的专属追踪链接。
  - 支持整包导出为 Markdown 文件供运营团队协同。

### 5. 涉外法务调研助手 (Legal Research Studio)
- **知识库全文智能检索**：
  - 深度索引 `legal_kb/` 涉外商事法规、跨境证据认证（海牙 Apostille）、域外执行实务。
  - 关键词高亮、法域分类标识、一键复制标准法条与实务观点。
- **涉外案情评估备忘录 (AI Legal Memo)**：
  - 录入案情基本事实、涉外争议标的、涉及法域。
  - 自动排版生成包含「争议要点」、「管辖权与准据法分析」、「行动策略与证据清单」的正式法律备忘录。
  - 支持一键导出为标准 PDF 或复制为邮件草稿。

---

## 四、 前端技术栈与工程目录规划

### 1. 核心依赖选型（基于 shadcn-vue-admin）
```json
{
  "name": "shenyuan-admin",
  "private": true,
  "version": "2.0.0",
  "dependencies": {
    "vue": "^3.5.0",
    "vue-router": "^4.4.0",
    "pinia": "^2.2.0",
    "radix-vue": "^1.9.0",
    "lucide-vue-next": "^0.400.0",
    "tailwindcss": "^3.4.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.1",
    "tailwind-merge": "^2.5.0",
    "@tanstack/vue-table": "^8.20.0",
    "@vueuse/core": "^11.0.0",
    "vue-sonner": "^1.1.0",
    "markdown-it": "^14.1.0",
    "axios": "^1.7.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.1.0",
    "typescript": "^5.5.0",
    "vue-tsc": "^2.1.0",
    "vite": "^5.4.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  }
}
```

### 2. 规范化工程目录结构
```text
frontend-admin/
├── src/
│   ├── assets/                 # 品牌 Logo、SVG 图标
│   ├── components/
│   │   ├── ui/                 # 基于 Radix Vue 与 Tailwind 封装的 shadcn-vue 组件
│   │   │   ├── button/         # Button 按钮 (default, destructive, outline, ghost 等)
│   │   │   ├── card/           # Card 卡片体系
│   │   │   ├── table/          # Table 数据表格
│   │   │   ├── sheet/          # Sheet 抽屉（客户详情）
│   │   │   ├── dialog/         # Dialog 模态弹窗
│   │   │   ├── badge/          # Badge 状态胶囊
│   │   │   ├── tabs/           # Tabs 选项卡
│   │   │   ├── input/          # Input 基础输入框
│   │   │   ├── select/         # Select 下拉选择器
│   │   │   ├── command/        # Cmd+K 全局指令面板
│   │   │   └── toast/          # Sonner 现代化通知
│   │   ├── layout/             # 框架布局组件
│   │   │   ├── AppHeader.vue   # 顶栏（面包屑, Cmd+K, 深浅色切换, 状态指示灯）
│   │   │   ├── AppSidebar.vue  # 侧边栏（律所品牌徽标, 模块分组, 折叠开关）
│   │   │   ├── AppTagsView.vue # 多标签历史标签页
│   │   │   └── AppFooter.vue   # 状态底栏（Supabase 状态, 法律免责声明）
│   │   └── business/           # 律所业务专属组件
│   │       ├── SlaCountdown.vue# 24h / 7d SLA 倒计时与逾期红标组件
│   │       ├── TimezoneTip.vue # 涉外客源地时区换算与作息提醒
│   │       ├── ScoreBadge.vue  # 线索高/中/低意向评分徽章
│   │       └── MarkdownDualEditor.vue # 双语分栏 Markdown 编辑预览器
│   ├── layouts/
│   │   ├── AdminLayout.vue     # 主管理后台布局
│   │   └── AuthLayout.vue      # 登录/认证布局
│   ├── views/
│   │   ├── dashboard/          # 1. 经营概览与数据大盘
│   │   │   └── IndexView.vue
│   │   ├── crm/                # 2. 涉外商事线索中枢
│   │   │   ├── ListView.vue    # 表格模式
│   │   │   ├── KanbanView.vue  # 看板流转模式
│   │   │   └── components/
│   │   │       └── IntakeDetailSheet.vue # 客户 360° 档案抽屉
│   │   ├── content/            # 3. 双语 CMS 内容工厂
│   │   │   ├── ArticleList.vue # 文章列表与版本状态
│   │   │   └── ArticleEdit.vue # 双语对照编辑与发布
│   │   ├── marketing/          # 4. 出海营销与获客矩阵
│   │   │   ├── GeneratorView.vue # 7 大渠道素材生成器
│   │   │   └── CalendarView.vue  # 40 周营销排期日历
│   │   ├── research/           # 5. 涉外法律智能调研
│   │   │   ├── SearchHub.vue   # 知识库语义检索
│   │   │   └── MemoStudio.vue  # 法律备忘录工作台
│   │   ├── settings/           # 6. 设置与合规配置
│   │   │   └── SettingsView.vue
│   │   └── auth/
│   │       └── LoginView.vue   # 现代化律所认证登录页
│   ├── api/                    # 统一接口模块 (client.ts, intakes.ts, content.ts 等)
│   ├── stores/                 # Pinia 状态库 (app.ts, user.ts, tags.ts, crm.ts)
│   ├── composables/            # 通用组合式函数 (useTheme.ts, useSla.ts, useCommand.ts)
│   ├── lib/                    # 工具函数 (utils.ts cn() 类名合并, formatters.ts)
│   ├── router/                 # 路由守卫与动态导航配置
│   ├── styles/                 # globals.css (Tailwind CSS 变量与主题色)
│   ├── App.vue
│   └── main.ts
```

### 3. 色彩规范与律所品牌调色板
- **Primary 品牌深青色（Shenyuan Teal）**：
  - Light 模式：`#084d50`（侧边栏、主操作按钮）
  - Dark 模式：`#15928d`（深色适配高对比度）
- **Accent 辅色暖金/琥珀（Amber & Gold）**：
  - 核心标签与高价值案源高亮：`#d76e39` / `#f59e0b`
- **Surface 背景与卡片色**：
  - Light：背景 `#f8fafc` / `#f4f1ea`，卡片 `#ffffff`，边框 `#e2e8f0`
  - Dark：背景 `#090d12`，卡片 `#111720`，边框 `#1e293b`

---

## 五、 分步实施里程碑与步骤清单

| 阶段 | 核心任务 | 交付物 |
| :--- | :--- | :--- |
| **Phase 1: 技术基座与依赖重构** | 升级 `package.json` 引入 Tailwind CSS、Radix Vue、Lucide 图标，配置 `globals.css` 与工具函数 `cn()`，移除 Element Plus 强依赖 | 现代化的 CSS 变量系统与构建配置 |
| **Phase 2: 基础组件与主框架布局** | 封装 Button, Card, Table, Sheet, Dialog, Badge 等基础 UI 原语；实现带折叠侧边栏、顶栏 Cmd+K 面板与 TagsView 的 `AdminLayout` | 全新视觉规范与后台基础骨架 |
| **Phase 3: 线索中枢 CRM 重构** | 开发表格视图、看板流转视图、24h/7d SLA 倒计时预警、客户 360° 档案抽屉及跟进时间轴 | 具备高商业价值的涉外案源流转中台 |
| **Phase 4: 双语 CMS 内容中心升级** | 打造中英双语分栏 Markdown 编辑器、实时分屏渲染、SEO 质量检测与版本历史快照 | 涉外律所双语内容工厂与发布工作流 |
| **Phase 5: 出海营销矩阵与法律调研** | 落地 7 渠道出海营销素材生成器、UTM 追踪生成、40 周排期日历以及涉外法律备忘录工作台 | 营销获客与办案调研赋能工具集 |
| **Phase 6: 经营大盘与安全合规验收** | 构建经营分析数据大盘、敏感手机号/邮箱脱敏控制，完成 TypeScript 编译与端到端交互走查 | 全量功能打通与高质量生产交付 |

---

## 六、 验证标准与交付成果

1. **功能完整度**：
   - 线索管理支持表格与看板自由切换，SLA 状态倒计时与告警精准，客户档案抽屉正常操作。
   - 内容中心支持中英双语对照编辑、实时预览与一键发布上线。
   - 出海营销 7 渠道生成、排期日历、知识库搜索与法律备忘录生成均与后端 API 顺畅连通。
2. **体验与交互品质**：
   - 彻底摆脱传统后台粗糙感，呈现 `shadcn-vue` 原生高质感，响应式设计与深浅色主题无缝切换。
   - 键盘快捷键（`Cmd+K / Ctrl+K`）可快速唤起全局指令面板，实现跨模块极速跳转。
3. **工程质量与稳定性**：
   - 严格遵循 TypeScript 类型规范，`pnpm build` 零报错通过。
   - 请求异常（401/403/500）均有友好通知提醒，未登录自动重定向到认证页面。
