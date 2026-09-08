"""Bounded localhost bridge; the HTTP surface has no execution methods."""
from __future__ import annotations

import argparse
import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from .service import Service, arena

ROOT = Path(__file__).resolve().parents[1] / 'ui' / 'dist'


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Ambiguous JSON object')
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError('Non-standard JSON constant')


def create_server(port: int = 8890, live_enabled: bool = False) -> ThreadingHTTPServer:
    service = Service(live_enabled)

    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(15)

        def log_message(self, format, *args):
            # Request paths and payloads may contain attacker-controlled text.
            pass

        def respond(self, status, value, content_type='application/json'):
            body = json.dumps(value, allow_nan=False).encode() if content_type == 'application/json' else value
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; font-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
            self.end_headers()
            self.wfile.write(body)

        def guard(self):
            if (self.headers.get('Sec-Fetch-Site') == 'cross-site'
                    or not service.valid_request(self.headers.get('Host'), self.headers.get('Origin'), self.server.server_port)):
                self.respond(403, {'error': 'Use the local application origin'})
                return False
            return True

        def do_GET(self):
            if not self.guard():
                return
            path = urlsplit(self.path).path
            if path == '/api/state':
                return self.respond(200, service.state())
            # Serve only known build output. Never serve the repository or private evidence.
            relative = 'index.html' if path == '/' else path.lstrip('/')
            if path != '/' and not path.startswith(('/assets/', '/fonts/', '/wordmark')):
                return self.respond(404, {'error': 'Not found'})
            target = (ROOT / relative).resolve()
            if not target.is_relative_to(ROOT.resolve()) or not target.is_file():
                return self.respond(404, {'error': 'Build UI first' if path == '/' else 'Not found'})
            self.respond(200, target.read_bytes(), mimetypes.guess_type(target.name)[0] or 'application/octet-stream')

        def do_POST(self):
            if not self.guard():
                return
            if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
                return self.respond(415, {'error': 'JSON required'})
            try:
                length = int(self.headers.get('Content-Length', '0'))
            except ValueError:
                return self.respond(400, {'error': 'Invalid request length'})
            if not 0 < length <= 16384:
                return self.respond(413, {'error': 'Request exceeds limit'})
            try:
                payload = json.loads(self.rfile.read(length), object_pairs_hook=unique_object,
                                     parse_constant=reject_constant)
                if self.path == '/api/compile':
                    return self.respond(200, service.compile(payload))
                if self.path == '/api/verify':
                    return self.respond(200, {'verified': service.verify(payload), 'basis': 'server-retained-original-digest'})
                if self.path == '/api/arena':
                    return self.respond(200, arena())
                return self.respond(404, {'error': 'Not found'})
            except (ValueError, TypeError, KeyError, RecursionError):
                return self.respond(400, {'error': 'Invalid or unauthorized request'})
            except Exception:
                return self.respond(503, {'error': 'Observation or compilation unavailable; no authorization issued'})

    return ThreadingHTTPServer(('127.0.0.1', port), Handler)


def main():
    parser = argparse.ArgumentParser(description='KACHING! local command deck')
    parser.add_argument('--port', type=int, default=8890)
    parser.add_argument('--live', action='store_true', help='Enable explicit, read-only Binance observations')
    args = parser.parse_args()
    with create_server(args.port, args.live) as server:
        print(f'KACHING! http://127.0.0.1:{server.server_port} — live reads {"enabled" if args.live else "disabled"}', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
