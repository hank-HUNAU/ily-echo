# -*- coding: utf-8 -*-
"""v42 组 1 收尾修正：
① 跟读按稿做行窗口化（横屏 5 行 / 竖屏 7 行，当前句居中）
② 完成录音后重绘整页（顶栏改「本课完成」+ 四段全 ✓）
③ now 行中文强调只用于录音页（稿屏 5 内联），不污染跟读
"""
from pathlib import Path

P = Path(r"E:\04 少儿原版课程\06 新概念英语\ily-echo\v42\index.html")
src = P.read_text(encoding="utf-8")

# ①-a 删通用 now 中文强调（稿跟读页 now 行中文仍是 12px）
old = "#app.v42-lesson .krow.now .zh{font-size:18px;color:var(--ink);font-weight:600;margin-top:2px}\n"
assert old in src
src = src.replace(old, "", 1)

# ①-b 删横屏 now 英文覆盖（稿横屏 .krow.now .en 仍是 21px）
old = "  #app.v42-lesson .krow.now .en{font-size:19px}\n"
assert old in src
src = src.replace(old, "", 1)

# ② 完成录音 → 重绘整页
old = """        if(CUR.mode==='rev'){ revMark(2); finishReview(); return; }
        renderStage();"""
new = """        if(CUR.mode==='rev'){ revMark(2); finishReview(); return; }
        renderLesson();   /* 屏 6：顶栏换「本课完成」、四段全打 ✓ */"""
assert old in src
src = src.replace(old, new, 1)

# ③ 跟读行窗口化（整块替换为 for 循环）
old = """  const cur=CUR.shSi;
  let rows='';
  d.sentences.forEach((s,i)=>{
    if(i===0) return;
    const now=i===cur;
    const en=(CUR.lang==='zh')?'':`<div class="en">${esc(s.en)}</div>`;
    const zh=(CUR.lang==='en')?'':`<div class="zh">${esc(s.zh)}</div>`;
    rows+=`<div class="krow ${now?'now':'dim'}" data-act="shrow" data-i="${i}">${en}${zh}</div>`;
  });"""
new = """  const cur=CUR.shSi;
  /* 行窗口：稿 §3「N=min(7, 奇数(floor(可用高/行高)))」—— 竖屏 7 行、横屏可用高 230px 故 5 行 */
  const landNow=window.matchMedia('(orientation:landscape)').matches;
  const winN=landNow?5:7, half=(winN-1)/2;
  let winFrom=Math.max(1,Math.round(cur-half)), winTo=winFrom+winN-1;
  if(winTo>total){ winTo=total; winFrom=Math.max(1,total-winN+1); }
  if(winFrom<1){ winFrom=1; winTo=Math.min(total,winN); }
  let rows='';
  for(let i=winFrom;i<=winTo;i++){
    const s=d.sentences[i], now=i===cur;
    const en=(CUR.lang==='zh')?'':`<div class="en">${esc(s.en)}</div>`;
    const zh=(CUR.lang==='en')?'':`<div class="zh">${esc(s.zh)}</div>`;
    rows+=`<div class="krow ${now?'now':'dim'}" data-act="shrow" data-i="${i}">${en}${zh}</div>`;
  }"""
assert old in src
src = src.replace(old, new, 1)

# ④ 录音页当前句中文强调（照稿屏 5 内联 style）
old = """    return `<div class="krow ${now?'now':(done?'':'dim')}" data-act="recrow" data-i="${i}"><div class="zh">${esc(s.zh)}</div></div>`;"""
new = """    const zs=now?'font-size:18px;color:var(--ink);font-weight:600':'';
    return `<div class="krow ${now?'now':(done?'':'dim')}" data-act="recrow" data-i="${i}"><div class="zh" style="${zs}">${esc(s.zh)}</div></div>`;"""
assert old in src
src = src.replace(old, new, 1)

P.write_text(src, encoding="utf-8")
print("patched", len(src))
