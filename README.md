
# scrapy-ua-rotator

[![PyPI](https://img.shields.io/pypi/v/scrapy-ua-rotator)](https://pypi.org/project/scrapy-ua-rotator/)
[![Python](https://img.shields.io/badge/Python-3.9%20|%203.10%20|%203.11%20|%203.12%20|%203.13-blue)](https://pypi.org/project/scrapy-ua-rotator/)
[![License](https://img.shields.io/github/license/geeone/scrapy-ua-rotator)](LICENSE)
[![Build Status](https://github.com/geeone/scrapy-ua-rotator/actions/workflows/build.yml/badge.svg)](https://github.com/geeone/scrapy-ua-rotator/actions/workflows/build.yml)
[![Codecov](https://codecov.io/gh/geeone/scrapy-ua-rotator/branch/main/graph/badge.svg)](https://codecov.io/gh/geeone/scrapy-ua-rotator)

A modern, pluggable User-Agent rotator middleware for the Scrapy framework.

Supports rotation via:
- [`fake-useragent`](https://pypi.org/project/fake-useragent/)
- [`Faker`](https://faker.readthedocs.io/en/stable/providers/faker.providers.user_agent.html)
- Scrapy’s built-in `USER_AGENT` setting

Also supports per-proxy rotation and easy extensibility with custom providers.

---

## 📋 Requirements

- Python 3.9+
- `Faker >= 18.0.0`
- `fake-useragent >= 1.5.0`

> ✅ **Tested with**: Scrapy 2.9, 2.10, 2.11, and 2.12  

---

## 📦 Installation

```bash
pip install scrapy-ua-rotator
```

---

## ⚙️ Configuration

Disable Scrapy’s default middleware and enable ours:

```python
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
    'scrapy_ua_rotator.middleware.RandomUserAgentMiddleware': 400,
    'scrapy_ua_rotator.middleware.RetryUserAgentMiddleware': 550,
}
```

Recommended provider order:

```python
FAKEUSERAGENT_PROVIDERS = [
    'scrapy_ua_rotator.providers.FakeUserAgentProvider',  # Primary provider using the fake-useragent library
    'scrapy_ua_rotator.providers.FakerProvider',          # Fallback provider that generates synthetic UAs via Faker
    'scrapy_ua_rotator.providers.FixedUserAgentProvider', # Final fallback: uses the static USER_AGENT setting
]

# Static user-agent string to be used if all providers fail to return a valid value
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64)..."
```

---

## 🧩 Provider Details

### FakeUserAgentProvider

Assigns a new user-agent using [`fake-useragent`](https://github.com/fake-useragent/fake-useragent).  
Supports fine-tuned filtering via:

```python
FAKE_USERAGENT_RANDOM_UA_TYPE = 'Chrome Mobile iOS'   # str; browser to prioritize (default: 'random')
FAKEUSERAGENT_OS = ['Linux']                          # str or list[str]; OS filter (default: None — all OSes)
FAKEUSERAGENT_PLATFORMS = ['mobile']                  # str or list[str]; platform filter (default: None — all platforms)
FAKEUSERAGENT_FALLBACK = 'Mozilla/5.0 (...)'          # str; fallback UA string (default: internal fallback)
```

> 💡 **Note:** See [docs](https://github.com/fake-useragent/fake-useragent/blob/main/README.md) for supported options and advanced usage.

### FakerProvider

Uses [`Faker`](https://faker.readthedocs.io/en/stable/providers/faker.providers.user_agent.html) to generate synthetic UA strings.

```python
FAKER_RANDOM_UA_TYPE = 'chrome'  # or 'firefox', 'safari', etc.
```

> 💡 **Note:** See [docs](https://github.com/joke2k/faker/blob/master/README.rst) for supported options and advanced usage.

### FixedUserAgentProvider

Simply uses the provided `USER_AGENT` setting without rotation.  
Useful as a fallback if other providers fail.

```python
USER_AGENT = "Mozilla/5.0 ..."
```

---

## 🔀 Proxy-Aware Mode

If you’re using rotating proxies (e.g., via `scrapy-proxies`), enable per-proxy UA assignment:

```python
RANDOM_UA_PER_PROXY = True
```

Make sure `RandomUserAgentMiddleware` has higher priority than your proxy middleware.

---

## 🧪 Example Output

To verify it’s working, log your request headers in your spider:

```python
def parse(self, response):
    self.logger.info("Using UA: %s", response.request.headers.get('User-Agent'))
```

---

## 🔧 Extending with Custom Providers

Add your own class:

```python
FAKEUSERAGENT_PROVIDERS = [
    'your_project.providers.MyCustomProvider',
    ...
]
```

Just inherit from `BaseProvider` and implement `get_random_ua()`.

---

## 🤝 Contributing

Contributions, suggestions, and issues are welcome!  
Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

MIT © [Sergei Denisenko](https://github.com/geeone)  
See [LICENSE](https://github.com/geeone/scrapy-ua-rotator/blob/main/LICENSE)
