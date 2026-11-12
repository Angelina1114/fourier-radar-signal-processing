"""
verify_math.py — numerical check of every formula / number shown on the slides
(spec section F 數學正確性驗收清單).  Run: python3 assets/verify_math.py
Writes assets/math_verification.txt and exits non-zero on any failure.
"""
import os
import sys

import numpy as np

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "math_verification.txt")
lines, fails = [], 0


def check(name, got, want, tol=1e-6):
    global fails
    ok = np.allclose(got, want, atol=tol, rtol=0)
    fails += not ok
    lines.append(f"[{'PASS' if ok else 'FAIL'}] {name}: got {np.round(got, 6)} expected {want}")


def integ(y, t):
    return np.trapezoid(y, t)


# ---- Slide 09 / convention: a0 is the mean (no a0/2)
T0 = 0.01
t = np.linspace(0, T0, 200001)
x = 3 + 2 * np.sin(2 * np.pi * 100 * t)
check("S09 a0 = (1/T0)∫x dt for 3+2sin(2π100t)", integ(x, t) / T0, 3.0)

# ---- Slide 13 worked example
w0 = 2 * np.pi / T0
x = 2 + 3 * np.cos(2 * np.pi * 100 * t) + 4 * np.sin(2 * np.pi * 300 * t)
a = lambda n: 2 / T0 * integ(x * np.cos(n * w0 * t), t)
b = lambda n: 2 / T0 * integ(x * np.sin(n * w0 * t), t)
check("S13 a0", integ(x, t) / T0, 2.0)
check("S13 (a1,b1,a2,b2,a3,b3)", [a(1), b(1), a(2), b(2), a(3), b(3)], [3, 0, 0, 0, 0, 4])
A = lambda n: np.hypot(a(n), b(n))
phi = lambda n: np.degrees(np.arctan2(-b(n), a(n)))
check("S13 A1, A3", [A(1), A(3)], [3, 4])
check("S13 φ1, φ3 (deg) via atan2(-bn, an)", [phi(1), phi(3)], [0, -90], tol=1e-4)
check("S13 no 200 Hz component (A2)", A(2), 0.0)

# ---- Slide 12 identity and example
an, bn = 2.0, 1.5
An, ph = np.hypot(an, bn), np.arctan2(-bn, an)
th = np.linspace(0, 10, 1001)
check("S12 an cos+bn sin = An cos(θ+φn)", an * np.cos(th) + bn * np.sin(th), An * np.cos(th + ph))
check("S12 example An, φn(deg)", [An, np.degrees(ph)], [2.5, -36.869898])

# ---- Slide 10 / A1 orthogonality on one full period
u = np.linspace(0, T0, 200001)
c = lambda m: np.cos(m * w0 * u)
s = lambda m: np.sin(m * w0 * u)
check("S10 ∫cos(ω0t)cos(2ω0t) = 0", integ(c(1) * c(2), u), 0.0)
check("S10 ∫cos²(nω0t) = T0/2 (n=1,3)", [integ(c(1) ** 2, u), integ(c(3) ** 2, u)], [T0 / 2, T0 / 2])
check("A1 ∫sin·cos = 0 (m=n=2)", integ(s(2) * c(2), u), 0.0)
check("A1 ∫sin(2)sin(3) = 0", integ(s(2) * s(3), u), 0.0)

# ---- Slide 11 example a1 = 3 for x = 2+3cos(ω0t)+4sin(3ω0t)
x11 = 2 + 3 * c(1) + 4 * s(3)
check("S11 ∫x cos(ω0t) dt = a1 T0/2 with a1=3", integ(x11 * c(1), u), 3 * T0 / 2)

# ---- Slide 06 delay → phase
f, tau = 5.0, 0.04
tt = np.linspace(0, 1, 1001)
check("S06 cos[2πf(t−τ)] = cos(2πft − 2πfτ)", np.cos(2 * np.pi * f * (tt - tau)), np.cos(2 * np.pi * f * tt - 2 * np.pi * f * tau))
check("S06 Δφ = −2πfτ = −72°", np.degrees(-2 * np.pi * f * tau), -72.0)

# ---- Slide 08 square wave partial sums: mean of jump at t=0 and value ±1 inside
tq = np.array([0.0, np.pi / 2, -np.pi / 2])
SN = 4 / np.pi * sum(np.sin((2 * k + 1) * tq) / (2 * k + 1) for k in range(20000))
check("S08 S_N(0)=0 (jump midpoint), S_N(±π/2)→±1", SN, [0, 1, -1], tol=1e-3)


# ---- Slide 18 rect pulse FT, time shift
def ft(xfun, fs, lo, hi, n=200001):
    tg = np.linspace(lo, hi, n)
    xv = xfun(tg)
    return np.array([integ(xv * np.exp(-2j * np.pi * fv * tg), tg) for fv in fs])


for T in (1.0, 2.0):
    fs = np.array([0, 0.3, 1 / T, 1.7 / T, 2 / T])
    X = ft(lambda q: (np.abs(q) <= T / 2).astype(float), fs, -T / 2, T / 2)
    check(f"S18 X(f) = T sinc(fT), T={T}", X, T * np.sinc(fs * T), tol=2e-4)
check("S18 normalized sinc: numpy.sinc(u)=sin(πu)/(πu)", np.sinc(0.37), np.sin(np.pi * 0.37) / (np.pi * 0.37))
fs = np.array([0.2, 0.9, 1.4])
tau = 0.3
Xs = ft(lambda q: (np.abs(q - tau) <= 0.5).astype(float), fs, -0.2, 0.8)
X0 = ft(lambda q: (np.abs(q) <= 0.5).astype(float), fs, -0.5, 0.5)
check("S18 x(t−τ) ↔ X(f)e^{−j2πfτ}", Xs, X0 * np.exp(-2j * np.pi * fs * tau), tol=2e-4)
check("S18 |X| unchanged by pure delay", np.abs(Xs), np.abs(X0), tol=2e-4)
check("S18 X(f) real with negative side-lobe at f=1.5/T (T=1)", float(np.sinc(1.5) < 0), 1.0)

# ---- Slide 15 c_n = X_T(f_n) Δf (rect of width 1 inside period T=4)
T = 4.0
tg = np.linspace(-T / 2, T / 2, 400001)
xv = (np.abs(tg) <= 0.5).astype(float)
for n in (0, 1, 3):
    fn = n / T
    cn = integ(xv * np.exp(-2j * np.pi * fn * tg), tg) / T
    XT = integ(xv * np.exp(-2j * np.pi * fn * tg), tg)
    check(f"S15 c_{n} = X_T(f_{n})·Δf (T=4)", cn, XT * (1 / T))
check("S15 Δf = 1/T", 1 / T, 0.25)
# complex <-> trig: c_n = (a_n - j b_n)/2 for the S13 signal
cn13 = integ(x * np.exp(-1j * 3 * w0 * t), t) / T0
check("S15 notes c_n=(a_n−j b_n)/2 (S13 signal, n=3)", cn13, (0 - 1j * 4) / 2)

# ---- Slide 16 inverse FT reconstructs rect at a continuity point and jump midpoint
fgrid = np.linspace(-400, 400, 800001)
Xf = np.sinc(fgrid)
for t0, want in ((0.0, 1.0), (0.5, 0.5), (0.8, 0.0)):
    check(f"S16 x({t0}) = ∫X(f)e^{{j2πft}}df", integ(Xf * np.exp(2j * np.pi * fgrid * t0), fgrid).real, want, tol=3e-3)

# ---- Appendix A3 radar relations (symbolic consistency with arbitrary numbers)
cl, fc, R = 299792458.0, 10e9, 7.3
lam, tau = cl / fc, 2 * R / cl
check("A3 R = cτ/2", cl * tau / 2, R)
check("A3 −2πf_c τ = −4πR/λ", -2 * np.pi * fc * tau, -4 * np.pi * R / lam)
check("A3 phase ambiguity: R and R+λ/2 give same phase mod 2π",
      np.mod(-4 * np.pi * R / lam, 2 * np.pi), np.mod(-4 * np.pi * (R + lam / 2) / lam, 2 * np.pi))

# ---- Website additions: physical-meaning boxes and the linear-algebra page
# sinusoid mean power A²/2
tp = np.linspace(0, 1, 200001)
check("Phys: mean of (A sin)^2 = A^2/2 (A=0.5)", integ((0.5 * np.sin(2 * np.pi * 7 * tp)) ** 2, tp), 0.125)
# S13 Parseval: mean x² = a0² + ½Σ(an²+bn²) = 4 + 4.5 + 8
x13 = 2 + 3 * np.cos(2 * np.pi * 100 * t) + 4 * np.sin(2 * np.pi * 300 * t)
check("Phys S13 Parseval mean x^2 = 16.5", integ(x13 ** 2, t) / T0, 16.5, tol=1e-5)
# orthogonal components: power of sum = sum of powers
check("Phys S10 cross term averages to 0", integ(np.cos(w0 * t) * np.cos(2 * w0 * t), t) / T0, 0.0)
# 10 GHz, target moves 1.5 mm -> round trip 3 mm -> phase change 36°
lam10 = cl / 10e9
check("Phys S6 10 GHz wavelength ≈ 3 cm", lam10, 0.03, tol=2e-4)
check("Phys S6 ΔR=1.5 mm → |Δφ| = 4πΔR/λ (deg, λ=3 cm)", np.degrees(4 * np.pi * 1.5e-3 / 0.03), 36.0)
# rect pulse main lobe width 2/T, FT Parseval ∫|X|² df = ∫|x|² dt = T
check("Phys S18 sinc zeros at ±1/T (T=1)", [np.sinc(1.0), np.sinc(-1.0)], [0, 0])
ff = np.linspace(-2000, 2000, 4000001)
check("Phys S16 Parseval ∫|T sinc(fT)|² df = T (T=1)", integ(np.sinc(ff) ** 2, ff), 1.0, tol=2e-3)
# Doppler: v = λ f_D / 2 is the inverse of |f_D| ≈ 2|v|/λ
vr = 12.0
check("Phys S19 v = λ f_D / 2", lam10 * (2 * vr / lam10) / 2, vr)
# Linear-algebra page: projection = coordinate iff basis orthogonal (default x=(1.8,1.6), |e1|=1.5, |e2|=1.2)
xv2 = np.array([1.8, 1.6])
for deg_, want_same in ((90, True), (60, False)):
    th_ = np.radians(deg_)
    e1, e2 = np.array([1.5, 0.0]), 1.2 * np.array([np.cos(th_), np.sin(th_)])
    coords = np.linalg.solve(np.column_stack([e1, e2]), xv2)
    proj = np.array([xv2 @ e1 / (e1 @ e1), xv2 @ e2 / (e2 @ e2)])
    check(f"LA {deg_}°: projection equals coordinates is {want_same}", float(np.allclose(coords, proj)), float(want_same))
check("LA 90°: (c1, c2) = (1.2, 1.333)", np.linalg.solve(np.array([[1.5, 0], [0, 1.2]]), xv2), [1.2, 1.6 / 1.2])
th60 = np.radians(60)
e1, e2 = np.array([1.5, 0.0]), 1.2 * np.array([np.cos(th60), np.sin(th60)])
check("LA 60°: (c1, c2, ĉ1, ĉ2) shown on page", [*np.linalg.solve(np.column_stack([e1, e2]), xv2), xv2 @ e1 / (e1 @ e1), xv2 @ e2 / (e2 @ e2)],
      [0.58, 1.54, 1.20, 1.90], tol=5e-3)
# S11 demo numbers: <x, cos ω0t> = 1.5 T0, <x, sin 3ω0t> = 2 T0, <x, 1> = 2 T0
check("S11 <x,cos ω0t>/T0 = 1.5", integ(x13 * np.cos(w0 * t), t) / T0, 1.5, tol=1e-5)
check("S11 <x,sin 3ω0t>/T0 = 2", integ(x13 * np.sin(3 * w0 * t), t) / T0, 2.0, tol=1e-5)
check("S11 a0 = <x,1>/||1||² = 2", integ(x13, t) / T0, 2.0)

lines.append(f"\n{len(lines) - fails} passed, {fails} failed")
open(OUT, "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
sys.exit(1 if fails else 0)
