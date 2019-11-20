CC=gcc
CFLAGS+=-Wall -std=c99 -g
CFLAGS+=$(shell pkg-config --cflags dbus-1 dbus-glib-1 gio-2.0)
LDFLAGS+=$(shell pkg-config --libs dbus-1 dbus-glib-1 gio-2.0)
EXEC=barctl

$(EXEC): barctl.c
	$(CC) $(CFLAGS) barctl.c -o $(EXEC) $(LDFLAGS)

clean:
	rm -f $(EXEC)
