# bard and barctl

## usage

### bard

```c
$ bard.py -h
usage: bard.py [-h] [--log ] config.ini

positional arguments:
  config.ini  config file to use to run the bar

optional arguments:
  -h, --help  show this help message and exit
  --log []    info, debug, warning, error, critical
```

### barctl

```c
barctl [options] [action] [action arguments] [module action]

options:
   -h, --help            show help
   -v, --verbose         verbose
   --version             show version and exit

actions:
   -l, --load            load a bar module, requires a path argument
   -u, --unload          unload a bar module, requires a dbus name argument
   -s, --stop            stop the bar
   -r, --refresh         refresh bar contents
   --list                list currently loaded modules
   --status              print current bar status

module actions:
   module specific calls are done arbitrarily
   eg: barctl [module name] [method name]
   note: '-' replaced with '_' in method call
```
