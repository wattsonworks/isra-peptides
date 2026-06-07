# CLAUDE.md - working notes for Claude Code

## What this is
Isra.Peptides: a bilingual (Hebrew RTL / English LTR), research-use-only peptide
reference and catalog website. Single brand, static site.

## Architecture
- Everything is in `index.html`: one inline `<style>` block and one inline `<script>`.
  Vanilla JS only. No framework, no bundler, no build step. Edit `index.html` directly.
- Single-page app. A hash router toggles `.view` sections by adding `.active`.
  Routes: home, products, product/<id>, bundles, quiz, compare, explore, pricing,
  glossary, library, learn, blog, post/<slug>, about, contact, page/<slug>.
- `img/` holds images. `manifest.json` + `sw.js` provide the PWA.
- `standalone.html` is a generated single-file build (images inlined). Do not hand-edit
  it; it is produced from `index.html` + assets.

## Internationalization
- Every UI string carries `data-he` and `data-en` (use `data-html` when the value is
  HTML). `applyLang()` swaps text and flips direction. Keep BOTH languages in sync for
  any copy you add or change.

## Data (objects/arrays inside the script)
- `PRODUCTS` - catalog (id, name, mg, sizes, img, purity, cat, bilingual sum/over/origin/
  mech, areas, tags). Enriched at runtime with stock, diagram, faq.
- `CHEM` - per-product chemical data (sequence, formula, mw, cas, store, pm, d2).
- `CID` - PubChem compound IDs for the products that have real 3D records.
- `TARGETS` - receptor/pathway groups used to build the knowledge graph.
- `BUNDLES`, `LEARN`, `POSTS`, `LIBRARY`, `GLOSSARY`, `PROD_CATS`, `LIB2PROD`.

## Hard rules (do not break)
- RESEARCH USE ONLY. Never add human or animal dosing, administration, or usage
  instructions. Preserve "not for human consumption / not medical advice" framing.
- Chemical data must be verified against an authoritative source (PubChem, FDA,
  Sigma, peer-reviewed) before being added. Never invent a CAS number, molecular
  weight, sequence or formula. If a value cannot be verified, leave that field out.
- No emojis in code.
- Keep bilingual parity (HE + EN) for all content.

## Design tokens
- Dark navy background; gold accents (#c9a24b / #e6c977) and cyan (#5fa8d3).
- Display serif: Playfair Display / Frank Ruhl Libre. Body: Heebo.
- Terminal/clinical aesthetic; subtle motion; respects prefers-reduced-motion.

## Runtime-only externals (must degrade gracefully offline)
- PubChem 2D images and 3Dmol.js 3D viewer, NCBI PubMed live feed, Google Fonts.
  These need a live connection and are expected to be unavailable on file:// or in
  sandboxed previews. The site must still render fully without them.

## Preview / verify
- Serve over HTTP: `python3 -m http.server 8080`.
- After edits, sanity-check the inline script parses (e.g. extract `<script>` and run
  `node --check`). Bump the `sw.js` cache name (currently `isra-peptides-v3`) whenever
  cached assets change.

## Placeholders to confirm with the owner
- Email `info@israpeptides.com` is a placeholder. WhatsApp 972506787586,
  Instagram @isra.peptides.

## Added features (AR / QR / SEO / stack)
- AR: `models/vial.glb` (branded vial). Loaded on demand via Google `<model-viewer>`
  (CDN module). The AR button appears on product pages.
- QR batch COA: per-product modal with a QR (qrcodejs CDN) encoding the product's
  live URL. Specimen document only.
- SEO: `updateSEO()` sets canonical, Open Graph and a per-product Product JSON-LD on
  every route. Organization JSON-LD is static in the head.
- Research stack: route `#stack` (from favorites) or `#stack/<id,id,...>` (shareable).
  Shows shared-pathway hints (from TARGETS) and a radar overlay.
- New runtime-only externals (degrade offline): model-viewer, qrcodejs.

## Languages (HE / EN / RU / AR)
- `lang` is one of he/en/ru/ar. `applyLang()` sets dir (he+ar = rtl) and swaps text.
- Static markup uses data-he/data-en. For ru/ar, `applyLang` looks up the English
  string in the `TR` dictionary (TR.ru / TR.ar); if missing it falls back to English.
- Content objects use `t({he,en})`; for ru/ar `t()` returns `TR[lang][en]` or English.
- To localize more: add `"English string":"translation"` pairs to TR.ru / TR.ar.
  Untranslated strings safely fall back to English. Keep Arabic accurate (RTL).
- ARABIC IS NOW FULLY TRANSLATED (TR.ar ~1334 keys). RU is still partial.
- Every rendered string routes through `tr()`: all `L('he','en')` helpers return
  `lang==='he'?he:tr(en)`, inline `lang==='he'?'..':'..'` text ternaries wrap the
  English in `tr(...)`, and `localizeContentAr()` (called at the top of `applyLang`)
  walks all content arrays (PRODUCTS/SYS/LEARN/POSTS/VALUES/FAQ/GLOSSARY/LIBRARY/
  BUNDLES/PROD_CATS/LIB_CATS/REGIONS/ANALOG) injecting `obj.ar` (and `obj.nar` for
  region notes) so array-valued and `obj[lang]||obj.en` content also localizes.
- When you ADD any new user-facing English string (data-en, an `L('he','en')`, a
  content `.en`, etc.), add its `"English":"العربية"` pair to TR.ar or it shows
  English in Arabic. The `.tag` eyebrow labels (e.g. "CATALOG · RESEARCH USE ONLY")
  are intentionally hardcoded Latin in all languages — leave them.
- Brand ("Isra.Peptides"), peptide names (BPC-157…), units, and scientific acronyms
  (GH, IGF, GLP-1, DNA, COA, HPLC, MS, PubChem, RUO, AR, QR…) are kept Latin in AR.

## WebGL hero
- `models/vial.glb` is the AR model. The homepage hero also renders a Three.js
  double-helix into `#heroGL` (loaded from CDN, lazy). Falls back to the hero photo
  if Three.js is unavailable. Respects prefers-reduced-motion.

## Research Journal + Supabase
- Code-login journal (no email). State in `JOURNAL`, code in localStorage `ip_jcode`.
- Works locally by default. For cross-device sync, run `SUPABASE_SETUP.sql` in Supabase
  and set `var SUPA_URL='https://YOUR-REF.supabase.co';` near the top of the script.
  The publishable key (`SUPA_KEY`) is already set and is safe to be public.
- Access is via two security-definer RPCs (journal_load / journal_save); the table has
  RLS on with no policies, so the public key cannot read it directly or enumerate codes.
- Strictly a research log (notes, log entries, saved stack, .txt export) — never a
  dosing/symptom diary. Keep it that way.

## Research Games (#games)
- One `#games` view with a tab switcher (`gameTab`: daily / build / quiz); `renderGames()`
  dispatches to `renderPeptidle` / `renderBuilder` / `renderQuizArena` into `#gameHost`.
  Linked in nav + footer; rendered on showView('games') and re-rendered in applyLang if active.
- Peptidle: deterministic daily compound (`Math.floor(Date.now()/864e5) % pool`), up to 6
  guesses with category/MW(up-down)/length/shared-pathway hints; state in localStorage
  `ip_pdl`, streak/best in `ip_pdlst`; monochrome (O/^/v/.) shareable grid, no emoji.
- Build-a-Peptide: AA tile palette -> chain; live length + approx mass from `AAMASS`
  (average residue masses + WATER, factual ExPASy values); identifies known peptides by
  exact residue match; "recreate target" challenges from short parseable sequences.
- Quiz Arena: 8 runtime-generated MCQs (pathway/family/analog/length/glossary) from
  PRODUCTS/TARGETS/ANALOG/GLOSSARY; score + streak + best (`ip_quizbest`) + rank label.
- All game strings go through `tr()` and have AR translations in TR.ar (keep that parity
  when editing game copy). Educational/RUO-safe, no dosing, no emojis.

## Markdown articles
- Blog merges JS `POSTS` with markdown posts listed in `posts/manifest.json`.
- To add an article: add an entry to `posts/manifest.json` (slug, date, ic, title{he,en},
  excerpt{he,en}) and create `posts/<slug>.en.md` (and optionally `<slug>.he.md`).
- Rendered at runtime via marked.js (CDN, lazy). Needs the hosted site (fetch); on
  file:// it shows a graceful "needs a connection" message. No rebuild needed to add posts.
- FAQ JSON-LD (FAQPage) is injected from the `FAQ` array for Google rich results.

## Knowledge Center (language-aware infographics)
- `LEARN` chapters carry `imgHe`/`imgEn` (and `imgHe2` for the two-part "made of" chapter).
  `renderStep()` picks per language and falls back gracefully. 24 `kc_*` images in `img/`
  (11 EN, 13 HE). Header says 12 PARTS.
- Homepage What/Shift/Systems figures are language-aware via `data-img-he`/`data-img-en`;
  `applyLang()` swaps the `src`. EN shows `kc_*_en`, HE shows `kc_*_he`.

## Structure features (client-side, no backend)
- `seqParse(p)` parses `CHEM[id].seq` into residue objects (3-letter dash format, cyclic
  brackets, D-/modified residues like Nle/Aib, or a 1-letter run inside parentheses).
  Returns null if not parseable. Result cached in `SEQ_CACHE`.
- `seqViewer(p)` renders colored residue tiles + composition legend (`.seqv`/`.aa` CSS).
  Shows for ANY parseable sequence. `AA` map holds class + bilingual names; `SEQ_CLR` colors.
- `loadSchematic(p,el)` builds an idealized alpha-helix CA-trace PDB (`seqToPDB`) and renders
  it via 3Dmol, colored by residue class. ONLY for peptides without a real PubChem `CID`
  (those keep the accurate PubChem 3D). Clearly labeled "schematic/illustrative — not a
  predicted or experimental structure" (do not relabel as real structure).

## Live PubMed badge
- `pubmedBadge(p,el)` shows an NCBI study count near the product title. Cached in
  localStorage (`ip_pm_<id>`, 7-day TTL). Degrades silently offline. Separate from the
  existing `pubmedFeed` (latest-papers list lower on the page).

## Regulatory map (`#regulatory` route)
- `renderRegmap()` draws an inline stylized SVG world map from the `REGIONS` array
  (9 regions, bilingual). Click a region -> side panel with a GENERAL RUO framing.
  IMPORTANT: never assert specific per-country legal status (no "legal"/"banned" claims) —
  this is general, non-legal framing only, by design. Middle East is flagged `home:1`.
  Linked from main nav and footer. CSS prefix `.rmap-`/`.rgn`.
- Continent polygons in `REGIONS[].pts` are equirectangular-projected (lon->x on 0..1000,
  lat->y on 0..440) so they read as real continents. `renderRegmap()` draws an ocean rect +
  graticule behind them. To move/reshape a region, edit its `pts` (and `cx`/`cy` label).

## Branded spec sheet (print -> PDF)
- `specSheet(p)` opens a branded printable window (logo, chem table, sequence, analog, RUO
  disclaimer) and calls print. Bound to the product page "Spec sheet (PDF)" button
  (`#specBtn`). Replaced the old raw `window.print()`. Bilingual; RTL-aware.

## Smart search (intent/concept layer)
- `SEM` array maps natural-language regexes (EN+HE cues: "fat loss", "tendons", "sleep",
  "tanning", "memory"...) to product id lists with a bilingual concept label. `runSearch()`
  scores products: exact name 100, text match 60, concept 55-. Concept-only hits show the
  concept label as the result subtitle. Extend by adding `{re,he,en,ids}` to `SEM`.

## AR: molecule in your space (runtime-generated glb)
- `openAR(p)` is molecule-first. `buildMolecule(p,cb)` returns `{url,kind,atoms}`:
  - CID with a PubChem 3D conformer -> fetch `.../cid/<cid>/SDF?record_type=3d`,
    `parseSDF` -> all-atom (`kind:'atomic'`). NOTE only ~7 of our CIDs have a 3D
    conformer; larger peptides 404 and fall back.
  - else parseable `seqParse` -> CA-trace helix backbone (`kind:'backbone'`,
    colored by residue class). else -> branded `models/vial.glb`.
- The glb is built in-browser: `moleculeMesh()` makes vertex-colored spheres
  (`_sphere`) + split two-color bond cylinders (`_cyl`); `_glbFromMesh()` writes a
  valid binary GLB (POSITION/NORMAL/COLOR_0 + uint32 indices, JSON+BIN chunks,
  4-byte padded) and returns a Blob -> object URL into `<model-viewer>`. Scaled to
  ~0.3 m so AR placement is desk-sized. `ELEM` = CPK-ish colors/radii.
- Modal has a Molecule/Vial toggle (`_arSetSrc`), studio lighting (tone-mapping
  neutral, soft shadow), auto-rotate, and AR modes. Labels are honest: "All-atom
  (PubChem)" vs "Schematic backbone — illustrative". Do not relabel the backbone
  as an experimental structure.
- model-viewer needs the element on-screen (lazy) to fire `load`; for off-screen
  tests set `loading="eager"`.
- `CID3D` whitelists the 9 CIDs verified to HAVE a PubChem 3D conformer; ONLY those
  get the all-atom SDF fetch (others go straight to backbone, so no 404s/console
  noise). Most peptide CIDs lack a 3D conformer. To add an all-atom compound: verify
  `.../cid/<cid>/SDF?record_type=3d` returns 200, then add to `CID` + `CID3D`.
- `CID2D` = verified CIDs WITHOUT 3D, used only for a clean 2D PubChem depiction +
  exact compound deep-link (the on-page 3D stays the schematic backbone — do not
  promote a no-3D CID into the `CID` map or it regresses the 3D button).

## Explore knowledge graph (interactive, accessible)
- Force layout cached in `_G` (nodes/links/degree/neighbors); positions persist
  across re-renders (no restart on language/tab switch). `renderGraph` seeds only
  when fresh or on resize.
- `graphTick` runs while heated, then parks (`graphRaf=0`) so the CPU rests; any
  hover/drag re-heats via `_gKick`. (Old code hard-stopped at 420 frames and died.)
- Interaction: hover highlights a node + neighbors + edges and reveals only those
  labels (plus hub labels, degree>=5) — kills the label clutter. Drag to arrange;
  click (no drag, <500ms) opens the product. `prefers-reduced-motion` settles
  synchronously, no idle motion.
- Accessibility: third Explore tab "Accessible list" (`renderExploreList`) renders
  pathways (TARGETS) -> peptides as real `<a href="#product/..">` links (keyboard +
  screen-reader friendly); `#graphWrap` has an aria-label pointing there.
- Labels: ALL node names render by default (10px, dark halo); on hover/grab the
  focused node + neighbors stay bright and the rest dim to ~0.16 (focus + context).
- Touch/mobile: `#graphCanvas` has `touch-action:none` (or the browser hijacks the
  drag and it "glitches out"). pointerdown sets `_Ghover` to the grabbed node so
  connections reveal on touch (no hover on mobile). During a drag, `graphTick` skips
  global physics (only the dragged node moves, vx/vy zeroed) so there's no fling;
  on release `_Gheat=0` leaves nodes where dropped. A no-move tap (<500ms) opens the
  product; a drag does not navigate.

## NOTE on the service worker while developing
- `sw.js` cache-first means a hosted/preview client keeps serving the OLD cached
  `index.html` until cache `C` is bumped (currently `isra-peptides-v6`). ALWAYS bump `C`
  when shipping index.html/asset changes, or returning users won't see them. In a local
  preview, unregister the SW + clear caches and hard-reload to see edits.
