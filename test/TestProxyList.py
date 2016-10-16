from ProxyMonitor import ProxyList, Monitor, HttpProxy
from datetime import datetime
import unittest


class TestProxyList(unittest.TestCase):
    def setUp(self):
        self.ip = '127.0.0.1'
        self.port = 2342
        self.proxy = HttpProxy(self.ip, self.port)

    def proxy_list_test(self):
        http_proxies = ProxyList(HttpProxy, 'cat test/test_proxies.txt')
        assert not http_proxies.updated

        for item in http_proxies.aquire():
            pass

        proxy = http_proxies.get('127.0.0.1:9090')
        print proxy
        assert proxy
        assert len(http_proxies) is 2
        assert http_proxies.updated < datetime.now()
        assert '127.0.0.1:9090' in http_proxies
        assert len(http_proxies.keys()) is 2

        assert http_proxies.get('127.0.0.1:9090')
        assert http_proxies.items()

        del http_proxies['127.0.0.1:9090']
        assert len(http_proxies) is 1

        http_proxies[str(self.proxy)] = self.proxy

        for v in http_proxies:
            assert v

        http_proxies.clear()

        print http_proxies.keys()
        assert len(http_proxies) is 0

    def proxy_monitor_test(self):
        http_proxies = ProxyList(HttpProxy, 'cat test/test_proxies.txt')
        http_monitor = Monitor(http_proxies)
        assert http_monitor
