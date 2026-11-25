# -*- coding: utf-8 -*-
"""主 App 横屏跟读照稿屏3验收：外壳/行窗/播放条/工具条/无底 tab + 竖屏无退化。"""
import http.server
import socketserver
import threading
import time
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(r"E:\04 少儿原版课程\06 新概念英语\ily-echo")
OUT = ROOT / "_ia_design" / "v42"
PORT = 8144


class Q(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(ROOT), **k)
    def log_message(self, *a):
        pass


h = socketserver.TCPServer(("127.0.0.1", PORT), Q)
threading.Thread(target=h.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{PORT}/index.html"
R = []
def chk(tag, ok, got):
    R.append((tag, bool(ok), got))

SEED = """() => { const pr={_v:4,__v4:1,courses:{nce2:{'1':{
  stage:2,si:3,blindDone:true,hard:[],listened:{},shadow:{},firstLearnAt:Date.now(),reviews:0,revDone:null,revMiss:0}}}};
  localStorage.setItem('el2_progress',JSON.stringify(pr));
  localStorage.setItem('el2_mycourses',JSON.stringify(['nce2']));
  localStorage.removeItem('el2_intro'); }"""

with sync_playwright() as pw:
    br = pw.chromium.launch(channel="msedge", headless=True)
    ctx = br.new_context(viewport={"width": 844, "height": 390}, device_scale_factor=1)
    p = ctx.new_page()
    errs = []
    p.on("pageerror", lambda e: errs.append(str(e)))
    p.goto(BASE + "#/lesson/1", wait_until="networkidle")
    p.evaluate(SEED)
    p.reload(wait_until="networkidle")
    time.sleep(1.4)

    appcls = p.locator("#app").get_attribute("class") or ""
    chk("C1 横屏挂 land-shadow 作用域", "land-shadow" in appcls, appcls)
    chk("C2 顶栏 = 跟读 · 全篇", p.locator(".khead span").first.inner_text() == "跟读 · 全篇"
        if p.locator(".khead span").count() else False,
        p.locator(".khead").inner_text().replace("\n", " | ") if p.locator(".khead").count() else "-")
    chk("C3 顶栏右侧 ‹ 退出", "退出" in p.locator(".khead").inner_text(), "")
    chk("C4 无四段 stepper", p.locator(".stepper").count() == 0
        or not p.locator(".stepper").is_visible(), p.locator(".stepper").count())
    chk("C5 无底部 tab", p.locator("nav.tabs").count() == 0
        or not p.locator("nav.tabs").is_visible(), p.locator("nav.tabs").count())
    n = p.locator("#kstage .krow").count()
    chk("C6 正文 5 行窗口", n == 5, n)
    now = p.evaluate("""() => {const e=document.querySelector('#kstage .krow.now');return e?+e.dataset.i:-1;}""")
    chk("C7 焦点句居中(第3行)", now == 3, now)
    st = p.evaluate("""() => {const k=document.querySelector('#kstage'),c=getComputedStyle(k);
      return {bg:c.backgroundColor,border:c.borderWidth,margin:c.margin,h:Math.round(k.getBoundingClientRect().height)};}""")
    chk("C8 kstage 透明底/无边框/无留白",
        "rgba(0, 0, 0, 0)" in st["bg"] and st["border"] == "0px" and st["margin"] == "0px", st)
    chk("C9 紧凑播放条", p.locator(".land-play").count() == 1 and p.locator(".land-play .kplay").count() == 1, "")
    tm = p.locator(".land-play .ktime").inner_text() if p.locator(".land-play .ktime").count() else ""
    chk("C10 时间为 mm:ss / mm:ss", ":" in tm and "/" in tm, tm)
    chk("C11 工具条两 seg + 读完了", p.locator(".ktool .seg").count() == 2
        and "读完了" in p.locator(".ktool").inner_text(), p.locator(".ktool").inner_text().replace("\n", " | "))
    p.screenshot(path=str(OUT / "主App_横屏跟读_稿屏3对照.png"))

    # 交互：点第 4 行聚焦 → 行窗右移
    p.locator("#kstage .krow[data-i='4']").click()
    time.sleep(.5)
    idxs = p.evaluate("[...document.querySelectorAll('#kstage .krow')].map(e=>+e.dataset.i)")
    chk("C12 点行聚焦、窗口右移", idxs == [2, 3, 4, 5, 6], idxs)
    # 遍数切换
    p.locator(".ktool .seg").nth(1).locator("span").nth(1).click()
    time.sleep(.4)
    chk("C13 遍数切 3 遍", "on" in (p.locator(".ktool .seg").nth(1).locator("span").nth(1).get_attribute("class") or ""), "")

    # 转竖屏 → 恢复主 App 原样，无 land-shadow
    p.set_viewport_size({"width": 420, "height": 900})
    time.sleep(.8)
    cls2 = p.locator("#app").get_attribute("class") or ""
    chk("C14 竖屏摘掉 land-shadow", "land-shadow" not in cls2, cls2)
    chk("C15 竖屏恢复四段 stepper", p.locator(".stepper").count() == 1
        and p.locator(".stepper").is_visible(), p.locator(".stepper").count())
    chk("C16 竖屏恢复全文 16 行", p.locator("#kstage .krow").count() == 16, p.locator("#kstage .krow").count())
    p.screenshot(path=str(OUT / "主App_竖屏跟读_未退化.png"))

    chk("C17 无 JS 错误", len(errs) == 0, errs[:3])
    br.close()

h.shutdown()
n = sum(1 for _, ok, _ in R if ok)
print(f"\n== 主App 横屏照稿屏3：{n}/{len(R)} PASS ==\n")
for tag, ok, got in R:
    print(("PASS " if ok else "FAIL ") + tag + ("" if ok else f"  →  {got}"))
