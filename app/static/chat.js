/* 深远国际 · AI 咨询助手 (chat intake widget)
 * Self-contained: injects its own styles, renders a floating launcher and a
 * guided bilingual intake chat, then POSTs a structured intake to
 * /api/intakes/chat. The server re-classifies the matter (keyword triage),
 * stores it in the same intakes pipeline (dedupe / webhook / auto-reply).
 *
 * Language follows <html lang>: zh-CN -> Chinese, anything else -> English.
 */
(function () {
  "use strict";

  var L = document.documentElement.lang === "zh-CN" ? "zh" : "en";

  var T = {
    launcher: { zh: "免费咨询", en: "Free consult" },
    title: { zh: "在线咨询", en: "Intake chat" },
    badge: { zh: "AI 接待 · 不构成法律意见", en: "AI assistant · not legal advice" },
    human: { zh: "转人工", en: "Talk to us" },
    close: { zh: "关闭", en: "Close" },
    placeholder: { zh: "输入内容，按回车发送…", en: "Type and press Enter…" },
    send: { zh: "发送", en: "Send" },
    skip: { zh: "跳过", en: "Skip" },
    intro: {
      zh: "您好，我是深远国际的在线咨询助手。为把您的案情准确转给合适的律师，我先问几个简短问题（约 2 分钟）。我无法代替律师意见，请勿在对话中发送涉密文件。",
      en: "Hi, I'm the intake assistant at Shenyuan International. To route your matter to the right lawyer I'll ask a few short questions (about 2 minutes). I'm not a lawyer — please don't share privileged documents here.",
    },
    q_business: {
      zh: "您的案情更接近哪一类？",
      en: "Which area does your matter fall under?",
    },
    opt_business: [
      { v: "trade", zh: "国际贸易争议", en: "International trade dispute" },
      { v: "recovery", zh: "诉讼与债务追收", en: "Litigation & debt recovery" },
      { v: "legacy", zh: "继承与家族资产纠纷", en: "Inheritance & family assets" },
      { v: "unsure", zh: "不确定，先沟通", en: "Not sure yet" },
    ],
    q_parties: {
      zh: "请描述您和对方的身份与关系（例：美国客户拖欠我们工厂货款；父亲在加拿大去世，我们兄弟二人继承房产）。",
      en: "Who are the parties? (e.g., a US buyer owes our factory; my father passed away in Canada and two of us inherit the property.)",
    },
    q_amount: {
      zh: "涉及金额大约多少？（点选或直接输入）",
      en: "Roughly how much is at stake? (tap or type)",
    },
    opt_amount: [
      { v: "5万以下", zh: "5万以下", en: "Under ¥50k" },
      { v: "5-50万", zh: "5-50万", en: "¥50k–500k" },
      { v: "50万以上", zh: "50万以上", en: "Over ¥500k" },
      { v: "不确定", zh: "不确定", en: "Not sure" },
    ],
    q_timeline: {
      zh: "事情发生在什么时候？",
      en: "When did this happen?",
    },
    opt_timeline: [
      { v: "半年内", zh: "半年内", en: "Within 6 months" },
      { v: "半年-2年", zh: "半年-2年", en: "6 months–2 years" },
      { v: "2年以上", zh: "2年以上", en: "Over 2 years" },
      { v: "不确定", zh: "不确定", en: "Not sure" },
    ],
    q_evidence: {
      zh: "目前有哪些材料？（可多选，用逗号分隔；没有也没关系）",
      en: "What documents do you have? (pick any; none is fine)",
    },
    opt_evidence: [
      { v: "合同、发票、订单", zh: "合同、发票、订单", en: "Contracts, invoices, POs" },
      { v: "邮件、微信、WhatsApp", zh: "邮件、微信、WhatsApp", en: "Emails, WeChat, WhatsApp" },
      { v: "催款记录", zh: "催款记录", en: "Collection records" },
      { v: "判决、仲裁文书", zh: "判决、仲裁文书", en: "Judgments / awards" },
      { v: "暂时没有", zh: "暂时没有", en: "None yet" },
    ],
    q_goal: {
      zh: "您希望达成什么结果？",
      en: "What outcome do you want?",
    },
    opt_goal: [
      { v: "追回欠款", zh: "追回欠款", en: "Recover money" },
      { v: "解决合同纠纷", zh: "解决合同纠纷", en: "Resolve a contract dispute" },
      { v: "执行判决/裁决", zh: "执行判决/裁决", en: "Enforce a judgment/award" },
      { v: "继承财产", zh: "继承财产", en: "Inherit assets" },
      { v: "先做评估咨询", zh: "先做评估咨询", en: "Get an initial assessment" },
    ],
    q_country: {
      zh: "对方或资产在哪个国家/地区？（可跳过）",
      en: "Where are the counterparty or the assets? (optional)",
    },
    q_name: {
      zh: "怎么称呼您？",
      en: "What should we call you?",
    },
    q_contact: {
      zh: "请留下您的手机、微信或邮箱，律师会在 24 小时内联系您。",
      en: "Please leave a phone, WeChat, or email. A lawyer will reach out within 24 hours.",
    },
    review_title: { zh: "请确认信息", en: "Please confirm" },
    review_consent: {
      zh: "我同意《隐私说明》，允许律所为初步评估目的处理以上信息。",
      en: "I agree to the privacy notice and consent to processing this information for an initial assessment.",
    },
    submit: { zh: "提交给律师团队", en: "Submit to the legal team" },
    submitting: { zh: "提交中…", en: "Submitting…" },
    done_title: { zh: "已收到，感谢！", en: "Received — thank you!" },
    done_body: {
      zh: "律师助理会在 24 小时内通过您留下的方式联系您。如情况紧急（资产转移、期限临近、证据灭失），请在微信上直接说明“紧急”。",
      en: "Our team will reach out within 24 hours via your contact. If urgent (asset transfer, looming deadline, evidence at risk), please mention it on WeChat.",
    },
    dup_body: {
      zh: "我们已收到过您的信息，无需重复提交。律师会按之前的方式与您联系。",
      en: "We already received your submission — no need to resubmit. The team will reach out as before.",
    },
    err_body: {
      zh: "提交失败，请检查网络后重试。",
      en: "Submission failed. Please check your connection and try again.",
    },
    consent_err: {
      zh: "请先勾选同意隐私说明。",
      en: "Please accept the privacy notice first.",
    },
    human_title: { zh: "转人工服务", en: "Talk to a human" },
    human_body: {
      zh: "请添加我们的微信并注明“转人工”，或直接留言您的需求：",
      en: "Add us on WeChat and mention “human”, or leave a message with your needs:",
    },
    labels: {
      business: { zh: "业务类型", en: "Area" },
      parties: { zh: "双方身份", en: "Parties" },
      amount: { zh: "金额", en: "Amount" },
      timeline: { zh: "时间", en: "Timing" },
      evidence: { zh: "材料", en: "Documents" },
      goal: { zh: "诉求", en: "Goal" },
      country: { zh: "国家/地区", en: "Country" },
      contact: { zh: "联系方式", en: "Contact" },
    },
  };
  function tr(obj) {
    return (obj && obj[L]) || "";
  }

  var state = {
    business: "",
    parties: "",
    amount: "",
    timeline: "",
    evidence: "",
    goal: "",
    country: "",
    name: "",
    contact: "",
    consent: false,
  };
  var transcript = [];
  var stepIndex = 0;

  /* ---------- styles ---------- */
  var css =
    "#chat-widget-root{position:fixed;right:18px;bottom:18px;z-index:9999;font-family:'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;}" +
    "#cw-launcher{display:flex;align-items:center;gap:8px;min-height:46px;padding:0 18px;border:0;border-radius:24px;background:#d76e39;color:#fff;font-size:14px;font-weight:700;cursor:pointer;box-shadow:0 8px 24px rgba(215,110,57,.35);transition:transform .2s ease;}" +
    "#cw-launcher:hover{transform:translateY(-2px);}" +
    "#cw-panel{position:fixed;right:18px;bottom:18px;width:370px;max-width:calc(100vw - 24px);height:min(600px,calc(100vh - 90px));display:none;flex-direction:column;overflow:hidden;background:#fffdf9;border:1px solid #d9d9d2;border-radius:14px;box-shadow:0 24px 60px rgba(20,33,44,.22);}" +
    "#cw-panel.open{display:flex;}" +
    "#cw-head{display:flex;align-items:center;gap:10px;padding:14px 16px;background:#084d50;color:#f5f2ec;}" +
    "#cw-head .cw-title{font-size:14px;font-weight:700;}" +
    "#cw-head .cw-badge{display:block;font-size:10.5px;font-weight:400;color:rgba(245,242,236,.75);margin-top:2px;}" +
    "#cw-human{margin-left:auto;padding:6px 10px;font-size:11.5px;color:#f5f2ec;background:rgba(255,255,255,.14);border:0;border-radius:6px;cursor:pointer;}" +
    "#cw-close{width:28px;height:28px;border:0;border-radius:50%;background:rgba(255,255,255,.14);color:#f5f2ec;font-size:13px;cursor:pointer;}" +
    "#cw-msgs{flex:1;overflow-y:auto;padding:16px 14px 6px;display:flex;flex-direction:column;gap:10px;background:#f6f3ed;}" +
    ".cw-bot,.cw-user{max-width:86%;padding:10px 13px;font-size:13.5px;line-height:1.6;border-radius:12px;white-space:pre-wrap;word-break:break-word;}" +
    ".cw-bot{align-self:flex-start;background:#fffdf9;border:1px solid #e2ddd2;border-top-left-radius:4px;color:#334454;}" +
    ".cw-user{align-self:flex-end;background:#0d6c6b;color:#fff;border-top-right-radius:4px;}" +
    ".cw-chips{display:flex;flex-wrap:wrap;gap:8px;align-self:flex-start;max-width:92%;}" +
    ".cw-chip{padding:7px 13px;font-size:12.5px;color:#084d50;background:#deefea;border:1px solid #bcdbd3;border-radius:16px;cursor:pointer;}" +
    ".cw-chip:hover{background:#cbe6de;}" +
    ".cw-chip.on{background:#0d6c6b;color:#fff;border-color:#0d6c6b;}" +
    "#cw-inputrow{display:flex;gap:8px;padding:10px 12px;border-top:1px solid #e2ddd2;background:#fffdf9;}" +
    "#cw-input{flex:1;min-height:36px;padding:8px 12px;font-size:13.5px;border:1px solid #d9d9d2;border-radius:8px;outline:none;}" +
    "#cw-input:focus{border-color:#0d6c6b;}" +
    "#cw-send{width:56px;border:0;border-radius:8px;background:#d76e39;color:#fff;font-size:13px;font-weight:700;cursor:pointer;}" +
    "#cw-send:disabled{opacity:.5;cursor:default;}" +
    ".cw-summary{margin:0;padding:12px 14px;font-size:12.5px;line-height:1.8;color:#334454;background:#fffdf9;border:1px solid #e2ddd2;border-radius:10px;align-self:flex-start;max-width:94%;}" +
    ".cw-summary b{color:#0d6c6b;}" +
    ".cw-consent{display:flex;gap:8px;align-items:flex-start;font-size:11.5px;color:#627180;line-height:1.5;align-self:flex-start;max-width:94%;}" +
    ".cw-consent input{margin-top:2px;}" +
    ".cw-submit{align-self:flex-start;min-height:40px;padding:0 18px;border:0;border-radius:8px;background:#d76e39;color:#fff;font-size:13.5px;font-weight:700;cursor:pointer;}" +
    ".cw-submit:disabled{opacity:.55;cursor:default;}" +
    "#cw-qr{width:150px;height:150px;border-radius:10px;border:1px solid #e2ddd2;background:#fff;}" +
    ".cw-note{font-size:10.5px;color:#94a1ad;text-align:center;padding:4px 10px 10px;background:#f6f3ed;}" +
    "@media (max-width:480px){#cw-panel{right:0;bottom:0;left:0;width:auto;height:min(85vh,620px);border-radius:14px 14px 0 0;}#cw-launcher{right:12px;bottom:12px;}}";

  var styleEl = document.createElement("style");
  styleEl.textContent = css;
  document.head.appendChild(styleEl);

  var root = document.createElement("div");
  root.id = "chat-widget-root";
  root.innerHTML =
    '<button id="cw-launcher" type="button">💬 ' + tr(T.launcher) + "</button>" +
    '<div id="cw-panel" role="dialog" aria-label="' + tr(T.title) + '">' +
    '<div id="cw-head"><div><div class="cw-title">Shenyuan · ' + tr(T.title) + '</div><span class="cw-badge">' + tr(T.badge) + "</span></div>" +
    '<button id="cw-human" type="button">👤 ' + tr(T.human) + "</button>" +
    '<button id="cw-close" type="button" aria-label="' + tr(T.close) + '">✕</button></div>' +
    '<div id="cw-msgs"></div>' +
    '<div id="cw-inputrow"><input id="cw-input" type="text" placeholder="' + tr(T.placeholder) + '" autocomplete="off"><button id="cw-send" type="button">' + tr(T.send) + "</button></div>" +
    '<div class="cw-note">' + tr(T.badge) + "</div></div>";
  document.body.appendChild(root);

  var launcher = root.querySelector("#cw-launcher");
  var panel = root.querySelector("#cw-panel");
  var msgs = root.querySelector("#cw-msgs");
  var inputEl = root.querySelector("#cw-input");
  var sendBtn = root.querySelector("#cw-send");

  launcher.addEventListener("click", function () {
    panel.classList.add("open");
    launcher.style.display = "none";
    inputEl.focus();
  });
  root.querySelector("#cw-close").addEventListener("click", function () {
    panel.classList.remove("open");
    launcher.style.display = "";
  });
  root.querySelector("#cw-human").addEventListener("click", showHuman);

  /* ---------- helpers ---------- */
  function addMsg(cls, html) {
    var d = document.createElement("div");
    d.className = cls;
    d.innerHTML = html;
    msgs.appendChild(d);
    msgs.scrollTop = msgs.scrollHeight;
    return d;
  }
  function bot(html) {
    addMsg("cw-bot", html);
    transcript.push("bot: " + html.replace(/<[^>]+>/g, " "));
  }
  function user(text) {
    addMsg("cw-user", text);
    transcript.push("user: " + text);
  }
  function setInput(visible, placeholder) {
    inputEl.style.display = visible ? "" : "none";
    sendBtn.style.display = visible ? "" : "none";
    if (visible) {
      inputEl.placeholder = placeholder || tr(T.placeholder);
      inputEl.value = "";
      inputEl.focus();
    }
  }
  function chips(options, onPick, multi) {
    var wrap = document.createElement("div");
    wrap.className = "cw-chips";
    options.forEach(function (opt) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "cw-chip";
      b.textContent = opt.zh === opt.en ? opt.zh : (L === "zh" ? opt.zh : opt.en);
      b.addEventListener("click", function () {
        if (multi) {
          b.classList.toggle("on");
          onPick(opt.v, b.classList.contains("on"));
        } else {
          onPick(opt.v);
        }
      });
      wrap.appendChild(b);
    });
    msgs.appendChild(wrap);
    msgs.scrollTop = msgs.scrollHeight;
    return wrap;
  }
  function addSkip(onSkip) {
    var b = document.createElement("button");
    b.type = "button";
    b.className = "cw-chip";
    b.textContent = tr(T.skip);
    b.addEventListener("click", onSkip);
    msgs.appendChild(b);
  }
  function summaryHtml() {
    return buildSummary()
      .split("；")
      .filter(Boolean)
      .map(function (s) {
        var i = s.indexOf("：");
        return i > 0 ? "<b>" + s.slice(0, i + 1) + "</b>" + s.slice(i + 1) : s;
      })
      .join("<br>");
  }
  function buildSummary() {
    var LBL = T.labels;
    var parts = [
      (L === "zh" ? "业务类型" : "Area") + "：" + ({ trade: { zh: "国际贸易争议", en: "International trade dispute" }, recovery: { zh: "诉讼与债务追收", en: "Litigation & debt recovery" }, legacy: { zh: "继承与家族资产纠纷", en: "Inheritance & family assets" }, unsure: { zh: "不确定，先沟通", en: "Not sure yet" } }[state.business] || {})[L],
      (L === "zh" ? "双方身份" : "Parties") + "：" + state.parties,
      (L === "zh" ? "金额" : "Amount") + "：" + (state.amount || "-"),
      (L === "zh" ? "时间" : "Timing") + "：" + (state.timeline || "-"),
      (L === "zh" ? "材料" : "Documents") + "：" + (state.evidence || "-"),
      (L === "zh" ? "诉求" : "Goal") + "：" + (state.goal || "-"),
      (L === "zh" ? "国家/地区" : "Country") + "：" + (state.country || "-"),
    ];
    return parts.join("；") + "。";
  }
  function submitIntake() {
    sendBtn.disabled = true;
    var payload = {
      name: state.name,
      contact: state.contact,
      matter: state.business,
      summary: buildSummary(),
      parties: state.parties,
      amount: state.amount,
      timeline: state.timeline,
      evidence: state.evidence,
      goal: state.goal,
      country: state.country || null,
      language: L,
      consent: state.consent,
      source: new URLSearchParams(window.location.search).get("utm_source") || "",
      transcript: transcript.join("\n").slice(-4000),
    };
    fetch("/api/intakes/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
      .then(function (resp) {
        if (resp.status === 201) {
          // GA4 conversion: chat intake completion counts as a lead.
          if (window.gtag) {
            gtag("event", "generate_lead", { event_category: "intake", event_label: "chat" });
          }
          bot("<strong>" + tr(T.done_title) + "</strong><br>" + tr(T.done_body));
          setInput(false);
          return;
        }
        return resp.json().then(function (data) {
          var detail = (data && data.detail) || "";
          if (resp.status === 409) {
            bot(tr(T.dup_body));
          } else if (resp.status === 400) {
            bot(detail || tr(T.consent_err));
          } else {
            bot(tr(T.err_body));
          }
          sendBtn.disabled = false;
        });
      })
      .catch(function () {
        bot(tr(T.err_body));
        sendBtn.disabled = false;
      });
  }

  function showHuman() {
    setInput(false);
    bot("<strong>" + tr(T.human_title) + "</strong><br>" + tr(T.human_body));
    var img = document.createElement("img");
    img.id = "cw-qr";
    img.src = "/wechat-qrcode.png";
    img.alt = "WeChat QR";
    msgs.appendChild(img);
    msgs.scrollTop = msgs.scrollHeight;
  }

  /* ---------- flow ---------- */
  function next() {
    stepIndex += 1;
    var s = steps[stepIndex];
    if (s) {
      s();
    } else {
      setInput(false);
    }
  }

  var steps = [
    function stepIntro() {
      bot(tr(T.intro));
      bot(tr(T.q_business));
      chips(T.opt_business, function (v) {
        state.business = v;
        user(tr({ trade: { zh: "国际贸易争议", en: "International trade dispute" }, recovery: { zh: "诉讼与债务追收", en: "Litigation & debt recovery" }, legacy: { zh: "继承与家族资产纠纷", en: "Inheritance & family assets" }, unsure: { zh: "不确定，先沟通", en: "Not sure yet" } }[v]));
        next();
      });
      setInput(false);
    },
    function stepParties() {
      bot(tr(T.q_parties));
      setInput(true);
      sendBtn.onclick = function () {
        var v = inputEl.value.trim();
        if (!v) return;
        state.parties = v;
        user(v);
        next();
      };
      inputEl.onkeydown = function (e) {
        if (e.key === "Enter") sendBtn.click();
      };
    },
    function stepAmount() {
      bot(tr(T.q_amount));
      chips(T.opt_amount, function (v) {
        state.amount = v;
        user(tr({ zh: { "5万以下": "5万以下", "5-50万": "5-50万", "50万以上": "50万以上", 不确定: "不确定" }[v] || v, en: v }));
        next();
      });
      setInput(true);
      sendBtn.onclick = function () {
        var v = inputEl.value.trim();
        if (!v) return;
        state.amount = v;
        user(v);
        next();
      };
      inputEl.onkeydown = function (e) {
        if (e.key === "Enter") sendBtn.click();
      };
    },
    function stepTimeline() {
      bot(tr(T.q_timeline));
      chips(T.opt_timeline, function (v) {
        state.timeline = v;
        user(tr({ zh: v, en: v }));
        next();
      });
      setInput(true);
      sendBtn.onclick = function () {
        var v = inputEl.value.trim();
        if (!v) return;
        state.timeline = v;
        user(v);
        next();
      };
      inputEl.onkeydown = function (e) {
        if (e.key === "Enter") sendBtn.click();
      };
    },
    function stepEvidence() {
      bot(tr(T.q_evidence));
      var chosen = [];
      chips(
        T.opt_evidence,
        function (v, on) {
          if (v === "暂时没有" || v === "None yet") {
            state.evidence = tr({ zh: "暂时没有", en: "None yet" });
          } else {
            var key = tr({ zh: v, en: v });
            if (on && chosen.indexOf(key) === -1) chosen.push(key);
            if (!on) chosen = chosen.filter(function (c) { return c !== key; });
            state.evidence = chosen.join("、");
          }
        },
        true
      );
      // multi-select step: explicit "done" chip to advance
      var done = document.createElement("button");
      done.type = "button";
      done.className = "cw-chip";
      done.textContent = tr({ zh: "完成选择 ✓", en: "Done ✓" });
      done.addEventListener("click", function () {
        next();
      });
      msgs.appendChild(done);
      setInput(true);
      sendBtn.onclick = function () {
        var v = inputEl.value.trim();
        if (!v) return;
        state.evidence = state.evidence ? state.evidence + "、" + v : v;
        user(v);
        next();
      };
      inputEl.onkeydown = function (e) {
        if (e.key === "Enter") sendBtn.click();
      };
    },
    function stepGoal() {
      bot(tr(T.q_goal));
      chips(T.opt_goal, function (v) {
        state.goal = v;
        user(tr({ zh: v, en: v }));
        next();
      });
      setInput(true);
      sendBtn.onclick = function () {
        var v = inputEl.value.trim();
        if (!v) return;
        state.goal = v;
        user(v);
        next();
      };
      inputEl.onkeydown = function (e) {
        if (e.key === "Enter") sendBtn.click();
      };
    },
    function stepCountry() {
      bot(tr(T.q_country));
      setInput(true);
      sendBtn.onclick = function () {
        var v = inputEl.value.trim();
        state.country = v;
        if (v) user(v);
        next();
      };
      inputEl.onkeydown = function (e) {
        if (e.key === "Enter") sendBtn.click();
      };
      addSkip(function () {
        next();
      });
    },
    function stepName() {
      bot(tr(T.q_name));
      setInput(true);
      sendBtn.onclick = function () {
        var v = inputEl.value.trim();
        if (!v) return;
        state.name = v;
        user(v);
        next();
      };
      inputEl.onkeydown = function (e) {
        if (e.key === "Enter") sendBtn.click();
      };
    },
    function stepContact() {
      bot(tr(T.q_contact));
      setInput(true);
      sendBtn.onclick = function () {
        var v = inputEl.value.trim();
        if (v.length < 2) return;
        state.contact = v;
        user(v);
        next();
      };
      inputEl.onkeydown = function (e) {
        if (e.key === "Enter") sendBtn.click();
      };
    },
    function stepReview() {
      setInput(false);
      var sum = document.createElement("div");
      sum.className = "cw-summary";
      sum.innerHTML = "<b>" + tr(T.review_title) + "</b><br>" + summaryHtml();
      msgs.appendChild(sum);
      var consent = document.createElement("label");
      consent.className = "cw-consent";
      var cb = document.createElement("input");
      cb.type = "checkbox";
      consent.appendChild(cb);
      consent.appendChild(document.createTextNode(tr(T.review_consent)));
      msgs.appendChild(consent);
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "cw-submit";
      btn.textContent = tr(T.submit);
      btn.disabled = true;
      cb.addEventListener("change", function () {
        state.consent = cb.checked;
        btn.disabled = !cb.checked;
      });
      btn.addEventListener("click", function () {
        btn.textContent = tr(T.submitting);
        submitIntake();
      });
      msgs.appendChild(btn);
      msgs.scrollTop = msgs.scrollHeight;
    },
  ];

  steps[stepIndex]();
})();
