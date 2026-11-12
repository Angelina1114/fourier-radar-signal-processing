"""
build_web.py — 把 build_deck.js 裡 22 頁的講者備註抽出來，注入網頁版 (web/src.html → web/fourier_talk.html)。
Usage: python3 web/build_web.py
"""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
deck = open(os.path.join(HERE, "..", "build_deck.js"), encoding="utf-8").read()
notes = [n.strip() for n in re.findall(r"s\._finish\(`([\s\S]*?)`\);", deck)]
assert len(notes) == 22, len(notes)
src = open(os.path.join(HERE, "src.html"), encoding="utf-8").read()
data = json.dumps(notes, ensure_ascii=False).replace("</", "<\\/")
out = src.replace("__NOTES_JSON__", data)
open(os.path.join(HERE, "fourier_talk.html"), "w", encoding="utf-8").write(out)
# 本機預覽用：補上發布時平台會自動加上的 doctype / charset / viewport
open(os.path.join(HERE, "preview.html"), "w", encoding="utf-8").write(
    '<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"></head><body style="margin:0">' + out + "</body></html>")
print("notes:", len(notes), "→ web/fourier_talk.html", len(out) // 1024, "KB")
