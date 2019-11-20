#include <stdbool.h>
#include <stdio.h>
#include <glib.h>
#include <dbus/dbus-glib.h>
#include <glib/gprintf.h>
#include <gio/gio.h>

int main(int argc, char const *argv[])
{
    GDBusProxy *proxy;
    GDBusConnection *conn;
    GError *error = NULL;

    conn = g_bus_get_sync(G_BUS_TYPE_SESSION, NULL, &error);
    proxy = g_dbus_proxy_new_sync(conn,
                                  G_DBUS_PROXY_FLAGS_NONE,
                                  NULL,
                                  "com.yeet.bard",
                                  "/com/yeet/bard",
                                  "com.yeet.bard",
                                  NULL,
                                  &error);

    g_assert_no_error(error);

    const gchar *str;
    GVariant *res = g_dbus_proxy_call_sync(proxy, "lmao", NULL, G_DBUS_CALL_FLAGS_NONE, -1, NULL, &error);
    g_assert_no_error(error);
    g_variant_get(res, "(&s)", &str);
    g_printf("Response: %s\n", str);

    return 0;
}
