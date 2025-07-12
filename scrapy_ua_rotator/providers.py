import logging
from abc import abstractmethod
from faker import Faker

try:
    import fake_useragent
except ImportError:
    fake_useragent = None

logger = logging.getLogger(__name__)


class BaseProvider:
    def __init__(self, settings):
        self.settings = settings
        self._ua_type = None

    @abstractmethod
    def get_random_ua(self):
        pass


class FixedUserAgentProvider(BaseProvider):
    def __init__(self, settings):
        super().__init__(settings)
        self._ua = settings.get('USER_AGENT', '')

    def get_random_ua(self):
        return self._ua


class FakeUserAgentProvider(BaseProvider):
    DEFAULT_UA_TYPE = 'random'
    DEFAULT_OS = None
    DEFAULT_PLATFORMS = None

    def __init__(self, settings):
        super().__init__(settings)
        self._ua_type = settings.get('FAKE_USERAGENT_RANDOM_UA_TYPE', self.DEFAULT_UA_TYPE)
        self._ua_os = settings.get('FAKE_USERAGENT_OS', self.DEFAULT_OS)
        self._ua_platforms = settings.get('FAKE_USERAGENT_PLATFORMS', self.DEFAULT_PLATFORMS)
        fallback = settings.get('FAKEUSERAGENT_FALLBACK', '')

        if fake_useragent:
            try:
                self._ua = fake_useragent.UserAgent(
                    fallback=fallback,
                    os=self._ua_os,
                    platforms=self._ua_platforms
                )
            except Exception:
                logger.warning("Failed to init fake_useragent, fallback will be used")
                self._ua = None
        else:
            logger.warning("fake_useragent not installed")
            self._ua = None

    def get_random_ua(self):
        if not self._ua:
            return None  # Or return empty string / raise error if preferred

        if self._ua_type:
            # First, try attribute-based access (e.g., ua.chrome, ua.ff, ua.random)
            try:
                return getattr(self._ua, self._ua_type)
            except AttributeError:
                pass

            # Second, try dict-style access (e.g., ua['Chrome Mobile iOS'])
            try:
                return self._ua[self._ua_type]
            except (KeyError, TypeError):
                pass

        # Final fallback
        return self._ua.random


class FakerProvider(BaseProvider):
    DEFAULT_UA_TYPE = 'user_agent'

    def __init__(self, settings):
        super().__init__(settings)
        self._ua = Faker()
        self._ua_type = settings.get('FAKER_RANDOM_UA_TYPE', self.DEFAULT_UA_TYPE)

    def get_random_ua(self):
        try:
            return getattr(self._ua, self._ua_type)()
        except AttributeError:
            logger.debug("Couldn't retrieve '%s', using default '%s'", self._ua_type, self.DEFAULT_UA_TYPE)
            return getattr(self._ua, self.DEFAULT_UA_TYPE)()
