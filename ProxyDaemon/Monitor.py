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
                 recheck_interval=300, reuse_interval=300,
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

        self.discovery_shared = {'active': 0}
        self.recheck_shared = {'active': 0}

        self.recheck_interval = recheck_interval
        self.reuse_interval = reuse_interval
        self.acquire_threshold = acquire_threshold

        self.is_acquiring = False
        self.is_cleaning = False

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
                last_used = self.used[0].last_used
                now = datetime.now()
                diff = (now - last_used).total_seconds()
                if diff > self.reuse_interval:
                    self.is_cleaning = True
                    proxy = self.used.pop()
                    self.recheck.put(proxy)
                else:
                    self.is_cleaning = False
            else:
                self.is_cleaning = False

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
                    self.is_cleaning = True
                    proxy = self.ready.pop()
                    self.recheck.put(proxy)
                else:
                    self.is_cleaning = False
            else:
                self.is_cleaning = False

            self.lock.release()

            time.sleep(1)

    def validation_worker(self, queue, shared):
        """Worker that validates a proxy.

        Gets a proxy from the assigned queue and validates it. If it is invalid
        it gets removed from the system.

        :param queue: The queue to process
        :type queue: Queue
        """
        while not self.done:
            proxy = queue.get()
            shared['active'] += 1
            if proxy.validates():
                self.ready.append(proxy)
            else:
                self.lock.acquire()

                del self.proxy_list[str(proxy)]

                self.lock.release()

            shared['active'] -= 1
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
        self.is_acquiring = True

        proxies = self.proxy_list.aquire()
        for proxy in proxies.values():
            self.discovered.put(proxy)

        self.is_acquiring = False

    def get_stats(self):
        """Return monitoring statistics.

        :returns: Return a dictionary with different metrics
        :rtype: dict
        """
        return {
            'total': len(self.proxy_list),
            'discovered': self.discovered.qsize(),
            'ready': len(self.ready),
            'recheck': self.recheck.qsize(),
            'used': len(self.used),
            'workers': {
                'discovery': {
                    'count': self.discovery_workers,
                    'active': self.discovery_shared['active']
                },
                'recheck': {
                    'count': self.recheck_workers,
                    'active': self.recheck_shared['active']
                }
            },
            'state': {
                'acquiring': self.is_acquiring,
                'cleaning': self.is_cleaning
            }
        }

    def get_ready(self):
        """Return a proxy from the ready queue.

        The proxy is taken from the ready queue, moved to the used queue and
        returned.
        """
        proxy = self.ready.pop()
        proxy.last_used = datetime.now()
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
                                      args=(self.discovered,
                                            self.discovery_shared))
            worker.daemon = True
            worker.start()

        for i in range(0, self.recheck_workers):
            worker = threading.Thread(target=self.validation_worker,
                                      args=(self.recheck,
                                            self.recheck_shared))
            worker.daemon = True
            worker.start()

        ready_worker = threading.Thread(target=self.ready_worker)
        ready_worker.daemon = True
        ready_worker.start()

        used_worker = threading.Thread(target=self.used_worker)
        used_worker.daemon = True
        used_worker.start()

        dbus_path = '/xxx/daemon/proxy/%s' % self.proxy_list.Protocol.name
        bus = dbus.SessionBus()
        bus_name = dbus.service.BusName('proxy.daemon.xxx', bus=bus)
        self.dbusProxy = DbusProxy(bus_name, dbus_path, self.get_ready)

        gobject.threads_init()
        self.dbus_loop = gobject.MainLoop()
        self.dbus_loop.run()
