# -*- coding: utf-8 -*-
"""主 App：删除四段流程中的录音段 → 三段流程 + 学习完成卡；复习三段 → 两段。
与 _rm_rec_v42.py 同口径；保留难句补练的逐句录音（独立功能）。
"""
from pathlib import Path

P = Path(r"E:\04 少儿原版课程\06 新概念英语\ily-echo\index.html")
src = P.read_text(encoding="utf-8")


def rep(old, new, tag, n=1):
    global src
    assert old in src, "MISS " + tag
    src = src.replace(old, new, n)
    print("ok", tag)


# ── 1. 常量与复习段数 ──
rep("const STAGES=['盲听','精听','跟读','录音'];",
    "const STAGES=['盲听','精听','跟读'];      /* 11-23 用户定：删录音段，三段 + 学习完成卡 */",
    "STAGES")
rep("/* ===== 复习 7 轮：本轮三段有效提取（v4.2 屏 7/8） =====\n   revDone 只对「当前轮」有效，换轮自动重置；seen 记录精听已走过的句卡，跨会话保留。\n   三段齐了才 reviews+1 —— 不允许「点一次就记账」。 */",
    "/* ===== 复习 7 轮：本轮两段有效提取（11-23 删录音段后） =====\n   revDone 只对「当前轮」有效，换轮自动重置；seen 记录精听已走过的句卡，跨会话保留。\n   两段齐了才 reviews+1 —— 不允许「点一次就记账」。 */",
    "rev 注释")
rep("const REV_STEPS=['精听','跟读','录音'];",
    "const REV_STEPS=['精听','跟读'];           /* 11-23：复习随首学改为两段 */",
    "REV_STEPS")
rep("if(!p.revDone||typeof p.revDone!=='object'||p.revDone.r!==r) p.revDone={r:r,s:[false,false,false],seen:{}};",
    "if(!p.revDone||typeof p.revDone!=='object'||p.revDone.r!==r) p.revDone={r:r,s:[false,false],seen:{}};",
    "revState init")
rep("if(!Array.isArray(p.revDone.s)||p.revDone.s.length!==3) p.revDone.s=[false,false,false];",
    "if(!Array.isArray(p.revDone.s)||p.revDone.s.length!==REV_STEPS.length) p.revDone.s=[false,false];",
    "revState len")
rep("  CUR.rec=null; CUR.rstep=null;               /* 保留 CUR.blob：屏 8 的「分享给家人」要用 */",
    "  CUR.rstep=null;                             /* 11-23：录音段已删，屏 8 不再有分享录音 */",
    "finishReview 尾部")

# ── 2. 文案 ──
rep("desc:'96 课 · 盲听 / 精听 / 跟读 / 录音 + 7 轮复习'",
    "desc:'96 课 · 盲听 / 精听 / 跟读 + 7 轮复习'",
    "课程描述")
rep('<div class="item"><div class="tt"><div class="en">③ 录音 → 等 7 轮复习</div><div class="meta">全篇中文提示下脱稿背诵录音；系统自动排 7 轮复习提醒（红点提示）</div></div></div>',
    '<div class="item"><div class="tt"><div class="en">③ 读完 → 等 7 轮复习</div><div class="meta">跟读完成后系统自动排 7 轮复习提醒（红点提示）</div></div></div>',
    "引导卡")
rep('<div class="rev-lab">本轮三段</div>',
    '<div class="rev-lab">本轮 ${REV_STEPS.length} 段</div>',
    "屏7 段数文案")

# ── 3. renderLesson：stage>=3 的学习完成卡 ──
rep("  const steps=rev?REV_STEPS:STAGES;                   /* 复习只跑后三段，盲听不重跑 */",
    "  const steps=rev?REV_STEPS:STAGES;                   /* 复习只跑后两段，盲听不重跑 */",
    "steps 注释")
rep("""    <h1 style="flex:1;min-width:0;font-size:19px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">L${d.no} · ${esc(d.title)}</h1>""",
    """    <h1 style="flex:1;min-width:0;font-size:19px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${(!rev&&cur>=STAGES.length)?'本课完成':`L${d.no} · ${esc(d.title)}`}</h1>""",
    "renderLesson 完成卡标题")

# ── 4. renderStage ──
rep("""  if(rev){
    /* 复习三段：精听 → 跟读 → 录音（无盲听、无难句补练） */
    el.innerHTML=[stageIntensive,stageShadow,stageRetell][step]();
  }else{
    el.innerHTML=[stageBlind,stageIntensive,stageShadow,stageRetell][step]();
  }""",
    """  if(rev){
    /* 复习两段：精听 → 跟读（无盲听、无难句补练） */
    el.innerHTML=[stageIntensive,stageShadow][step]();
  }else if(step>=STAGES.length){
    el.innerHTML=studyDoneCard();                /* 学习完成卡：三段走完的终点 */
    return;
  }else{
    el.innerHTML=[stageBlind,stageIntensive,stageShadow][step]();
  }""",
    "renderStage 分段")
rep("""  /* 跟读 / 录音：把焦点行滚到容器中部 */
  const isShadow=(!rev&&step===2)||(rev&&step===1);
  const isRec=(!rev&&step===3)||(rev&&step===2);
  if(isShadow||isRec){""",
    """  /* 跟读：把焦点行滚到容器中部（录音段已删） */
  const isShadow=(!rev&&step===2)||(rev&&step===1);
  if(isShadow){""",
    "renderStage 滚动")

# ── 5. tostage ──
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
      if(+el.dataset.v>=STAGES.length) p.firstLearnAt=p.firstLearnAt||Date.now();
      saveProgress();
    }
    CUR.grade=''; CUR.loopsLeft=null; renderLesson();""",
    "tostage 分支")

# ── 6. stageRetell / recDoneCard → studyDoneCard ──
DONE = r"""/* —— 学习完成卡（11-23 定案）：三段走完的终点，不再是「第四段」 —— */
function studyDoneCard(){
  const p=prog(CUR.no), d=CUR.data;
  const next=p.reviews>=OFFSETS.length
    ? '7 轮复习已全部完成，本课通关'
    : `首轮复习：约 6 小时后（${fmtDate(isoOf(nextDue(p)))}）`;
  return `<div class="shadow-wrap rec-done">
    <div class="khead2"><span>本课完成</span><a href="#/c/${curCourse()}">‹ 退出</a></div>
    <div class="reccard">
      <div class="rct">学习完成</div>
      <div class="rcs">第 ${d.no} 课 · ${esc(d.title)}</div>
      <div class="rcrow"><span>已完成</span><b>盲听 · 精听 · 跟读</b></div>
      <div class="rcrow"><span>复习安排</span><b>${next}</b></div>
    </div>
    <div class="rcacts">
      <button class="fbtn" data-act="doneback">完成，返回课程</button>
    </div>
  </div>`;
}
"""
a = src.index("function stageRetell(){")
b = src.index("function fmtSec(sec){", a)
src = src[:a] + DONE + src[b:]
print("ok stageRetell → studyDoneCard")

a = src.index("/* —— 屏 6：唯一完成卡") if "/* —— 屏 6：唯一完成卡" in src else src.index("function recDoneCard(){")
b = src.index("function finBlock(){", a)
src = src[:a] + src[b:]
print("ok 删 recDoneCard + 录音控制函数")

# ── 7. 事件分支 ──
a = src.index("  else if(act==='rectoggle')")
b = src.index("  else if(act==='jump'){", a)
src = src[:a] + """  else if(act==='doneback'){
    p.firstLearnAt=p.firstLearnAt||Date.now(); p.stage=STAGES.length; saveProgress();
    location.hash='#/c/'+curCourse();
  }
""" + src[b:]
print("ok 删录音事件分支 + 加 doneback")

# ── 8. 屏 8 删分享、统计删录音次数 ──
rep("""    <div class="rev-acts">
      <button class="fbtn" data-act="revclose">回到课程</button>
      <button class="fbtn ghost sm" data-act="recshare">分享给家人</button>
    </div>""",
    """    <div class="rev-acts">
      <button class="fbtn" data-act="revclose">回到课程</button>
    </div>""",
    "屏8 删分享")
rep("""    <div class="item"><div class="tt">跟读句子次数</div><b>${STATS.shadowN||0}</b></div>
    <div class="item"><div class="tt">录音次数</div><b>${STATS.recN||0}</b></div></div>`;""",
    """    <div class="item"><div class="tt">跟读句子次数</div><b>${STATS.shadowN||0}</b></div></div>`;""",
    "统计删录音次数")

P.write_text(src, encoding="utf-8")
print("written", len(src))
