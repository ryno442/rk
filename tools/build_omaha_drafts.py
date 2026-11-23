"""Build the Mutual of Omaha (Medicare Supplement) draft pages for floridahealthagents.com.

Usage: python3 tools/build_omaha_drafts.py
Writes drafts/fl/mutual-of-omaha.html and drafts/fl/mutual-of-omaha-medicare.html,
then checks every link in them. Nothing here publishes anything.

Rules baked in:
  * Every Mutual of Omaha quote/rate link goes to AGENT (the Mutual of Omaha agent
    page for NPN 8478911). SunFire is never used on these pages.
  * The standalone dental application URL never appears on these pages.
"""
import json
import os
import re
import sys

AGENT = "https://applyformedsupp.com/?npn=8478911"
PHONE, TEL = "(855) 847-7020", "tel:+18558477020"
SITE = "https://floridahealthagents.com"
BANNED = ("sunfirematrix", "thinkagent", "applyforindividualdental", "banner=dental", "dental")
# Internal pages confirmed live (HTTP 200 + in page-sitemap.xml) on 2026-11-23.
INTERNAL_OK = {
    "/", "/mutual-of-omaha/", "/mutual-of-omaha-medicare/", "/medicare-supplement-quotes/",
    "/insurance-carriers/", "/faq/medicare-supplement-frequently-asked-questions/",
    "/medicare-annual-enrollment/", "/medicare-advantage-vs-medicare-supplement/",
    "/contact-us/", "/appointment/", "/medicare-appointment/", "/aetna-medicare/",
    "/humana-medicare/", "/cigna-medicare-supplement/", "/unitedhealthcare-medicare/",
    "/florida-blue-medicare/",
}

CSS = """<style>
.iha-gp{max-width:1000px;margin:0 auto;font-size:17px;line-height:1.65;color:#1f2a37}
.iha-gp h2{font-size:28px;line-height:1.25;margin:36px 0 12px;color:#0a2a4e}
.iha-gp h3{font-size:20px;margin:24px 0 8px;color:#0a2a4e}
.iha-gp p{margin:0 0 14px}
.iha-gp ul{margin:0 0 16px 22px;padding:0}
.iha-gp li{margin:0 0 6px}
.iha-gp .iha-lead{font-size:19px}
.iha-gp .iha-box{background:#f3f7fb;border-left:4px solid #1565c0;padding:16px 20px;margin:20px 0;border-radius:4px}
.iha-gp table{width:100%;border-collapse:collapse;margin:12px 0 20px;font-size:16px}
.iha-gp th,.iha-gp td{border:1px solid #d6dee8;padding:10px 12px;text-align:left;vertical-align:top}
.iha-gp th{background:#0a2a4e;color:#fff}
.iha-gp details{border:1px solid #d6dee8;border-radius:6px;margin:0 0 10px;padding:12px 16px;background:#fff}
.iha-gp summary{font-weight:700;cursor:pointer;color:#0a2a4e}
.iha-gp details p{margin:10px 0 0}
.iha-gp .iha-zip{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:16px 0 6px}
.iha-gp .iha-zip input{padding:12px 14px;font-size:17px;border:1px solid #b8c4d2;border-radius:6px;width:180px}
.iha-gp .iha-zip .iha-err{width:100%;color:#b00020;font-size:14px;margin:0;min-height:18px}
.iha-gp .iha-cta{display:flex;flex-wrap:wrap;gap:12px;margin:28px 0;padding:24px;background:#0a2a4e;border-radius:8px}
.iha-gp .iha-cta h2{color:#fff;margin:0 0 4px;width:100%;font-size:24px}
.iha-gp .iha-cta p{color:#dbe6f3;width:100%;margin:0 0 8px}
.iha-gp .iha-btn{display:inline-block;padding:13px 22px;border-radius:6px;font-weight:700;text-decoration:none;background:#fff;color:#0a2a4e;border:0;cursor:pointer;font-size:17px}
.iha-gp .iha-btn.iha-alt{background:#f5a623;color:#1f2a37}
.iha-gp .iha-fine{font-size:13px;color:#5b6775;line-height:1.5;margin-top:24px}
@media(max-width:600px){.iha-gp{font-size:16px}.iha-gp h2{font-size:23px}.iha-gp .iha-btn,.iha-gp .iha-zip input{width:100%;text-align:center}}
</style>"""


def zip_widget(uid, heading):
    # Inline handlers only, no // comments, no backslash regex (Divi code-module safe).
    go = ("var z=document.getElementById('%(u)sZip').value.trim();"
          "if(z.length!==5||isNaN(z)){document.getElementById('%(u)sErr').textContent='Please enter a valid 5-digit ZIP code.';return false}"
          "document.getElementById('%(u)sErr').textContent='';"
          "window.open('%(a)s&zip='+z,'_blank','noopener');return false") % {"u": uid, "a": AGENT}
    return ('<div class="iha-box"><h3 style="margin-top:0">%s</h3>'
            '<div class="iha-zip"><input id="%sZip" type="text" inputmode="numeric" maxlength="5" '
            'placeholder="ZIP code" aria-label="Florida ZIP code" onkeydown="if(event.key===\'Enter\'){%s}">'
            '<button type="button" class="iha-btn iha-alt" onclick="%s">See my rates</button>'
            '<p class="iha-err" id="%sErr" role="status" aria-live="polite"></p></div>'
            '<p style="margin:0">Opens Mutual of Omaha&rsquo;s rate tool. No contact details needed. '
            'Or call <a href="%s">%s</a>, Mon-Fri 8:30am-5pm ET.</p></div>'
            % (heading, uid, go, go, uid, TEL, PHONE))


def faq_ld(items):
    return ('<script type="application/ld+json">' + json.dumps({
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                       for q, a in items]}) + "</script>")


def faq_html(items):
    return "\n".join("<details><summary>%s</summary><p>%s</p></details>" % (q, a) for q, a in items)


def cta(h, p):
    return ('<div class="iha-cta"><h2>%s</h2><p>%s</p>'
            '<a class="iha-btn iha-alt" href="%s" rel="nofollow">Get My Mutual of Omaha Quote</a>'
            '<a class="iha-btn" href="%s">Call %s</a>'
            '<a class="iha-btn" href="/appointment/">Have an Agent Call Me</a></div>' % (h, p, AGENT, TEL, PHONE))


FINE = ('<p class="iha-fine">Florida Health Agents is a licensed independent insurance agency (NPN 14924332). '
        'We are not affiliated with or endorsed by the U.S. government or the federal Medicare program. '
        'Medicare Supplement plans are standardized by law; premiums, rating method and availability vary by '
        'carrier, age, ZIP code and tobacco status. Agents are paid by carriers, not by you. '
        'Confirm plan details with Mutual of Omaha before you enroll.</p>')

CHIPS = ('<p><a href="/humana-medicare/">Humana</a> | <a href="/aetna-medicare/">Aetna</a> | '
         '<a href="/cigna-medicare-supplement/">Cigna</a> | <a href="/unitedhealthcare-medicare/">UnitedHealthcare</a> | '
         '<a href="/florida-blue-medicare/">Florida Blue</a> | <a href="/insurance-carriers/">All Florida carriers</a></p>')

# ---------------------------------------------------------------- overview
OV_FAQ = [
    ("Which Medicare Supplement plans does Mutual of Omaha sell in Florida?",
     "Mutual of Omaha sells standardized Medigap plans in Florida, including Plans A, F, G and N. Plan F is open only "
     "to people who became eligible for Medicare before January 1, 2020. Ask us for the plans offered at your ZIP code."),
    ("Does Mutual of Omaha use attained-age pricing?",
     "Yes. Mutual of Omaha prices Medicare Supplement plans by attained age, so premiums rise as you get older. "
     "Rates can also vary by ZIP code and tobacco status, and non-tobacco users usually pay less."),
    ("Can I see Mutual of Omaha rates for my ZIP code?",
     "Yes. Enter your ZIP code in the rate tool on this page and it opens Mutual of Omaha's quote for your area. "
     "You can also call (855) 847-7020 and an agent will compare it with other Florida carriers."),
    ("Do I need a doctor network or referrals?",
     "No. Medigap has no network. You can see any doctor or hospital in the U.S. that accepts Medicare."),
    ("Is there a health questionnaire?",
     "Not during your 6-month Medigap Open Enrollment Period, which starts when you are 65 and enrolled in Part B. "
     "Outside that window, Mutual of Omaha may ask health questions."),
    ("Is the quote free?",
     "Yes. Quotes are free and carry no obligation. Our agents are paid by carriers, not by you."),
]

OV_META = """<!--
DRAFT for floridahealthagents.com - not published
Replaces the body of page ID 12476 (Mutual of Omaha, carrier overview)
WP page title (H1 is in the body, keep the WP title as-is): Mutual of Omaha Medicare Supplement in Florida
Slug: /mutual-of-omaha/  (do not change)
SEO title: Mutual of Omaha Medicare Supplement Florida | 2027 Rates
Meta description: Compare Mutual of Omaha Medicare Supplement plans in Florida. Search rates by ZIP code, see how attained-age pricing works, and get a free agent quote.
Changes vs live: all quote links go to the Mutual of Omaha agent page (no SunFire), no ancillary-product links or cards,
one consistent plan list (A, F, G, N - CONFIRM with the carrier), "Rates Held for Life" claim removed (Medigap premiums
are not locked), unverifiable "usually the lowest rates" wording softened, sidebar trimmed to Medicare-only, FAQ + FAQPage schema added.
-->"""


def build_overview():
    return "\n".join([
        OV_META, CSS, '<div class="iha-gp">',
        '<h1>Mutual of Omaha Medicare Supplement in Florida</h1>',
        '<p class="iha-lead">Mutual of Omaha has sold Medicare Supplement (Medigap) insurance since 1909 and is still '
        'policyholder-owned. Search rates for your ZIP code below, or have a licensed Florida agent compare it with '
        'the other carriers for you.</p>',
        zip_widget("mooOv", "Search Mutual of Omaha rates by ZIP code"),
        '<h2>Mutual of Omaha plans in Florida</h2>',
        '<p>Medicare Supplement plans are standardized by law, so a Plan G from Mutual of Omaha covers the same benefits '
        'as a Plan G from any other carrier. What differs is price, rate history and service.</p>',
        '<table><tr><th>Plan</th><th>What it covers</th><th>Who it fits</th></tr>'
        '<tr><td>Plan A</td><td>Core benefits only</td><td>Lowest-cost entry point</td></tr>'
        '<tr><td>Plan F</td><td>Everything, including the Part B deductible</td><td>Only if you became eligible for Medicare before January 1, 2020</td></tr>'
        '<tr><td>Plan G</td><td>Everything except the Part B deductible</td><td>The most popular choice for people new to Medicare</td></tr>'
        '<tr><td>Plan N</td><td>Like Plan G, with small copays on some visits</td><td>Lower premium in exchange for copays</td></tr></table>',
        '<p>Plan availability can change. We confirm what Mutual of Omaha offers at your ZIP code before you apply.</p>',
        '<h2>How Mutual of Omaha prices Medigap</h2>',
        '<ul><li><strong>Attained-age pricing.</strong> Your premium is based on your current age and rises as you get older.</li>'
        '<li><strong>Tobacco status.</strong> Non-tobacco rates are usually lower.</li>'
        '<li><strong>Location.</strong> Premiums can vary by ZIP code and county.</li>'
        '<li><strong>Guaranteed renewable.</strong> Mutual of Omaha cannot cancel your policy because of your health or claims.</li></ul>',
        '<h2>Why Floridians choose Mutual of Omaha</h2>',
        '<ul><li>See any doctor or hospital that accepts Medicare, with no network or referrals</li>'
        '<li>Coverage works across the U.S., useful for snowbirds and travelers</li>'
        '<li>Plans F, G and N include foreign travel emergency benefits</li>'
        '<li>No claim forms needed in most cases</li>'
        '<li>Guaranteed acceptance during your 6-month Medigap Open Enrollment Period</li></ul>',
        '<h2>Compare other Florida Medicare Supplement carriers</h2>',
        '<p>Every Plan G is the same coverage by law, so the real comparison is price and how the carrier treats you later. '
        'We will put Mutual of Omaha next to the others.</p>', CHIPS,
        '<p>New to Medicare? See our <a href="/medicare-supplement-quotes/">Medicare Supplement quotes</a>, the '
        '<a href="/medicare-advantage-vs-medicare-supplement/">Medicare Advantage vs Medigap guide</a> and the '
        '<a href="/faq/medicare-supplement-frequently-asked-questions/">Medicare FAQ</a>. Details on enrolling are on our '
        '<a href="/mutual-of-omaha-medicare/">Mutual of Omaha Medicare enrollment page</a>.</p>',
        cta("Get your Mutual of Omaha quote", "Free, no obligation. A licensed Florida agent will compare it with other carriers."),
        '<h2>Frequently asked questions</h2>', faq_html(OV_FAQ), FINE, '</div>', faq_ld(OV_FAQ)])


# ---------------------------------------------------------------- medicare
MD_FAQ = [
    ("When can I enroll in Mutual of Omaha Medicare Supplement?",
     "Your best window is the 6-month Medigap Open Enrollment Period that starts the month you are 65 or older and enrolled "
     "in Part B. During it you cannot be turned down or charged more for health reasons. After it, Mutual of Omaha may ask health questions."),
    ("Is Mutual of Omaha a Medicare Advantage plan?",
     "No. The plans on this page are Medicare Supplement (Medigap) plans. They work alongside Original Medicare. "
     "You cannot use a Medigap plan together with a Medicare Advantage plan."),
    ("Do I still need Part A and Part B?",
     "Yes. You must be enrolled in both Medicare Part A and Part B to buy a Medicare Supplement plan, and you keep paying your Part B premium."),
    ("Can I switch to Mutual of Omaha later?",
     "Yes, but outside your open enrollment window you may have to answer health questions, and Florida does not guarantee "
     "acceptance for most people. Some situations carry guaranteed-issue rights. An agent can check yours."),
    ("How do I get a Mutual of Omaha quote?",
     "Use the ZIP code search on this page, or call (855) 847-7020. Quotes are free and carry no obligation."),
]

MD_META = """<!--
DRAFT for floridahealthagents.com - not published
Replaces the body of page ID 12741 (Mutual of Omaha Medicare, enrollment page)
WP page title: Mutual of Omaha Medicare Enrollment in Florida
Slug: /mutual-of-omaha-medicare/  (do not change)
SEO title: Mutual of Omaha Medicare in Florida | How to Enroll
Meta description: How to enroll in Mutual of Omaha Medicare Supplement in Florida: when you can enroll, what you need, and how to search rates by ZIP code with a licensed agent.
Changes vs live: separate ancillary-product application URL and its cards removed, every quote link goes to the
Mutual of Omaha agent page (no SunFire), ZIP rate search added, "24/7 Nurse Support Line" claim removed (unverified),
plan list made consistent (A, F, G, N - CONFIRM with the carrier), page repositioned around enrollment so it no longer
duplicates /mutual-of-omaha/ (which targets plans and rates), AEP dates left as the live page had them, FAQ + FAQPage schema added.
-->"""


def build_medicare():
    return "\n".join([
        MD_META, CSS, '<div class="iha-gp">',
        '<h1>Mutual of Omaha Medicare Enrollment in Florida</h1>',
        '<p class="iha-lead">Mutual of Omaha is one of the best-known Medicare Supplement (Medigap) carriers in the country. '
        'Here is when you can enroll in Florida and what to have ready. Prefer to see plans and pricing first? Start with our '
        '<a href="/mutual-of-omaha/">Mutual of Omaha plans and rates page</a>.</p>',
        zip_widget("mooMd", "See Mutual of Omaha Medicare rates in your ZIP code"),
        '<h2>What Mutual of Omaha Medicare offers in Florida</h2>',
        '<p>Mutual of Omaha&rsquo;s Medicare product in Florida is Medicare Supplement insurance, offered as Plans A, F, G and N. '
        'It fills the deductibles, copays and coinsurance that Original Medicare leaves you with.</p>',
        '<ul><li>Use any doctor or hospital in the U.S. that accepts Medicare</li><li>No networks or referrals</li>'
        '<li>Guaranteed renewable for as long as you pay your premium</li><li>Coverage travels with you anywhere in the U.S.</li>'
        '<li>Plan F is closed if you became eligible for Medicare after 2019</li></ul>',
        '<h2>When can you enroll?</h2>',
        '<table><tr><th>Period</th><th>When</th><th>What it means</th></tr>'
        '<tr><td>Medigap Open Enrollment</td><td>6 months starting the month you are 65+ and enrolled in Part B</td>'
        '<td>Best time to buy: no health questions, and you cannot be charged more for your health</td></tr>'
        '<tr><td>Initial Enrollment Period</td><td>7 months around your 65th birthday</td><td>When you first sign up for Medicare Parts A and B</td></tr>'
        '<tr><td>Annual Enrollment Period</td><td>October 15 - December 7</td><td>Switch or join a Medicare Advantage or Part D plan for the next year</td></tr>'
        '<tr><td>Medicare Advantage Open Enrollment</td><td>January 1 - March 31</td><td>Switch Medicare Advantage plans once, or return to Original Medicare</td></tr>'
        '<tr><td>Special Enrollment Period</td><td>Varies</td><td>After a qualifying life event, such as losing employer coverage</td></tr></table>',
        '<p>Medigap can be bought at other times of year too, but you may need to answer health questions. '
        'See the <a href="/medicare-annual-enrollment/">Medicare annual enrollment guide</a> for the full picture.</p>',
        '<h2>What to have ready</h2>',
        '<ul><li>Your red, white and blue Medicare card (Medicare number and Part A and B start dates)</li>'
        '<li>Your date of birth and tobacco status</li><li>Your Florida ZIP code</li></ul>',
        '<h2>Medigap or Medicare Advantage?</h2>',
        '<p>You cannot have both. Medigap adds to Original Medicare and keeps your doctor choice wide open. '
        'Medicare Advantage replaces it and usually uses a network. Our '
        '<a href="/medicare-advantage-vs-medicare-supplement/">side-by-side guide</a> walks through the trade-offs.</p>',
        '<h2>Compare other Florida Medicare Supplement carriers</h2>', CHIPS,
        cta("Get your Mutual of Omaha Medicare quote", "Free, no obligation. Our licensed Florida agents will help you find the right plan."),
        '<h2>Frequently asked questions</h2>', faq_html(MD_FAQ), FINE,
        '<p><a href="/mutual-of-omaha/">&larr; Back to the Mutual of Omaha overview</a></p>', '</div>', faq_ld(MD_FAQ)])


# ---------------------------------------------------------------- verify
def verify(name, html):
    errors = []
    for h in re.findall(r'(?:href|window\.open\()=?["\']([^"\']+)["\']', html):
        if h.startswith(("tel:", "mailto:")):
            if h != TEL.replace("tel:", "") and h != TEL:
                errors.append("%s: unexpected tel/mailto %s" % (name, h))
        elif h.startswith("http"):
            if not (h == AGENT or h == AGENT + "&zip="):
                errors.append("%s: external link not the agent page: %s" % (name, h))
        elif h.startswith("/"):
            if h not in INTERNAL_OK:
                errors.append("%s: internal link not verified live: %s" % (name, h))
    low = html.lower()
    for b in BANNED:
        if b in low:
            errors.append("%s: banned string present: %s" % (name, b))
    if html.count("<h1") != 1:
        errors.append("%s: expected exactly one H1" % name)
    if "&#8211;" in html or "–" in html or "—" in html:
        errors.append("%s: non-hyphen dash present" % name)
    return errors


def main():
    pages = {"mutual-of-omaha": build_overview(), "mutual-of-omaha-medicare": build_medicare()}
    errs = []
    for slug, html in pages.items():
        errs += verify(slug, html)
        path = os.path.join(os.path.dirname(__file__), "..", "drafts", "fl", slug + ".html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html + "\n")
        print("wrote", slug, len(html), "bytes")
    if errs:
        print("\n".join(errs))
        sys.exit(1)
    print("link check passed")


if __name__ == "__main__":
    main()
