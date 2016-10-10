"""
Holds information about a single proxy.

Ip address, ports, protocols, and different time metrics.
"""

from abc import ABCMeta, abstractmethod
from datetime import datetime
import subprocess
import requests
import sys


class Proxy:
    """Abstract proxy base class."""

    __metaclass__ = ABCMeta

    def __init__(self, ip, port):
        """Initialize the proxy.

        :param ip: The IP Address of the proxy
        :type ip: string

        :param port: The port of the proxy
        :type port: int

        :returns: True if file size is bigger than minValid and smaller than
                  or equal to maxValid
        :rtype: boolean
        """
        self.ip = ip
        self.port = port

        self.valid = False
        self.checked = False
        self.last_used = None
        self.last_check = None
        self.added = datetime.now()

    def __str__(self):
        """Get string representation.

        :returns: Return the string representation of the proxy
        :rtype: string
        """
        return '%s:%i' % (self.ip, self.port)

    def validates(self):
        """Validate the proxy.

        :returns: Return true if the proxy is valid
        :rtype: boolean
        """
        self.valid = self._is_valid()
        self._set_checked()
        return self.valid

    @abstractmethod
    def _is_valid(self):
        """Subclass needs to implement this method.

        :returns: Return true if the proxy is valid
        :rtype: boolean
        """
        return NotImplemented

    def _set_checked(self):
        """Mark the proxy as checked."""
        self.checked = True
        self.last_check = datetime.now()


class HttpProxy(Proxy):
    """HTTP proxy base class"""

    def __init__(self, ip, port):
        """Initialize a HTTP proxy.

        :param ip: The IP Address of the http proxy
        :type ip: string

        :param port: The port of the http proxy
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
    pass


class Socks4Proxy(Proxy):
    pass


class Socks5Proxy(Proxy):
    pass


class ProxyList():
    """Base Class for proxy List."""

    def __init__(self, Protocol, command):
        """Initialize an empty proxy list.

        :param protocol: The proxy protocol for this list
        :type protocol: Proxy

        :param command: The commandline string used to aquire new proxies
        :type command: string
        """
        self.command = command
        self.Protocol = Protocol
        self.proxies = {}
        self.updated = None

    def __len__(self):
        """Return length of the list.

        :returns: Return the length of the proxy list
        :rtype: int
        """
        return len(self.proxies)

    def __getitem__(self, key):
        """Return a proxy item.

        :param key: The name of the proxy
        :type key: str

        :returns: Return the proxy
        :rtype: Proxy
        """
        return self.proxies[key]

    def __setitem__(self, key, value):
        """Set a proxy item.

        :param key: The name of the proxy
        :type key: str

        :param value: The proxy
        :type value: Proxy
        """
        self.proxies[key] = value

    def __contains__(self, key):
        """Check if list contains proxy.

        :param key: The name of the proxy
        :type key: str

        :returns: Return true if proxy is in list
        :rtype: boolean
        """
        return key in self.proxies

    def __delitem__(self, key):
        """Remove a proxy from the list.

        :param name: The name of the proxy
        :type name: str
        """
        del self.proxies[key]

    def __iter__(self):
        """Return an iterator.

        :returns: Return list of Proxy items
        :rtype: list
        """
        return iter(self.proxies.values())

    def clear(self):
        """Clear the proxy list."""
        self.proxies.clear()

    def keys(self):
        """Return the proxy list keys.

        :returns: Return the porxy lists keys
        :rtype: list
        """
        return self.proxies.keys()

    def get(self, key, default=None):
        """Return a proxy by key.

        :returns: Return the porxy lists keys
        :rtype: Proxy or None if no matching key was found
        """
        return self.proxies.get(key, default)

    def items(self):
        """Return all proxies.

        :returns: Return the porxy items
        :rtype: list
        """
        return self.proxies.items()

    def aquire(self):
        """Run the aquire command and append new proxies."""
        p = subprocess.Popen(self.command, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        lines = p.stdout.readlines()
        retval = p.wait()
        proxies = {}

        for line in lines:
            ip = line.strip().split(':')[0]
            port = int(line.strip().split(':')[1])

            proxy = self.Protocol(ip, port)
            key = str(proxy)
            if key not in self.proxies.keys():
                self.proxies[key] = proxy
                proxies[key] = proxy

        self.updated = datetime.now()

        return proxies
