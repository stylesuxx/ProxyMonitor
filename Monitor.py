"""Monitor for proxy list."""
from dbus.mainloop.glib import DBusGMainLoop
from datetime import datetime
from Queue import Queue
import dbus.service
import threading
import dbus.glib
import gobject
import dbus
import time


class DbusProxy(dbus.service.Object):
    """DBUS service object."""

    def __init__(self, bus_name, object_path, get_proxy):
        """Initialize the DBUS service object."""
        dbus.service.Object.__init__(self, bus_name, object_path)
        self.get_proxy = get_proxy

    @dbus.service.method('xxx.daemon.proxy.ProxyInterface')
    def getProxy(self):
        """Return a proxy tuple with ip and port."""
        proxy = self.get_proxy()
        return (proxy.ip, proxy.port)


class Monitor(threading.Thread):
    """Monitor a proxy list."""

    def __init__(self, proxy_list, discovery_workers=1, recheck_workers=1,
                 recheck_interval=180):
        """Initialize the Monitor thread.

        :param proxy_list: The proxy list object
        :type proxy_list: ProxyList
        """
        threading.Thread.__init__(self)

        self.proxy_list = proxy_list

        self.discovered = Queue()
        self.recheck = Queue()
        self.ready = Queue()
        self.used = Queue()

        self.discovery_workers = discovery_workers
        self.recheck_workers = recheck_workers
        self.recheck_interval = recheck_interval

        self.done = False
        self.workers = []

    def recheck_worker(self):
        """Worker that checks proxies on the ready queue."""
        while not self.done:
            proxy = self.ready.get()
            now = datetime.now()
            delta = (now - proxy.last_check).total_seconds()
            if delta > self.recheck_interval:
                if proxy.validates():
                    self.ready.put(proxy)
                else:
                    del self.proxy_list[str(proxy)]
            else:
                self.ready.put(proxy)
                self.ready.task_done()
                time.sleep(self.recheck_interval / 2)
                continue

            self.ready.task_done()

    def discovery_worker(self):
        """Worker that checks newly discovered proxies."""
        while not self.done:
            proxy = self.discovered.get()
            if proxy.validates():
                self.ready.put(proxy)
            else:
                del self.proxy_list[str(proxy)]

            self.discovered.task_done()

    def acquire(self):
        """Add newly discovered proxies to the queue."""
        proxies = self.proxy_list.aquire()
        for proxy in proxies.values():
            self.discovered.put(proxy)

    def get_stats(self):
        """Return proxy list statistics."""
        return('%05i | %05i | %05i | %05i | %05i' %
               (len(self.proxy_list), self.discovered.qsize(),
                self.ready.qsize(), self.recheck.qsize(),
                self.used.qsize()))

    def get_ready(self):
        """Return a proxy from the ready queue.

        The proxy is taken from the ready queue, moved to the used queue and
        returned.
        """
        proxy = self.ready.get()
        self.used.put(proxy)
        self.ready.task_done()

        return proxy

    def stop(self):
        """Shutdown the monitor gracefully."""
        self.done = True
        self.dbus_loop.quit()

    def run(self):
        """Run the monitor thread.

        It will aquire the proxy list items, and process them:
        * Aquire a list of proxy servers
        * Spawn workers to validate newly discovered
        * Spawn workers to recheck ready
        * Re - acquire new proxies if below threshold
        """
        self.acquire()

        for i in range(0, self.discovery_workers):
            worker = threading.Thread(target=self.discovery_worker)
            worker.daemon = True
            worker.start()

        for i in range(0, self.recheck_workers):
            worker = threading.Thread(target=self.recheck_worker)
            worker.daemon = True
            worker.start()

        bus = dbus.SessionBus()
        bus_name = dbus.service.BusName('proxy.daemon.xxx', bus=bus)
        self.dbusProxy = DbusProxy(bus_name,
                                   '/xxx/daemon/proxy/DbusProxy',
                                   self.get_ready)

        gobject.threads_init()
        self.dbus_loop = gobject.MainLoop()
        self.dbus_loop.run()
