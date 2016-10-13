from ProxyDaemon import (ProxyView)
from datetime import datetime
import unittest
import curses

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

    def test_proxy_view_active(self):
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

        view = ProxyView(0, 0, 'Http', provider)
        view.refresh()
