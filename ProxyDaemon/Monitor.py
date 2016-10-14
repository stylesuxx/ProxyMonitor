"""Monitor for proxy list."""
from dbus.mainloop.glib import DBusGMainLoop
from DbusHandler import DbusHandler, DbusHandlerFactory
from datetime import datetime
from Queue import Queue
import threading
import gobject
import time


class Monitor(threading.Thread):
    """Monitor a proxy list."""

    def __init__(self, proxy_list,
                 discovery_workers=1, recheck_workers=1):
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

        self.recheck_interval = 300
        self.reuse_interval = 300
        self.acquire_interval = 300

        self._proxy_list = proxy_list

        self._discovered = Queue()
        self._recheck = Queue()

        self._ready = []
        self._used = []

        self._discovery_workers = discovery_workers
        self._recheck_workers = recheck_workers

        self._discovery_shared = {'active': 0}
        self._recheck_shared = {'active': 0}

        self._is_acquiring = False
        self._is_cleaning = False

        self._done = False

        self._log = []

        # self._lock = threading.Lock()

    def log(self, message):
        """Log a message.

        :param message: The message to log
        :type message: str
        """
        now = datetime.now()
        self._log.append({
            'date': now,
            'message': message,
            'source': self._proxy_list.Protocol.name
        })

    def used_cleaner(self):
        """Monitor the used list.

        When a proxy is older than its time to life time on the list, it is
        moved to the recheck queue.
        """
        if len(self._used) > 0:
            last_used = self._used[0].last_used
            now = datetime.now()
            diff = (now - last_used).total_seconds()
            if diff > self.reuse_interval:
                self._is_cleaning = True
                proxy = self._used.pop()
                self._recheck.put(proxy)
            else:
                self._is_cleaning = False
        else:
            self._is_cleaning = False

    def ready_cleaner(self):
        """Monitor the ready list.

        When a proxy is above its time to life time on the list, it is moved
        to the recheck queue.
        """
        if len(self._ready) > 0:
            last_check = self._ready[0].last_check
            now = datetime.now()
            diff = (now - last_check).total_seconds()
            if diff > self.recheck_interval:
                self._is_cleaning = True
                proxy = self._ready.pop()
                self._recheck.put(proxy)
            else:
                self._is_cleaning = False
        else:
            self._is_cleaning = False

    def cleaner_worker(self, method):
        """A woerker wrapper for the cleaner methods."""
        while not self._done:
            method()

            time.sleep(1)

    def validation_worker(self, queue, shared):
        """Worker that validates a proxy.

        Gets a proxy from the assigned queue and validates it. If it is invalid
        it gets removed from the system.

        :param queue: The queue to process
        :type queue: Queue
        """
        while not self._done:
            proxy = queue.get()
            shared['active'] += 1
            if proxy.validates():
                self._ready.append(proxy)
            else:
                del self._proxy_list[str(proxy)]

            shared['active'] -= 1
            queue.task_done()

    def acquire_worker(self):
        """Worker that acquires new proxies.

        This worker acquires new proxies in a specified interval.
        """
        while not self._done:
            self.acquire()
            time.sleep(self.acquire_interval)

    def acquire(self):
        """Add newly discovered proxies to the queue.

        Triggers the proxy lists acquire function and fills the discovered
        queue.
        """
        self.log("Acquire: Start")
        self._is_acquiring = True

        for proxy in self._proxy_list.aquire():
            self._discovered.put(proxy)

        self._is_acquiring = False
        self.log("Acquire: Done")

    def get_log(self):
        """Return the log.

        :returns: Return the log
        :rtype: list
        """
        log = list(self._log)
        self._log = []
        return log

    def get_stats(self):
        """Return monitoring statistics.

        :returns: Return a dictionary with different metrics
        :rtype: dict
        """
        return {
            'total': len(self._proxy_list),
            'discovered': self._discovered.qsize(),
            'ready': len(self._ready),
            'recheck': self._recheck.qsize(),
            'used': len(self._used),
            'workers': {
                'discovery': {
                    'count': self._discovery_workers,
                    'active': self._discovery_shared['active']
                },
                'recheck': {
                    'count': self._recheck_workers,
                    'active': self._recheck_shared['active']
                }
            },
            'state': {
                'acquiring': self._is_acquiring,
                'cleaning': self._is_cleaning
            }
        }

    def pop(self):
        """Return a proxy from the ready queue.

        The proxy is taken from the ready queue, moved to the used queue and
        returned.
        """
        self.log("DBUS: pop")
        proxy = self._ready.pop()
        proxy.last_used = datetime.now()
        self._used.append(proxy)

        return proxy

    def get(self, n):
        pass

    def getAll(self):
        pass

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

        for i in range(0, self._discovery_workers):
            worker = threading.Thread(target=self.validation_worker,
                                      args=(self._discovered,
                                            self._discovery_shared))
            worker.daemon = True
            worker.start()

        for i in range(0, self._recheck_workers):
            worker = threading.Thread(target=self.validation_worker,
                                      args=(self._recheck,
                                            self._recheck_shared))
            worker.daemon = True
            worker.start()

        target = self.cleaner_worker
        ready_worker = threading.Thread(target=target,
                                        args=(self._ready_cleaner,))
        ready_worker.daemon = True
        ready_worker.start()

        target = self.cleaner_worker
        used_worker = threading.Thread(target=target,
                                       args=(self._used_cleaner,))
        used_worker.daemon = True
        used_worker.start()

        dbus_path = '/xxx/daemon/proxy/%s' % self._proxy_list.Protocol.name
        dbus_domain = 'proxy.daemon.xxx'
        self.dbus_proxy = DbusHandlerFactory(dbus_domain,
                                             dbus_path,
                                             {'pop': self.pop})

        gobject.threads_init()
        self.dbus_loop = gobject.MainLoop()
        self.dbus_loop.run()
