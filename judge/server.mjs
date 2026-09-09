import {createServer} from 'node:http';
import {readFile, stat} from 'node:fs/promises';
import {extname, resolve, sep} from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';

const TYPES = new Map([
  ['.html', 'text/html; charset=utf-8'],
  ['.js', 'text/javascript; charset=utf-8'],
  ['.css', 'text/css; charset=utf-8'],
  ['.json', 'application/json; charset=utf-8'],
  ['.svg', 'image/svg+xml'],
  ['.png', 'image/png'],
  ['.webp', 'image/webp'],
]);

function headers(contentType) {
  return {
    'Content-Type': contentType,
    'Cache-Control': contentType.startsWith('text/html') || contentType.includes('json') ? 'no-store' : 'public, max-age=31536000, immutable',
    'X-Content-Type-Options': 'nosniff',
    'Referrer-Policy': 'no-referrer',
    'Content-Security-Policy': "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; font-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'",
  };
}

export function createStaticServer(distRoot) {
  const root = resolve(distRoot);
  return createServer(async (request, response) => {
    try {
      const url = new URL(request.url || '/', 'http://localhost');
      if (request.method !== 'GET' && request.method !== 'HEAD') {
        response.writeHead(405, {...headers('text/plain; charset=utf-8'), Allow: 'GET, HEAD'});
        return response.end('Method not allowed');
      }
      if (url.pathname === '/health') {
        response.writeHead(200, headers('text/plain; charset=utf-8'));
        return response.end(request.method === 'HEAD' ? undefined : 'ok');
      }

      const relative = url.pathname === '/' ? 'index.html' : url.pathname.slice(1);
      if (!(relative === 'index.html' || relative === 'evidence.json' || relative.startsWith('assets/'))) {
        response.writeHead(404, headers('text/plain; charset=utf-8'));
        return response.end('Not found');
      }
      const target = resolve(root, relative);
      if (target !== root && !target.startsWith(root + sep)) {
        response.writeHead(404, headers('text/plain; charset=utf-8'));
        return response.end('Not found');
      }
      const info = await stat(target);
      if (!info.isFile()) throw new Error('Not a file');
      const body = await readFile(target);
      response.writeHead(200, headers(TYPES.get(extname(target)) || 'application/octet-stream'));
      return response.end(request.method === 'HEAD' ? undefined : body);
    } catch {
      response.writeHead(404, headers('text/plain; charset=utf-8'));
      return response.end('Not found');
    }
  });
}

const thisFile = pathToFileURL(process.argv[1] || '').href;
if (import.meta.url === thisFile) {
  const port = Number(process.env.PORT || 3000);
  if (!Number.isInteger(port) || port < 1 || port > 65535) throw new Error('Invalid PORT');
  const dist = resolve(fileURLToPath(new URL('./dist/', import.meta.url)));
  const server = createStaticServer(dist);
  server.listen(port, '0.0.0.0', () => console.log(`KACHING Proof Explorer listening on ${port}`));
}
