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
