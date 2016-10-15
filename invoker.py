#!/usr/bin/python
"""Invoke remote methods."""
import dbus

session = dbus.SessionBus()
http = session.get_object('proxy.daemon.xxx', '/xxx/daemon/proxy/Http')

print http.pop(dbus_interface='xxx.daemon.proxy.ProxyInterface')
print http.getAll(dbus_interface='xxx.daemon.proxy.ProxyInterface')
