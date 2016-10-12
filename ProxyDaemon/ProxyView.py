import curses


class ProxyView():
    def __init__(self, y, x, header, source):
        self.y = y
        self.x = x
        self.header = header
        self.source = source

    def refresh(self):
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
