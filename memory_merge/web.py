"""Loopback-only viewer. No HTTP mutations; CLI/MCP own writes and review."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from .store import scope
STATIC=Path(__file__).parent/'static'

def make_server(store,port=8765):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.headers.get('Host') not in {f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}'}:
                self.send_error(403); return
            parsed=urlsplit(self.path)
            try:
                if parsed.path=='/api/graph':
                    project=scope(parse_qs(parsed.query).get('project',['default'])[0])
                    body=json.dumps(store.graph(project),ensure_ascii=False).encode(); mime='application/json'
                elif parsed.path in {'/','/app.js','/style.css'}:
                    name={'/':'index.html','/app.js':'app.js','/style.css':'style.css'}[parsed.path]
                    body=(STATIC/name).read_bytes(); mime={'/':'text/html','/app.js':'text/javascript','/style.css':'text/css'}[parsed.path]
                else: self.send_error(404); return
            except ValueError:
                self.send_error(400); return
            self.send_response(200)
            self.send_header('Content-Type',mime+'; charset=utf-8')
            self.send_header('Content-Length',str(len(body)))
            self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; frame-ancestors 'none'")
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Cache-Control','no-store')
            self.send_header('Referrer-Policy','no-referrer')
            self.end_headers(); self.wfile.write(body)
        def log_message(self,*args): pass
    return ThreadingHTTPServer(('127.0.0.1',port),Handler)
