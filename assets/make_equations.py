"""
make_equations.py
-----------------
Typesets every display equation of the deck with real LaTeX (amsmath, Latin Modern)
and writes, for each equation id:

  assets/equations/<id>.png   600 dpi, transparent (placed in the PPTX at natural size)
  assets/equations/<id>.svg   vector version (glyphs as paths)
  assets/equations/manifest.json  {id: {latex, pt, w, h}}  (w, h in inches)

The LaTeX source of every equation is also copied into the speaker notes of the
slide that uses it, so formulas can be re-typed / copied.

Requires: latex, dvipng, dvisvgm (TeX Live).
Run:      python3 assets/make_equations.py
"""
import json
import os
import shutil
import subprocess
import tempfile

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "equations")
os.makedirs(OUT, exist_ok=True)
DPI = 600

# id: (latex, point size).  Conventions (spec A-5 / 教學與精度約定):
#   t, f, ω, T₀, ω₀ = 2π/T₀, λ, j;  a₀ is the MEAN (no a₀/2);
#   φₙ = atan2(−bₙ, aₙ);  X(f) = ∫ x(t) e^{−j2πft} dt  (no extra 2π factors)
EQ = {
    # Slide 03 / 04
    "s03_x": (r"x(t)=\sin(2\pi\cdot 100\,t)+0.5\,\sin(2\pi\cdot 300\,t)", 26),
    # Slide 05
    "s05_main": (r"x(t)=A\cos(2\pi f t+\varphi)", 32),
    # Slide 06
    "s06_s": (r"s(t)=A\cos(2\pi f t)", 27),
    "s06_r": (r"r(t)=A_r\cos\!\big[2\pi f\,(t-\tau)\big]", 27),
    "s06_r2": (r"r(t)=A_r\cos(2\pi f t-2\pi f\tau)", 27),
    "s06_dphi": (r"\Delta\varphi=-2\pi f\tau \pmod{2\pi}", 30),
    # Slide 07
    "s07_per": (r"x(t+T_0)=x(t)", 28),
    "s07_f0": (r"f_0=\frac{1}{T_0},\qquad \omega_0=\frac{2\pi}{T_0}", 27),
    "s07_fn": (r"f_n=n\,f_0", 27),
    # Slide 08
    "s08_fs": (r"x(t)\sim a_0+\sum_{n=1}^{\infty}\Big[a_n\cos(n\omega_0 t)+b_n\sin(n\omega_0 t)\Big]", 28),
    # Slide 09
    "s09_a0": (r"a_0=\frac{1}{T_0}\int_0^{T_0}x(t)\,dt", 30),
    "s09_ex": (r"x(t)=3+2\sin(2\pi\cdot 100\,t)\;\;\Longrightarrow\;\; a_0=3", 26),
    # Slide 10
    "s10_ip": (r"\langle u,v\rangle=\int_0^{T_0}u(t)\,v(t)\,dt", 28),
    "s10_orth": (r"\langle u,v\rangle=0", 26),
    "s10_cc": (r"\int_0^{T_0}\cos(m\omega_0 t)\cos(n\omega_0 t)\,dt="
               r"\begin{cases}0, & m\neq n\\[4pt] \dfrac{T_0}{2}, & m=n\geq 1\end{cases}", 25),
    # Slide 11
    "s11_1": (r"x(t)=a_0+\sum_{k=1}^{\infty}\Big[a_k\cos(k\omega_0 t)+b_k\sin(k\omega_0 t)\Big]", 25),
    "s11_3": (r"\int_0^{T_0}x(t)\cos(n\omega_0 t)\,dt=a_n\cdot\frac{T_0}{2}", 26),
    "s11_an": (r"a_n=\frac{2}{T_0}\int_0^{T_0}x(t)\cos(n\omega_0 t)\,dt", 26),
    "s11_bn": (r"b_n=\frac{2}{T_0}\int_0^{T_0}x(t)\sin(n\omega_0 t)\,dt", 26),
    # Slide 12
    "s12_id": (r"a_n\cos(n\omega_0 t)+b_n\sin(n\omega_0 t)=A_n\cos(n\omega_0 t+\varphi_n)", 27),
    "s12_ab": (r"a_n=A_n\cos\varphi_n,\qquad b_n=-A_n\sin\varphi_n", 26),
    "s12_A": (r"A_n=\sqrt{a_n^2+b_n^2}", 26),
    "s12_phi": (r"\varphi_n=\operatorname{atan2}(-b_n,\,a_n)\quad (A_n>0)", 26),
    # Slide 13
    "s13_x": (r"x(t)=2+3\cos(2\pi\cdot 100\,t)+4\sin(2\pi\cdot 300\,t)", 27),
    "s13_par": (r"f_0=100\ \mathrm{Hz};\qquad a_0=2,\quad a_1=3,\quad b_3=4", 25),
    # Slide 15
    "s15_xT": (r"x_T(t)=\sum_{n\in\mathbb{Z}}c_n\,e^{\,j2\pi f_n t},\qquad f_n=\frac{n}{T}", 26),
    "s15_cn": (r"c_n=\frac{1}{T}\int_{-T/2}^{T/2}x_T(t)\,e^{-j2\pi f_n t}\,dt", 26),
    "s15_df": (r"\Delta f=\frac{1}{T}", 26),
    "s15_XTf": (r"X_T(f)=\int_{-T/2}^{T/2}x(t)\,e^{-j2\pi f t}\,dt", 26),
    "s15_res": (r"c_n=X_T(f_n)\,\Delta f", 30),
    # Slide 16 / 17
    "s16_sum": (r"x_T(t)=\sum_{n\in\mathbb{Z}}X_T(f_n)\,e^{\,j2\pi f_n t}\,\Delta f", 26),
    "s16_inv": (r"x(t)=\int_{-\infty}^{\infty}X(f)\,e^{\,j2\pi f t}\,df", 28),
    "s16_fwd": (r"X(f)=\int_{-\infty}^{\infty}x(t)\,e^{-j2\pi f t}\,dt", 28),
    "s17_euler": (r"e^{\,j\theta}=\cos\theta+j\sin\theta", 26),
    "s17_polar": (r"X(f)=|X(f)|\,e^{\,j\varphi(f)}", 26),
    # Slide 18
    "s18_shift": (r"x(t-\tau)\;\longleftrightarrow\;X(f)\,e^{-j2\pi f\tau}", 28),
    "s18_rect": (r"x(t)=\begin{cases}1, & |t|\leq T/2\\ 0, & |t|>T/2\end{cases}", 25),
    "s18_ft": (r"X(f)=\int_{-T/2}^{T/2}e^{-j2\pi f t}\,dt=T\,\operatorname{sinc}(fT)", 26),
    "s18_sinc": (r"\operatorname{sinc}(u)=\frac{\sin(\pi u)}{\pi u},\qquad \operatorname{sinc}(0)=1", 25),
    # Appendix A1
    "a1_cc": (r"\cos A\cos B=\tfrac{1}{2}\big[\cos(A-B)+\cos(A+B)\big]", 26),
    "a1_ss": (r"\sin A\sin B=\tfrac{1}{2}\big[\cos(A-B)-\cos(A+B)\big]", 26),
    "a1_k": (r"\int_0^{T_0}\cos(k\omega_0 t)\,dt=0\qquad (k\in\mathbb{Z},\ k\neq 0)", 26),
    "a1_sq": (r"\int_0^{T_0}\cos^2(n\omega_0 t)\,dt=\int_0^{T_0}\frac{1+\cos(2n\omega_0 t)}{2}\,dt=\frac{T_0}{2}\qquad (n\geq 1)", 25),
    "a1_mn": (r"\int_0^{T_0}\cos(m\omega_0 t)\cos(n\omega_0 t)\,dt"
              r"=\tfrac12\int_0^{T_0}\cos\big((m-n)\omega_0 t\big)dt+\tfrac12\int_0^{T_0}\cos\big((m+n)\omega_0 t\big)dt=0", 25),
    # Appendix A2
    "a2_SN": (r"S_N(t)=a_0+\sum_{k=1}^{N}\Big[a_k\cos(k\omega_0 t)+b_k\sin(k\omega_0 t)\Big]", 26),
    "a2_ip": (r"\big\langle S_N,\cos(n\omega_0 t)\big\rangle=a_n\,\frac{T_0}{2}\qquad (N\geq n)", 26),
    "a2_cs": (r"\big|\langle S_N-x,\cos(n\omega_0 t)\rangle\big|\leq\|S_N-x\|_2\,\|\cos(n\omega_0 t)\|_2"
              r"\;\xrightarrow[N\to\infty]{}\;0", 26),
    "a2_an": (r"a_n=\frac{2}{T_0}\big\langle x,\cos(n\omega_0 t)\big\rangle", 26),
    # Appendix A3
    "a3_tau": (r"\tau=\frac{2R}{c}\quad\Longrightarrow\quad R=\frac{c\,\tau}{2}", 26),
    "a3_phi": (r"\Delta\varphi=-2\pi f_c\,\tau=-\frac{4\pi R}{\lambda}\pmod{2\pi}", 26),
    "a3_fd": (r"|f_D|\approx\frac{2\,|v_r|}{\lambda}\qquad (|v_r|\ll c)", 26),
}

TEMPLATE = r"""\documentclass[border=2pt]{standalone}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{amsmath,amssymb,mathtools}
\usepackage{xcolor}
\definecolor{ink}{HTML}{1B2A4A}
\DeclareMathOperator{\sinc}{sinc}
\begin{document}
\fontsize{%(pt)s}{%(lead)s}\selectfont\color{ink}$\displaystyle %(tex)s$
\end{document}
"""


def render(key, tex, pt, work):
    base = os.path.join(work, key)
    with open(base + ".tex", "w") as fh:
        fh.write(TEMPLATE % {"pt": pt, "lead": round(pt * 1.2, 1), "tex": tex})
    subprocess.run(["latex", "-interaction=nonstopmode", "-halt-on-error", key + ".tex"], cwd=work,
                   check=True, stdout=subprocess.DEVNULL)
    png = os.path.join(OUT, key + ".png")
    subprocess.run(["dvipng", "-q", "-T", "tight", "-D", str(DPI), "-bg", "Transparent", "-o", png, key + ".dvi"],
                   cwd=work, check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["dvisvgm", "--no-fonts", "--exact-bbox", "-o", os.path.join(OUT, key + ".svg"), key + ".dvi"],
                   cwd=work, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    w, h = Image.open(png).size
    return {"latex": tex, "pt": pt, "w": round(w / DPI, 3), "h": round(h / DPI, 3)}


if __name__ == "__main__":
    work = tempfile.mkdtemp()
    manifest = {}
    try:
        for key, (tex, pt) in EQ.items():
            manifest[key] = render(key, tex, pt, work)
            print(f"  {key:10s} {manifest[key]['w']:5.2f} x {manifest[key]['h']:4.2f} in  ({pt} pt)")
    finally:
        shutil.rmtree(work, ignore_errors=True)
    with open(os.path.join(OUT, "manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=1, ensure_ascii=False)
    print("done:", len(manifest), "equations")
