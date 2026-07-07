/* ==== Spit'Up — animations partagées : titres, sections, boutons (toutes pages) ==== */
(function () {
  const REDUCED = matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (REDUCED) {
    // freeze ambient videos on their poster frame
    document.querySelectorAll(".step-media video, .bel-card video, .pp-wave").forEach(v => {
      if (v.tagName === "VIDEO") { v.removeAttribute("autoplay"); v.pause(); }
    });
  }

  /* ---------- Boutons — origine du remplissage arrondi sous le curseur ----------
     Le ::before circulaire du .btn part du point d'entrée du curseur (--bx/--by)
     et se rétracte vers le point de sortie. */
  document.querySelectorAll(".btn").forEach(b => {
    const setOrigin = e => {
      const r = b.getBoundingClientRect();
      b.style.setProperty("--bx", ((e.clientX - r.left) / r.width * 100).toFixed(1) + "%");
      b.style.setProperty("--by", ((e.clientY - r.top) / r.height * 100).toFixed(1) + "%");
    };
    b.addEventListener("pointerenter", setOrigin);
    b.addEventListener("pointerleave", setOrigin);
  });

  if (REDUCED || !window.gsap) return;
  gsap.registerPlugin(ScrollTrigger);

  /* ---------- Titres — reveal par balayage de couleur vers la droite ----------
     Chaque ligne (séparée par <br>) est doublée : une copie fantôme très pâle
     en dessous, et la copie colorée au-dessus, révélée par clip-path de gauche
     à droite quand la section entre à l'écran. */
  const TITLES = document.querySelectorAll(".section-title, .finalcta h2, .mhero h1, .dhero h1");
  TITLES.forEach(t => {
    const lines = [[]];
    [...t.childNodes].forEach(n => {
      if (n.nodeName === "BR") { lines.push([]); n.remove(); }
      else lines[lines.length - 1].push(n);
    });
    t.textContent = "";
    const fills = [];
    lines.forEach(group => {
      if (!group.length) return;
      const row = document.createElement("span");
      row.className = "rl";
      const fill = document.createElement("span");
      fill.className = "rl-fill";
      group.forEach(n => fill.appendChild(n));
      const ghost = fill.cloneNode(true);
      ghost.className = "rl-ghost";
      ghost.setAttribute("aria-hidden", "true");
      row.appendChild(ghost);
      row.appendChild(fill);
      t.appendChild(row);
      fills.push(fill);
    });
    gsap.set(fills, { clipPath: "inset(-8% 100% -12% 0)" });
    gsap.to(fills, {
      clipPath: "inset(-8% 0% -12% 0)",
      duration: 1.15, ease: "power3.inOut", stagger: 0.14,
      scrollTrigger: { trigger: t, start: "top 85%", once: true }
    });
  });

  /* ---------- Apparition parallax de chaque section (liée au scroll) ---------- */
  document.querySelectorAll("main section:not(.hero):not(.mhero):not(.dhero)").forEach(sec => {
    const inner = sec.querySelector(":scope > .container-wide, :scope > .container");
    if (!inner) return;
    gsap.fromTo(inner,
      { y: 90, opacity: 0 },
      { y: 0, opacity: 1, ease: "none",
        scrollTrigger: { trigger: sec, start: "top 97%", end: "top 45%", scrub: 0.6 } });
  });

  /* ---------- Bridge « L'IA répond. L'humain reprend. » : parallax étagé ---------- */
  const bridge = document.querySelector(".hyb-bridge");
  if (bridge) {
    gsap.fromTo([...bridge.children],
      { y: 70, opacity: 0 },
      { y: 0, opacity: 1, stagger: .15, ease: "none",
        scrollTrigger: { trigger: bridge, start: "top 96%", end: "top 55%", scrub: 0.6 } });
  }

  /* ---------- Paragraphes d'intro : montent avec leur titre ---------- */
  document.querySelectorAll(".sec-head .right").forEach(el => {
    gsap.from(el, {
      y: 28, opacity: 0, duration: .9, ease: "power3.out", delay: .15,
      scrollTrigger: { trigger: el, start: "top 85%", once: true }
    });
  });

  /* ---------- Pages démo : mise en scène ---------- */
  const stage = document.querySelector(".demo-stage");
  if (stage) {
    gsap.from(".demo-stage .phone-preview", { y: 40, opacity: 0, duration: 1.1, ease: "power3.out", delay: .2 });
    gsap.from(".demo-side > *", { y: 26, opacity: 0, duration: .8, stagger: .09, ease: "power3.out", delay: .35 });
  }
  const cx = document.querySelector(".cx-grid");
  if (cx) {
    gsap.from(".cx-card", {
      y: 40, opacity: 0, duration: .9, stagger: .12, ease: "power3.out",
      scrollTrigger: { trigger: cx, start: "top 80%", once: true }
    });
  }
  const md = document.querySelector(".more-grid");
  if (md) {
    gsap.from(".more-grid .mic-card", {
      y: 24, opacity: 0, duration: .7, stagger: .07, ease: "power3.out",
      scrollTrigger: { trigger: md, start: "top 85%", once: true }
    });
  }

  /* ---------- Spoke pages : groupes de contenu génériques ---------- */
  if (document.body.dataset.anim === "spoke") {
    [[".duty-grid", ".duty"], [".bel-checks", "li"], [".faq-list", ".faq-item"], [".xlinks .grid", ".xlink"]]
      .forEach(([wrap, item]) => {
        const w = document.querySelector(wrap);
        if (!w) return;
        gsap.from(w.querySelectorAll(item), {
          y: 34, opacity: 0, duration: .85, stagger: .1, ease: "power3.out",
          scrollTrigger: { trigger: w, start: "top 80%", once: true }
        });
      });
    const q = document.querySelector(".testi-quote");
    if (q) {
      gsap.from(q, {
        y: 30, opacity: 0, duration: 1, ease: "power3.out",
        scrollTrigger: { trigger: q, start: "top 82%", once: true }
      });
    }
    const demo = document.querySelector(".demo-card");
    if (demo) gsap.from(demo, { y: 34, opacity: 0, duration: 1.1, ease: "power3.out", delay: .25 });
  }
})();
