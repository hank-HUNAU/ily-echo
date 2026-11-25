# -*- coding: utf-8 -*-
"""教材页 IA 改版验收：首屏课格 / 筛选 / 搜索 / 新手指引浮层 / 跨页返回"""
import http.server, socketserver, threading
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(r"E:\04 少儿原版课程\06 新概念英语\ily-echo")
OUT = ROOT / "_ia_design"; OUT.mkdir(exist_ok=True)
PORT = 8118
BASE = f"http://127.0.0.1:{PORT}/index.html"

class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
    def __init__(self, *a, **kw): super().__init__(*a, directory=str(ROOT), **kw)
socketserver.TCPServer.allow_reuse_address = True
srv = socketserver.TCPServer(("127.0.0.1", PORT), Q)
threading.Thread(target=srv.serve_forever, daemon=True).start()

def fresh(pw, **kw):
    ctx = pw.chromium.launch(channel="msedge", headless=True).new_context(**kw)
    return ctx.new_page()

with sync_playwright() as pw:
    br = pw.chromium.launch(channel="msedge", headless=True)
    ctx = br.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2,
                         has_touch=True, is_mobile=True)
    page = ctx.new_page()
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e)[:160]))

    print("=== ① 首次进入教材页（新用户）===")
    page.goto(BASE + "#/c/nce2", wait_until="load"); page.wait_for_timeout(900)
    m = page.evaluate("""() => {
      const vh=window.innerHeight, cells=[...document.querySelectorAll('#app .cell')];
      const vis=cells.filter(c=>{const r=c.getBoundingClientRect();return r.top<vh&&r.bottom>0});
      const full=cells.filter(c=>{const r=c.getBoundingClientRect();return r.bottom<=vh-90});
      const grid=document.querySelector('#app .grid');
      return {total:cells.length, visible:vis.length, full:full.length,
              first:cells[0]&&cells[0].textContent, last:vis[vis.length-1]&&vis[vis.length-1].textContent,
              gridTop:Math.round(grid.getBoundingClientRect().top),
              mask:!document.getElementById('introMask').hidden,
              hasOld:!!document.querySelector('[data-go*="m=rev"]')&&!!document.querySelector('.sec h2'),
              h2:[...document.querySelectorAll('.sec h2')].map(x=>x.textContent.trim()),
              next:document.querySelector('.cell.next')&&document.querySelector('.cell.next').textContent,
              chips:[...document.querySelectorAll('[data-filter]')].map(x=>x.textContent.trim()),
              dlBtn:!!document.getElementById('homeOlBtn')};
    }""")
    print("  结果:", m)
    page.screenshot(path=str(OUT / "course_after_real.png"))
    assert m["visible"] >= 15, "首屏可见课格过少"
    assert m["mask"], "首次应弹新手引导"
    assert m["h2"] == [], "旧的三张卡应全部移除"
    assert not m["dlBtn"], "离线按钮应移除"

    print("=== ② 关引导后：再进入不弹 ===")
    page.click("#introGo"); page.wait_for_timeout(250)
    hidden1 = page.evaluate("document.getElementById('introMask').hidden")
    page.goto(BASE + "#/home", wait_until="load"); page.wait_for_timeout(400)
    page.goto(BASE + "#/c/nce2", wait_until="load"); page.wait_for_timeout(700)
    hidden2 = page.evaluate("document.getElementById('introMask').hidden")
    print(f"  关闭后 hidden={hidden1} / 再进入 hidden={hidden2}")
    assert hidden1 and hidden2

    print("=== ③ 顶栏 ? 可重开引导 ===")
    page.click("#homeIntroBtn"); page.wait_for_timeout(200)
    print("  再次弹出:", not page.evaluate("document.getElementById('introMask').hidden"))
    page.click("#introGo"); page.wait_for_timeout(200)

    print("=== ④ 筛选胶囊 ===")
    for key, expect in [("due", 0), ("new", 96), ("doing", 0), ("done", 0), ("all", 96)]:
        page.click(f'[data-filter="{key}"]'); page.wait_for_timeout(250)
        n = page.locator("#app .cell").count()
        sel = page.locator("[data-filter].on").inner_text()
        print(f"  {key:6s} → {n} 格 (期望{expect}) 选中={sel}")
        assert n == expect, f"筛选 {key} 数量不符"

    print("=== ⑤ 搜索与筛选叠加 ===")
    page.fill("#cellQ", "12"); page.wait_for_timeout(250)
    vis = page.evaluate("""() => [...document.querySelectorAll('#app .cell')]
        .filter(c=>getComputedStyle(c).display!=='none').map(c=>c.textContent)""")
    print("  搜 '12':", vis)
    assert any("L12" in x for x in vis)
    page.fill("#cellQ", ""); page.wait_for_timeout(200)

    print("=== ⑥ 从课格进课文，再返回教材页 ===")
    page.goto(BASE + "#/lesson/1", wait_until="load"); page.wait_for_timeout(800)
    page.click('.tbBack'); page.wait_for_timeout(700)
    back = page.evaluate("""() => ({hash:location.hash, cells:document.querySelectorAll('#app .cell').length,
        gridTop:Math.round(document.querySelector('#app .grid').getBoundingClientRect().top),
        filter:document.querySelector('[data-filter].on').textContent.trim()})""")
    print("  返回:", back)
    assert back["hash"] == "#/c/nce2" and back["cells"] == 96 and back["filter"].startswith("全部")

    print("=== ⑦ 我的课程 tab 与我的页仍在 ===")
    page.goto(BASE + "#/home", wait_until="load"); page.wait_for_timeout(500)
    print("  tab:", page.evaluate("""() => ({h2:[...document.querySelectorAll('.sec h2')].map(x=>x.textContent.trim()),
        due:[...document.querySelectorAll('.item .en')].map(x=>x.textContent.trim()).slice(0,2)})"""))
    page.goto(BASE + "#/me", wait_until="load"); page.wait_for_timeout(500)
    print("  我的页离线区:", "离线包" in page.locator("body").inner_text())

    print("=== JS 错误 ===", errs if errs else "无")
    br.close()
srv.shutdown()
