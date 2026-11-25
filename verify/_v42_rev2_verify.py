# -*- coding: utf-8 -*-
"""v42 复习流程验收：录音段删除后复习从三段改两段。"""
import http.server
import socketserver
import threading
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(r"E:\04 少儿原版课程\06 新概念英语\ily-echo")
OUT = ROOT / "_ia_design" / "v42"
PORT = 8138


class Q(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(ROOT), **k)

    def log_message(self, *a):
        pass


h = socketserver.TCPServer(("127.0.0.1", PORT), Q)
threading.Thread(target=h.serve_forever, daemon=True).start()

R = []
def chk(tag, ok, got):
    R.append((tag, bool(ok), got))

with sync_playwright() as pw:
    br = pw.chromium.launch(channel="msedge", headless=True)
    ctx = br.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
    p = ctx.new_page()
    errs = []
    p.on("pageerror", lambda e: errs.append(str(e)))
    p.goto(f"http://127.0.0.1:{PORT}/v42/index.html", wait_until="networkidle")
    time.sleep(.6)
    # 首学已完成 + 第 1 轮已过期（3 天前首学，OFFSETS[1]=1 天）
    p.evaluate("""() => {
      const days=Date.now()-3*864e5;
      localStorage.setItem('el2_progress', JSON.stringify({_v:4,courses:{nce2:{'1':{
        stage:3,si:1,blindDone:true,hard:[],listened:{},shadow:{},
        firstLearnAt:days,reviews:1,lastReviewAt:days,revDone:null,revMiss:0
      }}}}));
    }""")
    p.goto(f"http://127.0.0.1:{PORT}/v42/index.html#/lesson/1?m=rev&c=nce2", wait_until="networkidle")
    p.reload(wait_until="networkidle")   # 必须真刷新：hash 导航不会重读 localStorage
    time.sleep(1.4)

    p.evaluate("""() => { window.__writes=[]; const o=localStorage.setItem.bind(localStorage);
      localStorage.setItem=(k,v)=>{ if(k==='el2_progress'){ try{window.__writes.push(JSON.parse(v).courses.nce2['1'].reviews);}catch(e){} } return o(k,v); }; }""")

    # ── 屏 7 到期入口 ──
    t = p.locator("#app").inner_text()
    chk("B1 到期入口写「本轮 2 段」", "本轮 2 段" in t, t.replace("\n", " | ")[:110])
    chk("B2 两段胶囊", p.locator(".rev-pills .pill").count() == 2,
        p.locator(".rev-pills").inner_text().replace("\n", " | "))
    chk("B3 无录音胶囊", "录音" not in p.locator(".rev-card").inner_text(),
        p.locator(".rev-card").inner_text().replace("\n", " | "))
    p.screenshot(path=str(OUT / "rev_s7_entry.png"))

    # ── 精听：补满 seen 才能进跟读 ──
    p.locator("[data-act='revbegin']").click()
    time.sleep(.7)
    chk("B4 复习从精听起", "精听 · 第" in p.locator(".khead").inner_text(),
        p.locator(".khead").inner_text().replace("\n", " | "))
    chk("B5 流程条 3 格、盲听恒 ✓", p.locator(".flownav .fn").count() == 3
        and p.locator(".flownav .fn").nth(0).locator(".fni").inner_text() == "✓",
        p.locator(".flownav").inner_text().replace("\n", " | "))

    # 纯 UI 走完 16 句：renderStage 会逐句记 seen，不用注入 revDone（避免内存/本地分叉）
    for _ in range(15):
        p.locator("[data-act='intnext']").click()
        time.sleep(.12)
    p.locator("[data-act='tostage'][data-v='1']").click()
    time.sleep(.8)
    chk("B6 进跟读", "跟读 · 全篇" in p.locator(".khead").inner_text(),
        p.locator(".khead").inner_text().replace("\n", " | "))

    # ── 跟读完 → 直接本轮完成卡 ──
    p.locator("[data-act='tostage'][data-v='2']").click()
    time.sleep(1.0)
    t = p.locator("#app").inner_text()
    chk("B7 第 2 轮完成卡", "本轮完成" in t, t.replace("\n", " | ")[:120])
    chk("B8 完成卡两段记录", p.locator(".rev-pills .pill").count() == 2,
        p.locator(".rev-pills").inner_text().replace("\n", " | "))
    chk("B9 无分享给家人", "分享给家人" not in t and p.locator("[data-act='recshare']").count() == 0, "")
    dbg = p.evaluate("""() => ({round: (typeof CUR!=='undefined'&&CUR.revDoneShown)?CUR.revDoneShown.round:'n/a',
      ls: JSON.parse(localStorage.getItem('el2_progress')).courses.nce2['1'].reviews,
      writes: window.__writes||[],
      ttl: document.querySelector('.rev-ttl')?document.querySelector('.rev-ttl').innerText:'-'})""")
    print("DEBUG reviews", dbg)
    chk("B10 复习轮次已 +1", dbg["ls"] == 2, dbg)
    p.screenshot(path=str(OUT / "rev_s8_done.png"))
    chk("B11 无 JS 错误", len(errs) == 0, errs[:3])
    br.close()

h.shutdown()
n = sum(1 for _, ok, _ in R if ok)
print(f"\n== v42 复习两段：{n}/{len(R)} PASS ==\n")
for tag, ok, got in R:
    print(("PASS " if ok else "FAIL ") + tag + ("" if ok else f"  →  {got}"))
