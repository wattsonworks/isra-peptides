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

## Markdown articles
- Blog merges JS `POSTS` with markdown posts listed in `posts/manifest.json`.
- To add an article: add an entry to `posts/manifest.json` (slug, date, ic, title{he,en},
  excerpt{he,en}) and create `posts/<slug>.en.md` (and optionally `<slug>.he.md`).
- Rendered at runtime via marked.js (CDN, lazy). Needs the hosted site (fetch); on
  file:// it shows a graceful "needs a connection" message. No rebuild needed to add posts.
- FAQ JSON-LD (FAQPage) is injected from the `FAQ` array for Google rich results.
