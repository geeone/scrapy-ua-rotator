import logging
from typing import Optional, Any

from scrapy.crawler import Crawler
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.http import Request, Response
from scrapy.spiders import Spider
from scrapy.utils.misc import load_object
from scrapy.utils.response import response_status_message


logger = logging.getLogger(__name__)

FIXED_PROVIDER_PATH = 'scrapy_ua_rotator.providers.FixedUserAgentProvider'
FAKE_USERAGENT_PROVIDER_PATH = 'scrapy_ua_rotator.providers.FakeUserAgentProvider'


class RandomUserAgentBase:
    """Base class that provides User-Agent selection logic via configured providers."""

    def __init__(self, crawler: Crawler):
        self._ua_provider: Any = self._get_provider(crawler)
        self._per_proxy: bool = crawler.settings.get(
            'RANDOM_UA_PER_PROXY', False)
        self._proxy2ua: dict[str, str] = {}

    def _get_provider(self, crawler: Crawler) -> Any:
        """Load the first available provider from settings or fall back to FixedUserAgentProvider."""
        self.providers_paths = crawler.settings.get(
            'FAKEUSERAGENT_PROVIDERS', None)
        if not self.providers_paths:
            self.providers_paths = [FAKE_USERAGENT_PROVIDER_PATH]

        for provider_path in self.providers_paths:
            try:
                provider = load_object(provider_path)(crawler.settings)
                logger.debug(f"Loaded User-Agent provider: {provider_path}")
                return provider
            except Exception as e:
                logger.warning(f"Failed loading provider {provider_path}: {e}")

        logger.info('Falling back to FixedUserAgentProvider')
        return load_object(FIXED_PROVIDER_PATH)(crawler.settings)


class RandomUserAgentMiddleware(RandomUserAgentBase):
    """Downloader middleware that injects User-Agent header into outgoing requests."""

    def __init__(self, crawler: Crawler):
        super().__init__(crawler)

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> 'RandomUserAgentMiddleware':
        return cls(crawler)

    def process_request(self, request: Request, spider: Spider) -> None:
        if self._per_proxy:
            proxy = request.meta.get('proxy')
            if proxy not in self._proxy2ua:
                self._proxy2ua[proxy] = self._ua_provider.get_random_ua()
                logger.debug(
                    f"Assigned UA {self._proxy2ua[proxy]} to proxy {proxy}")
            request.headers.setdefault('User-Agent', self._proxy2ua[proxy])
        else:
            request.headers.setdefault(
                'User-Agent', self._ua_provider.get_random_ua())


class RetryUserAgentMiddleware(RetryMiddleware, RandomUserAgentBase):
    """Extends retry logic to rotate User-Agent on retry attempts."""

    def __init__(self, crawler: Crawler):
        RetryMiddleware.__init__(self, crawler.settings)
        RandomUserAgentBase.__init__(self, crawler)

        # Scrapy 2.10+ dropped EXCEPTIONS_TO_RETRY in favor of instance attr
        if hasattr(self, 'exceptions_to_retry'):
            self.EXCEPTIONS_TO_RETRY = self.exceptions_to_retry

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> 'RetryUserAgentMiddleware':
        return cls(crawler)

    def process_response(self, request: Request, response: Response, spider: Spider) -> Response:
        if request.meta.get('dont_retry', False):
            return response
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            request.headers['User-Agent'] = self._ua_provider.get_random_ua()
            return self._retry(request, reason, spider) or response
        return response

    def process_exception(self, request: Request, exception: Exception, spider: Spider) -> Optional[Response]:
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY) and not request.meta.get('dont_retry', False):
            request.headers['User-Agent'] = self._ua_provider.get_random_ua()
            return self._retry(request, exception, spider)
        return None
