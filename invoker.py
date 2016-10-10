#!/usr/bin/python
"""Invoke remote methods."""
import dbus

obj = dbus.SessionBus().get_object('proxy.daemon.xxx',
                                   '/xxx/daemon/proxy/DbusProxy')

print obj.getProxy(dbus_interface='xxx.daemon.proxy.ProxyInterface')
