#!/usr/bin/env python3
"""Batch optimization fixes for NexifyAI website."""
import re
import os
import glob

REPO = os.path.dirname(os.path.abspath(__file__))
os.chdir(REPO)

WORKER_URL = 'https://chatbox.yuanxin0222.workers.dev'
BASE_URL = 'https://nexifyai.org'

ALL_HTML = sorted(glob.glob('*.html'))
print("Found HTML files:", ALL_HTML)

# Internal filenames eligible for .html -> clean path link rewriting
INTERNAL_FILES = [f for f in ALL_HTML if f not in ('index.html', '404.html')]

FONT_LINK = (
    '<link rel="preload" as="style" '
    'href="https://api.fontshare.com/v2/css?f[]=zodiak@400,500,700&f[]=satoshi@400,500,700,900&display=swap">\n'
    '<link rel="stylesheet" '
    'href="https://api.fontshare.com/v2/css?f[]=zodiak@400,500,700&f[]=satoshi@400,500,700,900&display=swap">\n'
)

FAVICON_LINKS = (
    '<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">\n'
    '<link rel="icon" type="image/x-icon" href="/favicon.ico">\n'
    '<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">\n'
)

ABOUT_THEME_BTN = '''      <button class="theme-btn" data-theme-toggle aria-label="Toggle theme">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
      </button>'''

COOKIE_BANNER = '''
<div id="nx-cookie-banner" style="position:fixed;left:16px;right:16px;bottom:16px;max-width:640px;margin:0 auto;background:#153122;color:#f7fff8;padding:16px 20px;border-radius:14px;box-shadow:0 18px 40px rgba(0,0,0,.25);z-index:9999;display:none;font-family:inherit;font-size:.9rem;line-height:1.5;">
  <span id="nx-cookie-text">We use essential cookies and Google Fonts to run this site. By continuing, you agree to our <a href="/privacy" style="color:#78df97;text-decoration:underline;">Privacy Policy</a>.</span>
  <button id="nx-cookie-accept" style="margin-left:12px;background:#2daa58;color:#fff;border:none;padding:8px 16px;border-radius:8px;cursor:pointer;font-weight:600;white-space:nowrap;">Got it</button>
</div>
<script>
(function(){
  var TXT = {
    en: {t:'We use essential cookies and Google Fonts to run this site. By continuing, you agree to our <a href="/privacy" style="color:#78df97;text-decoration:underline;">Privacy Policy</a>.', b:'Got it'},
    nl: {t:'We gebruiken essenti\\u00eble cookies en Google Fonts om deze site te laten werken. Door verder te gaan ga je akkoord met ons <a href="/privacy" style="color:#78df97;text-decoration:underline;">Privacybeleid</a>.', b:'Begrepen'},
    fr: {t:'Nous utilisons des cookies essentiels et Google Fonts pour faire fonctionner ce site. En continuant, vous acceptez notre <a href="/privacy" style="color:#78df97;text-decoration:underline;">politique de confidentialit\\u00e9</a>.', b:'Compris'}
  };
  try {
    if (localStorage.getItem('nexify_cookie_ack')) return;
    var lang = (localStorage.getItem('nexify_lang') || navigator.language || 'en').slice(0,2);
    if (!TXT[lang]) lang = 'en';
    var el = document.getElementById('nx-cookie-banner');
    document.getElementById('nx-cookie-text').innerHTML = TXT[lang].t;
    document.getElementById('nx-cookie-accept').textContent = TXT[lang].b;
    el.style.display = 'block';
    document.getElementById('nx-cookie-accept').addEventListener('click', function(){
      localStorage.setItem('nexify_cookie_ack', '1');
      el.style.display = 'none';
    });
  } catch(e) {}
})();
</script>
'''

stats = {
    'api_url_fixed': [],
    'theme_icon_fixed': [],
    'fonts_added': [],
    'favicons_added': [],
    'og_added': [],
    'cookie_added': [],
    'links_cleaned': [],
    'skipped_no_head': [],
}

for fname in ALL_HTML:
    with open(fname, 'r', encoding='utf-8') as f:
        content = f.read()
    original = content
    slug = fname[:-5]  # strip .html
    canonical_path = '/' if fname == 'index.html' else f'/{slug}'
    canonical_url = BASE_URL + canonical_path

    # --- 1. API_URL fix ---
    if "const API_URL = '';" in content:
        content = content.replace("const API_URL = '';", f"const API_URL = '{WORKER_URL}';")
        stats['api_url_fixed'].append(fname)

    # --- 2. Theme icon fix (button + JS) ---
    # button variants
    btn_patterns = [
        '<button class="theme-btn" data-theme-toggle aria-label="Toggle theme">\u263e</button>',
        '<button class="theme-btn" data-theme-toggle aria-label="Toggle theme">&#9790;</button>',
    ]
    btn_changed = False
    for pat in btn_patterns:
        if pat in content:
            content = content.replace(pat, ABOUT_THEME_BTN)
            btn_changed = True
    # JS line variants (delete the textContent swap line entirely)
    js_pattern = re.compile(r"\n\s*if\(themeBtn\)\s*themeBtn\.textContent\s*=\s*theme\s*===\s*'dark'\s*\?\s*'[^']*'\s*:\s*'[^']*';")
    if js_pattern.search(content):
        content = js_pattern.sub('', content)
        btn_changed = True
    if btn_changed:
        stats['theme_icon_fixed'].append(fname)

    # --- 3. Font loading (insert after preconnect lines, before <style> or before </head>) ---
    if '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>' in content and 'api.fontshare.com' not in content:
        content = content.replace(
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n' + FONT_LINK,
            1
        )
        stats['fonts_added'].append(fname)
    elif '</head>' in content and 'api.fontshare.com' not in content:
        content = content.replace('</head>', FONT_LINK + '</head>', 1)
        stats['fonts_added'].append(fname)

    # --- 4. Favicon links ---
    if '<title>' in content and 'favicon' not in content.lower():
        content = re.sub(r'(<title>.*?</title>)', r'\1\n' + FAVICON_LINKS.rstrip('\n'), content, count=1, flags=re.S)
        stats['favicons_added'].append(fname)

    # --- 5. OG tags + canonical + JSON-LD ---
    title_m = re.search(r'<title>(.*?)</title>', content)
    desc_m = re.search(r'<meta name="description" content="([^"]*)"', content)
    title_text = title_m.group(1) if title_m else 'Nexify AI'
    desc_text = desc_m.group(1) if desc_m else 'Nexify AI — 24/7 AI customer service for European SMEs.'
    if 'og:title' not in content:
        og_block = (
            f'<link rel="canonical" href="{canonical_url}">\n'
            f'<meta property="og:type" content="website">\n'
            f'<meta property="og:site_name" content="Nexify AI">\n'
            f'<meta property="og:title" content="{title_text}">\n'
            f'<meta property="og:description" content="{desc_text}">\n'
            f'<meta property="og:url" content="{canonical_url}">\n'
            f'<meta property="og:image" content="{BASE_URL}/logo.png">\n'
            f'<meta name="twitter:card" content="summary_large_image">\n'
            f'<meta name="twitter:title" content="{title_text}">\n'
            f'<meta name="twitter:description" content="{desc_text}">\n'
        )
        if fname == 'index.html':
            og_block += (
                '<script type="application/ld+json">\n'
                '{"@context":"https://schema.org","@type":"Organization","name":"Nexify AI",'
                f'"url":"{BASE_URL}/","logo":"{BASE_URL}/logo.png",'
                '"description":"24/7 AI customer service agent for European SMEs handling chat, phone, and email in 30+ languages.",'
                '"email":"hello@nexifyai.org",'
                '"address":{"@type":"PostalAddress","addressLocality":"The Hague","addressCountry":"NL"},'
                '"identifier":{"@type":"PropertyValue","name":"KVK","value":"42114767"}}\n'
                '</script>\n'
            )
        if '<meta name="description"' in content:
            content = content.replace(
                re.search(r'<meta name="description"[^>]*>', content).group(0),
                re.search(r'<meta name="description"[^>]*>', content).group(0) + '\n' + og_block,
                1
            )
        else:
            content = content.replace('</head>', og_block + '</head>', 1)
        stats['og_added'].append(fname)

    # --- 6. Cookie consent banner (before </body>) ---
    if '</body>' in content and 'nx-cookie-banner' not in content:
        content = content.replace('</body>', COOKIE_BANNER + '</body>', 1)
        stats['cookie_added'].append(fname)

    # --- 7. Internal .html links -> clean paths ---
    before = content
    for internal in INTERNAL_FILES:
        internal_slug = internal[:-5]
        content = re.sub(rf'href="{re.escape(internal)}"', f'href="/{internal_slug}"', content)
        content = re.sub(rf"href='{re.escape(internal)}'", f"href='/{internal_slug}'", content)
    # index.html -> "/"
    content = re.sub(r'href="index\.html"', 'href="/"', content)
    content = re.sub(r"href='index\.html'", "href='/'", content)
    if content != before:
        stats['links_cleaned'].append(fname)

    if content != original:
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(content)

# --- 8. "View Work" -> "View Pricing" label fix in index.html ---
with open('index.html', 'r', encoding='utf-8') as f:
    idx = f.read()
idx2 = idx.replace("heroCtaSecondary:'View Work'", "heroCtaSecondary:'View Pricing'")
idx2 = idx2.replace('data-i18n="heroCtaSecondary">View Work<', 'data-i18n="heroCtaSecondary">View Pricing<')
if idx2 != idx:
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(idx2)
    print("Fixed View Work -> View Pricing label")

for k, v in stats.items():
    print(f"\n{k} ({len(v)}):")
    for x in v:
        print(" -", x)
