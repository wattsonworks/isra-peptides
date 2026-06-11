#!/usr/bin/env python3
"""Prerender static, crawlable HTML pages for the Isra.Peptides SPA.

The live site is a client-side hash-router SPA -> Google effectively sees ONE URL.
This emits a real HTML page per product at /p/<id>/ plus a /catalog/ hub and a full
sitemap, so the 63 compounds become indexable. Pages carry genuine content (no
cloaking) and link into the interactive app. Re-run after catalog changes:
    python build/prerender.py
"""
import re, os, html, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://wattsonworks.github.io/isra-peptides"
src = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
script = re.search(r"<script>(.*)</script>", src, re.DOTALL).group(1)

ESC = {'n':'\n','t':'\t','r':'\r','b':'\b','f':'\f','v':'\v','0':'\0'}
def pjs(s, i):
    q = s[i]; i += 1; o = []
    while i < len(s):
        c = s[i]
        if c == '\\':
            nx = s[i+1]
            if nx == 'u':
                o.append(chr(int(s[i+2:i+6], 16))); i += 6; continue
            if nx == 'x':
                o.append(chr(int(s[i+2:i+4], 16))); i += 4; continue
            o.append(ESC.get(nx, nx)); i += 2; continue
        if c == q:
            return ''.join(o), i+1
        o.append(c); i += 1
    return ''.join(o), i
def he_en_after(s, key, start, window=1200):
    seg = s[start:start+window]
    m = re.search(re.escape(key) + r":\{he:", seg)
    if not m:
        return ('', '')
    i = start + m.end()
    he, i = pjs(s, i)
    j = s.index("en:", i)
    en, _ = pjs(s, j+3)
    return (he, en)

# ---- products ----
prods, seen = [], set()
for mm in re.finditer(r"\{id:'([^']+)',name:'([^']*)',mg:'([^']*)',", script):
    pid = mm.group(1)
    if pid in seen: continue
    seen.add(pid)
    win = script[mm.end():mm.end()+3000]
    def f1(key, default=''):
        m = re.search(key + r":'([^']*)'", win); return m.group(1) if m else default
    sum_he, sum_en = he_en_after(script, "sum", mm.end())
    over_he, over_en = he_en_after(script, "over", mm.end())
    prods.append(dict(id=pid, name=mm.group(2), mg=mm.group(3), img=f1('img', pid),
                      purity=f1('purity', '≥ 98%'), cat=f1('cat'),
                      sum_he=sum_he, sum_en=sum_en, over_he=over_he, over_en=over_en))
for p in prods:
    for k, v in {'bpc157':'recovery','cjc1295':'gh','epitalon':'longevity','motsc':'metabolic','tb500':'recovery'}.items():
        if p['id'] == k: p['cat'] = v

# ---- CHEM ----
def field(blk, key):
    m = re.search(key + r":'([^']*)'", blk); return m.group(1) if m else ''
chem = {}
for m in re.finditer(r"(?:CHEM\.([A-Za-z0-9_]+)=|\b([a-z0-9]+):)\{([^{}]*)\}", script):
    pid = m.group(1) or m.group(2); blk = m.group(3)
    if 'formula:' in blk or 'mw:' in blk or 'seq:' in blk:
        chem.setdefault(pid, dict(seq=field(blk,'seq'), formula=field(blk,'formula'),
                                  mw=field(blk,'mw'), cas=field(blk,'cas'), store=field(blk,'store')))

# ---- IMG map ----
img = {}
mb = re.search(r"var IMG=\{(.+?)\};", script, re.DOTALL)
if mb:
    for k, v in re.findall(r'([A-Za-z0-9_]+):"(img/[^"]+)"', mb.group(1)):
        img[k] = v
for k, v in re.findall(r'IMG\.([A-Za-z0-9_]+)=[\'"](img/[^\'"]+)[\'"]', script):
    img[k] = v

CAT = {'recovery':('שיקום ותיקון','Recovery & Repair'),'gh':('הורמון גדילה','Growth Hormone'),
 'metabolic':('מטבולי','Metabolic'),'immune':('מערכת החיסון','Immune'),
 'cognitive':('נוירו וקוגניציה','Neuro & Cognitive'),'longevity':('אריכות ימים','Longevity'),
 'skin':('עור','Skin'),'melano':('מלנוקורטין','Melanocortin'),'ancillary':('נלווים','Ancillary')}

E = lambda s: html.escape(s or '', quote=True)
CSS = """*{margin:0;box-sizing:border-box}body{font-family:Heebo,system-ui,Arial,sans-serif;background:#05070f;color:#eaedf6;line-height:1.65;margin:0}
a{color:#e6c977;text-decoration:none}a:hover{text-decoration:underline}.wrap{max-width:860px;margin:0 auto;padding:0 20px}
header{border-bottom:1px solid rgba(201,162,75,.18);padding:14px 0;background:rgba(5,7,15,.8)}
header .wrap{display:flex;align-items:center;gap:12px}header img{width:38px;height:38px;border-radius:50%}
header b{font-weight:800}.crumb{font-size:13px;color:#9aa3b8;margin:22px 0 6px}.crumb a{color:#9aa3b8}
h1{font-size:32px;font-family:'Playfair Display',serif;margin:4px 0 10px}.mg{color:#9aa3b8;font-size:18px}
.badges{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0 18px}.badge{border:1px solid rgba(201,162,75,.3);border-radius:999px;padding:5px 12px;font-size:12.5px;color:#e6c977}
.ruo{border-color:rgba(224,107,107,.35);color:#f0b3b3}.hero-img{width:100%;max-width:420px;border-radius:16px;border:1px solid rgba(201,162,75,.18);display:block;margin:0 0 20px}
h2{font-size:15px;letter-spacing:1px;color:#c9a24b;border-bottom:1px solid rgba(201,162,75,.15);padding-bottom:6px;margin:26px 0 10px;text-transform:uppercase}
p{margin:0 0 12px;color:#c7cdda}table{width:100%;border-collapse:collapse;margin:6px 0}td{border:1px solid rgba(201,162,75,.15);padding:8px 11px;font-size:13.5px}td.k{color:#c9a24b;width:42%}
.cta{display:inline-block;background:linear-gradient(180deg,#e6c977,#9a7a32);color:#05070f;font-weight:800;border-radius:11px;padding:12px 20px;margin:18px 0}.cta:hover{text-decoration:none}
.rel{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0 0}.rel a{border:1px solid rgba(201,162,75,.2);border-radius:999px;padding:6px 13px;font-size:13px;color:#c7cdda}
footer{border-top:1px solid rgba(201,162,75,.15);margin-top:40px;padding:26px 0;color:#6c7690;font-size:12.5px;text-align:center}
.rtl{direction:rtl;text-align:right}.ltr{direction:ltr;text-align:left}"""

FONTS = '<link href="https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;700;800&family=Playfair+Display:wght@600;700&display=swap" rel="stylesheet">'

def head(title, desc, url, image, jsonld):
    return f"""<!DOCTYPE html><html lang="he" dir="rtl"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{E(title)}</title><meta name="description" content="{E(desc)}">
<link rel="canonical" href="{url}"><meta name="robots" content="index,follow">
<link rel="icon" href="{SITE}/img/logo.jpg">
<meta property="og:type" content="website"><meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{url}">
<meta property="og:image" content="{image}"><meta property="og:site_name" content="Isra.Peptides">
<meta name="twitter:card" content="summary_large_image">
{FONTS}<style>{CSS}</style>
<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>
</head><body>
<header><div class="wrap"><img src="{SITE}/img/logo.jpg" alt="Isra.Peptides"><b>Isra<span style="color:#e6c977">.</span>Peptides</b><span style="color:#6c7690;font-size:12px;margin-inline-start:auto">RESEARCH · SCIENCE · RESULTS</span></div></header>
<main class="wrap">"""

FOOT = ('</main><footer><div class="wrap">RESEARCH USE ONLY · NOT FOR HUMAN CONSUMPTION · NOT MEDICAL ADVICE'
        '<br>© Isra.Peptides · Amino Chains Solutions · '
        f'<a href="{SITE}/">interactive catalog</a> · <a href="{SITE}/catalog/">all products</a> · '
        f'<a href="{SITE}/about.html">about</a></div></footer></body></html>')

os.makedirs(os.path.join(ROOT, "p"), exist_ok=True)
sitemap = [(SITE + "/", "1.0", "weekly"), (SITE + "/catalog/", "0.9", "weekly"), (SITE + "/about.html", "0.7", "monthly")]
by_cat = {}
for p in prods:
    by_cat.setdefault(p['cat'], []).append(p)

for p in prods:
    pid = p['id']; url = f"{SITE}/p/{pid}/"
    cat_he, cat_en = CAT.get(p['cat'], ('', ''))
    image = f"{SITE}/{img.get(p['img'], 'img/logo.jpg')}"
    ch = chem.get(pid, {})
    desc = (p['sum_en'] or p['sum_he'] or f"{p['name']} research peptide")[:300]
    ld_prod = {"@context":"https://schema.org","@type":"Product","@id":url+"#product",
        "name":p['name'],"category":f"Research chemical (RUO) · {cat_en}","description":desc,"url":url,
        "image":image,"brand":{"@id":SITE+"/#org"},"isRelatedTo":{"@id":SITE+"/#website"}}
    extra = []
    if ch.get('cas'): extra.append({"@type":"PropertyValue","name":"CAS","value":ch['cas']})
    if ch.get('mw'): extra.append({"@type":"PropertyValue","name":"Molecular weight","value":ch['mw']})
    if extra: ld_prod["additionalProperty"] = extra
    if ch.get('formula'): ld_prod["material"] = ch['formula']
    ld_crumb = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Catalog","item":SITE+"/catalog/"},
        {"@type":"ListItem","position":2,"name":p['name'],"item":url}]}
    title = f"{p['name']} ({p['mg']}, {p['purity']}) — {cat_en} research peptide | Isra.Peptides"

    def chem_rows(lang):
        L = lambda he,en: he if lang=='he' else en
        rows = ""
        for k, v in [(L('רצף','Sequence'), ch.get('seq')),(L('נוסחה','Formula'), ch.get('formula')),
                     (L('משקל מולקולרי','Molecular weight'), (ch.get('mw')+' g/mol') if ch.get('mw') else ''),
                     ('CAS', ch.get('cas')),(L('אחסון','Storage'), ch.get('store'))]:
            if v: rows += f'<tr><td class="k">{E(k)}</td><td>{E(v)}</td></tr>'
        return f'<table>{rows}</table>' if rows else ''

    related = [q for q in by_cat.get(p['cat'], []) if q['id'] != pid][:5]
    rel_html = ''.join(f'<a href="../{q["id"]}/">{E(q["name"])}</a>' for q in related)

    body = head(title, desc, url, image, ld_prod)
    body += f'<script type="application/ld+json">{json.dumps(ld_crumb, ensure_ascii=False)}</script>'
    body += (f'<div class="crumb"><a href="{SITE}/catalog/">קטלוג · Catalog</a> › {E(p["name"])}</div>'
        f'<h1>{E(p["name"])} <span class="mg">{E(p["mg"])}</span></h1>'
        f'<div class="badges"><span class="badge">{E(cat_he)} · {E(cat_en)}</span>'
        f'<span class="badge">{E(p["purity"])}</span><span class="badge ruo">RESEARCH USE ONLY</span></div>'
        f'<img class="hero-img" src="{image}" alt="{E(p["name"])}" loading="lazy">')
    # Hebrew block
    body += '<div class="rtl">'
    body += f'<h2>תיאור</h2><p>{E(p["over_he"] or p["sum_he"])}</p>'
    body += chem_rows('he')
    body += '</div>'
    # English block
    body += '<div class="ltr">'
    body += f'<h2>Overview</h2><p>{E(p["over_en"] or p["sum_en"])}</p>'
    body += chem_rows('en')
    body += '</div>'
    body += f'<a class="cta" href="{SITE}/#product/{pid}">פתח בקטלוג האינטראקטיבי · Open in the interactive catalog →</a>'
    if rel_html:
        body += f'<h2>מתחמים קשורים · Related</h2><div class="rel">{rel_html}</div>'
    body += ('<p style="font-size:12px;color:#6c7690;margin-top:22px">המידע לחינוך ומחקר בלבד ואינו ייעוץ רפואי. '
             'Information is for research and education only and is not medical advice. '
             'Chemical data sourced from public references (PubChem).</p>')
    body += FOOT
    os.makedirs(os.path.join(ROOT, "p", pid), exist_ok=True)
    open(os.path.join(ROOT, "p", pid, "index.html"), "w", encoding="utf-8").write(body)
    sitemap.append((url, "0.8", "monthly"))

# ---- catalog hub ----
cat_url = SITE + "/catalog/"
ld_items = {"@context":"https://schema.org","@type":"CollectionPage","@id":cat_url+"#catalog",
    "name":"Isra.Peptides Catalog","url":cat_url,"isPartOf":{"@id":SITE+"/#website"},
    "mainEntity":{"@type":"ItemList","numberOfItems":len(prods),
        "itemListElement":[{"@type":"ListItem","position":i+1,"name":p['name'],"url":f"{SITE}/p/{p['id']}/"} for i,p in enumerate(prods)]}}
cbody = head("Catalog — 63 research peptides | Isra.Peptides",
             "Full index of Isra.Peptides research-use-only peptides with molecular data — BPC-157, Semaglutide, MOTS-c, Retatrutide and more.",
             cat_url, f"{SITE}/img/banner.jpg", ld_items)
cbody += '<div class="crumb"><a href="'+SITE+'/">Isra.Peptides</a> › Catalog</div><h1>קטלוג הפפטידים · Peptide Catalog</h1>'
cbody += f'<p>{len(prods)} מתחמים למחקר · {len(prods)} research compounds. כל המוצרים למחקר בלבד.</p>'
order = ['gh','metabolic','recovery','longevity','cognitive','immune','skin','melano','ancillary']
for c in order:
    items = by_cat.get(c, [])
    if not items: continue
    he, en = CAT[c]
    cbody += f'<h2>{E(he)} · {E(en)}</h2><div class="rel">'
    cbody += ''.join(f'<a href="{SITE}/p/{p["id"]}/">{E(p["name"])} <span style="color:#6c7690">{E(p["mg"])}</span></a>' for p in items)
    cbody += '</div>'
cbody += f'<a class="cta" href="{SITE}/#products">פתח קטלוג אינטראקטיבי · Open interactive catalog →</a>'
cbody += FOOT
os.makedirs(os.path.join(ROOT, "catalog"), exist_ok=True)
open(os.path.join(ROOT, "catalog", "index.html"), "w", encoding="utf-8").write(cbody)

# ---- sitemap ----
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for loc, pri, freq in sitemap:
    sm.append(f'  <url><loc>{loc}</loc><changefreq>{freq}</changefreq><priority>{pri}</priority></url>')
sm.append('</urlset>')
open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write('\n'.join(sm))

print(f"prerendered {len(prods)} product pages + catalog hub; sitemap has {len(sitemap)} URLs")
print("CHEM coverage:", sum(1 for p in prods if chem.get(p['id'])), "/", len(prods))
