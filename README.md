# Isra.Peptides

Bilingual (Hebrew / English) research-use-only peptide reference and catalog website.
Brand: Isra.Peptides (Amino Chains Solutions). Israel based, worldwide shipping.

> RESEARCH USE ONLY. Educational and reference content. Not medical advice.
> Products are not for human or animal consumption. No dosing or administration
> guidance is provided anywhere on the site.

## Stack

- Single-file vanilla site: all HTML, CSS and JavaScript live in `index.html`.
- No framework, no build step, no dependencies to install.
- Single-page app with a hash router (`#products`, `#product/<id>`, `#explore`, ...).
- Progressive Web App (`manifest.json` + `sw.js`, offline caching).
- Fully bilingual HE (RTL) / EN (LTR), toggled at runtime.

## Structure

```
index.html        Host-ready site (inline CSS+JS, relative img/ paths)
standalone.html   Self-contained copy (images inlined as base64; open directly, no server)
img/              Images and generated product visuals
manifest.json     PWA manifest
sw.js             Service worker (cache-first)
CLAUDE.md         Conventions for editing with Claude Code
netlify.toml      Netlify config (publish root)
.github/workflows/pages.yml   GitHub Pages deploy
```

## Local preview

Serve over HTTP (not file://) so relative paths and the service worker work:

```bash
python3 -m http.server 8080
# then open http://localhost:8080
```

`standalone.html` can be opened directly in a browser with no server.

## Deploy

GitHub Pages: push to `main`, then in the repo go to Settings -> Pages and set
the source to "GitHub Actions". The included workflow deploys the root on every push.

Netlify: connect the repo (no build command, publish directory = root) or drag the
folder into the Netlify dashboard.

Vercel: import the repo, framework preset = Other, output directory = root.

## Editing

The whole app is `index.html`. See CLAUDE.md for architecture, data structures and
the rules that must be preserved (research-use-only framing, verified chemical data,
bilingual parity, design tokens). When you change cached assets, bump the cache name
in `sw.js` so clients pick up the update.
