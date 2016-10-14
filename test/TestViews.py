from ProxyDaemon import (ProxyView, LogView, MainView)
from datetime import datetime
import unittest
import curses

class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

class MonitorMock:
    protocol = Bunch(name='Http')
    proxy_list = Bunch(Protocol=protocol)

    def __init__(self, stats_provider, log_provider):
        self.get_stats = stats_provider
        self.get_log = log_provider

    def get_log(self):
        return self.get_log()

    def get_log(self):
        return self.get_stats()

class TestHttpProxy(unittest.TestCase):
    def setUp(self):
        self.stdscr = curses.initscr()
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()

    def tearDown(self):
        self.stdscr.clear()
        curses.endwin()

    def test_proxy_view(self):
        def provider():
            return {
                'total': 10,
                'discovered': 11,
                'ready': 12,
                'recheck': 13,
                'used': 14,
                'workers': {
                    'discovery': {
                        'count': 15,
                        'active': 0
                    },
                    'recheck': {
                        'count': 16,
                        'active': 0
                    }
                },
                'state': {
                    'acquiring': False,
                    'cleaning': False
                }
            }

        view = ProxyView(0, 0, 'Http', provider)
        view.refresh()

    def stats_provider(self):
        return {
            'total': 10,
            'discovered': 11,
            'ready': 12,
            'recheck': 13,
            'used': 14,
            'workers': {
                'discovery': {
                    'count': 15,
                    'active': 15
                },
                'recheck': {
                    'count': 16,
                    'active': 16
                }
            },
            'state': {
                'acquiring': True,
                'cleaning': True
            }
        }

    def log_provider(self):
        return([
            {
                'date': datetime.now(),
                'message': 'Some message to log',
                'source': 'Http'
            }
        ])

    def test_proxy_view_active(self):
        view = ProxyView(0, 0, 'Http', self.stats_provider)
        view.refresh()

    def test_log_view(self):
        sources = [self.log_provider]
        view = LogView(0, 0, 'Http', sources)
        view.refresh(20, 20)


    def test_main_view(self):
        """
        monitor.proxy_list.Protocol.name,
        monitor.get_stats
        monitor.get_log
        """
        monitor = MonitorMock(self.stats_provider, self.log_provider)
        view = MainView([monitor])
        view.refresh()
        view.stop()
