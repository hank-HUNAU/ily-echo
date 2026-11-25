# -*- coding: utf-8 -*-
"""全站滚动条隐藏 + 手势滚动可用性验收（P4.5）
① 无滚动条占位（gutter=0、scrollbar-width:none）
② 页面/内层容器仍能用真实触摸手势滚动（CDP Input.dispatchTouchEvent 序列）
"""
import http.server, socketserver, threading, functools
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(r"E:\04 少儿原版课程\06 新概念英语\ily-echo")
OUT = ROOT / "_p1_shots"; OUT.mkdir(exist_ok=True)
PORT = 8115
BASE = f"http://127.0.0.1:{PORT}/index.html"

Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)
socketserver.TCPServer.allow_reuse_address = True
srv = socketserver.TCPServer(("127.0.0.1", PORT), Quiet)
threading.Thread(target=srv.serve_forever, daemon=True).start()

ROUTES = [("home", "#/home"), ("store", "#/store"), ("listen", "#/listen"),
          ("player", "#/player"), ("me", "#/me"), ("cards", "#/cards"),
          ("hard", "#/hard"), ("lesson1", "#/lesson/1"), ("course", "#/c/nce2")]

TOUCH = {"touchPoints": [{"x": 195, "y": 600, "radiusX": 12, "radiusY": 12, "force": 1}],
         "modifiers": 0}

def swipe(page, x, y, dx, dy, steps=12):
    """真实触摸滑动：touchStart → 逐步 touchMove → touchEnd"""
    cdp = page.context.new_cdp_session(page)
    cdp.send("Input.dispatchTouchEvent", {"type": "touchStart",
             "touchPoints": [{"x": x, "y": y, "radiusX": 12, "radiusY": 12, "force": 1}]})
    for i in range(1, steps + 1):
        cdp.send("Input.dispatchTouchEvent", {"type": "touchMove",
                 "touchPoints": [{"x": x + dx * i / steps, "y": y + dy * i / steps,
                                  "radiusX": 12, "radiusY": 12, "force": 1}]})
        page.wait_for_timeout(16)
    cdp.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
    cdp.detach()

with sync_playwright() as pw:
    browser = pw.chromium.launch(channel="msedge", headless=True)
    ctx = browser.new_context(viewport={"width": 390, "height": 844},
                              device_scale_factor=2, has_touch=True, is_mobile=True)
    page = ctx.new_page()
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e)[:160]))

    print("=== ① 滚动条占位（390×844 移动视口）===")
    for name, route in ROUTES:
        page.goto(BASE + route, wait_until="load"); page.wait_for_timeout(700)
        m = page.evaluate("""() => { const de=document.documentElement;
          return {gutter: de.offsetWidth-de.clientWidth, sh: de.scrollHeight, ch: de.clientHeight,
                  sbw: getComputedStyle(de).scrollbarWidth||'N/A'}; }""")
        need = "需滚动" if m["sh"] > m["ch"] else "一屏内"
        print(f"{name:9s} gutter={m['gutter']}px  h={m['sh']}/{m['ch']} {need}  scrollbar-width={m['sbw']}")
        if m["gutter"] != 0:
            print("  !! 仍有滚动条占位")

    print("=== ② 页面手势滚动（真实 touch 序列）===")
    for name, route in [("course", "#/c/nce2"), ("me", "#/me"), ("store", "#/store")]:
        page.goto(BASE + route, wait_until="load"); page.wait_for_timeout(800)
        page.evaluate("window.scrollTo(0,0)"); page.wait_for_timeout(150)
        mx = page.evaluate("document.documentElement.scrollHeight-window.innerHeight")
        y0 = page.evaluate("window.scrollY")
        swipe(page, 195, 620, 0, -420)
        page.wait_for_timeout(600)
        y1 = page.evaluate("window.scrollY")
        exp = min(60, mx)
        ok1 = y1 > y0 + exp - 5
        swipe(page, 195, 260, 0, 420)          # 反向滑回
        page.wait_for_timeout(500)
        y2 = page.evaluate("window.scrollY")
        ok2 = y2 < y1 - exp + 5
        print(f"{name:7s} 可滚={round(mx)}px  scrollY {y0} → {round(y1)} → {round(y2)}  "
              f"{'PASS' if ok1 and ok2 else 'FAIL'}（上滑/下滑双向）")
        if name == "course":
            page.screenshot(path=str(OUT / "p45_course_no_scrollbar.png"))

    print("=== ②b 桌面视口滚动条（1280×800）===")
    ctx2 = browser.new_context(viewport={"width": 1280, "height": 800}, has_touch=False)
    p2 = ctx2.new_page(); p2.goto(BASE + "#/c/nce2", wait_until="load"); p2.wait_for_timeout(700)
    d = p2.evaluate("""() => { const de=document.documentElement;
      return {gutter: de.offsetWidth-de.clientWidth, innerW: window.innerWidth,
              w: de.clientWidth, sh: de.scrollHeight, ch: de.clientHeight}; }""")
    print(f"desktop gutter={d['gutter']}px  clientWidth={d['w']}/innerWidth={d['innerW']}  "
          f"h={d['sh']}/{d['ch']}  {'PASS' if d['gutter']==0 else 'FAIL 仍有滚动条'}")
    p2.screenshot(path=str(OUT / "p45_desktop_no_scrollbar.png"))
    ctx2.close()

    print("=== ③ 内层容器手势滚动 ===")
    # 播放页字幕 .plyrics
    page.goto(BASE + "#/player", wait_until="play" if False else "load"); page.wait_for_timeout(1000)
    box = page.evaluate("""() => { const b=document.querySelector('.plyrics'); if(!b) return null;
      const r=b.getBoundingClientRect();
      return {x:Math.round(r.x+r.width/2), y:Math.round(r.y+r.height/2),
              top:b.scrollTop, sh:b.scrollHeight, ch:b.clientHeight}; }""")
    if box and box["sh"] > box["ch"]:
        swipe(page, box["x"], box["y"], 0, -240)
        page.wait_for_timeout(500)
        t1 = page.evaluate("document.querySelector('.plyrics').scrollTop")
        print(f".plyrics h={box['sh']}/{box['ch']} scrollTop {box['top']} → {round(t1)}  "
              f"{'PASS' if t1 > box['top'] + 30 else 'FAIL'}")
    else:
        print(f".plyrics 跳过 {box}")

    # 跟读页 .kstage（p.stage=2）
    page.goto(BASE + "#/lesson/1", wait_until="load"); page.wait_for_timeout(800)
    page.evaluate("""() => { const c=curCourse(); const p=prog(CUR.no);
        p.stage=2; p.blindDone=true; saveProgress(); renderLesson(); }""")
    page.wait_for_timeout(700)
    ks = page.evaluate("""() => { const b=document.querySelector('.kstage'); if(!b) return null;
      const r=b.getBoundingClientRect();
      return {x:Math.round(r.x+r.width/2), y:Math.round(r.y+r.height/2),
              top:b.scrollTop, sh:b.scrollHeight, ch:b.clientHeight}; }""")
    if ks and ks["sh"] > ks["ch"]:
        swipe(page, ks["x"], ks["y"], 0, -220)
        page.wait_for_timeout(500)
        t2 = page.evaluate("document.querySelector('.kstage').scrollTop")
        print(f".kstage  h={ks['sh']}/{ks['ch']} scrollTop {ks['top']} → {round(t2)}  "
              f"{'PASS' if t2 > ks['top'] + 30 else 'FAIL'}")
    else:
        print(f".kstage 跳过 {ks}")

    # 听单页横向课本胶囊 .lbooks
    page.goto(BASE + "#/listen", wait_until="load"); page.wait_for_timeout(900)
    ch = page.evaluate("""() => { const b=document.querySelector('.lbooks'); if(!b) return null;
      const r=b.getBoundingClientRect();
      return {y:Math.round(r.y+r.height/2), left:b.scrollLeft, sw:b.scrollWidth, cw:b.clientWidth,
              bar: b.offsetHeight-b.clientHeight}; }""")
    if ch and ch["sw"] > ch["cw"]:
        swipe(page, 300, ch["y"], -180, 0)
        page.wait_for_timeout(500)
        l1 = page.evaluate("document.querySelector('.lbooks').scrollLeft")
        print(f".lbooks  w={ch['sw']}/{ch['cw']} scrollLeft {ch['left']} → {round(l1)}  "
              f"{'PASS' if l1 > ch['left'] + 20 else 'FAIL'}  横条占高={ch['bar']}px")
    else:
        print(f".lbooks 跳过 {ch}")

    print("=== JS 错误 ===", errs if errs else "无")
    browser.close()
srv.shutdown()
