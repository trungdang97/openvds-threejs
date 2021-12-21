import uvicorn
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import pyvds
import numpy as np
import orjson
import io
from http import HTTPStatus
from matplotlib import pyplot as plt
from enum import Enum

_file_path = "Kerry3D.vds"
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_headers=['*']
)


class SLICE_TYPE(Enum):
    INLINE = 1
    CROSSLINE = 2
    TIMESLICE = 3

    def __str__(self):
        return '%s' % self.value


class VolumeInfo:
    def __init__(self, ilines_minmax, ilines_shape, xlines_minmax, xlines_shape, timeslices, timeslices_shape):

        self.ilines = ilines_minmax
        self.ilines_shape = ilines_shape
        self.xlines = xlines_minmax
        self.xlines_shape = xlines_shape
        self.timeslices = timeslices
        self.timeslices_shape = timeslices_shape


class SliceData:
    def __init__(self, slice, data):
        self.slice = slice
        self.vm = np.percentile(data, 99)
        data = data.T
        self.shape = data.shape
        self.data = data.tolist()


@app.get('/seismic-slices/info')
async def getVolumeInfo(filePath=_file_path):
    with pyvds.open(filePath) as vdsfile:
        return VolumeInfo([int(vdsfile.ilines.min()), int(vdsfile.ilines.max())], [vdsfile.iline.n_samples, vdsfile.iline.n_xlines],
                          [int(vdsfile.xlines.min()), int(vdsfile.xlines.max())], [
            vdsfile.xline.n_samples, vdsfile.xline.n_ilines],
            vdsfile.n_samples, [vdsfile.iline.n_xlines, vdsfile.xline.n_ilines])


@app.get('/seismic-slices')
async def getSlice(filePath=_file_path, slice_type: int = -1, slice_idx: int = -1):
    if slice_type == -1:
        return []
    with pyvds.open(filePath) as vdsfile:
        if slice_type == SLICE_TYPE.INLINE.value:
            return orjson.dumps({"vm": np.percentile(vdsfile.iline[slice_idx], 99), "data": np.ascontiguousarray(vdsfile.iline[slice_idx].T)}, option=orjson.OPT_SERIALIZE_NUMPY)
        if slice_type == SLICE_TYPE.CROSSLINE.value:
            return orjson.dumps({"vm": np.percentile(vdsfile.xline[slice_idx], 99), "data": np.ascontiguousarray(vdsfile.xline[slice_idx].T)}, option=orjson.OPT_SERIALIZE_NUMPY)
        if slice_type == SLICE_TYPE.TIMESLICE.value:
            return orjson.dumps({"vm": np.percentile(vdsfile.depth_slice[slice_idx], 99), "data": np.ascontiguousarray(vdsfile.depth_slice[slice_idx].T)}, option=orjson.OPT_SERIALIZE_NUMPY)


@app.get('/seismic-slices/image')
async def vds_data(filePath=_file_path, slice_type: int = -1, slice_idx: int = -1):
    with pyvds.open(filePath) as vdsfile:
        if slice_type == SLICE_TYPE.INLINE.value:
            data = vdsfile.iline[slice_idx].T
        if slice_type == SLICE_TYPE.CROSSLINE.value:
            data = vdsfile.xline[slice_idx].T
        if slice_type == SLICE_TYPE.TIMESLICE.value:
            data = vdsfile.depth_slice[slice_idx].T
        with io.BytesIO() as output:
            vm = np.percentile(data, 99)
            plt.imsave(output, arr=data, cmap="coolwarm",
                       vmin=-vm, vmax=vm)
            responseData = output.getvalue()
        response = Response(responseData, HTTPStatus.OK)
        response.headers['Content-Type'] = 'image/png'
        response.headers['Content-Disposition'] = 'inline; filename={0}{1}.png'.format(
            "inline", slice_idx)
        return response


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
