"""
Downloader Middlewares for BookScraper

Available middlewares:
    - ScrapeOpsFakeBrowserHeaderAgentMiddleware : rotates full browser header sets
    - ScrapeOpsFakeUserAgentMiddleware          : rotates User-Agent strings only
    - MyProxyMiddleware                         : Oxylabs Web Unblocker proxy
    - ScrapeOpsProxyMiddleware                  : ScrapeOps Proxy Aggregator API

Enable/disable via DOWNLOADER_MIDDLEWARES in settings.py
"""

from scrapy import signals
from scrapy import Request
from itemadapter import ItemAdapter
from urllib.parse import urlencode
from random import randint
import requests
import base64


# DEFAULT SCRAPY MIDDLEWARES (required boilerplate)

class BookscraperSpiderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        return None

    def process_spider_output(self, response, result, spider):
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        pass

    async def process_start(self, start):
        async for item_or_request in start:
            yield item_or_request

    def spider_opened(self, spider):
        spider.logger.info(f"Spider opened: {spider.name}")


class BookscraperDownloaderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        return None

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass

    def spider_opened(self, spider):
        spider.logger.info(f"Spider opened: {spider.name}")


# HEADER ROTATION MIDDLEWARES

class ScrapeOpsFakeUserAgentMiddleware:
    """Rotates User-Agent strings using ScrapeOps API."""

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def __init__(self, settings):
        self.scrapeops_api_key = settings.get('SCRAPEOPS_API_KEY')
        self.scrapeops_endpoint = settings.get(
            'SCRAPEOPS_FAKE_USER_AGENT_ENDPOINT',
            'http://headers.scrapeops.io/v1/user-agents?'
        )
        self.active = settings.get('SCRAPEOPS_FAKE_USER_AGENT_ENABLED', False)
        self.num_results = settings.get('SCRAPEOPS_NUM_RESULTS')
        self.user_agents_list = []

        if self.active and self.scrapeops_api_key:
            self._fetch_user_agents()

    def _fetch_user_agents(self):
        payload = {'api_key': self.scrapeops_api_key}
        if self.num_results:
            payload['num_results'] = self.num_results
        response = requests.get(self.scrapeops_endpoint, params=urlencode(payload))
        self.user_agents_list = response.json().get('result', [])

    def _get_random_user_agent(self):
        return self.user_agents_list[randint(0, len(self.user_agents_list) - 1)]

    def process_request(self, request, spider):
        if self.active and self.user_agents_list:
            request.headers['User-Agent'] = self._get_random_user_agent()


class ScrapeOpsFakeBrowserHeaderAgentMiddleware:
    """Rotates full browser header sets using ScrapeOps API."""

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def __init__(self, settings):
        self.scrapeops_api_key = settings.get('SCRAPEOPS_API_KEY')
        self.scrapeops_endpoint = settings.get(
            'SCRAPEOPS_FAKE_BROWSER_HEADER_ENDPOINT',
            'http://headers.scrapeops.io/v1/browser-headers?'
        )
        self.active = settings.get('SCRAPEOPS_FAKE_BROWSER_HEADER_ENABLED', False)
        self.num_results = settings.get('SCRAPEOPS_NUM_RESULTS')
        self.headers_list = []

        if self.active and self.scrapeops_api_key:
            self._fetch_headers()

    def _fetch_headers(self):
        payload = {'api_key': self.scrapeops_api_key}
        if self.num_results:
            payload['num_results'] = self.num_results
        response = requests.get(self.scrapeops_endpoint, params=urlencode(payload))
        self.headers_list = response.json().get('result', [])

    def _get_random_headers(self):
        return self.headers_list[randint(0, len(self.headers_list) - 1)]

    def process_request(self, request, spider):
        if self.active and self.headers_list:
            request.headers = self._get_random_headers()


# PROXY MIDDLEWARES

class MyProxyMiddleware:
    """
    Routes requests through Oxylabs Web Unblocker.
    Configure via settings: PROXY_USER, PROXY_PASSWORD, PROXY_ENDPOINT, PROXY_PORT
    """

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def __init__(self, settings):
        self.user = settings.get('PROXY_USER')
        self.password = settings.get('PROXY_PASSWORD')
        self.endpoint = settings.get('PROXY_ENDPOINT')
        self.port = settings.get('PROXY_PORT')

    def process_request(self, request, spider):
        credentials = f'{self.user}:{self.password}'
        encoded = base64.b64encode(credentials.encode()).decode()
        request.meta['proxy'] = f'http://{self.endpoint}:{self.port}'
        request.headers['Proxy-Authorization'] = f'Basic {encoded}'


class ScrapeOpsProxyMiddleware:
    """
    Routes requests through ScrapeOps Proxy Aggregator.
    Handles proxy rotation, headers, and retries automatically.
    Configure via settings: SCRAPEOPS_API_KEY, SCRAPEOPS_PROXY_SETTINGS
    """

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def __init__(self, settings):
        self.scrapeops_api_key = settings.get('SCRAPEOPS_API_KEY')
        self.scrapeops_endpoint = 'https://proxy.scrapeops.io/v1/?'
        self.active = settings.get('SCRAPEOPS_PROXY_ENABLED', False)
        self.proxy_settings = settings.get('SCRAPEOPS_PROXY_SETTINGS', {})

    @staticmethod
    def _replace_response_url(response):
        real_url = response.headers.get('Sops-Final-Url', def_val=response.url)
        return response.replace(url=real_url.decode(response.headers.encoding))

    def _build_proxy_url(self, request):
        payload = {'api_key': self.scrapeops_api_key, 'url': request.url}
        payload.update(self.proxy_settings)
        for key, value in request.meta.items():
            if key.startswith('sops_'):
                payload[key.replace('sops_', '')] = value
        return self.scrapeops_endpoint + urlencode(payload)

    def _is_active(self):
        return bool(self.active and self.scrapeops_api_key)

    def process_request(self, request, spider):
        if not self._is_active() or self.scrapeops_endpoint in request.url:
            return None
        proxy_url = self._build_proxy_url(request)
        return request.replace(cls=Request, url=proxy_url, meta=request.meta)

    def process_response(self, request, response, spider):
        return self._replace_response_url(response)