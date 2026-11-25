# -*- coding: utf-8 -*-
"""ily-echo P1 视觉骨架验收：逐屏截图 + JS 错误 + 关键断言。"""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(r"E:\04 少儿原版课程\06 新概念英语")
OUT = ROOT / "ily-echo" / "_p1_shots"
OUT.mkdir(exist_ok=True)
BASE = "http://127.0.0.1:8112/index.html"

ROUTES = [
    ("home", "#/home"),
    ("lesson1_blind", "#/lesson/1"),
    ("lesson1_jingting", "#/lesson/1"),   # 需交互切段，下方单独处理
    ("hard", "#/hard"),
    ("cards", "#/cards"),
    ("store", "#/store"),
    ("listen", "#/listen"),
    ("player", "#/player"),
    ("me", "#/me"),
]

report = []
with sync_playwright() as pw:
    browser = pw.chromium.launch(channel="msedge", headless=True)
    ctx = browser.new_context(viewport={"width": 420, "height": 900}, device_scale_factor=2, has_touch=True)
    page = ctx.new_page()
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e).slice(0, 160)))
    page.on("console", lambda m: errs.append("console:" + m.text[:120]) if m.type == "error" else None)

    for name, route in ROUTES:
        page.goto(BASE + route, wait_until="load")
        page.wait_for_timeout(700)
        page.screenshot(path=str(OUT / f"p1_{name}.png"))
        txt = page.locator("body").inner_text()
        report.append((name, len(txt), "OK" if txt.strip() else "EMPTY"))

    # 关键断言
    page.goto(BASE + "#/listen", wait_until="load"); page.wait_for_timeout(500)
    a_fab = page.locator("nav.tabs .fabbtn").count()
    a_tabn = page.locator("nav.tabs a").count()
    a_pack = page.locator(".lpack").count()
    a_book = page.locator(".lbooks .lchip").count()   # P4：课本胶囊改 button（ready 门禁）
    a_green = page.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--brand').trim()")

    page.goto(BASE + "#/player", wait_until="load"); page.wait_for_timeout(400)
    a_lines = page.locator(".pline").count()
    a_now = page.locator(".pline.now").count()

    page.goto(BASE + "#/home", wait_until="load"); page.wait_for_timeout(400)
    a_stages = page.evaluate("typeof STAGES!=='undefined'?STAGES.join('/'):'N/A'")

    print("=== 断言 ===")
    print(f"五tab圆钮 fabbtn={a_fab} (期望1) / tab总数含圆钮={a_tabn} (期望5)")
    print(f"听单包 {a_pack} 行 (期望3) / 课本胶囊 {a_book} (期望6=课程数)")
    print(f"brand 色 = {a_green} (期望 #10B981)")
    print(f"播放页字幕 {a_lines} 行 / 高亮 {a_now} (P4：L01 正文 16 句，高亮1)")
    print(f"STAGES = {a_stages} (期望 盲听/精听/跟读 · 录音段已删)")
    print("=== 逐屏文本长度 ===")
    for r in report: print(r)
    print("=== JS 错误 ===")
    print(errs if errs else "无")
    browser.close()
