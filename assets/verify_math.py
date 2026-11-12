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

lines.append(f"\n{len(lines) - fails} passed, {fails} failed")
open(OUT, "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
sys.exit(1 if fails else 0)
