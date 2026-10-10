"""Placeholder images for the exhibition layer.

These are NOT the exhibited works. Each placement in demo/data/artworks.json
gets a seeded, procedurally drawn image in a visual register loosely matched
to its exhibition, so the rooms read as hung rather than empty. Real works,
captions and rights come from Mudam in a later phase.

    python3 -I web/scripts/make_artworks.py
"""
import json, math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
DATA = os.path.join(REPO, 'demo/data/artworks.json')
OUT = os.path.join(REPO, 'demo/art')
os.makedirs(OUT, exist_ok=True)

PAPER = [(238, 233, 222), (244, 241, 233), (230, 226, 214), (236, 230, 216)]


def canvas(w, h, colour):
    return Image.new('RGB', (w, h), colour)


def grain(im, rng, amount=10):
    amount *= 0.45
    a = np.asarray(im).astype(np.int16)
    n = np.random.default_rng(rng.randrange(1 << 30)).normal(0, amount, a.shape[:2])[..., None]
    return Image.fromarray(np.clip(a + n, 0, 255).astype(np.uint8))


def brush(d, rng, pts, colour, width):
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        w = max(1, int(width * rng.uniform(0.7, 1.15)))
        d.line([(x0, y0), (x1, y1)], fill=colour, width=w, joint='curve')
        r = w / 2
        d.ellipse([x1 - r, y1 - r, x1 + r, y1 + r], fill=colour)


def wander(rng, w, h, n, step):
    x, y = rng.uniform(0.15, 0.85) * w, rng.uniform(0.15, 0.85) * h
    a = rng.uniform(0, 2 * math.pi)
    pts = [(x, y)]
    for _ in range(n):
        a += rng.gauss(0, 0.45)
        x = min(max(x + math.cos(a) * step, 0.05 * w), 0.95 * w)
        y = min(max(y + math.sin(a) * step, 0.05 * h), 0.95 * h)
        pts.append((x, y))
    return pts


# ----------------------------------------------------------------- Kaihō register

def k_circuit(w, h, rng):
    im = canvas(w, h, rng.choice(PAPER)); d = ImageDraw.Draw(im)
    pal = [(214, 48, 39), (240, 186, 35), (35, 92, 170), (40, 140, 90), (230, 120, 160), (20, 20, 20)]
    nodes = [(rng.uniform(.1, .9) * w, rng.uniform(.1, .9) * h, rng.uniform(.03, .11) * min(w, h)) for _ in range(rng.randint(9, 18))]
    for i, (x, y, r) in enumerate(nodes):
        for j in rng.sample(range(len(nodes)), 2):
            d.line([(x, y), nodes[j][:2]], fill=(30, 30, 30), width=max(2, w // 300))
    for x, y, r in nodes:
        c = rng.choice(pal)
        d.ellipse([x - r, y - r, x + r, y + r], fill=c)
        if rng.random() < .6:
            r2 = r * rng.uniform(.35, .6)
            d.ellipse([x - r2, y - r2, x + r2, y + r2], fill=rng.choice(pal))
    return grain(im, rng, 6)


def k_ink(w, h, rng):
    im = canvas(w, h, rng.choice(PAPER)); d = ImageDraw.Draw(im)
    ink = (18, 17, 16)
    for _ in range(rng.randint(2, 5)):
        pts = wander(rng, w, h, rng.randint(14, 40), min(w, h) * .05)
        brush(d, rng, pts, ink, min(w, h) * rng.uniform(.025, .09))
    if rng.random() < .5:
        cx, cy, r = w * .5, h * .5, min(w, h) * rng.uniform(.25, .38)
        a0 = rng.uniform(0, 6.28)
        pts = [(cx + math.cos(a0 + t / 40 * 5.6) * r, cy + math.sin(a0 + t / 40 * 5.6) * r) for t in range(41)]
        brush(d, rng, pts, ink, min(w, h) * .05)
    im = im.filter(ImageFilter.GaussianBlur(1.2))
    if rng.random() < .35:
        d = ImageDraw.Draw(im); x, y = rng.uniform(.6, .85) * w, rng.uniform(.7, .88) * h
        d.rectangle([x, y, x + w * .045, y + w * .045], fill=(180, 40, 30))
    return grain(im, rng, 7)


def k_dots(w, h, rng):
    base = rng.choice([(20, 20, 24), (236, 230, 216), (196, 38, 46), (240, 196, 40)])
    dot = (240, 236, 226) if sum(base) < 300 else rng.choice([(20, 20, 24), (190, 30, 40)])
    im = canvas(w, h, base); d = ImageDraw.Draw(im)
    s = min(w, h) * rng.uniform(.08, .13)
    y = 0
    while y < h + s:
        x = rng.uniform(0, s)
        while x < w + s:
            r = s * rng.uniform(.25, .48)
            d.ellipse([x - r, y - r * rng.uniform(.8, 1.2), x + r, y + r], outline=dot, width=max(1, int(s * .12)))
            x += s * rng.uniform(.8, 1.15)
        y += s * rng.uniform(.75, 1.0)
    return grain(im.filter(ImageFilter.GaussianBlur(.6)), rng, 5)


def k_fog(w, h, rng):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    f = np.zeros((h, w), np.float32)
    g = np.random.default_rng(rng.randrange(1 << 30))
    for k in range(6):
        cx, cy, s = g.uniform(0, w), g.uniform(0, h), g.uniform(.15, .5) * max(w, h)
        f += np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * s * s)))
    f = f / f.max()
    tone = np.array(rng.choice([(196, 204, 208), (214, 210, 200), (170, 186, 196)]), np.float32)
    dark = tone * .45
    img = dark[None, None] * (1 - f[..., None]) + tone[None, None] * f[..., None]
    horizon = int(h * rng.uniform(.55, .75))
    img[horizon:] *= .82
    return grain(Image.fromarray(img.astype(np.uint8)).filter(ImageFilter.GaussianBlur(6)), rng, 9)


def k_score(w, h, rng):
    im = canvas(w, h, (242, 238, 228)); d = ImageDraw.Draw(im)
    m = int(w * .1)
    rows = rng.randint(6, 14)
    for r in range(rows):
        y = m + (h - 2 * m) * r / rows
        x = m
        while x < w - m:
            seg = rng.uniform(.02, .1) * w
            if rng.random() < .7:
                d.line([(x, y), (min(x + seg, w - m), y)], fill=(40, 38, 36), width=max(1, w // 400))
            else:
                d.ellipse([x, y - 4, x + 8, y + 4], fill=(40, 38, 36))
            x += seg + rng.uniform(.01, .04) * w
    d.rectangle([m * .6, m * .6, w - m * .6, h - m * .6], outline=(60, 58, 54), width=max(1, w // 500))
    if rng.random() < .5:
        x, y = rng.uniform(.2, .7) * w, rng.uniform(.2, .7) * h
        d.ellipse([x, y, x + w * .08, y + w * .08], fill=(200, 50, 40))
    return grain(im, rng, 4)


def k_bands(w, h, rng):
    pal = [(222, 70, 40), (240, 170, 40), (30, 70, 150), (200, 40, 90), (20, 120, 110), (246, 240, 228), (25, 25, 30)]
    im = canvas(w, h, rng.choice(pal)); d = ImageDraw.Draw(im)
    for _ in range(rng.randint(2, 4)):
        cx, cy = rng.uniform(-.3, 1.3) * w, rng.uniform(-.3, 1.3) * h
        r = rng.uniform(.5, 1.2) * max(w, h)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rng.choice(pal))
        r2 = r * rng.uniform(.75, .92)
        d.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], fill=rng.choice(pal))
    return grain(im.filter(ImageFilter.GaussianBlur(1.5)), rng, 8)


def k_weave(w, h, rng):
    im = canvas(w, h, (236, 232, 222)); d = ImageDraw.Draw(im)
    col = rng.choice([(70, 66, 60), (150, 110, 60), (40, 40, 44)])
    cx = w / 2
    for i in range(rng.randint(5, 8)):
        y0 = h * (.08 + i * .12)
        rx = w * rng.uniform(.12, .38)
        ry = h * .06
        for k in range(18):
            off = (k % 2) * rx * .2
            d.arc([cx - rx - off, y0 - ry, cx + rx + off, y0 + ry * 1.8], 0, 360, fill=col, width=max(1, w // 600))
    return grain(im.filter(ImageFilter.GaussianBlur(.7)), rng, 4)


# ------------------------------------------------------------ 1980s register

def v_neoexp(w, h, rng):
    pal = [(220, 40, 40), (250, 200, 30), (30, 60, 160), (20, 20, 20), (250, 245, 235), (40, 150, 70), (240, 120, 30)]
    im = canvas(w, h, rng.choice(pal)); d = ImageDraw.Draw(im)
    for _ in range(rng.randint(6, 12)):
        pts = wander(rng, w, h, rng.randint(6, 18), min(w, h) * .07)
        brush(d, rng, pts, rng.choice(pal), min(w, h) * rng.uniform(.03, .12))
    for _ in range(rng.randint(2, 5)):
        x, y = rng.uniform(.1, .8) * w, rng.uniform(.1, .8) * h
        r = rng.uniform(.04, .12) * min(w, h)
        d.ellipse([x - r, y - r, x + r, y + r], outline=(15, 15, 15), width=max(3, w // 150))
    return grain(im.filter(ImageFilter.GaussianBlur(.8)), rng, 12)


def v_photo(w, h, rng):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    g = np.random.default_rng(rng.randrange(1 << 30))
    f = np.zeros((h, w), np.float32)
    for _ in range(5):
        cx, cy, s = g.uniform(0, w), g.uniform(0, h), g.uniform(.1, .45) * max(w, h)
        f += g.uniform(.3, 1) * np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * s * s)))
    f = (f - f.min()) / (f.max() - f.min() + 1e-6)
    img = np.stack([f * 210 + 20] * 3, -1)
    im = Image.fromarray(img.astype(np.uint8)).filter(ImageFilter.GaussianBlur(3))
    im = grain(im, rng, 18)
    d = ImageDraw.Draw(im)
    tint = rng.choice([(200, 30, 30), (240, 240, 240), (20, 20, 20)])
    x0 = rng.uniform(.05, .3) * w; y0 = rng.uniform(.65, .85) * h
    d.rectangle([x0, y0, x0 + rng.uniform(.4, .65) * w, y0 + h * .07], fill=tint)
    return im


def v_memphis(w, h, rng):
    pal = [(244, 196, 200), (150, 210, 200), (250, 220, 90), (30, 30, 30), (90, 120, 220), (240, 90, 70)]
    im = canvas(w, h, rng.choice([(246, 240, 230), (250, 235, 220)])); d = ImageDraw.Draw(im)
    for _ in range(rng.randint(10, 22)):
        k = rng.random(); c = rng.choice(pal)
        x, y, s = rng.uniform(0, w), rng.uniform(0, h), rng.uniform(.04, .16) * min(w, h)
        if k < .3:
            d.polygon([(x, y - s), (x + s, y + s), (x - s, y + s)], fill=c)
        elif k < .55:
            d.ellipse([x - s, y - s, x + s, y + s], fill=c)
        elif k < .8:
            pts = [(x + i * s * .4, y + math.sin(i * 1.4) * s * .5) for i in range(8)]
            d.line(pts, fill=c, width=max(3, int(s * .18)), joint='curve')
        else:
            for i in range(5):
                d.line([(x + i * s * .3, y), (x + i * s * .3, y + s * 1.5)], fill=(30, 30, 30), width=max(2, int(s * .06)))
    return grain(im, rng, 4)


def v_video(w, h, rng):
    g = np.random.default_rng(rng.randrange(1 << 30))
    bars = [(235, 235, 235), (235, 235, 30), (30, 235, 235), (30, 235, 30), (235, 30, 235), (235, 30, 30), (30, 30, 235)]
    img = np.zeros((h, w, 3), np.float32)
    if rng.random() < .5:
        bw = w / len(bars)
        for i, c in enumerate(bars):
            img[:, int(i * bw):int((i + 1) * bw)] = c
        img[int(h * .7):] *= .35
    else:
        yy, xx = np.mgrid[0:h, 0:w]
        ph = g.uniform(0, 6.28, 3)
        for k in range(3):
            img[..., k] = 127 + 120 * np.sin(xx / w * g.uniform(2, 9) + yy / h * g.uniform(1, 6) + ph[k])
    shift = int(w * .01)
    img[..., 0] = np.roll(img[..., 0], shift, 1)
    img *= (0.78 + 0.22 * (np.arange(h) % 4 < 2))[:, None, None]
    img += g.normal(0, 6, img.shape)
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.7))


def v_slogan(w, h, rng):
    bg, fg = rng.choice([((20, 20, 20), (240, 236, 226)), ((200, 30, 35), (245, 245, 240)), ((245, 242, 232), (20, 20, 20))])
    im = canvas(w, h, bg); d = ImageDraw.Draw(im)
    rows = rng.randint(3, 6)
    for r in range(rows):
        y = h * (.18 + r * .62 / rows)
        x = w * .1
        while x < w * .9:
            bw = rng.uniform(.03, .14) * w
            d.rectangle([x, y, min(x + bw, w * .9), y + h * .07], fill=fg)
            x += bw + w * .02
    return grain(im, rng, 5)


# ---------------------------------------------------------- FOR EVER register

def f_charcoal(w, h, rng):
    im = canvas(w, h, (240, 236, 228)); d = ImageDraw.Draw(im)
    ink = (28, 27, 26)
    for _ in range(rng.randint(2, 4)):
        cx, cy = rng.uniform(.3, .7) * w, rng.uniform(.3, .7) * h
        rx, ry = rng.uniform(.18, .35) * w, rng.uniform(.12, .3) * h
        a0 = rng.uniform(0, 6.28); turns = rng.uniform(1.2, 2.4)
        pts = [(cx + math.cos(a0 + t / 60 * turns * 6.28) * rx * (1 - t / 140), cy + math.sin(a0 + t / 60 * turns * 6.28) * ry * (1 - t / 140)) for t in range(61)]
        brush(d, rng, pts, ink, w * .012)
        x1, y1 = pts[-1]; x0, y0 = pts[-3]
        a = math.atan2(y1 - y0, x1 - x0); s = w * .05
        d.polygon([(x1 + math.cos(a) * s, y1 + math.sin(a) * s), (x1 + math.cos(a + 2.5) * s, y1 + math.sin(a + 2.5) * s), (x1 + math.cos(a - 2.5) * s, y1 + math.sin(a - 2.5) * s)], fill=ink)
    im = im.filter(ImageFilter.GaussianBlur(1.6))
    return grain(im, rng, 9)


REGISTERS = {
    'kaiho': [k_circuit, k_ink, k_dots, k_fog, k_score, k_bands, k_weave],
    'vktrs': [v_neoexp, v_photo, v_memphis, v_video, v_slogan],
    'forever': [f_charcoal],
}

# Each Kaihō room leans on one or two registers, so a room reads as a section.
ROOM_BIAS = {
    'galerie-est-0': ['k_ink', 'k_circuit'], 'galerie-ouest-0': ['k_score', 'k_score', 'k_dots'],
    'galerie-est-1': ['k_bands', 'k_circuit'], 'galerie-ouest-1': ['k_fog', 'k_weave'],
    'petite-galerie-ouest': ['k_score'], 'grand-hall': ['k_weave'], 'jardin-sculptures': ['k_fog', 'k_weave'],
    'galerie-est-m1': ['v_neoexp', 'v_memphis'], 'foyer': ['v_video', 'v_photo'], 'galerie-ouest-m1': ['v_photo', 'v_slogan'],
}


def main():
    arts = json.load(open(DATA))['artworks']
    for a in arts:
        rng = random.Random(a['seed'])
        gens = REGISTERS[a['exhibition']]
        bias = ROOM_BIAS.get(a['room'])
        if bias and rng.random() < .75:
            name = rng.choice(bias)
            gen = next(g for g in gens if g.__name__ == name)
        else:
            gen = rng.choice(gens)
        aspect = a['w'] / a['h']
        W = 960 if aspect >= 1 else int(960 * aspect)
        H = int(W / aspect)
        im = gen(W, H, rng)
        a['register'] = gen.__name__
        im.save(os.path.join(OUT, f"{a['id']}.webp"), quality=74, method=6)
        t = im.copy(); t.thumbnail((320, 320))
        t.save(os.path.join(OUT, f"{a['id']}-s.webp"), quality=72, method=5)
    json.dump(dict(artworks=arts), open(DATA, 'w'), separators=(',', ':'))
    total = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))
    print(len(arts), 'images', round(total / 1048576, 1), 'MB')


if __name__ == '__main__':
    main()
