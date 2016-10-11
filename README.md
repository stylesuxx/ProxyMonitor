## Running the tests
From the root directory of the project run:

    nosetests --cover-branches --with-coverage --cover-package=ProxyDaemon

Coverage will report multiple missings in *Proxy.py* those are the validation
tests. Unfortunately this is hard to test since it would need permanent proxies
to test against. If anyone if willing to provide those, I will gladly add them
to the test cases.
