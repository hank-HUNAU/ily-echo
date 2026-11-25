# -*- coding: utf-8 -*-
"""P2 学习完成卡验收（11-23 录音段已删）：三段终点 / 无录音入口 / 返回课程。"""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(r"E://04 少儿原版课程//06 新概念英语")
OUT = ROOT / "ily-echo" / "_p1_shots"
OUT.mkdir(exist_ok=True)
BASE = "http://127.0.0.1:8112/index.html"

with sync_playwright() as pw:
    b = pw.chromium.launch(channel="msedge", headless=True)
    ctx = b.new_context(viewport={"width": 420, "height": 900}, device_scale_factor=2, has_touch=True)
    p = ctx.new_page()
    errs = []
    p.on("pageerror", lambda e: errs.append(str(e)[:150]))

    # stage=3 现在是学习完成卡（不是录音段）
    p.goto(BASE + "#/home", wait_until="load")
    p.evaluate("""() => {
      const pr={_v:4,__v4:1,courses:{nce2:{"1":{stage:3,si:16,listened:{},shadow:{},hard:[],
        firstLearnAt:Date.now(),reviews:0,lastReviewAt:0,blindDone:true,revDone:null,revMiss:0}}}};
      localStorage.setItem('el2_progress',JSON.stringify(pr));
      localStorage.setItem('el2_mycourses',JSON.stringify(['nce2']));
      localStorage.removeItem('el2_intro');
    }""")
    p.goto(BASE + "#/lesson/1", wait_until="load")
    p.reload(wait_until="load")
    p.wait_for_timeout(1200)
    p.screenshot(path=str(OUT / "p2_study_done.png"))

    card = p.evaluate("""() => {
      const q=s=>document.querySelector(s);
      return {
        head: q('.topbar h1')?q('.topbar h1').innerText.trim():null,
        title: q('.rct')?q('.rct').innerText:null,
        sub: q('.rcs')?q('.rcs').innerText:null,
        rows: [...document.querySelectorAll('.rcrow')].map(r=>r.innerText.replace(/\\n/g,' ')),
        steps: [...document.querySelectorAll('.stepper .st')].map(x=>x.innerText.trim()),
        recBtns: document.querySelectorAll("[data-act^='rec']").length,
        acts: [...document.querySelectorAll('.rcacts button')].map(b=>b.innerText.trim())
      };
    }""")
    print("=== 学习完成卡 ===")
    for k,v in card.items(): print(f"  {k}: {v}")
    assert card["title"] == "学习完成" and card["head"] == "本课完成"
    assert card["steps"] == ["盲听","精听","跟读"] and card["recBtns"] == 0
    assert card["acts"] == ["完成，返回课程"]

    p.click("button[data-act='doneback']")
    p.wait_for_timeout(700)
    print("=== 返回课程 ===", p.evaluate("location.hash"))
    assert p.evaluate("location.hash").startswith("#/c/")
    print("=== JS 错误 ===", errs if errs else "无")
    b.close()
