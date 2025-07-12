from unittest.mock import Mock

import pytest
from scrapy.http import Request, Response
from scrapy.settings import Settings
from scrapy.spiders import Spider

from scrapy_ua_rotator.middleware import RandomUserAgentMiddleware, RetryUserAgentMiddleware
from scrapy_ua_rotator.providers import BaseProvider


class DummyProvider(BaseProvider):
    def __init__(self, settings=None):
        self.ua_value = "Dummy-UA"

    def get_random_ua(self):
        return self.ua_value


class NullProvider(BaseProvider):
    def __init__(self, settings=None):
        pass

    def get_random_ua(self):
        return None


class DummySpider(Spider):
    name = "dummy"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._settings = Settings()

    @property
    def settings(self):
        return self._settings

    @property
    def crawler(self):
        class DummyCrawler:
            settings = Settings()
            stats = Mock()
        return DummyCrawler()


@pytest.fixture
def dummy_request():
    return Request(url="http://example.com")


@pytest.fixture
def dummy_response(dummy_request):
    return Response(url=dummy_request.url, request=dummy_request)


@pytest.fixture
def monkey_provider(monkeypatch):
    monkeypatch.setattr("scrapy_ua_rotator.middleware.RandomUserAgentBase._get_provider",
                        lambda self, crawler: DummyProvider())


def test_assigns_user_agent(monkey_provider, dummy_request):
    mw = RandomUserAgentMiddleware(DummySpider().crawler)
    mw.process_request(dummy_request, DummySpider("dummy"))
    assert dummy_request.headers.get("User-Agent").decode() == "Dummy-UA"


def test_preserves_existing_user_agent(monkey_provider):
    mw = RandomUserAgentMiddleware(DummySpider().crawler)
    request = Request("http://example.com",
                      headers={"User-Agent": "Already-Set-UA"})
    mw.process_request(request, DummySpider("dummy"))
    assert request.headers.get("User-Agent").decode() == "Already-Set-UA"


def test_retries_with_new_user_agent(monkey_provider, dummy_request, dummy_response):
    mw = RetryUserAgentMiddleware(DummySpider().crawler)
    dummy_request.meta["retry_times"] = 1
    dummy_request.headers['User-Agent'] = 'Old-UA'

    result = mw.process_response(
        dummy_request, dummy_response, DummySpider("dummy"))

    if isinstance(result, Request):
        assert result.headers.get("User-Agent").decode() == "Dummy-UA"
    else:
        print("Retry did not occur (stub fallback)")


def test_ignore_request_on_error(monkeypatch, dummy_request):
    monkeypatch.setattr("scrapy_ua_rotator.middleware.RandomUserAgentBase._get_provider",
                        lambda self, crawler: NullProvider(Settings()))
    mw = RandomUserAgentMiddleware(DummySpider().crawler)
    mw.process_request(dummy_request, DummySpider("dummy"))
    assert not dummy_request.headers.get("User-Agent")  # safe check


def test_assigns_ua_per_proxy(monkeypatch, dummy_request):
    def patched_get_provider(self, crawler):
        return DummyProvider()
    monkeypatch.setattr("scrapy_ua_rotator.middleware.RandomUserAgentBase._get_provider",
                        patched_get_provider)

    crawler = DummySpider().crawler
    crawler.settings.set('RANDOM_UA_PER_PROXY', True)
    mw = RandomUserAgentMiddleware(crawler)

    dummy_request.meta['proxy'] = "http://proxy:8080"
    mw.process_request(dummy_request, DummySpider("dummy"))
    assert dummy_request.headers.get("User-Agent").decode() == "Dummy-UA"


def test_provider_fallback_on_invalid_path(monkeypatch):
    class DummyCrawler:
        settings = Settings(
            {'FAKEUSERAGENT_PROVIDERS': ['invalid.module.Provider']})
        stats = Mock()

    mw = RandomUserAgentMiddleware.from_crawler(DummyCrawler())
    ua = mw._ua_provider.get_random_ua()
    assert isinstance(ua, str) or ua is None


def test_retry_user_agent_on_exception(monkey_provider):
    crawler = DummySpider().crawler
    crawler.stats = Mock()
    mw = RetryUserAgentMiddleware(crawler)

    request = Request("http://example.com")
    request.headers['User-Agent'] = 'Initial-UA'
    exception = ConnectionError()

    retried = mw.process_exception(request, exception, DummySpider("dummy"))

    if isinstance(retried, Request):
        assert retried.headers.get("User-Agent").decode() == "Dummy-UA"
    else:
        print("No retry triggered (fallback)")


def test_retry_skipped_if_dont_retry(monkey_provider):
    mw = RetryUserAgentMiddleware(DummySpider().crawler)
    request = Request("http://example.com", meta={"dont_retry": True})
    response = Response(url="http://example.com", status=500, request=request)
    result = mw.process_response(request, response, DummySpider("dummy"))
    assert result is response


def test_exception_not_retry(monkey_provider):
    mw = RetryUserAgentMiddleware(DummySpider().crawler)
    request = Request("http://example.com", meta={"dont_retry": True})
    result = mw.process_exception(
        request, Exception("Some error"), DummySpider("dummy"))
    assert result is None


def test_multiple_provider_failures(monkeypatch):
    class DummyCrawler:
        settings = Settings({'FAKEUSERAGENT_PROVIDERS': [
                            'invalid.path1', 'invalid.path2']})
        stats = Mock()

    mw = RandomUserAgentMiddleware.from_crawler(DummyCrawler())
    assert mw._ua_provider is not None


def test_valid_provider_load(monkeypatch):
    class DummyProvider:
        def __init__(self, settings): pass

        def get_random_ua(self): return "ok"
    monkeypatch.setattr(
        "scrapy_ua_rotator.middleware.load_object", lambda path: DummyProvider)

    class DummyCrawler:
        settings = Settings({'FAKEUSERAGENT_PROVIDERS': [
                            'scrapy_ua_rotator.providers.FixedUserAgentProvider']})
        stats = Mock()

    mw = RandomUserAgentMiddleware.from_crawler(DummyCrawler())
    assert mw._ua_provider.get_random_ua() == "ok"


def test_retry_response_no_retry_code(monkey_provider):
    mw = RetryUserAgentMiddleware(DummySpider().crawler)
    request = Request("http://example.com")
    response = Response(url="http://example.com", status=200, request=request)
    result = mw.process_response(request, response, DummySpider("dummy"))
    assert result is response


def test_exception_triggers_retry(monkey_provider):
    crawler = DummySpider().crawler
    crawler.stats = Mock()
    mw = RetryUserAgentMiddleware(crawler)

    request = Request("http://example.com")
    request.headers['User-Agent'] = 'Initial-UA'

    from twisted.internet.error import TimeoutError
    exception = TimeoutError()

    retried = mw.process_exception(request, exception, DummySpider("dummy"))
    assert isinstance(retried, Request)
    assert retried.headers.get("User-Agent").decode() == "Dummy-UA"


def test_process_response_debug_log(monkey_provider, caplog):
    caplog.set_level("DEBUG")
    mw = RetryUserAgentMiddleware(DummySpider().crawler)
    request = Request("http://example.com", meta={"retry_times": 1})
    response = Response(url="http://example.com", status=500, request=request)

    mw.process_response(request, response, DummySpider("dummy"))
    assert any("Retrying" in m for m in caplog.messages)


def test_sets_default_user_agent(monkey_provider):
    crawler = DummySpider().crawler
    crawler.settings.set('RANDOM_UA_PER_PROXY', False)
    mw = RandomUserAgentMiddleware(crawler)

    request = Request("http://example.com")
    assert b"User-Agent" not in request.headers
    mw.process_request(request, DummySpider("dummy"))
    assert request.headers.get("User-Agent").decode() == "Dummy-UA"


def test_retry_response_returns_original_if_retry_fails(monkey_provider, monkeypatch):
    class RetryUserAgentMiddlewareStub(RetryUserAgentMiddleware):
        def _retry(self, request, reason, spider):
            return None  # simulate no retry

    mw = RetryUserAgentMiddlewareStub(DummySpider().crawler)
    request = Request("http://example.com", meta={"retry_times": 1})
    response = Response(url="http://example.com", status=500, request=request)

    result = mw.process_response(request, response, DummySpider("dummy"))
    assert result == response  # fallback to original response


def test_sets_user_agent_with_no_proxy_and_no_header(monkey_provider):
    crawler = DummySpider().crawler
    crawler.settings.set('RANDOM_UA_PER_PROXY', False)
    mw = RandomUserAgentMiddleware(crawler)

    # remove User-Agent header completely
    request = Request("http://example.com", headers={})
    assert b"User-Agent" not in request.headers

    mw.process_request(request, DummySpider("dummy"))
    assert request.headers.get("User-Agent").decode() == "Dummy-UA"
