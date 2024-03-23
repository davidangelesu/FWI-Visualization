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
folders = sorted(os.listdir(path2DData), key=lambda x: -1 if x == 'Reference' else 1)

timesteps = len([filename for filename in os.listdir(path2DData + '/' + folders[0]) if 'material' not in filename])
print(timesteps)
pv.OFF_SCREEN = True

server = get_server()
server.client_type = 'vue2'
state, ctrl = server.state, server.controller

state['first_folder'] = folders[0]
state['second_folder'] = folders[0]
state['timestep'] = 0
state['plotMode']='displacement'

server.hot_reload = True


def get_file_path(folder, timestep):
    return path2DData + '/{}/mesh_t_{}.vti'.format(folder, timestep)


p = pv.Plotter(shape=(1, 2))


def plot_graph(timestep, folder, subplot_index, **kwargs):
    # idk why it is recieved as a string....
    p.subplot(0, subplot_index)
    p.add_text(folder, font_size=16, name='title')

    grid = pv.read(get_file_path(folder, timestep))
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
plot_graph(0, folders[0], 0)
plot_graph(0,folders[0], 1)
p.link_views()

@state.change("enable_contour","timestep","first_folder","second_folder")
def on_state_change(**kwargs):
    view.update()

@state.change("enable_contour","timestep" ,"first_folder")
def on_first_graph_contour_change(enable_contour, **kwargs):
    if enable_contour:
        show_contour(0)

        return
    remove_contour(0)




@state.change("enable_contour","timestep","second_folder")
def on_second_graph_contour_change(enable_contour, **kwargs):
    if enable_contour:
        show_contour(1)
        return
    remove_contour(1)

@state.change("timestep", "first_folder")
def on_first_graph_change(timestep, first_folder, **kwargs):

    plot_graph(int(timestep), first_folder, 0)
    p.subplot(0, 0)
    p.add_text('timestep:{}'.format(timestep), position='lower_left', font_size=6, name="timestep")


@state.change("timestep", "second_folder")
def on_second_graph_change(timestep, second_folder, **kwargs):
    plot_graph(int(timestep), second_folder, 1)


@state.change("plotMode")
def on_plot_mode_change(plotMode,**kwargs):
    print(plotMode)

def create_select(label:str,variable:str):
    vuetify.VSelect(label=label,v_model=(variable,), items=("options",folders))
    # with vuetify.VRadioGroup(
    #         v_model=(variable,),
    # ):
    #     for key, value in config_dic.items():
    #         vuetify.VRadio(label=value, value=key)



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
                with vuetify.VBtnToggle(v_model=("plotMode","displacement")):
                    with vuetify.VBtn(value="displacement"):
                        vuetify.VIcon("mdi-cube-send")
                    with vuetify.VBtn( value="material"):
                        vuetify.VIcon("mdi-cube-outline")
                vuetify.VCheckbox(
                    label="Show Contour Plots",
                    dense=True,
                    v_model=("enable_contour", False)
                )
                with vuetify.VContainer(fluid=True,):
                    vuetify.VSlider(
                        label="Timestep",
                        dense=True,
                        min=0,
                        max=timesteps - 1,
                        v_model=("timestep",),
                    )
                    with vuetify.VContainer(fluid=True):
                        with vuetify.VRow():
                            with vuetify.VBtn():
                                vuetify.VIcon("mdi-plus")
                            with vuetify.VBtn():
                                vuetify.VIcon("mdi-minus")
                with vuetify.VContainer(
                    fluid=True,
                    classes="d-flex flex-row p-2",
                ):
                    create_select("Reference",'first_folder')
                    vuetify.VDivider()
                    create_select("Comparison",'second_folder')

server.start()
