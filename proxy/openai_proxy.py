"""Codex Responses API proxy for AI Town.

Converts OpenAI Chat Completions requests → Codex Responses API calls.
Only chat is proxied; embeddings go to Ollama directly.

Codex backend constraints:
- Only /codex/responses works (chat/completions and embeddings get 403)
- Only gpt-5.4 model supported
- stream=True and store=False required
"""

import json
import time
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import HTTPError

CODEX_AUTH_PATH = os.path.expanduser("~/.codex/auth.json")
CODEX_RESPONSES_URL = "https://chatgpt.com/backend-api/codex/responses"
PROXY_PORT = 18850

_token_cache = {"token": None, "expires_at": 0}


def get_access_token() -> str:
    now = time.time()
    if _token_cache["token"] and _token_cache["expires_at"] > now + 60:
        return _token_cache["token"]

    with open(CODEX_AUTH_PATH) as f:
        auth = json.load(f)

    tokens = auth.get("tokens", {})
    access_token = tokens.get("access_token", "")
    expires_at = tokens.get("expires_at", 0)

    if expires_at and expires_at > now + 60:
        _token_cache["token"] = access_token
        _token_cache["expires_at"] = expires_at
        return access_token

    refresh_token = tokens.get("refresh_token")
    if refresh_token:
        try:
            new_tokens = _refresh_token(refresh_token)
            access_token = new_tokens["access_token"]
            expires_at = new_tokens.get("expires_in", 3600) + now

            auth["tokens"]["access_token"] = access_token
            if "expires_at" in auth["tokens"]:
                auth["tokens"]["expires_at"] = int(expires_at)
            if "refresh_token" in new_tokens:
                auth["tokens"]["refresh_token"] = new_tokens["refresh_token"]
            auth["last_refresh"] = time.strftime("%Y-%m-%dT%H:%M:%S.000000Z", time.gmtime())

            with open(CODEX_AUTH_PATH, "w") as f:
                json.dump(auth, f, indent=2)

            _token_cache["token"] = access_token
            _token_cache["expires_at"] = expires_at
            print(f"[proxy] Token refreshed, expires in {new_tokens.get('expires_in', '?')}s")
            return access_token
        except Exception as e:
            print(f"[proxy] Refresh failed: {e}, using existing token")

    _token_cache["token"] = access_token
    _token_cache["expires_at"] = expires_at or now + 300
    return access_token


def _refresh_token(refresh_token: str) -> dict:
    data = json.dumps({
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": "app_BblB0OyR3aFOOGgJLKHIO",
    }).encode()

    req = Request(
        "https://auth.openai.com/oauth/token",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def _chat_to_responses_format(chat_body: dict) -> dict:
    """Convert OpenAI Chat Completions request to Responses API format."""
    messages = chat_body.get("messages", [])

    # Extract system message as instructions, rest as input
    instructions = ""
    input_messages = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            instructions += content + "\n"
        else:
            input_messages.append({
                "role": role,
                "content": [{"type": "input_text", "text": content}],
            })

    # If no user/assistant messages, create a dummy user message from instructions
    if not input_messages:
        input_messages.append({
            "role": "user",
            "content": [{"type": "input_text", "text": "Please respond in character based on your instructions."}],
        })

    return {
        "model": "gpt-5.4",
        "instructions": instructions.strip() or "You are a helpful assistant.",
        "store": False,
        "stream": True,
        "input": input_messages,
    }


def _parse_sse_response(raw: bytes) -> str:
    """Parse SSE stream from Responses API and extract text content."""
    text_parts = []
    for line in raw.decode("utf-8", errors="replace").split("\n"):
        if not line.startswith("data: "):
            continue
        data_str = line[6:].strip()
        if data_str == "[DONE]":
            break
        try:
            data = json.loads(data_str)
            if data.get("type") == "response.output_text.delta":
                text_parts.append(data.get("delta", ""))
        except json.JSONDecodeError:
            continue
    return "".join(text_parts)


def _make_chat_completion_response(content: str, model: str = "gpt-5.4") -> dict:
    """Build an OpenAI Chat Completions-style response."""
    return {
        "id": f"chatcmpl-proxy-{int(time.time())}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": content,
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }


class ProxyHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length) if content_length else b""

        try:
            body = json.loads(raw_body) if raw_body else {}
        except json.JSONDecodeError:
            body = {}

        if "/chat/completions" in self.path:
            self._handle_chat(body)
        else:
            # Unsupported endpoint
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Only chat/completions supported via proxy"}).encode())

    def _handle_chat(self, body: dict):
        token = get_access_token()
        responses_body = _chat_to_responses_format(body)

        req = Request(
            CODEX_RESPONSES_URL,
            data=json.dumps(responses_body).encode(),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
            method="POST",
        )

        try:
            with urlopen(req, timeout=60) as resp:
                raw = resp.read()

            content = _parse_sse_response(raw)
            result = _make_chat_completion_response(content)

            print(f"[proxy] chat OK: {content[:80]}...")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

        except HTTPError as e:
            error_body = e.read()
            print(f"[proxy] Error {e.code}: {error_body[:300]}")
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(error_body)

    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", PROXY_PORT), ProxyHandler)
    print(f"[proxy] Codex→Responses proxy on http://127.0.0.1:{PROXY_PORT}")
    print(f"[proxy] Chat → {CODEX_RESPONSES_URL} (GPT-5.4)")
    print(f"[proxy] Embeddings → NOT proxied (use Ollama)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[proxy] Shutting down")
        server.server_close()
