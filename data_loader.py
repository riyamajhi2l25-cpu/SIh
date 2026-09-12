import numpy as np
def load_dwr_data(lat_center=26.71, lon_center=88.43, size=128):
    frames=6
    data=np.random.rand(frames,size,size)*20
    for t in range(frames):
        cx=30+t*8
        cy=40+t*5
        x,y=np.ogrid[:size,:size]
        mask=(x-cx)**2+(y-cy)**2<=144
        data[t][mask]=50+np.random.rand()*10
    return data
def load_insat_data(size=128):
    frames=6
    ctt=np.random.rand(frames,size,size)*60+240
    ctt[:,30:70,40:80]-=50
    return ctt
def get_bounds(lat=26.71, lon=88.43):
    return [[lat-0.8,lon-0.8],[lat+0.8,lon+0.8]]
