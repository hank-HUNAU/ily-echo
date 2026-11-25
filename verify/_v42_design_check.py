import json
from playwright.sync_api import sync_playwright

FILE = 'E:/04 少儿原版课程/06 新概念英语/设计稿_五段流程_v4_2.html'
OUT  = 'E:/04 少儿原版课程/06 新概念英语/设计稿_五段流程_v4_2_截图.png'

BANNED = [
    '选一个答案，再按下播放','一次一层：先出题干中文','全程零字幕','逐句跟读 · 不录音、不打分',
    '焦点恒在正中一行','不用写，说出来就行','对照即反馈，不打分数','选一个就行，随时可以换',
    '背诵＝视频 MP4','逐句首词 + 关键词（占位）','自动收藏仅作','五段都走完了',
    '这一轮从精听开始，盲听不用再做','盲听只在首次学习做一次','才算一次有效提取',
    '收藏喜欢的课文，随时听','正在播放','提交答案','最近在学','听完一遍，选答案','答对 → 精听','答错 → 重听 1 遍','再错 → 显示答案','作答 1 / 2','已盲听 1 遍',
    '全部 96','全部课程'
]
FIRSTUSE = ['断点录制可暂停继续，最后合成完整录音']

JS = """
(BANNED) => {
  const imgs = [...document.querySelectorAll('img')];
  const shots = [...document.querySelectorAll('.shot')];
  const overflow = [];
  shots.forEach((s, idx) => {
    const scr = s.querySelector('.scr');
    if (!scr) return;
    const box = scr.getBoundingClientRect();
    const selfOv = scr.scrollHeight - scr.clientHeight;
    let childMax = 0, worst = '';
    [...scr.querySelectorAll('*')].forEach(el => {
      const st = getComputedStyle(el);
      if (st.position === 'absolute' || st.position === 'fixed' || st.display === 'none') return;
      const b = el.getBoundingClientRect();
      if (b.height === 0 || b.width === 0) return;
      const ov = Math.max(0, b.bottom - box.bottom, b.right - box.right);
      if (ov > childMax) { childMax = ov; worst = (typeof el.className === 'string' ? el.className : '') || el.tagName; }
    });
    if (selfOv > 1 || childMax > 1) {
      overflow.push({ n: idx + 1, lab: (s.querySelector('.lab') || {}).innerText || '', selfOv, childMax: Math.round(childMax), worst });
    }
  });
  const navs = [...document.querySelectorAll('.flownav')];
  const navClickable = navs.filter(n =>
    n.hasAttribute('onclick') || n.querySelector('[data-act]') || getComputedStyle(n).cursor === 'pointer'
  ).length;
  const labs = [...document.querySelectorAll('.lab .n')].map(n => Number(n.innerText));
  const groups = [...document.querySelectorAll('.grouphead')].map(g => {
    const row = g.nextElementSibling;
    return { text: g.innerText.split('\\n')[0], shots: row ? row.querySelectorAll('.shot').length : 0 };
  });
  const scrTexts = [...document.querySelectorAll('.scr')].map(s => s.innerText);
  const bannedHits = [];
  BANNED.forEach(b => scrTexts.forEach((t, i) => { if (t.includes(b)) bannedHits.push({ scr: i + 1, text: b }); }));
  const allText = document.body.innerText;
  const shot4 = shots.slice(9);
  const noImgInGroup4 = shot4.every(s => !s.querySelector('img'));
  const fabGreen = shot4[0] ? !!shot4[0].querySelector('[style*="background:#10B981"][style*="border:4px solid #FFFFFF"]') : false;
  /* 屏 10 跨课本升级 / 屏 11 来源行 */
  const s10 = shots[9], s11 = shots[10];
  const s10t = s10.querySelector('.scr').innerText;
  const listen = {
    courseChips: s10.querySelectorAll('.hscroll > span').length,
    lockedChip:  !!s10.querySelector('.hscroll > span svg rect'),
    packRows:    (s10t.match(/课 · /g) || []).length,
    hasOfflineTab: s10t.includes('离线音频'),
    hasViewAll:    s10t.includes('查看全部'),
    hasManage:     s10t.includes('管理'),
    hasRef:        s10t.includes('参考'),
    hasDone:       s10t.includes('已下载'),
    hasRun:        s10t.includes('47%'),
    hasDownBtn:    !!s10.querySelector('svg path[d="M12 4v11M7 10l5 5 5-5M4 20h16"]'),
    srcLine:       s11.innerText.includes('新概念 2 · L1')
  };
  /* 跟读两屏工具条同族断言（屏 3 横屏 / 屏 4 竖屏） */
  const ktool = [2, 3].map(i => {
    const k = shots[i].querySelector('.ktool');
    if (!k) return null;
    const kids = [...k.children];
    return {
      n: kids.length,
      h: kids.map(c => Math.round(c.getBoundingClientRect().height)),
      segSegs: [...k.querySelectorAll('.seg')].map(s => s.children.length).join('/'),
      hasPill: !!k.querySelector('.pill'),
      inlineW: kids.some(c => ((c.getAttribute('style') || '')).includes('min-width')),
      btn: (k.querySelector('.fbtn') || { innerText: '' }).innerText.trim(),
      btnRadius: k.querySelector('.fbtn') ? getComputedStyle(k.querySelector('.fbtn')).borderRadius : ''
    };
  });
  /* 滚动容器不得裁行（横屏 5 行必须在 230px 内放下） */
  const kstageOv = shots.map((s, i) => {
    const k = s.querySelector('.kstage');
    return k ? { n: i + 1, ov: Math.round(k.scrollHeight - k.clientHeight) } : null;
  }).filter(Boolean);
  return {
    title: document.title,
    shots: shots.length, labs: labs.length, labSeq: labs.join(','),
    groups, phones: document.querySelectorAll('.phone').length,
    wide: document.querySelectorAll('.shot.wide').length,
    decisions: document.querySelectorAll('.decisions li').length,
    navs: navs.length, navClickable,
    imgs: imgs.length,
    imgSrcs: imgs.map(i => i.getAttribute('src')),
    bannedHits,
    noImgInGroup4, fabGreen, listen, ktool, kstageOv,
    overflow,
    docW: document.documentElement.scrollWidth,
    docH: document.documentElement.scrollHeight
  };
}
"""

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, channel='msedge')
    ctx = browser.new_context(viewport={'width': 1660, 'height': 1000}, device_scale_factor=1)
    page = ctx.new_page()
    errs = []
    page.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)[:160]))
    page.on('console', lambda m: errs.append('console: ' + m.text[:160]) if m.type == 'error' else None)

    page.goto('file:///' + FILE.replace('\\', '/').replace('E:/', 'E:/'), wait_until='load')
    page.wait_for_timeout(500)

    # 等封面图真实加载
    page.evaluate("""async () => {
      await Promise.all([...document.querySelectorAll('img')].map(i => i.complete ? 1 :
        new Promise(res => { i.onload = res; i.onerror = res; setTimeout(res, 3000); })));
    }""")

    r = page.evaluate(JS, BANNED)
    # FIRSTUSE 常量注入进第二个 evaluate 太绕，直接在 Python 侧补查
    body_text = page.evaluate("() => document.body.innerText")
    r['firstUseKept'] = [f for f in FIRSTUSE if f in body_text]

    print('[结构] title=' + r['title'])
    print(f"[结构] shots={r['shots']} labs={r['labs']} phones={r['phones']} wide={r['wide']} decisions={r['decisions']}")
    print('[结构] 编号序列=' + r['labSeq'])
    print('[分组] ' + json.dumps(r['groups'], ensure_ascii=False))
    print(f"[进度条] flownav={r['navs']} 可点击={r['navClickable']} (应为 0)")
    print(f"[封面] imgs={r['imgs']} 路径={r['imgSrcs']}")
    print(f"[组4] 零封面图={r['noImgInGroup4']} 凸起圆钮绿={r['fabGreen']}")
    L = r['listen']
    print(f"[听单升级] 课本胶囊={L['courseChips']}(应4) 锁定置灰={L['lockedChip']} 音频包行={L['packRows']}(应3)")
    print(f"[听单升级] 离线音频胶囊={L['hasOfflineTab']} 悬空入口(查看全部)={L['hasViewAll']}(应False) 悬空入口(管理)={L['hasManage']}(应False) 参考档={L['hasRef']} 已下载={L['hasDone']} 下载中={L['hasRun']} 下载键={L['hasDownBtn']} 播放页来源行={L['srcLine']}")
    for idx, k in enumerate(r['ktool']):
        if not k:
            print(f"[工具条] 屏{idx+3} 缺失 .ktool"); continue
        print(f"[工具条] 屏{idx+3} 件数={k['n']} 高={k['h']} 分段段数={k['segSegs']} 残留pill={k['hasPill']} inline宽={k['inlineW']} 按钮='{k['btn']}' 圆角={k['btnRadius']}")
    for k in r['kstageOv']:
        print(f"[滚动容器] 屏{k['n']} 内容溢出={k['ov']}px (应 0)")
    print(f"[文案] 禁用句残留={len(r['bannedHits'])}")
    for h in r['bannedHits']:
        print(f"   残留 屏{h['scr']}：{h['text']}")
    print(f"[文案] 首用提示保留={len(r['firstUseKept'])}/1 → {r['firstUseKept']}")
    print(f"[溢出] {len(r['overflow'])} 屏有问题")
    for o in r['overflow']:
        print(f"   #{o['n']} {o['lab'][:40]} | 容器滚动溢出={o['selfOv']}px 子元素越界={o['childMax']}px ({o['worst']})")
    print(f"[页面] docW={r['docW']} docH={r['docH']} | JS 错误={len(errs)}")
    for e in errs:
        print('   ' + e)

    page.screenshot(path=OUT, full_page=True)
    print('[截图] ' + OUT)

    L = r['listen']
    ok_listen = (L['courseChips'] == 4 and L['lockedChip'] and L['packRows'] == 3 and
        L['hasOfflineTab'] and L['hasRef'] and
        (not L['hasViewAll']) and (not L['hasManage']) and
        L['hasDone'] and L['hasRun'] and L['hasDownBtn'] and L['srcLine'])
    """跟读两屏工具条同族：3 件 / 同高 / 分段 3+2 / 无 pill / 无 inline 宽 / 全圆按钮"""
    ok_ktool = all(k is not None for k in r['ktool']) and all(
        k['n'] == 3 and len(set(k['h'])) == 1 and k['segSegs'] == '3/2' and
        not k['hasPill'] and not k['inlineW'] and k['btn'].startswith('读完了') and
        k['btnRadius'].startswith('999')
        for k in r['ktool'])
    ok_imgs = r['imgs'] == 4
    ok_kstage = all(k['ov'] <= 1 for k in r['kstageOv'])
    pass_all = (r['shots'] == 11 and r['labs'] == 11 and r['phones'] == 11 and
        r['labSeq'] == ','.join(str(i) for i in range(1, 12)) and
        len(r['groups']) == 4 and [g['shots'] for g in r['groups']] == [6, 2, 1, 2] and
        r['navClickable'] == 0 and ok_imgs and ok_listen and ok_ktool and ok_kstage and
        len(r['bannedHits']) == 0 and len(r['firstUseKept']) == 1 and
        r['noImgInGroup4'] and r['fabGreen'] and
        len(r['overflow']) == 0 and len(errs) == 0)
    print('[总判定] ' + ('PASS' if pass_all else 'FAIL'))
    browser.close()
    raise SystemExit(0 if pass_all else 1)
