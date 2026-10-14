"""Loopback-only viewer. Read-only unless started with --review.

Defences: binds 127.0.0.1 only; rejects any Host header but 127.0.0.1:port / localhost:port (blocks
DNS rebinding); strict CSP, nosniff, no-store, no referrer; the page never uses innerHTML for memory
content. In review mode the only write route is POST /api/review, which additionally requires
Content-Type application/json, a same-origin Origin header and a per-process random token that a
cross-origin page cannot read (same-origin policy) -- so a malicious website cannot approve memories
through the user's browser.
"""
import json
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from .errors import InvalidInput, MemoryMergeError
from .schema import INDEXED_STATUSES
from .store import TRANSITIONS, scope

STATIC = Path(__file__).parent / 'static'
FILES = {'/': ('index.html', 'text/html'), '/app.js': ('app.js', 'text/javascript'), '/style.css': ('style.css', 'text/css')}
CSP = "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"


def make_server(store, port=8765, review=False):
    token = secrets.token_urlsafe(24)

    class Handler(BaseHTTPRequestHandler):
        def _allowed_hosts(self):
            p = self.server.server_port
            return {f'127.0.0.1:{p}', f'localhost:{p}'}

        def _send(self, code, body, mime):
            self.send_response(code)
            self.send_header('Content-Type', mime + '; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Content-Security-Policy', CSP)
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.end_headers(); self.wfile.write(body)

        def _json(self, obj, code=200):
            self._send(code, json.dumps(obj, ensure_ascii=False).encode(), 'application/json')

        def do_GET(self):
            if self.headers.get('Host') not in self._allowed_hosts():
                self.send_error(403); return
            parsed = urlsplit(self.path)
            q = {k: v[0] for k, v in parse_qs(parsed.query).items()}
            try:
                if parsed.path in FILES:
                    name, mime = FILES[parsed.path]
                    self._send(200, (STATIC / name).read_bytes(), mime); return
                project = scope(q.get('project', 'default'))
                if parsed.path == '/api/graph':
                    limit = int(q.get('limit', 1000))
                    out = store.graph(project, limit=limit, category=q.get('category') or None, tag=q.get('tag') or None,
                                      include_user=q.get('include_user') == '1')
                elif parsed.path == '/api/search':
                    out = {'results': store.recall(project, q.get('q', ''), limit=min(int(q.get('limit', 20)), 50))}
                elif parsed.path == '/api/timeline':
                    out = store.page(project, status='approved', limit=min(int(q.get('limit', 100)), 500), cursor=q.get('cursor') or None)
                elif parsed.path == '/api/memory':
                    m = store.get(project, q.get('id', ''))
                    visible = INDEXED_STATUSES + (('pending',) if review else ())
                    if m['status'] not in visible: self.send_error(404); return  # never forgotten/rejected text
                    out = dict(m, edges=store.edges_of(project, [m['id']]), support=store.support(m['id']))
                elif parsed.path == '/api/session':  # same-origin pages only can read this
                    out = {'review': review, 'token': token if review else None}
                elif parsed.path == '/api/queue' and review:
                    out = store.page(project, status='pending', limit=200)
                else:
                    self.send_error(404); return
            except (MemoryMergeError, ValueError) as e:
                self._json({'error': {'code': getattr(e, 'code', 'invalid_input'), 'message': str(e)[:200]}}, 400 if not isinstance(e, KeyError) else 404); return
            self._json(out)

        def do_POST(self):
            if not review: self.send_error(501); return
            p = self.server.server_port
            if (self.headers.get('Host') not in self._allowed_hosts()
                    or self.headers.get('Origin') not in {f'http://127.0.0.1:{p}', f'http://localhost:{p}'}
                    or not secrets.compare_digest(self.headers.get('X-MM-Token', ''), token)
                    or (self.headers.get('Content-Type') or '').split(';')[0].strip() != 'application/json'):
                self.send_error(403); return
            if urlsplit(self.path).path != '/api/review': self.send_error(404); return
            try:
                n = int(self.headers.get('Content-Length') or 0)
                if not 0 < n <= 4096: raise InvalidInput('bad request body')
                body = json.loads(self.rfile.read(n))
                if not isinstance(body, dict) or body.get('action') not in TRANSITIONS: raise InvalidInput('bad action')
                r = store.review(body.get('project'), str(body.get('id')), body['action'], actor='web-review')
                store.flush()
            except (MemoryMergeError, ValueError) as e:
                self._json({'error': {'code': getattr(e, 'code', 'invalid_input'), 'message': str(e)[:200]}}, 400); return
            self._json({'memory': r})

        def log_message(self, *args): pass

    return ThreadingHTTPServer(('127.0.0.1', port), Handler)
