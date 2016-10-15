#!/usr/bin/python
"""Invoke remote methods."""
import dbus

session = dbus.SessionBus()
http = session.get_object('proxy.daemon.xxx', '/xxx/daemon/proxy/Http')

print http.pop()
print http.get(3)
print http.getAll()
