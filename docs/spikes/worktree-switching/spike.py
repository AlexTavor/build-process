#!/usr/bin/env python3
"""Run one sequence (a to i) of the worktree-switching spike; see ../worktree-switching.md.

Usage: spike.py <sequence> <dir> [--claude PATH] [--approve] [--mode MODE] [--real]

Makes a fresh toy repo under <dir>/<sequence> with setup.sh and runs `claude -p` inside it, with
stream-json input and output. Each turn is a fixed list of tool calls. By default a local fake
Messages API plays the model: it answers each request with the next call on the list, so the run
needs no login and costs no tokens, and the tools themselves run in Claude Code. With --real, the
real model gets the same list as numbered instructions. With --approve, every permission prompt is
answered yes through the SDK control protocol, as the owner would answer it in the app. --mode sets
the permission mode (default acceptEdits). Prints each tool call and its result, then
`git worktree list` and the hook logs. Everything is saved in <dir>/<sequence>.
"""
import argparse, itertools, json, os, queue, shutil, subprocess, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

here = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("seq", choices=list("abcdefghi"))
ap.add_argument("dir")
ap.add_argument("--claude", default="claude")
ap.add_argument("--approve", action="store_true")
ap.add_argument("--mode", default="acceptEdits")
ap.add_argument("--real", action="store_true")
args = ap.parse_args()

D = os.path.join(os.path.realpath(args.dir), args.seq)
subprocess.run([f"{here}/setup.sh", D], check=True, stdout=subprocess.DEVNULL)
T, W1, W2 = f"{D}/toy", f"{D}/toy-worktrees/w1-a", f"{D}/toy-worktrees/w2-b"
if args.seq in ("d", "e", "i"):  # the WorktreeCreate hook
    os.makedirs(f"{T}/.claude")
    for f in ("settings.json", "worktree-create.sh"):
        shutil.copy(f"{here}/{f}", f"{T}/.claude/")
if args.seq == "h":  # a PreToolUse hook that approves EnterWorktree, in the repo and in both worktrees
    for d in (T, W1, W2):
        os.makedirs(f"{d}/.claude")
        shutil.copy(f"{here}/settings-allow.json", f"{d}/.claude/settings.json")
        shutil.copy(f"{here}/allow-enter.sh", f"{d}/.claude/")
if args.seq == "f":  # two worktrees under .claude/worktrees/, made with git
    for w in ("w6-c", "w7-d"):
        subprocess.run(["git", "-C", T, "worktree", "add", "-q", f".claude/worktrees/{w}", "-b", w, "main"], check=True)

def enter(**where): return ["EnterWorktree", where]
CHECK = ["Bash", {"command": "pwd; git branch --show-current; git worktree list", "description": "Show where the session is"}]
EXIT = ["ExitWorktree", {"action": "keep"}]
TURNS = {
    "a": [[enter(path=W1), CHECK, enter(path=W2), CHECK]],
    "b": [[enter(path=W1), CHECK, EXIT, CHECK, enter(path=W2), CHECK]],
    "c": [[enter(name="w3"), CHECK, enter(path=W2), CHECK]],
    "d": [[enter(name="w4"), CHECK, enter(path=W2), CHECK]],
    "e": [[CHECK]],  # the session starts with --worktree w5
    "f": [[enter(path=f"{T}/.claude/worktrees/w6-c"), CHECK, enter(path=f"{T}/.claude/worktrees/w7-d"), CHECK]],
    "g": [[enter(path=W1), CHECK], "/clear", [CHECK, enter(path=W2), CHECK, EXIT, CHECK, enter(path=W2), CHECK]],
    "h": [[enter(path=W1), CHECK, EXIT, CHECK, enter(path=W2), CHECK]],  # b, with the PreToolUse hook
    "i": [[enter(name="w1-a"), CHECK], "/clear", [CHECK, EXIT, CHECK, enter(name="w2-b"), CHECK]],  # the hook returns existing worktrees
}[args.seq]

def prompt(turn):
    if isinstance(turn, str):
        return turn
    if args.real:
        steps = " ".join(f"{i}. Call {n} with input {json.dumps(x)}." for i, (n, x) in enumerate(turn, 1))
        return ("This is a test of the worktree tools. Make exactly these tool calls, in order, one at a time. "
                "If a call fails, do not retry it or work around it; go on to the next one. " + steps)
    return "SCRIPT:" + json.dumps(turn)

ids = itertools.count(1)
def say(*parts): print(" ".join(map(str, parts)).replace(D, "<run>"), flush=True)
def blocks(m): return m["content"] if isinstance(m["content"], list) else [{"type": "text", "text": m["content"]}]

def next_block(body):
    """The next scripted call for this conversation, or a closing text."""
    names = {t.get("name") for t in body.get("tools", [])}
    if "Bash" not in names:  # a side request, such as a session title
        system = body.get("system", "")
        system = " ".join(b.get("text", "") for b in system) if isinstance(system, list) else system
        say(f"FAKE-API side request: {system[:150]!r}")
        return {"type": "text", "text": "ok"}
    if not os.path.exists(f"{D}/tools.json"):
        with open(f"{D}/tools.json", "w") as f:
            json.dump([t for t in body["tools"] if "Worktree" in t.get("name", "")] or sorted(names), f, indent=1)
    msgs = body["messages"]
    for i in range(len(msgs) - 1, -1, -1):
        marks = [b["text"].split("SCRIPT:", 1)[1] for b in blocks(msgs[i]) if b.get("type") == "text" and "SCRIPT:" in b["text"]]
        if msgs[i]["role"] == "user" and marks:
            calls = json.JSONDecoder().raw_decode(marks[-1])[0]
            done = sum(any(b.get("type") == "tool_use" and b["name"] != "ToolSearch" for b in blocks(m))
                       for m in msgs[i + 1:] if m["role"] == "assistant")
            say(f"FAKE-API request with {len(msgs)} messages; {done} of {len(calls)} calls done")
            if done == len(calls):
                break
            name, inp = calls[done]
            if name not in names and "ToolSearch" in names:  # a deferred tool must be loaded first
                name, inp = "ToolSearch", {"query": f"select:{name}", "max_results": 1}
            return {"type": "tool_use", "id": f"toolu_fake_{next(ids):04d}", "name": name, "input": inp}
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
        block = next_block(body)
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

def show(ev):
    t = ev.get("type")
    if t == "system" and ev.get("subtype") == "init":
        say(f"INIT cwd={ev.get('cwd')} version={ev.get('claude_code_version')} apiKeySource={ev.get('apiKeySource')} session={ev.get('session_id')}")
    elif t == "system":
        say("SYSTEM", json.dumps(ev).replace(D, "<run>")[:700])
    elif t == "assistant":
        for b in ev["message"]["content"]:
            if b.get("type") == "tool_use":
                say(f"CALL {b['name']} {json.dumps(b['input'])}")
    elif t == "user":
        for b in blocks(ev["message"]):
            c = b.get("content", b.get("text", ""))
            c = "".join(x.get("text", json.dumps(x)) for x in c) if isinstance(c, list) else str(c)
            say(("  -> ERROR: " if b.get("is_error") else "  -> ") + c.replace(D, "<run>").strip()[:900].replace("\n", "\n     "))
    elif t == "result":
        say(f"END {ev.get('subtype')} session={ev.get('session_id')} denials={json.dumps(ev.get('permission_denials'))}")

server = ThreadingHTTPServer(("127.0.0.1", 0), FakeAPI)
threading.Thread(target=server.serve_forever, daemon=True).start()
env = {k: os.environ[k] for k in ("HOME", "PATH", "USER", "TMPDIR", "LANG") if k in os.environ}
env["DISABLE_AUTOUPDATER"] = "1"
if not args.real:
    env.update(ANTHROPIC_BASE_URL=f"http://127.0.0.1:{server.server_port}", ANTHROPIC_API_KEY="fake-key-for-the-local-fake-api")
cmd = [args.claude, "-p", "--input-format", "stream-json", "--output-format", "stream-json", "--verbose",
       "--include-hook-events", "--setting-sources", "project,local", "--permission-mode", args.mode, "--model", "sonnet",
       "--allowedTools", "ToolSearch,EnterWorktree,ExitWorktree,Bash(pwd),Bash(git branch:*),Bash(git worktree list:*)"]
if args.approve:
    cmd += ["--permission-prompt-tool", "stdio"]
if args.seq == "e":
    cmd += ["--worktree", "w5"]
say("$", subprocess.run([args.claude, "--version"], capture_output=True, text=True).stdout.strip())
proc = subprocess.Popen(cmd, cwd=T, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
lines = queue.Queue()
threading.Thread(target=lambda: [lines.put(l) for l in proc.stdout] + [lines.put(None)], daemon=True).start()
with open(f"{D}/out.jsonl", "w") as out:
    def take(timeout):
        """Print output until this turn's result line; False once the process has ended."""
        while True:
            try:
                line = lines.get(timeout=timeout)
            except queue.Empty:
                return True  # a slash command may end without a result line
            if line is None:
                return False
            out.write(line)
            ev = json.loads(line) if line.startswith("{") else {}
            show(ev)
            req = ev.get("request", {})
            if ev.get("type") == "control_request" and req.get("subtype") == "can_use_tool":
                say(f"PROMPT {req.get('tool_name')} {json.dumps(req.get('input'))} reason={json.dumps(req.get('decision_reason'))} -> answered yes")
                answer = {"behavior": "allow", "updatedInput": req.get("input")}
                proc.stdin.write(json.dumps({"type": "control_response", "response": {"subtype": "success", "request_id": ev["request_id"], "response": answer}}) + "\n")
                proc.stdin.flush()
            if ev.get("type") == "result":
                return True
    for turn in TURNS:
        say(f"=== turn: {prompt(turn).replace(D, '<run>')[:300]}")
        proc.stdin.write(json.dumps({"type": "user", "message": {"role": "user", "content": prompt(turn)}}) + "\n")
        proc.stdin.flush()
        if not take(20 if isinstance(turn, str) else 300):
            break
    proc.stdin.close()
    take(60)
proc.wait()
say("=== git worktree list")
say(subprocess.run(["git", "-C", T, "worktree", "list"], capture_output=True, text=True).stdout.strip())
for log in ("hook.log", "pretooluse.log"):
    say(f"=== {log}")
    say(open(f"{D}/{log}").read().strip() if os.path.exists(f"{D}/{log}") else f"(no {log})")
