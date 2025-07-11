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

    def __init__(self, settings):
        super().__init__(settings)
        self._ua_type = settings.get('FAKE_USERAGENT_RANDOM_UA_TYPE', self.DEFAULT_UA_TYPE)
        fallback = settings.get('FAKEUSERAGENT_FALLBACK', '')

        if fake_useragent:
            try:
                self._ua = fake_useragent.UserAgent(fallback=fallback)
            except Exception:
                logger.warning("Failed to init fake_useragent, fallback will be used")
                self._ua = None
        else:
            logger.warning("fake_useragent not installed")
            self._ua = None

    def get_random_ua(self):
        if not self._ua:
            return self.settings.get('USER_AGENT', '')
        return getattr(self._ua, self._ua_type)


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
