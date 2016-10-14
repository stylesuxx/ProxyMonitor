from ProxyDaemon import (HttpProxy, HttpsProxy, ProxyList, Monitor, ProxyView,
                         AnonymousHttpProxy, AnonymousHttpsProxy, Socks4Proxy,
                         LogView)
import threading
import curses
import signal
import time
import sys


stdscr = curses.initscr()
curses.curs_set(0)
curses.start_color()
curses.use_default_colors()
curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)

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

"""
--https
--http
"""
monitors.append(http_monitor)
#monitors.append(https_monitor)

"""
--anon
--anon-http
--anon-https
"""
#monitors.append(anon_http_monitor)
#monitors.append(anon_https_monitor)

""""""
#monitors.append(socks4_monitor)

top_offset = 1
box_offset = 7
counter = 0

logs = []
views = []
for monitor in monitors:
    monitor.daemon = True
    monitor.start()

    view = ProxyView(top_offset + box_offset * counter, 1,
                     monitor.proxy_list.Protocol.name,
                     monitor.get_stats)

    logs.append(monitor.get_log)

    views.append(view)
    counter += 1

log_view = LogView(1, 42, 'Log', logs)

def signal_handler(signal, frame):
    global running
    running = False
    stdscr.clear()
    curses.endwin()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


while running:
    stdscr.bkgd(curses.color_pair(1))
    stdscr.border()
    stdscr.addstr(0, 2, ' Proxy Daemon Monitor ', curses.color_pair(2))
    stdscr.refresh()

    for view in views:
        view.refresh()

    maxY, maxX = stdscr.getmaxyx()
    log_view.refresh(maxY - 2, maxX - 43)

    time.sleep(1)
