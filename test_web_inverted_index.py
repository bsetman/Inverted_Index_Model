import unittest
from unittest.mock import patch, MagicMock
from web_inverted_index import (
    build_inverted_index, compress_index_gamma, decompress_index_gamma,
    elias_gamma_encode, elias_gamma_decode
)

class TestIndexCompression(unittest.TestCase):
    """Тестирование кодирования Elias Gamma и сжатия индекса"""

    def test_elias_gamma_encode(self):
        self.assertEqual(elias_gamma_encode(1), "1")
        self.assertEqual(elias_gamma_encode(2), "010")
        self.assertEqual(elias_gamma_encode(3), "011")
        self.assertEqual(elias_gamma_encode(4), "00100")

    def test_elias_gamma_decode(self):
        bits = elias_gamma_encode(3) + elias_gamma_encode(5)
        decoded = elias_gamma_decode(bits)
        self.assertEqual(decoded, [3, 5])

    def test_build_and_compress_index(self):
        docs = {
            1: "hello world hello",
            2: "test hello"
        }
        index = build_inverted_index(docs)
        self.assertEqual(index["hello"], [1, 2])
        self.assertEqual(index["world"], [1])
        self.assertEqual(index["test"], [2])

        compressed = compress_index_gamma(index)
        decompressed = decompress_index_gamma(compressed)
        self.assertEqual(decompressed, index)


class TestFastAPIEndpoints(unittest.TestCase):
    """Тестирование конечных точек FastAPI (имитация сети и базы данных)"""

    @patch("index_web_app.requests.get")
    @patch("index_web_app.SessionLocal")
    def test_index_pages_endpoint(self, mock_session_local, mock_requests_get):
        from fastapi.testclient import TestClient
        from index_web_app import app

        client = TestClient(app)

        # Имитация ответа от веб-страницы
        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value.text = "<html><body>Hello test hello</body></html>"

        # Имитация сессии базы данных
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session

        response = client.post("/index_pages", json={"urls": ["http://example.com"]})
        self.assertEqual(response.status_code, 200)
        self.assertIn("indexed_terms", response.json())

    @patch("index_web_app.SessionLocal")
    def test_search_endpoint(self, mock_session_local):
        from fastapi.testclient import TestClient
        from index_web_app import app, compress_index_gamma

        client = TestClient(app)

        # Имитация записи из базы данных
        index = {"hello": [1, 2, 4]}
        compressed = compress_index_gamma(index)
        bitstring = compressed["hello"]

        mock_record = MagicMock()
        mock_record.term = "hello"
        mock_record.postings = bitstring.encode("utf-8")

        mock_session = MagicMock()
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_record
        mock_session_local.return_value = mock_session

        response = client.get("/search", params={"term": "hello"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"term": "hello", "postings": [1, 2, 4]})


if __name__ == "__main__":
    unittest.main(verbosity=2)
