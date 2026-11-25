# -*- coding: utf-8 -*-
"""v42 组 1 对稿图：左设计稿（.phone 评审外壳）/ 右 v42 实码，6 屏逐行。"""
import http.server
import socketserver
import threading
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

PROJ = Path(r"E:\04 少儿原版课程\06 新概念英语")
ROOT = PROJ / "ily-echo"
OUT = ROOT / "_ia_design" / "v42"
PORT = 8132


class Quiet(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(PROJ), **kw)

    def log_message(self, *a):
        pass


httpd = socketserver.TCPServer(("127.0.0.1", PORT), Quiet)
threading.Thread(target=httpd.serve_forever, daemon=True).start()

SHOTS = [
    # (编号, 标题, 稿 .shot 序号 0-based, v42 图, 是否横屏)
    ("1", "盲听 · 播完出题", 0, "s1_blind_quiz.png", False),
    ("2", "精听 · Anki 句卡", 1, "s2_intensive.png", False),
    ("3", "跟读 · 横屏主态", 2, "s3_shadow_landscape.png", True),
    ("4", "跟读 · 竖屏备态", 3, "s4_shadow_portrait.png", False),
]
# 11-23 用户决策：稿屏 5/6（录音页 / 录音完成卡）整段删除，不再参与对稿。


with sync_playwright() as pw:
    br = pw.chromium.launch(channel="msedge", headless=True)
    ctx = br.new_context(viewport={"width": 1700, "height": 1200}, device_scale_factor=1)
    p = ctx.new_page()
    p.goto(f"http://127.0.0.1:{PORT}/%E8%AE%BE%E8%AE%A1%E7%A8%BF_%E4%BA%94%E6%AE%B5%E6%B5%81%E7%A8%8B_v4_2.html",
           wait_until="networkidle")
    time.sleep(1.2)
    shots = p.locator(".shot .phone")
    print("稿内 .phone 数量：", shots.count())
    for idx, (no, title, si, img, land) in enumerate(SHOTS):
        el = shots.nth(si)
        el.screenshot(path=str(OUT / f"ref_s{no}.png"))
        print("截稿", no, title)
    br.close()
httpd.shutdown()

# ── 拼对比页 ──
rows = []
for no, title, si, img, land in SHOTS:
    rows.append(f"""
  <section class="row">
    <div class="meta"><b>{no}</b><span>{title}</span></div>
    <div class="cell ref{' land' if land else ''}"><img src="ref_s{no}.png" alt="稿 {no}"></div>
    <div class="cell ours{' land' if land else ''}"><img src="{img}" alt="v42 {no}"></div>
  </section>""")

html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>v42 组1 对稿</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#EEF1F4;font-family:"Noto Sans SC","Microsoft YaHei",system-ui,sans-serif;
  color:#263039;padding:28px 32px 40px}}
h1{{font-size:20px;font-weight:700;margin-bottom:4px}}
.sub{{font-size:12.5px;color:#5C6773;margin-bottom:20px}}
.sub code{{font-family:ui-monospace,Consolas,monospace;background:#fff;border:1px solid #E2E6EB;
  border-radius:4px;padding:1px 5px}}
.legend{{display:flex;gap:18px;font-size:12px;color:#5C6773;margin-bottom:18px}}
.legend i{{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:5px;vertical-align:middle}}
.row{{display:grid;grid-template-columns:132px 424px auto;gap:18px;align-items:start;justify-content:start;
  background:#fff;border:1px solid #E2E6EB;border-radius:14px;padding:16px 18px;margin-bottom:16px}}
.row.land{{grid-template-columns:132px 824px auto}}
.meta b{{display:block;width:26px;height:26px;border-radius:50%;background:#263039;color:#fff;
  font-size:13px;line-height:26px;text-align:center;margin-bottom:8px}}
.meta span{{font-size:12.5px;color:#5C6773;line-height:1.5}}
.cell{{background:#F4F6F8;border:1px dashed #D7DDE4;border-radius:10px;padding:8px;
  display:flex;justify-content:flex-start}}
.cell img{{display:block;max-width:100%;max-height:600px;width:auto;height:auto;border-radius:6px}}
.cell.ref img{{border-radius:30px}}
.tag{{font-size:11px;color:#8A939C;text-align:center;margin-top:6px}}
.obsolete{{display:flex;align-items:center;justify-content:center;width:100%;height:600px;text-align:center;line-height:2;color:#98A1AA;font-size:13px}}
</style></head><body>
<h1>设计稿 v4.2 × App 实码 · 组 1（屏 1–6）逐屏对稿</h1>
<div class="sub">左＝<code>设计稿_五段流程_v4_2.html</code> 原稿屏（含评审外壳 .phone）　右＝<code>ily-echo/v42/index.html</code> 实码（安全区替代假状态栏、去手机边框）　数据：L01 · 正文 16 句</div>
<div class="legend"><span><i style="background:#0B8A5F"></i>--focus 深绿</span>
<span><i style="background:#10B981"></i>--brand 亮绿</span>
<span><i style="background:#8A5E22"></i>--amberInk 收藏</span>
<span><i style="background:#E2E6EB"></i>--line 描边</span></div>
{''.join(rows)}
  <section class="row">
    <div class="meta"><b>✓</b><span>稿屏 5/6 已删除<br><small>11-23 用户决策</small></span></div>
    <div class="cell ref"><div class="obsolete">稿原「录音全篇」+「录音完成·分享到微信群」<br>两段整体移除，不再对照</div></div>
    <div class="cell ours"><img src="s6_study_done.png" alt="学习完成卡"></div>
  </section>
</body></html>"""
(OUT / "compare_g1.html").write_text(html, encoding="utf-8")

with sync_playwright() as pw:
    br = pw.chromium.launch(channel="msedge", headless=True)
    ctx = br.new_context(viewport={"width": 1780, "height": 1200}, device_scale_factor=1)
    p = ctx.new_page()
    p.goto((OUT / "compare_g1.html").as_uri(), wait_until="networkidle")
    time.sleep(1)
    p.screenshot(path=str(OUT / "对稿_组1_屏1-6.png"), full_page=True)
    br.close()
print("done")
