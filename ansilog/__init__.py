#--------------------------------------------------------------------
# ansilog.py: Smart and colorful logging, output, and basic terminal control.
#
# Author: Lain Supe (lainproliant)
# Date: Feb 1 2018
#
# `screen.getch()` courtesy of https://code.activestate.com/recipes/134892/
# `screen.set_echo()` courtesy of https://blog.hartwork.org/?p=1498
#--------------------------------------------------------------------
__all__ = [
    'seq', 'attr', 'clrscr', 'clreol', 'reset', 'TagFactory', 'default',
    'bright', 'dim', 'underscore', 'blink', 'reverse', 'hidden', 'fraktur',
    'fg_color', 'bold_color', 'bg_color', 'fg', 'bg', 'cursor', 'screen',
    'Formatter', 'StreamHandler', 'handler', 'print'
]

#--------------------------------------------------------------------
import atexit
import logging
import os
import re
import shutil
import sys
import termios

#--------------------------------------------------------------------
# Environment variable that, when exists, should prevent colorized
# output completely.  See https://no-color.org for more info.
NO_COLOR = 'NO_COLOR' in os.environ

#--------------------------------------------------------------------
class Node:
    def __init__(self):
        self.content = []

    @staticmethod
    def list(*content):
        node = Node()
        for c in content:
            node.add(c)
        return node

    def add(self, *nodes):
        self.content.extend(nodes)

    def to_file(self):
        sb = []
        for element in self.content:
            if isinstance(element, Node):
                sb.append(element.to_file())
            else:
                sb.append(element)
        return ''.join(sb)

    def to_screen(self, stack = None):
        sb = []
        if stack is None:
            stack = []
        for element in self.content:
            if isinstance(element, Node):
                sb.append(element.to_screen(stack))
            else:
                sb.append(element)
        return ''.join([str(s) for s in sb])

    def __str__(self):
        return self.to_screen()

    def __add__(self, rhs):
        if isinstance(rhs, Node):
            return Node.list(self, rhs)
        else:
            return Node.list(self, Text(rhs))

#--------------------------------------------------------------------
class Text(Node):
    def __init__(self, text):
        super().__init__()
        self.text = str(text)

    def to_screen(self, stack = None):
        return self.text

    def to_file(self):
        return self.text

    def add(self, *nodes):
        raise NotImplementedError()

#--------------------------------------------------------------------
class Tag(Node):
    def __init__(self, before = None, after = None):
        super().__init__()
        self.before = before or Text('')
        self.after = after or Text('')

    def to_screen(self, stack = None):
        sb = []
        if not stack:
            stack = []
        sb.append(self.before)
        stack.append(self.before)
        sb.append(super().to_screen(stack))
        stack.pop()
        sb.append(self.after)
        sb.extend(stack)
        return ''.join([str(s) for s in sb])

#--------------------------------------------------------------------
class Sequence(Node):
    def __init__(self, seq):
        self.seq = seq

    def to_screen(self, stack = None):
        return self.seq

    def add(self, *nodes):
        raise NotImplementedError()

#--------------------------------------------------------------------
class LogRecord(logging.LogRecord):
    """
        An override of LogRecord allowing the message to be returned
        as an ansilog.Node.
    """
    def getMessage(self):
        msg = None
        if not isinstance(self.msg, Node):
            msg = super().getMessage()
        else:
            msg = self.msg
        return msg

#--------------------------------------------------------------------
logging.setLogRecordFactory(LogRecord)

#--------------------------------------------------------------------
seq = lambda *parts: Sequence(''.join(["\033[", *(str(p) for p in parts)]))
attr = lambda *parts: Sequence(''.join(["\033[", ';'.join(str(p) for p in parts), 'm']))
clrscr = Node.list(seq('2J'), seq('0;0H'))
clreol = seq('K')
reset = attr(0)

#--------------------------------------------------------------------
class TagFactory:
    def __init__(self, before = None, after = None):
        self.before = before or ''
        self.after = after or reset

    def __call__(self, *content):
        tag = Tag(self.before, self.after)
        tag.add(*content)
        return tag

    def __str__(self):
        return str(self.before)

#--------------------------------------------------------------------
default = TagFactory() if NO_COLOR else TagFactory(attr(0))
bright = TagFactory() if NO_COLOR else TagFactory(attr(1))
dim = TagFactory() if NO_COLOR else TagFactory(attr(2))
underscore = TagFactory() if NO_COLOR else TagFactory(attr(4))
blink = TagFactory() if NO_COLOR else TagFactory(attr(5))
reverse = TagFactory() if NO_COLOR else TagFactory(attr(7))
hidden = TagFactory() if NO_COLOR else TagFactory(attr(8))
fraktur = TagFactory() if NO_COLOR else TagFactory(attr(20))

#--------------------------------------------------------------------
fg_color = lambda x: TagFactory() if NO_COLOR else TagFactory(attr(30 + x))
bold_color = lambda x: TagFactory() if NO_COLOR else TagFactory(attr(1, 30 + x))
bg_color = lambda x: TagFactory() if NO_COLOR else TagFactory(attr(40 + x))

colors = ('black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white')

class fg:
    class bright:
        pass
class bg:
    pass

for x, color in enumerate(colors):
    setattr(fg, color, fg_color(x))
    setattr(fg.bright, color, bold_color(x))
    setattr(bg, color, bg_color(x))

#--------------------------------------------------------------------
class cursor:
    hide = lambda: seq('?25l')
    show = lambda: seq('?25h')
    save = lambda: seq('s')
    restore = lambda: seq('u')
    move = lambda x, y: seq(x, ';', y, 'H')
    up = lambda n: seq(n, 'A')
    down = lambda n: seq(n, 'B')
    right = lambda n: seq(n, 'C')
    left = lambda n: seq(n, 'D')

#--------------------------------------------------------------------
class screen:
    size = lambda: shutil.get_terminal_size((80, 20))
    clear = clrscr

#--------------------------------------------------------------------
class Formatter(logging.Formatter):
    def __init__(self, stream):
        super().__init__(self)
        self.stream = stream
        self.level_colors = {
            logging.CRITICAL:   lambda x: bg.red(fg.bright.white(x)),
            logging.ERROR:      fg.bright.red,
            logging.WARNING:    fg.bright.yellow,
            logging.DEBUG:      fg.blue
        }
    
    def get_file_format(self, record):
        return Text("{asctime} [{levelname}] {message}")
        
    def get_screen_format(self, record):
        if record.levelno != logging.INFO:
            return Node.list(
                    self.level_colors.get(record.levelno, default)("[{levelname}]"),
                    " {message}")
        else:
            return "{message}"

    def formatMessage(self, record):
        if self.stream.isatty():
            return str(self.get_screen_format(record)).format(**record.__dict__)
        else:
            output_dict = {}
            for key, value in record.__dict__.items():
                if isinstance(value, Node):
                    output_dict[key] = value.to_file()
                else:
                    output_dict[key] = value

            return self.get_file_format(record).to_file().format(**output_dict)

    def usesTime(self):
        return True
        
#--------------------------------------------------------------------
class StreamHandler(logging.StreamHandler):
    def __init__(self, stream = None):
        super().__init__(stream)
        self.setFormatter(Formatter(self.stream))

#--------------------------------------------------------------------
handler = StreamHandler()
handler.setLevel(logging.INFO)

#--------------------------------------------------------------------
def getLogger(*args, **kwargs):
    log = logging.getLogger(*args, **kwargs)
    log.removeHandler(handler)
    log.addHandler(handler)
    log.setLevel(logging.INFO)
    return log

#--------------------------------------------------------------------
def print(*values, sep = ' ', end = '\n', file = sys.stdout, flush = False):
    if not file.isatty():
        values = [v.to_file() if isinstance(v, Node) else v for v in values]
    __builtins__['print'](*values, sep = sep, end = end, file = file, flush = flush)

#--------------------------------------------------------------------
class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()

#--------------------------------------------------------------------
class _GetchUnix:
    def __init__(self):
        import tty, sys, termios # import termios now or else you'll get the Unix version on the Mac

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

#--------------------------------------------------------------------
class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()

#--------------------------------------------------------------------
class screen:
    size = lambda: shutil.get_terminal_size((80, 20))
    clear = clrscr
    getch = _Getch()
    _atexit_registered = False
    
    @staticmethod
    def echo_off():
        fd = sys.stdin.fileno()
        screen.set_echo(fd, False)
        if not screen._atexit_registered:
            screen._atexit_registered = True
            atexit.register(screen.echo_on)

    @staticmethod
    def echo_on():
        fd = sys.stdin.fileno()
        screen.set_echo(fd, True)

    @staticmethod
    def set_echo(fd, enabled):
        (iflag, oflag, cflag, lflag, ispeed, ospeed, cc) = termios.tcgetattr(fd)
        if enabled:
           lflag |= termios.ECHO
        else:
           lflag &= ~termios.ECHO
        new_attr = [iflag, oflag, cflag, lflag, ispeed, ospeed, cc]
        termios.tcsetattr(fd, termios.TCSANOW, new_attr)

