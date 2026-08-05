# -*- coding: utf-8 -*-
"""Génère toutes les répliques des 12 dialogues via ElevenLabs v3 (curl, reprise auto)."""
import json, pathlib, subprocess, sys, time

SC = pathlib.Path("/private/tmp/claude-501/-Users-svetlanatotolina-SpitUp/48298a37-5dcc-4c65-9952-9f97987e6685/scratchpad")
OUT = SC / "vo12"
OUT.mkdir(exist_ok=True)
import os
KEY = os.environ["XI_KEY"]  # export XI_KEY=... avant de lancer

D = json.loads((SC / "dialogues.json").read_text(encoding="utf-8"))

ALEXIA = "HuLbOdhRlvQQN8oPP0AJ"  # Claire
CALLERS = {
    ("medical", "nouveau"): "6FXyooAOTqUK8m2HWm32",      # Marine - Sophie
    ("medical", "connu"): "FFXYdAYPzn8Tw8KiHZqg",        # Ingrid - Mme Peeters
    ("avocats", "nouveau"): "mVjOqyqTPfwlXPjV5sjX",      # Thierry - M. Dubois
    ("avocats", "connu"): "fBpCO0Kf0krKLYGOu65w",        # Émilie - Mme Lambert
    ("immobilier", "nouveau"): "8R6pzcy1HIr4WcoApmzw",   # Amadou - Julien Moreau
    ("immobilier", "connu"): "t28pUgJnL2wUUQ8SOnaU",     # Lucas - M. Hendrickx
    ("construction", "nouveau"): "8qnuneLiGjGrT4A62CCe", # Jules - M. Rossi
    ("construction", "connu"): "t28pUgJnL2wUUQ8SOnaU",   # Lucas - M. Georges
    ("horeca", "nouveau"): "Xb7hH8MSUJpSbSDYk0k2",       # Alice - Emily (EN)
    ("horeca", "connu"): "FFXYdAYPzn8Tw8KiHZqg",         # Ingrid - Mme Rousseau
    ("automobile", "nouveau"): "zlP1wgh6FsmMZswaDa2M",   # Julien - Stef Wouters
    ("automobile", "connu"): "zlP1wgh6FsmMZswaDa2M",     # Julien - Stef Wouters (même client !)
}
SETTINGS = {"stability": 0.5, "similarity_boost": 0.85, "use_speaker_boost": True}

def tts(voice_id, text, out: pathlib.Path):
    body = json.dumps({"text": text, "model_id": "eleven_v3", "voice_settings": SETTINGS})
    for attempt in range(4):
        r = subprocess.run([
            "curl", "-s", "-w", "%{http_code}", "-o", str(out),
            "-X", "POST",
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128",
            "-H", f"xi-api-key: {KEY}", "-H", "Content-Type: application/json",
            "--data-binary", body,
        ], capture_output=True, text=True, timeout=240)
        code = r.stdout.strip()[-3:]
        if code == "200" and out.exists() and out.stat().st_size > 3000:
            return True
        time.sleep(4 + attempt * 4)
    print(f"ÉCHEC {out.name} (HTTP {code})", flush=True)
    return False

total = ok = skipped = 0
for metier, variants in D.items():
    for var, data in variants.items():
        for i, (role, text) in enumerate(data["turns"]):
            total += 1
            f = OUT / f"{metier}_{var}_{i+1:02d}.mp3"
            if f.exists() and f.stat().st_size > 3000:
                skipped += 1
                continue
            vid = ALEXIA if role == "a" else CALLERS[(metier, var)]
            if tts(vid, text, f):
                ok += 1
                print(f"✓ {f.name}", flush=True)
print(f"\nDONE: {ok} générés · {skipped} déjà présents · {total} total", flush=True)
