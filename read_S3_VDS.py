import openvds
from matplotlib import pyplot as plt
import numpy

url = "s3://testing-play-minio/" + ""
connectionString = "EndpointOverride=https://play.min.io:9000;AccessKeyId=;SecretKey=;"

vds = openvds.open(url, connectionString)

layout = openvds.getLayout(vds)
accessManager = openvds.VolumeDataAccessManager(vds)
axisDescriptors = [layout.getAxisDescriptor(dim) for dim in range(layout.getDimensionality())]
sliceType = 'inline'
sliceIndex = 55
sliceDimension = 2 if sliceType == 'inline' else 1 if sliceType == 'crossline' else 0 if sliceType == 'timeslice' else 0 if sliceType == 'depthslice' else -1

min = tuple(sliceIndex + 0 if dim == sliceDimension else 0 for dim in range(6))
max = tuple(sliceIndex + 1 if dim == sliceDimension else layout.getDimensionNumSamples(dim) for dim in range(6))

req = accessManager.requestVolumeSubset(min, max, format = openvds.VolumeDataChannelDescriptor.Format.Format_R32)
height = max[0] if sliceDimension != 0 else max[1]
width  = max[2] if sliceDimension != 2 else max[1]

data = req.data.reshape(width, height).transpose()
cmap=plt.get_cmap("seismic")
plt.set_cmap(cmap)
plt.imshow(data)
plt.show()