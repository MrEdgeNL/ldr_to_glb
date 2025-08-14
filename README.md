# ldr_to_glb
LDraw to GLB online viewer

Main goal:

Create a LDR/MDP file with LeoCAD & custom library and publish this as 3D viewable content on a webpage.

1. Custom LDraw library. (done, on local machine)
2. Create a model with LeoACD. (done, local machine.)
3. Let ChatGPT create python script: LDraw format → (Wavefront) OBJ format. (Done, see script.)

Open command window & type:

python ldr_to_glb_compleet.py --ldr Moubal_4-73_(KW).ldr --parts C:/Users/Public/Documents/LDraw/vintage_toys_library_all/ldraw/ --out Moubal_4-73.glb --scale 0.0004

Response:

✅ Export voltooid: Moubal_4-73.glb

4. Check if GLB model works. (Done, with windows 3D viewer. Model is upsidedown, no color information yet. This is fine for now.)

5. Upload GLB example. (done)
6. Let ChatGPT create a html script, adding viewer & point to OBJ file:
   a. Not working: example Three.js-viewer.html
   b. Working (only on local machine): example model viewer - google.html
8. Show HTML page from github:
Open browser:
* https://html-preview.github.io/?url=https://github.com/MrEdgeNL/ldr_to_glb/main/example%20Three.js-viewer.html
* https://html-preview.github.io/?url=https://github.com/MrEdgeNL/ldr_to_glb/main/example%20model%20viewer%20-%20google.html


Additional three.js info:
* https://threejs.org/manual/
* https://www.youtube.com/watch?v=aOQuuotM-Ww
