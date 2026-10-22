#!/usr/bin/env python3
"""IRL original procedural PBR texture + mesh source assets (no external art)."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import numpy as np
from PIL import Image, ImageDraw

MATERIALS = {
    "ForestSoil": {"dark": (49, 38, 26), "light": (116, 91, 60), "rough": (0.74, 0.93), "bump": 1.5},
    "Granite": {"dark": (57, 65, 63), "light": (156, 166, 154), "rough": (0.57, 0.84), "bump": 2.1},
    "LeafGreen": {"dark": (30, 66, 25), "light": (94, 144, 58), "rough": (0.60, 0.84), "bump": 0.8},
}

def periodic_noise(n, frequency, seed):
    """Tileable value noise; all samples refer to a wrapped frequency lattice."""
    rng = np.random.default_rng(seed)
    grid = rng.random((frequency, frequency), dtype=np.float32)
    yy, xx = np.mgrid[:n, :n]
    u = xx.astype(np.float32) * frequency / n
    v = yy.astype(np.float32) * frequency / n
    i, j = np.floor(u).astype(np.int32), np.floor(v).astype(np.int32)
    tx, ty = u - i, v - j
    tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
    g00, g01 = grid[j % frequency, i % frequency], grid[j % frequency, (i + 1) % frequency]
    g10, g11 = grid[(j + 1) % frequency, i % frequency], grid[(j + 1) % frequency, (i + 1) % frequency]
    return ((g00 * (1 - tx) + g01 * tx) * (1 - ty)
            + (g10 * (1 - tx) + g11 * tx) * ty).astype(np.float32)

def fractal(n, seed):
    weights = ((3, .40), (7, .28), (17, .18), (43, .09), (91, .05))
    result = np.zeros((n, n), dtype=np.float32)
    for frequency, weight in weights:
        result += weight * periodic_noise(n, frequency, seed + frequency * 101)
    return np.clip(result, 0, 1)

def save_texture_set(folder, name, data, size, seed):
    height = fractal(size, seed)
    variation = fractal(size, seed + 600)
    color_weight = np.clip(0.78 * height + 0.22 * variation, 0, 1)
    dark = np.array(data['dark'], np.float32)
    light = np.array(data['light'], np.float32)
    base = dark[None, None, :] + (light - dark)[None, None, :] * color_weight[:, :, None]
    base = np.uint8(np.clip(np.rint(base), 0, 255))
    dx = (np.roll(height, -1, 1) - np.roll(height, 1, 1)) * size * 0.010 * data['bump']
    dy = (np.roll(height, -1, 0) - np.roll(height, 1, 0)) * size * 0.010 * data['bump']
    normal = np.stack((-dx, dy, np.ones_like(dx)), axis=-1)
    normal /= np.maximum(np.linalg.norm(normal, axis=2, keepdims=True), 1e-6)
    normal = np.uint8(np.clip(np.rint((normal * .5 + .5) * 255), 0, 255))
    roughness = data['rough'][0] + (data['rough'][1] - data['rough'][0]) * variation
    outputs = {
        'BaseColor': Image.fromarray(base, 'RGB'),
        'Normal': Image.fromarray(normal, 'RGB'),
        'Roughness': Image.fromarray(np.uint8(np.rint(roughness * 255)), 'L'),
        'Height': Image.fromarray(np.uint8(np.rint(height * 255)), 'L'),
    }
    for kind, img in outputs.items():
        img.save(folder / f'T_{name}_{kind}.png', optimize=True)
    return outputs['BaseColor']

def write_terrain(path, seed, grid_size=65, extent_cm=8000):
    """Original 80m x 80m sculpted patch. Coordinates are centimeters for Unreal."""
    rng = np.random.default_rng(seed)
    phases = rng.uniform(-math.pi, math.pi, 4)
    def h(x, y):
        return (170 * math.sin(x / 1300 + phases[0]) * math.cos(y / 1100 + phases[1])
                + 60 * math.sin(x / 370 + phases[2]) * math.cos(y / 310 + phases[3]))
    with path.open('w', encoding='utf-8') as f:
        f.write('# IRL creator-generated terrain mesh; cm coordinates; not a AAA scan\no IRL_ForestTerrain\n')
        for iy in range(grid_size):
            y = extent_cm * (iy / (grid_size - 1) - 0.5)
            for ix in range(grid_size):
                x = extent_cm * (ix / (grid_size - 1) - 0.5)
                f.write(f'v {x:.3f} {y:.3f} {h(x,y):.3f}\n')
        for iy in range(grid_size):
            for ix in range(grid_size):
                f.write(f'vt {ix * 5/(grid_size-1):.5f} {iy * 5/(grid_size-1):.5f}\n')
        for iy in range(grid_size - 1):
            for ix in range(grid_size - 1):
                a = iy * grid_size + ix + 1
                b, c, d = a + 1, a + grid_size, a + grid_size + 1
                f.write(f'f {a}/{a} {b}/{b} {c}/{c}\nf {b}/{b} {d}/{d} {c}/{c}\n')

def write_rock(path, seed, rings=11, slices=18):
    rng = np.random.default_rng(seed)
    distortion = rng.uniform(.84, 1.16, (rings + 1, slices)).astype(float)
    with path.open('w', encoding='utf-8') as f:
        f.write('# Original IRL granite boulder; cm coordinates, triangulated\no IRL_Rock_A\n')
        for i in range(rings + 1):
            polar = math.pi * i / rings
            for j in range(slices):
                az = 2 * math.pi * j / slices
                r = 95 * distortion[i, j]
                x, y = r*math.sin(polar)*math.cos(az), r*math.sin(polar)*math.sin(az)
                z = 65 * math.cos(polar)
                f.write(f'v {x:.3f} {y:.3f} {z:.3f}\n')
                f.write(f'vt {j/slices:.5f} {i/rings:.5f}\n')
        for i in range(rings):
            for j in range(slices):
                a = i * slices + j + 1
                b = i * slices + (j+1)%slices + 1
                c, d = a + slices, b + slices
                if i > 0: f.write(f'f {a}/{a} {b}/{b} {c}/{c}\n')
                if i < rings - 1: f.write(f'f {b}/{b} {d}/{d} {c}/{c}\n')

def write_grass(path, seed, blade_count=12):
    rng = np.random.default_rng(seed)
    with path.open('w', encoding='utf-8') as f:
        f.write('# Original IRL opaque grass blade clump; cm coordinates\no IRL_GrassClump\n')
        for i in range(blade_count):
            phi = 2 * math.pi * i / blade_count + rng.uniform(-.12, .12)
            radius = rng.uniform(4, 16)
            height = rng.uniform(35, 79)
            halfwidth = rng.uniform(2.4, 5.4)
            x, y = radius * math.cos(phi), radius * math.sin(phi)
            sx, sy = -math.sin(phi)*halfwidth, math.cos(phi)*halfwidth
            for dx,dy,z in [(-sx,-sy,0),(sx,sy,0),(sx*.12,sy*.12,height)]:
                f.write(f'v {x+dx:.3f} {y+dy:.3f} {z:.3f}\n')
            start = i*3+1
            f.write(f'vt 0 0\nvt 1 0\nvt 0.5 1\nf {start}/{start} {start+1}/{start+1} {start+2}/{start+2}\n')

def main():
    cli=argparse.ArgumentParser()
    cli.add_argument('--out',type=Path,default=Path(__file__).with_name('Generated'))
    cli.add_argument('--size',type=int,default=512,choices=(256,512,1024))
    cli.add_argument('--seed',type=int,default=20261022)
    args=cli.parse_args()
    folder=args.out.resolve(); folder.mkdir(parents=True,exist_ok=True)
    previews=[]
    for i,(name, config) in enumerate(MATERIALS.items()):
        img=save_texture_set(folder,name,config,args.size,args.seed+i*300)
        previews.append((name,img))
    write_terrain(folder/'SM_IRL_TerrainPatch.obj', args.seed)
    write_rock(folder/'SM_IRL_GraniteBoulder.obj',args.seed+40)
    write_grass(folder/'SM_IRL_GrassClump.obj',args.seed+50)
    contact=Image.new('RGB',(args.size*3,args.size+45),(16,20,23))
    d=ImageDraw.Draw(contact)
    for i,(name,image) in enumerate(previews):
        contact.paste(image,(i*args.size,45));d.text((i*args.size+12,14),name,fill='white')
    contact.save(folder/'IRL_Original_PBR_Preview.png',optimize=True)
    manifest={
       'project':'IRL — one authoritative Unreal Engine game',
       'asset_origin':'Generated by original procedural source; NOT copied from any AAA title',
       'generator':'generate_irl_showcase.py', 'seed':args.seed, 'texture_pixels':args.size,
       'texture_packs':list(MATERIALS),
       'notes':'Source visual material set, not photogrammetry; Unreal importer/editor must build .uassets and shaders.',
       'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(folder.iterdir()) if p.is_file() and p.name!='IRL_Original_PBR_Manifest.json'}
    }
    (folder/'IRL_Original_PBR_Manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
    print('GENERATED',folder,'files',len(manifest['sha256'])+1)

if __name__=='__main__':
    main()
