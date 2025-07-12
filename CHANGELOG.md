
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-07-12

### Added

- **Initial release** of `scrapy-ua-rotator`, a modern and actively maintained alternative to `scrapy-fake-useragent`, compatible with Scrapy 2.10.0 and above.
- Support for multiple User-Agent providers with configurable priority:
  - **FakeUserAgentProvider** – uses [`fake-useragent`](https://pypi.org/project/fake-useragent/), with fallback support.
  - **FakerProvider** – uses [`Faker`](https://pypi.org/project/Faker/) to generate user agents (e.g. `chrome()`, `firefox()`, etc.).
  - **FixedUserAgentProvider** – uses the static `USER_AGENT` from Scrapy settings.
- `RandomUserAgentMiddleware` – injects random UAs into each request, optionally per proxy.
- `RetryUserAgentMiddleware` – sets a new UA upon retrying failed requests.
- Support for filtering user-agents by `os` and `platforms` in `FakeUserAgentProvider`, via new optional settings: `FAKE_USERAGENT_OS` and `FAKE_USERAGENT_PLATFORMS`.
  - Example: `FAKE_USERAGENT_OS = ['Linux']`, `FAKE_USERAGENT_PLATFORMS = ['mobile']`.
- Modular architecture – allows users to define their own providers using Scrapy’s `load_object()` mechanism.
- Fallback logic – if a provider fails to load, middleware falls back to the fixed UA provider.
- Installable as a pip package (`pip install scrapy-ua-rotator` or `pip install -e .` for local use).
- Documentation:
  - Example configuration for Scrapy’s `DOWNLOADER_MIDDLEWARES` and `FAKEUSERAGENT_PROVIDERS`.
  - Provider configuration keys (`FAKER_RANDOM_UA_TYPE`, `FAKEUSERAGENT_RANDOM_UA_TYPE`, etc.).

### Changed

- Minimum supported Python version is `3.9`.
- Minimum supported `Faker` version is `36.0.0`.
- Minimum supported `fake-useragent` version is `2.0.0`.

### Deprecated

- Nothing yet.

### Removed

- Nothing yet.

### Fixed

- Ensure compatibility with Scrapy 2.10.0+ by replacing deprecated `EXCEPTIONS_TO_RETRY` class attribute usage with instance-level `exceptions_to_retry` fallback logic.
- `RetryUserAgentMiddleware` now safely assigns `EXCEPTIONS_TO_RETRY` using `hasattr`, improving compatibility with Scrapy 2.10+ and avoiding crashes when the class attribute is missing.
- `FakeUserAgentProvider` now supports both attribute-style (e.g. `ua.chrome`) and dict-style (e.g. `ua['Chrome Mobile iOS']`) access to user-agents.
- Avoid overriding `fake-useragent`'s internal default fallback when `FAKEUSERAGENT_FALLBACK` is not set in settings.

### Security

- N/A
