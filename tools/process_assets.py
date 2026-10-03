#!/usr/bin/env python3
"""Batch post-process generated art assets:
- sprites/decor: checkerboard cutout -> autocrop -> downscale -> PNG
- portraits: resize -> PNG
- backgrounds: resize -> JPG
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image
from cutout import flood_key, sample_bg_colors, autocrop

RAW = 'public/assets/raw'
SPRITES = ['ren', 'alice', 'roland', 'selena', 'kage',
           'goblin', 'skeleton', 'orc', 'cultist', 'gargoyle', 'dark-priest', 'chaos-knight']

def load(p):
    for ext in ('.jpg', '.png', '.jpeg'):
        if os.path.exists(p + ext):
            return Image.open(p + ext).convert('RGB')
    raise FileNotFoundError(p)

def cutout(img):
    bg = sample_bg_colors(img)
    if not bg:
        raise RuntimeError('no bg colors')
    out = flood_key(img, bg)
    return autocrop(out, pad=10)

os.makedirs('public/assets/sprites', exist_ok=True)
os.makedirs('public/assets/portraits', exist_ok=True)

# ---- sprites: cutout + resize to 512 tall ----
for name in SPRITES:
    img = load(f'{RAW}/spr-{name}')
    out = cutout(img)
    r = 512 / out.height
    out = out.resize((max(1, round(out.width * r)), 512), Image.LANCZOS)
    out.save(f'public/assets/sprites/{name}.png')
    print(f'sprite {name}: {out.size}')

# ---- decors: cutout + resize to 256 tall ----
for name in ['tree', 'rock', 'wall']:
    img = load(f'{RAW}/decor-{name}')
    out = cutout(img)
    r = 256 / out.height
    out = out.resize((max(1, round(out.width * r)), 256), Image.LANCZOS)
    out.save(f'public/assets/decor-{name}.png')
    print(f'decor {name}: {out.size}')

# ---- portraits: resize to 640x854 ----
for name in SPRITES:
    img = load(f'{RAW}/por-{name}')
    out = img.resize((640, 854), Image.LANCZOS)
    out.save(f'public/assets/portraits/{name}.png')
    print(f'portrait {name}: {out.size}')

# ---- backgrounds: resize to 1920x1080 JPG ----
for name in ['title', 'plains', 'forest', 'fortress']:
    img = load(f'{RAW}/bg-{name}')
    out = img.resize((1920, 1080), Image.LANCZOS)
    out.save(f'public/assets/bg-{name}.jpg', quality=88)
    print(f'bg {name}: {out.size}')

print('DONE')
