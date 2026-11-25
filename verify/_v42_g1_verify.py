# -*- coding: utf-8 -*-
"""v42 组 1（屏 1-6）验收：逐屏比对设计稿 DOM 结构与文案。"""
import http.server
import socketserver
import threading
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(r"E:\04 少儿原版课程\06 新概念英语\ily-echo")
OUT = ROOT / "_ia_design" / "v42"
OUT.mkdir(parents=True, exist_ok=True)
PORT = 8130


class Quiet(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)

    def log_message(self, *a):
        pass


httpd = socketserver.TCPServer(("127.0.0.1", PORT), Quiet)
threading.Thread(target=httpd.serve_forever, daemon=True).start()
URL = f"http://127.0.0.1:{PORT}/v42/index.html"

R = []


def chk(tag, cond, got):
    R.append((tag, bool(cond), got))


with sync_playwright() as pw:
    br = pw.chromium.launch(channel="msedge", headless=True, args=[
        "--use-fake-ui-for-media-stream",
        "--use-fake-device-for-media-stream",
        "--autoplay-policy=no-user-gesture-required",
    ])
    ctx = br.new_context(viewport={"width": 390, "height": 844}, is_mobile=True,
                         has_touch=True, device_scale_factor=2,
                         permissions=["microphone"])
    p = ctx.new_page()
    errs = []
    p.on("pageerror", lambda e: errs.append(str(e)))
    p.goto(URL + "#/lesson/1", wait_until="networkidle")
    time.sleep(1.2)

    chk("A1 稿作用域类 #app.v42-lesson", p.locator("#app.v42-lesson").count() == 1,
        p.locator("#app").get_attribute("class"))

    # ── 屏 1 听态 ──
    head = p.locator(".khead span").first.inner_text()
    chk("A2 khead = L1 · 私人谈话", head == "L1 · 私人谈话", head)
    chk("A3 khead 右侧 = ‹ 退出", "退出" in p.locator(".khead").inner_text(), p.locator(".khead").inner_text())
    fn = p.locator(".flownav .fn")
    chk("A4 流程条 3 段（录音已删）", fn.count() == 3, fn.count())
    chk("A5 盲听段为当前", "on" in (fn.nth(0).get_attribute("class") or ""),
        fn.nth(0).get_attribute("class"))
    t = p.locator("#stage").inner_text()
    chk("A6 进入即显示题干 + 3 选项", "Why did the writer complain" in t
        and p.locator(".opt").count() == 3, t.replace("\n", " | ")[:100])
    p.screenshot(path=str(OUT / "s1_blind_listen.png"))

    # ── 屏 1 出题态（headless 无真人音频，走统一入口推进） ──
    p.evaluate("window.el2BlindDone()")
    time.sleep(.4)
    q = p.locator(".body .big").first.inner_text()
    chk("A7 题干出题", "Why did the writer complain" in q, q)
    chk("A8 3 个选项", p.locator(".opt").count() == 3, p.locator(".opt").count())
    chk("A9 选项圆徽 A/B/C", p.locator(".opt b").nth(0).inner_text() == "A",
        [p.locator(".opt b").nth(i).inner_text() for i in range(3)])
    chk("A10 显示中文提示键", p.locator("[data-act='blindhint']").count() == 1, "")
    p.screenshot(path=str(OUT / "s1_blind_quiz.png"))

    # 答错一次 → 自动重听；再答错 → 揭底
    correct = p.evaluate("CUR.blindOpt.correctIdx")
    wrong = (correct + 1) % 3
    p.locator(f".opt[data-i='{wrong}']").click()
    time.sleep(.5)
    if p.locator(".opt").count() == 0:          # 答错 → 自动重听，页面回到聆听态
        p.evaluate("window.el2BlindDone()")
        time.sleep(.4)
    p.locator(f".opt[data-i='{wrong}']").click()
    time.sleep(.5)
    t = p.locator("#stage").inner_text()
    chk("A11 二错揭底：正确答案 + 进入精听", "正确答案" in t and "进入精听" in t, t.replace("\n", " | "))
    chk("A12 揭底标出正确项", p.locator(".opt.right").count() == 1, p.locator(".opt.right").count())
    p.screenshot(path=str(OUT / "s1_blind_reveal.png"))

    # ── 屏 2 精听 ──
    p.locator("[data-act='blind2jingting']").click()
    time.sleep(.6)
    chk("A13 进入精听：khead 句序",
        p.locator(".khead span").first.inner_text() == "精听 · 第 1 / 16 句",
        p.locator(".khead span").first.inner_text())
    chk("A14 Anki 句卡存在", p.locator(".ankiCard").count() == 1, "")
    chk("A15 句卡标签 = 句卡 1 / 16", p.locator(".ankiTag").inner_text().strip() == "句卡 1 / 16",
        p.locator(".ankiTag").inner_text())
    chk("A16 ★ 收藏在卡片右上角", p.locator(".ankiTop .ankiFav").count() == 1,
        p.locator(".ankiFav").inner_text() if p.locator(".ankiFav").count() else "")
    chk("A17 卡片脚注含轮次", "/ 07 轮" in p.locator(".ankiFoot").inner_text(),
        p.locator(".ankiFoot").inner_text().replace("\n", " | "))
    segs = p.locator(".v42-play .seg span")
    chk("A18 语言三档右对齐", segs.count() == 3 and "双语" in p.locator(".v42-play .seg span.on").inner_text(),
        [segs.nth(i).inner_text() for i in range(segs.count())])
    chk("A19 底部三键", p.locator(".v42-ctl .v42-mini").count() == 2 and p.locator(".v42-ctl .v42-main").count() == 1,
        "")
    chk("A20 盲听段标 ✓", p.locator(".flownav .fn").nth(0).locator(".fni").inner_text() == "✓",
        p.locator(".flownav .fn").nth(0).locator(".fni").inner_text())
    p.screenshot(path=str(OUT / "s2_intensive.png"))

    # ── 屏 4 跟读竖屏 ──
    p.locator("[data-act='tostage'][data-v='2']").click()
    time.sleep(.6)
    chk("A21 跟读 khead", p.locator(".khead span").first.inner_text() == "跟读 · 全篇",
        p.locator(".khead span").first.inner_text())
    chk("A22 竖屏窗口 7 行（稿 §3 行窗）", p.locator("#kstage .krow").count() == 7, p.locator("#kstage .krow").count())
    chk("A23 仅 1 行焦点", p.locator("#kstage .krow.now").count() == 1, p.locator("#kstage .krow.now").count())
    chk("A24 其余 6 行虚化", p.locator("#kstage .krow.dim").count() == 6, p.locator("#kstage .krow.dim").count())
    idx = p.evaluate("[...document.querySelectorAll('#kstage .krow')].map(e=>+e.dataset.i)")
    chk("A24b 窗口从首句起 1..7", idx == [1, 2, 3, 4, 5, 6, 7], idx)
    chk("A25 工具条两组 seg + 读完了",
        p.locator(".ktool .seg").count() == 2 and "读完了" in p.locator(".ktool .fbtn").inner_text(),
        p.locator(".ktool").inner_text().replace("\n", " | "))
    chk("A26 竖屏三键可见", p.locator(".v42-ctl.port-only").is_visible(), "")
    chk("A27 竖屏横屏播放条隐藏", not p.locator(".v42-play.land-only").is_visible(), "")
    for _ in range(2):
        p.locator("[data-act='shnext']").click()
        time.sleep(.3)
    idx2 = p.evaluate("[...document.querySelectorAll('#kstage .krow')].map(e=>+e.dataset.i)")
    nowi = p.evaluate("+document.querySelector('#kstage .krow.now').dataset.i")
    chk("A24c 窗口随句右移、焦点居中", nowi == 3 and idx2 == [1, 2, 3, 4, 5, 6, 7], (nowi, idx2))
    p.locator("[data-act='shprev']").click()
    p.locator("[data-act='shprev']").click()
    time.sleep(.4)
    p.screenshot(path=str(OUT / "s4_shadow_portrait.png"))

    # ── 屏 3 跟读横屏 ──
    p.set_viewport_size({"width": 844, "height": 390})
    time.sleep(.6)
    chk("A28 横屏流程条隐藏", not p.locator(".flownav").is_visible(), "")
    chk("A29 横屏紧凑播放条可见", p.locator(".v42-play.land-only").is_visible(), "")
    chk("A30 横屏三键隐藏", not p.locator(".v42-ctl.port-only").is_visible(), "")
    kh = p.evaluate("document.querySelector('#kstage').getBoundingClientRect().height")
    chk("A31 横屏容器吃满剩余高（≥稿 230）", kh >= 230, round(kh, 1))
    over = p.evaluate("""() => { const k=document.querySelector('#kstage');
        return {sh:k.scrollHeight, ch:k.clientHeight}; }""")
    chk("A32 横屏 5 行不裁首行", over["sh"] <= over["ch"] + 2, over)
    p.screenshot(path=str(OUT / "s3_shadow_landscape.png"))
    p.set_viewport_size({"width": 390, "height": 844})
    time.sleep(.5)

    # ── 学习完成卡（11-23：录音段已删，跟读完直接进卡） ──
    p.locator("[data-act='tostage'][data-v='3']").click()
    time.sleep(.8)
    chk("A33 完成卡 khead = 本课完成", p.locator(".khead span").first.inner_text() == "本课完成",
        p.locator(".khead span").first.inner_text())
    chk("A34 完成卡标题 = 学习完成", p.locator(".card .title").count() == 1
        and p.locator(".card .title").inner_text() == "学习完成",
        p.locator(".card .title").inner_text() if p.locator(".card .title").count() else "")
    chk("A35 三段流程条全 ✓", p.locator(".flownav .fn").count() == 3
        and p.locator(".flownav .fn.done").count() == 3,
        p.locator(".flownav").inner_text().replace("\n", " | "))
    chk("A36 已完成写明三段", "盲听 · 精听 · 跟读" in p.locator("#stage").inner_text(),
        p.locator("#stage").inner_text().replace("\n", " | "))
    chk("A37 无录音/分享入口", p.locator("[data-act^='rec']").count() == 0
        and "分享" not in p.locator("#stage").inner_text(), "")
    chk("A38 只有返回课程一键", p.locator("[data-act='doneback']").count() == 1
        and p.locator("#stage button").count() == 1, p.locator("#stage").inner_text().replace("\n", " | "))
    p.screenshot(path=str(OUT / "s6_study_done.png"))
    p.locator("[data-act='doneback']").click()
    time.sleep(.8)
    chk("A39 返回教材页", p.evaluate("location.hash").startswith("#/c/"), p.evaluate("location.hash"))

    chk("A44 无 JS 错误", len(errs) == 0, errs[:3])
    br.close()

httpd.shutdown()
n = sum(1 for _, ok, _ in R if ok)
print(f"\n== v42 组1 屏1-6 验收：{n}/{len(R)} PASS ==\n")
for tag, ok, got in R:
    print(("PASS " if ok else "FAIL ") + tag + ("" if ok else f"  →  {got}"))
print(f"\n截图目录：{OUT}")
