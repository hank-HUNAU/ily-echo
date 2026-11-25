# -*- coding: utf-8 -*-
"""P2-2 精听 Anki 卡验收：走盲听答对自然进入精听。"""
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
    pg.evaluate("window.el2BlindDone()"); pg.wait_for_timeout(400)
    correct=BO["1"]["correctIdx"]
    pg.locator(".blind-opt").nth(correct).click(); pg.wait_for_timeout(500)
    pg.wait_for_function("document.querySelector('.int-card')!==null",timeout=10000)
    pg.wait_for_timeout(300)

    tag=pg.locator(".ankiTag").inner_text()
    en=pg.locator(".ankiEn").inner_text() if pg.locator(".ankiEn").count() else ""
    zh=pg.locator(".ankiZh").inner_text() if pg.locator(".ankiZh").count() else ""
    print("① 句卡:",tag,"| 英文:",en[:30],"| 中文:",zh[:20],"| 双语:",bool(en and zh))
    print("   收藏右上:",pg.locator(".ankiFav").count()==1,"| 三档seg:",pg.locator(".int-lang .seg span").count())
    pg.screenshot(path=str(OUT/"p2_intensive_card.png"))

    pg.locator('[data-act="intnext"]').click(); pg.wait_for_timeout(300)
    print("② 下一句:",pg.locator(".ankiTag").inner_text(),"(期望 句卡 2 / 16)")
    pg.locator('.int-lang .seg span[data-v="en"]').click(); pg.wait_for_timeout(300)
    print("③ 英档 英文/中文:",pg.locator(".ankiEn").count(),pg.locator(".ankiZh").count(),"(期望 1/0)")
    pg.locator('.int-lang .seg span[data-v="zh"]').click(); pg.wait_for_timeout(300)
    print("   中档 英文/中文:",pg.locator(".ankiEn").count(),pg.locator(".ankiZh").count(),"(期望 0/1)")
    pg.locator('.int-lang .seg span[data-v="bi"]').click(); pg.wait_for_timeout(300)

    before=pg.locator(".ankiFav.on").count()
    pg.locator(".ankiFav").click(); pg.wait_for_timeout(300)
    print("④ 收藏:",before,"→",pg.locator(".ankiFav.on").count())
    pg.evaluate("""(()=>{const c=document.getElementById('intCard');
      const t=(x,y)=>new Touch({identifier:1,target:c,clientX:x,clientY:y});
      c.dispatchEvent(new TouchEvent('touchstart',{changedTouches:[t(300,400)],bubbles:true}));
      c.dispatchEvent(new TouchEvent('touchend',{changedTouches:[t(120,405)],bubbles:true}));})()""")
    pg.wait_for_timeout(300)
    print("⑤ 左滑后:",pg.locator(".ankiTag").inner_text(),"(期望 句卡 3 / 16)")
    print("⑥ 语言档:",pg.locator('.int-lang .seg span').all_inner_texts(),"(无遍数)")
    print("=== JS 错误 ===",errs if errs else "无")
    br.close()
