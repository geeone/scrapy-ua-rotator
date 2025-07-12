from abc import ABC, abstractmethod
import logging
from typing import Optional, Union, List

from faker import Faker
from scrapy.settings import Settings


try:
    import fake_useragent
except ImportError:
    fake_useragent = None

logger = logging.getLogger(__name__)


class BaseProvider(ABC):
    """Abstract base class for all User-Agent providers."""

    def __init__(self, settings: Settings):
        self.settings: Settings = settings
        self._ua_type: Optional[str] = None

    @abstractmethod
    def get_random_ua(self) -> Optional[str]:
        """Return a random user-agent string."""
        raise NotImplementedError


class FixedUserAgentProvider(BaseProvider):
    """Returns the fixed USER_AGENT value from settings."""

    def __init__(self, settings: Settings):
        super().__init__(settings)
        self._ua: str = settings.get('USER_AGENT', '')

    def get_random_ua(self) -> str:
        return self._ua


class FakeUserAgentProvider(BaseProvider):
    """
    Uses `fake_useragent` to generate realistic UAs.
    Supports filtering by UA type, OS, and platform.
    """

    DEFAULT_UA_TYPE = 'random'
    DEFAULT_OS = None
    DEFAULT_PLATFORMS = None

    def __init__(self, settings: Settings):
        super().__init__(settings)
        self._ua_type: str = settings.get(
            'FAKE_USERAGENT_RANDOM_UA_TYPE', self.DEFAULT_UA_TYPE)
        self._ua_os: Optional[Union[str, List[str]]] = settings.get(
            'FAKE_USERAGENT_OS', self.DEFAULT_OS)
        self._ua_platforms: Optional[Union[str, List[str]]] = settings.get(
            'FAKEUSERAGENT_PLATFORMS', self.DEFAULT_PLATFORMS)
        fallback: str = settings.get('FAKEUSERAGENT_FALLBACK', '')

        if fake_useragent:
            try:
                self._ua = fake_useragent.UserAgent(
                    os=self._ua_os,
                    platforms=self._ua_platforms,
                    **({'fallback': fallback} if fallback else {})
                )
            except Exception:
                logger.warning(
                    "Failed to init fake_useragent, fallback will be used")
                self._ua = None
        else:
            logger.warning("fake_useragent not installed")
            self._ua = None

    def get_random_ua(self) -> Optional[str]:
        """Return user-agent string using attribute or dict-style access."""
        if not self._ua:
            return None

        if self._ua_type:
            try:
                return getattr(self._ua, self._ua_type)
            except AttributeError:
                pass

            try:
                return self._ua[self._ua_type]
            except (KeyError, TypeError):
                pass

        return self._ua.random


class FakerProvider(BaseProvider):
    """Generates synthetic user-agents using the `faker` library."""

    DEFAULT_UA_TYPE = 'user_agent'

    def __init__(self, settings: Settings):
        super().__init__(settings)
        self._ua = Faker()
        self._ua_type: str = settings.get(
            'FAKER_RANDOM_UA_TYPE', self.DEFAULT_UA_TYPE)

    def get_random_ua(self) -> str:
        try:
            return getattr(self._ua, self._ua_type)()
        except AttributeError:
            logger.debug(
                f"Couldn't retrieve '{self._ua_type}', using default '{self.DEFAULT_UA_TYPE}'")
            return getattr(self._ua, self.DEFAULT_UA_TYPE)()
