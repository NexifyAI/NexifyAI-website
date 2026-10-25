# -*- coding: utf-8 -*-
"""
Phase 1 funnel unification migration (approved plan v2, 2026-10-25).

One-off (but committed for reproducibility) migration that:
  1. Replaces every shared page's <nav> with the canonical nav
     (Pilot dropdown -> Results link; + Sign in; + ⚡ Get Started Free ?from=nav)
  2. Replaces every shared page's <footer> with the canonical footer
     (+ Sign in, - Pilot Program link, Results, ?from=footer)
  3. Injects the nav-cta stylesheet before </head>
  4. Ensures i18n copy keys (en/nl/fr) exist for the new chrome
  5. Re-points body /pilot-apply CTAs to onboarding?from=<tag> + relabels them
  6. Injects the FinalCtaBlock before the footer on the 15 sub-pages
  7. index hero CTA ?from=hero; login register link ?from=login
  8. 404: appends Sign in + CTA to its simplified nav
  9. sitemap.xml drops pilot-apply; writes _redirects; pilot-apply.html
     becomes a tiny fallback page

Idempotent-ish: re-running on migrated pages is a no-op for blocks already
canonical (regex still matches, replacement is identical); copy-key inserts
are guarded by existence checks.
"""
import io
import re
import sys

ONB = "https://agent.nexifyai.org/onboarding"

SHARED = [
    "index.html", "demo.html", "demo-phone.html",
    "pricing-subscription.html", "pricing-payg.html", "pricing-custom.html",
    "pilot-results.html",
    "solutions-restaurants.html", "solutions-general-practice.html",
    "solutions-law-firms.html", "solutions-real-estate.html",
    "solutions-physiotherapy.html", "solutions-dentists.html",
    "solutions-beauty-salons.html",
    "about.html", "contact.html", "privacy.html", "terms.html", "login.html",
]
FINAL_CTA_PAGES = {
    "demo.html", "demo-phone.html",
    "pricing-subscription.html", "pricing-payg.html", "pricing-custom.html",
    "pilot-results.html",
    "solutions-restaurants.html", "solutions-general-practice.html",
    "solutions-law-firms.html", "solutions-real-estate.html",
    "solutions-physiotherapy.html", "solutions-dentists.html",
    "solutions-beauty-salons.html",
    "about.html", "contact.html",
}
FROM_TAG = {
    "pricing-subscription.html": "pricing", "pricing-payg.html": "pricing",
    "pricing-custom.html": "pricing", "demo.html": "demo",
    "demo-phone.html": "demo-phone", "pilot-results.html": "results",
}
for s in FINAL_CTA_PAGES & set(SHARED):
    FROM_TAG.setdefault(s, "solutions" if s.startswith("solutions-") else "page")

NAV = """<nav class="nav" id="site-nav">
      <div class="nav-item">
        <button class="nav-link" data-i18n="navSolutions">Solutions <svg viewBox="0 0 24 24"><polyline points="6 9 12 15 18 9"/></svg></button>
        <div class="dropdown">
          <a href="/solutions-restaurants" data-i18n="navSolRestaurants">Restaurants</a>
          <a href="/solutions-general-practice" data-i18n="navSolGP">General Practice</a>
          <a href="/solutions-law-firms" data-i18n="navSolLaw">Law Firms</a>
          <a href="/solutions-real-estate" data-i18n="navSolRE">Real Estate</a>
          <a href="/solutions-physiotherapy" data-i18n="navSolPhysio">Physiotherapy</a>
          <a href="/solutions-dentists" data-i18n="navSolDentist">Dentists</a>
          <a href="/solutions-beauty-salons" data-i18n="navSolSalon">Beauty & Salons</a>
        </div>
      </div>
      <div class="nav-item">
        <button class="nav-link" data-i18n="navDemo">See It in Action <svg viewBox="0 0 24 24"><polyline points="6 9 12 15 18 9"/></svg></button>
        <div class="dropdown">
          <a href="/demo" data-i18n="navDemoLive">Live Demo</a>
          <a href="/demo-phone" data-i18n="navDemoPhone">Phone Demo</a>
        </div>
      </div>
      <div class="nav-item">
        <button class="nav-link" data-i18n="navPricing">Pricing <svg viewBox="0 0 24 24"><polyline points="6 9 12 15 18 9"/></svg></button>
        <div class="dropdown">
          <a href="/pricing-subscription" data-i18n="navPriceSub">Subscription</a>
          <a href="/pricing-payg" data-i18n="navPricePayg">Pay As You Use</a>
          <a href="/pricing-custom" data-i18n="navPriceCustom">Custom</a>
        </div>
      </div>
      <a href="/pilot-results" data-i18n="navResults">Results</a>
      <a href="/about" data-i18n="navAbout">About</a>
      <a href="/contact" data-i18n="navContact">Contact</a>
      <a href="https://agent.nexifyai.org/admin" class="nav-signin" data-i18n="navSignIn">Sign in</a>
      <a href="https://agent.nexifyai.org/onboarding?from=nav" class="nav-cta" data-i18n="navStartTrial">&#9889; Get Started Free</a>
    </nav>"""

FOOTER = """<footer class="site-footer">
  <div class="container footer-main">
    <div class="footer-grid">
      <div class="footer-brand">
        <a href="/" class="brand">
          <span class="brand-logo-wrap"><img src="assets/logo/logo-horizontal-green.png" alt="Nexify AI" class="brand-logo logo-light" onerror="this.style.display='none'"><img src="assets/logo/logo-horizontal-light.png" alt="Nexify AI" class="brand-logo logo-dark" onerror="this.style.display='none'"></span>
        </a>
        <p data-i18n="footerTagline">24/7 AI customer service for European SMEs.</p>
      </div>
            <div class="footer-col">
        <h5 data-i18n="footerProduct">Product</h5>
        <ul>
          <li><a href="https://agent.nexifyai.org/onboarding?from=footer" data-i18n="footerStartTrial">&#9889; Get Started Free</a></li>
          <li><a href="https://agent.nexifyai.org/admin" data-i18n="footerSignIn">Sign in</a></li>
          <li><a href="/solutions-restaurants" data-i18n="footerSolutions">Industry Solutions</a></li>
          <li><a href="/demo" data-i18n="footerDemo">See It in Action</a></li>
          <li><a href="/demo-phone" data-i18n="footerPhoneDemo">Phone Demo</a></li>
          <li><a href="/pricing-subscription" data-i18n="footerPricing">Pricing</a></li>
          <li><a href="/pilot-results" data-i18n="footerResults">Results</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h5 data-i18n="footerCompany">Company</h5>
        <ul>
          <li><a href="/about" data-i18n="footerAbout">About Us</a></li>
          <li><a href="/contact" data-i18n="footerContact">Contact</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h5 data-i18n="footerLegal">Legal</h5>
        <ul>
          <li><a href="/privacy" data-i18n="footerPrivacy">Privacy Policy</a></li>
          <li><a href="/terms" data-i18n="footerTerms">Terms of Service</a></li>
        </ul>
      </div>
    </div>
  </div>
  <div class="footer-bottom">
    <div class="container footer-bottom-inner">
      <p>&copy; 2026 Nexify AI &middot; The Hague, Netherlands &middot; <a href="mailto:hello@nexifyai.org">hello@nexifyai.org</a></p>
    </div>
  </div>
</footer>"""

NAV_CSS = """<style>.nav a.nav-cta{display:inline-flex;align-items:center;padding:.42rem 1.05rem;border-radius:999px;background:var(--color-primary,#2daa58);color:var(--color-bg,#fff);font-weight:600}.nav a.nav-cta:hover{color:var(--color-bg,#fff);opacity:.92}.nav a.nav-signin:hover{color:var(--color-primary)}@media(max-width:980px){.nav a.nav-cta{align-self:flex-start;margin:.35rem 0}}</style>"""

FINAL_CTA = """<section class="nex-final-cta">
  <style>.nex-final-cta{padding:4rem 1.5rem;background:var(--color-bg-alt,rgba(45,170,88,.06));border-top:1px solid rgba(127,127,127,.14)}.nex-final-cta .nfc-inner{max-width:720px;margin:0 auto;text-align:center}.nex-final-cta h2{font-size:1.6rem;line-height:1.25;margin:0 0 1rem}.nex-final-cta .nfc-btn{display:inline-flex;align-items:center;gap:.4rem;padding:.85rem 1.9rem;border-radius:999px;background:var(--color-primary,#2daa58);color:#fff;font-weight:600;text-decoration:none}.nex-final-cta .nfc-btn:hover{opacity:.92}.nex-final-cta .nfc-trust{margin:1rem 0 .35rem;font-size:.92rem;color:var(--color-text-muted,#5b6b66)}.nex-final-cta .nfc-sub{margin:.15rem 0 0;font-size:.82rem;color:var(--color-text-muted,#5b6b66)}</style>
  <div class="nfc-inner">
    <h2 data-i18n="nexCtaTitle">Ready to launch your own assistant?</h2>
    <a class="nfc-btn" href="https://agent.nexifyai.org/onboarding?from=cta" data-i18n="nexCtaBtn">&#9889; Get Started Free</a>
    <p class="nfc-trust"><span data-i18n="nexCtaT1">&#10003; 100% Self-Serve</span> &middot; <span data-i18n="nexCtaT2">&#10003; Zero Backend Integration</span> &middot; <span data-i18n="nexCtaT3">&#10003; Full Control &mdash; Live in Minutes</span></p>
    <p class="nfc-sub" data-i18n="nexCtaReady">Ready in 3 minutes &middot; 14-day free trial &middot; No credit card</p>
  </div>
</section>

"""

# copy keys: key -> {en, nl, fr}
KEYS = {
    "navStartTrial": {"en": "&#9889; Get Started Free", "nl": "&#9889; Gratis Beginnen", "fr": "&#9889; Commencer Gratuitement"},
    "footerStartTrial": {"en": "&#9889; Get Started Free", "nl": "&#9889; Gratis Beginnen", "fr": "&#9889; Commencer Gratuitement"},
    "navSignIn": {"en": "Sign in", "nl": "Inloggen", "fr": "Se connecter"},
    "footerSignIn": {"en": "Sign in", "nl": "Inloggen", "fr": "Se connecter"},
    "navResults": {"en": "Results", "nl": "Resultaten", "fr": "R&eacute;sultats"},
    "footerResults": {"en": "Results", "nl": "Resultaten", "fr": "R&eacute;sultats"},
    "nexCtaTitle": {"en": "Ready to launch your own assistant?", "nl": "Klaar om uw eigen assistent te lanceren?", "fr": "Pr&ecirc;t &agrave; lancer votre propre assistant ?"},
    "nexCtaBtn": {"en": "&#9889; Get Started Free", "nl": "&#9889; Gratis Beginnen", "fr": "&#9889; Commencer Gratuitement"},
    "nexCtaT1": {"en": "&#10003; 100% Self-Serve", "nl": "&#10003; 100% zelfstandig", "fr": "&#10003; 100 % en libre-service"},
    "nexCtaT2": {"en": "&#10003; Zero Backend Integration", "nl": "&#10003; Geen backend-integratie", "fr": "&#10003; Z&eacute;ro int&eacute;gration backend"},
    "nexCtaT3": {"en": "&#10003; Full Control &mdash; Live in Minutes", "nl": "&#10003; Volledige controle &mdash; live binnen enkele minuten", "fr": "&#10003; Contr&ocirc;le total &mdash; en ligne en quelques minutes"},
    "nexCtaReady": {"en": "Ready in 3 minutes &middot; 14-day free trial &middot; No credit card", "nl": "Klaar in 3 minuten &middot; 14 dagen gratis proberen &middot; Geen creditcard", "fr": "Pr&ecirc;t en 3 minutes &middot; essai gratuit de 14 jours &middot; sans carte bancaire"},
}
# NOTE: JS copy values are set via textContent — entities would render literally.
# Use plain unicode in JS strings instead:
for k, langs in KEYS.items():
    for l, v in langs.items():
        v = (v.replace("&#9889;", "⚡").replace("&#10003;", "✓")
              .replace("&mdash;", "—").replace("&middot;", "·")
              .replace("&eacute;", "é").replace("&ecirc;", "ê")
              .replace("&agrave;", "à").replace("&ocirc;", "ô"))
        KEYS[k][l] = v

RELABELED = {"en": "⚡ Start Free", "nl": "⚡ Gratis Beginnen", "fr": "⚡ Commencer Gratuitement"}

NAV_RE = re.compile(r'<nav class="nav" id="site-nav">[\s\S]*?</nav>')
FOOTER_RE = re.compile(r'<footer class="site-footer">[\s\S]*?</footer>')


def lang_sections(html):
    """Return {lang: (start, end)} char ranges of the copy object's language blocks."""
    cs = html.find("const copy = {")
    if cs < 0:
        return None, {}
    ranges = {}
    pos = cs
    order = ["en", "nl", "fr"]
    for i, lang in enumerate(order):
        m = re.compile(r'["\']?' + lang + r'["\']?\s*:\s*\{').search(html, pos)
        if not m:
            continue
        start = m.end()  # just after '{'
        nxt = None
        if i + 1 < len(order):
            m2 = re.compile(r'["\']?' + order[i + 1] + r'["\']?\s*:\s*\{').search(html, m.end())
            nxt = m2.start() if m2 else None
        if nxt is None:
            m3 = re.compile(r'\n\s*\};').search(html, m.end())
            nxt = m3.start() if m3 else len(html)
        ranges[lang] = (start, nxt)
        pos = m.end()
    return cs, ranges


def set_key(html, key, values):
    """Insert or update key in each language section of the copy object."""
    cs, ranges = lang_sections(html)
    if not ranges:
        return html
    for lang in ["en", "nl", "fr"]:
        rng = ranges.get(lang)
        if not rng:
            continue
        start, end = rng
        section = html[start:end]
        pat = re.compile(r'(["\']?)' + re.escape(key) + r'\1\s*:\s*([\'"]).*?\2,?')
        if pat.search(section):
            new_section = pat.sub(lambda m: f"{key}:'{values[lang]}',", section, count=1)
            html = html[:start] + new_section + html[end:]
            _, ranges = lang_sections(html)
        else:
            # insert right after the language opener (start is just after '{')
            line_end = html.find("\n", start)
            insert_at = line_end + 1 if line_end != -1 and line_end < end else start
            html = html[:insert_at] + f"    {key}:'{values[lang]}',\n" + html[insert_at:]
            _, ranges = lang_sections(html)
    return html


def migrate(path):
    html = io.open(path, encoding="utf-8").read()
    orig = html
    notes = []

    # 1-2. canonical nav + footer
    n = len(NAV_RE.findall(html))
    f = len(FOOTER_RE.findall(html))
    if n != 1 or f != 1:
        return path, f"SKIP (nav x{n}, footer x{f})"
    html = NAV_RE.sub(lambda m: NAV, html, count=1)
    html = FOOTER_RE.sub(lambda m: FOOTER, html, count=1)

    # 3. nav-cta css
    if "nav a.nav-cta" not in html:
        html = html.replace("</head>", NAV_CSS + "\n</head>", 1)

    # 5. body pilot-apply re-points (nav/footer already canonical, so any
    # remaining /pilot-apply anchors are body CTAs)
    tag = FROM_TAG.get(path, "page")
    pat = re.compile(r'<a\s+href="/pilot-apply"([^>]*)>([^<]*)</a>')
    keys_hit = []

    def rep(m):
        attrs = m.group(1)
        km = re.search(r'data-i18n="([\w.-]+)"', attrs)
        if km:
            keys_hit.append(km.group(1))
        return f'<a href="{ONB}?from={tag}"{attrs}>&#9889; Start Free</a>'

    html = pat.sub(rep, html)
    for k in set(keys_hit):
        html = set_key(html, k, RELABELED)
        notes.append(f"relabel {k}")

    # 6. FinalCtaBlock
    if path in FINAL_CTA_PAGES and "nex-final-cta" not in html:
        html = html.replace('<footer class="site-footer">', FINAL_CTA + '<footer class="site-footer">', 1)

    # 7. index hero + login register param
    if path == "index.html":
        html = html.replace('href="https://agent.nexifyai.org/onboarding" id="btn-start-trial"',
                            'href="' + ONB + '?from=hero" id="btn-start-trial"')
    if path == "login.html":
        html = html.replace('href="https://agent.nexifyai.org/onboarding"',
                            'href="' + ONB + '?from=login"')

    # 4. chrome keys (FinalCta keys harmless everywhere; scoped to need)
    need = {k: KEYS[k] for k in
            ["navStartTrial", "footerStartTrial", "navSignIn", "footerSignIn", "navResults", "footerResults"]}
    if path in FINAL_CTA_PAGES:
        need.update({k: KEYS[k] for k in
                     ["nexCtaTitle", "nexCtaBtn", "nexCtaT1", "nexCtaT2", "nexCtaT3", "nexCtaReady"]})
    for k, v in need.items():
        html = set_key(html, k, v)

    if html != orig:
        io.open(path, "w", encoding="utf-8", newline="").write(html)
    return path, f"OK nav+footer, relabeled={sorted(set(keys_hit))}, ctaBlock={path in FINAL_CTA_PAGES}"


def migrate_404():
    path = "404.html"
    html = io.open(path, encoding="utf-8").read()
    orig = html
    if "nav-cta" not in html:
        html = html.replace("</nav>",
            '  <a href="https://agent.nexifyai.org/admin" class="nav-signin" data-i18n="navSignIn">Sign in</a>\n'
            '      <a href="https://agent.nexifyai.org/onboarding?from=nav" class="nav-cta" data-i18n="navStartTrial">&#9889; Get Started Free</a>\n    </nav>', 1)
        html = html.replace("</head>", NAV_CSS + "\n</head>", 1)
    for k in ["navStartTrial", "navSignIn"]:
        html = set_key(html, k, KEYS[k])
    if html != orig:
        io.open(path, "w", encoding="utf-8", newline="").write(html)
    return path, "OK 404 nav cta"


def main():
    for p in SHARED:
        print(*migrate(p))
    print(*migrate_404())

    # sitemap: drop pilot-apply
    sm = io.open("sitemap.xml", encoding="utf-8").read()
    sm2 = re.sub(r'\s*<url>\s*<loc>[^<]*pilot-apply</loc>[\s\S]*?</url>', '', sm)
    if sm2 != sm:
        io.open("sitemap.xml", "w", encoding="utf-8", newline="").write(sm2)
        print("sitemap.xml: pilot-apply removed")

    # _redirects
    io.open("_redirects", "w", encoding="utf-8", newline="").write(
        "/pilot-apply " + ONB + "?from=pilot 301\n")
    print("_redirects: /pilot-apply -> onboarding 301")

    # pilot-apply.html -> tiny fallback page
    io.open("pilot-apply.html", "w", encoding="utf-8", newline="").write(
        "<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<title>NexifyAI — Pilot program is now open self-service</title>"
        "<meta name=\"robots\" content=\"noindex\">"
        "<meta http-equiv=\"refresh\" content=\"0;url=" + ONB + "?from=pilot\">"
        "<style>body{font-family:system-ui,sans-serif;display:grid;place-items:center;"
        "min-height:100vh;margin:0;background:#f6f8f7;color:#1a2b26;text-align:center}"
        "a{color:#2daa58}</style></head><body><div>"
        "<h1>Good news — no pilot application needed anymore</h1>"
        "<p>Self-service launch is now open to everyone: build your assistant in minutes, free for 14 days.</p>"
        "<p><a href=\"" + ONB + "?from=pilot\">⚡ Get Started Free</a></p>"
        "</div></body></html>\n")
    print("pilot-apply.html: replaced with fallback redirect page")


if __name__ == "__main__":
    sys.exit(main())
