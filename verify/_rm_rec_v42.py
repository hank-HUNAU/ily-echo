# -*- coding: utf-8 -*-
"""v42：删除四段流程中的录音段 → 三段流程 + 学习完成卡；复习三段 → 两段。
保留：难句补练的逐句录音（独立功能，不属四段流程）。
"""
from pathlib import Path

P = Path(r"E:\04 少儿原版课程\06 新概念英语\ily-echo\v42\index.html")
src = P.read_text(encoding="utf-8")


def rep(old, new, tag, n=1):
    global src
    assert old in src, "MISS " + tag
    src = src.replace(old, new, n)
    print("ok", tag)


def swap(start, end, new, tag):
    global src
    a = src.index(start)
    b = src.index(end, a)
    src = src[:a] + new + src[b:]
    print("ok", tag)


# ── 1. 常量与复习段数 ──
rep("const STAGES=['盲听','精听','跟读','录音'];",
    "const STAGES=['盲听','精听','跟读'];      /* 11-23 用户定：删录音段，三段 + 学习完成卡 */",
    "STAGES")
rep("const REV_STEPS=['精听','跟读','录音'];",
    "const REV_STEPS=['精听','跟读'];           /* 11-23：复习随首学改为两段 */",
    "REV_STEPS")
rep("   revDone 只对「当前轮」有效，换轮自动重置；seen 记录精听已走过的句卡，跨会话保留。\n   三段齐了才 reviews+1 —— 不允许「点一次就记账」。 */",
    "   revDone 只对「当前轮」有效，换轮自动重置；seen 记录精听已走过的句卡，跨会话保留。\n   两段齐了才 reviews+1 —— 不允许「点一次就记账」。 */",
    "rev 注释1")
rep("if(!p.revDone||typeof p.revDone!=='object'||p.revDone.r!==r) p.revDone={r:r,s:[false,false,false],seen:{}};",
    "if(!p.revDone||typeof p.revDone!=='object'||p.revDone.r!==r) p.revDone={r:r,s:[false,false],seen:{}};",
    "revState init")
rep("if(!Array.isArray(p.revDone.s)||p.revDone.s.length!==3) p.revDone.s=[false,false,false];",
    "if(!Array.isArray(p.revDone.s)||p.revDone.s.length!==REV_STEPS.length) p.revDone.s=[false,false];",
    "revState len")
rep("/* 本轮收尾：三段齐了才 reviews+1；超 3 天宽限记未通关；随后进屏 8 */",
    "/* 本轮收尾：两段齐了才 reviews+1；超 3 天宽限记未通关；随后进屏 8 */",
    "rev 注释2")
rep("  CUR.rec=null; CUR.rstep=null;               /* 保留 CUR.blob：屏 8 的「分享给家人」要用 */",
    "  CUR.rstep=null;                             /* 11-23：录音段已删，屏 8 不再有分享录音 */",
    "finishReview 尾部")

# ── 2. 课程描述与引导文案 ──
rep("desc:'96 课 · 盲听 / 精听 / 跟读 / 录音 + 7 轮复习'",
    "desc:'96 课 · 盲听 / 精听 / 跟读 + 7 轮复习'",
    "课程描述")
rep('<div class="item"><div class="tt"><div class="en">③ 录音 → 等 7 轮复习</div><div class="meta">全篇中文提示下脱稿背诵录音；系统自动排 7 轮复习提醒（红点提示）</div></div></div>',
    '<div class="item"><div class="tt"><div class="en">③ 读完 → 等 7 轮复习</div><div class="meta">跟读完成后系统自动排 7 轮复习提醒（红点提示）</div></div></div>',
    "引导卡")

# ── 3. 流程条：四段 → 三段 ──
rep("/* 四段流程条：只读指示。首学按 stage 推进；复习从精听起，盲听恒显示已完成（7 轮不重跑） */",
    "/* 三段流程条：只读指示。首学按 stage 推进；复习从精听起，盲听恒显示已完成（7 轮不重跑） */",
    "flowNav 注释")
rep("  const names=['盲听','精听','跟读','录音'];\n  const base=rev?cur+1:cur;",
    "  const names=STAGES;\n  const base=rev?cur+1:cur;",
    "flowNav names")

# ── 4. renderLesson：完成卡判定 ──
rep("  const recDone=!rev&&cur===3&&CUR.rec&&CUR.rec.state==='done';\n  /* .khead 左文案随当前段变化（照稿逐屏） */\n  let head;\n  if(recDone) head='本课完成';",
    "  const doneCard=!rev&&cur>=STAGES.length;      /* 跟读完 → 学习完成卡（不再是第四段） */\n  /* .khead 左文案随当前段变化（照稿逐屏） */\n  let head;\n  if(doneCard) head='本课完成';",
    "renderLesson doneCard")
rep("  else if(cur===(rev?1:2)) head='跟读 · 全篇';\n  else head='背诵 · 全篇 · 仅中文';",
    "  else head='跟读 · 全篇';",
    "renderLesson head 兜底")
rep("  ${flowNav(rev,cur,recDone)}", "  ${flowNav(rev,cur,doneCard)}", "flowNav 调用")

# ── 5. renderStage：三段 + 完成卡 ──
old = """  if(rev){
    /* 复习三段：精听 → 跟读 → 录音（无盲听、无难句补练） */
    el.innerHTML=[stageIntensive,stageShadow,stageRetell][step]();
  }else{
    el.innerHTML=[stageBlind,stageIntensive,stageShadow,stageRetell][step]();
  }"""
new = """  if(rev){
    /* 复习两段：精听 → 跟读（无盲听、无难句补练） */
    el.innerHTML=[stageIntensive,stageShadow][step]();
  }else if(step>=STAGES.length){
    el.innerHTML=studyDoneCard();                /* 学习完成卡：三段走完的终点 */
    return;
  }else{
    el.innerHTML=[stageBlind,stageIntensive,stageShadow][step]();
  }"""
rep(old, new, "renderStage 分段")
rep("""  /* 跟读 / 录音：把焦点行滚到容器中部 */
  const isShadow=(!rev&&step===2)||(rev&&step===1);
  const isRec=(!rev&&step===3)||(rev&&step===2);
  if(isShadow||isRec){""",
    """  /* 跟读：把焦点行滚到容器中部（录音段已删） */
  const isShadow=(!rev&&step===2)||(rev&&step===1);
  if(isShadow){""",
    "renderStage 滚动")

# ── 6. 跟读出口：首学 v=3 进完成卡；复习 v=2 直接收尾 ──
rep("""  else if(act==='tostage'){
    if(CUR.mode==='rev'){
      const v=+el.dataset.v, p0=prog(CUR.no), st=revState(p0);""",
    """  else if(act==='tostage'){
    if(CUR.mode==='rev'){
      const v=+el.dataset.v, p0=prog(CUR.no), st=revState(p0);""",
    "tostage head (no-op guard)")
rep("""      /* 跟读 → 录音：点「读完了」即本段有效提取 */
      if(v===2) revMark(1);
      CUR.rstep=v;
    }else{
      p.stage=+el.dataset.v; p.si=CUR.si??p.si; saveProgress();
    }
    CUR.blob=null; CUR.grade=''; CUR.loopsLeft=null; CUR.rec=null; renderLesson();""",
    """      /* 跟读读完 → 两段齐，直接进入本轮完成卡（录音段已删） */
      if(v===2){ revMark(1); finishReview(); return; }
      CUR.rstep=v;
    }else{
      p.stage=+el.dataset.v; p.si=CUR.si??p.si;
      if(+el.dataset.v>=STAGES.length) p.firstLearnAt=p.firstLearnAt||Date.now();  /* 首学锚点：进完成卡即落定 */
      saveProgress();
    }
    CUR.grade=''; CUR.loopsLeft=null; renderLesson();""",
    "tostage 分支")

# ── 7. stageRetell → studyDoneCard ──
DONE = r"""/* —— 学习完成卡（11-23 定案）：三段走完的终点，不再是「第四段」 —— */
function studyDoneCard(){
  const p=prog(CUR.no), d=CUR.data;
  const next=p.reviews>=OFFSETS.length
    ? '7 轮复习已全部完成，本课通关'
    : `首轮复习：约 6 小时后（${fmtDate(isoOf(nextDue(p)))}）`;
  return `<div class="body" style="padding:14px 18px calc(10px + env(safe-area-inset-bottom,0px))">
    <div class="card" style="margin-top:14px">
      <div class="title" style="margin:0">学习完成</div>
      <div class="subtle" style="margin-top:6px">第 ${d.no} 课 · ${esc(d.title)}</div>
      <div style="display:flex;justify-content:space-between;margin-top:16px;font-size:13px;color:var(--sub)"><span>已完成</span><b style="color:var(--ink)">盲听 · 精听 · 跟读</b></div>
      <div style="display:flex;justify-content:space-between;margin-top:8px;font-size:13px;color:var(--sub)"><span>复习安排</span><b style="color:var(--ink)">${next}</b></div>
    </div>
    <div style="margin-top:auto;display:flex;flex-direction:column;gap:9px">
      <button class="fbtn" data-act="doneback">完成，返回课程</button>
    </div>
  </div>`;
}
"""
swap("/* —— 录音（稿屏 5）：全篇模式 · 只滚中文 · 断点录制 · 分段进度 —— */",
     "\nfunction fmtSec(sec){", DONE, "studyDoneCard")

# ── 8. 删 recDoneCard + 录音控制函数（保留 fmtSec，删到 finBlock 前） ──
a = src.index("/* —— 屏 6：唯一完成卡")
b = src.index("function finBlock(){", a)
src = src[:a] + src[b:]
print("ok 删 recDoneCard + 录音控制函数")

# ── 9. 删事件分支：rectoggle / recpause / recfinish / recrow / recback / recshare ──
a = src.index("  else if(act==='rectoggle')")
b = src.index("  else if(act==='jump'){", a)
src = src[:a] + """  else if(act==='doneback'){
    p.firstLearnAt=p.firstLearnAt||Date.now(); p.stage=STAGES.length; saveProgress();
    location.hash='#/c/'+curCourse();
  }
""" + src[b:]
print("ok 删录音事件分支 + 加 doneback")

# ── 10. 屏 8 删「分享给家人」（分享的是录音文件） ──
rep("""    <div class="rev-acts">
      <button class="fbtn" data-act="revclose">回到课程</button>
      <button class="fbtn ghost sm" data-act="recshare">分享给家人</button>
    </div>""",
    """    <div class="rev-acts">
      <button class="fbtn" data-act="revclose">回到课程</button>
    </div>""",
    "屏8 删分享")

# ── 11. 统计删「录音次数」 ──
rep("""    <div class="item"><div class="tt">跟读句子次数</div><b>${STATS.shadowN||0}</b></div>
    <div class="item"><div class="tt">录音次数</div><b>${STATS.recN||0}</b></div></div>`;""",
    """    <div class="item"><div class="tt">跟读句子次数</div><b>${STATS.shadowN||0}</b></div></div>`;""",
    "统计删录音次数")

P.write_text(src, encoding="utf-8")
print("written", len(src))
