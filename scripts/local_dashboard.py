"""Thin local launcher and SSH-to-native-snapshot adapter; no alternate parser/UI."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "skills/codex-usage-dashboard/scripts/codex_usage_dashboard.py"
os.environ["COUSASH_CONFIG_DIR"] = str(ROOT / "local-data")
sys.path.insert(0, str(MODULE.parent))
import codex_usage_dashboard as dashboard


def sync_ssh(target):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+@[A-Za-z0-9.-]+", target):
        raise ValueError("Invalid SSH target")
    # Execute only our reviewed parser over stdin. No installation or source-log writes.
    encoded = base64.b64encode(MODULE.read_bytes()).decode("ascii")
    code = "linux-" + hashlib.sha256(target.encode()).hexdigest()[:8]
    remote = f'''import base64, types, sys
m=types.ModuleType("codex_usage_dashboard")
m.__file__="/tmp/codex_usage_dashboard.py"
sys.modules[m.__name__]=m
exec(compile(base64.b64decode({encoded!r}),m.__file__,"exec"),m.__dict__)
m.current_device_short_code=lambda: {code!r}
a=m.CodexUsageAnalyzer(m.Path.home()/".codex",parallel_workers=0)
try:
 p=a.export_snapshot_payload()
 for detail in p["snapshot"]["details_by_uid"].values():
  detail.pop("first_user_prompt",None)
  detail.pop("last_agent_preview",None)
 print(m.json.dumps(p,ensure_ascii=True))
finally: a.close()
'''
    result = subprocess.run(["ssh", "-T", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes", "-o", "ConnectTimeout=10", target, "python3", "-"], input=remote, text=True, encoding="utf-8", capture_output=True, timeout=300, creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
    if result.returncode:
        raise RuntimeError("SSH snapshot failed; verify the connection and Python 3 on the remote host.")
    payload = json.loads(result.stdout)
    imported = dashboard.RemoteSnapshotStore().import_snapshot(payload, label="Ubuntu")
    if not imported.get("ok"):
        raise RuntimeError("Snapshot import failed")
    print(f"Ubuntu: {len(payload['snapshot']['sessions'])} sessions imported into the native snapshot store.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sync-ssh", metavar="USER@HOST")
    args = parser.parse_args()
    if args.sync_ssh:
        sync_ssh(args.sync_ssh)
        return
    analyzer = dashboard.CodexUsageAnalyzer(dashboard.default_codex_sources(), remote_store=dashboard.RemoteSnapshotStore(), persistent_cache=dashboard.PersistentParseCache(), parallel_workers=0)
    # Fail if occupied; never terminate another process automatically.
    server = dashboard.FixedPortHTTPServer(("127.0.0.1", 8765), dashboard.make_handler(analyzer))
    print("http://127.0.0.1:8765/", flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()
        analyzer.close()


if __name__ == "__main__":
    main()
