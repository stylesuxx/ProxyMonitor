from ProxyDaemon import (HttpProxy, HttpsProxy, ProxyList, Monitor,
                         AnonymousHttpProxy, AnonymousHttpsProxy, Socks4Proxy,
                         MainView)
import threading
import signal
import time
import sys

running = True

monitors = []
cmd = ('cd tmp/http && proxy-lists getProxies '
       '--sources-white-list="hidemyass" '
       '--protocols="http" '
       '> /dev/null 2>&1 && cat proxies.txt')
http_proxies = ProxyList(HttpProxy, cmd)

cmd = ('cd tmp/httpa && proxy-lists getProxies '
       '--sources-white-list="hidemyass" '
       '--protocols="http" '
       '--anonymity-levels="anonymous,elite" '
       '> /dev/null 2>&1 && cat proxies.txt')
anon_http_proxies = ProxyList(AnonymousHttpProxy, cmd)

cmd = ('cd tmp/https && proxy-lists getProxies '
       '--sources-white-list="hidemyass" '
       '--protocols="https" '
       '> /dev/null 2>&1 && cat proxies.txt')
https_proxies = ProxyList(HttpsProxy, cmd)

cmd = ('cd tmp/httpsa && proxy-lists getProxies '
       '--sources-white-list="hidemyass" '
       '--protocols="https" '
       '--anonymity-levels="anonymous,elite" '
       '> /dev/null 2>&1 && cat proxies.txt')
anon_https_proxies = ProxyList(AnonymousHttpsProxy, cmd)

cmd = ('cd tmp/socks4 && proxy-lists getProxies '
       #'--sources-white-list="hidemyass" '
       '--protocols="socks4 socks5" '
       '> /dev/null 2>&1 && cat proxies.txt')
socks4_proxies = ProxyList(Socks4Proxy, cmd)

http_monitor = Monitor(http_proxies, 23, 5)
https_monitor = Monitor(https_proxies, 23, 5)
anon_http_monitor = Monitor(anon_http_proxies, 23, 5)
anon_https_monitor = Monitor(anon_https_proxies, 23, 5)
socks4_monitor = Monitor(socks4_proxies, 23, 5)

monitors.append(http_monitor)
#monitors.append(https_monitor)

#monitors.append(anon_http_monitor)
#monitors.append(anon_https_monitor)

#monitors.append(socks4_monitor)


for monitor in monitors:
    monitor.daemon = True
    monitor.start()

view = MainView(monitors)

def signal_handler(signal, frame):
    global running
    running = False
    view.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

while running:
    view.refresh()
    time.sleep(1)
