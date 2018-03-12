# `\033[1;31m [ANSIlog] \033[0m`: Utilities for colorful output, logging, and
# basic terminal control.

`ansilog` is a CLI-focused module that provides colorful output primitives and
basic terminal control.  It currently supports 16-color terminal escape
sequences, along with various ANSI control sequences, attributes, and some
extra terminal control features.  It also offers `ansilog.StreamHandler`, which
can be added to loggers to enable colorized log levels and other colorized
output.  `ansilog` is smart enough to know when it is writing to a `tty` or a
file, and will strip all ANSI sequences before writing to files.

Colors and attributes are wrapped in a convenient tag interface, with the
`ansilog.print()` function and `ansilog.StreamHandler` being able to convert
these tags to output strings and strip ANSI sequences from them when necessary.

The tags help automate the labor of resetting to terminal defaults (and
previous highlights) when switching between highlight modes.  You can include
any number of string-able objects in the tag factory function and they will
be concatenated.

ANSIlog respects the `NO_COLOR` environment variable in that all color and
format sequences will be ignored if it is set, however cursor escapes and
explicitly constructed escape sequences (ala `seq()`) will not be suppressed.

```
from ansilog import *
print('Welcome to the ', bright(fg.red('U'), fg.white('S'), fg.blue('A')), '!', sep = '')
```

For more precise control, you can output the colors and
attributes directly as well, but you must remember to reset afterwards.

```
from ansilog import *
print('Welcome to the ', bright, fg.red, 'U', fg.white, 'S', fg.blue, 'A', reset, '!', sep = '')
```

### License
ANSIlog is released under a 3 clause BSD license.  See LICENSE for more details.
