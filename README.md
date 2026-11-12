# fourier-radar-signal-processing

傅立葉分析與雷達訊號處理的學習與報告資料。

報告者：盧詠涵（數學系資訊數學組）

## 目前內容：Ch.1–4 第一次報告（2026/11/12）
主題是傅立葉分析的數學基礎、物理意義，以及雷達訊號處理的初步應用，範圍涵蓋訊號與頻率、振幅與相位、傅立葉級數、傅立葉轉換。

- **簡報**：[`Fourier_Analysis_Radar_Ch1-4.pptx`](Fourier_Analysis_Radar_Ch1-4.pptx)，共 19 張主頁加 3 張 Appendix，附講者備註；另有 [PDF 預覽](Fourier_Analysis_Radar_Ch1-4.pdf)
- **互動報告網頁**：[`web/`](web/)，與簡報逐頁對應，每頁都有可操作的波形與頻譜示範
- 所有圖都由公式精確繪製（[`assets/generate_figures.py`](assets/generate_figures.py)），公式以 LaTeX 排版；[`assets/math_verification.txt`](assets/math_verification.txt) 是數值驗算結果（33 項）
- 本報告是理論與示意，沒有使用實測雷達資料

**開啟互動網頁：**
```bash
python3 -m http.server 8765 --directory web
```
啟動後用瀏覽器開啟 http://localhost:8765/preview.html。操作方式：→ / ← 翻頁，N 開講者備註，O 總覽，F 全螢幕。

---



## 檔案說明
| 檔案 | 內容 |
|---|---|
| `Fourier_Analysis_Radar_Ch1-4.pptx` | 16:9 可編輯簡報：19 張主頁 + 3 張 Appendix，每頁都有講者備註 |
| `Fourier_Analysis_Radar_Ch1-4.pdf` | 預覽 PDF（由 Keynote 匯出） |
| `Fourier_Analysis_Radar_Ch1-4_contact_sheet.png` | 22 頁縮圖接觸表，供人工校對 |
| `assets/figures/` | 20 張圖的 SVG（向量）＋ PNG（300 dpi）＋ `manifest.json` |
| `assets/equations/` | 51 條 LaTeX 排版公式的 SVG＋PNG（600 dpi） |
| `assets/generate_figures.py` | 所有圖都用精確公式繪製（NumPy + Matplotlib） |
| `assets/make_equations.py` | 所有公式的 LaTeX 原文與排版腳本 |
| `assets/verify_math.py` → `math_verification.txt` | 依規格 F 節做數值驗算（33 項全部通過） |
| `build_deck.js` | 用 pptxgenjs 組簡報：版面、文字、講者備註 |
| `postprocess.py` | 設定主題字型（微軟正黑體）與色彩；在 PNG 旁另嵌入 SVG 向量圖 |

## 重新產生
```bash
python3 assets/generate_figures.py
python3 assets/make_equations.py
node build_deck.js
python3 postprocess.py Fourier_Analysis_Radar_Ch1-4.pptx
python3 assets/verify_math.py
```
PDF 預覽：`osascript export_pdf.applescript <絕對路徑.pptx> <絕對路徑.pdf>`（需要 Keynote）；之後執行 `./make_pngs.sh` 和 `python3 make_contact_sheet.py` 產生縮圖接觸表。
需要：Python 3（numpy、matplotlib、Pillow）、TeX Live（latex、dvipng、dvisvgm）、Node.js（先執行 `npm install`）。

## 設計約定
- 配色：原始訊號藍 `1F5FBF`、直流／基準橘 `E07B00`、頻譜綠 `1E8449`、相位紫 `7D3C98`、雷達回波紅 `C0392B`；主色深藍 `1B2A4A`，輔色墨綠 `1F6F6B`。
- 字級：正文 22 pt 以上；標題 32 pt；公式 25–32 pt；圖表依實際放置尺寸繪製，軸標 16 pt、註解 15 pt。
- 公式以高解析度圖片呈現（PNG＋SVG），LaTeX 原文附在每頁講者備註和圖片替代文字中。行內符號（aₙ、T₀ 等）是可編輯的文字。
- 符號慣例：a₀ 為平均值（不使用 a₀/2）、φₙ = atan2(−bₙ, aₙ)、X(f)=∫x(t)e^{−j2πft}dt，不含額外的 2π 因子。

## 互動網頁版（`web/`）
| 檔案 | 內容 |
|---|---|
| `web/src.html` | 網頁原始檔：22 頁內容、互動示範、樣式（要改網頁就改這個） |
| `web/build_web.py` | 從 `build_deck.js` 抽出講者備註，產生 `fourier_talk.html` 與本機預覽用的 `preview.html` |
| `web/fourier_talk.html` | 發布用的成品（已發布成 claude.ai 私人連結） |

修改流程：編輯 `web/src.html` → `python3 web/build_web.py` → 本機預覽：`python3 -m http.server 8765 --directory web`，再開啟 http://localhost:8765/preview.html
操作：→ / 空白鍵 下一頁、← 上一頁、N 講者備註、O 總覽、F 全螢幕；手機可左右滑動。
