"""
generate_figures.py
-------------------
Draws every figure of the deck "傅立葉分析：從時間域、頻率域到雷達回波" from exact formulas
(NumPy + Matplotlib). No AI-generated or hand-sketched waveforms are used.

Output: assets/figures/<name>.svg  (vector, text converted to paths)
        assets/figures/<name>.png  (300 dpi, used inside the PPTX)
        assets/figures/manifest.json (physical size of each figure, in inches)

Each figure is drawn at the exact physical size it occupies on the slide, so the
font sizes below are the real on-slide point sizes (axis labels >= 16 pt,
annotations >= 15 pt).

Run:  python3 assets/generate_figures.py
"""
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Arc, Circle, FancyArrowPatch, FancyBboxPatch, Rectangle  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "figures")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- style
# Semantic colours (identical meaning on every slide)
BLUE = "#1F5FBF"     # original / transmitted signal
BLUE_L = "#7FA7E3"   # secondary signal component
ORANGE = "#E07B00"   # DC / reference baseline
GREEN = "#1E8449"    # spectrum
GREEN_L = "#82C9A0"  # |X(f)| helper curve
PURPLE = "#7D3C98"   # phase
RED = "#C0392B"      # radar echo
NAVY = "#1B2A4A"     # text / ink
TEAL = "#1F6F6B"     # theme accent (deep green)
GRAY = "#6B7280"
LIGHT = "#E5E9F0"

FS = 16      # axis labels & ticks
FS_ANN = 15  # annotations

plt.rcParams.update({
    "font.family": ["Heiti TC"],   # Traditional Chinese + Latin (mathtext needs one font with both)
    "mathtext.fontset": "cm",
    "axes.unicode_minus": True,
    "font.size": FS,
    "axes.labelsize": FS,
    "axes.titlesize": FS,
    "xtick.labelsize": FS,
    "ytick.labelsize": FS,
    "legend.fontsize": FS_ANN,
    "axes.edgecolor": "#9AA3AF",
    "axes.labelcolor": NAVY,
    "xtick.color": NAVY,
    "ytick.color": NAVY,
    "text.color": NAVY,
    "axes.titlecolor": NAVY,
    "axes.grid": True,
    "grid.color": "#E3E7ED",
    "grid.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "lines.linewidth": 2.4,
    "svg.fonttype": "path",
    "savefig.transparent": False,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})

MANIFEST = {}


def save(fig, name):
    w, h = fig.get_size_inches()
    fig.savefig(os.path.join(OUT, name + ".svg"))
    fig.savefig(os.path.join(OUT, name + ".png"), dpi=300)
    plt.close(fig)
    MANIFEST[name] = {"w": round(float(w), 3), "h": round(float(h), 3)}
    print(f"  {name}: {w:.2f} x {h:.2f} in")


def title(ax, text, color=NAVY, size=FS):
    ax.set_title(text, loc="left", fontsize=size, color=color, pad=6)


def top_legend(ax, ncol=2):
    ax.legend(loc="lower right", bbox_to_anchor=(1.0, 1.0), ncol=ncol, frameon=False,
              fontsize=FS_ANN, handlelength=1.8, borderaxespad=0.1, columnspacing=1.0)


def ms_axis(ax):
    ax.set_xlabel("時間 $t$（ms）")


def stem(ax, xs, ys, color, lw=3.2, ms=9, marker="o", mfc=None):
    for x, y in zip(xs, ys):
        ax.plot([x, x], [0, y], color=color, lw=lw, solid_capstyle="butt")
    ax.plot(xs, ys, marker, color=color, ms=ms, mfc=mfc or color, mew=2, ls="none")


def harrow(ax, x0, x1, y, text, color=NAVY, dy=0.0, fs=FS_ANN, va="bottom"):
    ax.annotate("", xy=(x1, y), xytext=(x0, y),
                arrowprops=dict(arrowstyle="<->", color=color, lw=1.8, shrinkA=0, shrinkB=0))
    ax.text((x0 + x1) / 2, y + dy, text, ha="center", va=va, fontsize=fs, color=color)


# ---------------------------------------------------------------- signals
t20 = np.linspace(0, 0.02, 4001)            # 0–20 ms, seconds
x1 = np.sin(2 * np.pi * 100 * t20)
x2 = 0.5 * np.sin(2 * np.pi * 300 * t20)
xsum = x1 + x2


# ================================================================ 01 cover
def fig_cover():
    fig = plt.figure(figsize=(6.0, 4.6))
    bg = fig.add_axes([0, 0, 1, 1])
    bg.set_xlim(0, 6.0)
    bg.set_ylim(0, 4.6)
    bg.axis("off")
    # faint radar range rings centred at the antenna (lower-left)
    cx, cy = 0.45, 0.55
    for r in np.arange(0.9, 7.0, 0.9):
        bg.add_patch(Arc((cx, cy), 2 * r, 2 * r, theta1=0, theta2=90, color="#D5E2F0", lw=1.4))
    ang = np.deg2rad(7)
    tr = 4.6
    bg.plot([cx, cx + 6.5 * np.cos(ang)], [cy, cy + 6.5 * np.sin(ang)], color="#D5E2F0", lw=1.2, ls="--")
    tx, ty = cx + tr * np.cos(ang), cy + tr * np.sin(ang)
    bg.add_patch(Circle((tx, ty), 0.11, color=RED, zorder=5))
    bg.text(tx - 0.2, ty + 0.05, "目標（示意）", ha="right", fontsize=FS_ANN, color=RED, va="center")
    # antenna icon
    bg.plot([cx, cx], [cy - 0.35, cy + 0.05], color=NAVY, lw=2.2)
    bg.add_patch(Arc((cx, cy + 0.12), 0.5, 0.5, theta1=200, theta2=340, color=NAVY, lw=2.6))
    bg.text(cx + 0.3, cy - 0.32, "雷達", fontsize=FS_ANN, color=NAVY, va="center")

    # time-domain panel
    a1 = fig.add_axes([0.10, 0.50, 0.40, 0.33])
    a1.plot(t20 * 1e3, xsum, color=BLUE, lw=2.0)
    a1.set_xlim(0, 20)
    a1.set_ylim(-1.6, 1.6)
    a1.set_xticks([0, 10, 20])
    a1.set_yticks([])
    a1.set_xlabel("$t$（ms）", fontsize=FS_ANN, labelpad=1)
    a1.tick_params(labelsize=FS_ANN)
    a1.set_facecolor((1, 1, 1, 0.85))
    a1.grid(False)
    title(a1, "時間域  $x(t)$", BLUE, FS_ANN)

    # frequency-domain panel
    a2 = fig.add_axes([0.66, 0.50, 0.30, 0.33])
    stem(a2, [100, 300], [1.0, 0.5], GREEN, lw=3.0, ms=7)
    a2.set_xlim(0, 400)
    a2.set_ylim(0, 1.25)
    a2.set_xticks([100, 300])
    a2.set_yticks([])
    a2.set_xlabel("$f$（Hz）", fontsize=FS_ANN, labelpad=1)
    a2.tick_params(labelsize=FS_ANN)
    a2.set_facecolor((1, 1, 1, 0.85))
    a2.grid(False)
    title(a2, "頻率域（單邊振幅）", GREEN, FS_ANN)

    bg.add_patch(FancyArrowPatch((3.12, 3.0), (3.85, 3.0), arrowstyle="-|>", mutation_scale=26,
                                 color=TEAL, lw=2.6))
    bg.text(3.48, 3.22, "傅立葉", ha="center", fontsize=FS_ANN, color=TEAL)
    bg.text(5.92, 0.12, "示意圖：以精確公式繪製，非實測雷達資料", ha="right", fontsize=FS_ANN - 2.5, color=GRAY)
    save(fig, "cover_time_frequency_radar")


# ================================================================ 02 radar icon for roadmap
def fig_roadmap_radar():
    fig = plt.figure(figsize=(1.9, 2.0))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1.9)
    ax.set_ylim(0, 2.0)
    ax.axis("off")
    # antenna
    ax.plot([0.32, 0.32], [0.55, 1.0], color=NAVY, lw=2.4)
    ax.plot([0.18, 0.46], [0.55, 0.55], color=NAVY, lw=2.4)
    ax.add_patch(Arc((0.32, 1.12), 0.46, 0.46, theta1=200, theta2=340, color=NAVY, lw=3))
    # target
    ax.add_patch(Circle((1.6, 1.05), 0.1, color=RED))
    ax.add_patch(FancyArrowPatch((0.55, 1.3), (1.45, 1.3), arrowstyle="-|>", mutation_scale=16, color=BLUE, lw=2.2))
    ax.add_patch(FancyArrowPatch((1.45, 0.8), (0.55, 0.8), arrowstyle="-|>", mutation_scale=16, color=RED, lw=2.2))
    ax.text(1.0, 1.42, "發射", ha="center", fontsize=FS_ANN, color=BLUE)
    ax.text(1.0, 0.45, "回波", ha="center", fontsize=FS_ANN, color=RED)
    ax.text(0.95, 1.78, "雷達（示意）", ha="center", fontsize=FS_ANN, color=NAVY)
    save(fig, "roadmap_radar_icon")


# ================================================================ 03
def fig_signal_components():
    fig, axs = plt.subplots(3, 1, figsize=(7.0, 4.6), sharex=True,
                            gridspec_kw=dict(hspace=0.55, left=0.12, right=0.97, top=0.92, bottom=0.13))
    data = [(x1, BLUE_L, "成分 1：$\\sin(2\\pi\\cdot 100\\,t)$　（20 ms 內 2 個週期）"),
            (x2, BLUE_L, "成分 2：$0.5\\,\\sin(2\\pi\\cdot 300\\,t)$　（20 ms 內 6 個週期）"),
            (xsum, BLUE, "合成：$x(t)$ = 成分 1 + 成分 2")]
    for ax, (y, c, lab) in zip(axs, data):
        ax.plot(t20 * 1e3, y, color=c, lw=2.4 if c == BLUE else 2.0)
        ax.set_ylim(-1.7, 1.7)
        ax.set_yticks([-1, 0, 1])
        ax.set_xlim(0, 20)
        title(ax, lab, size=FS_ANN)
    axs[-1].set_xticks([0, 5, 10, 15, 20])
    ms_axis(axs[-1])
    fig.supylabel("振幅（任意單位）", fontsize=FS, color=NAVY, x=0.012)
    fig.text(0.97, 0.985, "時間域", ha="right", va="top", fontsize=FS_ANN, color=GRAY)
    save(fig, "signal_components_time")


# ================================================================ 04
def fig_time_vs_spectrum():
    fig = plt.figure(figsize=(12.1, 3.6))
    a1 = fig.add_axes([0.065, 0.24, 0.40, 0.62])
    a2 = fig.add_axes([0.625, 0.24, 0.355, 0.62])
    a1.plot(t20 * 1e3, xsum, color=BLUE)
    a1.set_xlim(0, 20)
    a1.set_ylim(-1.7, 1.7)
    a1.set_xticks([0, 5, 10, 15, 20])
    ms_axis(a1)
    a1.set_ylabel("振幅（任意單位）")
    title(a1, "時間域：$x(t)$，0–20 ms")

    stem(a2, [100, 300], [1.0, 0.5], GREEN)
    a2.set_xlim(0, 500)
    a2.set_ylim(0, 1.25)
    a2.set_xticks([0, 100, 200, 300, 400, 500])
    a2.set_yticks([0, 0.5, 1.0])
    a2.set_xlabel("頻率 $f$（Hz）")
    a2.set_ylabel("正弦振幅")
    a2.text(112, 1.0, "1", fontsize=FS, color=GREEN, va="center")
    a2.text(312, 0.5, "0.5", fontsize=FS, color=GREEN, va="center")
    title(a2, "頻率域：單邊振幅譜（成分示意）")
    fig.add_artist(FancyArrowPatch((0.478, 0.55), (0.538, 0.55), transform=fig.transFigure,
                                   arrowstyle="<|-|>", mutation_scale=22, color=TEAL, lw=2.4))
    fig.text(0.508, 0.62, "同一訊號", ha="center", fontsize=FS_ANN, color=TEAL)
    fig.text(0.98, 0.015, "註：右圖以各正弦成分的振幅為高度，不是連續時間 FT 的函數圖。",
             ha="right", fontsize=FS_ANN, color=GRAY)
    save(fig, "time_vs_spectrum")


# ================================================================ 05
def fig_amp_freq_phase():
    t = np.linspace(0, 1, 3001)
    fig, axs = plt.subplots(3, 1, figsize=(6.9, 5.45), sharex=True,
                            gridspec_kw=dict(hspace=0.75, left=0.12, right=0.97, top=0.93, bottom=0.11))
    a = axs[0]
    a.plot(t, np.cos(2 * np.pi * 2 * t), color=BLUE, label="$A=1$")
    a.plot(t, 2 * np.cos(2 * np.pi * 2 * t), color=NAVY, ls="--", label="$A=2$")
    a.set_ylim(-2.5, 2.5)
    a.set_yticks([-2, 0, 2])
    title(a, "改變振幅 $A$（$f$ = 2 Hz，$\\varphi$ = 0）", size=FS_ANN)
    top_legend(a)
    a = axs[1]
    a.plot(t, np.cos(2 * np.pi * 2 * t), color=BLUE, label="$f$ = 2 Hz")
    a.plot(t, np.cos(2 * np.pi * 4 * t), color=NAVY, ls="--", label="$f$ = 4 Hz")
    a.set_ylim(-1.4, 1.4)
    a.set_yticks([-1, 0, 1])
    title(a, "改變頻率 $f$（$A$ = 1，$\\varphi$ = 0）", size=FS_ANN)
    top_legend(a)
    a = axs[2]
    a.plot(t, np.cos(2 * np.pi * 2 * t), color=BLUE, label="$\\varphi$ = 0°")
    a.plot(t, np.cos(2 * np.pi * 2 * t + np.pi / 2), color=NAVY, ls="--", label="$\\varphi$ = 90°")
    a.set_ylim(-1.4, 1.4)
    a.set_yticks([-1, 0, 1])
    title(a, "改變相位 $\\varphi$（$A$ = 1，$f$ = 2 Hz）", size=FS_ANN)
    top_legend(a)
    a.set_xlim(0, 1)
    a.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    a.set_xlabel("時間 $t$（s）")
    fig.supylabel("$x(t)$（任意單位）", fontsize=FS, color=NAVY, x=0.012)
    save(fig, "amplitude_frequency_phase")


# ================================================================ 06
def fig_delay_phase():
    f, tau = 5.0, 0.04
    t = np.linspace(0, 0.3, 3001)
    fig, ax = plt.subplots(figsize=(6.3, 4.4), gridspec_kw=dict(left=0.13, right=0.97, top=0.80, bottom=0.16))
    ax.plot(t, np.cos(2 * np.pi * f * t), color=BLUE, label="發射 $s(t)=\\cos(2\\pi f t)$")
    ax.plot(t, 0.7 * np.cos(2 * np.pi * f * (t - tau)), color=RED, label="接收 $r(t)=0.7\\cos[2\\pi f(t-\\tau)]$")
    for x in (0.2, 0.2 + tau):
        ax.axvline(x, color=GRAY, lw=1.2, ls=":")
    harrow(ax, 0.2, 0.2 + tau, 1.12, "$\\tau$", NAVY, dy=0.03, fs=FS + 2)
    ax.set_ylim(-1.3, 1.45)
    ax.set_xlim(0, 0.3)
    ax.set_xticks([0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3])
    ax.set_xlabel("時間 $t$（s）")
    ax.set_ylabel("振幅（任意單位）")
    ax.legend(loc="lower left", bbox_to_anchor=(0.0, 1.0), ncol=1, frameon=False, fontsize=FS_ANN, borderaxespad=0.2)
    ax.text(0.01, 0.02, "時間域｜$f$ = 5 Hz，$\\tau$ = 0.04 s（示意）", transform=ax.transAxes, ha="left", va="bottom", fontsize=FS_ANN, color=GRAY)
    save(fig, "delay_phase_shift")


# ================================================================ 07
def fig_period_harmonic():
    t = np.linspace(0, 0.03, 4001)
    x = np.sin(2 * np.pi * 100 * t) + 0.5 * np.sin(2 * np.pi * 300 * t)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.4, 5.3),
                                 gridspec_kw=dict(height_ratios=[2.2, 1], hspace=0.75, left=0.11, right=0.97, top=0.91, bottom=0.12))
    a1.axvspan(0, 10, color="#EAF1FB", lw=0)
    a1.axvspan(10, 20, color="#F4F7FC", lw=0)
    a1.plot(t * 1e3, x, color=BLUE)
    for xv in (0, 10, 20):
        a1.axvline(xv, color=GRAY, lw=1.2, ls=":")
    harrow(a1, 0, 10, 1.6, "$T_0$ = 10 ms", NAVY, dy=0.05)
    harrow(a1, 10, 20, 1.6, "$T_0$ = 10 ms", NAVY, dy=0.05)
    a1.set_xlim(0, 30)
    a1.set_ylim(-1.7, 2.3)
    a1.set_yticks([-1, 0, 1])
    a1.set_xticks([0, 10, 20, 30])
    ms_axis(a1)
    a1.set_ylabel("振幅")
    title(a1, "時間域｜週期訊號：$x(t+T_0)=x(t)$", size=FS_ANN)

    fs = [100, 200, 300, 400]
    a2.axhline(0, color=GRAY, lw=1.4)
    a2.plot(fs, [0] * 4, "o", ms=13, mfc="white", mec=GREEN, mew=2.4)
    for i, fv in enumerate(fs, start=1):
        a2.text(fv, 0.5, f"$n$={i}", ha="center", fontsize=FS_ANN, color=GREEN)
    a2.set_xlim(0, 500)
    a2.set_ylim(-0.6, 1.1)
    a2.set_yticks([])
    a2.set_xticks([0, 100, 200, 300, 400, 500])
    a2.set_xlabel("頻率 $f$（Hz）")
    a2.grid(False)
    a2.spines["left"].set_visible(False)
    title(a2, "頻率域｜可能的諧波位置 $f_n=n f_0$（空心＝只標位置）", size=FS_ANN)
    save(fig, "period_harmonic_grid")


# ================================================================ 08
def fig_square_wave():
    t = np.linspace(-np.pi, np.pi, 6001)
    sq = np.sign(t)
    fig, axs = plt.subplots(1, 3, figsize=(12.1, 2.95), sharey=True,
                            gridspec_kw=dict(wspace=0.12, left=0.065, right=0.99, top=0.84, bottom=0.25))
    for ax, N in zip(axs, (1, 3, 10)):
        s = np.zeros_like(t)
        for k in range(N):
            s += np.sin((2 * k + 1) * t) / (2 * k + 1)
        s *= 4 / np.pi
        ax.plot(t, sq, color=GRAY, lw=1.6, ls="--", alpha=0.7, label="理想方波")
        ax.plot(t, s, color=BLUE, lw=2.2, label=f"$S_{{{N}}}(t)$")
        ax.set_xlim(-np.pi, np.pi)
        ax.set_ylim(-1.55, 1.55)
        ax.set_xticks([-np.pi, -np.pi / 2, 0, np.pi / 2, np.pi])
        ax.set_xticklabels(["$-\\pi$", "$-\\pi/2$", "0", "$\\pi/2$", "$\\pi$"])
        title(ax, ("時間域｜" if N == 1 else "") + f"$N$ = {N}（最高諧波 {2 * N - 1}$\\omega_0$）", size=FS_ANN)
        if N == 10:
            i = np.argmax(s[(t > 0) & (t < 0.6)])
            tp = t[(t > 0) & (t < 0.6)][i]
            ax.annotate("Gibbs 現象", xy=(tp, s[(t > 0) & (t < 0.6)][i]), xytext=(0.9, 1.33),
                        fontsize=FS_ANN, color=RED, va="center",
                        arrowprops=dict(arrowstyle="->", color=RED, lw=1.5))
    axs[0].set_ylabel("$x(t)$")
    axs[0].set_yticks([-1, 0, 1])
    axs[1].set_xlabel("$t$（rad，取 $\\omega_0=1$、$T_0=2\\pi$）")
    axs[0].legend(loc="lower right", fontsize=FS_ANN - 1, frameon=True, framealpha=0.9, handlelength=1.4)
    save(fig, "square_wave_fourier_series")


# ================================================================ 09
def fig_dc():
    fig, ax = plt.subplots(figsize=(5.9, 4.8), gridspec_kw=dict(left=0.13, right=0.84, top=0.82, bottom=0.15))
    y0 = 2 * np.sin(2 * np.pi * 100 * t20)
    ax.axhline(0, color=GRAY, lw=1.6, ls="-")
    ax.axhline(3, color=ORANGE, lw=2.2, ls="--")
    ax.plot(t20 * 1e3, y0, color=BLUE_L, lw=2.2, ls="--", label="無 DC：$2\\sin(2\\pi\\cdot100\\,t)$")
    ax.plot(t20 * 1e3, 3 + y0, color=BLUE, lw=2.6, label="DC = 3：$3+2\\sin(2\\pi\\cdot100\\,t)$")
    ax.text(20.3, 3, "$a_0$ = 3", color=ORANGE, fontsize=FS, va="center")
    ax.text(20.3, 0, "$y$ = 0", color=GRAY, fontsize=FS, va="center")
    ax.set_xlim(0, 20)
    ax.set_ylim(-2.7, 5.7)
    ax.set_xticks([0, 5, 10, 15, 20])
    ms_axis(ax)
    ax.set_ylabel("振幅（任意單位）")
    ax.legend(loc="lower left", bbox_to_anchor=(0.0, 1.0), ncol=1, frameon=False, fontsize=FS_ANN, borderaxespad=0.2)
    fig.text(0.97, 0.985, "時間域", ha="right", va="top", fontsize=FS_ANN, color=GRAY)
    save(fig, "dc_offset")


# ================================================================ 10
def fig_orthogonality():
    u = np.linspace(0, 1, 3001)  # t / T0
    c1, c2 = np.cos(2 * np.pi * u), np.cos(4 * np.pi * u)
    p = c1 * c2
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(5.6, 5.3), sharex=True,
                                 gridspec_kw=dict(hspace=0.62, left=0.12, right=0.97, top=0.88, bottom=0.12))
    a1.plot(u, c1, color=BLUE, label="$\\cos(\\omega_0 t)$")
    a1.plot(u, c2, color=NAVY, ls="--", label="$\\cos(2\\omega_0 t)$")
    a1.set_ylim(-1.3, 1.3)
    a1.set_yticks([-1, 0, 1])
    title(a1, "時間域｜兩個基底", size=FS_ANN)
    top_legend(a1)
    a2.fill_between(u, p, 0, where=p >= 0, color=TEAL, alpha=0.35, lw=0, interpolate=True)
    a2.fill_between(u, p, 0, where=p < 0, color=GRAY, alpha=0.35, lw=0, interpolate=True)
    a2.plot(u, p, color=NAVY, lw=2.2)
    a2.axhline(0, color=GRAY, lw=1.2)
    zc = np.concatenate(([0.0], u[1:][np.sign(p[1:]) != np.sign(p[:-1])], [1.0]))
    for lo, hi in zip(zc[:-1], zc[1:]):
        xc = 0.5 * (lo + hi)
        yv = np.interp(xc, u, p)
        if hi - lo > 0.05:
            a2.text(xc, yv * 0.45, "+" if yv > 0 else "−", ha="center", va="center", fontsize=FS + 4, color=NAVY)
    a2.set_ylim(-1.15, 1.15)
    a2.set_yticks([-1, 0, 1])
    a2.set_xlim(0, 1)
    a2.set_xticks([0, 0.25, 0.5, 0.75, 1])
    a2.set_xlabel("$t\\,/\\,T_0$（一個完整基本週期）")
    title(a2, "乘積 $\\cos(\\omega_0 t)\\cos(2\\omega_0 t)$：正負面積抵銷，積分 = 0", size=FS_ANN)
    save(fig, "orthogonality_integrand")


# ================================================================ 11
def fig_coefficient_extraction():
    u = np.linspace(0, 1, 3001)  # t / T0
    x = 2 + 3 * np.cos(2 * np.pi * u) + 4 * np.sin(6 * np.pi * u)
    b = np.cos(2 * np.pi * u)
    p = x * b
    fig, axs = plt.subplots(3, 1, figsize=(4.5, 5.4), sharex=True,
                            gridspec_kw=dict(hspace=1.05, left=0.07, right=0.97, top=0.86, bottom=0.25))
    axs[0].plot(u, x, color=BLUE, lw=2.0)
    title(axs[0], "① 混合訊號 $x(t)$", BLUE, FS_ANN)
    axs[1].plot(u, b, color=TEAL, lw=2.0, ls="--")
    title(axs[1], "② 指定基底 $\\cos(n\\omega_0 t)$，$n$ = 1", TEAL, FS_ANN)
    axs[2].fill_between(u, p, 0, where=p >= 0, color=TEAL, alpha=0.35, lw=0, interpolate=True)
    axs[2].fill_between(u, p, 0, where=p < 0, color=GRAY, alpha=0.35, lw=0, interpolate=True)
    axs[2].plot(u, p, color=NAVY, lw=1.8)
    title(axs[2], "③ 相乘後積分一個完整週期", NAVY, FS_ANN)
    for a in axs:
        a.set_yticks([])
        a.axhline(0, color=GRAY, lw=1)
        a.grid(False)
        a.spines["left"].set_visible(False)
    axs[2].set_xlim(0, 1)
    axs[2].set_xticks([0, 0.5, 1])
    axs[2].set_xlabel("$t\\,/\\,T_0$", labelpad=1)
    fig.text(0.5, 0.07, "④ 積分 $=a_1T_0/2\\ \\Rightarrow\\ a_1=3$",
             ha="center", va="center", fontsize=FS_ANN, color=NAVY,
             bbox=dict(boxstyle="round,pad=0.35", fc="#FFF4E5", ec=ORANGE, lw=1.4))
    fig.text(0.02, 0.995, "例：$x(t)=2+3\\cos(\\omega_0 t)+4\\sin(3\\omega_0 t)$", ha="left", va="top",
             fontsize=FS_ANN - 1, color=GRAY)
    save(fig, "coefficient_extraction")


# ================================================================ 12
def fig_coeff_plane():
    a, b = 2.0, 1.5
    A = np.hypot(a, b)
    phi = np.arctan2(-b, a)
    fig, ax = plt.subplots(figsize=(4.8, 4.6), gridspec_kw=dict(left=0.03, right=0.97, top=0.88, bottom=0.03))
    ax.set_xlim(-0.45, 4.45)
    ax.set_ylim(-2.65, 1.3)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.annotate("", xy=(3.2, 0), xytext=(-0.6, 0), arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.6))
    ax.annotate("", xy=(0, 1.2), xytext=(0, -1.95), arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.6))
    ax.text(3.18, 0.12, "$a_n$", fontsize=FS + 2, ha="right")
    ax.text(0.1, 1.12, "$-b_n$（注意負號）", fontsize=FS, va="top")
    ax.plot([a, a], [0, -b], color=GRAY, ls=":", lw=1.5)
    ax.plot([0, a], [-b, -b], color=GRAY, ls=":", lw=1.5)
    ax.annotate("", xy=(a, -b), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=3, mutation_scale=20))
    ax.plot(a, -b, "o", color=GREEN, ms=7)
    ax.add_patch(Arc((0, 0), 1.5, 1.5, theta1=np.degrees(phi), theta2=0, color=PURPLE, lw=2.4))
    ax.text(0.86, -0.32, "$\\varphi_n$", fontsize=FS + 2, color=PURPLE, va="center")
    ax.text(0.8, -1.05, "$A_n$", fontsize=FS + 2, color=GREEN, ha="right")
    ax.text(a + 0.1, -b - 0.06, "$(a_n,\\,-b_n)$", fontsize=FS, va="top")
    ax.text(a, 0.15, "$a_n=A_n\\cos\\varphi_n$", fontsize=FS_ANN, ha="center", color=GRAY)
    ax.text(a + 0.1, -b / 2, "$-b_n=A_n\\sin\\varphi_n$", fontsize=FS_ANN, ha="left", va="center", color=GRAY)
    ax.text(-0.4, -2.6, f"例：$a_n$ = 2，$b_n$ = 1.5 $\\Rightarrow$ $A_n$ = {A:.1f}，$\\varphi_n$ = {np.degrees(phi):.1f}°",
            fontsize=FS_ANN, va="bottom", color=NAVY)
    fig.text(0.03, 0.985, "係數平面（$\\cos(\\theta+\\varphi)$ 慣例）", ha="left", va="top", fontsize=FS_ANN, color=GRAY)
    save(fig, "coefficient_amplitude_phase")


# ================================================================ 13
def fig_worked_example():
    t = np.linspace(0, 0.02, 4001)
    x = 2 + 3 * np.cos(2 * np.pi * 100 * t) + 4 * np.sin(2 * np.pi * 300 * t)
    fig = plt.figure(figsize=(12.1, 3.6))
    a1 = fig.add_axes([0.055, 0.2, 0.28, 0.58])
    a2 = fig.add_axes([0.40, 0.2, 0.26, 0.58])
    a3 = fig.add_axes([0.73, 0.2, 0.26, 0.58])
    a1.axhline(2, color=ORANGE, ls="--", lw=1.8)
    a1.plot(t * 1e3, x, color=BLUE, lw=2.0)
    a1.text(20.3, 2, "$a_0$", color=ORANGE, fontsize=FS, va="center")
    a1.set_xlim(0, 20)
    a1.set_xticks([0, 10, 20])
    a1.set_ylim(-6, 10)
    ms_axis(a1)
    a1.set_ylabel("$x(t)$")
    title(a1, "時間域｜$x(t)$，0–20 ms\n（$T_0$ = 10 ms，共 2 個週期）", size=FS_ANN)

    stem(a2, [0], [2], ORANGE)
    stem(a2, [100, 300], [3, 4], GREEN)
    for fv, av in ((0, 2), (100, 3), (300, 4)):
        a2.text(fv + 14, av + 0.15, str(av), fontsize=FS, color=GREEN if fv else ORANGE)
    a2.set_xlim(-30, 430)
    a2.set_ylim(0, 4.9)
    a2.set_xticks([0, 100, 200, 300, 400])
    a2.set_yticks([0, 1, 2, 3, 4])
    a2.set_xlabel("頻率 $f$（Hz）")
    a2.set_ylabel("$A_n$")
    title(a2, "頻率域｜單邊 Fourier-series 振幅譜\n（不是雙邊 FT；200 Hz 無成分）", size=FS_ANN)

    a3.axhline(0, color=GRAY, lw=1.2)
    stem(a3, [100, 300], [0, -90], PURPLE)
    a3.text(115, 6, "0°", fontsize=FS, color=PURPLE)
    a3.text(315, -90, "−90°", fontsize=FS, color=PURPLE, va="center")
    a3.set_xlim(0, 430)
    a3.set_ylim(-120, 30)
    a3.set_yticks([-90, -45, 0])
    a3.set_xticks([0, 100, 200, 300, 400])
    a3.set_xlabel("頻率 $f$（Hz）")
    a3.set_ylabel("$\\varphi_n$（度）")
    title(a3, "頻率域｜相位譜 $\\varphi_n$\n（只畫非零交流諧波）", size=FS_ANN)
    save(fig, "worked_example_spectra")


# ================================================================ 14
def fig_periodic_vs_pulse():
    fig = plt.figure(figsize=(12.1, 2.75))
    a1 = fig.add_axes([0.055, 0.25, 0.40, 0.62])
    a2 = fig.add_axes([0.58, 0.25, 0.40, 0.62])
    t = np.linspace(-3, 3, 3001)
    a1.plot(t, np.sin(2 * np.pi * t), color=BLUE)
    a1.text(-3.35, 0, "⋯", fontsize=FS + 6, ha="center", va="center", color=BLUE)
    a1.text(3.35, 0, "⋯", fontsize=FS + 6, ha="center", va="center", color=BLUE)
    a1.set_xlim(-3.6, 3.6)
    a1.set_ylim(-1.4, 1.4)
    a1.set_yticks([-1, 0, 1])
    a1.set_xlabel("$t$（任意單位）")
    title(a1, "時間域｜週期訊號：向兩端永遠重複", size=FS_ANN)
    a1.text(0.99, 0.97, "示意", transform=a1.transAxes, ha="right", va="top", fontsize=FS_ANN, color=GRAY)

    tt = np.linspace(-2, 2, 4001)
    a2.plot(tt, (np.abs(tt) <= 0.5).astype(float), color=BLUE, drawstyle="steps-mid")
    harrow(a2, -0.5, 0.5, 1.15, "$T$", NAVY, dy=0.03)
    a2.set_xlim(-2, 2)
    a2.set_ylim(-0.2, 1.45)
    a2.set_yticks([0, 1])
    a2.set_xticks([-2, -1, -0.5, 0, 0.5, 1, 2])
    a2.set_xticklabels(["", "", "$-T/2$", "0", "$T/2$", "", ""])
    a2.set_xlabel("$t$")
    title(a2, "時間域｜單次矩形脈衝：只出現一次", size=FS_ANN)
    a2.text(0.99, 0.97, "示意", transform=a2.transAxes, ha="right", va="top", fontsize=FS_ANN, color=GRAY)
    save(fig, "periodic_vs_pulse")


# ================================================================ 15
def fig_freq_grid():
    fig, ax = plt.subplots(figsize=(4.4, 2.5), gridspec_kw=dict(left=0.04, right=0.96, top=0.80, bottom=0.30))
    n = np.arange(-3, 4)
    ax.axhline(0, color=NAVY, lw=1.6)
    ax.plot(n, np.zeros_like(n), "o", color=GREEN, ms=9)
    ax.text(-3.75, 0, "⋯", fontsize=FS + 4, va="center", ha="center")
    ax.text(3.75, 0, "⋯", fontsize=FS + 4, va="center", ha="center")
    harrow(ax, 1, 2, 0.45, "$\\Delta f = 1/T$", NAVY, dy=0.08)
    ax.set_xlim(-4.1, 4.1)
    ax.set_ylim(-0.5, 1.2)
    ax.set_yticks([])
    ax.set_xticks([-2, -1, 0, 1, 2])
    ax.set_xticklabels(["$-\\frac{2}{T}$", "$-\\frac{1}{T}$", "0", "$\\frac{1}{T}$", "$\\frac{2}{T}$"], fontsize=FS + 2)
    ax.grid(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.tick_params(axis="x", length=0, pad=6)
    title(ax, "頻率域｜格點 $f_n=n/T$", size=FS_ANN)
    ax.set_xlabel("頻率 $f$", labelpad=2)
    save(fig, "frequency_grid_spacing")


# ================================================================ 16
def fig_riemann():
    f = np.linspace(-3, 3, 3001)
    X = np.sinc(f)       # rect pulse of width 1 s, height 1 → X(f) = sinc(f)
    fig, axs = plt.subplots(3, 1, figsize=(5.0, 5.4), sharex=True,
                            gridspec_kw=dict(hspace=0.7, left=0.13, right=0.97, top=0.87, bottom=0.17))
    for ax, T in zip(axs[:2], (4, 16)):
        df = 1.0 / T
        fn = np.arange(-3 * T, 3 * T + 1) * df
        ax.bar(fn, np.sinc(fn), width=df, color=GREEN_L, edgecolor=GREEN, lw=0.6 if T == 16 else 1.0, alpha=0.75)
        ax.plot(fn, np.sinc(fn), "o", color=GREEN, ms=4 if T == 16 else 6)
        title(ax, f"$T$ = {T}：$\\Delta f$ = 1/{T}；長條面積 = $c_n$", size=FS_ANN)
    axs[2].plot(f, X, color=GREEN, lw=2.4)
    title(axs[2], "$T\\to\\infty$：連續頻率表示 $X(f)$", size=FS_ANN)
    for ax in axs:
        ax.set_ylim(-0.35, 1.15)
        ax.set_yticks([0, 1])
        ax.axhline(0, color=GRAY, lw=1)
    axs[2].set_xlim(-3, 3)
    axs[2].set_xticks([-3, -2, -1, 0, 1, 2, 3])
    axs[2].set_xlabel("頻率 $f$（Hz）")
    fig.supylabel("$X_T(f_n)$ 與 $X(f)$", fontsize=FS, color=NAVY, x=0.01)
    fig.text(0.97, 0.995, "頻率域｜例：寬 1 s 矩形脈衝；$c_n=X_T(f_n)\\,\\Delta f$", ha="right", va="top", fontsize=FS_ANN, color=GRAY)
    fig.text(0.97, 0.008, "形式上的極限；需要適當收斂條件", ha="right", va="bottom", fontsize=FS_ANN, color=RED)
    save(fig, "riemann_sum_to_integral")


# ================================================================ 17
def fig_ft_domain_map():
    fig = plt.figure(figsize=(5.2, 5.45))
    top = fig.add_axes([0, 0.62, 1, 0.38])
    top.set_xlim(0, 5.2)
    top.set_ylim(0, 2.07)
    top.axis("off")
    for x0, txt, col in ((0.15, "時間域\n$x(t)$", BLUE), (3.25, "頻率域\n$X(f)$", GREEN)):
        top.add_patch(FancyBboxPatch((x0, 0.45), 1.8, 1.15, boxstyle="round,pad=0.04,rounding_size=0.15",
                                     fc="white", ec=col, lw=2.4))
        top.text(x0 + 0.9, 1.025, txt, ha="center", va="center", fontsize=FS + 1, color=col, linespacing=1.4)
    top.add_patch(FancyArrowPatch((2.0, 1.3), (3.2, 1.3), arrowstyle="-|>", mutation_scale=20, color=NAVY, lw=2))
    top.add_patch(FancyArrowPatch((3.2, 0.75), (2.0, 0.75), arrowstyle="-|>", mutation_scale=20, color=NAVY, lw=2))
    top.text(2.6, 1.42, "正轉換", ha="center", fontsize=FS_ANN)
    top.text(2.6, 0.4, "逆轉換", ha="center", va="top", fontsize=FS_ANN)

    ax = fig.add_axes([0.05, 0.03, 0.9, 0.56])
    ax.set_xlim(-0.5, 1.6)
    ax.set_ylim(-0.5, 1.4)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.annotate("", xy=(1.55, 0), xytext=(-0.45, 0), arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.5))
    ax.annotate("", xy=(0, 1.35), xytext=(0, -0.3), arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.5))
    ax.text(1.55, 0.04, "Re", ha="right", va="bottom", fontsize=FS)
    ax.text(0.05, 1.33, "Im", va="top", fontsize=FS)
    ang = np.deg2rad(50)
    px, py = 1.15 * np.cos(ang), 1.15 * np.sin(ang)
    ax.annotate("", xy=(px, py), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=3, mutation_scale=20))
    ax.add_patch(Arc((0, 0), 0.6, 0.6, theta1=0, theta2=50, color=PURPLE, lw=2.4))
    ax.text(0.36, 0.13, "$\\varphi(f_1)$", fontsize=FS, color=PURPLE)
    ax.text(px * 0.45 - 0.1, py * 0.45 + 0.12, "$|X(f_1)|$", fontsize=FS, color=GREEN, ha="right")
    ax.text(px + 0.04, py + 0.02, "$X(f_1)$", fontsize=FS)
    ax.text(-0.45, -0.48, "複平面：某一頻率 $f_1$ 的 $X(f_1)$（一般為複數）", fontsize=FS_ANN, color=GRAY, va="bottom")
    save(fig, "ft_domain_map")


# ================================================================ 18
def fig_rect_sinc():
    T = 1.0
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(5.6, 5.35),
                                 gridspec_kw=dict(height_ratios=[1, 1.45], hspace=0.95, left=0.13, right=0.97, top=0.93, bottom=0.12))
    tt = np.linspace(-1.5, 1.5, 3001)
    a1.plot(tt, (np.abs(tt) <= T / 2).astype(float), color=BLUE, drawstyle="steps-mid")
    harrow(a1, -0.5, 0.5, 1.18, "$T$ = 1 s", NAVY, dy=0.03)
    a1.set_xlim(-1.5, 1.5)
    a1.set_ylim(-0.15, 1.6)
    a1.set_yticks([0, 1])
    a1.set_xticks([-1, -0.5, 0, 0.5, 1])
    a1.set_xticklabels(["", "$-T/2$", "0", "$T/2$", ""])
    a1.set_xlabel("時間 $t$", labelpad=1)
    a1.set_ylabel("$x(t)$")
    title(a1, "時間域｜矩形脈衝", size=FS_ANN)

    f = np.linspace(-4, 4, 4001)
    X = T * np.sinc(f * T)
    a2.axhline(0, color=GRAY, lw=1.2)
    a2.plot(f, np.abs(X), color=GREEN_L, lw=2.0, ls="--", label="$|X(f)|$")
    a2.plot(f, X, color=GREEN, lw=2.6, label="$X(f)=T\\,\\mathrm{sinc}(fT)$")
    z = np.array([-3, -2, -1, 1, 2, 3]) / T
    a2.plot(z, np.zeros_like(z), "o", color=GREEN, ms=6, mfc="white", mew=1.8)
    a2.set_xlim(-4, 4)
    a2.set_ylim(-0.35, 1.25)
    a2.set_yticks([0, 0.5, 1])
    a2.set_xticks([-3, -2, -1, 0, 1, 2, 3])
    a2.set_xticklabels(["$-\\frac{3}{T}$", "$-\\frac{2}{T}$", "$-\\frac{1}{T}$", "0", "$\\frac{1}{T}$", "$\\frac{2}{T}$", "$\\frac{3}{T}$"])
    a2.set_xlabel("頻率 $f$", labelpad=1)
    a2.set_ylabel("$X(f)$")
    a2.legend(loc="upper right", fontsize=FS_ANN, frameon=False, handlelength=1.6, borderaxespad=0.1)
    a2.text(-0.25, 1.0, "$X(0)=T$", fontsize=FS_ANN, color=GREEN, va="center", ha="right")
    title(a2, "頻率域｜此圖畫實值 $X(f)$（有負旁瓣）；\n振幅頻譜 $|X(f)|$ 不會有負值", size=FS_ANN)
    save(fig, "rect_pulse_sinc")


# ================================================================ 19
def car(ax, x, y, s=1.0, color=GRAY):
    ax.add_patch(FancyBboxPatch((x - 0.55 * s, y - 0.18 * s), 1.1 * s, 0.38 * s,
                                boxstyle="round,pad=0.02,rounding_size=0.08", fc="#D9DEE6", ec=color, lw=1.8))
    ax.add_patch(FancyBboxPatch((x - 0.3 * s, y + 0.18 * s), 0.55 * s, 0.25 * s,
                                boxstyle="round,pad=0.02,rounding_size=0.08", fc="#D9DEE6", ec=color, lw=1.8))
    for dx in (-0.32, 0.32):
        ax.add_patch(Circle((x + dx * s, y - 0.2 * s), 0.11 * s, fc=NAVY, ec=NAVY))


def antenna(ax, x, y, s=1.0):
    ax.plot([x, x], [y - 0.55 * s, y], color=NAVY, lw=2.4)
    ax.plot([x - 0.25 * s, x + 0.25 * s], [y - 0.55 * s, y - 0.55 * s], color=NAVY, lw=2.4)
    ax.add_patch(Arc((x, y + 0.15 * s), 0.7 * s, 0.7 * s, theta1=200, theta2=340, color=NAVY, lw=3))


def fig_radar_summary():
    fig = plt.figure(figsize=(5.4, 5.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 5.4)
    ax.set_ylim(0, 5.4)
    ax.axis("off")
    antenna(ax, 0.7, 4.1)
    ax.text(0.25, 3.05, "單站雷達（收發同處）", ha="left", va="top", fontsize=FS_ANN, color=NAVY)
    car(ax, 4.55, 3.95, 0.9)
    ax.text(4.55, 3.05, "目標", ha="center", va="top", fontsize=FS_ANN, color=NAVY)
    ax.add_patch(FancyArrowPatch((4.95, 4.75), (5.35, 4.75), arrowstyle="-|>", mutation_scale=14, color=NAVY, lw=1.8))
    ax.text(5.15, 4.86, "$v_r$", ha="center", fontsize=FS, color=NAVY)
    ax.add_patch(FancyArrowPatch((1.2, 4.55), (3.85, 4.55), arrowstyle="-|>", mutation_scale=18, color=BLUE, lw=2.4))
    ax.add_patch(FancyArrowPatch((3.85, 3.75), (1.2, 3.75), arrowstyle="-|>", mutation_scale=18, color=RED, lw=2.4))
    ax.text(2.5, 4.67, "發射", ha="center", fontsize=FS_ANN, color=BLUE)
    ax.text(2.5, 3.62, "回波", ha="center", va="top", fontsize=FS_ANN, color=RED)
    ax.text(2.7, 2.45, "延遲 $\\tau$ → 相位因子 $e^{-j2\\pi f\\tau}$", ha="center", fontsize=FS, color=NAVY)
    ax.text(2.7, 1.95, "運動 $v_r$ → 都卜勒頻移 $f_D$", ha="center", fontsize=FS, color=NAVY)
    # mind map
    labels = ["Time", "Fourier", "Spectrum", "Radar\ninterpretations"]
    ws = [0.8, 1.0, 1.15, 1.5]
    cols = [BLUE, TEAL, GREEN, RED]
    gap, x0, yc = 0.28, 0.06, 1.0
    for w, lab, c in zip(ws, labels, cols):
        ax.add_patch(FancyBboxPatch((x0, yc - 0.4), w, 0.8,
                                    boxstyle="round,pad=0.02,rounding_size=0.12", fc="white", ec=c, lw=2))
        ax.text(x0 + w / 2, yc, lab, ha="center", va="center", fontsize=FS_ANN, color=c, linespacing=1.1)
        if lab != labels[-1]:
            ax.add_patch(FancyArrowPatch((x0 + w + 0.02, yc), (x0 + w + gap - 0.02, yc), arrowstyle="-|>",
                                         mutation_scale=13, color=NAVY, lw=1.6))
        x0 += w + gap
    ax.text(5.3, 0.25, "示意圖：非量測結果", ha="right", fontsize=FS_ANN - 2, color=GRAY)
    save(fig, "radar_summary")


# ================================================================ A3
def fig_round_trip_phase():
    fig = plt.figure(figsize=(6.0, 4.2))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 6.0)
    ax.set_ylim(0, 4.2)
    ax.set_aspect("equal")
    ax.axis("off")
    antenna(ax, 0.55, 3.15, 0.85)
    ax.add_patch(Circle((3.35, 2.9), 0.13, color=RED))
    ax.text(3.35, 2.6, "目標", ha="center", va="top", fontsize=FS_ANN, color=RED)
    ax.add_patch(FancyArrowPatch((0.95, 3.45), (3.1, 3.45), arrowstyle="-|>", mutation_scale=16, color=BLUE, lw=2.2))
    ax.add_patch(FancyArrowPatch((3.1, 2.4), (0.95, 2.4), arrowstyle="-|>", mutation_scale=16, color=RED, lw=2.2))
    ax.text(2.0, 3.56, "去程 $R$", ha="center", fontsize=FS_ANN, color=BLUE)
    ax.text(2.0, 2.28, "回程 $R$", ha="center", va="top", fontsize=FS_ANN, color=RED)
    ax.text(1.95, 1.55, "總路徑 $2R$ $\\Rightarrow$ $\\tau = 2R/c$", ha="center", fontsize=FS, color=NAVY)
    # phase circle
    cx, cy, r = 4.9, 2.75, 0.85
    ax.add_patch(Circle((cx, cy), r, fill=False, ec=PURPLE, lw=2))
    ax.plot([cx - r - 0.1, cx + r + 0.1], [cy, cy], color=GRAY, lw=1)
    ax.plot([cx, cx], [cy - r - 0.1, cy + r + 0.1], color=GRAY, lw=1)
    ax.text(cx + r + 0.12, cy, "0", va="center", fontsize=FS_ANN, color=GRAY)
    ax.text(cx, cy + r + 0.12, "$\\pi/2$", ha="center", fontsize=FS_ANN, color=GRAY)
    ax.text(cx - r - 0.12, cy, "$\\pi$", ha="right", va="center", fontsize=FS_ANN, color=GRAY)
    ang = np.deg2rad(-60)
    px, py = cx + r * np.cos(ang), cy + r * np.sin(ang)
    ax.plot([cx, px], [cy, py], color=PURPLE, lw=2)
    ax.plot(px, py, "o", color=PURPLE, ms=9)
    ax.text(cx, cy - r - 0.25, "相位圓 $0\\sim 2\\pi$", ha="center", va="top", fontsize=FS_ANN, color=PURPLE)
    ax.text(3.0, 0.55, "$\\tau,\\ \\tau+\\frac{1}{f_c},\\ \\tau+\\frac{2}{f_c},\\ \\ldots$ → 同一相位點（mod $2\\pi$）",
            ha="center", fontsize=FS_ANN, color=NAVY)
    ax.text(5.95, 0.08, "示意圖", ha="right", fontsize=FS_ANN - 2, color=GRAY)
    save(fig, "radar_round_trip_phase")


if __name__ == "__main__":
    print("Generating figures ...")
    fig_cover()
    fig_roadmap_radar()
    fig_signal_components()
    fig_time_vs_spectrum()
    fig_amp_freq_phase()
    fig_delay_phase()
    fig_period_harmonic()
    fig_square_wave()
    fig_dc()
    fig_orthogonality()
    fig_coefficient_extraction()
    fig_coeff_plane()
    fig_worked_example()
    fig_periodic_vs_pulse()
    fig_freq_grid()
    fig_riemann()
    fig_ft_domain_map()
    fig_rect_sinc()
    fig_radar_summary()
    fig_round_trip_phase()
    with open(os.path.join(OUT, "manifest.json"), "w") as fh:
        json.dump(MANIFEST, fh, indent=1)
    print("done:", len(MANIFEST), "figures")
