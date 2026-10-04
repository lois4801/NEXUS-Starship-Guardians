# Luxury Single-Page Website — NEXUS Template

A reusable, self-contained luxury landing-page template: smooth scrolling (Lenis), high-end motion (GSAP + ScrollTrigger), animated type, custom cursor, and pinned horizontal sections. Built for the NEXUS Starship Guardians site (`docs/index.html`) — reuse it for any project.

## Files

| File | Purpose |
|---|---|
| `index.html` | The entire site — markup, styles, and scripts in one file, no build step |
| `assets/` | Imagery the page references (`hero-lux.jpg`, `capsules.jpg`, `constellation.jpg`, `core-nebula.jpg`, plus the two SVG diagrams). Copy `docs/assets/` here or adjust the `./assets/...` paths. |

## Run it locally

```bash
python -m http.server -d website-template 8000
# → http://localhost:8000
```

No install step — GSAP and Lenis load from CDN. Missing images degrade gracefully (alt text shows); drop real files in for the full effect.

## Publish on GitHub Pages

1. Put the site on your default branch (this repo serves `docs/`).
2. Repo **Settings → Pages → Build and deployment → Deploy from a branch → main → pick the folder → Save**.
3. Live at `https://<user>.github.io/<repo>/`.

## How the effects work (map for next time)

| Effect | Where | Technique |
|---|---|---|
| Smooth scrolling | bottom `<script>` | `new Lenis({...})` driven by `gsap.ticker`; anchors call `lenis.scrollTo` |
| Preloader | `#loader` | GSAP percent counter, then `yPercent:-100` reveal; on complete starts `introTl` + `lenis.start()` |
| Hero type reveal | `splitChars()` + `[data-chars]` | Text split into `<span>`s, `y` animated from 115% with stagger on a paused timeline |
| Italic slide-in | `[data-slide]` | Same timeline, gradient serif line slides up |
| Manifesto word scrub | `[data-scrub-words]` + `splitWords()` | Word spans start at `.14` opacity, scrubbed to scroll position |
| Horizontal sections | `#coPin`, `#roPin` | ScrollTrigger `pin:true` + `x` tween over track `scrollWidth`; progress bar in `onUpdate` |
| Parallax figures | `[data-parallax]` | Image `yPercent` −12 → 6, scrubbed |
| Animated counters | `[data-count]` | GSAP object tween (`expo.out`) fired by the intro timeline |
| Custom cursor | `#cDot`, `#cRing` | `mousemove` + `gsap.ticker` lerp; ring grows on `[data-cursor]` hover |
| Magnetic buttons | `.magnetic` | `gsap.to` x/y on mousemove, elastic release on leave |
| Section background shifts | `[data-bg]` | ScrollTrigger toggles `body` background-color per section |
| Terminal typing | `#typePre` | `setInterval` reveals the `GATES` array line by line on scroll into view |
| Header hide/show | `#siteHeader` | ScrollTrigger `onUpdate` compares scroll direction past 180px |

## Customization checklist

1. **Copy** — take `index.html`, add an `assets/` folder beside it.
2. **Content** — edit the hero `<h1>` rows, `.hero-lede`, the six `.sys-row`s, and the company panels directly. The Roster and Agency cards are rendered from the `WINGS` array in the first `<script>` block — edit data there, not HTML.
3. **Palette** — change the CSS variables in `:root` (`--bg0`, `--bg1`, `--gold`, `--grad-flow`, the wing colors).
4. **Fonts** — swap the Google Fonts `<link>` and the `--font-d/s/b/m` variables.
5. **Sections** — each `<section>` is independent; delete or duplicate freely. Keep section `id`s in sync with the header nav (`#systems`, `#company`, …).
6. **Timing** — the intro timeline uses absolute second positions (`.08`, `.73`, `1.13`); tweak to taste.
7. **Images** — hero uses `object-fit:cover` at 118% height for the parallax headroom; figures use 120–130%.

## Notes

- Mobile: custom cursor and magnetic effects auto-disable on touch (`pointer:coarse` check); stats grid collapses to 2 columns.
- Everything is vanilla JS + CDN libs — no build tooling to maintain.
- `index.html` here is byte-identical to the live `docs/index.html`.
