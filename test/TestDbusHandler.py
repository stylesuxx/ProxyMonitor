from nose.tools import *
from ProxyDaemon import (DbusHandlerFactory)
import threading
import unittest
import gobject
import dbus

proxy_list = []


class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

class TestDbusHandler(unittest.TestCase):
    global proxy_list

    def pop(self):
        return proxy_list.pop()

    def get(self, n):
        count = 0
        proxies = []
        while proxy_list and count < n:
            proxies.append(proxy_list.pop())
            count += 1

        return proxies

    def getAll(self):
        return proxy_list

    def start(self):
        try:
            dbus_path = '/xxx/daemon/proxy/%s' % 'Test'
            dbus_domain = 'proxy.daemon.xxx'
            self.dbus_proxy = DbusHandlerFactory(dbus_domain,
                                                 dbus_path,
                                                 {'pop': self.pop,
                                                  'get': self.get,
                                                  'getAll': self.getAll})
            gobject.threads_init()
            self.dbus_loop = gobject.MainLoop()
            self.dbus_loop.run()
        except:
            '''Was already registered.'''
            pass

    def setUp(self):
        self.proxy_list = []
        self.dbus_t = threading.Thread(target=self.start)
        self.dbus_t.daemon = True
        self.dbus_t.start()

        self.session = dbus.SessionBus()
        self.dbus_test = self.session.get_object('proxy.daemon.xxx', '/xxx/daemon/proxy/Test')

    def tearDown(self):
        pass

    def test_dbus_pop_from_list(self):
        proxy_list.append(Bunch(ip="127.0.0.1", port=1234))

        proxy = self.dbus_test.pop()
        ip, port = proxy
        assert ip
        assert port

    def test_dbus_getAll_from_list(self):
        proxy_list.append(Bunch(ip="127.0.0.1", port=1234))
        proxy_list.append(Bunch(ip="127.0.0.2", port=1234))

        proxies = self.dbus_test.getAll()
        assert len(proxies) is 2

    def test_dbus_get_less_than_available_from_list(self):
        proxy_list.append(Bunch(ip="127.0.0.1", port=1234))
        proxy_list.append(Bunch(ip="127.0.0.2", port=1234))
        proxy_list.append(Bunch(ip="127.0.0.3", port=1234))
        proxy_list.append(Bunch(ip="127.0.0.4", port=1234))

        proxies = self.dbus_test.get(3)
        assert len(proxies) is 3

    def test_dbus_get_more_than_available_from_list(self):
        proxies = self.dbus_test.get(100)
        assert len(proxies) > 0

    @raises(dbus.DBusException)
    def test_dbus_pop_from_empty_list(self):
        print self.dbus_test.pop()

    def test_dbus_get_from_empty_list(self):
        proxies = self.dbus_test.get(5)
        assert len(proxies) is 0

    def test_dbus_get_all_from_empty_list(self):
        proxies = self.dbus_test.getAll()
        assert len(proxies) is 0
