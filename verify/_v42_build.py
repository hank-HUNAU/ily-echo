# -*- coding: utf-8 -*-
"""【已冻结 · 请勿重跑】v42 原型脚手架（2026-11-22）

它只做过「从主 index.html 复制 → 加 <base href="../"> → 禁 SW」的初始搭建。
此后 v42/index.html 已按设计稿 v4.2 逐组重画（组 1 屏 1-6 已完成），
与主 App 的渲染层持续分叉 —— 重跑本脚本会把这些改动全部覆盖掉。

同步主 App 后续修复的做法：手工挑补丁打到 v42/index.html，不要重新生成。

原始用途记录：生成 v42 独立原型骨架：复用主 App 逻辑，套设计稿 v4.2 视觉。
"""
from pathlib import Path
ROOT = Path(r"E:\04 少儿原版课程\06 新概念英语\ily-echo")
src = (ROOT / "index.html").read_text(encoding="utf-8")
out = ROOT / "v42"
out.mkdir(exist_ok=True)

# 资产走上级目录（data/audio/covers/catalog/blind_options）
src = src.replace('<meta charset="utf-8" data-page-node-id="qQhZAkRop4bIHsrFjgoiia">',
                  '<meta charset="utf-8" data-page-node-id="qQhZAkRop4bIHsrFjgoiia">\n<base href="../">', 1)
# 原型不注册 SW，避免控制主 App 作用域
src = src.replace("if ('serviceWorker' in navigator) {\n  window.addEventListener('load', function(){ navigator.serviceWorker.register('sw.js').catch(function(){}); });",
                  "/* v42 prototype: no service worker registration */\nif (false) {", 1)

CSS = r"""
/* ===== v42 原型：设计稿 v4.2 骨架（安全区替代假状态栏）===== */
body:has(#app.v42-lesson) .wrap{padding:0;max-width:none}
body:has(#app.v42-lesson) nav.tabs{display:none}
#app.v42-lesson{--ink:#263039;--sub:#5C6773;--line:#E2E6EB;--bg:#F4F6F8;--focus:#0B8A5F;
 --focusDeep:#08704D;--brand:#10B981;--brandSoft:#E6F7F0;
 min-height:100vh;background:var(--bg);color:var(--ink);padding-top:env(safe-area-inset-top,0px);
 display:flex;flex-direction:column}
.v42-lesson .v42-head{display:flex;justify-content:space-between;align-items:center;padding:calc(8px + env(safe-area-inset-top,0px)) 20px 2px;color:var(--sub);font-size:12.5px;flex:0 0 auto}
.v42-lesson .v42-head a{color:var(--sub);text-decoration:none}
.v42-lesson .flownav{display:flex;align-items:center;justify-content:center;gap:3px;padding:7px 8px 9px;border-bottom:1px solid var(--line);background:transparent;flex:0 0 auto}
.v42-lesson .fn{display:flex;flex-direction:column;align-items:center;gap:2px;width:58px;font-size:10.5px;color:var(--sub)}
.v42-lesson .fni{width:22px;height:22px;border-radius:50%;border:1.5px solid var(--line);display:flex;align-items:center;justify-content:center;font-size:10px;font-style:normal;font-weight:600}
.v42-lesson .fn.on{color:var(--focusDeep)}
.v42-lesson .fn.on .fni{border-color:var(--focus);background:#EDF1F4;color:var(--focusDeep)}
.v42-lesson .fn.done .fni{background:var(--focus);border-color:var(--focus);color:#fff}
.v42-lesson .fnar{color:var(--line);font-size:11px}
.v42-lesson .v42-body{flex:1;min-height:0;display:flex;flex-direction:column;overflow:hidden}
.v42-lesson .big{font-family:Georgia,"Times New Roman",serif;font-size:21px;line-height:1.55;color:var(--ink);text-align:center}
.v42-lesson .zhline{font-size:14px;color:var(--sub);line-height:1.6;text-align:center}
.v42-lesson .fbtn{display:flex;align-items:center;justify-content:center;gap:8px;border:0;border-radius:16px;font-family:inherit;font-size:16px;font-weight:600;min-height:54px;background:var(--focus);color:#fff;cursor:pointer;width:100%}
.v42-lesson .fbtn.ghost{background:transparent;color:var(--sub);font-size:14px;font-weight:500;border:1.5px solid var(--line)}
.v42-lesson .fbtn.sm{min-height:44px;font-size:13.5px;border-radius:12px;width:auto}
.v42-lesson .opt{display:flex;align-items:center;gap:10px;width:100%;border:1.5px solid var(--line);background:#fff;border-radius:14px;padding:11px 12px;font-size:14.5px;text-align:left;color:var(--ink);cursor:pointer}
.v42-lesson .opt b{flex:0 0 24px;height:24px;border-radius:50%;background:#F1F3F5;color:var(--sub);font-size:12px;display:flex;align-items:center;justify-content:center}
.v42-lesson .opt.right{border-color:var(--focus);background:var(--brandSoft)}
.v42-lesson .opt.wrong{border-color:var(--bad);background:#FCEBEB}
.v42-lesson .ankiCard{background:var(--bg);border:1px solid var(--line);border-radius:16px;padding:14px 16px;display:flex;flex:1;flex-direction:column;min-height:0;touch-action:pan-y;user-select:none;margin:10px 16px}
.v42-lesson .ankiTop{display:flex;justify-content:space-between;align-items:center;font-size:11.5px;color:var(--sub)}
.v42-lesson .ankiTag{background:var(--brandSoft);color:var(--focusDeep);border-radius:999px;padding:3px 9px;font-weight:600}
.v42-lesson .ankiBody{flex:1;display:flex;flex-direction:column;justify-content:center;gap:10px;text-align:center}
.v42-lesson .ankiFoot{display:flex;justify-content:space-between;font-size:11px;color:var(--sub);border-top:1px solid var(--line);padding-top:8px;margin-top:8px}
.v42-lesson .seg{display:flex;gap:3px;background:#F1F3F5;border-radius:999px;padding:3px}
.v42-lesson .seg span{padding:5px 11px;border-radius:999px;font-size:12px;color:var(--sub);white-space:nowrap;cursor:pointer}
.v42-lesson .seg span.on{background:#fff;color:var(--focusDeep);font-weight:600}
.v42-lesson .v42-play{background:#fff;border-top:1px solid var(--line);padding:4px 24px 6px;flex:0 0 auto}
.v42-lesson .v42-track{height:4px;background:#E3E5E8;border-radius:2px;position:relative}
.v42-lesson .v42-track i{position:absolute;left:0;top:0;height:4px;background:var(--focus);border-radius:2px}
.v42-lesson .v42-track b{position:absolute;top:-5px;width:14px;height:14px;border-radius:50%;background:var(--focus);border:2.5px solid #fff;margin-left:-7px}
.v42-lesson .v42-ctl{display:flex;align-items:center;justify-content:center;gap:26px;padding:4px 20px calc(10px + env(safe-area-inset-bottom,0px));background:#fff;flex:0 0 auto}
.v42-lesson .v42-mini{width:44px;height:44px;display:flex;align-items:center;justify-content:center;cursor:pointer}
.v42-lesson .v42-main{width:56px;height:56px;border-radius:50%;background:var(--focus);display:flex;align-items:center;justify-content:center;cursor:pointer}
.v42-lesson .v42-kstage{flex:1;min-height:0;display:flex;flex-direction:column;justify-content:center;overflow-y:auto;background:#fff;margin:0 16px;border-radius:14px;border:1px solid var(--line)}
.v42-lesson .v42-kstage.land{height:230px;flex:0 0 230px;padding:2px 0}
.v42-lesson .v42-row{padding:5px 18px;text-align:center;transition:opacity .2s}
.v42-lesson .v42-row .en{font-family:Georgia,"Times New Roman",serif;font-size:16px;line-height:1.4;color:var(--ink)}
.v42-lesson .v42-row .zh{font-size:12px;color:var(--sub);margin-top:2px}
.v42-lesson .v42-row.dim{opacity:.32}
.v42-lesson .v42-row.now .en{font-size:21px;font-weight:700}
.v42-lesson .land .v42-row{padding:2px 18px}
.v42-lesson .land .v42-row .en{line-height:1.32}
.v42-lesson .land .v42-row .zh{margin-top:0}
.v42-lesson .land .v42-row.now .en{font-size:19px}
.v42-lesson .ktool{display:flex;align-items:center;justify-content:flex-start;gap:10px;padding:8px 12px;border-top:1px solid var(--line);background:#fff;flex:0 0 auto}
.v42-lesson .ktool .fbtn.sm{min-height:34px;min-width:0;border-radius:999px;font-size:13px;font-weight:600;padding:0 15px;margin-left:auto}
.v42-lesson .v42-stepper{position:fixed;left:12px;right:12px;top:calc(56px + env(safe-area-inset-top,0px));z-index:60;display:flex;gap:6px;padding:8px;border-radius:12px;background:rgba(255,255,255,.97);border:1px solid var(--line);transition:opacity .2s}
.v42-lesson .v42-stepper.hidden{opacity:0;pointer-events:none}
.v42-lesson .v42-stepper span{flex:1;text-align:center;font-size:11px;color:var(--focusDeep)}
.v42-lesson .v42-card{background:#fff;border:1px solid var(--line);border-radius:14px;padding:12px 14px;margin:14px 16px}
.v42-lesson .v42-rowline{display:flex;justify-content:space-between;margin-top:8px;font-size:13px;color:var(--sub)}
"""

src = src.replace("</style>", CSS + "\n</style>", 1)
(out / "index.html").write_text(src, encoding="utf-8")
print("built", out / "index.html", len(src))
