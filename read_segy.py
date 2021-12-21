import pyvds
import numpy as np
from matplotlib import pyplot as plt

# with pyvds.open("chevron-santa-clara.vds") as vdsfile:
#     # data = vdsfile.iline[vdsfile.ilines[352]] #inline slice # X
#     data = vdsfile.xline[vdsfile.xlines[0]] #crossline slice # Y
#     # data = vdsfile.depth_slice[SLICE_IDX] # depth/horizontal slice # Z
# vm = np.percentile(data, 99)
# fig = plt.figure(figsize=(16,9))
# plt.imshow(data.T, cmap="RdBu", vmin=-vm, vmax=vm, aspect='auto')
# plt.colorbar()
# plt.show()

def getSlice(filePath="chevron-c-01-76-sc.vds", x = -1, y = -1, z = -1):
    with pyvds.open(filePath) as vdsfile:
        if x < 0 or x not in vdsfile.ilines:
            x = int(vdsfile.ilines[0])
        if y < 0 or y not in vdsfile.xlines:
            y = int(vdsfile.xlines[0])
        if z < 0 or z > len(vdsfile.depth_slice):
            z = 0
        inline_slice = vdsfile.iline[x] #inline slice # X
        crossline_slice = vdsfile.xline[y] #crossline slice # Y
        depth_slice = vdsfile.depth_slice[z] # depth/horizontal slice # Z
    return {
        "inline": inline_slice,
        "crossline": crossline_slice,
        "depth": depth_slice
    }

data = getSlice(x=55, y=400, z=100)['inline']
# mean, stdev = np.mean(data, axis=0), np.std(data, axis=0)
# outliers = ((np.abs(data[:,0] - mean[0]) > stdev[0])
#             * (np.abs(data[:,1] - mean[1]) > stdev[1])
#             * (np.abs(data[:,2] - mean[2]) > stdev[2]))
# print(data[outliers])
vm = np.percentile(data, 99)
# fig = plt.figure(figsize=(16,9))
plt.imshow(data.T, cmap="RdBu", vmin=-vm, vmax=vm, aspect='auto')
plt.colorbar()
plt.show()