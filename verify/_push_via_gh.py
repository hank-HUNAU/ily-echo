# -*- coding: utf-8 -*-
"""当 git push 的 HTTPS 通道不可用时，用 gh api 的 git-data 通道推送。

与 git push 等价：按本地提交顺序逐个创建 blob/tree/commit 并更新远端 ref，
因此 6 个提交历史原样保留（不是压平成一个 sync commit）。

用法：
  py -3 _push_via_gh.py --dry-run     # 只打印计划，不写远端
  py -3 _push_via_gh.py               # 真推送
凭据由 gh 从 keyring 读取，脚本内不出现 token。
"""
import argparse
import base64
import json
import subprocess
from pathlib import Path

REPO = Path(r"E:\04 少儿原版课程\06 新概念英语\ily-echo")
OWNER, NAME = "hank-HUNAU", "ily-echo"
BASE = "23d5e24e309b86aba15cc81df422b4e5aeabfc51"   # 远端 main 当前 sha（已用 gh api 核实，用全 sha 比对）
BRANCH = "main"

ap = argparse.ArgumentParser()
ap.add_argument("--dry-run", action="store_true")
ARGS = ap.parse_args()


def git(*a, binary=False):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True)
    if r.returncode:
        raise RuntimeError("git " + " ".join(a) + " → " + r.stderr.decode("utf-8", "replace")[:300])
    return r.stdout if binary else r.stdout.decode("utf-8", "replace").strip()


def gh(endpoint, method="GET", payload=None, jq=None):
    cmd = ["gh", "api", endpoint, "-X", method]
    if payload is not None:
        cmd += ["--input", "-"]
    if jq:
        cmd += ["--jq", jq]
    r = subprocess.run(cmd, cwd=REPO, input=json.dumps(payload).encode("utf-8") if payload is not None else None,
                       capture_output=True)
    if r.returncode:
        raise RuntimeError("gh api " + endpoint + " → " + r.stderr.decode("utf-8", "replace")[:400])
    return r.stdout.decode("utf-8", "replace").strip()


commits = git("rev-list", "--reverse", f"{BASE}..HEAD").split()
print(f"待推提交 {len(commits)} 个：")
for c in commits:
    print("  " + c[:7], git("log", "-1", "--format=%s", c)[:90])

if ARGS.dry_run:
    print("\n[dry-run] 各提交变更文件：")
    for c in commits:
        files = git("diff-tree", "--no-commit-id", "--name-only", "-r", c).splitlines()
        print("  " + c[:7] + " → " + ", ".join(files))
    print("\n[dry-run] 不写远端。")
    raise SystemExit(0)

remote_head = gh(f"repos/{OWNER}/{NAME}/git/ref/heads/{BRANCH}", jq=".object.sha")
if remote_head != BASE:
    raise SystemExit(f"远端 main 已变动：{remote_head} != {BASE}，停止以免覆盖他人提交")

tree = gh(f"repos/{OWNER}/{NAME}/git/commits/{BASE}", jq=".tree.sha")
parent = BASE

for c in commits:
    lines = [x for x in git("diff-tree", "--no-commit-id", "--name-status", "-r", c).splitlines() if x.strip()]
    entries = []
    for line in lines:
        status, path = line.split("\t", 1)
        if status.startswith("D"):
            entries.append({"path": path, "mode": "100644", "type": "blob", "sha": None})
            continue
        mode = git("ls-tree", c, "--", path).split()[0]
        blob = git("show", f"{c}:{path}", binary=True)
        b64 = base64.b64encode(blob).decode("ascii")
        sha = gh(f"repos/{OWNER}/{NAME}/git/blobs", "POST",
                 {"content": b64, "encoding": "base64"}, jq=".sha")
        entries.append({"path": path, "mode": mode, "type": "blob", "sha": sha})
        print(f"  blob {c[:7]} {path} ({len(blob)} B)")

    if entries:
        tree = gh(f"repos/{OWNER}/{NAME}/git/trees", "POST",
                  {"base_tree": tree, "tree": entries}, jq=".sha")

    author_raw = git("log", "-1", "--format=%an%n%ae%n%aI", c).splitlines()
    payload = {
        "message": git("log", "-1", "--format=%B", c),
        "tree": tree,
        "parents": [parent],
        "author": {"name": author_raw[0], "email": author_raw[1], "date": author_raw[2]},
        "committer": {"name": author_raw[0], "email": author_raw[1], "date": author_raw[2]},
    }
    parent = gh(f"repos/{OWNER}/{NAME}/git/commits", "POST", payload, jq=".sha")
    print(f"commit {c[:7]} → 远端 {parent[:7]}")

gh(f"repos/{OWNER}/{NAME}/git/refs/heads/{BRANCH}", "PATCH", {"sha": parent, "force": False})
print("\n远端 main 已更新到", parent)

# 本地 tracking ref 同步（HTTPS 不通无法 fetch；这里指向刚推上去的同一串 commit）
subprocess.run(["git", "update-ref", f"refs/remotes/origin/{BRANCH}", parent], cwd=REPO, check=True)
print("本地 origin/main 已同步")
