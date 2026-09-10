import http.client
import tempfile
import threading
import unittest
from pathlib import Path

from test_codex_usage_dashboard import dashboard


class LocalForkTests(unittest.TestCase):
    def test_large_windows_file_ids_round_trip_without_precision_loss(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = dashboard.PersistentParseCache(Path(directory) / "cache.sqlite3")
            try:
                entry = dashboard.FileParseCacheEntry(123, 8, 2**64 - 1, 2**127 + 11,
                                                       {}, {}, True, "prefix", "tail")
                cache.put("large-id", entry)
                self.assertEqual(cache.get("large-id"), entry)
            finally:
                cache.close()

    def test_browser_requests_cannot_cross_the_local_origin_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            analyzer = dashboard.CodexUsageAnalyzer(Path(directory), parallel_workers=0)
            server = dashboard.FixedPortHTTPServer(("127.0.0.1", 0), dashboard.make_handler(analyzer))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                cases = [
                    ("GET", {}, 200),
                    ("GET", {"Host": "attacker.example"}, 403),
                    ("GET", {"Origin": "https://attacker.example"}, 403),
                    ("GET", {"Sec-Fetch-Site": "cross-site"}, 403),
                    ("POST", {"Content-Type": "text/plain"}, 415),
                ]
                for method, headers, expected in cases:
                    with self.subTest(method=method, headers=headers):
                        connection = http.client.HTTPConnection("127.0.0.1", server.server_port)
                        try:
                            connection.request(method, "/api/health", headers=headers)
                            response = connection.getresponse()
                            self.assertEqual(response.status, expected)
                            self.assertEqual(response.getheader("X-Frame-Options"), "DENY")
                            response.read()
                        finally:
                            connection.close()
            finally:
                server.shutdown()
                thread.join()
                server.server_close()
                analyzer.close()
