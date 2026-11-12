/*
 * build_deck.js — 傅立葉分析：從時間域、頻率域到雷達回波（Ch.1–4）
 * Builds Fourier_Analysis_Radar_Ch1-4.pptx (16:9, 13.333 x 7.5 in) from:
 *   assets/figures/*.png    (exact-formula Matplotlib figures, see assets/generate_figures.py)
 *   assets/equations/*.png  (LaTeX-typeset equations,        see assets/make_equations.py)
 * Every slide gets speaker notes; the LaTeX source of each equation image on a slide is
 * appended to that slide's notes.
 *
 *   python3 assets/generate_figures.py && python3 assets/make_equations.py && node build_deck.js
 */
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");

const ROOT = __dirname;
const FIG = JSON.parse(fs.readFileSync(path.join(ROOT, "assets/figures/manifest.json")));
const EQM = JSON.parse(fs.readFileSync(path.join(ROOT, "assets/equations/manifest.json")));
const OUTFILE = process.argv[2] || path.join(ROOT, "Fourier_Analysis_Radar_Ch1-4.pptx");

// ------------------------------------------------------------------ palette
const C = {
  navy: "1B2A4A", teal: "1F6F6B", white: "FFFFFF", gray: "6B7280", line: "D5DCE5",
  blue: "1F5FBF", orange: "E07B00", green: "1E8449", purple: "7D3C98", red: "C0392B",
  tintTeal: "E8F3F1", tintBlue: "EEF3FB", tintRed: "FBEDEC", tintOrange: "FFF4E5",
  tintGray: "F3F5F8", tintPurple: "F4EEF8",
};
const MATH_FONT = "Times New Roman";
const W = 13.333, H = 7.5, X0 = 0.6, CW = 12.133;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.title = "傅立葉分析：從時間域、頻率域到雷達回波";
pres.subject = "Fourier Series & Fourier Transform — Chapters 1–4";
pres.author = "盧詠涵";
pres.theme = { headFontFace: "Arial", bodyFontFace: "Arial" };

// ------------------------------------------------------------------ layouts
pres.defineSlideMaster({
  title: "COVER",
  background: { color: C.white },
  objects: [],
});
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: C.white },
  margin: [0.4, 0.6, 0.5, 0.6],
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: X0, y: 0.72, w: CW, h: 0.72,
        fontSize: 32, bold: true, color: C.navy, align: "left", valign: "middle", margin: 0 }, text: "" } },
    { text: { text: "傅立葉分析與雷達｜Ch.1–4", options: { x: X0, y: 7.02, w: 6, h: 0.32,
        fontSize: 15, color: C.gray, margin: 0 } } },
  ],
  slideNumber: { x: 11.93, y: 7.02, w: 0.8, h: 0.32, fontSize: 15, color: C.gray, align: "right", margin: 0 },
});

// ------------------------------------------------------------------ inline rich-text mini markup
//  **bold**   $math$ (letters italic Times New Roman; _x / _{xy} subscript; ^x / ^{xy} superscript)
//  \n = new paragraph
function mathRuns(src, base) {
  const out = [];
  let i = 0;
  const push = (txt, extra = {}) => {
    if (!txt) return;
    // split into italic letters vs upright others
    let buf = "", it = null;
    const flush = () => { if (buf) out.push({ text: buf, options: { ...base, fontFace: MATH_FONT, italic: it, ...extra } }); buf = ""; };
    for (const part of txt.split(/(sinc|cos|sin|atan2)/)) {
      if (!part) continue;
      if (/^(sinc|cos|sin|atan2)$/.test(part)) { if (it !== false) flush(); it = false; buf += part; continue; }
      for (const ch of part) {
        const isIt = /[A-Za-zα-ωϕ]/.test(ch) && ch !== "π";
        if (it !== null && isIt !== it) flush();
        it = isIt; buf += ch;
      }
    }
    flush();
  };
  while (i < src.length) {
    const ch = src[i];
    if ((ch === "_" || ch === "^") && i + 1 < src.length) {
      let arg;
      if (src[i + 1] === "{") { const j = src.indexOf("}", i + 2); arg = src.slice(i + 2, j); i = j + 1; }
      else { arg = src[i + 1]; i += 2; }
      push(arg, ch === "_" ? { subscript: true } : { superscript: true });
    } else {
      let j = i; while (j < src.length && src[j] !== "_" && src[j] !== "^") j++;
      push(src.slice(i, j)); i = j;
    }
  }
  return out;
}
function rich(str, base = {}) {
  const runs = [];
  let bold = false;
  const tokens = str.split(/(\*\*|\$[^$]*\$)/);
  for (const tk of tokens) {
    if (!tk) continue;
    if (tk === "**") { bold = !bold; continue; }
    const b = { ...base, bold: base.bold || bold };
    if (tk.startsWith("$") && tk.endsWith("$") && tk.length > 1) runs.push(...mathRuns(tk.slice(1, -1), b));
    else runs.push({ text: tk, options: b });
  }
  return runs;
}
// paragraphs -> runs with paragraph breaks
function paras(list, pOpts = {}) {
  const runs = [];
  list.forEach((p, k) => {
    const str = typeof p === "string" ? p : p.t;
    const extra = typeof p === "string" ? {} : p.o || {};
    const r = rich(str, { ...pOpts, ...extra });
    if (k < list.length - 1 && r.length) r[r.length - 1].options.breakLine = true;
    runs.push(...r);
  });
  return runs;
}

// ------------------------------------------------------------------ helpers
let notesLatex = [];
function text(slide, content, o) {
  const runs = Array.isArray(content) ? paras(content, o.p || {}) : rich(content, o.p || {});
  slide.addText(runs, {
    isTextBox: true, margin: 0, fontSize: 22, color: C.navy, valign: "top", lineSpacingMultiple: 1.05,
    paraSpaceAfter: o.gap ?? 6, ...o.box,
  });
}
function box(slide, x, y, w, h, fill, opts = {}) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h, rectRadius: 0.08, fill: { color: fill }, line: { color: opts.line || fill, width: opts.lw || 1 },
    objectName: opts.name,
  });
}
function eq(slide, id, x, y, opts = {}) {
  const m = EQM[id];
  if (!m) throw new Error("missing equation " + id);
  const s = opts.scale || 1;
  slide.addImage({ path: path.join(ROOT, "assets/equations", id + ".png"), x, y, w: m.w * s, h: m.h * s,
    altText: "LaTeX: " + m.latex, objectName: "eq_" + id });
  notesLatex.push(`[${id}] ${m.latex}`);
  return { w: m.w * s, h: m.h * s, x2: x + m.w * s, y2: y + m.h * s };
}
function eqH(id) { return EQM[id].h; }
function fig(slide, name, x, y, alt) {
  const m = FIG[name];
  if (!m) throw new Error("missing figure " + name);
  if (x + m.w > W - 0.5 + 0.03 || y + m.h > 6.98) console.warn(`  ! ${name} exceeds safe area: x2=${(x + m.w).toFixed(2)} y2=${(y + m.h).toFixed(2)}`);
  slide.addImage({ path: path.join(ROOT, "assets/figures", name + ".png"), x, y, w: m.w, h: m.h,
    altText: alt, objectName: "fig_" + name });
  return m;
}
function pill(slide, label, color = C.teal) {
  const w = 0.32 + [...label].reduce((a, ch) => a + (/[　-鿿＀-￯]/.test(ch) ? 0.215 : 0.118), 0);
  slide.addText(label, { isTextBox: false, shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.17,
    x: X0, y: 0.3, w, h: 0.36, fill: { color }, color: C.white, fontSize: 15, bold: true,
    align: "center", valign: "middle", margin: 0, objectName: "chapter_pill" });
}
// a label (22pt) vertically centred on an equation that starts at ex
function rowLabel(slide, label, x, w, eqId, ey, color = C.navy) {
  const h = eqH(eqId);
  text(slide, label, { box: { x, y: ey + h / 2 - 0.2, w, h: 0.42, valign: "middle", color, bold: true } });
}

let slideNo = 0;
function newSlide(opts) {
  slideNo++;
  notesLatex = [];
  const s = pres.addSlide({ masterName: opts.master || "CONTENT", sectionTitle: opts.section });
  if (opts.title) s.addText(opts.title, { placeholder: "title" });
  if (opts.pill) pill(s, opts.pill, opts.pillColor);
  s._finish = (notes) => {
    let n = notes.trim();
    if (notesLatex.length) n += "\n\n【本頁公式 LaTeX 原文（可複製）】\n" + notesLatex.join("\n");
    s.addNotes(n);
  };
  return s;
}

// ================================================================== sections
pres.addSection({ title: "導論" });
// ------------------------------------------------------------------ 01 cover
{
  const s = newSlide({ master: "COVER", section: "導論" });
  pill(s, "Chapters 1–4 · 第一次報告");
  s.addText("傅立葉分析：\n從時間域、頻率域到雷達回波", { isTextBox: true, x: X0, y: 1.2, w: 6.4, h: 1.75,
    fontSize: 34, bold: true, color: C.navy, margin: 0, valign: "top", lineSpacingMultiple: 1.1, objectName: "cover_title" });
  s.addText("Fourier Series & Fourier Transform\n— Chapters 1–4", { isTextBox: true, x: X0, y: 3.1, w: 6.2, h: 0.9,
    fontSize: 22, color: C.teal, margin: 0, valign: "top", objectName: "cover_subtitle" });
  box(s, X0, 4.35, 6.0, 1.05, C.tintTeal, { name: "quote_bg" });
  s.addText("「複雜波形中，隱藏著哪些可觀測的物理資訊？」", { isTextBox: true, x: X0 + 0.25, y: 4.35, w: 5.6, h: 1.05,
    fontSize: 22, color: C.navy, margin: 0, valign: "middle", objectName: "cover_quote" });
  s.addText("報告者：盧詠涵　系級：數學系資訊數學組　日期：2026/11/12", { isTextBox: true, x: X0, y: 6.35, w: 10, h: 0.45,
    fontSize: 20, color: C.gray, margin: 0, objectName: "cover_presenter" });
  fig(s, "cover_time_frequency_radar", 6.75, 1.35, "主視覺：兩正弦疊加的時間波形、箭頭、兩根頻譜尖峰（100 Hz、300 Hz），背景為示意雷達同心圓與目標點。");
  s._finish(`
【時間】約 0:30
【講法】各位老師好，今天報告的主題是「傅立葉分析：從時間域、頻率域到雷達回波」，範圍是 Chapter 1–4：訊號與頻率、振幅與相位、傅立葉級數、傅立葉轉換。報告先介紹數學基礎：時間域與頻率域、波形的振幅與相位、傅立葉級數和傅立葉轉換；最後說明它們如何幫助理解雷達的回波。
【核心問題】為什麼雷達不能只看原始波形？
【圖說】右側主視覺：左邊是 sin(2π·100t)+0.5 sin(2π·300t) 的時間波形（以公式精確繪製），右邊是同一訊號的兩條成分線（100 Hz、300 Hz）。背景的雷達同心圓與目標點只是示意，並不代表量到實際雷達訊號。
【常見誤解】這份報告是理論與示意，沒有執行真正的雷達量測。
【銜接下一頁】先說明為什麼要研究這個問題，以及今天報告的地圖。`);
}

// ------------------------------------------------------------------ 02 motivation & roadmap
{
  const s = newSlide({ section: "導論", title: "研究動機與報告地圖", pill: "導論" });
  box(s, X0, 1.62, CW, 0.78, C.tintTeal, { name: "core_question_bg" });
  text(s, "**核心問題：**如何從複雜接收波形，辨認頻率與相位資訊？", { box: { x: X0 + 0.25, y: 1.62, w: CW - 0.5, h: 0.78, valign: "middle", fontSize: 24 } });
  const cards = [
    ["Ch.1", "時間域 vs.\n頻率域"], ["Ch.2", "振幅、頻率、相位"],
    ["Ch.3", "傅立葉級數：\n週期訊號"], ["Ch.4", "傅立葉轉換：\n更一般的訊號"],
  ];
  const cw = 2.15, gap = 0.42, y = 2.75, ch = 2.2;
  cards.forEach(([k, v], i) => {
    const x = X0 + i * (cw + gap);
    box(s, x, y, cw, ch, C.tintGray, { line: C.line, name: `step_card_${i + 1}` });
    s.addText(`${i + 1}`, { shape: pres.shapes.OVAL, x: x + 0.2, y: y + 0.22, w: 0.5, h: 0.5, fill: { color: C.teal },
      color: C.white, fontSize: 18, bold: true, align: "center", valign: "middle", margin: 0, objectName: `step_num_${i + 1}` });
    text(s, `**${k}**`, { box: { x: x + 0.82, y: y + 0.22, w: cw - 0.9, h: 0.5, valign: "middle", color: C.teal, fontSize: 24 } });
    text(s, v.split("\n"), { box: { x: x + 0.2, y: y + 0.9, w: cw - 0.3, h: ch - 1.0 }, gap: 0 });
    s.addShape(pres.shapes.RIGHT_ARROW, { x: x + cw + 0.07, y: y + ch / 2 - 0.16, w: gap - 0.14, h: 0.32,
      fill: { color: C.teal }, line: { color: C.teal }, objectName: `step_arrow_${i + 1}` });
  });
  fig(s, "roadmap_radar_icon", X0 + 4 * (cw + gap), y + 0.1, "簡化雷達發射與反射示意：天線、發射箭頭（藍）、回波箭頭（紅）、目標點。");
  box(s, X0, 5.3, CW, 0.95, C.tintRed, { name: "radar_link_bg" });
  text(s, "**雷達關聯：**回波延遲 → 相位變化；運動 → 都卜勒頻移", { box: { x: X0 + 0.25, y: 5.3, w: CW - 0.5, h: 0.95, valign: "middle" }, p: {} });
  s._finish(`
【時間】約 0:50
【講法】核心問題是：如何從複雜的接收波形中，辨認出頻率與相位資訊？我分四步走：Ch.1 時間域與頻率域兩種觀點；Ch.2 正弦波的振幅、頻率、相位；Ch.3 傅立葉級數處理週期訊號；Ch.4 傅立葉轉換處理更一般的訊號。最後連到雷達：回波的延遲會變成相位變化，目標運動會造成都卜勒頻移。
【定位】此次主要講數學工具的「為什麼」及「如何解讀」。實際雷達系統的 FFT、FMCW 與距離–速度圖屬後續學習，不是此次聲稱已掌握的內容。
【常見誤解】「傅立葉轉換直接輸出距離」——不是，後面 Slide 19 與 Appendix A3 會說明。
【銜接下一頁】先從最基本的「訊號」與「時間域」開始。`);
}

pres.addSection({ title: "Ch.1 訊號與頻率" });
// ------------------------------------------------------------------ 03 time domain
{
  const s = newSlide({ section: "Ch.1 訊號與頻率", title: "訊號與時間域（Time Domain）", pill: "Ch.1 訊號與頻率" });
  eq(s, "s03_x", X0, 1.72);
  text(s, ["**定義：**訊號 $x(t)$ 是隨時間變化的物理量或其模型（例如電壓）。"], { box: { x: X0, y: 2.5, w: 4.75, h: 1.4 } });
  box(s, X0, 4.25, 4.75, 1.75, C.tintBlue, { name: "question_bg" });
  text(s, "**問題：**看合成波形，能直接讀出 100 Hz 與 300 Hz 嗎？", { box: { x: X0 + 0.22, y: 4.25, w: 4.35, h: 1.75, valign: "middle", fontSize: 24 } });
  fig(s, "signal_components_time", 5.73, 2.3, "三層時間域波形（0–20 ms）：sin(2π100t)、0.5 sin(2π300t)、兩者相加 x(t)。");
  s._finish(`
【時間】約 1:00
【講法】訊號 x(t) 是隨時間變化的物理量或其模型，例如電壓。這裡的例子是 x(t)=sin(2π·100t)+0.5 sin(2π·300t)。右圖三層共用時間軸：第一條在 20 ms 內有 2 個週期（100 Hz），第二條有 6 個週期（300 Hz、振幅 0.5），第三條是兩者相加。
【重點】疊加後的時間曲線不容易一眼拆出成分。時間域強調「何時／如何變化」。
【常見誤解】時間域不是「錯的」表示法，它只是回答不同的問題。
【銜接下一頁】那麼，有沒有一種觀點能直接看出「有哪些頻率、各多強」？——頻率域。`);
}

// ------------------------------------------------------------------ 04 frequency domain
{
  const s = newSlide({ section: "Ch.1 訊號與頻率", title: "頻率域（Frequency Domain）", pill: "Ch.1 訊號與頻率" });
  text(s, "**頻率域：**訊號由哪些頻率組成、各自有多強？", { box: { x: X0, y: 1.6, w: CW, h: 0.5, fontSize: 24 } });
  eq(s, "s03_x", X0, 2.3);
  text(s, "**100 Hz（振幅 1）、300 Hz（振幅 0.5）**", { box: { x: 6.85, y: 2.24, w: 5.88, h: 0.5, color: C.green } });
  fig(s, "time_vs_spectrum", X0, 2.85, "左：時間域波形 0–20 ms；右：單邊振幅譜（成分示意），100 Hz 高度 1、300 Hz 高度 0.5。");
  text(s, "**同一個訊號，可用不同觀點描述。**", { box: { x: X0, y: 6.5, w: CW, h: 0.45, color: C.teal, fontSize: 24 } });
  s._finish(`
【時間】約 1:05
【講法】頻率域問的是：訊號由哪些頻率組成、各自有多強？同一個 x(t)，在頻率域只有兩條線：100 Hz 振幅 1、300 Hz 振幅 0.5。
【圖的標示】右圖是「單邊振幅譜（依原正弦振幅正規化）」——也就是傅立葉級數意義下的成分示意，不是直接繪製連續時間 FT 的一般函數。連續時間 FT 對純正弦會得到 Dirac delta，不能把 delta 當成普通函數的高度。
【重點】時間域不是錯的，只是不同表示方式回答不同問題；頻率域更容易找出週期成分。
【常見誤解】把右圖的「高度」當成 FT 函數值；這裡的高度是各正弦成分的振幅。
【銜接下一頁】要描述一個頻率成分，需要哪些參數？進入 Ch.2：振幅、頻率、相位。`);
}

pres.addSection({ title: "Ch.2 振幅與相位" });
// ------------------------------------------------------------------ 05 three parameters
{
  const s = newSlide({ section: "Ch.2 振幅與相位", title: "正弦波的三個參數", pill: "Ch.2 振幅與相位" });
  box(s, X0, 1.62, 5.0, 0.82, C.tintTeal, { name: "main_formula_bg" });
  eq(s, "s05_main", X0 + 0.42, 1.62 + (0.82 - eqH("s05_main")) / 2);
  text(s, [
    "$A$：振幅 Amplitude",
    "$f$：頻率 Frequency（Hz）；$T$ = 1/$f$",
    "$φ$：相位 Phase（rad 或 °）",
    "$ω$ = 2π$f$：角頻率（rad/s）",
  ], { box: { x: X0, y: 2.8, w: 5.1, h: 3.4 }, gap: 18 });
  fig(s, "amplitude_frequency_phase", 5.85, 1.5, "三個分圖（0–1 s），每圖只改變一個參數：振幅 1 vs 2、頻率 2 Hz vs 4 Hz、相位 0° vs 90°。");
  s._finish(`
【時間】約 1:00
【講法】正弦波 x(t)=A cos(2πft+φ) 由三個參數決定：A 振幅、f 頻率（Hz，週期 T=1/f）、φ 相位（rad 或 °）；ω=2πf 是角頻率（rad/s）。
右圖三個分圖每次只改變一個參數：振幅＝高低；頻率＝每秒震盪幾次；相位＝相對的水平位置。
【提醒】相位要有意義，需要一個參考點或參考波。弧度與角度勿混寫：90° = π/2。
【常見誤解】相位不是「振幅的一種」；φ=90° 的 cos 波等於把波形往左移四分之一週期（cos(θ+π/2) = −sin θ）。
【銜接下一頁】相位為什麼重要？因為「時間延遲」在固定頻率上會變成相位差——這正是雷達回波的關鍵。`);
}

// ------------------------------------------------------------------ 06 delay -> phase
{
  const s = newSlide({ section: "Ch.2 振幅與相位", title: "延遲為何對應相位差？", pill: "Ch.2 振幅與相位" });
  const lx = X0, ex = 1.75;
  let y = 1.7;
  eq(s, "s06_s", ex, y); rowLabel(s, "發射", lx, 1.05, "s06_s", y, C.blue);
  y = 2.42; eq(s, "s06_r", ex, y); rowLabel(s, "延遲", lx, 1.05, "s06_r", y, C.red);
  y = 3.17; eq(s, "s06_r2", ex, y); rowLabel(s, "展開", lx, 1.05, "s06_r2", y);
  box(s, X0, 3.95, 5.6, 0.85, C.tintTeal, { line: C.teal, lw: 1.5, name: "conclusion_box" });
  y = 3.95 + (0.85 - eqH("s06_dphi")) / 2; eq(s, "s06_dphi", ex, y); rowLabel(s, "結論", lx + 0.15, 0.95, "s06_dphi", y, C.teal);
  text(s, "**時間延遲在固定頻率上表現為相位差。**", { box: { x: X0, y: 5.15, w: 5.7, h: 0.9, fontSize: 24 } });
  fig(s, "delay_phase_shift", 6.45, 1.65, "同一座標軸上兩條 5 Hz 餘弦：發射 s(t)（藍）與延遲 τ=0.04 s 的接收 r(t)（紅），以雙箭頭標示 τ。");
  s._finish(`
【時間】約 1:15
【講法】發射 s(t)=A cos(2πft)；若回波延遲 τ，接收 r(t)=A_r cos[2πf(t−τ)]。展開得 r(t)=A_r cos(2πft−2πfτ)，和發射波相比，多了一個相位 Δφ=−2πfτ (mod 2π)。所以：時間延遲在固定頻率上表現為相位差。
【數值例（圖）】f=5 Hz、τ=0.04 s：Δφ = −2π·5·0.04 = −0.4π rad = −72°。圖中紅色曲線相對藍色向右平移 τ。
【補充】A_r 可與 A 不同，因為有路徑衰減；這裡只看時間延遲造成的相位效果（圖中取 A_r=0.7 只是示意）。
【常見誤解】mod 2π 很關鍵：相位具有週期模糊性，τ 與 τ+1/f 會給出相同相位，所以單看一個頻率的相位，無法唯一決定延遲。這為雷達連結埋下伏筆（見 Appendix A3）。
【銜接下一頁】接下來進入 Ch.3：如果訊號是週期的，能不能把它拆成許多正弦的和？`);
}

pres.addSection({ title: "Ch.3 傅立葉級數" });
// ------------------------------------------------------------------ 07 periodic, harmonics
{
  const s = newSlide({ section: "Ch.3 傅立葉級數", title: "週期函數、基頻與諧波", pill: "Ch.3 傅立葉級數" });
  let y = 1.68; eq(s, "s07_per", 2.75, y); rowLabel(s, "週期定義：", X0, 2.1, "s07_per", y);
  y = 2.35; eq(s, "s07_f0", 2.75, y); rowLabel(s, "基頻：", X0, 2.1, "s07_f0", y);
  y = 3.38; eq(s, "s07_fn", 2.75, y); rowLabel(s, "第 $n$ 次諧波：", X0, 2.1, "s07_fn", y);
  text(s, ["示例 $f_0$ = 100 Hz：第 1、2、3 次諧波 = 100、200、300 Hz"], { box: { x: X0, y: 4.05, w: 5.5, h: 0.95 } });
  box(s, X0, 5.2, 5.5, 0.85, C.tintOrange, { line: C.orange, name: "note_box" });
  text(s, "**注意：某些諧波的係數可以是零。**", { box: { x: X0 + 0.22, y: 5.2, w: 5.1, h: 0.85, valign: "middle" } });
  fig(s, "period_harmonic_grid", 6.35, 1.55, "上：週期訊號，標出兩個相鄰週期 T0=10 ms；下：100、200、300、400 Hz 的空心刻度，只表示可能的諧波位置。");
  s._finish(`
【時間】約 1:05
【講法】週期訊號滿足 x(t+T₀)=x(t)，最小的正數 T₀ 稱為基本週期；基頻 f₀=1/T₀，角頻率 ω₀=2π/T₀。第 n 次諧波的頻率是 fₙ=n f₀。例如 f₀=100 Hz，第 1、2、3 次諧波是 100、200、300 Hz。
【圖說】上圖是 sin(2π·100t)+0.5 sin(2π·300t)，T₀=10 ms，標出兩個相鄰週期。下圖用空心圓只標出「可能」的諧波位置——不是每一項都一定有訊號。以這個例子來說，200 Hz 與 400 Hz 的係數其實為 0。
【補充】可連結高中固定端弦的諧波概念，但訊號處理中的諧波不必然來自真正的弦，只是週期訊號頻率的整數倍。
【常見誤解】「週期訊號一定有所有諧波」——錯，係數可以為零。
【銜接下一頁】那麼一個週期訊號要怎麼寫成這些諧波的和？這就是傅立葉級數。`);
}

// ------------------------------------------------------------------ 08 Fourier series form
{
  const s = newSlide({ section: "Ch.3 傅立葉級數", title: "傅立葉級數的基本形式", pill: "Ch.3 傅立葉級數" });
  eq(s, "s08_fs", X0, 1.62);
  text(s, [
    "$a_0$：直流分量（平均值；0 Hz）",
    "$a_n$、$b_n$：各諧波在 cos、sin\n基底上的係數",
  ], { box: { x: 7.75, y: 1.48, w: 5.0, h: 1.45 }, gap: 2 });
  fig(s, "square_wave_fourier_series", X0, 3.2, "正弦波疊加逼近方波：N=1、3、10 的部分和 S_N(t)，淡色虛線為理想方波，N=10 標示 Gibbs 現象。");
  box(s, X0, 6.24, CW, 0.66, C.tintTeal, { name: "conclusion_bg" });
  text(s, "**主結論：週期波形 = 不同諧波之和**（在適當收斂意義下）", { box: { x: X0 + 0.25, y: 6.24, w: CW - 0.5, h: 0.66, valign: "middle" } });
  s._finish(`
【時間】約 1:15
【講法】傅立葉級數寫成 x(t) ~ a₀ + Σₙ₌₁^∞ [aₙ cos(nω₀t) + bₙ sin(nω₀t)]。a₀ 是直流分量，也就是一週期的平均值（0 Hz）；aₙ、bₙ 是各諧波在 cos、sin 基底上的係數。
【符號約定】本報告的 a₀ 是平均值，不是另一些教材的 a₀/2 寫法；全篇一致。
【圖說】下圖以 S_N(t)=(4/π)Σ_{k=0}^{N−1} sin[(2k+1)t]/(2k+1) 逼近方波（ω₀=1、T₀=2π，區間 −π..π），N=1、3、10。項數越多越接近方波，但在跳躍點附近有過衝震盪，稱為 Gibbs 現象。
【嚴謹性】用「~」而不是無條件的等號：分段光滑函數的傅立葉級數在連續點收斂到訊號值，在跳躍點收斂到左右極限的平均（方波在 t=0 收斂到 0）。Gibbs 過衝的定量不在本次範圍。
【常見誤解】「項數夠多就處處等於方波」——跳躍點附近的過衝不會隨 N 增加而消失，只會變窄。
【銜接下一頁】先看最簡單的係數：a₀，直流分量。`);
}

// ------------------------------------------------------------------ 09 DC
{
  const s = newSlide({ section: "Ch.3 傅立葉級數", title: "直流分量（DC Component）", pill: "Ch.3 傅立葉級數" });
  eq(s, "s09_a0", X0, 1.7);
  text(s, "例：", { box: { x: X0, y: 2.95, w: 1.0, h: 0.45 } });
  eq(s, "s09_ex", X0, 3.48);
  box(s, X0, 4.45, 5.95, 1.05, C.tintOrange, { line: C.orange, lw: 1.5, name: "dc_box" });
  text(s, "**DC = 0 Hz = 一週期平均值**", { box: { x: X0 + 0.25, y: 4.45, w: 5.5, h: 1.05, valign: "middle", fontSize: 26, color: "A85A00" } });
  fig(s, "dc_offset", 6.85, 1.6, "同軸畫 2sin(2π100t)（無 DC）與 3+2sin(2π100t)（DC=3），標記 y=0 與 y=3 基準線，x 軸 0–20 ms。");
  s._finish(`
【時間】約 0:55
【講法】a₀=(1/T₀)∫₀^{T₀} x(t) dt，就是一週期的平均值，也是 0 Hz 的成分。例：x(t)=3+2 sin(2π·100t)，正弦項在一個完整週期的積分為 0，所以 a₀=3。圖中虛線是沒有 DC 的 2 sin，實線整條往上平移 3，橘色虛線就是 a₀=3。
【單位】若 x(t) 代表電壓，a₀ 的單位就是 V；它是訊號的常數偏移，不必等於物理上的直流供電。
【雷達補充】雷達接收器的直流偏移可能來自電路與洩漏，需要謹慎處理（此處只提觀念）。
【常見誤解】混用 a₀ 與 a₀/2 的定義——本報告一律以 a₀ 為平均值。
【銜接下一頁】a₀ 用「平均」取出；aₙ、bₙ 要怎麼取？關鍵是「正交性」。`);
}

// ------------------------------------------------------------------ 10 orthogonality
{
  const s = newSlide({ section: "Ch.3 傅立葉級數", title: "函數正交性（Orthogonality）", pill: "Ch.3 傅立葉級數" });
  let y = 1.65; eq(s, "s10_ip", 1.7, y); rowLabel(s, "定義：", X0, 1.1, "s10_ip", y);
  y = 2.35; eq(s, "s10_orth", 1.7, y); rowLabel(s, "正交：", X0, 1.1, "s10_orth", y);
  text(s, "**三角基底正交：**", { box: { x: X0, y: 3.0, w: 4, h: 0.45 } });
  eq(s, "s10_cc", X0, 3.5);
  box(s, X0, 5.2, 6.35, 0.9, C.tintTeal, { name: "conclusion_bg" });
  text(s, "**結論：正交性使我們能選出特定頻率。**", { box: { x: X0 + 0.25, y: 5.2, w: 6.0, h: 0.9, valign: "middle" } });
  fig(s, "orthogonality_integrand", 7.15, 1.55, "上：cos(ω0t) 與 cos(2ω0t)；下：兩者乘積在一個完整週期的正負面積（半透明兩色），積分為零。");
  s._finish(`
【時間】約 1:20
【講法】定義函數的內積 ⟨u,v⟩=∫₀^{T₀} u(t)v(t) dt；若 ⟨u,v⟩=0 就稱 u、v 正交。三角基底在一個完整基本週期上正交：∫₀^{T₀} cos(mω₀t)cos(nω₀t)dt = 0（m≠n），= T₀/2（m=n≥1）。
【圖說】右下把 cos(ω₀t)×cos(2ω₀t) 畫出來，正面積與負面積剛好抵銷，積分為 0。
【類比】與線性代數的 u·v=0 類比：函數像無限維向量，內積是「逐點相乘再加總（積分）」。
【證明提示】product-to-sum identity：cos A cos B = ½[cos(A−B)+cos(A+B)]；整數非零諧波在完整週期的積分為零。細節留 Slide 11 與 Appendix A1。
【常見誤解】正交不是「兩條波形在圖上垂直相交」，而是內積（乘積的積分）為 0；且必須是完整基本週期、正整數諧波。
【銜接下一頁】有了正交性，就能一步導出 aₙ、bₙ 的公式。`);
}

// ------------------------------------------------------------------ 11 coefficient derivation
{
  const s = newSlide({ section: "Ch.3 傅立葉級數", title: "正交性如何導出係數？（關鍵推導）", pill: "Ch.3 傅立葉級數" });
  const num = (n, y, hl) => s.addText(`${n}`, { shape: pres.shapes.OVAL, x: X0, y, w: 0.44, h: 0.44,
    fill: { color: hl ? C.orange : C.teal }, color: C.white, fontSize: 18, bold: true, align: "center", valign: "middle", margin: 0, objectName: `step_${n}` });
  const ex = 1.25;
  num(1, 1.7, false); eq(s, "s11_1", ex, 1.62);
  num(2, 2.5, false); text(s, "兩邊乘 $cos(nω_0t)$，於 [0, $T_0$] 積分（完整週期）", { box: { x: ex, y: 2.47, w: 6.7, h: 0.5 } });
  box(s, ex - 0.15, 3.12, 6.85, 1.38, C.tintOrange, { line: C.orange, lw: 1.5, name: "step3_highlight" });
  num(3, 3.22, true); text(s, "因正交性，**只留下** $a_n$·$T_0$/2：", { box: { x: ex, y: 3.2, w: 6.4, h: 0.45 } });
  eq(s, "s11_3", ex + 0.2, 3.68);
  num(4, 4.72, false); text(s, "**結果：**", { box: { x: ex, y: 4.7, w: 2, h: 0.45 } });
  eq(s, "s11_an", ex, 5.12);
  eq(s, "s11_bn", ex, 6.0);
  fig(s, "coefficient_extraction", 8.25, 1.5, "流程圖：混合訊號 x(t) → 乘指定基底 cos(nω0t) → 在完整週期積分 → 得到係數 a1=3。");
  s._finish(`
【時間】約 1:35
【講法】(1) 把 x(t) 寫成級數；(2) 兩邊乘 cos(nω₀t)，在一個完整基本週期 [0,T₀] 積分；(3) 由正交性，所有 k≠n 的 cos 項與所有 sin 項、以及 a₀ 項的積分都為 0，只留下 aₙ·T₀/2；(4) 得 aₙ=(2/T₀)∫₀^{T₀} x(t)cos(nω₀t)dt，bₙ 同理乘 sin(nω₀t)：bₙ=(2/T₀)∫₀^{T₀} x(t)sin(nω₀t)dt。
【圖說】右圖用 x(t)=2+3cos(ω₀t)+4sin(3ω₀t) 示範取 a₁：乘上 cos(ω₀t) 後積分一個完整週期，面積 = 3·T₀/2，所以 a₁=3。
【嚴謹推導（務必完整保留）】對有限傅立葉和 S_N，有 ∫S_N cos(nω₀t)dt = aₙ∫cos²(nω₀t)dt = aₙT₀/2（N≥n），其他項為 0。對 x∈L²[0,T₀]，利用傅立葉部分和 S_N→x 在 L² 中收斂，且內積連續，得到係數公式。bₙ 同理。直流 a₀=(1/T₀)∫x。這個細節可回答教授關於「無限級數是否可以逐項積分」的提問（見 Appendix A2）。
【常見誤解】不可聲稱任意時間區間都正交；必須是完整的基本週期（或其整數倍）。
【銜接下一頁】得到 aₙ、bₙ 之後，怎麼轉成「振幅」與「相位」？`);
}

// ------------------------------------------------------------------ 12 amplitude & phase from coefficients
{
  const s = newSlide({ section: "Ch.3 傅立葉級數", title: "振幅與相位怎麼從係數得到？", pill: "Ch.3 傅立葉級數" });
  eq(s, "s12_id", X0, 1.68);
  text(s, "由和角公式：", { box: { x: X0, y: 2.38, w: 3, h: 0.45 } });
  eq(s, "s12_ab", X0, 2.9);
  eq(s, "s12_A", X0, 3.55);
  eq(s, "s12_phi", X0, 4.22);
  box(s, X0, 5.05, 7.0, 1.0, C.tintTeal, { name: "summary_bg" });
  text(s, ["**每個頻率成分都能用**", "**「頻率＋振幅＋相位」描述。**"], { box: { x: X0 + 0.25, y: 5.05, w: 6.6, h: 1.0, valign: "middle" } });
  fig(s, "coefficient_amplitude_phase", 7.95, 2.3, "係數平面：向量 (an, −bn)，長度 An、角度 φn；縱軸為 −bn（cos(θ+φ) 慣例）。例 an=2、bn=1.5 得 An=2.5、φn=−36.9°。");
  s._finish(`
【時間】約 1:15
【講法】aₙcos(nω₀t)+bₙsin(nω₀t) 可以合成單一餘弦 Aₙcos(nω₀t+φₙ)。用 cos(θ+φ)=cosθcosφ−sinθsinφ 比較係數：aₙ=Aₙcosφₙ、bₙ=−Aₙsinφₙ。平方相加得 Aₙ=√(aₙ²+bₙ²)；角度 φₙ=atan2(−bₙ,aₙ)（Aₙ>0）。
【圖說】右圖把 (aₙ, −bₙ) 畫在平面上：長度就是 Aₙ，與水平軸的夾角就是 φₙ。注意縱軸是 −bₙ 而不是 bₙ，這是因為採用 cos(θ+φ) 慣例。例：aₙ=2、bₙ=1.5 ⇒ Aₙ=2.5、φₙ=atan2(−1.5, 2)=−36.87°。
【補充】atan2 是為了避免一般 arctan(−bₙ/aₙ) 失去象限資訊（例如 aₙ<0 時）。Aₙ=0 時相位無意義（未定義）。
【常見誤解】寫成 atan2(bₙ,aₙ)——在本報告的 cos(θ+φ) 慣例下符號會錯。
【銜接下一頁】用一個完整例子把係數、振幅譜、相位譜串起來。`);
}

// ------------------------------------------------------------------ 13 worked example
{
  const s = newSlide({ section: "Ch.3 傅立葉級數", title: "完整例子與雙頻譜", pill: "Ch.3 傅立葉級數" });
  eq(s, "s13_x", X0, 1.7);
  eq(s, "s13_par", X0, 2.3);
  text(s, [
    { t: "**單邊振幅頻譜：**", o: { color: C.green } },
    "0 Hz→2；100 Hz→3；300 Hz→4",
    { t: "**相位頻譜：**", o: { color: C.purple } },
    "100 Hz→0°；300 Hz→−90°",
  ], { box: { x: 7.75, y: 1.55, w: 4.98, h: 1.75 }, gap: 0 });
  fig(s, "worked_example_spectra", X0, 3.35, "三區塊：時間波形 0–20 ms；單邊振幅譜 stem (0,2)、(100,3)、(300,4)；相位譜 stem (100,0°)、(300,−90°)。");
  s._finish(`
【時間】約 1:30
【講法】x(t)=2+3cos(2π·100t)+4sin(2π·300t)。基頻 f₀=100 Hz（T₀=0.01 s）；係數 a₀=2、a₁=3、b₃=4，其餘為 0。
單邊振幅頻譜：0 Hz→2（DC）、100 Hz→A₁=√(3²+0²)=3、300 Hz→A₃=√(0²+4²)=4。
相位頻譜：φ₁=atan2(−0, 3)=0°；φ₃=atan2(−4, 0)=−90°。因為 sinθ=cos(θ−90°)，所以 300 Hz 的相位是 −90°。
【圖的標示】中間是「單邊 Fourier-series 振幅譜，不是雙邊 FT」；200 Hz 沒有成分，所以沒有畫峰值。相位譜只畫非零交流諧波（DC 不畫相位）。
【常見誤解】第三諧波振幅是 4，但 a₃=0（4 在 b₃）；某頻率是否存在由係數 (aₙ,bₙ) 是否非零決定，而不是只看 aₙ。
【銜接下一頁】傅立葉級數只處理週期訊號；真實量測常常不是週期的——怎麼辦？`);
}

pres.addSection({ title: "Ch.4 傅立葉轉換" });
// ------------------------------------------------------------------ 14 limits of periodic signals
{
  const s = newSlide({ section: "Ch.4 傅立葉轉換", title: "週期訊號的限制", pill: "Ch.3 → Ch.4" });
  box(s, X0, 1.6, 5.85, 0.95, C.tintBlue, { name: "fs_card" });
  text(s, ["**Fourier Series：**週期訊號、", "離散諧波 $f_n$ = $n$/$T_0$"], { box: { x: X0 + 0.2, y: 1.6, w: 5.5, h: 0.95, valign: "middle" } });
  box(s, 6.88, 1.6, 5.85, 0.95, C.tintGray, { name: "measurement_card" });
  text(s, ["**真實量測：**有限時間的脈衝或回波", "未必週期重複"], { box: { x: 7.08, y: 1.6, w: 5.5, h: 0.95, valign: "middle" } });
  fig(s, "periodic_vs_pulse", X0, 2.68, "左：永久重複的正弦波（示意）；右：單次矩形脈衝 x(t)=1（|t|≤T/2），其他 0（示意）。");
  text(s, "**問題：**非週期訊號能不能描述頻率成分？", { box: { x: X0, y: 5.6, w: CW, h: 0.5, fontSize: 24 } });
  s.addShape(pres.shapes.RIGHT_ARROW, { x: X0, y: 6.3, w: 0.5, h: 0.34, fill: { color: C.teal }, line: { color: C.teal }, objectName: "answer_arrow" });
  text(s, "**回答：Fourier Transform（傅立葉轉換）**", { box: { x: X0 + 0.65, y: 6.22, w: 10, h: 0.5, fontSize: 24, color: C.teal } });
  s._finish(`
【時間】約 1:00
【講法】傅立葉級數處理的是週期訊號，頻率是離散的諧波 fₙ=n/T₀。但真實量測到的往往是有限時間的脈衝或回波，未必週期重複。右邊的單次矩形脈衝 x(t)=1（|t|≤T/2），其他為 0，只出現一次。
問題：非週期訊號能不能描述頻率成分？答案：傅立葉轉換。
【重點】非週期並不代表「沒有頻率」，而是不能用有限基本週期所對應的離散諧波，去描述整條時間軸上的訊號。這會引出連續頻率的表述。
【常見誤解】矩形脈衝並不是只有單一頻率；它的頻率內容是一整片連續分布（Slide 18 會算出 T sinc(fT)）。
【銜接下一頁】從傅立葉級數出發，讓週期 T→∞，看看會得到什麼。`);
}

// ------------------------------------------------------------------ 15 derivation I
{
  const s = newSlide({ section: "Ch.4 傅立葉轉換", title: "從級數到轉換（推導 I）", pill: "Ch.4 傅立葉轉換" });
  const lx = X0, lw = 2.3, ex = 2.95;
  let y = 1.62; eq(s, "s15_xT", ex, y); rowLabel(s, "複數形式 FS：", lx, lw, "s15_xT", y);
  y = 2.42; eq(s, "s15_cn", ex, y); rowLabel(s, "係數：", lx, lw, "s15_cn", y);
  y = 3.3; eq(s, "s15_df", ex, y); rowLabel(s, "定義：", lx, lw, "s15_df", y);
  y = 4.18; eq(s, "s15_XTf", ex, y); rowLabel(s, "有限區間頻譜：", lx, lw, "s15_XTf", y);
  box(s, X0, 5.0, 7.4, 0.95, C.tintTeal, { line: C.teal, lw: 1.5, name: "result_box" });
  y = 5.0 + (0.95 - eqH("s15_res")) / 2; eq(s, "s15_res", ex, y); rowLabel(s, "得：", lx + 0.2, lw, "s15_res", y, C.teal);
  fig(s, "frequency_grid_spacing", 8.3, 1.62, "頻率格點軸：…, −2/T, −1/T, 0, 1/T, 2/T, …，相鄰間距 Δf=1/T。");
  box(s, 8.3, 4.35, 4.43, 1.6, C.tintRed, { name: "caution_box" });
  text(s, "**注意：**$c_n$ 與 $X_T(f_n)$ 不同，兩者差一個 $Δf$。", { box: { x: 8.5, y: 4.35, w: 4.05, h: 1.6, valign: "middle" } });
  s._finish(`
【時間】約 1:40
【講法】改用複數形式傅立葉級數：x_T(t)=Σ_{n∈ℤ} cₙ e^{j2πfₙt}，fₙ=n/T；係數 cₙ=(1/T)∫_{−T/2}^{T/2} x_T(t) e^{−j2πfₙt} dt。定義頻率間距 Δf=1/T，並定義有限區間的連續頻率表示 X_T(f)=∫_{−T/2}^{T/2} x(t) e^{−j2πft} dt。比較兩式立得 cₙ = X_T(fₙ)/T = X_T(fₙ)Δf。
【嚴謹推導】令 x 為有限時間支撐、充分良好的訊號；對大於訊號支撐的長度 T，先在 [−T/2,T/2] 定義 x 的週期延拓 x_T（在該區間上 x_T=x）。其複數 FS 係數 cₙ=(1/T)∫_{−T/2}^{T/2} x(t)e^{−j2πfₙt}dt。定義 X_T(f)，立得 cₙ=X_T(fₙ)/T=X_T(fₙ)Δf。選用負號的前向 transform，是為了和複數級數的正號基底 e^{+j2πfₙt} 一致。
【複數形式與三角形式的關係】c₀=a₀，cₙ=(aₙ−jbₙ)/2，c₋ₙ=(aₙ+jbₙ)/2（n≥1，實訊號）。
【常見誤解】把 cₙ 和 X_T(fₙ) 混為一談——兩者差一個 Δf；右圖格點間距正是 Δf=1/T。
【銜接下一頁】把 cₙ=X_T(fₙ)Δf 代回級數，讓 T→∞。`);
}

// ------------------------------------------------------------------ 16 derivation II
{
  const s = newSlide({ section: "Ch.4 傅立葉轉換", title: "從級數到轉換（推導 II）", pill: "Ch.4 傅立葉轉換" });
  text(s, "**代回級數：**", { box: { x: X0, y: 1.6, w: 4, h: 0.45 } });
  eq(s, "s16_sum", X0, 2.08);
  text(s, "當 $T$ → ∞，$Δf$ → 0，離散頻率變密集", { box: { x: X0, y: 2.85, w: 6.9, h: 0.5 } });
  text(s, "**黎曼和 → 積分：**", { box: { x: X0, y: 3.5, w: 4, h: 0.45 } });
  eq(s, "s16_inv", X0, 3.98);
  text(s, "**其中：**", { box: { x: X0, y: 4.65, w: 4, h: 0.45 } });
  eq(s, "s16_fwd", X0, 5.13);
  text(s, "此為形式上的極限；嚴謹成立需要適當的收斂條件。", { box: { x: X0, y: 6.0, w: 6.9, h: 0.45, fontSize: 18, color: C.gray } });
  fig(s, "riemann_sum_to_integral", 7.75, 1.5, "三層：T=4 與 T=16 的離散頻率格點長條（面積 = cn = X_T(fn)Δf），以及 T→∞ 的連續 X(f)；以寬 1 s 矩形脈衝為例。");
  s._finish(`
【時間】約 1:40
【講法】把 cₙ=X_T(fₙ)Δf 代回：x_T(t)=Σ_{n∈ℤ} X_T(fₙ) e^{j2πfₙt} Δf。這正是一個黎曼和的形式。當 T→∞，Δf→0，頻率格點越來越密，X_T→X，黎曼和變成積分：x(t)=∫_{−∞}^{∞} X(f)e^{j2πft} df，其中 X(f)=∫_{−∞}^{∞} x(t)e^{−j2πft} dt。
【圖說】右圖以寬 1 s、高 1 的矩形脈衝為例（X(f)=sinc(f)）。T=4 時格點間距 0.25，T=16 時 1/16，長條面積就是 cₙ；T→∞ 時得到連續的 X(f)。這是「形式上的極限，要求適當收斂條件」。
【嚴謹性】在足夠良好的函數類別（例如光滑且快速衰減的訊號，或其他足以使傅立葉反演與黎曼和極限成立的條件）下可嚴謹處理。對矩形脈衝等分段光滑函數，反演於連續點成立，在跳躍點取左右極限平均。
【常見誤解】不能只說「T 越大傅立葉係數不變」：cₙ 本身會隨 Δf 縮小而趨近 0；連續頻譜是對 cₙ/Δf 的恰當極限描述。
【銜接下一頁】把這兩條式子正式定義為傅立葉轉換與逆轉換，並看它的物理意義。`);
}

// ------------------------------------------------------------------ 17 FT definition
{
  const s = newSlide({ section: "Ch.4 傅立葉轉換", title: "傅立葉轉換的定義與物理意義", pill: "Ch.4 傅立葉轉換" });
  const lx = X0, lw = 2.1, ex = 2.75;
  let y = 1.65; eq(s, "s16_fwd", ex, y); rowLabel(s, "Forward FT", lx, lw, "s16_fwd", y, C.green);
  y = 2.42; eq(s, "s16_inv", ex, y); rowLabel(s, "Inverse FT", lx, lw, "s16_inv", y, C.blue);
  y = 3.2; eq(s, "s17_euler", ex, y); rowLabel(s, "Euler 公式", lx, lw, "s17_euler", y);
  y = 3.88; eq(s, "s17_polar", ex, y); rowLabel(s, "極座標形式", lx, lw, "s17_polar", y);
  box(s, X0, 4.75, 6.6, 1.65, C.tintTeal, { name: "interpretation_bg" });
  text(s, [
    "**解讀：**$|X(f)|$ 描述頻率成分大小",
    "　　　$φ(f)$ 描述相位",
    "　　　$X(f)$ 通常是**複數**函數",
  ], { box: { x: X0 + 0.25, y: 4.75, w: 6.2, h: 1.65, valign: "middle" }, gap: 6 });
  fig(s, "ft_domain_map", 7.55, 1.5, "上：時間域 x(t) 與頻率域 X(f) 之間的雙向箭頭（正轉換／逆轉換）；下：複平面上某一頻率 f1 的 X(f1) 向量，長度 |X|、角度 φ。");
  s._finish(`
【時間】約 1:20
【講法】正式定義：Forward FT X(f)=∫_{−∞}^{∞} x(t)e^{−j2πft}dt；Inverse FT x(t)=∫_{−∞}^{∞} X(f)e^{j2πft}df（本報告的定義不含額外的 2π 因子，正向負號、逆向正號）。Euler 公式 e^{jθ}=cosθ+j sinθ 把 cos、sin 合併成複指數。X(f) 一般是複數，可寫成極座標 X(f)=|X(f)|e^{jφ(f)}：|X(f)| 描述該頻率成分的大小，φ(f) 描述相位。
【圖說】右上：時間域與頻率域透過正／逆轉換互相對應；右下：在某一頻率 f₁，X(f₁) 是複平面上的一個向量。
【補充】j²=−1 是電機系寫法。X(f) 的量綱：若 x 是 V、時間用秒，X(f) 通常是 V·s（V/Hz），不是直接的電壓振幅。例如純正弦的 FT 是廣義函數（delta），需避免把「峰的高度」直覺套到所有情況。
【數學條件】對 L¹ 函數可定義正向積分，反演需額外條件；更一般可用 L² 理論或廣義函數。
【可能追問】週期訊號也有 FT 嗎？——在廣義函數意義下有，呈離散的 delta 譜，所以別說「FT 完全不能分析週期訊號」。為何用複數指數？——讓微分、積分、延遲及相位操作更簡潔。
【銜接下一頁】看一個最重要的性質（時間平移）與最典型的例子（矩形脈衝）。`);
}

// ------------------------------------------------------------------ 18 properties & rect pulse
{
  const s = newSlide({ section: "Ch.4 傅立葉轉換", title: "重要性質與矩形脈衝例子", pill: "Ch.4 傅立葉轉換" });
  const lx = X0, lw = 1.6, ex = 2.25;
  let y = 1.62; eq(s, "s18_shift", ex, y); rowLabel(s, "時間平移：", lx, lw, "s18_shift", y);
  y = 2.3; eq(s, "s18_rect", ex, y); rowLabel(s, "矩形脈衝：", lx, lw, "s18_rect", y);
  text(s, "**傅立葉轉換：**", { box: { x: X0, y: 3.42, w: 3, h: 0.45 } });
  eq(s, "s18_ft", X0, 3.9);
  y = 4.58; eq(s, "s18_sinc", 1.6, y); rowLabel(s, "定義：", lx, 1.0, "s18_sinc", y);
  box(s, X0, 5.5, 6.3, 1.0, C.tintTeal, { name: "conclusion_bg" });
  text(s, ["**時間上有限的脈衝，**", "**在頻率上具有連續的頻譜。**"], { box: { x: X0 + 0.25, y: 5.5, w: 5.9, h: 1.0, valign: "middle" } });
  fig(s, "rect_pulse_sinc", 7.15, 1.5, "上：寬 T=1 s、高 1 的矩形脈衝；下：實值頻譜 X(f)=T sinc(fT)（有正負旁瓣，在 ±1/T、±2/T… 為零），淡綠虛線為 |X(f)|。");
  s._finish(`
【時間】約 1:55
【講法】時間平移性質：x(t−τ) ↔ X(f)e^{−j2πfτ}——純延遲只乘上一個相位因子。矩形脈衝 x(t)=1（|t|≤T/2），其他為 0，其傅立葉轉換 X(f)=∫_{−T/2}^{T/2} e^{−j2πft}dt = T sinc(fT)，其中 sinc(u)=sin(πu)/(πu)、sinc(0)=1（normalized sinc）。結論：時間上有限的脈衝，在頻率上具有連續的頻譜。
【完整計算】X(f)=∫_{−T/2}^{T/2} e^{−j2πft}dt = [e^{−j2πft}/(−j2πf)]_{−T/2}^{T/2} = (e^{jπfT}−e^{−jπfT})/(j2πf) = sin(πfT)/(πf) = T sinc(fT)，f≠0；f=0 時 X(0)=∫_{−T/2}^{T/2}1 dt=T，與連續延拓一致。
【時間平移證明】令 u=t−τ：∫x(t−τ)e^{−j2πft}dt = e^{−j2πfτ}∫x(u)e^{−j2πfu}du = e^{−j2πfτ}X(f)。因 |e^{−j2πfτ}|=1，物理上純延遲只改變相位，不改變 |X(f)|（假設純延遲且未改變振幅）。這是與雷達回波最直接的數學連結。
【圖說】右下畫的是實值 X(f)（T=1 s），有正負旁瓣，零點在 f=±1/T, ±2/T, …；淡綠虛線是振幅頻譜 |X(f)|，不會有負值——兩者不可混淆。
【常見誤解】「矩形脈衝只有一個頻率」；或把 X(f) 的負旁瓣當成「負的振幅」。
【銜接下一頁】總結四章，並說明它們如何連到雷達。`);
}

pres.addSection({ title: "總結" });
// ------------------------------------------------------------------ 19 summary
{
  const s = newSlide({ section: "總結", title: "總結：由傅立葉分析走向雷達", pill: "總結" });
  text(s, [
    "**時間域：**訊號隨時間的變化",
    "**頻率域：**各頻率的振幅與相位",
    "**傅立葉級數：**週期訊號 → 離散諧波",
    "**傅立葉轉換：**非週期／一般訊號 → 連續頻譜（在適當條件下）",
    { t: "**雷達連結：**回波延遲 → 相位因子；", o: { color: C.red } },
    { t: "　　　　　運動 → 都卜勒頻移", o: { color: C.red } },
  ], { box: { x: X0, y: 1.62, w: 6.5, h: 4.0 }, gap: 12 });
  box(s, X0, 5.75, 6.5, 0.8, C.tintTeal, { name: "outlook_bg" });
  text(s, "**展望：**後續學習 DFT、FFT 與 FMCW 雷達", { box: { x: X0 + 0.25, y: 5.75, w: 6.1, h: 0.8, valign: "middle", color: C.teal } });
  fig(s, "radar_summary", 7.35, 1.5, "單站雷達（抽象天線）發射（藍）與回波（紅）箭頭到移動目標，標示延遲 τ 與都卜勒 f_D；下方思維導圖 Time → Fourier → Spectrum → Radar interpretations。");
  s._finish(`
【時間】約 1:25
【講法】總結：時間域看訊號隨時間的變化；頻率域看各頻率的振幅與相位；傅立葉級數把週期訊號拆成離散諧波；傅立葉轉換在適當條件下把非週期／一般訊號表示成連續頻譜。雷達連結：回波延遲在頻率域是相位因子 e^{−j2πfτ}；目標運動造成都卜勒頻移 f_D。
【補充（單站雷達）】最基本的距離關係 R=cτ/2，但必須明說：不是單靠傅立葉轉換得出 R；需要適合的波形與延遲估計方法才能量測。若談移動目標，非相對論近似的單站雷達都卜勒關係 |f_D|≈2|v_r|/λ（|v_r|≪c），正負號依慣例而定。
【圖說】右圖是示意，不是量測結果；不畫任何距離或速度的「假量測」。
【展望】下一階段研究：數位資料如何由 DFT/FFT 處理（含取樣定理、頻譜洩漏），並探索 FMCW 的距離與速度估計（Range–Doppler Map）。這些是後續主題，第一次報告誠實列為下一階段工作。
【可能追問】只用頻譜能測距嗎？——不必然，必須結合雷達波形與延遲／拍頻／相位估計；單一 CW 頻率的相位測距有 2π 模糊性（見 Appendix A3）。
【結尾】謝謝老師，請老師指教。`);
}

pres.addSection({ title: "Appendix" });
// ------------------------------------------------------------------ A1
{
  const s = newSlide({ section: "Appendix", title: "三角函數正交性的正式證明", pill: "Appendix A1", pillColor: C.purple });
  text(s, "**積化和差：**", { box: { x: X0, y: 1.6, w: 3, h: 0.45 } });
  eq(s, "a1_cc", X0, 2.08);
  eq(s, "a1_ss", X0, 2.62);
  eq(s, "a1_k", X0, 3.25);
  eq(s, "a1_sq", X0, 3.85);
  text(s, "**因此**（$m$ ≠ $n$，$m$, $n$ ≥ 1）：", { box: { x: X0, y: 4.72, w: 6, h: 0.45 } });
  eq(s, "a1_mn", X0, 5.2);
  box(s, X0, 5.85, CW, 1.0, C.tintPurple, { name: "conclusion_bg" });
  text(s, ["**結論：**不同正整數諧波正交；相同諧波平方積分是 $T_0$/2", "（限定積分一個完整基本週期、正整數索引）"], { box: { x: X0 + 0.25, y: 5.85, w: CW - 0.5, h: 1.0, valign: "middle" }, gap: 0 });
  s._finish(`
【用途】備用頁：教授追問「正交性怎麼證」時使用。
【逐行】(1) 積化和差 cos A cos B=½[cos(A−B)+cos(A+B)]，sin A sin B=½[cos(A−B)−cos(A+B)]。(2) 對非零整數 k，∫₀^{T₀} cos(kω₀t)dt = [sin(kω₀t)/(kω₀)]₀^{T₀} = sin(2πk)/(kω₀) = 0；同理 ∫₀^{T₀} sin(kω₀t)dt=0。(3) m≠n 時，m−n 與 m+n 都是非零整數，因此 ∫cos((m−n)ω₀t)dt 與 ∫cos((m+n)ω₀t)dt 都為 0，故 cos–cos 正交。(4) m=n≥1 時，cos²θ=(1+cos2θ)/2，積分得 T₀/2。
【其他組合】正弦–正弦用 sin A sin B 公式同法；正弦–餘弦用 sin A cos B=½[sin(A+B)+sin(A−B)]，對所有 m, n（含 m=n）積分皆為 0。
【限定條件】這些結論限定積分一個完整基本週期（或其整數倍）與正整數索引。也可補充：∫cos(nω₀t)=∫sin(nω₀t)=0（n≥1），所以常數基底 1 與所有諧波正交。`);
}

// ------------------------------------------------------------------ A2
{
  const s = newSlide({ section: "Appendix", title: "係數推導及 L² 意義", pill: "Appendix A2", pillColor: C.purple });
  let y = 1.62; eq(s, "a2_SN", 2.6, y); rowLabel(s, "有限部分和：", X0, 2.0, "a2_SN", y);
  text(s, "**正交性（有限和可逐項積分）：**", { box: { x: X0, y: 2.45, w: 7, h: 0.45 } });
  eq(s, "a2_ip", X0, 2.92);
  text(s, "**若** $S_N$ → $x$ in $L^2$，**由 Cauchy–Schwarz：**", { box: { x: X0, y: 3.8, w: 8.5, h: 0.45 } });
  eq(s, "a2_cs", X0, 4.3);
  y = 5.0; eq(s, "a2_an", 1.45, y); rowLabel(s, "故：", X0, 0.8, "a2_an", y);
  box(s, X0, 6.0, CW, 0.75, C.tintPurple, { name: "note_bg" });
  text(s, "**重點：**不能無條件交換無限和與積分；先取有限部分和，再用內積連續性取極限。", { box: { x: X0 + 0.25, y: 6.0, w: CW - 0.5, h: 0.75, valign: "middle" } });
  // native flow diagram (editable shapes)
  const steps = ["有限和 $S_N$", "內積 ⟨$S_N$, cos⟩", "$N$ → ∞（$L^2$ 收斂）", "係數 $a_n$"];
  steps.forEach((st, i) => {
    const yy = 1.65 + i * 1.05;
    box(s, 9.75, yy, 2.95, 0.7, i === 3 ? C.tintOrange : C.tintGray, { line: i === 3 ? C.orange : C.line, name: `flow_${i + 1}` });
    text(s, st, { box: { x: 9.75, y: yy, w: 2.95, h: 0.7, valign: "middle", align: "center", fontSize: 20 } });
    if (i < 3) s.addShape(pres.shapes.DOWN_ARROW, { x: 11.08, y: yy + 0.74, w: 0.3, h: 0.27, fill: { color: C.purple }, line: { color: C.purple }, objectName: `flow_arrow_${i + 1}` });
  });
  s._finish(`
【用途】備用頁：回答「無限級數可以逐項積分嗎？」。
【論證】先看有限部分和 S_N(t)=a₀+Σ_{k=1}^{N}[aₖcos(kω₀t)+bₖsin(kω₀t)]。有限和可以逐項積分，由正交性 ⟨S_N, cos(nω₀t)⟩ = aₙT₀/2（N≥n）。若 S_N→x 在 L²[0,T₀] 中收斂（對 x∈L² 的傅立葉部分和確實如此），由 Cauchy–Schwarz：|⟨S_N−x, cos(nω₀t)⟩| ≤ ‖S_N−x‖₂·‖cos(nω₀t)‖₂ → 0，故 ⟨x, cos(nω₀t)⟩ = lim ⟨S_N, cos(nω₀t)⟩ = aₙT₀/2，即 aₙ=(2/T₀)⟨x, cos(nω₀t)⟩。
【其他係數】對常數基底 1：⟨1,1⟩=T₀，得 a₀=(1/T₀)⟨x,1⟩；正弦基底得 bₙ=(2/T₀)⟨x, sin(nω₀t)⟩。
【重點】展示我們不能無條件交換無限和與積分；先取有限部分和，再使用內積連續性。右側流程圖為可編輯的原生圖形。`);
}

// ------------------------------------------------------------------ A3
{
  const s = newSlide({ section: "Appendix", title: "雷達限制與常見追問", pill: "Appendix A3", pillColor: C.purple });
  text(s, "**單站雷達傳播時間：**", { box: { x: X0, y: 1.6, w: 5.5, h: 0.45 } });
  eq(s, "a3_tau", X0, 2.08);
  text(s, "**連續波回波相位：**", { box: { x: X0, y: 2.98, w: 5.5, h: 0.45 } });
  eq(s, "a3_phi", X0, 3.46);
  text(s, "**都卜勒近似：**", { box: { x: X0, y: 4.36, w: 5.5, h: 0.45 } });
  eq(s, "a3_fd", X0, 4.84);
  fig(s, "radar_round_trip_phase", 6.73, 1.6, "單站雷達與目標的去程 R、回程 R 兩箭頭；相位圓 0–2π，顯示 τ、τ+1/fc、τ+2/fc… 對應同一相位點。");
  box(s, X0, 5.95, CW, 0.8, C.tintRed, { name: "warning_bg" });
  text(s, "**注意：單頻相位有模糊性；FT 不自動給出距離。**", { box: { x: X0 + 0.25, y: 5.95, w: CW - 0.5, h: 0.8, valign: "middle" } });
  s._finish(`
【用途】備用頁：回答雷達相關追問。
【公式】單站雷達往返路徑 2R，傳播時間 τ=2R/c，故 R=cτ/2。連續波（載波 f_c）回波相位 Δφ=−2πf_cτ=−4πR/λ (mod 2π)，其中 λ=c/f_c。都卜勒近似 |f_D|≈2|v_r|/λ，前提是 |v_r|≪c（非相對論近似），正負號依慣例（靠近／遠離）而定。
【相位模糊】右圖相位圓：τ、τ+1/f_c、τ+2/f_c… 對應同一個相位點；換成距離，就是 R 每增加 λ/2，相位繞一圈。所以單頻相位只能決定距離到 λ/2 的整數倍以內。
【若教授問「頻譜中的一條峰能否直接當作物體距離？」】回答：不行，要看系統波形及數學模型。在 FMCW 雷達中，經混頻後的拍頻與距離有關；脈衝雷達可利用回波到達時間；都卜勒估計則常分析跨時間的相位或頻率變化。這些屬於下一階段（DFT/FFT/FMCW）的學習內容。
【誠實聲明】本報告沒有執行真正的雷達量測，也沒有使用任何真實雷達規格；以上為理論關係。`);
}

// ------------------------------------------------------------------ write
(async () => {
  await pres.writeFile({ fileName: OUTFILE });
  console.log("wrote", OUTFILE, "slides:", slideNo);
})();
