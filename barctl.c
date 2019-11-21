#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

#include <systemd/sd-bus.h>

int main(int argc, char const *argv[])
{
    sd_bus_error error = SD_BUS_ERROR_NULL;
    sd_bus_message *m = NULL;
    sd_bus *bus = NULL;
    const char *path;
    int r;

    r = sd_bus_open_user(&bus);
    if(r < 0) {
        fprintf(stderr, "Failed to connect to user bus: %s\n", strerror(-r));
        goto end;
    }

    r = sd_bus_call_method(bus,
                           "com.yeet.bard",
                           "/com/yeet/bard",
                           "com.yeet.bard.desktop",
                           "refresh",
                           &error,
                           &m,
                           NULL);

    if(r < 0) {
        fprintf(stderr, "Failed to issue method call: %s\n", error.message);
        goto end;
    }

    r = sd_bus_message_read(m, "s", &path);
    if(r < 0) {
        fprintf(stderr, "Failed to parse response: %s\n", strerror(-r));
        goto end;
    }

    printf("resp: %s\n", path);

end:
    sd_bus_error_free(&error);
    sd_bus_message_unref(m);
    sd_bus_unref(bus);

    return 0;
}
