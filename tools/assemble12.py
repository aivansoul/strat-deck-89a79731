# -*- coding: utf-8 -*-
"""Assemble les 12 dialogues : EQ téléphone côté appelant, pauses, loudnorm, timings."""
import json, pathlib, subprocess

SC = pathlib.Path("/private/tmp/claude-501/-Users-svetlanatotolina-SpitUp/48298a37-5dcc-4c65-9952-9f97987e6685/scratchpad")
VO = SC / "vo12"
OUT = pathlib.Path("/Users/svetlanatotolina/SpitUp/assets/vo")
GAP = 0.55
D = json.loads((SC / "dialogues.json").read_text(encoding="utf-8"))

def dur(f):
    return float(subprocess.check_output(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)]).strip())

TIMES = {}
for metier, variants in D.items():
    TIMES[metier] = {}
    for var, data in variants.items():
        n = len(data["turns"])
        segs = [VO / f"{metier}_{var}_{i+1:02d}.mp3" for i in range(n)]
        missing = [s.name for s in segs if not s.exists()]
        if missing:
            print(f"⚠ {metier}/{var} : segments manquants {missing} - sauté")
            continue
        durs = [dur(s) for s in segs]
        t, starts = 0.0, []
        for d_ in durs:
            starts.append(round(t, 2)); t += d_ + GAP
        total = t - GAP
        TIMES[metier][var] = {"times": starts, "dur": f"{int(total//60):02d}:{int(total%60):02d}"}
        # filtres : appelant (rôle c) = EQ téléphone ; AlexIA claire
        fc = []
        for i, (role, _) in enumerate(data["turns"]):
            if role == "c":
                fc.append(f"[{i}]highpass=f=280,lowpass=f=3500,volume=0.9,aformat=sample_rates=44100:channel_layouts=mono[s{i}]")
            else:
                fc.append(f"[{i}]aformat=sample_rates=44100:channel_layouts=mono[s{i}]")
        for g in range(n - 1):
            fc.append(f"[{n+g}]aformat=sample_rates=44100:channel_layouts=mono[g{g}]")
        chain = "".join(f"[s{i}][g{i}]" if i < n - 1 else f"[s{i}]" for i in range(n))
        fc.append(f"{chain}concat=n={2*n-1}:v=0:a=1,loudnorm=I=-16:TP=-1.5[out]")
        cmd = ["ffmpeg", "-y"]
        for s in segs: cmd += ["-i", str(s)]
        for g in range(n - 1): cmd += ["-f", "lavfi", "-t", str(GAP), "-i", "anullsrc=r=44100:cl=mono"]
        outfile = OUT / f"{metier}-{var}.mp3"
        cmd += ["-filter_complex", ";".join(fc), "-map", "[out]", "-b:a", "112k", str(outfile)]
        subprocess.run(cmd, check=True, capture_output=True)
        size = outfile.stat().st_size // 1024
        print(f"{outfile.name} · {TIMES[metier][var]['dur']} · {size} KB")

(SC / "times.json").write_text(json.dumps(TIMES, ensure_ascii=False), encoding="utf-8")
print("times.json écrit")
