import pyvista as pv
from pyvista import examples
from pyvista.trame.ui import plotter_ui
from trame.app import get_server
from trame.ui.vuetify import SinglePageWithDrawerLayout, VAppLayout
from trame.widgets import vuetify
import numpy as np
import os

# ----find Parameters----
path2DData = './data/2D'
config_dic = dict(enumerate(sorted(os.listdir(path2DData), key=lambda x: -1 if x == 'Reference' else 1)))

timesteps = len(os.listdir(path2DData + '/' + config_dic[0]))

pv.OFF_SCREEN = True

server = get_server()
server.client_type = 'vue2'
state, ctrl = server.state, server.controller

state['first_graph_index'] = 0
state['second_graph_index'] = 0
state['timestep'] = 0

server.hot_reload = True


def getFilePath(i, timestep):
    return path2DData + '/{}/mesh_t_{}.vti'.format(config_dic[i], timestep)


p = pv.Plotter(shape=(1, 2))


def plot_graph(timestep, graph_index, subplot_index, **kwargs):
    # idk why it is recieved as a string....
    p.subplot(0, subplot_index)
    p.add_text(config_dic[graph_index], font_size=16, name='title')

    grid = pv.read(getFilePath(graph_index, timestep))
    terrain = grid.warp_by_scalar()
    p.add_mesh(
        terrain,
        name='terrain')


def show_contour(subplot_index):
    p.subplot(0, subplot_index)
    for mesh in p.meshes:
        if isinstance(mesh,pv.core.pointset.StructuredGrid):
            contour = mesh.contour()
            p.add_mesh(contour, color="white", line_width=5, name="contour")
            return


def remove_contour(subplot_index):
    p.subplot(0, subplot_index)
    if 'contour' in p.actors:
        p.remove_actor(p.actors['contour'])
        return


# initial plot
plot_graph(0, 0, 0)
plot_graph(0, 0, 1)
p.link_views()

@state.change("enable_contour","timestep","first_graph_index","second_graph_index")
def on_state_change(**kwargs):
    view.update()

@state.change("enable_contour","timestep" ,"first_graph_index")
def on_first_graph_contour_change(enable_contour, **kwargs):
    if enable_contour:
        show_contour(0)

        return
    remove_contour(0)




@state.change("enable_contour","timestep","second_graph_index")
def on_second_graph_contour_change(enable_contour, **kwargs):
    if enable_contour:
        show_contour(1)
        return
    remove_contour(1)

@state.change("timestep", "first_graph_index")
def on_first_graph_change(timestep, first_graph_index, **kwargs):

    plot_graph(int(timestep), int(first_graph_index), 0)
    p.subplot(0, 0)
    p.add_text('timestep:{}'.format(timestep), position='lower_left', font_size=6, name="timestep")


@state.change("timestep", "second_graph_index")
def on_second_graph_change(timestep, second_graph_index, **kwargs):
    plot_graph(int(timestep), int(second_graph_index), 1)






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
                vuetify.VCheckbox(
                    label="Show Contour Plots",
                    dense=True,
                    v_model=("enable_contour", False)
                )
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
