from ProxyDaemon import (Monitor, ProxyList, HttpProxy)
from datetime import datetime
import unittest


class TestHttpProxy(unittest.TestCase):
    def setUp(self):
        pass

    def test_monitor_init(self):
        http = ProxyList(HttpProxy, 'cat test/test_proxies.txt')
        monitor = Monitor(http)
        monitor.daemon = True
        monitor.start()

        print monitor.get_protocol()
        assert monitor.get_protocol() == 'Http'
