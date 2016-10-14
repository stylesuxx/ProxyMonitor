"""Ncurses views and related functionality."""
import curses


class MainView():
    """The main view for the proxy monitors."""

    def __init__(self, monitors):
        """
        Inititialize the main view.

        :param monitors: List of monitors to geneate views for.
        :type monitors: list
        """
        self.monitors = monitors
        self.stdscr = curses.initscr()

        top_offset = 1
        box_offset = 7
        counter = 0

        logs = []
        self.proxy_views = []
        for monitor in monitors:
            view = ProxyView(top_offset + box_offset * counter, 1,
                             monitor.proxy_list.Protocol.name,
                             monitor.get_stats)

            logs.append(monitor.get_log)

            self.proxy_views.append(view)
            counter += 1

        self.log_view = LogView(1, 42, 'Log', logs)

        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()

        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    def refresh(self):
        """Refresh all views."""
        self.stdscr.bkgd(curses.color_pair(1))
        self.stdscr.border()
        self.stdscr.addstr(0, 2,
                           ' Proxy Daemon Monitor ',
                           curses.color_pair(2))
        self.stdscr.refresh()

        for view in self.proxy_views:
            view.refresh()

        maxY, maxX = self.stdscr.getmaxyx()
        self.log_view.refresh(maxY - 2, maxX - 43)

    def stop(self):
        """Reset the console back to its original state."""
        self.stdscr.clear()
        curses.endwin()


class LogView():
    """Log View.

    Display log messages from all the monitors.
    """

    def __init__(self, y, x, header, sources):
        """Inititialize the proxy view.

        :param y: The y position
        :type y: int

        :param x: The x position
        :type x: int

        :param header: The title of the box
        :type header: str

        :param sources: Sources for the log messages
        :type sources: list
        """
        self.y = y
        self.x = x
        self.header = header
        self.sources = sources

        self.log = []

    def refresh(self, height, width):
        """
        Refresh the view.

        Height and width need to be passed when refreshing this view, since
        it should occupy all available space.

        :param height: The height
        :type height: int

        :param width: The width
        :type x: int
        """
        box = curses.newwin(height, width, self.y, self.x)
        box.bkgd(curses.color_pair(1))
        box.box()
        box.addstr(0, 2, ' %s ' % self.header)

        log_new = []
        for source in self.sources:
            log_new += source()

        log_new.sort(key=lambda item: item['date'])
        self.log += log_new

        count = height - 2
        items = self.log
        if(len(items) > count):
            items = items[count * -1]

        counter = 0
        for i in range(0, len(items)):
            item = items[i]
            box.addstr(1 + i, 2, '%s [%s] %s' %
                       (item['date'].strftime('%H:%M:%S'),
                        item['source'],
                        item['message']))

        box.refresh()


class ProxyView():
    """Proxy View.

    Displays statistics about a specific proxy type.
    """

    def __init__(self, y, x, header, source):
        """Inititialize the proxy view.

        :param y: The y position
        :type y: int

        :param x: The x position
        :type x: int

        :param header: The title of the box
        :type header: str

        :param source: Source for the statistics
        :type source: method
        """
        self.y = y
        self.x = x
        self.header = header
        self.source = source

    def refresh(self):
        """Refresh the view."""
        stats = self.source()

        self.box = curses.newwin(4, 41, self.y, self.x)
        self.box.bkgd(curses.color_pair(1))
        self.box.box()
        self.box.addstr(0, 2, ' %s ' % self.header)

        self.worker_box = curses.newwin(4, 41, self.y + 3, self.x)
        self.worker_box.bkgd(curses.color_pair(1))
        self.worker_box.box()
        self.worker_box.addstr(0, 16, ' Workers ')

        self.box.addstr(1, 2, 'Curr. | Disc. | Ready | ReCh. | Used')
        self.box.addstr(2, 2, '% 5i | % 5i | % 5i | % 5i | % 5i' %
                        (stats['total'], stats['discovered'], stats['ready'],
                         stats['recheck'], stats['used']))

        color = curses.color_pair(1)
        if stats['workers']['discovery']['active'] > 0:
            color = curses.color_pair(2)

        self.worker_box.addstr(1, 4, 'Discovery', color)
        self.worker_box.addstr(2, 8, '/', color)
        self.worker_box.addstr(2, 3,
                               ('% 5i' %
                                stats['workers']['discovery']['active']),
                               color)
        self.worker_box.addstr(2, 9,
                               ('%i' % stats['workers']['discovery']['count']),
                               color)

        color = curses.color_pair(1)
        if stats['workers']['recheck']['active'] > 0:
            color = curses.color_pair(2)

        r_offset = 15
        self.worker_box.addstr(1, r_offset + 2, 'Recheck', color)
        self.worker_box.addstr(2, r_offset + 5, '/', color)
        self.worker_box.addstr(2, r_offset,
                               '% 5i' % stats['workers']['recheck']['active'],
                               color)
        self.worker_box.addstr(2, r_offset + 6,
                               '%i' % stats['workers']['recheck']['count'],
                               color)

        a_offset = 27
        self.worker_box.addstr(1, a_offset + 2, 'Acquire')
        if stats['state']['acquiring']:
            self.worker_box.addstr(1, a_offset + 2, 'Acquire',
                                   curses.color_pair(2))

        c_offset = 27
        self.worker_box.addstr(2, a_offset + 2, 'Cleanup')
        if stats['state']['cleaning']:
            self.worker_box.addstr(2, a_offset + 2, 'Cleanup',
                                   curses.color_pair(2))

        self.box.refresh()
        self.worker_box.refresh()
