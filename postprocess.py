"""
postprocess.py — finishing touches pptxgenjs cannot write:
  * theme: Traditional-Chinese (ea / Hant) font = Microsoft JhengHei (微軟正黑體), theme name + colours
  * every PNG figure / equation also gets its SVG original embedded (a:svgBlip), the same way
    PowerPoint stores inserted SVGs: PowerPoint 2016+/365 shows the vector, older apps the PNG.
Usage: python3 postprocess.py Fourier_Analysis_Radar_Ch1-4.pptx
"""
import os
import re
import shutil
import sys
import tempfile
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
pptx = sys.argv[1]
NO_SVG = "--no-svg" in sys.argv
CJK = "Microsoft JhengHei"
COLORS = {"dk1": "1B2A4A", "lt1": "FFFFFF", "dk2": "1F6F6B", "lt2": "F3F5F8",
          "accent1": "1F5FBF", "accent2": "E07B00", "accent3": "1E8449", "accent4": "7D3C98",
          "accent5": "C0392B", "accent6": "1F6F6B", "hlink": "1F5FBF", "folHlink": "7D3C98"}
SVG_EXT = "{96DAC541-7B7A-43D3-8B79-37D633B846F1}"
SVG_NS = "http://schemas.microsoft.com/office/drawing/2016/SVG/main"

tmp = tempfile.mkdtemp()
with zipfile.ZipFile(pptx) as z:
    z.extractall(tmp)
    order = z.namelist()

# ---------------- theme
tp = os.path.join(tmp, "ppt/theme/theme1.xml")
t = open(tp, encoding="utf-8").read()
t = t.replace('<a:ea typeface=""/>', f'<a:ea typeface="{CJK}"/>')
t = re.sub(r'<a:font script="Hant" typeface="[^"]*"/>', f'<a:font script="Hant" typeface="{CJK}"/>', t)
t = re.sub(r'<a:theme ([^>]*)name="[^"]*"', r'<a:theme \1name="Fourier Radar"', t, count=1)
for k, v in COLORS.items():
    t = re.sub(rf'<a:{k}>.*?</a:{k}>', f'<a:{k}><a:srgbClr val="{v}"/></a:{k}>', t, count=1, flags=re.S)
open(tp, "w", encoding="utf-8").write(t)

# ---------------- svg alongside png
media = os.path.join(tmp, "ppt/media")
svg_sources = {}
for sub in ("assets/figures", "assets/equations"):
    d = os.path.join(ROOT, sub)
    for f in os.listdir(d):
        if f.endswith(".png"):
            svg_sources[open(os.path.join(d, f), "rb").read()] = os.path.join(d, f[:-4] + ".svg")
added = 0
sdir = os.path.join(tmp, "ppt/slides")
for sx in sorted(os.listdir(sdir)):
    if not sx.endswith(".xml"):
        continue
    relp = os.path.join(sdir, "_rels", sx + ".rels")
    rels = open(relp, encoding="utf-8").read()
    xml = open(os.path.join(sdir, sx), encoding="utf-8").read()
    rid_target = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="\.\./media/([^"]+)"', rels))
    rid_target.update({a: b for b, a in re.findall(r'Target="\.\./media/([^"]+)"[^>]*Id="(rId\d+)"', rels)})
    used = [int(x) for x in re.findall(r'Id="rId(\d+)"', rels)]
    nxt = max(used) + 1
    for rid, target in list(rid_target.items()):
        data = open(os.path.join(media, target), "rb").read()
        svg = svg_sources.get(data)
        pat = re.compile(rf'r:embed="{rid}"\s*(?:/>|></a:blip>)')
        if NO_SVG or not svg or not pat.search(xml):
            continue
        name = os.path.splitext(target)[0] + ".svg"
        shutil.copy(svg, os.path.join(media, name))
        new = f"rId{nxt}"; nxt += 1
        rels = rels.replace("</Relationships>",
                            f'<Relationship Id="{new}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/{name}"/></Relationships>')
        xml = pat.sub(f'r:embed="{rid}"><a:extLst><a:ext uri="{SVG_EXT}"><asvg:svgBlip xmlns:asvg="{SVG_NS}" r:embed="{new}"/></a:ext></a:extLst></a:blip>', xml)
        added += 1
    open(relp, "w", encoding="utf-8").write(rels)
    open(os.path.join(sdir, sx), "w", encoding="utf-8").write(xml)

ct = os.path.join(tmp, "[Content_Types].xml")
c = open(ct, encoding="utf-8").read()
if 'Extension="svg"' not in c:
    c = c.replace("<Default ", '<Default Extension="svg" ContentType="image/svg+xml"/><Default ', 1)
open(ct, "w", encoding="utf-8").write(c)

# ---------------- repack ([Content_Types].xml first)
out = pptx + ".tmp"
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    names = []
    for base, _, files in os.walk(tmp):
        for f in files:
            names.append(os.path.relpath(os.path.join(base, f), tmp))
    names.sort(key=lambda n: (n != "[Content_Types].xml", order.index(n) if n in order else 10 ** 6, n))
    for n in names:
        z.write(os.path.join(tmp, n), n)
os.replace(out, pptx)
shutil.rmtree(tmp)
print(f"theme fonts/colours set; svg blips added: {added}")
