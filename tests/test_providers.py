import pytest
from scrapy.settings import Settings

from scrapy_ua_rotator.providers import (
    BaseProvider,
    FixedUserAgentProvider,
    FakerProvider,
    FakeUserAgentProvider,
)


def test_fixed_user_agent_provider():
    settings = Settings({"USER_AGENT": "Fixed-UA"})
    provider = FixedUserAgentProvider(settings)
    assert provider.get_random_ua() == "Fixed-UA"


def test_faker_provider_default():
    settings = Settings({})
    provider = FakerProvider(settings)
    ua = provider.get_random_ua()
    assert isinstance(ua, str)
    assert any(x in ua for x in ["Mozilla", "Chrome", "Safari", "Opera"])


def test_faker_provider_with_type():
    settings = Settings({"FAKER_RANDOM_UA_TYPE": "chrome"})
    provider = FakerProvider(settings)
    ua = provider.get_random_ua()
    assert "Chrome" in ua or "Mozilla" in ua


def test_faker_provider_invalid_type():
    settings = Settings({"FAKER_RANDOM_UA_TYPE": "nonexistent"})
    provider = FakerProvider(settings)
    ua = provider.get_random_ua()
    assert isinstance(ua, str)


def test_fake_useragent_provider(monkeypatch):
    try:
        import fake_useragent
    except ImportError:
        pytest.skip("fake-useragent is not installed")

    settings = Settings({
        "FAKE_USERAGENT_RANDOM_UA_TYPE": "chrome",
        "FAKEUSERAGENT_OS": ["Linux"],
        "FAKEUSERAGENT_PLATFORMS": ["desktop"]
    })

    provider = FakeUserAgentProvider(settings)
    ua = provider.get_random_ua()
    assert isinstance(ua, str)
    assert "Mozilla" in ua or "Chrome" in ua


def test_fake_useragent_dict_and_attr(monkeypatch):
    try:
        import fake_useragent
    except ImportError:
        pytest.skip("fake-useragent is not installed")

    settings = Settings({
        "FAKE_USERAGENT_RANDOM_UA_TYPE": "Chrome Mobile iOS",
    })
    provider = FakeUserAgentProvider(settings)
    assert isinstance(provider.get_random_ua(), str)


def test_fake_useragent_provider_invalid_type(monkeypatch):
    class DummyUA:
        def __getitem__(self, key): raise KeyError
        random = None

    monkeypatch.setattr("scrapy_ua_rotator.providers.fake_useragent", type("mod", (), {
        "UserAgent": lambda **kwargs: DummyUA()
    }))
    settings = Settings({"FAKE_USERAGENT_RANDOM_UA_TYPE": "nonexistent"})
    provider = FakeUserAgentProvider(settings)
    assert provider.get_random_ua() is None


def test_fake_useragent_init_failure(monkeypatch):
    class BrokenUA:
        def __init__(self, *args, **kwargs): raise Exception("Boom")
    monkeypatch.setattr("scrapy_ua_rotator.providers.fake_useragent", type("mod", (), {
        "UserAgent": BrokenUA
    }))
    settings = Settings({})
    provider = FakeUserAgentProvider(settings)
    assert provider.get_random_ua() is None


def test_unimplemented_provider():
    class DummyBad(BaseProvider):
        def get_random_ua(self):
            raise NotImplementedError

    provider = DummyBad(Settings())
    with pytest.raises(NotImplementedError):
        provider.get_random_ua()


def test_base_provider_abstract_method():
    class Dummy(BaseProvider):
        pass

    with pytest.raises(TypeError):
        Dummy(Settings())


def test_base_provider_direct_call():
    class Dummy:
        settings = Settings()

    with pytest.raises(NotImplementedError):
        BaseProvider.get_random_ua(Dummy())


def test_fake_useragent_module_not_installed(monkeypatch):
    monkeypatch.setitem(__import__('sys').modules, 'fake_useragent', None)
    from importlib import reload
    import scrapy_ua_rotator.providers as providers_module

    reload(providers_module)  # re-import to simulate absence
    provider = providers_module.FakeUserAgentProvider(Settings({}))
    assert provider.get_random_ua() is None
