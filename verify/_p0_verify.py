# -*- coding: utf-8 -*-
"""P0 规格对齐验收：盲听去说明/重听键 · 学习完成卡（录音段已删）· 色板绿系 · 课程库右上入口"""
import http.server, socketserver, threading
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(r"E:\04 少儿原版课程\06 新概念英语\ily-echo")
PORT = 8122
BASE = f"http://127.0.0.1:{PORT}/index.html"

class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
    def __init__(self, *a, **kw): super().__init__(*a, directory=str(ROOT), **kw)
socketserver.TCPServer.allow_reuse_address = True
srv = socketserver.TCPServer(("127.0.0.1", PORT), Q)
threading.Thread(target=srv.serve_forever, daemon=True).start()

with sync_playwright() as pw:
    br = pw.chromium.launch(channel="msedge", headless=True)
    ctx = br.new_context(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True)
    p = ctx.new_page(); errs=[]; p.on("pageerror", lambda e: errs.append(str(e)[:160]))

    print("=== ① 屏1 盲听：无状态句/无手动重听键/无作答计数 ===")
    p.goto(BASE + "#/lesson/1", wait_until="load"); p.wait_for_timeout(800)
    a = p.evaluate("""() => ({sub:!!document.querySelector('.blind-sub'),
      replay:!!document.getElementById('blindReplay'),
      tip:[...document.querySelectorAll('.tip')].map(x=>x.textContent.trim()),
      opts:document.querySelectorAll('.blind-opt').length,
      title:document.querySelector('.blind-ttl')&&document.querySelector('.blind-ttl').textContent})""")
    print("  进入态:", a)
    assert not a["sub"] and not a["replay"] and a["opts"] == 3
    assert all("盲听只在首次" not in t for t in a["tip"])
    p.evaluate("window.el2BlindDone()"); p.wait_for_timeout(400)
    q = p.evaluate("""() => ({tip:[...document.querySelectorAll('.tip')].map(x=>x.textContent.trim()),
      opts:document.querySelectorAll('.blind-opt').length})""")
    print("  出题态:", q)
    assert not any("作答" in t for t in q["tip"]) and q["opts"] == 3

    print("=== ② 学习完成卡：三段终点、无录音/分享 ===")
    p.evaluate("""() => {
      localStorage.setItem('el2_progress', JSON.stringify({_v:4,__v4:true,courses:{nce2:{
        '1':{stage:3,si:16,firstLearnAt:Date.now(),reviews:0,blindDone:true}}}}));
    }""")
    p.goto(BASE + "#/lesson/1", wait_until="load"); p.reload(wait_until="load"); p.wait_for_timeout(900)
    done = p.evaluate("""() => ({
      title: document.querySelector('.rct')?document.querySelector('.rct').innerText:null,
      steps: [...document.querySelectorAll('.stepper .st')].map(x=>x.innerText.trim()),
      recBtns: document.querySelectorAll("[data-act^='rec']").length,
      acts: [...document.querySelectorAll('.rcacts button')].map(b=>b.innerText.trim())
    })""")
    print("  完成卡:", done)
    assert done["title"] == "学习完成" and done["steps"] == ["盲听","精听","跟读"]
    assert done["recBtns"] == 0 and done["acts"] == ["完成，返回课程"]

    print("=== ③ 色板：收藏星绿、超期红、统计环绿阶 ===")
    p.goto(BASE + "#/c/nce2", wait_until="load"); p.wait_for_timeout(500)
    p.evaluate("""() => {
      const now=Date.now();
      localStorage.setItem('el2_progress', JSON.stringify({_v:4,__v4:true,courses:{nce2:{
        '1':{stage:3,si:16,firstLearnAt:now-9*864e5,reviews:0,blindDone:true,hard:[1]}}}}));
    }""")
    p.reload(wait_until="load"); p.wait_for_timeout(700)
    p.evaluate("location.hash='#/lesson/1?m=rev'"); p.wait_for_timeout(900)
    col = p.evaluate("""() => ({warn:getComputedStyle(document.documentElement).getPropertyValue('--warn').trim(),
      badge:getComputedStyle(document.body).getPropertyValue('--focus').trim()})""")
    p.evaluate("location.hash='#/c/nce2'"); p.wait_for_timeout(700)
    ring = p.evaluate("""() => [...document.querySelectorAll('#app svg circle')].map(c=>c.getAttribute('stroke')).filter(Boolean)""")
    p.goto(BASE + "#/me", wait_until="load"); p.wait_for_timeout(700)
    me = p.evaluate("""() => [...document.querySelectorAll('.ring circle[stroke]')].map(c=>c.getAttribute('stroke'))""")
    print("  --warn:", repr(col["warn"]), "(应为空)")
    print("  我的页环:", me)
    assert col["warn"] == ""
    assert all(c in ("#0B8A5F","#10B981","#5DCAA5","#EDF2F7") for c in me), me
    star = p.evaluate("""() => {const s=document.createElement('span');s.className='star on';document.body.appendChild(s);
      const c=getComputedStyle(s).color;s.remove();return c;}""")
    print("  ★ 收藏色:", star)
    assert star == "rgb(11, 138, 95)", star

    print("=== ④ 屏9 课程库右上「＋ 选择课程」 ===")
    p.goto(BASE + "#/store", wait_until="load"); p.wait_for_timeout(700)
    btn = p.locator("#storePickBtn"); print("  按钮:", btn.inner_text(), "count", btn.count())
    assert btn.count() == 1
    btn.click(); p.wait_for_timeout(350)
    foc = p.evaluate("document.activeElement&&document.activeElement.id")
    print("  点击后焦点:", foc)
    assert foc == "codeIn"

    print("=== JS 错误 ===", errs if errs else "无")
    br.close()
srv.shutdown()
