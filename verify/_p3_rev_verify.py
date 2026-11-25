# -*- coding: utf-8 -*-
"""P3 验收：屏7 到期入口 / 屏8 完成本轮 / 复习两段有效提取 / 课程中心彩色四态。"""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(r"E:\04 少儿原版课程\06 新概念英语")
OUT = ROOT / "ily-echo" / "_p1_shots"
OUT.mkdir(exist_ok=True)
BASE = "http://127.0.0.1:8113/index.html"

SEED = """() => {
  const DAY=86400000, now=Date.now();
  const pr={_v:4,__v4:1,courses:{nce2:{
    "1":{stage:3,si:0,listened:{},shadow:{},hard:[],firstLearnAt:now-2*DAY,reviews:1,
         lastReviewAt:now-2*DAY,blindDone:true,retellDone:true,revDone:null,revMiss:0},
    "2":{stage:3,si:0,listened:{},shadow:{},hard:[],firstLearnAt:now-6*DAY,reviews:0,
         lastReviewAt:0,blindDone:true,retellDone:false,revDone:null,revMiss:0}
  }}};
  localStorage.setItem('el2_progress',JSON.stringify(pr));
  localStorage.setItem('el2_mycourses',JSON.stringify(['nce2']));
  localStorage.removeItem('el2_intro');
}"""

with sync_playwright() as pw:
    b = pw.chromium.launch(channel="msedge", headless=True)
    ctx = b.new_context(viewport={"width": 420, "height": 900}, device_scale_factor=2, has_touch=True)
    p = ctx.new_page()
    errs = []
    p.on("pageerror", lambda e: errs.append(str(e)[:160]))

    p.goto(BASE + "#/home", wait_until="load")
    p.evaluate(SEED)
    p.reload(wait_until="load")          # SPA hash 跳转不重读 localStorage，必须整页重载
    p.wait_for_timeout(900)
    p.goto(BASE + "#/lesson/1?m=rev&c=nce2", wait_until="load")
    p.wait_for_timeout(1400)
    p.screenshot(path=str(OUT / "p3_rev_entry.png"))

    print("=== 屏7 到期入口 ===")
    print(p.evaluate("""() => {
      const q=s=>document.querySelector(s);
      return {
        ttl: q('.rev-ttl')?q('.rev-ttl').innerText.trim():null,
        lab: q('.rev-lab')?q('.rev-lab').innerText.trim():null,
        pills: [...document.querySelectorAll('.rev-pills .pill')].map(x=>x.innerText.trim()),
        blind: q('.rev-blind .pill')?q('.rev-blind .pill').innerText.trim():null,
        note: q('.rev-note')?q('.rev-note').innerText.trim():null,
        acts: [...document.querySelectorAll('.rev-acts .fbtn')].map(x=>x.innerText.trim()),
        hasStepper: !!q('.stepper')
      };
    }"""))

    # 开始本轮 → 精听
    p.click("text=开始本轮")
    p.wait_for_timeout(700)
    p.screenshot(path=str(OUT / "p3_rev_jingting.png"))
    print("=== 开始本轮 → 精听 ===")
    print(p.evaluate("""() => ({
      steps: [...document.querySelectorAll('.stepper .st')].map((x,i)=>x.innerText.trim()+(x.classList.contains('on')?'*':'')),
      card: !!document.querySelector('.int-card'),
      foot: document.querySelector('.ankiFoot')?document.querySelector('.ankiFoot').innerText.replace(/\\n/g,' '):null
    })"""))

    # 精听门禁：还没滑完就点「进入跟读」
    p.click("text=进入跟读")
    p.wait_for_timeout(500)
    print("=== 精听门禁（未滑完）===")
    print(p.evaluate("""() => {
      const t=document.getElementById('el2toast');
      return { toast: t&&t.classList.contains('on')?t.innerText:null,
               stillJingting: !!document.querySelector('.int-card') };
    }"""))

    # 真实路径：把全部句卡翻完（L01 共 17 张，含首张题干）→ 16 次「下一句」
    ncards = p.evaluate("document.querySelectorAll('.int-card').length && +document.querySelector('.ankiTag').innerText.split('/')[1]")
    print("句卡总数:", ncards)
    for _ in range(int(ncards) - 1):
        p.click(".int-ctl .int-mini:last-child")
        p.wait_for_timeout(110)
    p.wait_for_timeout(400)
    print("=== 翻完 16 张句卡后 ===")
    print(p.evaluate("""() => {
      const st=JSON.parse(localStorage.getItem('el2_progress')).courses.nce2['1'].revDone;
      return {seen:Object.keys(st.seen||{}).length, s:st.s};
    }"""))
    p.click("text=进入跟读")
    p.wait_for_timeout(700)
    p.screenshot(path=str(OUT / "p3_rev_shadow.png"))
    print("=== 精听 → 跟读（seen 已满）===")
    print(p.evaluate("""() => ({
      on: [...document.querySelectorAll('.stepper .st')].map((x,i)=>x.innerText.trim()+(x.classList.contains('on')?'*':'')),
      kstage: !!document.querySelector('#kstage'),
      doneBtn: document.querySelector('.ktool .fbtn')?document.querySelector('.ktool .fbtn').innerText.trim():null
    })"""))

    # 读完了 → 两段齐，直接进屏 8（11-23 录音段已删）
    p.click("text=读完了")
    p.wait_for_timeout(1100)
    print("=== 跟读完 → 屏8 本轮收尾 ===")
    print(p.evaluate("""() => ({
      on: [...document.querySelectorAll('.stepper .st')].map((x,i)=>x.innerText.trim()+(x.classList.contains('on')?'*':'')),
      revDone: JSON.parse(localStorage.getItem('el2_progress')).courses.nce2['1'].revDone,
      shareBtns: document.querySelectorAll("[data-act='recshare']").length
    })"""))

    p.screenshot(path=str(OUT / "p3_rev_done.png"))
    print("=== 屏8 完成本轮 ===")
    print(p.evaluate("""() => {
      const q=s=>document.querySelector(s);
      const pr=JSON.parse(localStorage.getItem('el2_progress')).courses.nce2['1'];
      return {
        top: q('.topbar h1')?q('.topbar h1').innerText.trim():null,
        ttl: q('.rev-ttl')?q('.rev-ttl').innerText.trim():null,
        dots: [...document.querySelectorAll('.rnd .dot')].map(x=>x.innerText.trim()+':'+x.className.replace('dot','').trim()),
        rndlab: [...document.querySelectorAll('.rndlab span')].map(x=>x.innerText.trim()),
        pills: [...document.querySelectorAll('.rev-pills .pill')].map(x=>x.innerText.trim()),
        note: [...document.querySelectorAll('.rev-note')].map(x=>x.innerText.trim()),
        acts: [...document.querySelectorAll('.rev-acts .fbtn')].map(x=>x.innerText.trim()),
        prog: {reviews:pr.reviews, revMiss:pr.revMiss, revDone:pr.revDone, lastReviewAt:!!pr.lastReviewAt}
      };
    }"""))

    # 回到课程 → 课表应显示第 3 轮
    p.click("text=回到课程")
    p.wait_for_timeout(900)
    print("=== 回课程后课表标签 ===")
    print(p.evaluate("""() => {
      const c=[...document.querySelectorAll('.cell')].slice(0,3).map(x=>x.querySelector('b').innerText+' '+x.querySelector('span').innerText);
      return {cells:c};
    }"""))

    # 超期未通关：L2 首学 6 天前未复习（第 1 轮 due=6h 前）→ 超过 3 天宽限 → 标未通关
    p.goto(BASE + "#/lesson/2?m=rev&c=nce2", wait_until="load")
    p.wait_for_timeout(1200)
    p.screenshot(path=str(OUT / "p3_rev_late.png"))
    print("=== 超期入口（L2）===")
    print(p.evaluate("""() => {
      const q=s=>document.querySelector(s);
      return { ttl:q('.rev-ttl')?q('.rev-ttl').innerText.trim():null,
               note:[...document.querySelectorAll('.rev-note')].map(x=>x.innerText.trim()) };
    }"""))

    # 课程中心：彩色四态
    p.goto(BASE + "#/store", wait_until="load")
    p.wait_for_timeout(1200)
    p.screenshot(path=str(OUT / "p3_store.png"))
    print("=== 屏9 课程库 ===")
    print(p.evaluate("""() => {
      const q=s=>document.querySelector(s);
      const cs=[...document.querySelectorAll('.coCard')].map(c=>({
        name:c.querySelector('.coName').innerText.trim(),
        cls:c.querySelector('.cover').className.replace('cover','').trim(),
        badge:c.querySelector('.dlbadge')?c.querySelector('.dlbadge').className:'',
        ring:!!c.querySelector('.pring')
      }));
      const probe=(sel,prop)=>{const d=document.createElement('span');d.className=sel;document.body.appendChild(d);
        const v=getComputedStyle(d)[prop];d.remove();return v;};
      const box=document.createElement('div');box.innerHTML='<span class="cover dim"><img class="bkc"></span><span class="cover prog"><img class="bkc"></span>';
      document.body.appendChild(box);
      const bk=box.querySelectorAll('.bkc');
      const dimF=getComputedStyle(bk[0]).filter, progF=getComputedStyle(bk[1]).filter;
      const bd=document.createElement('span');bd.className='dlbadge ok';document.body.appendChild(bd);
      const okBg=getComputedStyle(bd).backgroundColor; bd.remove(); box.remove();
      return {
        cards:cs,
        foot:q('.stfoot')?q('.stfoot').innerText.replace(/\\n/g,' '):null,
        filters:{dim:dimF, prog:progF},
        okBadgeBg:okBg
      };
    }"""))

    print("=== JS 错误 ===", errs if errs else "无")
    b.close()
