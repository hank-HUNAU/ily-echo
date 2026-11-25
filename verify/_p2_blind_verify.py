# -*- coding: utf-8 -*-
"""P2-1 盲听三分支验收（纯 DOM，不依赖内部变量）。"""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

ROOT = Path(r"E:\04 少儿原版课程\06 新概念英语")
OUT = ROOT / "ily-echo" / "_p2_shots"
OUT.mkdir(exist_ok=True)
BASE = "http://127.0.0.1:8113/index.html"
BO = json.load(open(ROOT/"ily-echo"/"blind_options.json", encoding="utf-8"))

def fresh(page):
    page.goto(BASE + "#/home", wait_until="load")
    page.evaluate("localStorage.removeItem('el2_progress')")
    page.reload(wait_until="load")
    page.goto(BASE + "#/lesson/1", wait_until="load")
    page.wait_for_function("document.querySelector('#app') && document.querySelector('#app').innerText.length>30", timeout=20000)
    page.wait_for_timeout(700)

with sync_playwright() as pw:
    browser = pw.chromium.launch(channel="msedge", headless=True)
    ctx = browser.new_context(viewport={"width":420,"height":900}, device_scale_factor=2, has_touch=True)
    page = ctx.new_page()
    errs=[]
    page.on("pageerror", lambda e: errs.append(str(e)[:160]))

    # ① 聆听态
    fresh(page)
    t = page.locator("#app").inner_text()
    html = page.locator("#app").inner_html()
    print("① 聆听态:", "仔细听" in t, "| 无选项:", "blind-opt" not in html, "| 无说明句:", "正在播放全文" not in t)
    page.screenshot(path=str(OUT/"p2_blind_listening.png"))

    # 用页面注入触发出题（CUR 在函数块内，但 renderStage 通过 window 钩子不可用；
    # 改为模拟音频播放完成：dispatch ended 事件给 AU，再等 700ms 的 setTimeout）
    page.evaluate("window.el2BlindDone()")
    page.wait_for_timeout(1200)
    n = page.locator(".blind-opt").count()
    q = page.locator(".blind-q").inner_text() if n else "(无)"
    print("② 出题态 选项数:", n, "| 题干:", q[:52])
    page.screenshot(path=str(OUT/"p2_blind_quiz.png"))

    # ③ 答对（正确项文本匹配）
    correct_txt = BO["1"]["options"][BO["1"]["correctIdx"]]
    if n:
        opts = page.locator(".blind-opt")
        clicked = -1
        for i in range(opts.count()):
            if correct_txt[:10] in opts.nth(i).inner_text():
                clicked = i; break
        if clicked < 0: clicked = BO["1"]["correctIdx"]
        opts.nth(clicked).click()
        page.wait_for_timeout(500)
        # P2-2 起精听改为 Anki 句卡，判据改为卡片出现
        print("③ 答对 → 精听:", page.locator(".int-card").count() > 0)

    # ④ 答错分支：重进课程刷新
    fresh(page)
    page.evaluate("window.el2BlindDone()")
    page.wait_for_timeout(1200)
    wrong_txt = BO["1"]["options"][(BO["1"]["correctIdx"]+1)%3]
    opts = page.locator(".blind-opt")
    clicked=-1
    for i in range(opts.count()):
        if wrong_txt[:10] in opts.nth(i).inner_text(): clicked=i; break
    if clicked<0: clicked=(BO["1"]["correctIdx"]+1)%3
    opts.nth(clicked).click()
    page.wait_for_timeout(500)
    t4=page.locator("#app").inner_text()
    print("④ 答错1次 → 重听:", "仔细听" in t4 or "再听一遍" in t4, "| 未进精听:", "逐句精听" not in t4)

    # ⑤ 第二次答错 → 揭底（重听结束后再 dispatch ended 回出题态）
    page.evaluate("window.el2BlindDone()")
    page.wait_for_timeout(1200)
    opts=page.locator(".blind-opt")
    if opts.count():
        opts.nth(BO["1"]["correctIdx"]).click() if False else opts.nth(clicked).click()
    page.wait_for_timeout(500)
    t5=page.locator("#app").inner_text()
    h5=page.locator("#app").inner_html()
    print("⑤ 答错2次 → 揭底:", "正确答案" in t5, "| 进入精听按钮:", "blind2jingting" in h5)
    page.screenshot(path=str(OUT/"p2_blind_reveal.png"))

    print("=== JS 错误 ===", errs if errs else "无")
    browser.close()
