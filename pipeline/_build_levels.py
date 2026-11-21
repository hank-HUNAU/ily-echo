# -*- coding: utf-8 -*-
"""NCE2 逐课「难度参考」分档（levelSrc=quantile）。

口径来源：设计稿 v4.2 增补规格（设计稿_五段流程_v4_2.html:179）
  「实测『命中最高层』96 课全为 A1_Starters 无区分度，改用九层加权分
   （A1_Starters=1…CAE=7）按分位分档（前 1/3 A1、中 1/3 A2、后 1/3 B1），不称 CEFR 认证」

输入：分支项目/词汇分析_96课/NCE2_单课覆盖_技能口径.csv（token 级九层计数）
输出：ily-echo/data/levels_nce2.json

注意：本档位是「难度参考」，不是官方 CEFR 等级；界面文案禁止写成「NCE2 = A1」。
"""
import csv, json
from pathlib import Path

ROOT = Path(r"E:\04 少儿原版课程\06 新概念英语")
SRC = ROOT / "分支项目" / "词汇分析_96课" / "NCE2_单课覆盖_技能口径.csv"
OUT = ROOT / "ily-echo" / "data" / "levels_nce2.json"

# 九层顺序（现行 registry）：前 7 层进加权轴，NGSL/NAWL 是词频/学术词表，不是 CEFR 台阶，不入轴
LAYERS = ["A1_Starters", "A1_Movers", "A2_Flyers", "KET", "PET", "FCE", "CAE"]
AXIS = {name: i + 1 for i, name in enumerate(LAYERS)}      # 1..7
BANDS = ["A1", "A2", "B1"]                                  # 前/中/后三分位

rows = list(csv.DictReader(open(SRC, encoding="utf-8-sig")))
assert len(rows) == 96, len(rows)

scored = []
for r in rows:
    cnt = {L: int(r.get(L) or 0) for L in LAYERS}
    tot = sum(cnt.values())
    score = round(sum(cnt[L] * AXIS[L] for L in LAYERS) / tot, 4) if tot else 0.0
    scored.append({"no": int(r["课号"]), "title": r["标题"].strip(), "tokens": tot,
                   "score": score, "dist": cnt})

order = sorted(scored, key=lambda x: (x["score"], x["no"]))
n = len(order)
cut1, cut2 = n // 3, (2 * n) // 3            # 32 / 64：前 32 A1、中 32 A2、后 32 B1
for idx, item in enumerate(order):
    item["level"] = BANDS[0] if idx < cut1 else (BANDS[1] if idx < cut2 else BANDS[2])

lessons = {str(it["no"]): it["level"] for it in scored}
packs = {b: sorted([it["no"] for it in scored if it["level"] == b]) for b in BANDS}

# 每包聚合：课数 / 总时长（取 data/L*.json 的 duration，真实值）/ 体积（按课程 sizeMB 均摊）
DATA = ROOT / "ily-echo" / "data"
CAT = json.loads((ROOT / "ily-echo" / "catalog.json").read_text(encoding="utf-8"))
nce2 = [c for c in CAT["courses"] if c["id"] == "nce2"][0]
per_mb = (nce2.get("sizeMB") or 0) / max(1, nce2.get("lessons") or 96)
durs = {}
for n in range(1, 97):
    f = DATA / f"L{n:02d}.json"
    try:
        durs[n] = float(json.loads(f.read_text(encoding="utf-8")).get("duration") or 0)
    except Exception:
        durs[n] = 0.0
packMeta = {}
for b in BANDS:
    nos = packs[b]
    packMeta[b] = {
        "lessons": len(nos),
        "durSec": round(sum(durs.get(n, 0) for n in nos), 1),
        "mb": round(len(nos) * per_mb, 1),
        "missingDur": [n for n in nos if not durs.get(n)],
    }

data = {
    "cid": "nce2",
    "mode": "perLesson",
    "levelSrc": "quantile",
    "label": "难度参考",
    "metric": "九层加权分（A1_Starters=1…CAE=7，token 加权）",
    "banding": "按 96 课得分三分位：前 1/3 A1 / 中 1/3 A2 / 后 1/3 B1",
    "excluded": ["NGSL", "NAWL"],
    "note": "难度参考，非官方 CEFR；禁止表述为「NCE2 = A1」",
    "generatedAt": "2026-11-21",
    "scoreRange": [order[0]["score"], order[-1]["score"]],
    "cuts": {"A1_max": order[cut1 - 1]["score"], "A2_max": order[cut2 - 1]["score"]},
    "lessons": lessons,
    "packs": packs,
    "packMeta": packMeta,
    "scores": {str(it["no"]): it["score"] for it in scored},
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

print("写出:", OUT)
print("得分区间 %.3f – %.3f | 切点 A1<=%.3f, A2<=%.3f" % (order[0]["score"], order[-1]["score"],
                                                        data["cuts"]["A1_max"], data["cuts"]["A2_max"]))
for b in BANDS:
    print(f"  {b}: {len(packs[b])} 课 -> {packs[b][:8]}{' ...' if len(packs[b])>8 else ''}")
print("抽查 L01 =", lessons["1"], "| L48 =", lessons["48"], "| L96 =", lessons["96"])
