"""
Crash Test dashboard server — stdlib only.

  python3 server.py           # http://localhost:8787
  GET  /                      static files from ./web (index.html default)
  GET  /results.json, /progress.jsonl
  GET  /api/status            {running, mode, services}
  POST /api/run  {"dry_run": true}?   spawns crash_test.py, stdout/stderr → run.log
  GET  /api/progress          {running, events:[...]}
"""
import json, os, subprocess, sys, threading, mimetypes
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(PROJECT_DIR, "web")
PROGRESS = os.path.join(PROJECT_DIR, "progress.jsonl")
PORT = int(os.getenv("PORT", "8787"))

def load_dotenv(path=os.path.join(PROJECT_DIR, ".env")):
    if not os.path.exists(path):
        return
    for raw in open(path, encoding="utf-8", errors="ignore"):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]
        elif " #" in v:
            v = v.split(" #", 1)[0].strip()
        if k and v and k not in os.environ:
            os.environ[k] = v

load_dotenv()

VENV_PY = os.path.join(PROJECT_DIR, ".venv", "bin", "python")
PYTHON = VENV_PY if os.path.exists(VENV_PY) else sys.executable

def services():
    e = os.getenv
    return {"daytona": bool(e("DAYTONA_API_KEY")),
            "anchor": bool(e("ANCHOR_API_KEY") or e("ANCHORBROWSER_API_KEY")),
            "surrealdb": bool(e("SPECTRON_URL") and e("SPECTRON_CONTEXT_ID") and e("SPECTRON_API_KEY")),
            "arize": bool(e("ARIZE_SPACE_ID") and e("ARIZE_API_KEY")),
            "model": "bedrock" if e("USE_BEDROCK") else "anthropic" if e("ANTHROPIC_API_KEY") else "sim"}

def mode():
    s = services()
    live = s["model"] != "sim" and s["daytona"] and not os.getenv("FORCE_DRY_RUN")
    return "LIVE" if live else "DRY_RUN"

_lock = threading.Lock()
_proc = None

def running():
    global _proc
    with _lock:
        if _proc is not None and _proc.poll() is None:
            return True
        return False

def start_run(dry_run):
    global _proc
    with _lock:
        if _proc is not None and _proc.poll() is None:
            return {"ok": False, "reason": "running"}
        open(PROGRESS, "w").close()
        env = os.environ.copy()
        m = mode()
        if dry_run or m != "LIVE":
            env["DRY_RUN"] = "1"; m = "DRY_RUN"
        else:
            env.pop("DRY_RUN", None)
        log = open(os.path.join(PROJECT_DIR, "run.log"), "w")
        _proc = subprocess.Popen([PYTHON, "crash_test.py"], cwd=PROJECT_DIR, env=env,
                                 stdout=log, stderr=subprocess.STDOUT)
        return {"ok": True, "mode": m, "pid": _proc.pid}

def read_events():
    events = []
    try:
        with open(PROGRESS, encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try: events.append(json.loads(line))
                except Exception: pass          # partially written last line
    except FileNotFoundError:
        pass
    return events

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=WEB_DIR, **kw)

    def log_message(self, fmt, *args):
        if args and "/api/progress" in str(args[0]):
            return
        super().log_message(fmt, *args)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def _json(self, obj, code=200):
        body = json.dumps(obj, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _file(self, path, ctype):
        try:
            with open(path, "rb") as f: body = f.read()
        except FileNotFoundError:
            return self._json({"error": "not found"}, 404)
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        p = self.path.split("?", 1)[0]
        if p == "/api/status":
            return self._json({"running": running(), "mode": mode(), "services": services()})
        if p == "/api/progress":
            return self._json({"running": running(), "events": read_events()})
        if p == "/results.json":
            return self._file(os.path.join(PROJECT_DIR, "results.json"), "application/json")
        if p == "/progress.jsonl":
            return self._file(PROGRESS, "application/x-ndjson")
        if p == "/run.log":
            return self._file(os.path.join(PROJECT_DIR, "run.log"), "text/plain; charset=utf-8")
        if not os.path.isdir(WEB_DIR):
            return self._json({"error": "web/ not found", "hint": "the dashboard lives in ./web/index.html"}, 404)
        return super().do_GET()

    def do_POST(self):
        p = self.path.split("?", 1)[0]
        if p == "/api/run":
            n = int(self.headers.get("Content-Length") or 0)
            body = {}
            if n:
                try: body = json.loads(self.rfile.read(n) or b"{}") or {}
                except Exception: body = {}
            return self._json(start_run(bool(body.get("dry_run"))))
        return self._json({"error": "not found"}, 404)

    def do_OPTIONS(self):
        self.send_response(204); self.end_headers()

if __name__ == "__main__":
    mimetypes.add_type("application/javascript", ".js")
    srv = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    srv.daemon_threads = True
    print(f"Crash Test server → http://localhost:{PORT}  mode={mode()}  python={PYTHON}", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
