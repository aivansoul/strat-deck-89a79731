# -*- coding: utf-8 -*-
"""Patche les 6 pages démo : sélecteur de scénarios + chat/audio/résumé par variante."""
import json, pathlib, re

ROOT = pathlib.Path("/Users/svetlanatotolina/SpitUp")
SC = pathlib.Path("/private/tmp/claude-501/-Users-svetlanatotolina-SpitUp/48298a37-5dcc-4c65-9952-9f97987e6685/scratchpad")
D = json.loads((SC / "dialogues.json").read_text(encoding="utf-8"))
try:
    VT = json.loads((SC / "times.json").read_text(encoding="utf-8"))
except FileNotFoundError:
    VT = {}

DEFAULTS = {"horeca": "connu"}  # démo lancée en FR par défaut

PAGES = {"medical": "demo-medical.html", "avocats": "demo-avocats.html",
         "immobilier": "demo-immobilier.html", "construction": "demo-construction.html",
         "horeca": "demo-horeca.html", "automobile": "demo-automobile.html"}

def clean(t): return re.sub(r"\[[a-z ]+\] ?", "", t)

NEW_JS_TPL = '''/* ---------- Démo : 2 scénarios (nouveau client / client reconnu) ---------- */
const VARIANTS = __VARIANTS__;
let curVar = "__DEFVAR__";
const wave = document.getElementById("pp-wave");
const transcript = document.getElementById("pp-transcript");
const summaryEl = document.getElementById("pp-summary-text");
const tagsEl = document.getElementById("pp-summary-tags");
const durEl = document.getElementById("pp-dur");
const live = document.getElementById("demo-live");
const micBtn = document.getElementById("demo-mic");
const hint = document.getElementById("demo-mic-hint");
const voices = {};

(function buildWave() {
  for (let i = 0; i < 56; i++) {
    const s = document.createElement("span");
    const env = Math.sin((i / 56) * Math.PI);
    const detail = 0.5 + Math.sin(i * 0.7) * 0.25 + Math.cos(i * 1.3) * 0.2;
    const h = Math.max(5, Math.round(env * 22 * detail + 4));
    s.style.height = h + "px";
    s.style.animationDelay = (i * 0.04) + "s";
    wave.appendChild(s);
  }
})();

function applySummary() {
  const V = VARIANTS[curVar];
  summaryEl.textContent = V.summary;
  tagsEl.innerHTML = V.tags.map(t => `<span class="tag">${t}</span>`).join("");
  durEl.textContent = V.dur || "--:--";
}
applySummary();

let timers = [];
function playDemo() {
  timers.forEach(t => clearTimeout(t));
  timers = [];
  transcript.innerHTML = "";
  const V = VARIANTS[curVar];
  const synced = voices[curVar] && V.times.length === V.convo.length;
  V.convo.forEach(([who, text], i) => {
    const b = document.createElement("div");
    b.className = "pp-bubble " + (who === "a" ? "ai" : "caller");
    b.innerHTML = `<div class="who">${who === "a" ? "AlexIA" : "Appelant"}</div>${text}`;
    transcript.appendChild(b);
    const at = synced ? V.times[i] * 1000 + 150 : 400 + i * 2400;
    timers.push(setTimeout(() => {
      b.classList.add("show");
      transcript.scrollTop = transcript.scrollHeight;
    }, at));
  });
}

function stopAllAudio() {
  Object.values(voices).forEach(a => { if (a) { a.pause(); a.currentTime = 0; } });
}

function launchDemo() {
  live.classList.add("on");
  hint.textContent = "Démo en cours - appuyez pour rejouer";
  stopAllAudio();
  const V = VARIANTS[curVar];
  if (voices[curVar]) {
    voices[curVar].play().catch(() => {});
    playDemo();
  } else if (voices[curVar] === undefined) {
    fetch(V.audio, { method: "HEAD" }).then(r => {
      voices[curVar] = r.ok ? new Audio(V.audio) : null;
      if (voices[curVar]) voices[curVar].play().catch(() => {});
      playDemo();
    }).catch(() => { voices[curVar] = null; playDemo(); });
  } else {
    playDemo();
  }
}
micBtn.addEventListener("click", launchDemo);
document.getElementById("pp-replay").addEventListener("click", launchDemo);

document.querySelectorAll(".vs-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    if (btn.dataset.v === curVar) return;
    curVar = btn.dataset.v;
    document.querySelectorAll(".vs-btn").forEach(b => {
      const on = b.dataset.v === curVar;
      b.classList.toggle("active", on);
      b.setAttribute("aria-selected", on);
    });
    applySummary();
    stopAllAudio();
    if (live.classList.contains("on")) launchDemo();
  });
});'''

for metier, page in PAGES.items():
    p = ROOT / page
    h = p.read_text(encoding="utf-8")

    # variants JSON
    variants = {}
    for var in ("nouveau", "connu"):
        dd = D[metier][var]
        vt = VT.get(metier, {}).get(var, {})
        variants[var] = {
            "label": dd["label"],
            "audio": f"assets/vo/{metier}-{var}.mp3",
            "times": vt.get("times", []),
            "dur": vt.get("dur", ""),
            "summary": dd["summary"],
            "tags": dd["tags"],
            "convo": [[r, clean(x)] for r, x in dd["turns"]],
        }
    vjson = json.dumps(variants, ensure_ascii=False)
    defvar = DEFAULTS.get(metier, "nouveau")

    # 1) switch avant la carte (si pas déjà présent)
    if "variant-switch" not in h:
        m = re.search(r'(<div class="demo-live" id="demo-live">\n)(\s*<div class="demo-visual")', h)
        assert m, f"{page}: demo-live introuvable"
        switch = (f'{m.group(1)}        <div class="variant-switch" role="tablist" aria-label="Choix du scénario">\n'
                  f'          <button class="vs-btn active" data-v="nouveau" type="button" role="tab" aria-selected="true">{D[metier]["nouveau"]["label"]}</button>\n'
                  f'          <button class="vs-btn" data-v="connu" type="button" role="tab" aria-selected="false">{D[metier]["connu"]["label"]}</button>\n'
                  f'        </div>\n{m.group(2)}')
        h = h.replace(m.group(0), switch, 1)

    # 2) résumé dynamique
    h = re.sub(r'<div class="lbl">Résumé · envoyé par email · [^<]*</div>',
               '<div class="lbl">Résumé · envoyé par email · <span id="pp-dur">--:--</span></div>', h)
    h = re.sub(r'<span id="pp-summary-text">[^<]*</span>', '<span id="pp-summary-text"></span>', h)
    h = re.sub(r'<div class="tags">(<span class="tag">[^<]*</span>)*</div>',
               '<div class="tags" id="pp-summary-tags"></div>', h, count=1)

    # 3) bloc JS
    start = h.find("/* ---------- Démo")
    end = h.find("</script>", start)
    assert start > 0 and end > start, f"{page}: bloc JS introuvable"
    h = h[:start] + NEW_JS_TPL.replace("__VARIANTS__", vjson).replace("__DEFVAR__", defvar) + "\n" + h[end:]

    # 4) bump cache CSS
    h = re.sub(r'styles\.css\?v=[0-9a-z]+', 'styles.css?v=20260806e', h)
    p.write_text(h, encoding="utf-8")
    n_times = sum(1 for v in variants.values() if v["times"])
    print(f"{page} : patché · variantes audio synchronisées : {n_times}/2")
print("OK")
