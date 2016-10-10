from datetime import datetime
import unittest
import Proxy


class TestProxy(unittest.TestCase):
    def setUp(self):
        self.ip = '127.0.0.1'
        self.port = 2342
        self.proxy = Proxy.HttpProxy(self.ip, self.port)

    def initialize_http_proxy_test(self):
        assert self.proxy.ip is self.ip
        assert self.proxy.port is self.port
        assert self.proxy.added
        assert not self.proxy.last_used

    def to_string_test(self):
        print str(self.proxy)
        assert str(self.proxy) == '%s:%i' % (self.ip, self.port)

    def validate_http_proxy_test(self):
        self.proxy.validates()
        assert self.proxy.checked
        assert self.proxy.last_check

    def proxy_list_plain_test(self):
        http_proxies = {}

        http_proxies[str(self.proxy)] = self.proxy
        http_proxies[str(self.proxy)] = self.proxy

        assert len(http_proxies) is 1
        assert self.proxy in http_proxies.values()

    def proxy_list_test(self):
        http_proxies = Proxy.ProxyList(Proxy.HttpProxy, 'cat test_proxies.txt')
        assert not http_proxies.updated

        http_proxies.aquire()

        print http_proxies
        assert http_proxies['127.0.0.1:9090']
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
        http_proxies = Proxy.ProxyList(Proxy.HttpProxy, 'cat test_proxies.txt')
        http_monitor = Proxy.Monitor(http_proxies)

        assert http_monitor.discovered
        assert http_monitor.recheck
        assert http_monitor.ready
        assert http_monitor.used
