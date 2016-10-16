# Proxy Daemon Monitor
> Monitor your available proxies.

This application monitors your proxies, checks if they are on-line, rotates them and provides a Dbus interface for other application to retrieve one or more proxies.

## Features
Following proxy types are supported:

* http
* https
* anonymous http
* anonymous https

This means you they have a validator function and you can use them out of the box. It is easy to add other proxy types, simply subtype the abstract proxy class and implement a validator method. If you do so, feel free to submit a PR with your new proxy validator.

## Usage
You can use this module either as a module to extend your application, or as a stand alone daemon.

## Prerequisites
For this daemon to work properly you will need a system that supports Dbus. This means some kind of Linux. Might also work on Mac when the appropriate libs are installed validation Brew, if anyone can confirm this, please feel free to drop me a line in the issues section.

## Running the tests
From the root directory of the project run:

    nosetests --cover-branches --with-coverage --cover-package=ProxyDaemon

Coverage will report multiple missings in *Proxy.py* those are the validation
tests. Unfortunately this is hard to test since it would need permanent proxies
to test against. If anyone if willing to provide those, I will gladly add them
to the test cases.

In Monitor.py multiple lines show as exit, this is expected when the loop is
stopped.

## Contributing
Contribution is very welcome, no matter if documentation, typos or actual code. Before starting a big new feature please check back with be before hand in the issues section.

Make your PR's against the develop branch.
