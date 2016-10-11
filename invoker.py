#!/usr/bin/python
"""Invoke remote methods."""
import dbus

session = dbus.SessionBus()

http_provider = session.get_object('proxy.daemon.xxx',
                                   '/xxx/daemon/proxy/Http')

print http_provider.getProxy(dbus_interface='xxx.daemon.proxy.ProxyInterface')
