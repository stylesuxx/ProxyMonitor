"""Proxy list base class."""
from datetime import datetime
import subprocess


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
        """Run the aquire command and append new proxies.

        Returns an item as soon as it is found, technically this can be
        connected to a streaming source without the need to ever disconnect.
        """
        p = subprocess.Popen(self.command, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        lines = p.stdout.readlines()
        retval = p.wait()

        for line in lines:
            ip = line.strip().split(':')[0]
            port = int(line.strip().split(':')[1])

            proxy = self.Protocol(ip, port)
            key = str(proxy)

            """LOCK START"""

            if key not in self.proxies.keys():
                self.proxies[key] = proxy
                """LOCK END"""
                yield proxy



        self.updated = datetime.now()
