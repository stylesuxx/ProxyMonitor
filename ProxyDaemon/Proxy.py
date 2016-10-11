"""
Holds information about a single proxy.

Ip address, ports, protocols, and different time metrics.
"""

from abc import ABCMeta, abstractmethod, abstractproperty
from datetime import datetime
import requests


class Proxy:
    """Abstract proxy base class."""

    __metaclass__ = ABCMeta

    @abstractproperty
    def name(self):
        """Proxy type.

        This is the name used in the DBUS interface. Every proxy should have
        its unique name.
        """
        raise NotImplementedError

    def __init__(self, ip, port):
        """Initialize the proxy.

        :param ip: The IP Address of the proxy
        :type ip: string

        :param port: The port of the proxy
        :type port: int
        """
        self.ip = ip
        self.port = port

        self.valid = False
        self.checked = False
        self.last_used = None
        self.last_check = None
        self.added = datetime.now()

    def __str__(self):
        """Get a proxies string representation.

        :returns: Return the string representation of the proxy
        :rtype: string
        """
        return('%s:%i' % (self.ip, self.port))

    def validates(self):
        """Validate the proxy.

        :returns: Return true if the proxy is valid
        :rtype: boolean
        """
        self.valid = self._is_valid()

        self.checked = True
        self.last_check = datetime.now()

        return self.valid

    @abstractmethod
    def _is_valid(self):
        """Subclass needs to implement this method.

        This method is used to validate a proxy, anything can happen here.
        Return True if the proxy validates, False otherwise.

        :returns: Return true if the proxy is valid
        :rtype: boolean
        """
        raise NotImplementedError


class HttpProxy(Proxy):
    """HTTP proxy base class."""

    name = "Http"

    def __init__(self, ip, port):
        """Initialize a HTTP proxy.

        :param ip: IP Address of the http proxy
        :type ip: string

        :param port: Port of the http proxy
        :type port: int
        """
        super(HttpProxy, self).__init__(ip, port)

    def _is_valid(self):
        """Validate that the HTTP proxy is valid.

        To qualify as valid id needs to successfully connect to an IP service
        within 30 seconds.

        :returns: Return true if the proxy is valid
        :rtype: boolean
        """
        proxies = {'http': 'http://%s:%i' % (self.ip, self.port)}
        try:
            r = requests.get('http://api.ipify.org/?format=json',
                             proxies=proxies, timeout=30)
            result = r.json()
            assert result['ip']
            return True
        except:
            pass

        return False


class HttpsProxy(Proxy):
    """HTTPS proxy base class."""

    name = "Https"

    def __init__(self, ip, port):
        """Initialize a HTTP proxy.

        :param ip: IP Address of the https proxy
        :type ip: string

        :param port: Port of the https proxy
        :type port: int
        """
        super(HttpsProxy, self).__init__(ip, port)

    def _is_valid(self):
        """Validate that the HTTP proxy is valid.

        To qualify as valid id needs to successfully connect to an IP service
        within 30 seconds.

        :returns: Return true if the proxy is valid
        :rtype: boolean
        """
        proxies = {'https': 'https://%s:%i' % (self.ip, self.port)}
        try:
            r = requests.get('https://api.ipify.org/?format=json',
                             proxies=proxies, timeout=30)
            result = r.json()
            assert result['ip']
            return True
        except:
            pass

        return False


class Socks4Proxy(Proxy):
    pass


class Socks5Proxy(Proxy):
    pass
