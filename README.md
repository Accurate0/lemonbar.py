# lemonbar.py

#### _**Anurag Singh**_

## Description

A wrapper around [lemonbar](https://github.com/LemonBoy/bar) which provides a system for loading and unloading modules over the DBus IPC.
Modules are written in python3, and are loaded at runtime, modules have the ability to define their own DBus interface which is exposed under the main DBus interface.

Uses python's logging module to provide both file logs, and logs to terminal to allow monitoring of modules, and the base system itself.

## Goals

* Eventual goal is to stop using lemonbar and to write a different frontend to display the bar.
* Add a better callback system for clickable portions

## Setup/Installation Requirements

### bard

* python>=3.8
* ewmh==0.1.6
* python-xlib==0.25
* pydbus==0.6.0
* PyGObject==3.34.0
* requests==2.22.0
* pyudev==0.21.0
* lemonbar

### barctl

* systemd

## Known Bugs

* Need to replace lemonbar with custom version
* Sometimes does not run properly with an IO error

## Usage

### bar

```c
usage: bar [-h] [--log [str]] [--disable-dbus] [--disable-clickable]
           [--log-file [str]] [-q]
           [str]

positional arguments:
  str                  config file to use to run the bar

optional arguments:
  -h, --help           show this help message and exit
  --log [str]          possible levels: debug, info, warning, error, critical
  --disable-dbus       disable exposing interface over dbus
  --disable-clickable  make the bar ignore mouse actions
  --log-file [str]     file to log to
  -q, --quiet          disable logging to terminal
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
