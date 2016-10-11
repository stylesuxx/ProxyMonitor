from ProxyDaemon import ProxyList, Monitor, HttpProxy, HttpsProxy
from datetime import datetime
import unittest


class TestHttpProxy(unittest.TestCase):
    def setUp(self):
        self.ip = '127.0.0.1'
        self.port = 2342
        self.proxy = HttpProxy(self.ip, self.port)

    def initialize_http_proxy_test(self):
        assert self.proxy.ip is self.ip
        assert self.proxy.port is self.port
        assert self.proxy.added
        assert not self.proxy.last_used

    def to_string_test(self):
        print str(self.proxy)
        assert str(self.proxy) == '%s:%i' % (self.ip, self.port)

    def validate_http_proxy_test(self):
        validates = self.proxy.validates()
        assert not validates
        assert self.proxy.checked
        assert self.proxy.last_check

    def proxy_name_test(self):
        print self.proxy.name
        assert self.proxy.name is 'Http'


class TestHttpsProxy(unittest.TestCase):
    def setUp(self):
        self.ip = '127.0.0.1'
        self.port = 2342
        self.proxy = HttpsProxy(self.ip, self.port)

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

    def proxy_name_test(self):
        print self.proxy.name
        assert self.proxy.name is 'Https'
