import numpy as np
import pyvista as pv



grid= pv.ImageData(dimensions=(41, 41, 1), spacing=(.5, .5, .5),origin=(-10,-10,0))
r=np.sqrt(grid.x**2+grid.y**2)

phases=np.linspace(0,2*np.pi,15)



for timestep in range(0,15):

    phase=phases[timestep]
    z=np.sin(r+phase)
    grid['Height']=z
    grid.save('data/mesh_i_0_t_{}.vti'.format(timestep))

    for i,scale in enumerate([0.01,0.05,0.1]):
        noise = np.random.normal(0, scale, size=grid.x.size)
        grid['Height'] = z+noise
        grid.save('data/mesh_i_{}_t_{}.vti'.format(i+1,timestep))
