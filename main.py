import pyvista as pv
from pyvista import examples
from pyvista.trame.ui import plotter_ui
from trame.app import get_server
from trame.ui.vuetify import SinglePageWithDrawerLayout,VAppLayout
from trame.widgets import vuetify
import numpy as np




pv.OFF_SCREEN = True

server = get_server()
server.client_type='vue2'
state, ctrl = server.state, server.controller


server.hot_reload = True


def getFilePath(timestep,i):
    return 'data/mesh_i_{}_t_{}.vti'.format(i,timestep)
# Create and structured surface
grid = pv.read(getFilePath(0,0))
terrain=grid.warp_by_scalar()

state['plotter']=pv.Plotter()
p=state['plotter']
print(p.shape)

p.add_mesh(
    terrain,
    name='terrain',
    scalars="Height",
    lighting=False,
    show_edges=True,
)


timesteps = 15

data_config={}
data_config[0] = {
    "title": "Reference",
}
data_config[1] = {
    "title": "Noise .01",
}
data_config[2] = {
    "title": "Noise .05",
}
data_config[3] = {
    "title": "Noise .1",
}


@state.change("timestep")
def slider_value_change(timestep, **kwargs):
  grid = pv.read(getFilePath(timestep, 0))
  terrain = grid.warp_by_scalar()
  state['plotter'].add_mesh(
      terrain,
      name='terrain')
  print(f"Slider is changing slider_value to {timestep}")

@state.change("show_second_graph")
def toggle_show_second_graph(show_second_graph, **kwargs):
  print("state change",show_second_graph)
  state['disable_second_grid_radio_buttons']= not show_second_graph
  if(show_second_graph):
      return




with SinglePageWithDrawerLayout(server) as layout:
    with layout.content:
        with vuetify.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ):
            # Use PyVista UI template for Plotters
            view = plotter_ui(p)
            print(view)
            ctrl.view_update = view.update
    with layout.drawer:
        with vuetify.VContainer(
                fluid=True,
                classes="d-flex flex-column p-2",
        ):
            with vuetify.VContainer(
                    fluid=True,
                    classes="d-flex flex-column p-2",
            ):
                vuetify.VSlider(
                    label="Timestep",
                    dense=True,
                    min=0,
                    max=timesteps - 1,
                    v_model=("timestep", 0),
                )
                vuetify.VCheckbox(label='Show Second Graph',v_model=('show_second_graph',False))
                with vuetify.VRadioGroup(
                        v_model=("second_graph_grid", next(iter(data_config))),
                        disabled=("disable_second_grid_radio_buttons",False)


                ):
                    for key, value in data_config.items():
                        vuetify.VRadio(label=value["title"], value=key)

server.start()