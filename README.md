# `thyming`

I couldn't find a timer that matched my needs, so I created my own. I don't exactly remember which ones I tried and what reservations I had but whatever.

## Install `thyming`

```sh
pip install thyming
```

```py
from thyming import Timer # duh
```

## How to use `thyming.Timer`

There are two ways to use it: the ordinary way and as a context manager.

### 1. The ordinary way

You can use it the ordinary way, by creating a timer and measuring time with it multiple times.

```py
t = Timer()
# do something here
t.measure() # measure time
# do something else
t.measure() # measure time again
# ...
t.stop() # timer stops
print(t.rtimes()) 
# [2.8563, 5.0682, 22.2241] # print recorded times rounded to n digits (4 by default)

# You can reuse the timer after stopping it
t.start()
# ...
t.stop()
print(t.rtimes()) 
# [5.516]
# previous recorded times are stored in t.prev__recorded _times
print(t.prev_times)
[[2.8563294369996584, 5.068209224999919, 22.224131080000006]]
```

### 2. The context manager way

(This is the magic of `__enter__` and `__exit__`.)

```py
with Timer() as t:
    # ...
    t.measure()
    # ...
    t.measure()
# you leave timer here
```

### Logging time

`Timer` accepts a logger function, which takes a string and returns nothing (it's of type `Callable[[str], None]`). Theoretically, this could be `lambda s: None` but obviously we want to squeeze something useful out of it, so it's better to supply a function but prints the string argument to some output, e.g.: `print` or `logging.info`, which is the default.

```py
import logging
logging.basicConfig(level=logging.INFO)
t = Timer().start()
print(t.logger) # <function info at 0x7f38ac8b99d0> # i.e. logging.info
print(t.logger == logging.info) # True
t = Timer().start()
sleep(1)
t.measure() # INFO:root:Elapsed time: 1.0011 seconds.
```

## Links

- [PyPi](https://pypi.org/project/thyming/0.1.0/)
