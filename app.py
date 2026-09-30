"""Web chat (no extra libraries needed):  python app.py  ->  http://localhost:8000"""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from bot import DomainBot

bot = DomainBot()
PAGE = (Path(__file__).parent / "web" / "index.html").read_text(encoding="utf-8")
PAGE = PAGE.replace("{{BOT_NAME}}", bot.config["bot_name"]).replace(
    "{{DOMAIN}}", bot.config["domain_name"]
).replace("{{GREETING}}", json.dumps(bot.config["greeting"])).replace("{{CHIPS}}", json.dumps(bot.config["suggestions"]))


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, PAGE, "text/html; charset=utf-8")
        else:
            self._send(404, "Not found", "text/plain")

    def do_POST(self):
        if self.path != "/api/ask":
            return self._send(404, "Not found", "text/plain")
        length = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            payload = {}
        result = bot.ask(payload.get("message", ""))
        self._send(200, json.dumps(result), "application/json")

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    port = bot.config.get("port", 8000)
    print(f"{bot.config['bot_name']} running at http://localhost:{port}  (Ctrl+C to stop)")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
