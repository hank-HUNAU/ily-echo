# -*- coding: utf-8 -*-
"""v42 组 1（屏 1-6）照稿重画：CSS 原样搬运 + 六个渲染函数改写。
原则：稿内 .scr 的 DOM 结构 = 唯一蓝本；类名与稿完全一致；只把评审外壳 .phone/.status
换成安全区，假状态栏不保留。
"""
from pathlib import Path

P = Path(r"E:\04 少儿原版课程\06 新概念英语\ily-echo\v42\index.html")
src = P.read_text(encoding="utf-8")

# ────────────────────────────── 1. CSS 块：照稿 :41-137 搬运 ──────────────────────────────
CSS_NEW = r"""/* ===== v42 原型 · 设计稿 v4.2 样式表原样搬运 =====
   来源：设计稿_五段流程_v4_2.html :64-137（屏内组件），变量 :30-35
   差异仅两处：① 评审外壳 .phone/.status（假 9:41 状态栏 + 8px 边框）→ 安全区
              ② 容器 .scr → #app.v42-lesson 自身（去掉外包一层） */
body:has(#app.v42-lesson) .wrap{padding:0;max-width:none}
body:has(#app.v42-lesson) nav.tabs{display:none}
#app.v42-lesson{
 --ink:#263039;--sub:#5C6773;--line:#E2E6EB;--bg:#F4F6F8;
 --focus:#0B8A5F;--focusDeep:#08704D;--brand:#10B981;--brandSoft:#E6F7F0;
 --amber:#C08A3E;--amberInk:#8A5E22;--bad:#B04A43;--card:#fff;
 background:var(--bg);color:var(--ink);
 height:100vh;height:100dvh;overflow:hidden;
 display:flex;flex-direction:column;position:relative}
#app.v42-lesson *{box-sizing:border-box}
/* —— 顶栏（稿 .khead）：屏 1 L1·私人谈话 / 屏 2 精听·第n/m句 / 屏 3-4 跟读·全篇
      / 屏 5 背诵·全篇·仅中文 / 屏 6 本课完成 —— */
#app.v42-lesson .khead{display:flex;justify-content:space-between;align-items:center;
 padding:calc(6px + env(safe-area-inset-top,0px)) 20px 2px;color:var(--sub);font-size:12.5px;flex:0 0 auto}
#app.v42-lesson .khead a{color:var(--sub);text-decoration:none}
/* —— 四段流程条（稿 .flownav）：只读指示，不可点切段（11-17 拍板） —— */
#app.v42-lesson .flownav{display:flex;align-items:center;justify-content:center;gap:3px;
 padding:7px 8px 9px;border-bottom:1px solid var(--line);background:transparent;flex:0 0 auto}
#app.v42-lesson .fn{display:flex;flex-direction:column;align-items:center;gap:2px;
 width:58px;font-size:10.5px;color:var(--sub)}
#app.v42-lesson .fni{width:22px;height:22px;border-radius:50%;border:1.5px solid var(--line);
 display:flex;align-items:center;justify-content:center;font-size:10px;font-style:normal;font-weight:600}
#app.v42-lesson .fn.on{color:var(--focusDeep)}
#app.v42-lesson .fn.on .fni{border-color:var(--focus);background:#EDF1F4;color:var(--focusDeep)}
#app.v42-lesson .fn.done .fni{background:var(--focus);border-color:var(--focus);color:#fff}
#app.v42-lesson .fnar{color:var(--line);font-size:11px}
/* —— 舞台容器 —— */
#app.v42-lesson #stage{flex:1;min-height:0;display:flex;flex-direction:column;overflow:hidden}
#app.v42-lesson .body{flex:1;min-height:0;display:flex;flex-direction:column;overflow:hidden}
#app.v42-lesson .kstage{flex:1;min-height:0;display:flex;flex-direction:column;
 justify-content:center;overflow-y:auto;-webkit-overflow-scrolling:touch}
/* —— 文本层（稿 .title/.subtle/.big/.zhline） —— */
#app.v42-lesson .title{font-size:20px;font-weight:700;text-align:center;margin:6px 0 2px}
#app.v42-lesson .subtle{font-size:12.5px;color:var(--sub);text-align:center;line-height:1.6}
#app.v42-lesson .hint{font-size:12.5px;color:var(--sub);text-align:center}
#app.v42-lesson .big{font-family:Georgia,"Times New Roman",serif;font-size:21px;
 line-height:1.55;color:var(--ink);text-align:center}
#app.v42-lesson .zhline{font-size:14px;color:var(--sub);line-height:1.6;text-align:center}
/* —— 按钮（稿 .fbtn）：主按钮 54 / sm 44 / ghost 描边 —— */
#app.v42-lesson .fbtn{display:flex;align-items:center;justify-content:center;gap:8px;border:0;
 border-radius:16px;font-family:inherit;font-size:16px;font-weight:600;min-height:54px;
 background:var(--focus);color:#fff;cursor:pointer;width:100%}
#app.v42-lesson .fbtn:disabled{opacity:.45}
#app.v42-lesson .fbtn.ghost{background:transparent;color:var(--sub);font-size:14px;
 font-weight:500;border:1.5px solid var(--line)}
#app.v42-lesson .fbtn.sm{min-height:44px;font-size:13.5px;border-radius:12px;width:auto}
/* —— 选项（稿 .opt）：24px 圆徽 + 描边卡 —— */
#app.v42-lesson .opt{display:flex;align-items:center;gap:10px;width:100%;
 border:1.5px solid var(--line);background:#fff;border-radius:14px;padding:11px 12px;
 font-size:14.5px;text-align:left;color:var(--ink);font-family:inherit;cursor:pointer}
#app.v42-lesson .opt b{flex:0 0 24px;height:24px;border-radius:50%;background:#F1F3F5;
 color:var(--sub);font-size:12px;display:flex;align-items:center;justify-content:center}
#app.v42-lesson .opt.right{border-color:var(--focus);background:var(--brandSoft)}
#app.v42-lesson .opt.wrong{border-color:var(--bad);background:#FCEBEB}
/* —— 分段选择器（稿 .seg）：中/英/双语 · 1遍/3遍 同构 —— */
#app.v42-lesson .seg{display:flex;gap:3px;background:#F1F3F5;border-radius:999px;padding:3px}
#app.v42-lesson .seg span{padding:5px 11px;border-radius:999px;font-size:12px;
 color:var(--sub);white-space:nowrap;cursor:pointer}
#app.v42-lesson .seg span.on{background:#fff;color:var(--focusDeep);font-weight:600}
/* —— Anki 句卡（稿 .ankiCard）：白卡 + 中性描边，★ 收藏在右上角 —— */
#app.v42-lesson .ankiCard{background:var(--card);border:1px solid var(--line);border-radius:16px;
 padding:14px 16px;display:flex;flex:1;flex-direction:column;min-height:0;
 touch-action:pan-y;user-select:none}
#app.v42-lesson .ankiTop{display:flex;justify-content:space-between;align-items:center;
 font-size:11.5px;color:var(--sub)}
#app.v42-lesson .ankiTag{background:var(--brandSoft);color:var(--focusDeep);border-radius:999px;
 padding:3px 9px;font-weight:600}
#app.v42-lesson .ankiFav{color:var(--amberInk);font-size:14px;font-weight:600;cursor:pointer}
#app.v42-lesson .ankiFav.on{color:var(--focus)}
#app.v42-lesson .ankiBody{flex:1;display:flex;flex-direction:column;justify-content:center;
 gap:10px;text-align:center}
#app.v42-lesson .ankiFoot{display:flex;justify-content:space-between;font-size:11px;color:var(--sub);
 border-top:1px solid var(--line);padding-top:8px;margin-top:8px}
/* —— 通用卡（稿 .card/.pill） —— */
#app.v42-lesson .card{background:#fff;border:1px solid var(--line);border-radius:14px;padding:12px 14px}
#app.v42-lesson .pill{display:inline-flex;align-items:center;gap:5px;border-radius:999px;
 padding:4px 10px;font-size:11.5px;background:#EDF1F4;color:var(--focusDeep)}
#app.v42-lesson .pill.live{background:#E6F7F0;color:#0B8A5F}
/* —— 跟读/精听播放条 —— */
#app.v42-lesson .v42-play{background:#fff;border-top:1px solid var(--line);
 padding:0 24px 6px;flex:0 0 auto}
#app.v42-lesson .v42-prog{background:#fff;border-top:1px solid var(--line);
 padding:0 24px 6px;flex:0 0 auto}
#app.v42-lesson .v42-time{display:flex;justify-content:space-between;font-size:11px;
 color:#6C757D;font-variant-numeric:tabular-nums;padding-top:6px}
#app.v42-lesson .v42-track{height:4px;background:#E3E5E8;border-radius:2px;position:relative}
#app.v42-lesson .v42-track i{position:absolute;left:0;top:0;height:4px;background:var(--focus);
 border-radius:2px}
#app.v42-lesson .v42-track b{position:absolute;top:-5px;width:14px;height:14px;border-radius:50%;
 background:var(--focus);border:2.5px solid #fff;margin-left:-7px}
#app.v42-lesson .v42-clock{font-size:11px;color:#6C757D;font-variant-numeric:tabular-nums;white-space:nowrap}
#app.v42-lesson .v42-ctl{display:flex;align-items:center;justify-content:center;gap:26px;
 padding:4px 20px calc(10px + env(safe-area-inset-bottom,0px));background:#fff;flex:0 0 auto}
#app.v42-lesson .v42-mini{width:44px;height:44px;display:flex;align-items:center;
 justify-content:center;cursor:pointer;background:transparent;border:0}
#app.v42-lesson .v42-mini svg{width:26px;height:26px}
#app.v42-lesson .v42-main{width:56px;height:56px;border-radius:50%;background:var(--focus);
 display:flex;align-items:center;justify-content:center;cursor:pointer;border:0;flex:0 0 56px}
#app.v42-lesson .v42-main svg{width:24px;height:24px}
/* —— 跟读工具条（稿 .ktool）：三件同族 34px 全圆，选择器靠左、主按钮靠右 —— */
#app.v42-lesson .ktool{display:flex;align-items:center;justify-content:flex-start;gap:10px;
 padding:8px 12px;border-top:1px solid var(--line);background:#fff;flex:0 0 auto}
#app.v42-lesson .ktool .seg{padding:3px}
#app.v42-lesson .ktool .seg span{padding:7px 10px;font-size:12px;line-height:1.2}
#app.v42-lesson .ktool .fbtn.sm{min-height:34px;min-width:0;border-radius:999px;font-size:13px;
 font-weight:600;padding:0 15px;flex:0 0 auto;margin-left:auto}
/* —— 正文行（稿 .krow）：焦点 21px 加粗，其余虚化 32% —— */
#app.v42-lesson .krow{padding:5px 18px;text-align:center}
#app.v42-lesson .krow .en{font-family:Georgia,"Times New Roman",serif;font-size:16px;
 line-height:1.4;color:var(--ink)}
#app.v42-lesson .krow .zh{font-size:12px;color:var(--sub);margin-top:2px}
#app.v42-lesson .krow.dim{opacity:.32}
#app.v42-lesson .krow.now .en{font-size:21px;font-weight:700}
#app.v42-lesson .krow.now .zh{font-size:18px;color:var(--ink);font-weight:600;margin-top:2px}
/* —— 录音分段进度（稿屏 5）：深绿已录 / 亮绿当前 / 灰未录 —— */
#app.v42-lesson .rsegs{display:flex;gap:4px}
#app.v42-lesson .rseg{flex:1;height:5px;border-radius:3px;background:#E3E5E8}
#app.v42-lesson .rseg.done{background:var(--focus)}
#app.v42-lesson .rseg.now{background:var(--brand)}
#app.v42-lesson .v42-ctl.rctl{gap:18px}
#app.v42-lesson .v42-ctl.rctl .fbtn.sm{min-width:88px}
#app.v42-lesson .v42-ctl.rctl .fbtn.sm.done{border-color:var(--focus);color:var(--focusDeep)}
/* —— 横屏（稿 .phone.land）：隐藏流程条 + 可用高仅 230px 须压行距（11-19 修正） —— */
@media (orientation:landscape){
  #app.v42-lesson .flownav{display:none}
  #app.v42-lesson .kstage{flex:0 0 230px;height:230px;padding:2px 0}
  #app.v42-lesson .krow{padding:2px 18px}
  #app.v42-lesson .krow .en{line-height:1.32}
  #app.v42-lesson .krow .zh{margin-top:0}
  #app.v42-lesson .krow.now .en{font-size:19px}
  #app.v42-lesson .land-only{display:block}
  #app.v42-lesson .port-only{display:none}
}
@media (orientation:portrait){
  #app.v42-lesson .land-only{display:none}
  #app.v42-lesson .port-only{display:block}
  #app.v42-lesson .port-only.v42-ctl{display:flex}
}
"""

i = src.index("/* ===== v42 原型")
j = src.index("\n</style>", i)
src = src[:i] + CSS_NEW + src[j:]
print("CSS ok", len(CSS_NEW))

# ────────────────────────────── 2. router：挂 v42-lesson 类 ──────────────────────────────
old = """async function router(){
  nav();
  const h=location.hash||'#/home';
"""
new = """async function router(){
  nav();
  const h=location.hash||'#/home';
  /* v42：课文页挂稿作用域类；其余页（我的课程/教材页/课程库/听单）保持主 App 现状 */
  $('#app').className = h.startsWith('#/lesson/') ? 'v42-lesson' : '';
"""
assert old in src
src = src.replace(old, new, 1)
print("router ok")


def swap(start_mark, end_mark, body, tag):
    global src
    a = src.index(start_mark)
    b = src.index(end_mark, a)
    src = src[:a] + body + src[b:]
    print(tag, "ok")


# ────────────────────── 3. renderLesson + flowNav（屏 1-6 公共外壳） ──────────────────────
RENDER_LESSON = r"""function renderLesson(){
  const p=prog(CUR.no), d=CUR.data;
  const rev=CUR.mode==='rev';
  if(rev){
    /* 屏 7/8 尚未按稿重画：摘掉稿作用域类，按「保留现状」走主 App 样式 */
    if(CUR.revDoneShown){ $('#app').className=''; return renderRevDone(); }
    if(CUR.rstep==null){ $('#app').className=''; return renderRevEntry(p,d); }
  }
  const app=$('#app'); app.className='v42-lesson';
  const cur=rev?CUR.rstep:(p.stage??0);
  const body=Math.max(1,d.sentences.length-1);     /* 正文句数＝sentences[1..]，题干句不计 */
  const recDone=!rev&&cur===3&&CUR.rec&&CUR.rec.state==='done';
  /* .khead 左文案随当前段变化（照稿逐屏） */
  let head;
  if(recDone) head='本课完成';
  else if(!rev&&cur===0) head=`L${d.no} · ${esc(d.titleZh)}`;
  else if(cur===(rev?0:1)) head=`精听 · 第 ${CUR.intSi||1} / ${body} 句`;
  else if(cur===(rev?1:2)) head='跟读 · 全篇';
  else head='背诵 · 全篇 · 仅中文';
  app.innerHTML=`<div class="khead"><span>${head}</span><a href="#/c/${curCourse()}">‹ 退出</a></div>
  ${flowNav(rev,cur,recDone)}
  <div id="stage"></div>`;
  renderStage();
}
/* 四段流程条：只读指示。首学按 stage 推进；复习从精听起，盲听恒显示已完成（7 轮不重跑） */
function flowNav(rev,cur,done){
  const names=['盲听','精听','跟读','录音'];
  const base=rev?cur+1:cur;                        /* 复习第 0 段＝精听，对应段号 1 */
  let h='';
  names.forEach((nm,n)=>{
    let cls='',mark=String(n+1);
    if(done){ cls='done'; mark='✓'; }
    else if(rev&&n===0){ cls='done'; mark='✓'; }
    else if(n<base){ cls='done'; mark='✓'; }
    else if(n===base){ cls='on'; }
    h+=(n?'<span class="fnar">·</span>':'')+`<span class="fn ${cls}"><i class="fni">${mark}</i>${nm}</span>`;
  });
  return `<div class="flownav">${h}</div>`;
}
"""
swap("function renderLesson(){", "\n/* —— 屏 7：到期入口", RENDER_LESSON, "renderLesson")

# ────────────────────────────── 4. stageIntensive（屏 2） ──────────────────────────────
STAGE_INT = r"""/* —— 精听（稿屏 2）：Anki 句卡 + 右上角 ★ 收藏；语言三档上移到播放条上方右对齐 —— */
function stageIntensive(){
  const p=prog(CUR.no), d=CUR.data;
  const body=Math.max(1,d.sentences.length-1);     /* 题干句不入句卡 */
  if(CUR.intSi==null||CUR.intSi<1||CUR.intSi>body) CUR.intSi=(p.si>=1&&p.si<=body)?p.si:1;
  if(!CUR.lang) CUR.lang='bi';                     /* 中/英/双语，与跟读共用 */
  const i=CUR.intSi, s=d.sentences[i]||{};
  const star=p.hard.includes(i);
  const seg=(v,label)=>`<span class="${CUR.lang===v?'on':''}" data-act="intlang" data-v="${v}">${label}</span>`;
  const total=d.duration||76, t0=s.t||0;
  const pct=Math.min(100,Math.round(t0*100/(total||1)));
  /* 卡片只负责呈现：播放/切换统一走底部条（稿：删「跟读一次」「下一句」） */
  return `<div class="body" style="padding:10px 18px 8px">
    <div class="ankiCard" id="intCard">
      <div class="ankiTop"><span class="ankiTag">句卡 ${i} / ${body}</span>
        <span class="ankiFav${star?' on':''}" data-act="star" data-i="${i}">★ ${star?'已收藏':'收藏'}</span></div>
      <div class="ankiBody">
        ${CUR.lang==='zh'?'':`<div class="big">${esc(s.en||'')}</div>`}
        ${CUR.lang==='en'?'':`<div class="zhline">${esc(s.zh||'')}</div>`}
      </div>
      <div class="ankiFoot"><span>点播放听本句</span><span>${pad((p.reviews||0)+1)} / ${pad(OFFSETS.length)} 轮</span></div>
    </div>
  </div>
  <div class="v42-play">
    <div style="display:flex;align-items:center;justify-content:flex-end;padding:4px 0 2px">
      <div class="seg">${seg('zh','中')}${seg('en','英')}${seg('bi','双语')}</div></div>
    <div class="v42-time"><span>${fmtSec(t0)}</span><span>${fmtSec(total)}</span></div>
    <div style="height:18px;display:flex;align-items:center">
      <div class="v42-track" style="width:100%"><i style="width:${pct}%"></i><b style="left:${pct}%"></b></div></div>
  </div>
  <div class="v42-ctl">
    <button class="v42-mini" data-act="intprev" aria-label="上一句"><svg viewBox="0 0 24 24" fill="var(--focus)"><path d="M6 5h2v14H6zM20 5l-10 7 10 7z"/></svg></button>
    <button class="v42-main" data-act="intplay" aria-label="播放本句"><svg viewBox="0 0 24 24" fill="#fff"><path d="M8 5l11 7-11 7z"/></svg></button>
    <button class="v42-mini" data-act="intnext" aria-label="下一句"><svg viewBox="0 0 24 24" fill="var(--focus)"><path d="M16 5h2v14h-2zM4 5l10 7-10 7z"/></svg></button>
  </div>
  <div style="padding:0 16px calc(8px + env(safe-area-inset-bottom,0px));background:#fff">
    <button class="fbtn ghost sm" style="width:100%" data-act="tostage" data-v="${CUR.mode==='rev'?1:2}">进入跟读 →</button>
  </div>`;
}
"""
swap("/* —— 精听：Anki 句卡 + 左右手势切卡（P2-2） —— */", "\n/* 绑定精听卡片左右手势", STAGE_INT, "stageIntensive")

# ────────────────────────── 5. stageShadow（屏 3 横 / 屏 4 竖） ──────────────────────────
STAGE_SH = r"""/* —— 跟读（稿屏 3 横屏 / 屏 4 竖屏）：同一容器，横屏紧凑播放条 + 竖屏完整三键 —— */
function stageShadow(){
  const p=prog(CUR.no), d=CUR.data;
  const total=Math.max(1,d.sentences.length-1);    /* 与精听同口径：题干句不进正文 */
  if(CUR.shSi==null||CUR.shSi<1||CUR.shSi>total) CUR.shSi=(p.si>=1&&p.si<=total)?p.si:1;
  if(!CUR.lang) CUR.lang='bi';
  if(!CUR.loops||(CUR.loops!==1&&CUR.loops!==3)) CUR.loops=1;   /* 只有 1↔3 两档 */
  const cur=CUR.shSi;
  let rows='';
  d.sentences.forEach((s,i)=>{
    if(i===0) return;
    const now=i===cur;
    const en=(CUR.lang==='zh')?'':`<div class="en">${esc(s.en)}</div>`;
    const zh=(CUR.lang==='en')?'':`<div class="zh">${esc(s.zh)}</div>`;
    rows+=`<div class="krow ${now?'now':'dim'}" data-act="shrow" data-i="${i}">${en}${zh}</div>`;
  });
  const segLang=['zh','en','bi'].map(v=>
    `<span class="${CUR.lang===v?'on':''}" data-act="intlang" data-v="${v}">${{zh:'中',en:'英',bi:'双语'}[v]}</span>`).join('');
  const segLoop=[1,3].map(n=>
    `<span class="${CUR.loops===n?'on':''}" data-act="loopsel" data-v="${n}">${n} 遍</span>`).join('');
  const secs=d.duration||76, t0=(d.sentences[cur]||{}).t||0;
  const pct=Math.min(100,Math.round(t0*100/(secs||1)));
  const icoPrev=`<svg viewBox="0 0 24 24" fill="var(--focus)"><path d="M6 5h2v14H6zM20 5l-10 7 10 7z"/></svg>`;
  const icoNext=`<svg viewBox="0 0 24 24" fill="var(--focus)"><path d="M16 5h2v14h-2zM4 5l10 7-10 7z"/></svg>`;
  const icoPlay=`<svg viewBox="0 0 24 24" fill="#fff"><path d="M8 5l11 7-11 7z"/></svg>`;
  return `<div class="kstage" id="kstage">${rows}</div>
  <div class="ktool">
    <div class="seg">${segLang}</div>
    <div class="seg">${segLoop}</div>
    <button class="fbtn sm" data-act="tostage" data-v="${CUR.mode==='rev'?2:3}">读完了 →</button>
  </div>
  <div class="v42-play land-only">
    <div style="display:flex;align-items:center;gap:10px;padding:6px 0 2px">
      <button data-act="shplay" aria-label="播放/暂停" style="width:28px;height:28px;border-radius:50%;background:var(--focus);display:flex;align-items:center;justify-content:center;border:0;flex:0 0 28px;cursor:pointer"><svg viewBox="0 0 24 24" fill="#fff" style="width:14px;height:14px"><path d="M8 5l11 7-11 7z"/></svg></button>
      <div class="v42-track" style="flex:1"><i style="width:${pct}%"></i><b style="left:${pct}%"></b></div>
      <span class="v42-clock">${fmtSec(t0)} / ${fmtSec(secs)}</span>
    </div>
  </div>
  <div class="v42-prog port-only">
    <div class="v42-time"><span>${fmtSec(t0)}</span><span>${fmtSec(secs)}</span></div>
    <div style="height:18px;display:flex;align-items:center">
      <div class="v42-track" style="width:100%"><i style="width:${pct}%"></i><b style="left:${pct}%"></b></div></div>
  </div>
  <div class="v42-ctl port-only">
    <button class="v42-mini" data-act="shprev" aria-label="上一句">${icoPrev}</button>
    <button class="v42-main" data-act="shplay" aria-label="播放/暂停">${icoPlay}</button>
    <button class="v42-mini" data-act="shnext" aria-label="下一句">${icoNext}</button>
  </div>`;
}
"""
swap("/* —— 跟读 —— */", "\n/* 聚焦到跟读某句", STAGE_SH, "stageShadow")

# ────────────────────────────── 6. stageBlind（屏 1） ──────────────────────────────
STAGE_BL = r"""/* —— 盲听（稿屏 1）：无字播 1 遍 → 出题；答对直入 / 答错重听 / 再错揭底（11-18 拍板） —— */
function stageBlind(){
  const d=CUR.data;
  if(!CUR.blind) CUR.blind={tries:0,showAnswer:false,phase:'playing',picked:-1};
  const B=CUR.blind, O=CUR.blindOpt;
  /* 播的期间只留一个聆听提示：不显示题干、选项、译文、答案（无说明句） */
  if(B.phase==='playing'){
    return `<div class="body" style="padding:14px 18px 8px;justify-content:center;gap:12px">
      <div class="big" style="font-size:22px;margin:0">仔细听</div></div>`;
  }
  const opts=(O&&O.options)||[];
  const optHtml=opts.map((o,i)=>{
    let cls='opt';
    if(B.showAnswer&&i===O.correctIdx) cls+=' right';
    else if(B.picked===i&&i!==O.correctIdx) cls+=' wrong';
    return `<button class="${cls}" data-act="blindpick" data-i="${i}"><b>${'ABC'[i]}</b><span>${esc(o)}</span></button>`;
  }).join('');
  if(B.showAnswer){
    /* 第 2 次仍错：直接揭底，再点「进入精听」（不计分、不写 reviews） */
    return `<div class="body" style="padding:14px 18px 8px;justify-content:center;gap:12px">
      <div class="big" style="font-size:18px;margin:0">${esc((d.question&&d.question.en)||'')}</div>
      <div style="display:flex;flex-direction:column;gap:9px">${optHtml}</div>
      <div class="zhline">正确答案：${'ABC'[O.correctIdx]} ${esc(opts[O.correctIdx]||'')}</div>
      <button class="fbtn" style="margin-top:2px" data-act="blind2jingting">进入精听 →</button></div>`;
  }
  return `<div class="body" style="padding:14px 18px 8px;justify-content:center;gap:12px">
    <div class="big" style="font-size:18px;margin:0">${esc((d.question&&d.question.en)||'')}</div>
    <div style="display:flex;flex-direction:column;gap:9px">${optHtml}</div>
    <button class="fbtn ghost sm" style="margin-top:8px;align-self:center" data-act="blindhint">显示中文提示</button>
    <div class="zhline" id="blindHint" style="display:none">${esc((d.question&&d.question.zh)||'')}</div></div>`;
}
"""
swap("/* —— 盲听：无字播 1 遍 → 出题 → 答对直入/答错重听/再错揭底（11-18 拍板） —— */",
     "\n/* 异步启动盲听播放", STAGE_BL, "stageBlind")

# ────────────────────────────── 7. stageRetell（屏 5） ──────────────────────────────
STAGE_RC = r"""/* —— 录音（稿屏 5）：全篇模式 · 只滚中文 · 断点录制 · 分段进度 —— */
function stageRetell(){
  const p=prog(CUR.no), d=CUR.data;
  const body=d.sentences.slice(1);                 /* 跳过第 0 句（题干），只滚课文正文 */
  const total=body.length;
  if(!CUR.rec) CUR.rec={state:'idle',baseEl:0,segStart:0,cur:0,totalMs:0};
  const R=CUR.rec;
  if(R.state==='done') return recDoneCard();       /* 屏 6：唯一完成卡 */
  const cur=Math.min(R.cur||0,total-1);
  const rows=body.map((s,i)=>{
    const done=i<cur, now=i===cur;
    return `<div class="krow ${now?'now':(done?'':'dim')}" data-act="recrow" data-i="${i}"><div class="zh">${esc(s.zh)}</div></div>`;
  }).join('');
  /* 句子级分段进度：深绿＝已录句、亮绿＝当前句、灰＝未录句 */
  const rsegs=[...Array(total)].map((_,i)=>{
    const c=i<cur?'done':(i===cur&&R.state==='recording'?'now':'');
    return `<span class="rseg ${c}"></span>`;
  }).join('');
  const stateLbl=R.state==='recording'?'● 录制中':R.state==='paused'?'已暂停':'未开始';
  let recHintSeen=false;
  try{ recHintSeen=!!localStorage.getItem(LS+'recHint'); }catch(e){}
  const pauseLbl=R.state==='paused'?'继续':'暂停';
  const el=R.baseEl+(R.state==='recording'?(Date.now()-R.segStart)/1000:0);
  const micR=R.state==='recording'
    ? `<svg viewBox="0 0 24 24" fill="#fff" style="width:20px;height:20px"><rect x="7" y="7" width="10" height="10" rx="2"/></svg>`
    : `<svg viewBox="0 0 24 24" fill="#fff" style="width:20px;height:20px"><rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/></svg>`;
  return `<div class="kstage" id="kstage">${rows}</div>
  <div class="ktool">
    <span class="pill">第 ${cur+1} / ${total} 句</span>
    <span class="pill${R.state==='recording'?' live':''}">${stateLbl}</span>
  </div>
  <div class="v42-prog">
    <div class="rsegs">${rsegs}</div>
    <div class="v42-time"><span class="rec-time-now">${fmtSec(el)}</span><span>${R.state==='paused'?'已录片段保留':'已录片段保留'}</span></div>
  </div>
  <div class="v42-ctl rctl">
    <button class="fbtn ghost sm" data-act="recpause" ${R.state==='idle'?'disabled':''}>${pauseLbl}</button>
    <button class="v42-main" data-act="rectoggle" aria-label="录音">${micR}</button>
    <button class="fbtn ghost sm done" data-act="recfinish" ${(R.state==='idle'&&!R.baseEl)?'disabled':''}>完成录音</button>
  </div>
  ${recHintSeen?'':`<div style="padding:0 18px calc(10px + env(safe-area-inset-bottom,0px));background:#fff"><div class="hint" id="recFirstHint" style="font-size:11.5px;padding-bottom:8px">断点录制可暂停继续，最后合成完整录音</div></div>`}
  ${R.error?`<div style="padding:0 18px 10px;background:#fff"><div class="hint" style="color:var(--bad)">录音不可用：${esc(R.error)}</div>
    <div style="text-align:center;margin-top:6px"><button class="fbtn ghost sm" data-act="recback">跳过录音，直接完成</button></div></div>`:''}`;
}
"""
swap("/* —— 录音：全篇模式（仅中文）· 断点录制 · 完成卡（屏 5/6） —— */",
     "\nfunction fmtSec(sec){", STAGE_RC, "stageRetell")

# ────────────────────── 8. fmtSec 改 mm:ss + recDoneCard（屏 6） ──────────────────────
OLD_TAIL = src[src.index("function fmtSec(sec){"):src.index("\n/* 录音控制：MediaRecorder")]
NEW_TAIL = r"""function fmtSec(sec){
  sec=Math.max(0,Math.round(sec||0));
  const m=Math.floor(sec/60), s=sec%60;
  return pad(m)+':'+pad(s);                        /* 统一 mm:ss，照稿 00:48 / 01:16 */
}
/* —— 屏 6：唯一完成卡（全篇模式），分享只留本机 —— */
function recDoneCard(){
  const p=prog(CUR.no), d=CUR.data, rev=CUR.mode==='rev';
  const dur=Math.round((CUR.rec.totalMs||0)/1000);
  const durTxt=dur>=60?Math.floor(dur/60)+' 分 '+(dur%60)+' 秒':dur+' 秒';
  return `<div class="body" style="padding:14px 18px calc(10px + env(safe-area-inset-bottom,0px))">
    <div class="card" style="margin-top:14px">
      <div class="title" style="margin:0">录音完成</div>
      <div class="subtle" style="margin-top:6px">第 ${d.no} 课 · ${esc(d.title)}</div>
      <div style="display:flex;justify-content:space-between;margin-top:16px;font-size:13px;color:var(--sub)"><span>录音方式</span><b style="color:var(--ink)">全篇模式（断点录制）</b></div>
      <div style="display:flex;justify-content:space-between;margin-top:8px;font-size:13px;color:var(--sub)"><span>用时</span><b style="color:var(--ink)">${durTxt}</b></div>
    </div>
    <div style="margin-top:auto;display:flex;flex-direction:column;gap:9px">
      <button class="fbtn" data-act="recshare">分享到微信群</button>
      <button class="fbtn ghost sm" data-act="recback">${rev?`完成第 ${(p.reviews||0)+1} 轮`:'完成，返回课程'}</button>
    </div>
  </div>`;
}
"""
src = src.replace(OLD_TAIL, NEW_TAIL, 1)
print("fmtSec+recDoneCard ok")

# ────────────────────── 9. shprev / shnext 事件（竖屏三键） ──────────────────────
old = "  else if(act==='shrow'){ shFocus(+el.dataset.i); }"
new = """  else if(act==='shrow'){ shFocus(+el.dataset.i); }
  else if(act==='shprev'){ shFocus((CUR.shSi||1)-1); }
  else if(act==='shnext'){ shFocus((CUR.shSi||1)+1); }"""
assert old in src
src = src.replace(old, new, 1)
print("shprev/shnext ok")

P.write_text(src, encoding="utf-8")
print("written", P, len(src))
