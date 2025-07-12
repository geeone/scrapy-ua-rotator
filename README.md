
# scrapy-ua-rotator

[![PyPI](https://img.shields.io/pypi/v/scrapy-ua-rotator)](https://pypi.org/project/scrapy-ua-rotator/)
[![Python](https://img.shields.io/badge/Python-3.9%20|%203.10%20|%203.11%20|%203.12%20|%203.13-blue)](https://pypi.org/project/scrapy-ua-rotator/)
[![License](https://img.shields.io/github/license/geeone/scrapy-ua-rotator)](LICENSE)

A modern, pluggable User-Agent rotator middleware for the Scrapy framework.

Supports rotation via:
- [`fake-useragent`](https://pypi.org/project/fake-useragent/)
- [`Faker`](https://faker.readthedocs.io/en/stable/providers/faker.providers.user_agent.html)
- Scrapy’s built-in `USER_AGENT` setting

Also supports per-proxy rotation and easy extensibility with custom providers.

---

## 📋 Requirements

- Python 3.9+
- `Faker >= 36.0.0`
- `fake-useragent >= 2.0.0`

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
    'scrapy_ua_rotator.middleware.RandomUserAgentMiddleware': 400,
    'scrapy_ua_rotator.middleware.RetryUserAgentMiddleware': 550,
}
```

Recommended provider order:

```python
FAKEUSERAGENT_PROVIDERS = [
    'scrapy_ua_rotator.providers.FakeUserAgentProvider',
    'scrapy_ua_rotator.providers.FakerProvider',
    'scrapy_ua_rotator.providers.FixedUserAgentProvider',
]

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64)..."
```

---

## 🧩 Provider Details

### FakeUserAgentProvider

```python
FAKE_USERAGENT_RANDOM_UA_TYPE = 'random'  # or 'chrome', 'firefox', etc.
FAKEUSERAGENT_FALLBACK = 'Mozilla/5.0 (Android; Mobile; rv:40.0)'
```

### FakerProvider

```python
FAKER_RANDOM_UA_TYPE = 'chrome'  # or 'firefox', 'safari', etc.
```

### FixedUserAgentProvider

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

## 📄 License

MIT © [Sergei Denisenko](https://github.com/geeone)  
See [LICENSE](https://github.com/geeone/scrapy-ua-rotator/blob/main/LICENSE)
