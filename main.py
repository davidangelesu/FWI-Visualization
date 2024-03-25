import pyvista as pv
from pyvista.trame.ui import plotter_ui
from trame.app import get_server
from trame.ui.vuetify3 import SinglePageWithDrawerLayout
from trame.ui.router import RouterViewLayout
from trame.widgets import vuetify3 as vuetify,html,router
import os

# ----find Parameters----
path2DData = './data/2D'
folders = sorted(os.listdir(path2DData), key=lambda x: -1 if x == 'Reference' else 1)


timesteps = len([filename for filename in os.listdir(path2DData + '/' + folders[0]) if 'material' not in filename])
pv.OFF_SCREEN = True

server = get_server()
server.client_type = 'vue3'
state, ctrl = server.state, server.controller

state['first_folder'] = folders[0]
state['second_folder'] = folders[0]
state['timestep'] = 0
state['plotMode']=0
server.hot_reload = True


def get_displacement_file_path(folder, timestep):
    return path2DData + '/{}/mesh_t_{}.vti'.format(folder, timestep)


def get_material_file_path(folder):
    return path2DData + '/{}/mesh_material.vti'.format(folder)


p = pv.Plotter(shape=(1, 2))


def plot_graph(timestep, folder, subplot_index, **kwargs):
    p.subplot(0, subplot_index)
    p.add_text(folder, font_size=16, name='title')

    filePath=get_displacement_file_path(folder, timestep) if int(state['plotMode']) == 0 else get_material_file_path(folder)
    grid = pv.read(filePath)
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
    ctrl.view_update()


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


@state.change("timestep", "first_folder","plotMode")
def on_first_graph_change(timestep, first_folder,plotMode, **kwargs):

    plot_graph(int(timestep), first_folder, 0)
    p.subplot(0, 0)
    if int(plotMode)==0:
        p.add_text('timestep:{}'.format(timestep), position='lower_left', font_size=6, name="timestep")
    else:
        p.add_text("",name="timestep")


@state.change("timestep", "second_folder","plotMode")
def on_second_graph_change(timestep, second_folder,plotMode, **kwargs):
    plot_graph(int(timestep), second_folder, 1)



def add_timestep():
    state['timestep']=min(state['timestep']+1,timesteps - 1)


def minus_timestep():
    state['timestep']=max(state['timestep']-1,0)


def create_select(label:str,variable:str, **kwargs):
    vuetify.VSelect(label=label,v_model=(variable,), items=("options",folders), **kwargs)





def create_side_by_side_layout():
    with vuetify.VContainer(
            fluid=True,
            classes="pa-2 fill-height d-flex align-center",
    ):
        with vuetify.VCol(cols="3"):
            with vuetify.VCard():
                vuetify.VCardTitle("Parameters")
                vuetify.VDivider()
                with vuetify.VCardText():
                    with vuetify.VContainer(
                            fluid=True,
                            classes="d-flex flex-column p-2",
                    ):
                        html.H3("Mode:")
                        with vuetify.VBtnToggle(v_model=("plotMode", 0), mandatory=True,divided=True,  rounded="xs",
                                                classes="d-flex w-100", ):
                            with vuetify.VBtn(value=0, size="small"):
                                vuetify.VIcon("mdi-cube-send")
                                vuetify.VTooltip("displacement field",activator="parent",  location="bottom")

                            with vuetify.VBtn(value=1, size="small"):
                                vuetify.VIcon("mdi-cube-outline")
                                vuetify.VTooltip(    "material field",activator="parent",  location="bottom")

                        html.H3("Visualization Tools:")
                        vuetify.VCheckbox(
                            label="Show Contour Plots",
                            dense=True,
                            v_model=("enable_contour", False)
                        )
                        html.H3("Comparison:")
                        with vuetify.VRow():
                            with vuetify.VCol(cols="10", classes="fill-height"):
                                vuetify.VSlider(
                                    label="Timestep",
                                    min=0,
                                    max=timesteps - 1,
                                    step=1,
                                    v_model=("timestep",),
                                    disabled=("plotMode==1",)
                                )
                            with vuetify.VCol(cols="2", classes="fill-height"):
                                with vuetify.VContainer():
                                    with vuetify.VRow():
                                        vuetify.VBtn("+", size="x-small", tile=True, rounded="0",click=add_timestep,elevation="0")
                                    with vuetify.VRow():
                                        vuetify.VBtn("-", size="x-small", tile=True,rounded="0", click=minus_timestep,elevation="0")
                        with vuetify.VContainer(
                                fluid=True,
                                classes="d-flex flex-row p-2",
                        ):

                            create_select("Side A", 'first_folder', )

                            create_select("Side B", 'second_folder',)

        with vuetify.VCol(cols="9", classes="fill-height"):
            with vuetify.VContainer(fluid=True, classes="fill-height"):
                # Use PyVista UI template for Plotters
                view = plotter_ui(p)
                ctrl.view_update = view.update
                ctrl.view_reset_camera = view.reset_camera


def create_plot_layout():
    print()


def create_about_layout():
    print("About goes here")


with RouterViewLayout(server, "/",name="content"):
    create_side_by_side_layout()



with RouterViewLayout(server,"/plot",name="content"):
    create_plot_layout()


with RouterViewLayout(server,"/about",name="content"):
    create_about_layout()


with SinglePageWithDrawerLayout(server) as layout:
    layout.title.set_text("Full Waveform Inversion Results Visualizer")
    with layout.content:
        router.RouterView(name="content",classes="w-100 h-100")
    with layout.drawer:
        with vuetify.VContainer(
                fluid=True,
                classes="d-flex flex-column p-2",
        ):
            vuetify.VBtn("Side by Side Comparison",text=True,to="/")
            vuetify.VBtn("Plot",text=True,to="/plot")
            vuetify.VBtn("About",text=True,to="/about")


server.start()
