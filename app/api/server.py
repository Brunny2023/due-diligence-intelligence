"""Small dependency-free demo server; live credentials remain server-side only."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from app.rag import RAGService

ROOT = Path(__file__).resolve().parents[2]
CASE = ROOT / "sample" / "input" / "northstar_acquisition.json"
SERVICE = RAGService(CASE)
HTML = (ROOT / "app" / "api" / "demo.html").read_text(encoding="utf-8")
FRONTEND_ORIGIN = "https://ddi.maindev20.workers.dev"


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: str, content_type: str) -> None:
        payload = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        origin = self.headers.get("Origin")
        if origin == FRONTEND_ORIGIN:
            self.send_header("Access-Control-Allow-Origin", FRONTEND_ORIGIN)
            self.send_header("Vary", "Origin")
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self) -> None:
        if self.headers.get("Origin") != FRONTEND_ORIGIN:
            self._send(403, json.dumps({"error": "origin not allowed"}), "application/json")
            return
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", FRONTEND_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Vary", "Origin")
        self.end_headers()

    def do_GET(self) -> None:
        if urlparse(self.path).path in {"/", "/demo"}:
            self._send(200, HTML, "text/html; charset=utf-8")
        elif self.path == "/health":
            self._send(200, json.dumps({"ok": True, "retrieval_mode": "live-pinecone" if SERVICE.live else "offline-demo", "embedding_model": SERVICE.embedder.model, "upserted_chunks": SERVICE.upserted_chunks, "pinecone_available": SERVICE.live}), "application/json")
        else:
            self._send(404, "Not found", "text/plain")

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/query":
            self._send(404, "Not found", "text/plain")
            return
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))))
            question = str(body.get("question", "")).strip()
            if not question:
                raise ValueError("question is required")
            top_k = max(1, min(int(body.get("top_k", 5)), 10))
            result = SERVICE.query(question, top_k)
            self._send(200, json.dumps(result.as_dict()), "application/json")
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            self._send(400, json.dumps({"error": str(exc)}), "application/json")


def main() -> None:
    port = 8000
    print(f"Due Diligence demo listening on http://0.0.0.0:{port}/demo", flush=True)
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
