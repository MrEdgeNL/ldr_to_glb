# ldr_to_glb
LDraw to GLB online viewer

Main goal:

Create a LDR/MDP file with LeoCAD & custom library and publish this as 3D viewable content on a webpage.

1. Custom LDraw library. (done, on local machine)
2. Create a model with LeoACD. (done, local machine.)
3. Let ChatGPT create python script: LDraw format → (Wavefront) OBJ format. (Done, see script.)

Open cmd window & type:
python ldr_to_glb_compleet.py --ldr Moubal_4-73_(KW).ldr --parts C:/Users/Public/Documents/LDraw/vintage_toys_library_all/ldraw/ --out Moubal_4-73.glb --scale 0.0004
Response:
✅ Export voltooid: Moubal_4-73.glb

4. Check if OBJ model works. (Done, with windows 3D viewer. Model is upsidedown, no color information yet. This is fine for now.)

5. Upload OBJ example. (done)
6. Let ChatGPT create a html script, adding GLB-viewer & point to OBJ file. (not yet working?)
7. Show HTML page:
Open browser:
https://html-preview.github.io/?url=https://github.com/MrEdgeNL/ldr_to_glb/blob/main/viewer_HTML_Threejs.html
