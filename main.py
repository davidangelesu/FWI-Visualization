import pyvista as pv
from pyvista import examples
from pyvista.trame.ui import plotter_ui
from trame.app import get_server
from trame.ui.vuetify import SinglePageWithDrawerLayout
from trame.widgets import vuetify
import numpy as np




pv.OFF_SCREEN = True

server = get_server()
server.client_type='vue2'
state, ctrl = server.state, server.controller

server.hot_reload = True


x = np.arange(-10, 10, 0.5)
y = np.arange(-10, 10, 0.5)
x, y = np.meshgrid(x, y)
r = np.sqrt(x**2 + y**2)
z = np.sin(r)

# Create and structured surface
grid = pv.StructuredGrid(x, y, z)
grid["Height"] = z.ravel()

p = pv.Plotter()
p.add_mesh(
    grid,
    scalars="Height",
    lighting=False,
    show_edges=True,
    clim=[-1, 1],
)


nframe = 15
phases = np.linspace(0, 2 * np.pi, nframe + 1)[:nframe]

@state.change("timestep")
def slider_value_change(timestep, **kwargs):
  phase=phases[timestep]
  z = np.sin(r + phase)
  grid.points[:, -1] = z.ravel()
  grid["Height"] = z.ravel()
  view.update()
  print(phase,timestep)
  print(f"Slider is changing slider_value to {timestep}")




with SinglePageWithDrawerLayout(server) as layout:
    with layout.toolbar:
        vuetify.VSpacer()
        vuetify.VCheckbox(
            label="Log Scale",
            v_model=("log_scale", False),
            hide_details=True,
            dense=True,
            outlined=True,
        )
        vuetify.VSlider(
            label="Timestep",
            dense=True,
            min=0,
            max=nframe-1,
            v_model=("timestep", 0),
        )
    with layout.content:
        with vuetify.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ):
            # Use PyVista UI template for Plotters
            view = plotter_ui(p)
            ctrl.view_update = view.update

server.start()