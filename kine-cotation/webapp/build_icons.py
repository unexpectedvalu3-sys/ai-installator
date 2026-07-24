#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genere les icones PWA de KineCotation depuis le design system.

Monogramme « K » blanc sur fond petrole #0B6E5F.
  - icones « any » (192, 512, apple-touch 180) : coins arrondis (~18 %).
  - icone « maskable » 512 : plein cadre, K dans la safe zone ~80 %
    (survit au masque circulaire/arrondi d'Android).

Sortie : assets/icons/*.png  (COMMITES — necessaires au deploiement PWA).
Rejouable : python build_icons.py

Pre-requis : Pillow (deja installe).
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ICI = Path(__file__).resolve().parent
OUT = ICI / "assets" / "icons"
OUT.mkdir(parents=True, exist_ok=True)

PETROLE = (11, 110, 95, 255)   # --accent  #0B6E5F
BLANC = (255, 255, 255, 255)
SS = 4                         # super-sampling (anti-aliasing)

# police grasse la plus proche de Plex disponible sur le poste
_FONT_CANDIDATES = [
    r"C:\Windows\Fonts\segoeuib.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
]


def _font(px):
    for p in _FONT_CANDIDATES:
        if Path(p).exists():
            return ImageFont.truetype(p, px)
    return ImageFont.load_default()


def _draw_K(img_size, k_ratio):
    """Dessine le K centre sur un carre transparent, hauteur = k_ratio*taille."""
    d = Image.new("RGBA", (img_size, img_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(d)
    px = int(img_size * k_ratio)
    f = _font(px)
    # bbox reelle du glyphe pour un centrage optique parfait
    l, t, r, b = draw.textbbox((0, 0), "K", font=f)
    w, h = r - l, b - t
    x = (img_size - w) / 2 - l
    y = (img_size - h) / 2 - t
    draw.text((x, y), "K", font=f, fill=BLANC)
    return d


def _rounded_bg(size, radius_ratio):
    big = size * SS
    bg = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    draw = ImageDraw.Draw(bg)
    rad = int(big * radius_ratio)
    draw.rounded_rectangle([0, 0, big - 1, big - 1], radius=rad, fill=PETROLE)
    return bg


def make_any(size, radius_ratio=0.18, k_ratio=0.60):
    big = size * SS
    canvas = _rounded_bg(size, radius_ratio)
    k = _draw_K(big, k_ratio)
    canvas.alpha_composite(k)
    return canvas.resize((size, size), Image.LANCZOS)


def make_maskable(size, k_ratio=0.46):
    # plein cadre (pas de coins arrondis : Android applique son propre masque),
    # K plus petit pour rester dans la safe zone ~80 %.
    big = size * SS
    canvas = Image.new("RGBA", (big, big), PETROLE)
    k = _draw_K(big, k_ratio)
    canvas.alpha_composite(k)
    return canvas.resize((size, size), Image.LANCZOS)


def save(img, name):
    p = OUT / name
    img.save(p, "PNG")
    print(f"OK  {p.relative_to(ICI)}  ({p.stat().st_size} o)")


if __name__ == "__main__":
    save(make_any(192), "icon-192.png")
    save(make_any(512), "icon-512.png")
    save(make_maskable(512), "icon-512-maskable.png")
    save(make_any(180, k_ratio=0.60), "apple-touch-icon-180.png")
    print("Icones PWA generees dans", OUT)
