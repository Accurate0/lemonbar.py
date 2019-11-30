# bard and barctl

## usage

### bard

```c
$ bard.py -h
usage: bard.py [-h] config.ini

positional arguments:
  config.ini  config file to use to run the bar

optional arguments:
  -h, --help  show this help message and exit
```

### barctl

```c
barctl [options] [action || module] [action arguments] [module options]

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

module name can be given as DBus name or as last part
module options:
   -r, --refresh
   --arbitrary-command
  can be arbitrary method name, that will be invoked on given module
```
