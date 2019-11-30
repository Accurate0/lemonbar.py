#define _GNU_SOURCE
#include <stdbool.h>
#include <stdio.h>
#include <linux/limits.h>
#include <stdlib.h>
#include <getopt.h>
#include <string.h>
#include <sys/stat.h>

#include <systemd/sd-bus.h>

// add 'daemon-reload' with fork and execvp
// TODO: Module commands


#define STOP_MASK           1
#define STATUS_MASK         ((STOP_MASK) << 1)
#define UNLOAD_MASK         ((STATUS_MASK) << 1)
#define LOAD_MASK           ((UNLOAD_MASK) << 1)
#define REFRESH_MASK        ((LOAD_MASK) << 1)

#define PATH                "/com/yeet/bard"
#define SERVICE             "com.yeet.bard"

#define MANAGER_PATH        PATH"/Manager"
#define MANAGER_INTERFACE   SERVICE".Manager"

#define STOP_COMMAND        "stop"
#define REFRESH_COMMAND     "refresh"
#define STATUS_COMMAND      "status"
#define LOAD_COMMAND        "load"
#define UNLOAD_COMMAND      "unload"

#define VERSION             "0.0"

static void usage(const char *prog)
{
    printf("%s [options] [action || module] [action arguments] [module options]\n\n", prog);
    puts("options:");
    puts("   -h, --help            show help");
    puts("   -v, --verbose         verbose");
    puts("   --version             show version and exit");
    puts("");
    puts("actions:");
    puts("   -l, --load            load a bar module, requires a path argument");
    puts("   -u, --unload          unload a bar module, requires a dbus name argument");
    puts("   -s, --stop            stop the bar");
    puts("   -r, --refresh         refresh bar contents");
    puts("   --status              print current bar status");
    puts("");
    puts("module name can be given as DBus name or as last part");
    puts("module options:");
    puts("   -r, --refresh");
    puts("   --arbitrary-command");
    puts("  can be arbitrary method name, that will be invoked on given module");
}

// DBus Connection
static sd_bus* connect_to_bus(void)
{
    sd_bus *bus = NULL;
    int r = sd_bus_open_user(&bus);
    if(r < 0) {
        fprintf(stderr, "Failed to connect to user bus: %s\n", strerror(-r));
    }

    return bus;
}

static sd_bus_message* call_method(sd_bus *bus,
                                    const char *path,
                                    const char *interface,
                                    const char *method,
                                    const char *types, ...)
{
    if(bus == NULL) return NULL;
    sd_bus_error error = SD_BUS_ERROR_NULL;
    sd_bus_message *m = NULL;
    int r = sd_bus_call_method(bus,
                              SERVICE,
                              path,
                              interface,
                              method,
                              &error,
                              &m,
                              types);
    if(r < 0) {
        fprintf(stderr, "Failed to issue method call: %s\n", error.message);
        sd_bus_message_unref(m);
        m = NULL;
    }

    sd_bus_error_free(&error);
    return m;
}

static void parse_resp_as_str(sd_bus_message *m)
{
    const char *msg;
    int r = sd_bus_message_read(m, "s", &msg);
    if(r < 0) {
        fprintf(stderr, "Failed to parse response: %s\n", strerror(-r));
    } else {
        printf("%s\n", msg);
    }

    sd_bus_message_unref(m);
}

static bool check_error(int r, sd_bus_error error, sd_bus_message *msg)
{
    bool err = false;
    if(r < 0) {
        fprintf(stderr, "Failed to issue method call: %s\n", error.message);
        sd_bus_message_unref(msg);
        err = true;
    }

    return err;
}

// Verbose
static int verbose_flag = 0;
static int v_printf(const char *f, ...)
{
    int len = 0;
    if(verbose_flag) {
        char buff[BUFSIZ];
        va_list vl;
        va_start(vl, f);
        vsprintf(buff, f, vl);
        va_end(vl);

        len = fprintf(stderr, "%s", buff);
    }

    return len;
}

static bool file_exists(const char *filename)
{
    struct stat buf;
    return stat(filename, &buf) == 0;
}

int main(int argc, char *argv[])
{
    int c;
    int ret = 0;
    int version_flag = 0;
    int status_flag = 0;
    char *load_path = NULL;
    char *unload_name = NULL;
    int mask = 0;

    const struct option long_opts[] = {
        {"help", no_argument, NULL, 'h'},
        {"verbose", no_argument, NULL, 'v'},
        {"version", no_argument, &version_flag, 1},
        {"load", required_argument, NULL, 'l'},
        {"unload", required_argument, NULL, 'u'},
        {"stop", no_argument, NULL, 's'},
        {"refresh", no_argument, NULL, 'r'},
        {"status", no_argument, &status_flag, 1},
        {0, 0, 0, 0}
    };

    while((c = getopt_long(argc, argv, "hvl:u:sr", long_opts, NULL)) != -1) {
        switch(c) {
            case 0:
                break;

            case 'h':
                usage(argv[0]);
                break;

            case 'v':
                verbose_flag = 1;
                break;

            case 'l':
                mask |= LOAD_MASK;
                load_path = optarg;
                break;

            case 'u':
                mask |= UNLOAD_MASK;
                unload_name = optarg;
                break;

            case 's':
                mask |= STOP_MASK;
                break;

            case 'r':
                mask |= REFRESH_MASK;
                break;

            default:
                ret = 1;
        }
    }

    if(version_flag) {
        printf("%s: %s\n", argv[0], VERSION);
    }

    sd_bus *bus = connect_to_bus();
    sd_bus_error error = SD_BUS_ERROR_NULL;
    sd_bus_message *m = NULL;
    int r = 0;

    if(status_flag) {
        r = sd_bus_call_method(bus,
                               SERVICE,
                               PATH,
                               MANAGER_INTERFACE,
                               STATUS_COMMAND,
                               &error,
                               &m,
                               NULL);
        if(!check_error(r, error, m)) {
            parse_resp_as_str(m);
        }
    }

    if(mask & LOAD_MASK) {
        if(file_exists(load_path)) {
            char path[PATH_MAX + 1];
            realpath(load_path, path);
            r = sd_bus_call_method(bus,
                                SERVICE,
                                PATH,
                                MANAGER_INTERFACE,
                                LOAD_COMMAND,
                                &error,
                                &m,
                                "s",
                                path);
            check_error(r, error, m);
        }
    }

    if(mask & UNLOAD_MASK) {
        r = sd_bus_call_method(bus,
                            SERVICE,
                            PATH,
                            MANAGER_INTERFACE,
                            UNLOAD_COMMAND,
                            &error,
                            &m,
                            "s",
                            unload_name);
        check_error(r, error, m);
    }

    if(mask & REFRESH_MASK) {
        r = sd_bus_call_method(bus,
                            SERVICE,
                            PATH,
                            MANAGER_INTERFACE,
                            REFRESH_COMMAND,
                            &error,
                            &m,
                            NULL);
        check_error(r, error, m);
    }

    if(mask & STOP_MASK) {
        r = sd_bus_call_method(bus,
                            SERVICE,
                            PATH,
                            MANAGER_INTERFACE,
                            STOP_COMMAND,
                            &error,
                            &m,
                            NULL);
        check_error(r, error, m);
    }

    sd_bus_unref(bus);

    return ret ? EXIT_FAILURE : EXIT_SUCCESS;
}
