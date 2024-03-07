import numpy as np
import pyvista as pv
import os


def create_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)
        print("Folder %s created!" % path)
    else:
        print("Folder %s already exists" % path)

basePath="./data"

# 2D Data Creation


path2DData = basePath+'/2D'

create_dir(path2DData)


grid= pv.ImageData(dimensions=(41, 41, 1), spacing=(.5, .5, .5),origin=(-10,-10,0))
r=np.sqrt(grid.x**2+grid.y**2)

phases=np.linspace(0,2*np.pi,15)


for timestep in range(0,15):

    path=path2DData+'/Reference'

    if timestep==0:
        create_dir(path)
        grid['Height']=np.ones(r.shape)
        grid.save(path + '/mesh_material.vti')

    phase=phases[timestep]
    z=np.sin(r+phase)
    grid['Height']=z
    grid.save(path+'/mesh_t_{}.vti'.format(timestep))

    for i,scale in enumerate([0.01,0.05,0.1]):
        path = path2DData +'/Noise {}'.format(scale)

        noise = np.random.normal(0, scale, size=grid.x.size)

        if timestep == 0:
            create_dir(path)
            grid['Height'] = np.ones(r.shape)-np.clip(np.abs(noise),a_min=0,a_max=1)
            grid.save(path + '/mesh_material.vti')


        grid['Height'] = z+noise
        grid.save(path+'/mesh_t_{}.vti'.format(timestep))

