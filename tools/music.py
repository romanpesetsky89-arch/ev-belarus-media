# Generates an original royalty-free upbeat electronic track + whooshes at scene changes.
# usage: python3 music.py out.wav seconds "4,8,12.5,17,21.5"
import sys, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter
SR = 44100
out, dur = sys.argv[1], float(sys.argv[2])
cuts = [float(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 else []
BPM = 122; beat = 60 / BPM
N = int(SR * dur); t = np.arange(N) / SR
mix = np.zeros(N)
rng = np.random.default_rng(7)

def place(sig, start, gain=1.0):
    i = int(start * SR)
    if i >= N: return
    j = min(N, i + len(sig)); mix[i:j] += sig[:j - i] * gain

def env(n, a=0.005, d=0.2):
    x = np.arange(n) / SR
    return np.minimum(x / a, 1) * np.exp(-x / d)

def lp(x, f):
    b, a = butter(2, f / (SR / 2), 'low'); return lfilter(b, a, x)

def hp(x, f):
    b, a = butter(2, f / (SR / 2), 'high'); return lfilter(b, a, x)

# kick
kn = int(0.35 * SR); kx = np.arange(kn) / SR
kick = np.sin(2 * np.pi * (50 + 110 * np.exp(-kx * 30)) * kx) * np.exp(-kx * 9)
# hat
hn = int(0.06 * SR); hat = hp(rng.standard_normal(hn), 7000) * env(hn, 0.001, 0.02)
# clap
cn = int(0.2 * SR); clap = lp(hp(rng.standard_normal(cn), 1200), 5000) * env(cn, 0.002, 0.06)

# chord progression (Am - F - C - G), 2 bars each
prog = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
bass_notes = [45, 41, 48, 43]
mf = lambda m: 440 * 2 ** ((m - 69) / 12)
bar = 4 * beat
nbars = int(dur / bar) + 2
for b_ in range(nbars):
    st = b_ * bar
    ch = prog[(b_ // 2) % 4]; bn = bass_notes[(b_ // 2) % 4]
    intro = b_ < 1
    for k in range(4):
        bt = st + k * beat
        if not intro: place(kick, bt, 0.9)
        if k in (1, 3) and not intro: place(clap, bt, 0.35)
        place(hat, bt + beat / 2, 0.25)
        place(hat, bt + beat / 4 * 3, 0.12)
        # offbeat pluck bass
        n = int(beat / 2 * SR); x = np.arange(n) / SR
        f = mf(bn)
        saw = 2 * ((x * f) % 1) - 1
        place(lp(saw, 900) * env(n, 0.003, 0.12), bt + beat / 2, 0.35)
    # pad
    n = int(bar * SR); x = np.arange(n) / SR
    pad = sum(np.sin(2 * np.pi * mf(m) * x) + 0.3 * np.sin(2 * np.pi * mf(m) * 2.003 * x) for m in ch)
    pad *= np.minimum(x / 0.3, 1) * np.minimum((bar - x) / 0.3, 1)
    place(pad, st, 0.06)
    # arp
    for s in range(8):
        n2 = int(beat / 2 * SR); x2 = np.arange(n2) / SR
        m = ch[s % 3] + 12 * (1 + (s // 3) % 2)
        sq = np.sign(np.sin(2 * np.pi * mf(m) * x2))
        place(lp(sq, 3000) * env(n2, 0.002, 0.08), st + s * beat / 2, 0.06)

# whooshes / hits at scene cuts
for c in cuts:
    n = int(0.6 * SR); x = np.arange(n) / SR
    noise = rng.standard_normal(n)
    sweep = np.concatenate([lp(noise[: n // 2], 3000), hp(noise[n // 2:], 2000)])
    w = sweep * np.sin(np.pi * x / x[-1]) ** 2
    place(w, c - 0.3, 0.25)
    place(kick, c, 0.6)

mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.85
fade = int(0.4 * SR); mix[:fade] *= np.linspace(0, 1, fade)
fo = int(1.2 * SR); mix[-fo:] *= np.linspace(1, 0, fo)
st = np.stack([mix, np.roll(mix, 200) * 0.98], 1)
wavfile.write(out, SR, (st * 32767).astype(np.int16))
print('ok', out)
