# -*- coding: utf-8 -*-
"""验收用静态服务：8112 / 8113 指向 ily-echo/。仅本地，不对外。"""
import http.server
import threading
import time
from pathlib import Path

ROOT = Path(r"E:\04 少儿原版课程\06 新概念英语\ily-echo")


class Quiet(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)

    def log_message(self, *a):
        pass


for port in (8112, 8113):
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), Quiet)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    print("serving", port, flush=True)
while True:
    time.sleep(1)
