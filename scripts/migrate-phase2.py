# -*- coding: utf-8 -*-
"""
Phase 2 homepage redesign + nav slimming (plan v2, approved 2026-10-25).

index.html: hero rewrite (self-serve narrative) + trust microcopy + data bar
+ Instant Setup Preview strip + 3-Step Autonomous Setup + Old/New contrast
bar + solutions grid 4->7 (all linked) + simulation sub reframe (scripts kept)
+ pricing teaser with real prices and links + Pilot Program section DELETED
+ FAQ + FinalCtaBlock. All copy trilingual.

All 21 pages: canonical nav v2 — Solutions v · Demo · Pricing v · Results |
Sign in + CTA (See-It-In-Action dropdown and About/Contact links removed
from the top bar; they remain in the footer).
"""
import io
import re

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

NAV_V2 = """<nav class="nav" id="site-nav">
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
      <a href="/demo" data-i18n="navDemo">Demo</a>
      <div class="nav-item">
        <button class="nav-link" data-i18n="navPricing">Pricing <svg viewBox="0 0 24 24"><polyline points="6 9 12 15 18 9"/></svg></button>
        <div class="dropdown">
          <a href="/pricing-subscription" data-i18n="navPriceSub">Subscription</a>
          <a href="/pricing-payg" data-i18n="navPricePayg">Pay As You Use</a>
          <a href="/pricing-custom" data-i18n="navPriceCustom">Custom</a>
        </div>
      </div>
      <a href="/pilot-results" data-i18n="navResults">Results</a>
      <a href="https://agent.nexifyai.org/admin" class="nav-signin" data-i18n="navSignIn">Sign in</a>
      <a href="https://agent.nexifyai.org/onboarding?from=nav" class="nav-cta" data-i18n="navStartTrial">&#9889; Get Started Free</a>
    </nav>"""

PHASE2_CSS = """<style>
/* Phase 2: hero trust row, setup preview, 3-step, contrast, faq */
.hero-trust{display:flex;flex-wrap:wrap;gap:.5rem 1.4rem;justify-content:center;margin:1.1rem 0 .2rem;font-size:.9rem;color:var(--color-text-muted,#5b6b66)}
.hero-data{margin:.4rem 0 0;font-size:.82rem;color:var(--color-text-muted,#5b6b66)}
.spv-wrap{max-width:880px;margin:2.6rem auto 0}
.spv{border:1px solid rgba(127,127,127,.18);border-radius:18px;background:var(--color-surface,#fff);box-shadow:0 18px 50px rgba(10,40,25,.10);overflow:hidden}
.spv-bar{display:flex;align-items:center;gap:.5rem;padding:.6rem 1rem;border-bottom:1px solid rgba(127,127,127,.14);font-size:.75rem;color:var(--color-text-muted,#5b6b66)}
.spv-bar i{width:.65rem;height:.65rem;border-radius:50%;display:inline-block}
.spv-body{display:grid;grid-template-columns:1.4fr 1fr;gap:0}
.spv-chat{padding:1.1rem 1.2rem;display:flex;flex-direction:column;gap:.7rem}
.spv-msg{max-width:86%;padding:.6rem .9rem;border-radius:14px;font-size:.88rem;line-height:1.45}
.spv-user{align-self:flex-end;background:var(--color-primary,#2daa58);color:#fff;border-bottom-right-radius:4px}
.spv-bot{align-self:flex-start;background:rgba(127,127,127,.10);border-bottom-left-radius:4px}
.spv-draft{padding:1rem 1.1rem;border-left:1px solid rgba(127,127,127,.14);display:flex;flex-direction:column;gap:.55rem;font-size:.82rem}
.spv-draft h4{margin:0;font-size:.78rem;text-transform:uppercase;letter-spacing:.06em;color:var(--color-text-muted,#5b6b66)}
.spv-chip{display:flex;justify-content:space-between;gap:.6rem;padding:.4rem .6rem;border:1px solid rgba(127,127,127,.16);border-radius:10px}
.spv-chip b{font-weight:600}
.spv-cap{margin:.8rem 0 0;text-align:center;font-size:.8rem;color:var(--color-text-muted,#5b6b66)}
.how-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1.2rem;margin-top:2rem}
.how-card{border:1px solid rgba(127,127,127,.16);border-radius:18px;padding:1.4rem;background:var(--color-surface,#fff)}
.how-num{font-size:2rem;font-weight:700;color:var(--color-primary,#2daa58);line-height:1}
.how-card h3{margin:.6rem 0 .45rem;font-size:1.05rem}
.how-card p{margin:0;font-size:.9rem;line-height:1.55;color:var(--color-text-muted,#5b6b66)}
.cmp{display:grid;grid-template-columns:1fr 1fr;gap:1.2rem;margin-top:2rem;text-align:left}
.cmp-col{border-radius:18px;padding:1.3rem 1.4rem}
.cmp-old{background:rgba(220,60,60,.06);border:1px solid rgba(220,60,60,.22)}
.cmp-new{background:rgba(45,170,88,.08);border:1px solid rgba(45,170,88,.30)}
.cmp-col h3{margin:0 0 .7rem;font-size:1rem}
.cmp-old h3{color:#c23c3c}.cmp-new h3{color:var(--color-primary,#2daa58)}
.cmp-col ul{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:.5rem;font-size:.9rem;color:var(--color-text-muted,#5b6b66)}
.value-price{margin:.5rem 0 0;font-weight:600;font-size:.95rem}
.faq-list{max-width:760px;margin:2rem auto 0;text-align:left;display:flex;flex-direction:column;gap:.8rem}
.faq-item{border:1px solid rgba(127,127,127,.16);border-radius:14px;padding:.95rem 1.15rem}
.faq-item h3{margin:0 0 .4rem;font-size:.95rem}
.faq-item p{margin:0;font-size:.88rem;line-height:1.55;color:var(--color-text-muted,#5b6b66)}
@media(max-width:860px){.how-grid,.cmp,.spv-body{grid-template-columns:1fr}.spv-draft{border-left:none;border-top:1px solid rgba(127,127,127,.14)}}
</style>"""

HERO_EYEBROW = '<div class="eyebrow"><span class="dot"></span><span data-i18n="heroEyebrow">AI Customer Service Agent &mdash; 100% Self-Serve</span></div>'
HERO_H1 = '<h1 data-i18n="heroTitle">Your AI assistant, live in minutes &mdash; not weeks.</h1>'
HERO_COPY = '<p class="hero-copy" data-i18n="heroCopy">No backend setup. No waiting on sales or IT. Chat with our AI to build yours, confirm by email, and paste one line of code. You\'re in full control.</p>'
HERO_ACTIONS = """<div class="hero-actions">
      <a href="https://agent.nexifyai.org/onboarding?from=hero" id="btn-start-trial" class="btn btn-primary" data-i18n="heroCtaTrial">&#9889; Get Started Free</a>
      <a href="#how" id="btn-book-demo" class="btn btn-secondary" data-i18n="heroHowCta">See how it works</a>
      <a href="/pricing-subscription" class="btn btn-secondary" data-i18n="heroCtaSecondary">View Pricing</a>
    </div>
    <div class="hero-trust">
      <span data-i18n="heroTrust1">&#10003; 100% Self-Serve</span>
      <span data-i18n="heroTrust2">&#10003; Zero Backend Integration</span>
      <span data-i18n="heroTrust3">&#10003; Full Control &mdash; Live in Minutes</span>
    </div>
    <p class="hero-data" data-i18n="heroData">Ready in 3 minutes &middot; 14-day free trial &middot; No credit card</p>"""

PREVIEW_AND_HOW = """</section>

<section class="values" id="preview" style="padding-top:0;">
  <div class="container">
    <div class="spv-wrap">
      <div class="spv">
        <div class="spv-bar"><i style="background:#e2695e"></i><i style="background:#e9b949"></i><i style="background:#58bf71"></i><span data-i18n="pvBar">Build your assistant &mdash; live conversation</span></div>
        <div class="spv-body">
          <div class="spv-chat">
            <div class="spv-msg spv-user" data-i18n="pvUser">We're Bistro Zomer, a cozy bistro in Utrecht. Warm tone, please &mdash; and our color is #7C3AED.</div>
            <div class="spv-msg spv-bot" data-i18n="pvBot">Lovely! I've created your assistant: warm and welcoming, answering in your voice, in 30+ languages. Where should bookings go?</div>
          </div>
          <div class="spv-draft">
            <h4 data-i18n="pvDraft">Your draft</h4>
            <div class="spv-chip"><span data-i18n="pvName">Name</span><b>Bistro Zomer</b></div>
            <div class="spv-chip"><span data-i18n="pvTone">Tone</span><b data-i18n="pvWarm">Warm &amp; friendly</b></div>
            <div class="spv-chip"><span data-i18n="pvColor">Color</span><b>#7C3AED</b></div>
            <div class="spv-chip"><span data-i18n="pvBooking">Booking</span><b data-i18n="pvReady">&#10003; Ready</b></div>
          </div>
        </div>
      </div>
      <p class="spv-cap" data-i18n="pvCaption">A real first minute &mdash; the assistant is built while you chat. Restaurant shown as an example; yours will fit your business and your languages.</p>
    </div>
  </div>
</section>

<!-- ========== 3-Step Autonomous Setup ========== -->
<section class="values" id="how">
  <div class="container">
    <div class="sim-head" style="margin-bottom:var(--space-6);">
      <h2 data-i18n="howTitle">Launch it yourself &mdash; in three steps</h2>
      <p data-i18n="howSub">No project team, no integration sprint. The whole flow is yours, on your schedule.</p>
    </div>
    <div class="how-grid">
      <div class="how-card">
        <div class="how-num">1</div>
        <h3 data-i18n="how1T">&#128172; Chat to configure</h3>
        <p data-i18n="how1B">Tell our AI about your business &mdash; name, tone, brand color, booking method. It builds the assistant with you, in your language.</p>
      </div>
      <div class="how-card">
        <div class="how-num">2</div>
        <h3 data-i18n="how2T">&#9993;&#65039; One click to claim</h3>
        <p data-i18n="how2B">We email you a magic link. Click to confirm &mdash; your account, workspace and 14-day free trial are created instantly.</p>
      </div>
      <div class="how-card">
        <div class="how-num">3</div>
        <h3 data-i18n="how3T">&#128203; Paste one line, go live</h3>
        <p data-i18n="how3B">Copy the embed snippet into your site. Your branded assistant answers customers the same day.</p>
      </div>
    </div>
    <div class="cmp">
      <div class="cmp-col cmp-old">
        <h3 data-i18n="cmpOldT">&#10060; The old way</h3>
        <ul>
          <li data-i18n="cmpOld1">Weeks of IT tickets and API specs</li>
          <li data-i18n="cmpOld2">A backend integration project</li>
          <li data-i18n="cmpOld3">Waiting on vendor onboarding</li>
          <li data-i18n="cmpOld4">Support requests for every change</li>
        </ul>
      </div>
      <div class="cmp-col cmp-new">
        <h3 data-i18n="cmpNewT">&#9989; Your way (NexifyAI)</h3>
        <ul>
          <li data-i18n="cmpNew1">100% self-directed setup</li>
          <li data-i18n="cmpNew2">Zero backend integration</li>
          <li data-i18n="cmpNew3">Live in minutes, on your schedule</li>
          <li data-i18n="cmpNew4">Full control &mdash; you configure everything</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<!-- ========== Solutions ========== -->"""

NEW_SOL_CARDS = """      <div class="value-card" data-color="blue">
        <div class="value-icon">
          <svg viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a4 4 0 0 1 4 4v1a4 4 0 0 1-8 0V6a4 4 0 0 1 4-4z"></path><path d="M4 20a8 8 0 0 1 16 0"></path></svg>
        </div>
        <h3 class="value-title"><a href="/solutions-physiotherapy" data-i18n="solPhysioTitle" style="color:inherit;text-decoration:none;">Physiotherapy</a></h3>
        <p class="value-desc" data-i18n="solPhysioDesc">Appointment booking, intake questions and exercise FAQs &mdash; answered around the clock.</p>
      </div>
      <div class="value-card" data-color="green">
        <div class="value-icon">
          <svg viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a4 4 0 0 1 4 4v1a4 4 0 0 1-8 0V6a4 4 0 0 1 4-4z"></path><path d="M4 20a8 8 0 0 1 16 0"></path></svg>
        </div>
        <h3 class="value-title"><a href="/solutions-dentists" data-i18n="solDentistTitle" style="color:inherit;text-decoration:none;">Dentists</a></h3>
        <p class="value-desc" data-i18n="solDentistDesc">Scheduling, reminder FAQs and insurance questions handled instantly, in every patient's language.</p>
      </div>
      <div class="value-card" data-color="amber">
        <div class="value-icon">
          <svg viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3 3 8l9 5 9-5-9-5z"></path><path d="M3 8v8l9 5 9-5V8"></path></svg>
        </div>
        <h3 class="value-title"><a href="/solutions-beauty-salons" data-i18n="solSalonTitle" style="color:inherit;text-decoration:none;">Beauty &amp; Salons</a></h3>
        <p class="value-desc" data-i18n="solSalonDesc">Booking requests, service questions and opening-hours answers &mdash; even after closing time.</p>
      </div>
    </div>"""

FAQ_SECTION = """<!-- ========== FAQ ========== -->
<section class="values" id="faq">
  <div class="container">
    <div class="sim-head" style="margin-bottom:var(--space-6);">
      <h2 data-i18n="faqTitle">Questions, answered</h2>
    </div>
    <div class="faq-list">
      <div class="faq-item"><h3 data-i18n="faq1Q">How long does setup really take?</h3><p data-i18n="faq1A">About three minutes of chatting. The AI builds your assistant as you describe your business; the email confirmation and embed snippet take two more clicks.</p></div>
      <div class="faq-item"><h3 data-i18n="faq2Q">Do I need technical skills or a developer?</h3><p data-i18n="faq2A">No. If you can paste one line of code into your website &mdash; or forward it to whoever manages your site &mdash; you're done. There is no backend integration.</p></div>
      <div class="faq-item"><h3 data-i18n="faq3Q">What happens after the 14-day trial?</h3><p data-i18n="faq3A">You pick a plan: a fixed monthly subscription or pay-per-conversation. No credit card is required to start, and nothing is charged automatically.</p></div>
      <div class="faq-item"><h3 data-i18n="faq4Q">What about privacy and AI rules?</h3><p data-i18n="faq4A">Conversations are archived in the EU with automated PII redaction and fixed retention. The assistant always identifies itself as AI, and you confirm your own compliance responsibilities before going live.</p></div>
      <div class="faq-item"><h3 data-i18n="faq5Q">Can it really speak my customers' languages?</h3><p data-i18n="faq5A">Yes &mdash; 30+, including Dutch, French, German, Spanish and English. It detects the customer's language automatically and answers in kind.</p></div>
    </div>
  </div>
</section>

"""

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

IDX_KEYS = {
    "heroEyebrow": {"en": "AI Customer Service Agent — 100% Self-Serve", "nl": "AI-klantenserviceagent — 100% zelfstandig", "fr": "Agent de service client IA — 100 % en libre-service"},
    "heroTitle": {"en": "Your AI assistant, live in minutes — not weeks.", "nl": "Uw AI-assistent, live binnen enkele minuten — niet binnen weken.", "fr": "Votre assistant IA, en ligne en quelques minutes — pas en quelques semaines."},
    "heroCopy": {"en": "No backend setup. No waiting on sales or IT. Chat with our AI to build yours, confirm by email, and paste one line of code. You're in full control.", "nl": "Geen backend-setup. Niet wachten op sales of IT. Chat met onze AI om de uwe te bouwen, bevestig via e-mail en plak één regel code. U heeft volledige controle.", "fr": "Aucune configuration backend. Aucune attente commerciale ou informatique. Discutez avec notre IA pour construire la vôtre, confirmez par e-mail et collez une ligne de code. Vous gardez le contrôle total."},
    "heroCtaTrial": {"en": "⚡ Get Started Free", "nl": "⚡ Gratis Beginnen", "fr": "⚡ Commencer Gratuitement"},
    "heroHowCta": {"en": "See how it works", "nl": "Zie hoe het werkt", "fr": "Voir comment ça marche"},
    "heroTrust1": {"en": "✓ 100% Self-Serve", "nl": "✓ 100% zelfstandig", "fr": "✓ 100 % en libre-service"},
    "heroTrust2": {"en": "✓ Zero Backend Integration", "nl": "✓ Geen backend-integratie", "fr": "✓ Zéro intégration backend"},
    "heroTrust3": {"en": "✓ Full Control — Live in Minutes", "nl": "✓ Volledige controle — live binnen enkele minuten", "fr": "✓ Contrôle total — en ligne en quelques minutes"},
    "heroData": {"en": "Ready in 3 minutes · 14-day free trial · No credit card", "nl": "Klaar in 3 minuten · 14 dagen gratis · Geen creditcard", "fr": "Prêt en 3 minutes · essai gratuit de 14 jours · sans carte bancaire"},
    "pvBar": {"en": "Build your assistant — live conversation", "nl": "Bouw uw assistent — live gesprek", "fr": "Construisez votre assistant — conversation en direct"},
    "pvUser": {"en": "We're Bistro Zomer, a cozy bistro in Utrecht. Warm tone, please — and our color is #7C3AED.", "nl": "Wij zijn Bistro Zomer, een gezellige bistro in Utrecht. Graag een warme toon — en onze kleur is #7C3AED.", "fr": "Nous sommes Bistro Zomer, un bistro cosy à Utrecht. Un ton chaleureux, s'il vous plaît — et notre couleur est #7C3AED."},
    "pvBot": {"en": "Lovely! I've created your assistant: warm and welcoming, answering in your voice, in 30+ languages. Where should bookings go?", "nl": "Prachtig! Ik heb uw assistent gemaakt: warm en verwelkomend, in uw stem, in 30+ talen. Waar moeten reserveringen naartoe?", "fr": "Magnifique ! J'ai créé votre assistant : chaleureux et accueillant, dans votre voix, en 30+ langues. Où diriger les réservations ?"},
    "pvDraft": {"en": "Your draft", "nl": "Uw concept", "fr": "Votre brouillon"},
    "pvName": {"en": "Name", "nl": "Naam", "fr": "Nom"},
    "pvTone": {"en": "Tone", "nl": "Toon", "fr": "Ton"},
    "pvWarm": {"en": "Warm & friendly", "nl": "Warm & vriendelijk", "fr": "Chaleureux et amical"},
    "pvColor": {"en": "Color", "nl": "Kleur", "fr": "Couleur"},
    "pvBooking": {"en": "Booking", "nl": "Boeken", "fr": "Réservation"},
    "pvReady": {"en": "✓ Ready", "nl": "✓ Klaar", "fr": "✓ Prêt"},
    "pvCaption": {"en": "A real first minute — the assistant is built while you chat. Restaurant shown as an example; yours will fit your business and your languages.", "nl": "Een echte eerste minuut — de assistent wordt gebouwd ter u chattrouwt. Restaurant als voorbeeld; de uwe past bij uw bedrijf en uw talen.".replace("chattrouwt", "chat"), "fr": "Une vraie première minute — l'assistant se construit pendant que vous discutez. Restaurant à titre d'exemple ; le vôtre s'adaptera à votre activité et à vos langues."},
    "howTitle": {"en": "Launch it yourself — in three steps", "nl": "Lanceer het zelf — in drie stappen", "fr": "Lancez-le vous-même — en trois étapes"},
    "howSub": {"en": "No project team, no integration sprint. The whole flow is yours, on your schedule.", "nl": "Geen projectteam, geen integratiesprint. Het hele proces is van u, op uw schema.", "fr": "Pas d'équipe projet, pas de sprint d'intégration. Tout le parcours est à vous, à votre rythme."},
    "how1T": {"en": "💬 Chat to configure", "nl": "💬 Chatten om te configureren", "fr": "💬 Discutez pour configurer"},
    "how1B": {"en": "Tell our AI about your business — name, tone, brand color, booking method. It builds the assistant with you, in your language.", "nl": "Vertel onze AI over uw bedrijf — naam, toon, merkkleur, boekingswijze. Hij bouwt de assistent met u mee, in uw taal.", "fr": "Parlez de votre activité à notre IA — nom, ton, couleur de marque, mode de réservation. Elle construit l'assistant avec vous, dans votre langue."},
    "how2T": {"en": "✉️ One click to claim", "nl": "✉️ Eén klik om te claimen", "fr": "✉️ Un clic pour valider"},
    "how2B": {"en": "We email you a magic link. Click to confirm — your account, workspace and 14-day free trial are created instantly.", "nl": "Wij e-mailen u een magic link. Klik om te bevestigen — uw account, werkruimte en 14 dagen gratis proef worden direct aangemaakt.", "fr": "Nous vous envoyons un lien magique. Un clic pour confirmer — votre compte, votre espace et votre essai gratuit de 14 jours sont créés instantanément."},
    "how3T": {"en": "📋 Paste one line, go live", "nl": "📋 Plak één regel, ga live", "fr": "📋 Collez une ligne, en ligne"},
    "how3B": {"en": "Copy the embed snippet into your site. Your branded assistant answers customers the same day.", "nl": "Kopieer de embed-code naar uw site. Uw assistent met eigen merk beantwoordt klanten dezelfde dag nog.", "fr": "Copiez l'extrait d'intégration dans votre site. Votre assistant à votre marque répond à vos clients dès le jour même."},
    "cmpOldT": {"en": "❌ The old way", "nl": "❌ De oude weg", "fr": "❌ L'ancienne méthode"},
    "cmpOld1": {"en": "Weeks of IT tickets and API specs", "nl": "Weken aan IT-tickets en API-specificaties", "fr": "Des semaines de tickets IT et de spécifications d'API"},
    "cmpOld2": {"en": "A backend integration project", "nl": "Een backend-integratieproject", "fr": "Un projet d'intégration backend"},
    "cmpOld3": {"en": "Waiting on vendor onboarding", "nl": "Wachten op de leverancier", "fr": "Attendre l'intégration du fournisseur"},
    "cmpOld4": {"en": "Support requests for every change", "nl": "Supportverzoek bij elke wijziging", "fr": "Une demande d'assistance à chaque changement"},
    "cmpNewT": {"en": "✅ Your way (NexifyAI)", "nl": "✅ Uw weg (NexifyAI)", "fr": "✅ Votre méthode (NexifyAI)"},
    "cmpNew1": {"en": "100% self-directed setup", "nl": "100% zelfstandige setup", "fr": "Configuration 100 % autonome"},
    "cmpNew2": {"en": "Zero backend integration", "nl": "Nul backend-integratie", "fr": "Zéro intégration backend"},
    "cmpNew3": {"en": "Live in minutes, on your schedule", "nl": "Live binnen enkele minuten, op uw schema", "fr": "En ligne en quelques minutes, à votre rythme"},
    "cmpNew4": {"en": "Full control — you configure everything", "nl": "Volledige controle — u configureert alles", "fr": "Contrôle total — vous configurez tout"},
    "solPhysioTitle": {"en": "Physiotherapy", "nl": "Fysiotherapie", "fr": "Physiothérapie"},
    "solPhysioDesc": {"en": "Appointment booking, intake questions and exercise FAQs — answered around the clock.", "nl": "Afspraken, intakevragen en oefen-FAQ — dag en nacht beantwoord.", "fr": "Prise de rendez-vous, questions d'admission et FAQ exercices — répondues jour et nuit."},
    "solDentistTitle": {"en": "Dentists", "nl": "Tandartsen", "fr": "Dentistes"},
    "solDentistDesc": {"en": "Scheduling, reminder FAQs and insurance questions handled instantly, in every patient's language.", "nl": "Planning, herinneringen en verzekervragen direct afgehandeld, in de taal van elke patiënt.", "fr": "Planification, rappels et questions d'assurance traités instantanément, dans la langue de chaque patient."},
    "solSalonTitle": {"en": "Beauty & Salons", "nl": "Schoonheid & Salons", "fr": "Beauté & Salons"},
    "solSalonDesc": {"en": "Booking requests, service questions and opening-hours answers — even after closing time.", "nl": "Boekingsverzoeken, servicevragen en openingstijden — ook na sluitingstijd.", "fr": "Demandes de réservation, questions de services et horaires — même après la fermeture."},
    "simSub": {"en": "Built by a business owner in minutes — no developers. Shown here for a restaurant; yours will speak your voice and your customers' languages.", "nl": "Gebouwd door een ondernemer in enkele minuten — geen developers. Hier getoond voor een restaurant; de uwe spreekt uw stem en de talen van uw klanten.", "fr": "Construit par un entrepreneur en quelques minutes — sans développeurs. Ici pour un restaurant ; le vôtre parlera votre voix et les langues de vos clients."},
    "modelTitle": {"en": "Simple pricing", "nl": "Eenvoudige prijzen", "fr": "Une tarification simple"},
    "modelSub": {"en": "Start free for 14 days, then pick the model that fits your business.", "nl": "Begin 14 dagen gratis en kies daarna het model dat bij u past.", "fr": "Commencez gratuitement pendant 14 jours, puis choisissez le modèle qui vous convient."},
    "mPrice1": {"en": "From €199 / month", "nl": "Vanaf € 199 / maand", "fr": "À partir de 199 € / mois"},
    "mPrice2": {"en": "€0.45 per conversation", "nl": "€ 0,45 per gesprek", "fr": "0,45 € par conversation"},
    "mPrice3": {"en": "Tailored quote", "nl": "Maatwerk-offerte", "fr": "Devis sur mesure"},
    "mLink1": {"en": "See subscription plans →", "nl": "Bekijk abonnementen →", "fr": "Voir les abonnements →"},
    "mLink2": {"en": "See pay-as-you-use →", "nl": "Bekijk betalen-per-gebruik →", "fr": "Voir le paiement à l'usage →"},
    "mLink3": {"en": "Request a quote →", "nl": "Vraag een offerte aan →", "fr": "Demander un devis →"},
    "faqTitle": {"en": "Questions, answered", "nl": "Vragen, beantwoord", "fr": "Questions, réponses"},
    "faq1Q": {"en": "How long does setup really take?", "nl": "Hoe lang duurt de setup echt?", "fr": "Combien de temps prend vraiment l'installation ?"},
    "faq1A": {"en": "About three minutes of chatting. The AI builds your assistant as you describe your business; the email confirmation and embed snippet take two more clicks.", "nl": "Ongeveer drie minuten chatten. De AI bouwt uw assistent terwijl u uw bedrijf beschrijft; de e-mailbevestiging en embed-code kosten twee klikken meer.", "fr": "Environ trois minutes de discussion. L'IA construit votre assistant pendant que vous décrivez votre activité ; la confirmation par e-mail et le code d'intégration ne demandent que deux clics de plus."},
    "faq2Q": {"en": "Do I need technical skills or a developer?", "nl": "Heb ik technische kennis of een developer nodig?", "fr": "Faut-il des compétences techniques ou un développeur ?"},
    "faq2A": {"en": "No. If you can paste one line of code into your website — or forward it to whoever manages your site — you're done. There is no backend integration.", "nl": "Nee. Als u één regel code in uw website kunt plakken — of doorstuurt naar wie uw site beheert — bent u klaar. Er is geen backend-integratie.", "fr": "Non. Si vous savez coller une ligne de code dans votre site — ou la transmettre à celui qui le gère — c'est fini. Aucune intégration backend."},
    "faq3Q": {"en": "What happens after the 14-day trial?", "nl": "Wat gebeurt er na de 14-daagse proef?", "fr": "Que se passe-t-il après l'essai de 14 jours ?"},
    "faq3A": {"en": "You pick a plan: a fixed monthly subscription or pay-per-conversation. No credit card is required to start, and nothing is charged automatically.", "nl": "U kiest een plan: vast maandabonnement of betalen per gesprek. Geen creditcard nodig om te starten; er wordt niets automatisch afgeschreven.", "fr": "Vous choisissez une formule : abonnement mensuel fixe ou paiement à la conversation. Aucune carte bancaire pour commencer, aucun prélèvement automatique."},
    "faq4Q": {"en": "What about privacy and AI rules?", "nl": "Hoe zit het met privacy en AI-regels?", "fr": "Qu'en est-il de la confidentialité et des règles d'IA ?"},
    "faq4A": {"en": "Conversations are archived in the EU with automated PII redaction and fixed retention. The assistant always identifies itself as AI, and you confirm your own compliance responsibilities before going live.", "nl": "Gesprekken worden in de EU gearchiveerd met automatische PII-maskering en vaste bewaartermijnen. De assistente meldt zich altijd als AI, en u bevestigt uw eigen nalevingsverantwoordelijkheden vóór livegang.", "fr": "Les conversations sont archivées dans l'UE avec anonymisation automatique des données personnelles et une conservation fixe. L'assistant se présente toujours comme une IA, et vous confirmez vos propres responsabilités de conformité avant la mise en ligne."},
    "faq5Q": {"en": "Can it really speak my customers' languages?", "nl": "Spreekt hij echt de talen van mijn klanten?", "fr": "Parle-t-il vraiment les langues de mes clients ?"},
    "faq5A": {"en": "Yes — 30+, including Dutch, French, German, Spanish and English. It detects the customer's language automatically and answers in kind.", "nl": "Ja — 30+, waaronder Nederlands, Frans, Duits, Spaans en Engels. Hij herkent de taal van de klant automatisch en antwoordt in die taal.", "fr": "Oui — plus de 30, dont le néerlandais, le français, l'allemand, l'espagnol et l'anglais. Il détecte la langue du client et répond dans cette langue."},
    "nexCtaTitle": {"en": "Ready to launch your own assistant?", "nl": "Klaar om uw eigen assistent te lanceren?", "fr": "Prêt à lancer votre propre assistant ?"},
    "nexCtaBtn": {"en": "⚡ Get Started Free", "nl": "⚡ Gratis Beginnen", "fr": "⚡ Commencer Gratuitement"},
    "nexCtaT1": {"en": "✓ 100% Self-Serve", "nl": "✓ 100% zelfstandig", "fr": "✓ 100 % en libre-service"},
    "nexCtaT2": {"en": "✓ Zero Backend Integration", "nl": "✓ Geen backend-integratie", "fr": "✓ Zéro intégration backend"},
    "nexCtaT3": {"en": "✓ Full Control — Live in Minutes", "nl": "✓ Volledige controle — live binnen enkele minuten", "fr": "✓ Contrôle total — en ligne en quelques minutes"},
    "nexCtaReady": {"en": "Ready in 3 minutes · 14-day free trial · No credit card", "nl": "Klaar in 3 minuten · 14 dagen gratis · Geen creditcard", "fr": "Prêt en 3 minutes · essai gratuit de 14 jours · sans carte bancaire"},
}

NAV_KEYS = {
    "navDemo": {"en": "Demo", "nl": "Demo", "fr": "Démo"},
}


def lang_sections(html):
    cs = html.find("const copy = {")
    if cs < 0:
        return {}
    ranges = {}
    pos = cs
    order = ["en", "nl", "fr"]
    for i, lang in enumerate(order):
        m = re.compile(r'["\']?' + lang + r'["\']?\s*:\s*\{').search(html, pos)
        if not m:
            continue
        start = m.end()
        nxt = None
        if i + 1 < len(order):
            m2 = re.compile(r'["\']?' + order[i + 1] + r'["\']?\s*:\s*\{').search(html, m.end())
            nxt = m2.start() if m2 else None
        if nxt is None:
            m3 = re.compile(r'\n\s*\};').search(html, m.end())
            nxt = m3.start() if m3 else len(html)
        ranges[lang] = (start, nxt)
        pos = m.end()
    return ranges


def jval(s):
    """JS string literal body with embedded single quotes escaped."""
    return s.replace("'", "\\'")


def set_key(html, key, values):
    ranges = lang_sections(html)
    for lang in ["en", "nl", "fr"]:
        rng = ranges.get(lang)
        if not rng:
            continue
        start, end = rng
        section = html[start:end]
        pat = re.compile(r'(["\']?)' + re.escape(key) + r'\1\s*:\s*([\'"]).*?\2,?')
        if pat.search(section):
            html = html[:start] + pat.sub(lambda m: f"{key}:'{jval(values[lang])}',", section, count=1) + html[end:]
        else:
            line_end = html.find("\n", start)
            insert_at = line_end + 1 if line_end != -1 and line_end < end else start
            html = html[:insert_at] + f"    {key}:'{jval(values[lang])}',\n" + html[insert_at:]
        ranges = lang_sections(html)
    return html


NAV_RE = re.compile(r'<nav class="nav" id="site-nav">[\s\S]*?</nav>')


def slim_nav(path):
    html = io.open(path, encoding="utf-8").read()
    if len(NAV_RE.findall(html)) != 1:
        return f"{path}: SKIP (nav match != 1)"
    html = NAV_RE.sub(lambda m: NAV_V2, html, count=1)
    for k, v in NAV_KEYS.items():
        html = set_key(html, k, v)
    io.open(path, "w", encoding="utf-8", newline="").write(html)
    return f"{path}: nav v2"


def rebuild_index():
    p = "index.html"
    html = io.open(p, encoding="utf-8").read()

    # hero
    html = html.replace(
        '<div class="eyebrow"><span class="dot"></span><span data-i18n="heroEyebrow">AI Customer Service Agent</span></div>',
        HERO_EYEBROW)
    html = html.replace(
        '<h1 data-i18n="heroTitle">Flawless service, even when you can\'t be everywhere.</h1>',
        HERO_H1)
    html = html.replace(
        '<p class="hero-copy" data-i18n="heroCopy">Every call answered, every high-value order captured, your standards enforced 24/7. Try it once—you\'ll never go back.</p>',
        HERO_COPY)
    old_actions = """<div class="hero-actions">
      <a href="https://agent.nexifyai.org/onboarding?from=hero" id="btn-start-trial" class="btn btn-primary" data-i18n="heroCtaTrial">Get Started Free</a>
      <a href="/demo" id="btn-book-demo" class="btn btn-secondary" data-i18n="heroCtaPrimary">Book Demo</a>
      <a href="/pricing-subscription" class="btn btn-secondary" data-i18n="heroCtaSecondary">View Pricing</a>
    </div>"""
    assert old_actions in html, "hero-actions anchor missing"
    html = html.replace(old_actions, HERO_ACTIONS)

    # preview + how sections after hero (before Solutions comment)
    html, n = re.subn(r'</section>\s*\n\s*<!-- ========== Solutions ========== -->',
                      lambda m: PREVIEW_AND_HOW, html, count=1)
    assert n == 1, "hero/solutions boundary anchor missing"

    # linkify existing 4 solution card titles
    for key, href, txt in [
        ("solRestTitle", "/solutions-restaurants", "Restaurants"),
        ("solDocTitle", "/solutions-general-practice", "General Practice"),
        ("solLawTitle", "/solutions-law-firms", "Law Firms"),
        ("solRealTitle", "/solutions-real-estate", "Real Estate Agencies"),
    ]:
        html = html.replace(
            f'<h3 class="value-title" data-i18n="{key}">{txt}</h3>',
            f'<h3 class="value-title"><a href="{href}" data-i18n="{key}" style="color:inherit;text-decoration:none;">{txt}</a></h3>')

    # add 3 new solution cards
    real_close = """<p class="value-desc" data-i18n="solRealDesc">Viewing requests, listing questions and lead qualification, day and night.</p>
      </div>
    </div>"""
    assert real_close in html, "solutions grid close anchor missing"
    html = html.replace(real_close, """<p class="value-desc" data-i18n="solRealDesc">Viewing requests, listing questions and lead qualification, day and night.</p>
      </div>
""" + NEW_SOL_CARDS)

    # simulation sub (baked)
    html = html.replace(
        'A multilingual restaurant booking—handled across chat, phone and email, around the clock, in the customer\'s own language.',
        'Built by a business owner in minutes — no developers. Shown here for a restaurant; yours will speak your voice and your customers\' languages.')

    # pricing teaser: prices + links per card
    for desc_key, extra in [
        ("modelMonthlyDesc", ('mPrice1', 'mLink1', '/pricing-subscription')),
        ("modelPayDesc", ('mPrice2', 'mLink2', '/pricing-payg')),
        ("modelCustomDesc", ('mPrice3', 'mLink3', '/pricing-custom')),
    ]:
        m = re.search(r'(<p class="value-desc" data-i18n="' + desc_key + r'">[^<]*</p>)', html)
        assert m, desc_key
        pk, lk, href = extra
        ins = (f'\n        <p class="value-price" data-i18n="{pk}"></p>'
               f'\n        <p style="margin:.35rem 0 0;font-size:.85rem"><a href="{href}" data-i18n="{lk}" style="color:inherit;font-weight:600"></a></p>')
        html = html.replace(m.group(1), m.group(1) + ins, 1)

    # delete Pilot Program section
    start = html.find("<!-- ========== Pilot Program ========== -->")
    end = html.find("</section>", start)
    assert start > 0 and end > start, "pilot section anchors missing"
    html = html[:start] + html[end + len("</section>"):]

    # FAQ + FinalCta before footer
    html = html.replace('<footer class="site-footer">', FAQ_SECTION + FINAL_CTA + '<footer class="site-footer">', 1)

    # phase-2 css
    if "spv-wrap" not in html:
        html = html.replace("</head>", PHASE2_CSS + "\n</head>", 1)

    # trilingual keys
    for k, v in IDX_KEYS.items():
        html = set_key(html, k, v)

    io.open(p, "w", encoding="utf-8", newline="").write(html)
    return "index.html: rebuilt"


def main():
    print(rebuild_index())
    for p in SHARED:
        print(slim_nav(p))


if __name__ == "__main__":
    main()
