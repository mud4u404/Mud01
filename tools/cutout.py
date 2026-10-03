#!/usr/bin/env python3
"""Cut out a character from a checkerboard 'transparency pattern' background.

Strategy:
1. Sample the two checker colors from image corners/edges.
2. Flood fill from all border pixels that match either checker color (within tolerance).
3. Feather the mask edge by 1-2 px for smooth alpha.
4. Crop to the character's bounding box with padding, save as RGBA PNG.
"""
import sys
from PIL import Image, ImageFilter

def sample_bg_colors(img):
    w, h = img.size
    px = img.load()
    # Sample points along all four borders
    candidates = []
    for x in range(0, w, max(1, w // 60)):
        candidates += [px[x, 0], px[x, h - 1]]
    for y in range(0, h, max(1, h // 60)):
        candidates += [px[0, y], px[w - 1, y]]
    # Cluster: keep the two most common distinct colors
    from collections import Counter
    cnt = Counter(candidates)
    colors = [c for c, _ in cnt.most_common(8)]
    picked = []
    for c in colors:
        if all(abs(c[0] - p[0]) + abs(c[1] - p[1]) + abs(c[2] - p[2]) > 60 for p in picked):
            picked.append(c)
        if len(picked) == 2:
            break
    return picked

def flood_key(img, bg_colors, tol=60):
    """Mark pixels connected to border matching bg colors as transparent."""
    w, h = img.size
    px = img.load()
    visited = bytearray(w * h)
    from collections import deque
    q = deque()

    def is_bg(x, y):
        c = px[x, y]
        for b in bg_colors:
            if abs(c[0] - b[0]) + abs(c[1] - b[1]) + abs(c[2] - b[2]) <= tol:
                return True
        return False

    # Seed all border pixels that look like background
    for x in range(w):
        for y in (0, h - 1):
            if is_bg(x, y) and not visited[y * w + x]:
                visited[y * w + x] = 1
                q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if is_bg(x, y) and not visited[y * w + x]:
                visited[y * w + x] = 1
                q.append((x, y))

    while q:
        x, y = q.popleft()
        for nx, ny in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
            if 0 <= nx < w and 0 <= ny < h and not visited[ny * w + nx]:
                if is_bg(nx, ny):
                    visited[ny * w + nx] = 1
                    q.append((nx, ny))

    # Build alpha mask (255 = keep)
    mask = Image.new('L', (w, h), 255)
    m = mask.load()
    for y in range(h):
        row = y * w
        for x in range(w):
            if visited[row + x]:
                m[x, y] = 0

    # Feather: blur the mask slightly so edges anti-alias
    mask = mask.filter(ImageFilter.GaussianBlur(1.2))
    out = img.copy().convert('RGBA')
    out.putalpha(mask)
    return out

def autocrop(img, pad=8):
    bbox = img.getchannel('A').getbbox()
    if not bbox:
        return img
    l, t, r, b = bbox
    l = max(0, l - pad); t = max(0, t - pad)
    r = min(img.width, r + pad); b = min(img.height, b + pad)
    return img.crop((l, t, r, b))

def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} input.(png|jpg) output.png [--pad N]")
        sys.exit(1)
    src, dst = sys.argv[1], sys.argv[2]
    pad = 8
    if '--pad' in sys.argv:
        pad = int(sys.argv[sys.argv.index('--pad') + 1])
    img = Image.open(src).convert('RGB')
    bg = sample_bg_colors(img)
    print(f"Background colors detected: {bg}")
    if not bg:
        print("No background detected; aborting.")
        sys.exit(2)
    out = flood_key(img, bg)
    out = autocrop(out, pad)
    out.save(dst)
    print(f"Saved {dst} ({out.width}x{out.height})")

if __name__ == '__main__':
    main()
