//
const SLICE_TYPE = {
    INLINE: 1,
    CROSSLINE: 2,
    TIMESLICE: 3
}
let base_url = "http://localhost:8000/seismic-slices"
let camera, scene, renderer, stats, controls;
let inline_shape = []
let crossline_shape = []
let timeslices_shape = []

let inline_mesh, crossline_mesh, timeslice_mesh

$(document).ready(function () {
    $.ajax({
        url: base_url + "/info",
        method: "GET",
        success: function (data) {
            $("#inline_idx").attr("min", data.ilines[0])
            $("#inline_idx").attr("max", data.ilines[1])
            $("#inline_idx").attr("value", data.ilines[0])
            inline_shape = data.ilines_shape
            $("#crossline_idx").attr("min", data.xlines[0])
            $("#crossline_idx").attr("max", data.xlines[1])
            $("#crossline_idx").attr("value", data.xlines[0])
            crossline_shape = data.xlines_shape
            $("#timeslice_idx").attr("min", 0)
            $("#timeslice_idx").attr("max", data.timeslices - 1)
            $("#timeslice_idx").attr("value", 0)
            timeslices_shape = data.timeslices_shape

            // getSlice(SLICE_TYPE.INLINE, data.ilines[0])
            getSlice(SLICE_TYPE.INLINE, data.ilines[0])
            getSlice(SLICE_TYPE.CROSSLINE, data.xlines[0])
            getSlice(SLICE_TYPE.TIMESLICE, 0)
        }
    })

    document.getElementById("inline_idx").addEventListener("change", (e) => {
        scene.remove(inline_mesh)
        getSlice(SLICE_TYPE.INLINE, e.target.valueAsNumber)
    })
    $("#crossline_idx").change(function (e) {
        scene.remove(crossline_mesh)
        getSlice(SLICE_TYPE.CROSSLINE, e.target.valueAsNumber)
    })
    $("#timeslice_idx").change(function (e) {
        scene.remove(timeslice_mesh)
        getSlice(SLICE_TYPE.TIMESLICE, e.target.valueAsNumber)
    })

    init();
    animate();

})

function getSlice(slice_type, slice_idx) {
    $.ajax({
        url: base_url + "?" + "slice_type=" + slice_type + "&slice_idx=" + slice_idx,
        method: "GET",
        success: function (data) {
            switch (slice_type) {
                case SLICE_TYPE.INLINE:
                    inline_mesh = sliceRender(slice_type, slice_idx, data)
                    scene.add(inline_mesh)
                    break;
                case SLICE_TYPE.CROSSLINE:
                    crossline_mesh = sliceRender(slice_type, slice_idx, data)
                    scene.add(crossline_mesh)
                    break;
                case SLICE_TYPE.TIMESLICE:
                    timeslice_mesh = sliceRender(slice_type, slice_idx, data)
                    scene.add(timeslice_mesh)
                    break;
                default:
                    console.error("Parameter 'slice_type' value doesn't exist in SLICE_TYPE")
                    break;
            }
        }
    })
}

function init() {
    //
    camera = new THREE.PerspectiveCamera(80, window.innerWidth / window.innerHeight, 1, 3500);

    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x050505);

    //
    const light = new THREE.HemisphereLight();
    scene.add(light);
    scene.add(new THREE.AxesHelper(10))

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(window.innerWidth, window.innerHeight);
    controls = new THREE.OrbitControls(camera, renderer.domElement)
    controls.enablePan = true
    camera.position.set(1500, 0, 0);
    controls.update();
    document.getElementById("render").appendChild(renderer.domElement);
    //

    stats = new Stats();
    document.getElementById("stats").appendChild(stats.dom);

    //

    window.addEventListener('resize', onWindowResize);
}

function onWindowResize() {

    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();

    renderer.setSize(window.innerWidth, window.innerHeight);

}
function animate() {

    requestAnimationFrame(animate);

    render();
    stats.update();

}
function render() {
    renderer.render(scene, camera);
}

function sliceRender(slice_type, slice_idx, slice_data) {
    slice_data = JSON.parse(slice_data)
    const geometry = new THREE.BufferGeometry();
    const material = new THREE.MeshPhongMaterial({
        side: THREE.DoubleSide,
        vertexColors: true,
        // wireframe: true
    });
    const indices = [];
    let shape = [];
    switch (slice_type) {
        case SLICE_TYPE.INLINE:
            shape = inline_shape
            break;
        case SLICE_TYPE.CROSSLINE:
            shape = crossline_shape
            break;
        case SLICE_TYPE.TIMESLICE:
            shape = timeslices_shape
            break;
        default:
            console.error("Parameter 'slice_type' value doesn't exist in SLICE_TYPE")
            break;
    }

    const vertices = [];
    const normals = [];
    const colors = [];
    let color = new THREE.Color()
    const lut = new THREE.Lut('cooltowarm')
    lut.lut = lut.lut.reverse()
    let a, b, c, d

    lut.minV = -slice_data.vm
    lut.maxV = slice_data.vm
    let x, y, z
    for (let i = 0; i < shape[0]; i++) {
        for (let j = 0; j < shape[1]; j++) {
            switch (slice_type) {
                case SLICE_TYPE.INLINE:
                    x = slice_idx - parseInt($("#inline_idx").attr("min"));
                    y = -i
                    z = j
                    break;
                case SLICE_TYPE.CROSSLINE:
                    x = j
                    y = -i
                    z = slice_idx - parseInt($("#crossline_idx").attr("min"));
                    break;
                case SLICE_TYPE.TIMESLICE:
                    x = j
                    y = -slice_idx;
                    z = i
                    break;
                default:
                    console.error("Parameter 'slice_type' value doesn't exist in SLICE_TYPE")
                    break;
            }

            vertices.push(x, y, z)
            normals.push(0, 0, 1);
            color = lut.getColor(slice_data.data[i][j])
            if (color !== undefined) {
                colors.push(color.r, color.g, color.b)
            }
            else {
                colors.push(1, 1, 1)
            }
        }
    }
    for (let i = 0; i < shape[0] - 1; i++) {
        for (let j = 0; j < shape[1] - 1; j++) {
            a = i * shape[1] + j;
            b = i * shape[1] + j + 1;
            c = a + shape[1];
            d = a + shape[1] + 1;
            indices.push(a, b, c);
            indices.push(b, c, d);
        }
    }
    geometry.setIndex(indices);
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
    geometry.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
    geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

    return new THREE.Mesh(geometry, material);
}