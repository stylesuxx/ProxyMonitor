"""Dbus related functionality.

Exposes a DBUS interface to any application can access the data.
"""
import dbus.service
import dbus.glib
import dbus


class DbusHandler(dbus.service.Object):
    """DBUS service object."""

    def __init__(self, bus_name, object_path, methods):
        """Initialize the DBUS service object.

        :param domain: DBUS domain (Backwards domain)
        :type domain: str

        :param path: DBUS path
        :type path: str

        :param methods: This is a dict with the various methods to call
                        on the monitor.
        :type methods: dict
        """
        dbus.service.Object.__init__(self, bus_name, object_path)
        self.methods = methods

    @dbus.service.method('xxx.daemon.proxy.ProxyInterface')
    def pop(self):
        """Return a single proxy tuple with ip and port.

        :returns: A tuple in the form (IP Address, Port)
        :rtype: (str, int)

        :raises IndexError: If no proxy is available
        """
        proxy = self.methods['pop']()
        return (proxy.ip, proxy.port)

    @dbus.service.method('xxx.daemon.proxy.ProxyInterface')
    def getAll(self):
        """Return a proxy tuple with ip and port."""
        proxies = self.methods['getAll']()
        formatted = []
        while proxies:
            current = proxies.pop()
            formatted.append((current.ip, current.port))

        return formatted


def DbusHandlerFactory(domain, path, methods):
    """Return a fully set up Dbus Handler.

    See DbusHandler class for detailed parameter description
    """
    bus = dbus.SessionBus()
    name = dbus.service.BusName(domain, bus=bus)

    return DbusHandler(name, path, methods)
