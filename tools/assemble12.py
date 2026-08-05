# -*- coding: utf-8 -*-
"""Assemble les 12 dialogues - v2 rythme téléphonique :
   trim des extrémités, compression des pauses internes, tempo différencié,
   EQ téléphone côté appelant, pauses courtes, loudnorm, timings."""
import json, pathlib, subprocess, tempfile

SC = pathlib.Path("/private/tmp/claude-501/-Users-svetlanatotolina-SpitUp/48298a37-5dcc-4c65-9952-9f97987e6685/scratchpad")
VO = SC / "vo12"
OUT = pathlib.Path("/Users/svetlanatotolina/SpitUp/assets/vo")
GAP = 0.30
TEMPO_A = 1.10   # AlexIA : débit d'une pro
TEMPO_C = 1.07   # appelants : légère accélération naturelle
D = json.loads((SC / "dialogues.json").read_text(encoding="utf-8"))

def dur(f):
    return float(subprocess.check_output(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)]).strip())

def prep(src, dst, role):
    """Segment → wav prêt : trims, pauses internes compressées, tempo, EQ téléphone."""
    tempo = TEMPO_A if role == "a" else TEMPO_C
    filters = [
        "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05",
        "areverse",
        "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.12",
        "areverse",
        "silenceremove=stop_periods=-1:stop_duration=0.5:stop_threshold=-45dB:stop_silence=0.35",
        f"atempo={tempo}",
    ]
    if role == "c":
        filters += ["highpass=f=280", "lowpass=f=3500", "volume=0.9"]
    filters += ["aformat=sample_rates=44100:channel_layouts=mono"]
    subprocess.run(["ffmpeg", "-y", "-i", str(src), "-af", ",".join(filters), str(dst)],
                   check=True, capture_output=True)

TIMES = {}
with tempfile.TemporaryDirectory() as td:
    tdp = pathlib.Path(td)
    for metier, variants in D.items():
        TIMES[metier] = {}
        for var, data in variants.items():
            n = len(data["turns"])
            segs = [VO / f"{metier}_{var}_{i+1:02d}.mp3" for i in range(n)]
            missing = [s.name for s in segs if not s.exists()]
            if missing:
                print(f"⚠ {metier}/{var} : manquants {missing} - sauté")
                continue
            wavs = []
            for i, ((role, _), s) in enumerate(zip(data["turns"], segs)):
                w = tdp / f"{metier}_{var}_{i:02d}.wav"
                prep(s, w, role)
                wavs.append(w)
            durs = [dur(w) for w in wavs]
            t, starts = 0.0, []
            for d_ in durs:
                starts.append(round(t, 2)); t += d_ + GAP
            total = t - GAP
            TIMES[metier][var] = {"times": starts, "dur": f"{int(total//60):02d}:{int(total%60):02d}"}
            fc = []
            for i in range(n):
                fc.append(f"[{i}]anull[s{i}]")
            for g in range(n - 1):
                fc.append(f"[{n+g}]anull[g{g}]")
            chain = "".join(f"[s{i}][g{i}]" if i < n - 1 else f"[s{i}]" for i in range(n))
            fc.append(f"{chain}concat=n={2*n-1}:v=0:a=1,loudnorm=I=-16:TP=-1.5[out]")
            cmd = ["ffmpeg", "-y"]
            for w in wavs: cmd += ["-i", str(w)]
            for g in range(n - 1): cmd += ["-f", "lavfi", "-t", str(GAP), "-i", "anullsrc=r=44100:cl=mono"]
            outfile = OUT / f"{metier}-{var}.mp3"
            cmd += ["-filter_complex", ";".join(fc), "-map", "[out]", "-b:a", "112k", str(outfile)]
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"{outfile.name} · {TIMES[metier][var]['dur']} · {outfile.stat().st_size // 1024} KB")

(SC / "times.json").write_text(json.dumps(TIMES, ensure_ascii=False), encoding="utf-8")
print("times.json écrit")
