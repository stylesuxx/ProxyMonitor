from Proxy import HttpProxy, HttpsProxy
from ProxyList import ProxyList
from Monitor import Monitor
import threading
import curses
import time

stdscr = curses.initscr()

http_proxies = ProxyList(HttpProxy,
                         ('cd tmp/http && proxy-lists getProxies --sources-white-list="hidemyass" --protocols="http" > /dev/null 2>&1 && cat proxies.txt'))

https_proxies = ProxyList(HttpsProxy,
                         ('cd tmp/https && proxy-lists getProxies --sources-white-list="hidemyass" --protocols="https" > /dev/null 2>&1 && cat proxies.txt'))


http_monitor = Monitor(http_proxies, 5, 2)
http_monitor.daemon = True
http_monitor.start()

https_monitor = Monitor(https_proxies, 5, 2)
https_monitor.daemon = True
https_monitor.start()


stdscr.addstr(0, 0, 'Type   | Curr. | Disc. | Ready | ReCh. | Used  |')
stdscr.addstr(1, 0, '-------|-------|-------|-------|-------|-------|')
while threading.active_count() > 0:
    stdscr.addstr(2, 0, 'http   | %s |' % http_monitor.get_stats())
    stdscr.addstr(3, 0, 'https  | %s |' % https_monitor.get_stats())
    stdscr.refresh()
    time.sleep(1)

print """Shutdown completed"""
curses.endwin()
