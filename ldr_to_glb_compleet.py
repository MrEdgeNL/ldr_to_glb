import os
import sys
import argparse
import numpy as np
import trimesh

# ---------- LDraw parsing helpers ----------

def load_ldconfig_colors(ldconfig_path):
    """Laadt kleuren uit ldconfig.ldr en retourneert een dict {kleurcode: [r,g,b,a]}."""
    colors = {}
    if not os.path.exists(ldconfig_path):
        return colors
    with open(ldconfig_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if line.startswith("0 !COLOUR"):
                parts = line.strip().split()
                name = parts[2]
                try:
                    idx = int(parts[4])
                except:
                    continue
                rgb_hex = parts[6]
                r = int(rgb_hex[1:3], 16) / 255.0
                g = int(rgb_hex[3:5], 16) / 255.0
                b = int(rgb_hex[5:7], 16) / 255.0
                alpha = 1.0
                if "ALPHA" in parts:
                    a_idx = parts.index("ALPHA")
                    alpha = int(parts[a_idx+1]) / 255.0
                colors[idx] = [r, g, b, alpha]
    return colors

def find_part_file(part_name, parts_dirs):
    """Zoekt het .dat/.ldr partbestand in de LDraw-partbibliotheken."""
    candidates = [
        part_name,
        part_name.lower(),
        os.path.join("parts", part_name),
        os.path.join("p", part_name),
        os.path.join("parts", "s", part_name)
    ]
    for d in parts_dirs:
        for c in candidates:
            path = os.path.join(d, c)
            if os.path.exists(path):
                return path
    return None

def parse_ldraw_part(filepath, parts_dirs, colors_dict, current_color):
    """Parse een enkel LDraw partbestand naar een trimesh.Mesh."""
    vertices = []
    faces = []
    face_colors = []
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if not line.strip():
                continue
            if line.startswith('0'):  # comment/meta
                continue
            parts = line.strip().split()
            t = parts[0]
            if t == '1':  # subpart reference
                # 1 col x y z a b c d e f g h i part.dat
                col = int(parts[1])
                x, y, z = map(float, parts[2:5])
                m = np.array(list(map(float, parts[5:14]))).reshape((3,3))
                sub_name = parts[14]
                sub_path = find_part_file(sub_name, parts_dirs)
                if sub_path:
                    sub_mesh = parse_ldraw_part(sub_path, parts_dirs, colors_dict, col if col != 16 else current_color)
                    if sub_mesh:
                        # transform
                        sub_mesh.apply_transform(matrix_4x4(m, [x, y, z]))
                        vertices.extend(sub_mesh.vertices.tolist())
                        faces.extend((np.array(sub_mesh.faces) + len(vertices) - len(sub_mesh.vertices)).tolist())
                        face_colors.extend(sub_mesh.visual.vertex_colors[::3].tolist())
            elif t in ('3', '4'):  # triangle or quad
                col = int(parts[1])
                if col == 16:
                    col = current_color
                color = colors_dict.get(col, [0.5, 0.5, 0.5, 1.0])
                if t == '3':
                    v = [list(map(float, parts[2:5])),
                         list(map(float, parts[5:8])),
                         list(map(float, parts[8:11]))]
                    idx_start = len(vertices)
                    vertices.extend(v)
                    faces.append([idx_start, idx_start+1, idx_start+2])
                    face_colors.extend([color]*3)
                elif t == '4':
                    v = [list(map(float, parts[2:5])),
                         list(map(float, parts[5:8])),
                         list(map(float, parts[8:11])),
                         list(map(float, parts[11:14]))]
                    idx_start = len(vertices)
                    vertices.extend(v)
                    faces.append([idx_start, idx_start+1, idx_start+2])
                    faces.append([idx_start, idx_start+2, idx_start+3])
                    face_colors.extend([color]*4)
    if not vertices:
        return None
    mesh = trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces), process=False)
    mesh.visual.vertex_colors = np.array(face_colors)
    return mesh

def matrix_4x4(rot3x3, trans):
    """Maakt een 4x4 matrix van 3x3 rotatie en translatie."""
    mat = np.eye(4)
    mat[:3,:3] = rot3x3
    mat[:3, 3] = trans
    return mat

# ---------- Main conversion ----------

def parse_ldr(filepath, parts_dirs, colors_dict):
    """Parse een volledig .ldr/.mpd bestand naar één mesh."""
    model_meshes = []
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if not line.strip() or line.startswith('0'):
                continue
            parts = line.strip().split()
            if parts[0] == '1':  # part reference
                col = int(parts[1])
                x, y, z = map(float, parts[2:5])
                m = np.array(list(map(float, parts[5:14]))).reshape((3,3))
                part_name = parts[14]
                part_path = find_part_file(part_name, parts_dirs)
                if part_path:
                    mesh = parse_ldraw_part(part_path, parts_dirs, colors_dict, col)
                    if mesh:
                        mesh.apply_transform(matrix_4x4(m, [x, y, z]))
                        model_meshes.append(mesh)
    if not model_meshes:
        return None
    return trimesh.util.concatenate(model_meshes)

# ---------- CLI ----------

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Converteer LDraw LDR/MPD naar GLB.")
    ap.add_argument("--ldr", required=True, help="Pad naar LDR/MPD bestand")
    ap.add_argument("--parts", required=True, nargs="+", help="LDraw parts directories")
    ap.add_argument("--out", required=True, help="Uitvoer GLB bestand")
    ap.add_argument("--ldconfig", help="Pad naar ldconfig.ldr voor kleuren")
    ap.add_argument("--scale", type=float, default=0.0004, help="Schaalfactor (LDU naar meters: 0.0004)")
    args = ap.parse_args()

    colors = {}
    if args.ldconfig:
        colors = load_ldconfig_colors(args.ldconfig)

    mesh = parse_ldr(args.ldr, args.parts, colors)
    if mesh:
        if args.scale != 1.0:
            mesh.apply_scale(args.scale)
        mesh.export(args.out)
        print(f"✅ Export voltooid: {args.out}")
    else:
        print("❌ Geen mesh gegenereerd.")

"""
python ldr_to_glb_complete.py \
  --ldr /pad/naar/model.ldr \
  --parts /pad/naar/ldraw \
  --out /pad/naar/output.glb \
  --ldconfig /pad/naar/ldconfig.ldr \
  --scale 0.0004
  
  
D:/Temp/LDraw2GLB/Moubal_4-73_(KW).ldr
C:/Users/Public/Documents/LDraw/vintage_toys_library_all/ldraw/
Moubal_4-73.glb
"""