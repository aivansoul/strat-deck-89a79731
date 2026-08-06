# -*- coding: utf-8 -*-
"""Génère toutes les répliques des 12 dialogues via ElevenLabs v3 (curl, reprise auto)."""
import json, pathlib, subprocess, sys, time

SC = pathlib.Path("/private/tmp/claude-501/-Users-svetlanatotolina-SpitUp/48298a37-5dcc-4c65-9952-9f97987e6685/scratchpad")
OUT = SC / "vo12"
OUT.mkdir(exist_ok=True)
import os
KEY = os.environ.get("XI_KEY", "")

D = json.loads((SC / "dialogues.json").read_text(encoding="utf-8"))

ALEXIA = "HuLbOdhRlvQQN8oPP0AJ"  # Claire
CALLERS = {
    ("medical", "nouveau"): "6FXyooAOTqUK8m2HWm32",      # Marine - Sophie
    ("medical", "connu"): "FFXYdAYPzn8Tw8KiHZqg",        # Ingrid - Mme Peeters
    ("avocats", "nouveau"): "mVjOqyqTPfwlXPjV5sjX",      # Thierry - M. Dubois
    ("avocats", "connu"): "fBpCO0Kf0krKLYGOu65w",        # Émilie - Mme Lambert
    ("immobilier", "nouveau"): "usy5mXLbV9SeGWACyT3Y",   # Luca (belge) - Julien Moreau
    ("immobilier", "connu"): "IpTJxgMFj1wbxpha4zxm",     # Adrien Piret (belge) - M. Hendrickx
    ("construction", "nouveau"): "kRnE5e47lbU8Zg2MPQPm", # Moussa - M. Rossi (chaleureux)
    ("construction", "connu"): "necQJzI1X0vLpdnJteap",   # Laurent - M. Georges (warm reassuring)
    ("horeca", "nouveau"): "Xb7hH8MSUJpSbSDYk0k2",       # Alice - Emily (EN)
    ("horeca", "connu"): "FFXYdAYPzn8Tw8KiHZqg",         # Ingrid - Mme Rousseau
    ("automobile", "nouveau"): "zlP1wgh6FsmMZswaDa2M",   # Julien - Stef Wouters
    ("automobile", "connu"): "zlP1wgh6FsmMZswaDa2M",     # Julien - Stef Wouters (même client !)
}
import re as _re
from num2words import num2words as _n2w

def _num_be(tok, lang):
    """Nombre isolé → lettres. Les tokens commençant par 0 (GSM) se lisent par paires."""
    if tok.startswith("0") and len(tok) >= 2:
        pairs = [tok[i:i+2] for i in range(0, len(tok), 2)]
        parts = []
        for pr in pairs:
            if len(pr) == 2 and pr[0] == "0":
                parts.append("zéro " + _n2w(int(pr[1]), lang=lang))
            else:
                parts.append(_n2w(int(pr), lang=lang))
        return ", ".join(parts)
    return _n2w(int(tok), lang=lang)

def to_speech(text, lang="fr_BE"):
    """Version orale : heures et nombres en toutes lettres (septante/nonante en FR-BE)."""
    text = _re.sub(r"\b(\d{1,2})\s*h\s*(\d{2})\b",
                   lambda m: f"{_n2w(int(m[1]), lang=lang)} heures {_n2w(int(m[2]), lang=lang)}", text)
    text = _re.sub(r"\b(\d{1,2}) heures (\d{1,2})\b",
                   lambda m: f"{_n2w(int(m[1]), lang=lang)} heures {_n2w(int(m[2]), lang=lang)}", text)
    text = _re.sub(r"\b(\d{1,2}) heures\b",
                   lambda m: f"{_n2w(int(m[1]), lang=lang)} heures", text)
    text = _re.sub(r"\b\d+\b", lambda m: _num_be(m[0], lang), text)
    return text

# répliques avec prononciation orale imposée (numéro international anglais)
TTS_OVERRIDES = {
    ("horeca", "nouveau", 8): "It's plus double four, seven seven zero zero, nine zero zero, one two three.",
}

SET_ALEXIA = {"stability": 0.5, "similarity_boost": 0.85, "use_speaker_boost": True}
SET_CALLER = {"stability": 0.0, "similarity_boost": 0.85, "use_speaker_boost": True}

def tts(voice_id, text, out: pathlib.Path, settings=None):
    body = json.dumps({"text": text, "model_id": "eleven_v3", "voice_settings": settings or SET_ALEXIA})
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
            st = SET_ALEXIA if role == "a" else SET_CALLER
            ov = TTS_OVERRIDES.get((metier, var, i + 1))
            lang = "en" if (metier == "horeca" and var == "nouveau") else "fr_BE"
            speech = ov if ov else to_speech(text, lang)
            if tts(vid, speech, f, st):
                ok += 1
                print(f"✓ {f.name}", flush=True)
print(f"\nDONE: {ok} générés · {skipped} déjà présents · {total} total", flush=True)
