#!/usr/bin/env python3
"""ninepigs.py — call the Ninepigs public API, /api/v1, without an MCP client.

Usage:
  ninepigs.py GET /me
  ninepigs.py GET '/transactions?date_from=2026-09-01&limit=50'
  ninepigs.py POST /transactions '{"kind":"spend",...}'
  ninepigs.py POST /transactions -                  # JSON body on stdin
  ninepigs.py --dry-run POST /import-batches/41/approve '{...}'
  ninepigs.py --key approve-41-a POST /import-batches/41/approve '{...}'
  ninepigs.py --form POST /import-batches user_id=2 include_pending=1 'files[]=@chequing.csv'

Token: NINEPIGS_API_TOKEN in the environment, else the file ~/.config/ninepigs/token.
Base URL: NINEPIGS_API_URL (default https://api.ninepigs.com/api/v1).
Prints the JSON body; exit 0 on 2xx, 1 otherwise with the status and error on stderr.
Python 3.8+, standard library only. The token is sent only as the Authorization header
and never printed.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

VERSION = "0.1"
DEFAULT_URL = "https://api.ninepigs.com/api/v1"
TOKEN_FILE = Path.home() / ".config" / "ninepigs" / "token"


def die(message, code=1):
    print(f"ninepigs: {message}", file=sys.stderr)
    sys.exit(code)


def token():
    value = os.environ.get("NINEPIGS_API_TOKEN", "").strip()
    if value:
        return value
    if TOKEN_FILE.is_file():
        value = TOKEN_FILE.read_text().strip()
        if value:
            return value
    die(f"no token: set NINEPIGS_API_TOKEN or write it to {TOKEN_FILE}")


def multipart(fields):
    """Encode name=value pairs as multipart/form-data; a value of @path attaches that file."""
    boundary = uuid.uuid4().hex
    body = bytearray()
    for field in fields:
        if "=" not in field:
            die(f"form field must be name=value: {field}")
        name, value = field.split("=", 1)
        body += f"--{boundary}\r\n".encode()
        if value.startswith("@"):
            path = Path(value[1:])
            if not path.is_file():
                die(f"no such file: {path}")
            body += (
                f'Content-Disposition: form-data; name="{name}"; filename="{path.name}"\r\n'
                "Content-Type: text/csv\r\n\r\n"
            ).encode()
            body += path.read_bytes()
        else:
            body += f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode()
            body += value.encode()
        body += b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    return bytes(body), f"multipart/form-data; boundary={boundary}"


def main(argv):
    key = None
    dry_run = False
    form = False
    args = list(argv)
    while args and args[0].startswith("-") and args[0] != "-":
        option = args.pop(0)
        if option == "--key":
            if not args:
                die("--key needs a value")
            key = args.pop(0)
        elif option == "--dry-run":
            dry_run = True
        elif option == "--form":
            form = True
        elif option in ("-h", "--help"):
            print(__doc__)
            return 0
        else:
            die(f"unknown option {option}")
    if len(args) < 2:
        print(__doc__)
        return 2

    method, path, rest = args[0].upper(), args[1], args[2:]
    base = os.environ.get("NINEPIGS_API_URL", DEFAULT_URL).rstrip("/")
    url = base + "/" + path.lstrip("/")
    if dry_run:
        url += ("&" if "?" in url else "?") + "dry_run=true"

    # The API's edge blocks the default library User-Agent as a bot; name the client.
    headers = {
        "Authorization": f"Bearer {token()}",
        "Accept": "application/json",
        "User-Agent": f"ninepigs-skill/{VERSION}",
    }
    if key:
        headers["Idempotency-Key"] = key

    data = None
    if form:
        data, headers["Content-Type"] = multipart(rest)
    elif rest:
        raw = sys.stdin.read() if rest[0] == "-" else rest[0]
        try:
            json.loads(raw)
        except ValueError as error:
            die(f"body is not JSON: {error}")
        data = raw.encode()
        headers["Content-Type"] = "application/json"

    status, body = 0, b""
    for attempt in (1, 2):
        request = urllib.request.Request(url, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                status, body = response.status, response.read()
        except urllib.error.HTTPError as error:
            status, body = error.code, error.read()
            if status == 429 and attempt == 1:
                wait = int(error.headers.get("Retry-After") or 5)
                print(f"ninepigs: rate limited, retrying in {wait}s", file=sys.stderr)
                time.sleep(wait)
                continue
        except urllib.error.URLError as error:
            die(f"request failed: {error.reason}")
        break

    text = body.decode("utf-8", "replace")
    try:
        parsed = json.loads(text) if text else None
    except ValueError:
        parsed = None

    if 200 <= status < 300:
        if parsed is not None:
            print(json.dumps(parsed, indent=2, ensure_ascii=False))
        elif text:
            print(text)
        return 0

    if isinstance(parsed, dict) and isinstance(parsed.get("error"), dict):
        error = parsed["error"]
        print(f"HTTP {status} {error.get('code')}: {error.get('message')}", file=sys.stderr)
        if error.get("fields"):
            print(json.dumps(error["fields"], indent=2), file=sys.stderr)
        if error.get("hint"):
            print(f"hint: {error['hint']}", file=sys.stderr)
    else:
        print(f"HTTP {status}: {text[:500]}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
