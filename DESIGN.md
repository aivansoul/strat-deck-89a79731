# Design

Visual system extracted from `telesecretariat-ia.html` (the pillar page). All new pages — the six profession spokes included — reuse these tokens verbatim; the CSS custom properties below are the source of truth.

## Theme

Warm-neutral editorial ground with a single gold accent and deep-ink dark sections. Light by default; dark (`--ink`) is used as a full-section inversion for the hybrid, final-CTA and footer bands, not as a toggleable theme. The hero sits on full-bleed client video darkened by a gradient overlay, with white text.

## Color

| Token | Value | Role |
|---|---|---|
| `--bg` | `#F7F5EF` | Page ground |
| `--bg-2` | `#FFFFFF` | Cards / raised surfaces |
| `--panel` | `#EFEBE0` | Tinted panels (Belgium section, bubbles) |
| `--ink` | `#0B0B0B` | Primary text; dark section ground |
| `--ink-2` | `#1A1A1A` | Secondary text |
| `--mute` | `#8A8A85` | Muted text (labels, captions) |
| `--mute-2` | `#B9B5AB` | Muted-on-dark |
| `--line` | `#DAD6CB` | Borders |
| `--line-2` | `#E8E4D9` | Hairline borders |
| `--gold` | `#B08D57` | Accent (highlights, pins, italic words) |
| `--gold-2` | `#C9A876` | Accent on dark |
| `--gold-deep` | `#8E6F3F` | Accent hover / pressed |
| Live green | `#2BB673` | "En direct" status only — semantic, not accent |

Accent discipline: gold carries emphasis (one italic word per heading, icons, tags); it never fills large areas except the `.btn-gold` CTA.

## Typography

- **Family**: Poppins for display and body (700 display / 600 subhead / 400 body); JetBrains Mono for labels, numbers and meta.
- **Display**: `h1` clamp(48px→132px), line-height 1.0, letter-spacing −0.035em; `h2` clamp(36px→68px), −0.03em.
- **Signature move**: one italic gold word inside each heading (`.serif.italic` + `color: var(--gold)`), optionally with the hand-drawn SVG underline in the hero.
- **Mono labels**: 10–12px, uppercase, letter-spacing .12–.18em — used for eyebrows, stats, tags, footer meta.
- Body 14–17px, line-height 1.45–1.6, max ~56ch.

## Components

- **Buttons** (`.btn`): 14px/600, 10px radius, arrow SVG that slides on hover; variants `-primary` (ink), `-ghost` (outline), `-gold`. Magnetic cursor-follow on desktop.
- **Nav** (`.nav`): fixed, transparent over hero → blurred cream with hairline border after 24px scroll (`.scrolled`).
- **Mic cards** (`.mic-card`): 3/4 aspect, photo background behind cream gradient, concentric gold-ring mic button, float animation, `.active` gold-glow state.
- **Phone preview** (`.phone-preview`): sticky call-transcript card — header with live badge, animated waveform, caller/AI bubbles, summary block with mono tags.
- **Hero call-card** (`.hero-callcard`): glassmorphic dark card, rotated 1.6°, video thumbnail, equalizer bars, progress bar. (Glass is reserved for this one element.)
- **Metrics** (`.metric`): huge Poppins numbers with gold unit superscripts, hairline column dividers, counting animation on scroll.
- **FAQ** (`.faq-item`): border-top list, plus-circle icon that morphs to minus, max-height accordion.
- **Pricing** (`.cmp-card`): 3 columns, middle card inverted ink with gold badge "Le plus choisi".
- **Marquee**: mono uppercase strip with gold dots, 50s linear loop.

## Layout

- Containers: `.container` 1280px / `.container-wide` 1480px, fluid `100% − 64px` (32px on mobile).
- Section rhythm: 140px vertical padding (100px ≤580px); `.sec-head` is a 2-col grid — big title left, muted intro right, aligned to baseline.
- Numbered mono eyebrows (`01 · Sur mesure par métier`) mark the pillar page's real section sequence.
- Breakpoints: 980px (grids collapse, nav links hide) and 580px (single column).

## Motion

- GSAP + ScrollTrigger: fade-up reveals per section, staggered card entrances, number counters (fr-BE locale), all `once: true`.
- CSS keyframe ambience: mic-card float, equalizer bars, live-pulse dots, pin pulses, marquee.
- Hero: staged `reveal-up` lines (0.1–0.4s delays), SVG underline draw at 1.1s.
- **Gap to close on new pages**: add `@media (prefers-reduced-motion: reduce)` alternatives (pause marquee/floats, show counters at final value, crossfade instead of translate).
