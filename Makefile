CC=gcc
CFLAGS+=-Wall -std=c99 -g -Wno-unused-function
CFLAGS+=$(shell pkg-config --cflags libsystemd)
LDFLAGS+=$(shell pkg-config --libs libsystemd)
EXEC=barctl

$(EXEC): barctl.c
	$(CC) $(CFLAGS) barctl.c -o $(EXEC) $(LDFLAGS)

clean:
	rm -f $(EXEC)
