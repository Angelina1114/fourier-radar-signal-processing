#!/bin/zsh
# PDF -> per-slide PNGs + 2-column review grids.  Usage: ./make_pngs.sh deck.pdf outdir
set -e
mkdir -p "$2"; rm -f "$2"/slide-*.png(N) "$2"/g*.png(N)
gs -q -dNOPAUSE -dBATCH -sDEVICE=png16m -r110 -dTextAlphaBits=4 -dGraphicsAlphaBits=4 -sOutputFile="$2/slide-%02d.png" "$1"
python3 - "$2" <<'PY'
import sys, glob
from PIL import Image
d = sys.argv[1]
fs = sorted(glob.glob(d + "/slide-*.png"))
for k in range(0, len(fs), 4):
    ims = [Image.open(f) for f in fs[k:k + 4]]
    w, h = ims[0].size
    S = Image.new("RGB", (2 * w + 30, 2 * h + 30), "#777")
    for i, im in enumerate(ims):
        S.paste(im, (10 + (i % 2) * (w + 10), 10 + (i // 2) * (h + 10)))
    S.save(f"{d}/g{k // 4}.png")
print(len(fs), "pages", ims[0].size)
PY
