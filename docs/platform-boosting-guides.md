# 海外提速 + 本地 SEO + 国内收录：三份操作指引

> 版本：v1.0 · 2026-08-06 · 均为**用户操作项**（DNS/平台后台需要账号权限）
> 完成顺序建议：Cloudflare（1 小时）→ Google Business Profile（30 分钟）→ 百度/必应提交（30 分钟）

---

## 1. Cloudflare CDN（海外访问提速，免费）

**为什么**：VPS 在亚洲，欧美用户（目标客户）访问慢；Cloudflare 免费版全球节点缓存静态资源，海外访问速度提升明显，还自带 DDoS 防护和 HTTPS。

### 步骤
1. 注册 [cloudflare.com](https://dash.cloudflare.com/sign-up)（用能收验证码的邮箱）
2. Add a site → 输入 `shenyuanlegal.com` → 选 **Free** 套餐
3. Cloudflare 扫描现有 DNS 记录：确认以下记录被自动导入（没有就手动加）：
   - `A  @  45.128.210.102`（主域）
   - `A  www  45.128.210.102`
   - 其它子域（law.927900.xyz 等）照原样保留
4. 把域名 NS 改到 Cloudflare 给的两台服务器（在域名注册商处改，如阿里云/腾讯云/Namesilo 的 DNS 管理）
   - ⏳ NS 生效通常 5-30 分钟，最长 48h
5. Cloudflare 后台 → SSL/TLS → 加密模式选 **Full (strict)**（保证 Caddy 的自动 HTTPS 证书正常）
6. **必须**：Cloudflare 后台 → 规则（Rules）→ 确认回源地址为 `45.128.210.102`，且 **Proxy status 全部打开**（橙色云朵）
7. 验证：`curl -sI https://shenyuanlegal.com/ | grep -i "cf-ray\|server"` —— 出现 `cf-ray` 头即生效

### 注意
- 改 NS 期间站点会短暂中断属正常；先在本地确认 Cloudflare 后台记录与当前 DNS 一致再切
- 邮件（如有 MX 记录）保留原有解析，不要交给 Cloudflare 代理
- 若之后要换源站 IP，Cloudflare 后台改一条 A 记录即可

---

## 2. Google Business Profile（Google 地图 + 本地 SEO 信任）

**为什么**：海外华人搜「Chinese lawyer / 中国律师 美国」会在 Google 地图看到；GBP 档案是本地信任背书，也是 AI Overview 引用的实体来源之一。

### 步骤
1. 打开 [business.google.com](https://business.google.com) → 用 Google 账号登录（建议用律所专用账号）
2. 添加商家 → 名称：`Shenyuan International 深远(国际)律师事务所`
3. 类别：**Law firm（律师事务所）**，副类目可加 Legal services
4. 地址：按实际办公地址填写（无实体地址可选「服务区域」，但信任度低——建议先如实填）
5. 联系方式：官网 `https://shenyuanlegal.com/` + 邮箱 + 电话（如有）
6. 营业时间、简介（用网站首页描述）、Logo、封面图
7. **验证**（三选一）：明信片（最稳，1-2 周）/ 电话 / 视频——明信片会寄到填写的地址
8. 验证通过后：
   - 「网站」URL 填 `https://shenyuanlegal.com/?utm_source=google_business&utm_medium=local&utm_campaign=gbp`
   - 发 1-2 条「服务介绍」帖子（用素材包公众号标题变体）
   - 邀约真实客户留评价（律师行业：只能邀已服务客户，不得刷评）

### 合规提示
- 法律服务业评价要真实，平台与律师执业规范都不允许虚构
- 类别选 Law firm 后 Google 会按法律行业政策审核，避免任何「保证胜诉」表述

---

## 3. 百度 + 必应站长平台提交（国内收录）

**为什么**：国内出海企业主会搜「美国客户欠款怎么办」「跨境追债律师」——百度收录后才能覆盖这部分流量。站点已放行 Baiduspider/360Spider/Sogou（robots.txt 已更新）。

### 3.1 百度（百度搜索资源平台）
1. 打开 [ziyuan.baidu.com](https://ziyuan.baidu.com) → 用百度账号登录
2. 用户中心 → 站点管理 → 添加站点：`shenyuanlegal.com`
3. 验证站点（三选一，推荐 **CNAME** 或 HTML 标签）：
   - HTML 标签验证：把百度给的 `<meta name="baidu-site-verification" content="xxx">` 贴到首页 `<head>`（告诉我，我帮加）
   - CNAME：在域名 DNS 加一条记录（与 Cloudflare 共存注意：用 DNS 记录，别开代理）
4. 验证通过 → 普通收录 → **sitemap 提交**：`https://shenyuanlegal.com/sitemap.xml`
5. 资源提交 → 手动提交：把首页 + 3 个服务页 + 重点国家页（美国/加拿大/澳大利亚）URL 逐个提交
6. 关联小程序/爱番番等为可选

### 3.2 必应（Bing Webmaster Tools）
1. 打开 [bing.com/webmasters](https://www.bing.com/webmasters) → Microsoft 账号登录
2. 添加站点 → 建议走 **Google 导入**（若 GSC 已接入，一键导入最快）
3. 或 DNS 验证（同上）
4. 提交 sitemap：`https://shenyuanlegal.com/sitemap.xml`
5. Bing 会顺带收录 Yahoo/国内 Edge 流量

### 3.3 注意事项
- 国内访问 shenyuanlegal.com 受网络环境影响（未备案域名 + 海外主机），百度抓取可能不稳定——若收录失败，考虑给国内单独做一个纯中文镜像页（阿里云备案域名）或接受现状
- robots.txt 已显式放行中文爬虫，无需额外配置

---

## 完成后

| 项 | 预计效果 | 验证方式 |
|----|---------|---------|
| Cloudflare | 海外访问提速 + 免费防护 | `cf-ray` 响应头 |
| GBP | 地图曝光 + 本地搜索 | Google 搜「Chinese lawyer」看地图位 |
| 百度/必应 | 国内搜索收录 | 站长平台看抓取/收录数 |
