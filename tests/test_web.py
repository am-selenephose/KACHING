import http.client
import importlib.util
import json
import threading
import tempfile
import unittest
from pathlib import Path

HAS_WEB = importlib.util.find_spec('tradegate.web') is not None
if HAS_WEB:
    from tradegate.web import create_server


class WebTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(HAS_WEB, 'Loopback web bridge is not implemented')
        self.tmp = tempfile.TemporaryDirectory()
        self.server = create_server(port=0, issuer_key_path=Path(self.tmp.name) / 'issuer.pem')
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.server.server_port

    def tearDown(self):
        if hasattr(self, 'server'):
            self.server.shutdown()
            self.server.server_close()
            self.thread.join()
        if hasattr(self, 'tmp'):
            self.tmp.cleanup()

    def request(self, method, path, payload=None, headers=None):
        conn = http.client.HTTPConnection('127.0.0.1', self.port, timeout=5)
        try:
            conn.request(method, path, body=json.dumps(payload) if payload is not None else None,
                         headers={'Content-Type': 'application/json', **(headers or {})})
            r = conn.getresponse()
            return r.status, dict(r.headers), r.read()
        finally:
            conn.close()

    def test_state_is_sanitized_and_no_store(self):
        status, headers, body = self.request('GET', '/api/state')
        self.assertEqual(status, 200)
        self.assertEqual(headers['Cache-Control'], 'no-store')
        self.assertIsNone(json.loads(body)['receipt'])

    def test_compile_and_tamper_routes(self):
        status, _, body = self.request('POST', '/api/compile', {'scenario': 'block'})
        self.assertEqual(status, 200)
        receipt = json.loads(body)['receipt']
        receipt['verdict'] = 'ALLOW'
        _, _, result = self.request('POST', '/api/verify', receipt)
        self.assertFalse(json.loads(result)['verified'])

    def test_authzen_evaluation_and_enforcement_routes(self):
        payload = {
            'subject': {'type': 'agent', 'id': 'web-agent'},
            'action': {'name': 'BUY'},
            'resource': {'type': 'binance-spot', 'id': 'BNBUSDT'},
            'context': {'quote_notional': '10', 'audience': 'binance.spot.newOrder',
                        'mode': 'fixture', 'scenario': 'allow'},
        }
        status, _, body = self.request('POST', '/access/v1/evaluation', payload)
        self.assertEqual(status, 200)
        evaluation = json.loads(body)
        self.assertTrue(evaluation['decision'])
        lease = evaluation['context']['authorization_lease']
        enforce = {'lease': lease, 'origin': 'agent', 'action': 'BUY',
                   'symbol': 'BNBUSDT', 'quote': '10',
                   'audience': 'binance.spot.newOrder'}
        status, _, body = self.request('POST', '/api/enforce', enforce)
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), {'valid': True, 'reason': 'VALID'})
        enforce['quote'] = '10.01'
        _, _, body = self.request('POST', '/api/enforce', enforce)
        self.assertEqual(json.loads(body)['reason'], 'ACTION_MISMATCH')

    def test_cross_origin_refused(self):
        status, _, _ = self.request('POST', '/api/compile', {}, {'Origin': 'https://evil.test'})
        self.assertEqual(status, 403)

    def test_dns_rebinding_host_refused(self):
        status, _, _ = self.request('GET', '/api/state', headers={'Host': 'evil.test'})
        self.assertEqual(status, 403)

    def test_no_private_files_and_no_execution_route(self):
        for path in ('/../pyproject.toml', '/live-proof.json', '/api/order-test', '/api/execute'):
            with self.subTest(path=path):
                self.assertEqual(self.request('GET', path)[0], 404)

    def test_payload_limit(self):
        self.assertEqual(self.request('POST', '/api/compile', {'message': 'x'*20000})[0], 413)

    def test_non_json_refused(self):
        self.assertEqual(self.request('POST', '/api/compile', {}, {'Content-Type': 'text/plain'})[0], 415)

    def test_invalid_intent_is_generic(self):
        status, _, body = self.request('POST', '/api/compile', {'quote': 'NaN'})
        self.assertEqual(status, 400)
        self.assertNotIn(b'Traceback', body)

    def test_cross_site_fetch_without_origin_is_refused(self):
        status, _, _ = self.request('GET', '/api/state', headers={'Sec-Fetch-Site': 'cross-site'})
        self.assertEqual(status, 403)

    def test_ambiguous_json_is_rejected_before_compilation(self):
        for body in ('{"quote":"10","quote":"100"}', '{"message":NaN}'):
            with self.subTest(body=body):
                conn = http.client.HTTPConnection('127.0.0.1', self.port, timeout=5)
                try:
                    conn.request('POST', '/api/compile', body=body,
                                 headers={'Content-Type': 'application/json'})
                    response = conn.getresponse()
                    self.assertEqual(response.status, 400)
                    response.read()
                finally:
                    conn.close()
        self.assertIsNone(json.loads(self.request('GET', '/api/state')[2])['receipt'])
