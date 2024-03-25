from trame.app import get_server
from trame.ui.vuetify3 import SinglePageWithDrawerLayout
from trame.ui.router import RouterViewLayout
from trame.widgets import router, vuetify3 as vuetify

server = get_server()
server.client_type = "vue3"
state, ctrl = server.state, server.controller
with RouterViewLayout(server, "/"):
    with vuetify.VCard():
        vuetify.VCardTitle("This is home")

with RouterViewLayout(server, "/foo"):
    with vuetify.VCard():
        vuetify.VCardTitle("This is foo")

with RouterViewLayout(server, "/bar/:id"):
    with vuetify.VList():
        vuetify.VListItem("Bar {{ $route.params.id }} item 1")
        vuetify.VListItem("Bar {{ $route.params.id }} item 2")
        vuetify.VListItem("Bar {{ $route.params.id }} item 3")

with SinglePageWithDrawerLayout(server) as layout:
    with layout.toolbar:
        vuetify.VBtn("Home", to="/")
        vuetify.VBtn("Foo", to="/foo")
        vuetify.VBtn("Bar 1", to="/bar/1")
        vuetify.VBtn("Bar 2", to="/bar/2")
        vuetify.VBtn("Bar 3", to="/bar/3")

    with layout.content:
        router.RouterView()
if __name__ == "__main__":
    server.start()