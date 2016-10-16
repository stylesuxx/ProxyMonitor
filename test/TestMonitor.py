from ProxyMonitor import (Monitor, ProxyList, HttpProxy)
from nose.plugins.attrib import attr
from datetime import datetime
from nose.tools import *
import unittest

@attr(dbus=True)
class TestHttpProxy(unittest.TestCase):
    monitor = None

    @classmethod
    def setupClass(cls):
        http = ProxyList(HttpProxy, 'cat test/test_proxies.txt')
        cls.monitor = Monitor(http)
        cls.monitor.daemon = True
        cls.monitor.start()

    def test_monitor_protocol(self):
        print self.monitor.get_protocol()
        assert self.monitor.get_protocol() == 'Http'

    def test_monitor_log(self):
        log = self.monitor.get_log()
        print log
        assert log

    @raises(IndexError)
    def test_monitor_pop(self):
        self.monitor.pop()

    def test_monitor_get(self):
        proxies = self.monitor.get(5)
        print proxies
        assert len(proxies) is 0

    def test_monitor_getAll(self):
        proxies = self.monitor.getAll()

        '''
        stats = self.monitor.get_stats()
        '''
