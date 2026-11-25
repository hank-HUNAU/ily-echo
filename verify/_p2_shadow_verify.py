# -*- coding: utf-8 -*-
"""P2-3 跟读工具条验收。"""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path(r"E:\04 少儿原版课程\06 新概念英语")
OUT=ROOT/"ily-echo"/"_p2_shots"; OUT.mkdir(exist_ok=True)
B="http://127.0.0.1:8113/index.html"
BO=json.load(open(ROOT/"ily-echo"/"blind_options.json",encoding="utf-8"))
with sync_playwright() as pw:
    br=pw.chromium.launch(channel="msedge",headless=True)
    ctx=br.new_context(viewport={"width":420,"height":900},device_scale_factor=2,has_touch=True)
    pg=ctx.new_page(); errs=[]
    pg.on("pageerror",lambda e: errs.append(str(e)[:120]))
    pg.goto(B+"#/home",wait_until="load")
    pg.evaluate("localStorage.removeItem('el2_progress')")
    pg.reload(wait_until="load")
    pg.goto(B+"#/lesson/1",wait_until="load")
    pg.wait_for_timeout(800)
    # 盲听答对 → 精听 → 进入跟读
    pg.evaluate("window.el2BlindDone()"); pg.wait_for_timeout(400)
    pg.locator(".blind-opt").nth(BO["1"]["correctIdx"]).click(); pg.wait_for_timeout(500)
    pg.locator('[data-act="tostage"][data-v="2"]').click(); pg.wait_for_timeout(500)
    pg.wait_for_function("document.querySelector('.ktool')!==null",timeout=10000)
    pg.wait_for_timeout(300)

    print("① 跟读容器:",pg.locator('.kstage').count(),"| 工具条:",pg.locator('.ktool').count())
    print("   工具条 seg 组:",pg.locator('.ktool .seg').count(),"(期望2) | 读完了按钮:",pg.locator('.ktool .fbtn').count())
    print("   遍数档:",pg.locator('.ktool .seg').nth(1).inner_text().replace(chr(10),' '),"(期望 1遍/3遍)")
    print("   高亮行:",pg.locator('.krow.now').count(),"| 虚化行:",pg.locator('.krow.dim').count())
    pg.screenshot(path=str(OUT/"p2_shadow.png"))

    # 语言档（复用 intlang）
    pg.locator('.ktool .seg').nth(0).locator('span[data-v="en"]').click(); pg.wait_for_timeout(300)
    print("② 英档: 中文行:",pg.locator('.kstage .zh').count(),"(期望0)")
    pg.locator('.ktool .seg').nth(0).locator('span[data-v="bi"]').click(); pg.wait_for_timeout(300)

    # 遍数直选 3遍
    pg.locator('.ktool .seg').nth(1).locator('span[data-v="3"]').click(); pg.wait_for_timeout(300)
    on=pg.locator('.ktool .seg').nth(1).locator('span.on').inner_text()
    print("③ 遍数切3遍 选中:",on,"(期望 3遍)")
    print("   无旧5遍:",'5' not in pg.locator('.ktool').inner_text())

    # 点行聚焦
    pg.locator('.krow').nth(4).click(); pg.wait_for_timeout(300)
    print("④ 点第5行 高亮:",pg.locator('.krow.now').count()==1)

    # 读完了 → 学习完成卡（11-23 录音段已删）
    pg.locator('.ktool .fbtn').click(); pg.wait_for_timeout(500)
    st5 = pg.evaluate("""() => ({doneTitle: document.querySelector('.rct')?document.querySelector('.rct').innerText:null,
      steps: [...document.querySelectorAll('.stepper .st')].map(x=>x.innerText.trim())})""")
    print("⑤ 读完了进完成卡:", st5)
    assert st5["doneTitle"] == "学习完成" and st5["steps"] == ["盲听","精听","跟读"]
    print("=== JS 错误 ===",errs if errs else "无")
    br.close()
