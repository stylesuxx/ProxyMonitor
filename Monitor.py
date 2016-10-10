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

    def __init__(self, proxy_list,
                 discovery_workers=1, recheck_workers=1,
                 recheck_interval=180, reuse_interval=180,
                 acquire_threshold=10):
        """Initialize the Monitor thread.

        New proxies are moved to the discovered queue where workers will pick
        them up, and if they validate, add them to the ready list.

        A single worker monitors the ready list for items that have reached the
        timeout, and moves them to the recheck queue.

        Once a proxy has been used it is moved to the used list where it is
        checked for time to bring it back in rotation and moved it to the
        recheck queue if the time is reached.

        :param proxy_list: The proxy list object
        :type proxy_list: ProxyList

        :param discovery_workers: Amount of workers processing the discovery
                                  queue
        :type discovery_workers: int

        :param recheck_workers: Amount of workers processing the recheck queue
        :type recheck_workers: int

        :param recheck_interval: Recheck proxy on ready queue after this time
                                 in seconds
        :type recheck_interval: int

        :param reuse_interval: Recheck proxy on used queue after this time
                               in seconds
        :type reuse_interval: int
        """
        threading.Thread.__init__(self)

        self.proxy_list = proxy_list

        self.discovered = Queue()
        self.recheck = Queue()

        self.ready = []
        self.used = []

        self.discovery_workers = discovery_workers
        self.recheck_workers = recheck_workers
        self.recheck_interval = recheck_interval
        self.reuse_interval = reuse_interval
        self.acquire_threshold = acquire_threshold

        self.done = False
        self.workers = []

        self.lock = threading.Lock()

    def used_worker(self):
        """Monitor the used list.

        When a proxy is older than its time to life time on the list, it is
        moved to the recheck queue.
        """
        while not self.done:
            # Acquire a lock while we manipulate the list
            self.lock.acquire()

            if len(self.used) > 0:
                last_check = self.used[0].last_used
                now = datetime.now()
                diff = (now - last_check).total_seconds()
                if diff > self.reuse_interval:
                    proxy = self.used.pop()
                    self.recheck.put(proxy)

            self.lock.release()

            time.sleep(1)

    def ready_worker(self):
        """Monitor the ready list.

        When a proxy is above its time to life time on the list, it is moved
        to the recheck queue.
        """
        while not self.done:
            # Acquire a lock while we manipulate the list
            self.lock.acquire()

            if len(self.ready) > 0:

                last_check = self.ready[0].last_check
                now = datetime.now()
                diff = (now - last_check).total_seconds()
                if diff > self.recheck_interval:
                    proxy = self.ready.pop()
                    self.recheck.put(proxy)

            self.lock.release()

            time.sleep(1)

    def validation_worker(self, queue):
        """Worker that validates a proxy.

        Gets a proxy from the assigned queue and validates it. If it is invalid
        it gets removed from the system.

        :param queue: The queue to process
        :type queue: Queue
        """
        while not self.done:
            proxy = queue.get()
            if proxy.validates():
                self.ready.append(proxy)
            else:
                self.lock.acquire()

                del self.proxy_list[str(proxy)]

                self.lock.release()

            queue.task_done()

    def acquire_worker(self):
        """Worker that acquires new proxies.

        This worker acquires new proxies when the proxy list is below a
        threshold.
        """
        while not self.done:
            if len(self.proxy_list) < self.acquire_threshold:
                self.acquire()

            time.sleep(10)

    def acquire(self):
        """Add newly discovered proxies to the queue.

        Triggers the proxy lists acquire function and fills the discovered
        queue.
        """
        proxies = self.proxy_list.aquire()
        for proxy in proxies.values():
            self.discovered.put(proxy)

    def get_stats(self):
        """Return monitoring statistics."""
        return('%05i | %05i | %05i | %05i | %05i' %
               (len(self.proxy_list), self.discovered.qsize(),
                len(self.ready), self.recheck.qsize(), len(self.used)))

    def get_ready(self):
        """Return a proxy from the ready queue.

        The proxy is taken from the ready queue, moved to the used queue and
        returned.
        """
        proxy = self.ready.pop()
        self.used.append(proxy)

        return proxy

    def run(self):
        """Run the monitor thread.

        It will aquire the proxy list items, and process them:
        * Aquire a list of proxy servers
        * Spawn workers to validate newly discovered
        * Spawn workers to recheck previously validated
        * Run a worker to check the ttl on the ready list
        * Run a worker to check the ttl on the used list
        * Run the DBUS daemon
        """
        acquire_worker = threading.Thread(target=self.acquire_worker)
        acquire_worker.daemon = True
        acquire_worker.start()

        for i in range(0, self.discovery_workers):
            worker = threading.Thread(target=self.validation_worker,
                                      args=(self.discovered,))
            worker.daemon = True
            worker.start()

        for i in range(0, self.recheck_workers):
            worker = threading.Thread(target=self.validation_worker,
                                      args=(self.recheck,))
            worker.daemon = True
            worker.start()

        ready_worker = threading.Thread(target=self.ready_worker)
        ready_worker.daemon = True
        ready_worker.start()

        used_worker = threading.Thread(target=self.used_worker)
        used_worker.daemon = True
        used_worker.start()

        bus = dbus.SessionBus()
        bus_name = dbus.service.BusName('proxy.daemon.xxx', bus=bus)
        self.dbusProxy = DbusProxy(bus_name,
                                   '/xxx/daemon/proxy/DbusProxy',
                                   self.get_ready)

        gobject.threads_init()
        self.dbus_loop = gobject.MainLoop()
        self.dbus_loop.run()
