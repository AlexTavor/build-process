#!/usr/bin/env python3
"""Run the trust-enforcement spike without the model; see ../trust-enforcement.md.

Usage: python3 -B spike.py <rules|hook|both> <mode> <dir> [--claude PATH] [--untrusted]

Makes a fresh toy repo in <dir>/<variant>-<mode> with setup.sh and starts `claude -p` in it with
stream-json input and output and --permission-prompt-tool stdio. A local fake Messages API plays
the model, so the run needs no login and costs no tokens. Each command form in prompt.txt is its
own user turn, and the fake API answers it with one Bash call. Claude Code's own permission checks
and hooks run as usual. CLAUDE_CONFIG_DIR points at a throwaway config in the run folder that
marks toy as trusted, as a project the owner has opened would be (2.1.284 ignores a project's
allow rules until then); --untrusted leaves that mark out.
Every permission question is logged and answered no. Each form ends up:
  asked       a question came and was answered no
  refused     refused with no question
  ran         ran with no question (checked against origin.git's refs and toy/marker.txt)
  not tested  a classifier request came during its turn; the fake API answers those with an
              error, not a made-up decision
Prints one line per form and writes results.json, out.jsonl and side.log in the run folder.
"""
import argparse, itertools, json, os, queue, re, shutil, subprocess, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

here = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("variant", choices=["rules", "hook", "both"])
ap.add_argument("mode")
ap.add_argument("dir")
ap.add_argument("--claude", default="claude")
ap.add_argument("--untrusted", action="store_true")
args = ap.parse_args()

D = os.path.join(os.path.realpath(args.dir), f"{args.variant}-{args.mode}")
shutil.rmtree(D, ignore_errors=True)
subprocess.run(["sh", f"{here}/setup.sh", D, args.variant], check=True)
T, O = f"{D}/toy", f"{D}/origin.git"
LABELS = re.findall(r"^\d+\. (.+)$", open(f"{here}/prompt.txt").read(), re.M)
R = [{"label": l.replace("TOY", "<toy>"), "command": l.replace("TOY", T), "questions": [],
      "classifier": 0, "result": None} for l in LABELS]
cur = 0  # index of the form whose turn is running
CLASSIFIER = re.compile(r"(?i)classifier|auto mode|soft_deny|hard_deny|security monitor")
ids = itertools.count(1)

def blocks(m): return m["content"] if isinstance(m["content"], list) else [{"type": "text", "text": m["content"]}]

def reply(body):
    """The fake model's answer: the form's Bash call, then "done". None means: answer with an error."""
    names = sorted(t.get("name", "") for t in body.get("tools", []))
    if "Bash" not in names:  # a side request
        system = body.get("system", "")
        system = " ".join(b.get("text", "") for b in system) if isinstance(system, list) else system
        classifier = bool(CLASSIFIER.search(json.dumps(body)))
        with open(f"{D}/side.log", "a") as f:
            f.write(f"form {cur + 1} classifier={classifier} model={body.get('model')} tools={names}\n"
                    f"  system: {system[:1500]!r}\n")
        if classifier:
            R[cur]["classifier"] += 1
            return None
        return {"type": "text", "text": "ok"}
    msgs = body["messages"]
    for i in range(len(msgs) - 1, -1, -1):
        marks = [b["text"].split("SCRIPT:", 1)[1] for b in blocks(msgs[i]) if "SCRIPT:" in b.get("text", "")]
        if msgs[i]["role"] == "user" and marks:
            if any(b.get("type") == "tool_use" for m in msgs[i + 1:] for b in blocks(m)):
                break
            call = json.JSONDecoder().raw_decode(marks[-1])[0]
            return {"type": "tool_use", "id": f"toolu_fake_{next(ids):04d}", "name": "Bash", "input": call}
    return {"type": "text", "text": "done"}

class FakeAPI(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def send_json(self, code, obj):
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
    def do_GET(self): self.send_json(404, {"type": "error", "error": {"type": "not_found_error", "message": "fake API"}})
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        if not self.path.startswith("/v1/messages") or "count_tokens" in self.path:
            return self.send_json(200, {"input_tokens": 1})
        block = reply(body)
        if block is None:
            return self.send_json(400, {"type": "error", "error": {"type": "invalid_request_error",
                                                                    "message": "fake API: no classifier answers"}})
        tool = block["type"] == "tool_use"
        stop = "tool_use" if tool else "end_turn"
        msg = {"id": f"msg_fake_{next(ids)}", "type": "message", "role": "assistant", "model": body.get("model", "fake"),
               "content": [block], "stop_reason": stop, "stop_sequence": None, "usage": {"input_tokens": 1, "output_tokens": 1}}
        if not body.get("stream"):
            return self.send_json(200, msg)
        delta = {"type": "input_json_delta", "partial_json": json.dumps(block["input"])} if tool else {"type": "text_delta", "text": block["text"]}
        events = [("message_start", {"message": dict(msg, content=[], stop_reason=None)}),
                  ("content_block_start", {"index": 0, "content_block": dict(block, input={}) if tool else dict(block, text="")}),
                  ("content_block_delta", {"index": 0, "delta": delta}),
                  ("content_block_stop", {"index": 0}),
                  ("message_delta", {"delta": {"stop_reason": stop, "stop_sequence": None}, "usage": {"output_tokens": 1}}),
                  ("message_stop", {})]
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.end_headers()
        for name, data in events:
            self.wfile.write(f"event: {name}\ndata: {json.dumps(dict(data, type=name))}\n\n".encode())

server = ThreadingHTTPServer(("127.0.0.1", 0), FakeAPI)
threading.Thread(target=server.serve_forever, daemon=True).start()
env = {k: os.environ[k] for k in ("HOME", "PATH", "USER", "TMPDIR", "LANG") if k in os.environ}
os.makedirs(f"{D}/config")
with open(f"{D}/config/.claude.json", "w") as f:
    json.dump({"projects": {} if args.untrusted else {T: {"hasTrustDialogAccepted": True}}}, f)
env.update(DISABLE_AUTOUPDATER="1", ANTHROPIC_BASE_URL=f"http://127.0.0.1:{server.server_port}",
           ANTHROPIC_API_KEY="fake-key-for-the-local-fake-api", CLAUDE_CONFIG_DIR=f"{D}/config")
cmd = [args.claude, "-p", "--input-format", "stream-json", "--output-format", "stream-json", "--verbose",
       "--include-hook-events", "--setting-sources", "project,local", "--permission-mode", args.mode,
       "--model", "sonnet", "--permission-prompt-tool", "stdio"]
proc = subprocess.Popen(cmd, cwd=T, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
lines = queue.Queue()
threading.Thread(target=lambda: [lines.put(l) for l in proc.stdout] + [lines.put(None)], daemon=True).start()
info = {}

def send(obj):
    proc.stdin.write(json.dumps(obj) + "\n")
    proc.stdin.flush()

def take(out, timeout=120):
    """Handle output until this turn's result line. False once the process has ended."""
    while True:
        try:
            line = lines.get(timeout=timeout)
        except queue.Empty:
            return True
        if line is None:
            return False
        out.write(line)
        ev = json.loads(line) if line.startswith("{") else {}
        req = ev.get("request", {})
        if ev.get("type") == "system" and ev.get("subtype") == "init":
            info.update(claude=ev.get("claude_code_version"), mode=ev.get("permissionMode"), key=ev.get("apiKeySource"))
        elif ev.get("type") == "control_request" and req.get("subtype") == "can_use_tool":
            R[cur]["questions"].append(dict({k: v for k, v in req.items() if k.startswith("decision")},
                                            command=req.get("input", {}).get("command")))
            send({"type": "control_response", "response": {"subtype": "success", "request_id": ev["request_id"],
                  "response": {"behavior": "deny", "message": "The owner said no."}}})
        elif ev.get("type") == "user":
            for b in blocks(ev["message"]):
                if b.get("type") == "tool_result":
                    c = b.get("content")
                    text = "".join(x.get("text", "") for x in c) if isinstance(c, list) else str(c)
                    R[cur]["result"] = {"error": bool(b.get("is_error")), "text": text.replace(D, "<run>")[:300]}
        elif ev.get("type") == "result":
            return True

with open(f"{D}/out.jsonl", "w") as out:
    for cur, r in enumerate(R):
        send({"type": "user", "message": {"role": "user", "content": "SCRIPT:" + json.dumps(
            {"command": r["command"], "description": f"Form {cur + 1}"})}})
        if not take(out):
            break
    else:
        proc.stdin.close()
        take(out, 30)
proc.wait()

def git(*a): return subprocess.run(["git", *a], capture_output=True, text=True).stdout.strip()
def ran(c):
    m = re.search(r"refs/heads/(t\d)", c)
    if m:
        return git("-C", O, "rev-parse", "-q", "--verify", f"refs/heads/{m.group(1)}") != ""
    if c == "git push":
        return git("-C", O, "rev-parse", "main") == git("-C", T, "rev-parse", "main")
    return os.path.exists(f"{T}/marker.txt") and c.split()[-1] in open(f"{T}/marker.txt").read().split()

hook = {}
if os.path.exists(f"{T}/.claude/hook.log"):
    for l in open(f"{T}/.claude/hook.log"):
        decision, _, c = l.rstrip("\n").partition("\t")
        hook[c] = decision
for n, r in enumerate(R, 1):
    r["ran"], r["hook"] = ran(r["command"]), hook.get(r["command"])
    res = r["result"] or {"error": False, "text": "(no result)"}
    if r["classifier"]:
        r["outcome"] = "not tested"
    elif r["questions"]:
        r["outcome"] = "RAN after no" if r["ran"] else "asked"
    elif r["ran"]:
        r["outcome"] = "ran"
    else:
        r["outcome"] = "refused" if res["error"] and not res["text"].startswith("Exit code") else "failed"
    reason = json.dumps({k: v for k, v in r["questions"][0].items() if k != "command"}) if r["questions"] else ""
    print(f"{n:2}. {r['outcome']:10} {r['label']:48} hook={r['hook']} {reason} | {res['text'][:110]!r}")
json.dump(dict(info, variant=args.variant, requested_mode=args.mode, trusted=not args.untrusted, forms=R),
          open(f"{D}/results.json", "w"), indent=1)
print(f"claude {info.get('claude')}, mode {info.get('mode')}, apiKeySource {info.get('key')}, "
      f"classifier requests {sum(r['classifier'] for r in R)}")
