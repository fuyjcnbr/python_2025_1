
from python_2025_1.misc.worker import Worker


def test_url_of_request():
    request = "GET /api/v2/banner/25019354 HTTP/1.1"
    assert(Worker.url_of_request(request) == "/api/v2/banner/25019354")

    request = "HTTP/1.1"
    assert(Worker.url_of_request(request) is None)
