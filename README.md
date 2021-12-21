# OpenVDS Visualization Demo using Three.js (WebGL)

I used Python FastAPI for the convenience so use cmd "uvicorn api:app" to run the API.

For the visualization, I'm using Three.js to generate slices as meshes.
Current REST API responses are slow (2-3 seconds for an inline slice).

The web example using slice image as a mesh texture will come later.

C++ should give a better result (?) but I'm not familiar with the language so REST CPP may come later.

You should turn on "Hardware acceleration" in browser's options for better framerate.
