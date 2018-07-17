# Python Brainfuck interpreter

Just another small Brainfuck interpreter written in Python. It is able to evaluate inline BF script as well as read from file.

## Usage

### Standalone

```bash
$ ./bfi.py [OPTIONS] <file_name.bf>
```

#### Available options
```bash
--cell-size=NUM     Set single cell size in bits (default = 8)
--memory-dump       Show memory dump at the end of script execution
```

### Module

```python
from bfi import *

try:
    Brainfuck().eval("This comment will be ignored")
except BrainfuckException as e:
    print(str(e))
```

## Contributing

Did you find a bug or got an idea? Feel free to use the [issue tracker](//github.com/terenaa/python-brainfuck-interpreter/issues). Or make directly a [pull request](//github.com/terenaa/python-brainfuck-interpreter/pulls).

## Author & license

The code is written by Krzysztof Janda and is 100% FREE under MIT license.
