# -*- coding: utf-8 -*-
"""P4 验收：听单首页（课本门禁/三视图/离线音频包真实下载）+ 全屏播放页（字幕跟随/四操作/更多）。"""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(r"E:\04 少儿原版课程\06 新概念英语")
OUT = ROOT / "ily-echo" / "_p1_shots"
OUT.mkdir(exist_ok=True)
BASE = "http://127.0.0.1:8113/index.html"

SEED = """() => {
  const DAY=86400000, now=Date.now();
  const pr={_v:4,__v4:1,courses:{nce2:{
    "1":{stage:3,si:0,listened:{},shadow:{},hard:[],firstLearnAt:now-2*DAY,reviews:1,lastReviewAt:now-2*DAY,blindDone:true,retellDone:true,revDone:null,revMiss:0},
    "2":{stage:2,si:3,listened:{},shadow:{},hard:[],firstLearnAt:now-1*DAY,reviews:0,lastReviewAt:0,blindDone:true,retellDone:false,revDone:null,revMiss:0}
  }}};
  localStorage.setItem('el2_progress',JSON.stringify(pr));
  localStorage.setItem('el2_mycourses',JSON.stringify(['nce2']));
  localStorage.removeItem('el2_intro');
  localStorage.removeItem('el2_fav');
  localStorage.removeItem('el2_pack');
  localStorage.removeItem('el2_listen');
}"""

with sync_playwright() as pw:
    b = pw.chromium.launch(channel="msedge", headless=True,
                           args=["--autoplay-policy=no-user-gesture-required"])
    ctx = b.new_context(viewport={"width": 420, "height": 900}, device_scale_factor=2, has_touch=True)
    p = ctx.new_page()
    errs = []
    p.on("pageerror", lambda e: errs.append(str(e)[:200]))

    p.goto(BASE + "#/home", wait_until="load")
    p.evaluate(SEED)
    p.goto(BASE + "#/listen", wait_until="load")
    p.reload(wait_until="load")
    p.wait_for_timeout(1800)
    p.screenshot(path=str(OUT / "p4_listen_recent.png"))

    print("=== 屏10 默认视图（最近在听）===")
    print(p.evaluate("""() => {
      const q=s=>document.querySelector(s);
      return {
        chips: [...document.querySelectorAll('.lchip')].map(c=>c.innerText.trim()+(c.classList.contains('on')?'*':'')+(c.disabled?'[锁]':'')),
        caps: [...document.querySelectorAll('.lcap')].map(c=>c.innerText.trim()+(c.classList.contains('on')?'*':'')),
        nowCard: q('.lcard')?q('.lcard').innerText.replace(/\\n/g,' | '):null,
        packs: [...document.querySelectorAll('.lpacks .lpack')].map(x=>x.innerText.replace(/\\n/g,' · ')),
        badges: [...document.querySelectorAll('.lbadge')].map(x=>x.innerText.replace(/\\n/g,'/'))
      };
    }"""))

    # 离线音频视图
    p.click("text=离线音频")
    p.wait_for_timeout(900)
    p.screenshot(path=str(OUT / "p4_listen_packs.png"))
    print("=== 离线音频视图 ===")
    print(p.evaluate("""() => {
      const q=s=>document.querySelector(s);
      return { pad: q('.lpad')?q('.lpad').innerText.replace(/\\n/g,' · '):null,
               packs: [...document.querySelectorAll('.lpack')].map(x=>x.innerText.replace(/\\n/g,' · ')) };
    }"""))

    # 真实下载 A1 包
    p.click('.lpack [data-act="packdl"]')
    print("下载中…")
    for _ in range(90):
        p.wait_for_timeout(500)
        st = p.evaluate("""() => {
          const r = JSON.parse(localStorage.getItem('el2_pack')||'{}');
          const k = Object.keys(r)[0];
          return k ? {id:k, ...r[k]} : null;
        }""")
        if st and st.get("state") in ("done", "fail"):
            break
    print("下载结果:", st)
    p.wait_for_timeout(600)
    print("行状态:", p.evaluate("""() => [...document.querySelectorAll('.lpack')].map(x=>x.innerText.replace(/\\n/g,' · '))"""))
    p.screenshot(path=str(OUT / "p4_listen_downloaded.png"))

    # 播放页
    p.goto(BASE + "#/player?c=nce2&n=2", wait_until="load")
    p.wait_for_timeout(1800)
    p.screenshot(path=str(OUT / "p4_player.png"))
    print("=== 屏11 播放页 ===")
    print(p.evaluate("""() => {
      const q=s=>document.querySelector(s);
      return {
        title: q('.ptitle b')?q('.ptitle b').innerText.trim():null,
        src: q('.ptitle div')?q('.ptitle div').innerText.replace(/\\n/g,' '):null,
        lines: document.querySelectorAll('.pline').length,
        now: q('.pline.now')?q('.pline.now').innerText.trim():null,
        nowIdx: q('.pline.now')?q('.pline.now').dataset.si:null,
        firstLine: q('.pline')?q('.pline').innerText.trim():null,
        ops: [...document.querySelectorAll('.pops button')].map(x=>x.innerText.trim()+':'+x.className),
        times: [...document.querySelectorAll('.pbar>span')].map(x=>x.innerText.trim()),
        ctl: document.querySelectorAll('.pctl>div').length,
        more: q('.pmore')?q('.pmore').innerText.trim():null
      };
    }"""))

    # 播放 → 字幕跟随
    p.click('[data-act="plrtoggle"]')
    p.wait_for_timeout(2600)
    info = p.evaluate("""() => {
      const q=s=>document.querySelector(s);
      return { playing: window.PLR.playing, pos: Math.round(window.PLR.pos*10)/10,
               si: window.PLR.si, now: q('.pline.now')?q('.pline.now').innerText.trim():null,
               pnow: q('#pnow')?q('#pnow').innerText:null, fill: q('#pfill')?q('#pfill').style.width:null };
    }""")
    print("=== 播放/字幕跟随 ===", info)
    p.screenshot(path=str(OUT / "p4_player_playing.png"))
    p.click('[data-act="plrtoggle"]')
    p.wait_for_timeout(500)

    # 收藏 + 切无字幕 + 更多
    p.click('[data-act="plrfav"]')
    p.wait_for_timeout(700)
    print("=== 收藏 ===", p.evaluate("""() => ({
      fav: JSON.parse(localStorage.getItem('el2_fav')||'[]'),
      op: document.querySelector('[data-act="plrfav"]').innerText.trim()
    })"""))

    p.click('[data-act="plrsub"]')
    p.wait_for_timeout(700)
    print("=== 无字幕（黑胶）===", p.evaluate("""() => ({
      disc: !!document.querySelector('.pvinyl'),
      lines: document.querySelectorAll('.pline').length,
      op: document.querySelector('[data-act="plrsub"]').innerText.trim()
    })"""))
    p.screenshot(path=str(OUT / "p4_player_disc.png"))
    p.click('[data-act="plrsub"]')
    p.wait_for_timeout(600)

    p.click('[data-act="plrmore"]')
    p.wait_for_timeout(600)
    print("=== 更多面板 ===", p.evaluate("""() => ({
      open: !document.getElementById('plrqueue').hidden,
      txt: document.getElementById('plrqueue').innerText.replace(/\\n/g,' | ').slice(0,120)
    })"""))
    if p.query_selector('[data-act="plrpick"]'):
        p.click('[data-act="plrpick"]')
        p.wait_for_timeout(500)
    print("角标:", p.evaluate("""() => { const i=document.querySelector('.pmore i'); return i?i.innerText:null; }"""))
    p.screenshot(path=str(OUT / "p4_player_more.png"))

    # 回听单 → 我的收藏 计数
    p.goto(BASE + "#/listen", wait_until="load")
    p.wait_for_timeout(1200)
    p.click("text=我的收藏")
    p.wait_for_timeout(800)
    print("=== 我的收藏视图 ===", p.evaluate("""() => ({
      caps: [...document.querySelectorAll('.lcap')].map(c=>c.innerText.trim()),
      rows: [...document.querySelectorAll('.lpack')].map(x=>x.innerText.replace(/\\n/g,' · '))
    })"""))
    p.screenshot(path=str(OUT / "p4_listen_fav.png"))

    # 队列：收藏复选 → 按队列播放
    p.goto(BASE + "#/player?c=nce2&n=1", wait_until="load")
    p.wait_for_timeout(1500)
    p.click('[data-act="plrmore"]')
    p.wait_for_timeout(500)
    # 先清空（上一段「更多面板」已勾过一次），再勾一次
    if p.query_selector('[data-act="plrqclear"]'):
        p.click('[data-act="plrqclear"]')
        p.wait_for_timeout(300)
    if p.query_selector('[data-act="plrpick"]'):
        p.click('[data-act="plrpick"]')
        p.wait_for_timeout(400)
    print("勾选后角标:", p.evaluate("() => { const i=document.querySelector('.pmore i'); return i?i.innerText:null; }"))
    p.click('[data-act="plrqplay"]')
    p.wait_for_timeout(2500)
    print("=== 队列播放 ===", p.evaluate("""() => ({
      queue: (window.PLR.queue||[]).map(q=>q.cid+':'+q.no),
      playing: window.PLR.playing,
      hash: location.hash,
      picked: Object.keys(window.PLR.picked||{}).length
    })"""))

    print("=== 听单位置已存 ===", p.evaluate("() => localStorage.getItem('el2_listen')"))
    print("=== JS 错误 ===", errs if errs else "无")
    b.close()
