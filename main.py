import pyvista as pv
from pyvista import examples
from pyvista.trame.ui import plotter_ui
from trame.app import get_server
from trame.ui.vuetify import SinglePageWithDrawerLayout,VAppLayout
from trame.widgets import vuetify
import numpy as np
import os
# ----find Parameters----
path2DData='./data/2D'
config_dic=dict(enumerate(sorted(os.listdir(path2DData), key= lambda x:-1 if x=='Reference' else 1)))

timesteps= len(os.listdir(path2DData + '/' + config_dic[0]))


pv.OFF_SCREEN = True

server = get_server()
server.client_type='vue2'
state, ctrl = server.state, server.controller

state['first_graph_index']=0
state['second_graph_index']=0
state['timestep']=0

server.hot_reload = True

def getFilePath(i,timestep):
    return path2DData+'/{}/mesh_t_{}.vti'.format(config_dic[i],timestep)


p=pv.Plotter(shape=(1,2))


def plot_graph(timestep, graph_index,subplot_index, **kwargs):
  #idk why it is recieved as a string....
  p.subplot(0,subplot_index)
  p.add_text(config_dic[graph_index], font_size=16,name='title')

  grid = pv.read(getFilePath( graph_index,timestep))
  terrain = grid.warp_by_scalar()
  p.add_mesh(
      terrain,
      name='terrain')




#initial plot
plot_graph(0,0,0)
plot_graph(0,0,1)
p.link_views()


@state.change("timestep","first_graph_index")
def onFirstGraphChange(timestep, first_graph_index,**kwargs):
  plot_graph(int(timestep),int(first_graph_index),0)
  view.update()

@state.change("timestep","second_graph_index")
def onFirstGraphChange(timestep, second_graph_index,**kwargs):
  plot_graph(int(timestep),int(second_graph_index),1)
  view.update()


with SinglePageWithDrawerLayout(server) as layout:
    layout.title.set_text("Visual Comparison")
    with layout.content:
        with vuetify.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ):
            # Use PyVista UI template for Plotters
            view = plotter_ui(p)
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
                    v_model=("timestep",),
                )
                with vuetify.VRadioGroup(
                        v_model=("second_graph_index",),
                ):
                    for key, value in config_dic.items():
                        vuetify.VRadio(label=value, value=key)

server.start()