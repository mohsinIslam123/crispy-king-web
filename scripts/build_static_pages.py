#!/usr/bin/env python3
"""Build the static supporting pages (menu.html, delivery.html) and sitemap.xml.

Single source of truth:
  - Menu items come from the inline `menuData` object in index.html (the same data
    the homepage renders). Combos come from the `.combo-card` blocks in index.html.
  - Page CSS is the <style> block of index.html, so the pages match the homepage.

Run from the repository root after changing prices or menu items:
    python3 scripts/build_static_pages.py
"""
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://crispyking.store"
TODAY = "2026-11-22"
WA = "https://wa.me/917895743536"
PHONE_MAIN = "7895743536"

index_src = (ROOT / "index.html").read_text(encoding="utf-8")

# ---------- read menu data from index.html ----------
start = index_src.index("const menuData = {")
end = index_src.index("\n};", start)
menu_block = index_src[start:end]
CATEGORY_LABELS = {
    "veg-burgers": "Veg Burgers",
    "nonveg-burgers": "Non-Veg Burgers",
    "chicken": "Chicken Items",
    "fries": "Fries & Sides",
    "pizza": "Pizza",
    "wraps": "Wraps",
    "sandwich": "Sandwich & Subway",
    "shakes": "Shakes",
}
menu = []
for cat, body in re.findall(r"'([a-z\-]+)':\s*\[(.*?)\n  \]", menu_block, re.S):
    items = [(n, int(p_), d.replace("\\'", "'")) for n, p_, d in re.findall(
        r"\{name:'([^']+)', price:(\d+), emoji:'[^']*'(?:, image:'[^']*')?, desc:'((?:[^'\\]|\\.)*)'\}", body)]
    assert items, f"no items parsed for {cat}"
    menu.append((cat, [(n, int(p), d) for n, p, d in items]))
assert [c for c, _ in menu] == list(CATEGORY_LABELS), "unexpected menu categories"

# ---------- read combos from index.html ----------
combos = []
combo_chunks = re.split(r'<div class="combo-card[^"]*">', index_src)[1:]
for chunk in combo_chunks:
    block = chunk.split('<div class="combo-card')[0].split('</section>')[0]
    name = re.search(r'<div class="combo-name">([^<]+)</div>', block)
    price = re.search(r'<div class="combo-price">₹(\d+)</div>', block)
    items = re.findall(r"<li>([^<]+)</li>", block)
    if name and price:
        combos.append((name.group(1).strip(), int(price.group(1)), items))
assert len(combos) >= 5, f"expected combos, got {len(combos)}"

# ---------- shared page pieces ----------
style_block = re.search(r"<style>.*?</style>", index_src, re.S).group(0)
ga_id = re.search(r"gtag\('config', '([^']+)'\)", index_src).group(1)
GA = (f'<script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>\n'
      "<script>\n  window.dataLayer = window.dataLayer || [];\n  function gtag(){dataLayer.push(arguments);}\n"
      f"  gtag('js', new Date());\n  gtag('config', '{ga_id}');\n</script>")
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800;900&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">')

PAGE_CSS = """
  /* ---- supporting pages (menu.html, delivery.html) ---- */
  .site-head { position: sticky; top: 0; z-index: 50; background: rgba(6,6,6,0.94); border-bottom: 1px solid var(--border); }
  .pnav { max-width: 1100px; margin: 0 auto; padding: 14px 18px; display: flex; align-items: center; justify-content: space-between; gap: 14px; flex-wrap: wrap; }
  .pnav-logo { color: #fff; text-decoration: none; font-family: 'Poppins', sans-serif; font-weight: 800; font-size: 18px; }
  .pnav-logo span { color: var(--gold); }
  .pnav-links { display: flex; flex-wrap: wrap; gap: 18px; }
  .pnav-links a { color: rgba(255,255,255,0.8); text-decoration: none; font-size: 14px; }
  .pnav-links a:hover { color: var(--gold); }
  .page-wrap { max-width: 960px; margin: 0 auto; padding: 32px 18px 64px; }
  .crumbs { font-size: 13px; color: var(--gray); margin-bottom: 14px; }
  .crumbs a { color: var(--gray); }
  .page-wrap h1 { font-family: 'Poppins', sans-serif; font-weight: 900; font-size: clamp(26px, 6vw, 40px); line-height: 1.15; color: #fff; margin-bottom: 14px; }
  .page-wrap h2 { font-family: 'Poppins', sans-serif; font-weight: 800; font-size: 21px; color: #fff; margin: 40px 0 12px; padding-bottom: 8px; border-bottom: 1px solid var(--border); }
  .page-wrap h3 { font-family: 'Poppins', sans-serif; font-weight: 700; font-size: 16px; color: #fff; margin: 20px 0 6px; }
  .page-wrap h1 .gold, .page-wrap h2 .gold { color: var(--gold); }
  .page-wrap p, .page-wrap li { color: rgba(255,255,255,0.75); font-size: 15px; line-height: 1.75; }
  .page-wrap ul.plain { padding-left: 20px; }
  .page-wrap .updated { font-size: 12px; color: var(--gray); }
  .cta-row { display: flex; flex-wrap: wrap; gap: 12px; margin: 22px 0; }
  .menu-table { width: 100%; border-collapse: collapse; font-size: 14px; }
  .menu-table th, .menu-table td { padding: 11px 10px; border-bottom: 1px solid rgba(255,215,0,0.12); text-align: left; vertical-align: top; }
  .menu-table th { color: var(--gold); font-size: 11px; text-transform: uppercase; letter-spacing: 1px; }
  .menu-table td { color: rgba(255,255,255,0.85); }
  .menu-table td small { display: block; color: var(--gray); font-size: 12px; line-height: 1.5; margin-top: 2px; }
  .menu-table .price { text-align: right; white-space: nowrap; color: var(--gold); font-weight: 700; }
  .site-foot { border-top: 1px solid var(--border); padding: 28px 18px; text-align: center; color: var(--gray); font-size: 13px; line-height: 1.8; }
  .site-foot a { color: var(--gray); }
"""

def head(title, description, canonical_path, jsonld):
    canonical = f"{SITE}{canonical_path}"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{GA}
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title, quote=False)}</title>
<meta name="description" content="{html.escape(description)}">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}/og-image.jpg">
<meta property="og:locale" content="en_IN">
<meta property="og:site_name" content="Crispy King Muradnagar">
<meta name="theme-color" content="#C0001A">
<link rel="icon" type="image/png" sizes="48x48" href="/favicon-48.png">
<link rel="icon" type="image/png" sizes="192x192" href="/icon-192.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
{FONTS}
<script type="application/ld+json">
{json.dumps(jsonld, ensure_ascii=False, indent=2)}
</script>
{style_block}
<style>{PAGE_CSS}</style>
</head>
<body>
<header class="site-head"><div class="pnav">
  <a href="/" class="pnav-logo">👑 Crispy <span>King</span> Muradnagar</a>
  <nav class="pnav-links" aria-label="Main">
    <a href="/">Home</a><a href="/menu.html">Menu</a><a href="/delivery.html">Delivery</a>
  </nav>
  <a href="{WA}" class="btn-order-nav" target="_blank" rel="noopener">Abhi Order Karo 🍔</a>
</div></header>
"""

FOOT = f"""<footer class="site-foot">
  <p>Crispy King Muradnagar · Near Bilal Masjid, Rawli Road, Muradnagar, Ghaziabad, UP 201206</p>
  <p><a href="/">Home</a> · <a href="/menu.html">Menu</a> · <a href="/delivery.html">Delivery</a> · <a href="tel:{PHONE_MAIN}">Call {PHONE_MAIN}</a> · <a href="{WA}">WhatsApp</a></p>
</footer>
</body>
</html>
"""

# ---------- menu.html ----------
menu_jsonld_sections = []
for cat, items in menu:
    menu_jsonld_sections.append({
        "@type": "MenuSection", "name": CATEGORY_LABELS[cat],
        "hasMenuItem": [{"@type": "MenuItem", "name": n, "description": d,
                         "offers": {"@type": "Offer", "price": str(p), "priceCurrency": "INR"}}
                        for n, p, d in items]})
menu_jsonld_sections.append({
    "@type": "MenuSection", "name": "Combos",
    "hasMenuItem": [{"@type": "MenuItem", "name": n,
                     "description": ", ".join(it),
                     "offers": {"@type": "Offer", "price": str(p), "priceCurrency": "INR"}}
                    for n, p, it in combos]})
menu_jsonld = {"@context": "https://schema.org", "@graph": [
    {"@type": "Menu", "@id": f"{SITE}/menu.html#menu", "name": "Crispy King Muradnagar Menu",
     "inLanguage": "en-IN", "dateModified": TODAY,
     "provider": {"@id": f"{SITE}/#restaurant"},
     "hasMenuSection": menu_jsonld_sections},
    {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
        {"@type": "ListItem", "position": 2, "name": "Menu", "item": f"{SITE}/menu.html"}]},
]}

def table(rows_html):
    return ('<table class="menu-table"><thead><tr><th>Item</th><th>Details</th><th class="price">Price (₹)</th></tr></thead>'
            f'<tbody>{rows_html}</tbody></table>')

sections = []
for cat, items in menu:
    rows = "".join(
        f'<tr><td>{html.escape(n, quote=False)}</td><td>{html.escape(d, quote=False)}</td>'
        f'<td class="price">₹{p}</td></tr>' for n, p, d in items)
    sections.append(f'<h2 id="{cat}">{html.escape(CATEGORY_LABELS[cat], quote=False)} <span class="gold">👑</span></h2>\n' + table(rows))
combo_rows = "".join(
    f'<tr><td>{html.escape(n, quote=False)}</td><td>{html.escape(", ".join(it), quote=False)}</td>'
    f'<td class="price">₹{p}</td></tr>' for n, p, it in combos)
sections.append('<h2 id="combos">Combos <span class="gold">👑</span></h2>\n' + table(combo_rows))

item_count = sum(len(i) for _, i in menu)
menu_title = "Crispy King Muradnagar Menu & Prices | Halal Burgers"
menu_desc = ("Crispy King Muradnagar ka poora halal menu aur prices: burgers, chicken, pizza, wraps, "
             "sandwiches, shakes aur combos. WhatsApp pe order karein: 7895743536.")
menu_body = f"""<main class="page-wrap">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> › Menu</nav>
  <h1>Crispy King Muradnagar Menu — <span class="gold">Halal Burgers, Chicken, Pizza &amp; Shakes</span></h1>
  <p>Yeh Crispy King Muradnagar ka poora menu hai, {item_count} items aur {len(combos)} combos, sab prices INR mein. Sab items 100% Halal Certified brand ke standards par bante hain. Order ke liye WhatsApp ya call karein.</p>
  <p class="updated">Last updated: 22 November 2026. Prices badal sakte hain, order se pehle confirm karein.</p>
  <div class="cta-row">
    <a class="btn-primary" href="{WA}" target="_blank" rel="noopener">🍔 WhatsApp pe Order Karo</a>
    <a class="btn-outline" href="tel:{PHONE_MAIN}">📞 Call {PHONE_MAIN}</a>
  </div>
  {chr(10).join(sections)}
  <h2>Delivery aur order</h2>
  <p>3 km ke radius mein FREE home delivery, delivery charge ₹0, minimum order ₹350. Poori details ke liye <a href="/delivery.html" style="color:var(--gold)">Delivery page</a> dekhein.</p>
</main>
"""
menu_html = head(menu_title, menu_desc, "/menu.html", menu_jsonld) + menu_body + FOOT
(ROOT / "menu.html").write_text(menu_html, encoding="utf-8")

# ---------- delivery.html ----------
DELIVERY_FAQS = [
    ("Delivery kitni door tak milti hai?",
     "3 km ke radius tak FREE delivery milti hai. 3 km ke bahar ka order ho toh pehle 7895743536 par confirm karein."),
    ("Delivery ka time kitna lagta hai?",
     "Average delivery time 20 se 30 minutes hai."),
    ("Delivery ke liye koi charge lagta hai?",
     "Nahi. 3 km ke andar delivery charge ₹0 hai. Minimum order ₹350 hai."),
    ("Delivery ka order kaise karein?",
     f"WhatsApp pe {PHONE_MAIN} par message karein ya call karein. Cash on Delivery ya UPI se pay karein."),
]
delivery_jsonld = {"@context": "https://schema.org", "@graph": [
    {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
        {"@type": "ListItem", "position": 2, "name": "Delivery", "item": f"{SITE}/delivery.html"}]},
    {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
        for q, a in DELIVERY_FAQS]},
]}
faq_html = "".join(f'<h3>{html.escape(q, quote=False)}</h3>\n<p>{html.escape(a, quote=False)}</p>\n' for q, a in DELIVERY_FAQS)
delivery_title = "Crispy King Muradnagar Delivery | 3 km Free Home Delivery"
delivery_desc = ("Crispy King Muradnagar: 3 km tak FREE home delivery, delivery charge ₹0, minimum order ₹350. "
                 "Rawli Road, Modinagar, Hapur Road, Duhai. Order: 7895743536.")
delivery_body = f"""<main class="page-wrap">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> › Delivery</nav>
  <h1>Crispy King Muradnagar Delivery — <span class="gold">3 km Tak FREE</span></h1>
  <p>Crispy King Muradnagar 3 km ke radius mein FREE home delivery deta hai, delivery charge ₹0 aur minimum order ₹350. Delivery area: Muradnagar, Rawli Road, Modinagar, Hapur Road aur Duhai. Order ke liye WhatsApp {PHONE_MAIN}.</p>
  <p class="updated">Last updated: 22 November 2026</p>
  <div class="cta-row">
    <a class="btn-primary" href="{WA}" target="_blank" rel="noopener">🍔 WhatsApp pe Order Karo</a>
    <a class="btn-outline" href="/menu.html">📋 Poora Menu Dekho</a>
  </div>
  <h2>Delivery area</h2>
  <ul class="plain">
    <li>Muradnagar</li><li>Rawli Road</li><li>Modinagar</li><li>Hapur Road</li><li>Duhai</li>
  </ul>
  <h2>Delivery charge aur minimum order</h2>
  <ul class="plain">
    <li>3 km ke andar delivery charge: ₹0</li>
    <li>Minimum order (delivery ke liye): ₹350</li>
    <li>Average delivery time: 20 se 30 minutes</li>
  </ul>
  <h2>Timings</h2>
  <p>Somvar se Ravivar, subah 11:00 AM se raat 11:00 PM tak.</p>
  <h2>Payment</h2>
  <p>Cash on Delivery aur UPI dono accept hote hain (GPay, PhonePe, Paytm, BHIM).</p>
  <h2>Delivery ke sawaal</h2>
  {faq_html}
  <h2>Restaurant</h2>
  <p>Near Bilal Masjid, Rawli Road, Muradnagar, Ghaziabad, UP 201206. Call: <a href="tel:{PHONE_MAIN}" style="color:var(--gold)">{PHONE_MAIN}</a>.</p>
</main>
"""
delivery_html = head(delivery_title, delivery_desc, "/delivery.html", delivery_jsonld) + delivery_body + FOOT
(ROOT / "delivery.html").write_text(delivery_html, encoding="utf-8")

# ---------- sitemap.xml ----------
urls = ["/", "/menu.html", "/delivery.html"]
sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + "".join(f"  <url><loc>{SITE}{u}</loc><lastmod>{TODAY}</lastmod></url>\n" for u in urls)
           + "</urlset>\n")
(ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")

print(f"menu items={item_count} combos={len(combos)} -> menu.html, delivery.html, sitemap.xml written")
