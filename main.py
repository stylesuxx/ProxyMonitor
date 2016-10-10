from Proxy import ProxyList, HttpProxy
from Monitor import Monitor
import threading
import signal
import time
import sys

http_proxies = ProxyList(HttpProxy,
                         ('proxy-lists getProxies --sources-white-list="hidemyass" --protocols="http" > /dev/null 2>&1 && cat proxies.txt'))

http_monitor = Monitor(http_proxies, 10, 3, 300)
http_monitor.daemon = True
http_monitor.start()

"""
def signal_handler(signal, frame):
    print "Shutting down...."
    http_monitor.stop()

signal.signal(signal.SIGINT, signal_handler)
"""
print'Type   | Curr. | Disc. | Ready |       | Used  |'
print'-------|-------|-------|-------|-------|-------|'
while threading.active_count() > 0:
    if http_monitor:
        sys.stdout.write('\rHTTP   | %s |' % http_monitor.get_stats())
        sys.stdout.flush()
    time.sleep(1)

print """Shutdown completed"""
