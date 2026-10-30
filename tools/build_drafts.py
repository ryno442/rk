"""Build Divi-ready draft pages for the state health agent sites.

Usage: python3 tools/build_drafts.py
Writes drafts/<site>/<slug>.html. Each file is one self-contained block to paste
into a Divi Code module (or a builder-off page). Nothing here publishes anything.

Facts researched 2026-10-30. Lines marked ANNUAL UPDATE change every year.
"""

import html
import json
import os
import re

YEAR = 2027  # coverage year being sold this fall
SUNFIRE = "https://www.sunfirematrix.com/app/consumer/ember/?sfpath=spa&sfagid=8478911"

SITES = {
    "tx": dict(
        name="Texas Health Agents", domain="texashealthagents.com", state="Texas", abbr="TX",
        phone="(972) 666-0578", tel="+19726660578",
        mphone="(972) 666-0578 ext. 2", mtel="+19726660578,2",  # comma pause auto-dials ext. 2
        contact="/contact-us/",
        exchange="HealthCare.gov", exchange_url="https://www.healthcare.gov/",
        oe="November 1, 2026 through January 15, 2027", jan1="December 15, 2026",
        stm=True,
        stm_note=("Texas allows short-term plans, but most policies sold in Texas today run only a few "
                  "months. Ask us what terms are available on your start date."),
        ship=("HICAP (Health Information, Counseling and Advocacy Program)", "1-800-252-9240"),
        regulator="Texas Department of Insurance",
    ),
    "il": dict(
        name="Illinois Health Agents", domain="ilhealthagents.com", state="Illinois", abbr="IL",
        phone="312.726.6565", tel="+13127266565",
        mphone="312.800.0751", mtel="+13128000751",
        contact="/contact-us/",
        exchange="Get Covered Illinois", exchange_url="https://getcovered.illinois.gov/",
        oe="November 1, 2026 through January 15, 2027", jan1="December 15, 2026",
        stm=False,
        stm_note=("Illinois banned the sale of new short-term health plans starting January 1, 2025, "
                  "so they are not an option here."),
        ship=("the Illinois Senior Health Insurance Program (SHIP)", "1-800-252-8966"),
        regulator="Illinois Department of Insurance",
    ),
    "fl": dict(
        name="Florida Health Agents", domain="floridahealthagents.com", state="Florida", abbr="FL",
        phone="(312) 726-6565", tel="+13127266565",
        mphone="(312) 726-6565", mtel="+13127266565",
        contact="/contact-us/",
        exchange="HealthCare.gov", exchange_url="https://www.healthcare.gov/",
        oe="November 1, 2026 through January 15, 2027", jan1="December 15, 2026",
        stm=True,
        stm_note=("Florida law allows short-term plans with initial terms under 12 months and up to "
                  "36 months in total, but each carrier sets its own limits, and many sell shorter terms."),
        ship=("SHINE (Serving Health Insurance Needs of Elders)", "1-800-963-5337"),
        regulator="Florida Office of Insurance Regulation",
    ),
    "pa": dict(
        name="Pennsylvania Health Agents", domain="pahealthagents.com", state="Pennsylvania", abbr="PA",
        phone="(855) 847-7020", tel="+18558477020",
        mphone="(855) 847-7020", mtel="+18558477020",
        contact="/contact/",  # existing PA contact page (ID 19) - keep its slug
        exchange="Pennie", exchange_url="https://pennie.com/",
        oe="November 1, 2026 through January 15, 2027", jan1="December 15, 2026",
        stm=True,
        stm_note=("Short-term plans are sold in Pennsylvania, but the policies available today are "
                  "generally limited to about three or four months in total."),
        ship=("PA MEDI (Pennsylvania Medicare Education and Decision Insight)", "1-800-783-7067"),
        regulator="Pennsylvania Insurance Department",
    ),
    "ca": dict(
        name="California Health Agents", domain="californiahealthagents.com", state="California", abbr="CA",
        phone="(855) 847-7020", tel="+18558477020",
        mphone="(855) 847-7020", mtel="+18558477020",
        contact="/contact-us/",
        exchange="Covered California", exchange_url="https://www.coveredca.com/",
        oe="November 1, 2026 through January 31, 2027", jan1="December 31, 2026",
        stm=False,
        stm_note=("California bans short-term limited duration health insurance (SB 910, "
                  "Insurance Code 10123.61), so it is not an option here."),
        ship=("HICAP", "1-800-434-0222"),
        regulator="California Department of Insurance",
    ),
    "in": dict(
        name="Indiana Health Agents", domain="indianahealthagents.com", state="Indiana", abbr="IN",
        phone="(312) 726-6565", tel="+13127266565",
        mphone="(312) 726-6565", mtel="+13127266565",
        contact="/contact-us/",
        exchange="HealthCare.gov", exchange_url="https://www.healthcare.gov/",
        oe="November 1, 2026 through January 15, 2027", jan1="December 15, 2026",
        stm=True,
        stm_note=("Indiana law allows short-term plans with initial terms up to 364 days and up to 36 months "
                  "in total, with at least $2 million in benefits, but each carrier sets its own limits and "
                  "many sell shorter terms."),
        ship=("SHIP (State Health Insurance Assistance Program)", "1-800-452-4800"),
        regulator="Indiana Department of Insurance",
    ),
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
.iha-gp .iha-warn{background:#fff8e6;border-left-color:#e69500}
.iha-gp table{width:100%;border-collapse:collapse;margin:12px 0 20px;font-size:16px}
.iha-gp th,.iha-gp td{border:1px solid #d6dee8;padding:10px 12px;text-align:left;vertical-align:top}
.iha-gp th{background:#0a2a4e;color:#fff}
.iha-gp details{border:1px solid #d6dee8;border-radius:6px;margin:0 0 10px;padding:12px 16px;background:#fff}
.iha-gp summary{font-weight:700;cursor:pointer;color:#0a2a4e}
.iha-gp details p{margin:10px 0 0}
.iha-gp .iha-cta{display:flex;flex-wrap:wrap;gap:12px;margin:28px 0;padding:24px;background:#0a2a4e;border-radius:8px}
.iha-gp .iha-cta h2{color:#fff;margin:0 0 4px;width:100%;font-size:24px}
.iha-gp .iha-cta p{color:#dbe6f3;width:100%;margin:0 0 8px}
.iha-gp .iha-btn{display:inline-block;padding:13px 22px;border-radius:6px;font-weight:700;text-decoration:none;background:#fff;color:#0a2a4e}
.iha-gp .iha-btn.iha-alt{background:#f5a623;color:#1f2a37}
.iha-gp .iha-fine{font-size:13px;color:#5b6775;line-height:1.5;margin-top:24px}
@media(max-width:600px){.iha-gp{font-size:16px}.iha-gp h2{font-size:23px}.iha-gp .iha-btn{width:100%;text-align:center}}
</style>"""


def tel(s, medicare=False):
    t, d = (s["mtel"], s["mphone"]) if medicare else (s["tel"], s["phone"])
    return f'<a href="tel:{t}">{d}</a>'


def cta(s, heading, sub, quote_url=None, quote_label="Get a Quote", medicare=False):
    t, d = (s["mtel"], s["mphone"]) if medicare else (s["tel"], s["phone"])
    q = quote_url or s["contact"]
    target = ' target="_blank" rel="noopener"' if quote_url else ""
    return f"""<div class="iha-cta">
<h2>{heading}</h2>
<p>{sub}</p>
<a class="iha-btn iha-alt" href="{q}"{target}>{quote_label}</a>
<a class="iha-btn" href="tel:{t}">Call {d}</a>
<a class="iha-btn" href="{s['contact']}">Have an Agent Call Me</a>
</div>"""


def faq_html(faqs):
    return "<h2>Frequently asked questions</h2>\n" + "\n".join(
        f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in faqs)


def strip_tags(x):
    return html.unescape(re.sub(r"<[^>]+>", "", x))


def jsonld(s, title, slug, faqs):
    base = f"https://{s['domain']}"
    data = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": base + "/"},
                {"@type": "ListItem", "position": 2, "name": title, "item": f"{base}/{slug}/"},
            ]},
            {"@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": strip_tags(q),
                 "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in faqs
            ]},
        ],
    }
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=True) + "</script>"


def agency_fine(s):
    return (f'<p class="iha-fine">{s["name"]} is a licensed independent insurance agency. We are not '
            f'affiliated with or endorsed by {s["exchange"]}, the United States government, the federal '
            f'Medicare program, or the {s["regulator"]}. Plan availability, benefits and premiums vary by '
            f'county and carrier. Information on this page is general, current as of October 2026, and '
            f'subject to change. Quotes are estimates and are not a contract or offer of insurance.</p>')


def medicare_fine(s):
    prog, num = s["ship"]
    return (f'<p class="iha-fine">We do not offer every plan available in your area. Any information we '
            f'provide is limited to those plans we do offer in your area. Please contact Medicare.gov, '
            f'1-800-MEDICARE, or your local State Health Insurance Assistance Program (in {s["state"]}, '
            f'{prog} at {num}) to get information on all of your options. {s["name"]} is not connected '
            f'with or endorsed by the U.S. government or the federal Medicare program.</p>')


SUPP_FINE = ('<p class="iha-fine">This is supplemental coverage. It does not count as minimum essential '
             'coverage under the Affordable Care Act and does not replace a major medical health plan. '
             'Benefits, definitions, waiting periods, exclusions and availability vary by carrier and state; '
             'the policy and its outline of coverage control.</p>')


# ---------------------------------------------------------------- pages

def page_open_enrollment(s):
    ca = s["abbr"] == "CA"
    title = f"{YEAR} Open Enrollment in {s['state']}: Dates, Deadlines and What Changed"
    faqs = [
        (f"When is open enrollment for {YEAR} health insurance in {s['state']}?",
         f"Open enrollment through {s['exchange']} runs {s['oe']}. Enroll by {s['jan1']} for coverage that "
         f"starts January 1, {YEAR}. Deadlines can be extended, so check {s['exchange']} or call us."),
        ("Did the extra ACA subsidies come back?",
         "Not as of October 2026. The enhanced premium tax credits expired on December 31, 2025. For "
         f"{YEAR} coverage, households above 400% of the federal poverty level do not qualify for a premium "
         "tax credit, and those below it are expected to pay a larger share of income than they did through 2025."),
        ("What happens if my income estimate is wrong?",
         "Starting with 2026 coverage, there is no cap on paying back extra advance premium tax credits at tax "
         "time. If your income goes up during the year, report it right away so your credit is adjusted."),
        ("Can I keep my current plan?",
         f"Many people are renewed automatically, but carriers change networks, drugs and prices every year. "
         f"Compare before {s['jan1']} so a renewal does not lock you into a worse fit."),
        ("Does it cost more to use an agent?",
         "No. Licensed agents are paid by the carrier, and the premium is the same whether you enroll with us, "
         f"on {s['exchange']}, or with the carrier directly."),
    ]
    hsa = ("Bronze and catastrophic plans bought through the marketplace count as HSA-qualified plans starting "
           f"in 2026. For {YEAR} the HSA limit is $4,500 for self-only coverage and $9,000 for family coverage "
           "(plus $1,000 at age 55 or older).")
    if ca:
        hsa += (" California does not follow federal HSA tax rules, so contributions are not deductible on "
                "your California return and earnings are taxed by the state each year.")
    mandate = ""
    if ca:
        mandate = ("<li><strong>California still has an individual mandate.</strong> Going without qualifying "
                   "coverage can mean a state tax penalty on Form FTB 3853.</li>")
    body = f"""
<p class="iha-lead">Open enrollment for {YEAR} health insurance in {s['state']} runs <strong>{s['oe']}</strong>. <!-- ANNUAL UPDATE -->
This year matters more than most: the extra federal subsidies are gone, many carriers filed rate increases, and
the rules for paying back subsidies got stricter. Here is what changed and how to avoid a surprise bill.</p>

<h2>Key {YEAR} dates</h2>
<table>
<tr><th>Date</th><th>What it means</th></tr>
<tr><td>November 1, 2026</td><td>Open enrollment begins on {s['exchange']} and off-exchange with carriers</td></tr>
<tr><td>{s['jan1']}</td><td>Last day to enroll for coverage starting January 1, {YEAR}</td></tr>
<tr><td>{s['oe'].split(' through ')[1]}</td><td>Open enrollment ends. Enrolling after the January 1 deadline usually means a February 1 start</td></tr>
</table>
<p>After open enrollment closes, you generally need a qualifying life event (losing other coverage, moving,
marriage, a new baby) to enroll or change plans.</p>

<h2>What changed for {YEAR}</h2>
<ul>
<li><strong>The enhanced subsidies expired.</strong> The larger premium tax credits that ran from 2021 through 2025
ended on December 31, 2025, and Congress had not restored them as of October 2026. The 400% of poverty income
limit is back, so some households who had help before will get none in {YEAR}.</li>
<li><strong>No cap on paying subsidies back.</strong> Starting with 2026 coverage, if your advance credit was too
large you repay the full difference when you file taxes. Accurate income estimates now matter a lot.</li>
<li><strong>Higher out-of-pocket limits.</strong> The most an ACA plan can make you pay in {YEAR} for in-network
covered care is $12,000 for one person and $24,000 for a family. <!-- ANNUAL UPDATE --></li>
<li><strong>Fewer lawfully present immigrants qualify for credits.</strong> Eligibility narrows starting January 1,
{YEAR}. If this may affect your household, call us before you enroll.</li>
<li><strong>More plans work with an HSA.</strong> {hsa} <!-- ANNUAL UPDATE --></li>
{mandate}
</ul>

<div class="iha-box iha-warn"><strong>Do not just let it auto-renew.</strong> If your plan's premium jumped or your
subsidy shrank, a different metal level, network or carrier may cost less. We compare every plan we offer in your
county, on and off {s['exchange']}, in one call.</div>

<h2>If you earn too much for a subsidy</h2>
<p>Above 400% of the federal poverty level you will pay full price. You still have options: an HSA-qualified
Bronze plan to lower your taxes, off-exchange plans, an employer ICHRA if you own a business, and supplemental
coverage to fill a high deductible. See our guide to <a href="/no-subsidy-health-insurance-options/">health insurance
options without a subsidy</a>.</p>

<h2>How we help</h2>
<ul>
<li>Side-by-side comparison of carriers, networks and drug lists in your county</li>
<li>Subsidy estimate and an honest read on whether your income estimate is safe</li>
<li>Enrollment on {s['exchange']} or directly with the carrier, at no cost to you</li>
<li>Help all year with claims, ID cards and mid-year changes</li>
</ul>
{cta(s, f"Get your {YEAR} quote before {s['jan1']}", "Same premium as enrolling yourself. A licensed agent reviews your options with you.")}
{faq_html(faqs)}
{agency_fine(s)}
"""
    return dict(
        slug=f"open-enrollment-{YEAR}", title=title, faqs=faqs, body=body,
        seo=f"{YEAR} Open Enrollment {s['state']}: Dates and Deadlines",
        meta=(f"{s['state']} open enrollment for {YEAR} runs {s['oe'].replace(' through ', ' - ')}. "
              f"What changed with subsidies, deadlines, and how to compare plans free."),
        parent="Top level or under Individual / Health Insurance",
        sites="all")


def page_no_subsidy(s):
    ca = s["abbr"] == "CA"
    title = f"No Subsidy in {YEAR}? Health Insurance Options in {s['state']}"
    stm_block = (f"<h3>Short-term health insurance</h3><p>{s['stm_note']} Short-term plans are medically "
                 f"underwritten, usually exclude pre-existing conditions, and are not ACA coverage, so they "
                 f"fit healthy people bridging a gap, not people managing ongoing care. "
                 f'<a href="/short-term-health-insurance/">Learn more about short-term plans</a>.</p>'
                 if s["stm"] else
                 f"<h3>What about short-term plans?</h3><p>{s['stm_note']}</p>")
    hsa_ca = (" California does not follow federal HSA tax rules, so the state tax savings do not apply on a "
              "California return." if ca else "")
    faqs = [
        (f"Who loses their subsidy in {YEAR}?",
         "Households with income above 400% of the federal poverty level no longer qualify for a premium tax "
         "credit, because the enhanced subsidies expired at the end of 2025."),
        ("Is a cheaper plan off the exchange the same coverage?",
         f"ACA plans sold off-exchange follow the same benefit rules as plans on {s['exchange']}. Without a "
         "subsidy there is no price advantage to the exchange, and some carriers offer plans only off-exchange."),
        ("Can lowering my income bring the subsidy back?",
         "Possibly. Premium tax credits use modified adjusted gross income, so pre-tax retirement and HSA "
         "contributions lower it. Talk to your tax professional before relying on this."),
        ("Is hospital indemnity a replacement for health insurance?",
         "No. It pays fixed cash benefits and works alongside a major medical plan, for example to help cover a "
         "high deductible."),
    ]
    body = f"""
<p class="iha-lead">If your household earns more than 400% of the federal poverty level, the premium tax credit you may
have had through 2025 is gone for {YEAR}. You will pay the full premium. That does not mean you have to overpay.
Here are the options we walk clients through every day in {s['state']}.</p>

<div class="iha-box">Not sure whether you are above or below the line? Call {tel(s)}. We will estimate your {YEAR}
credit in a few minutes, using the poverty guidelines the marketplace uses for {YEAR} coverage.</div>

<h2>Ways to lower your cost without a subsidy</h2>
<h3>1. Re-shop every carrier, on and off {s['exchange']}</h3>
<p>Without a subsidy, the exchange price and the carrier's direct price are the same, and some plans are sold only
off-exchange. Prices for the same metal level often differ by hundreds of dollars a month between carriers.</p>

<h3>2. Use an HSA-qualified Bronze plan</h3>
<p>Since 2026, Bronze and catastrophic plans bought through the marketplace count as HSA-qualified. For {YEAR} you can
put up to $4,500 (self-only) or $9,000 (family) into an HSA before federal tax. <!-- ANNUAL UPDATE -->{hsa_ca}</p>

<h3>3. Check whether your income can drop below the line</h3>
<p>The credit is based on modified adjusted gross income. Pre-tax retirement contributions and HSA deposits lower
it, and for households just over 400% that can restore a credit. Confirm with your tax professional.</p>

<h3>4. If you own a business, look at an ICHRA</h3>
<p>An individual coverage HRA lets your company reimburse individual premiums tax-free for you and your employees.
Ask us whether it beats paying premiums personally.</p>

{stm_block}

<h3>Add supplemental coverage to a high deductible</h3>
<p><a href="/hospital-indemnity-insurance/">Hospital indemnity</a>, <a href="/critical-illness-cancer-insurance/">critical
illness and cancer</a>, and accident plans pay cash directly to you. Paired with a lower-premium Bronze plan, they can
cost less in total than a Gold plan for some families. They do not replace major medical coverage.</p>

<h3>Turning 65 soon?</h3>
<p>Medicare is not tied to income the way marketplace credits are. If anyone in your household is close to 65, plan
the switch now. See our <a href="/medicare-annual-enrollment/">Medicare annual enrollment guide</a>.</p>
{cta(s, "Get a full-price comparison", "We show every plan we offer in your county, with and without a subsidy.")}
{faq_html(faqs)}
{agency_fine(s)}
"""
    return dict(
        slug="no-subsidy-health-insurance-options", title=title, faqs=faqs, body=body,
        seo=f"No ACA Subsidy in {YEAR}? {s['abbr']} Health Insurance Options",
        meta=(f"Lost your ACA subsidy for {YEAR}? Options for {s['state']} households over 400% FPL: "
              f"off-exchange plans, HSA Bronze, ICHRA and more. Free agent help."),
        parent="Under Individual / Health Insurance",
        sites="all")


def page_hospital(s):
    title = f"Hospital Indemnity Insurance in {s['state']}"
    faqs = [
        ("What does hospital indemnity insurance pay?",
         "It pays a fixed cash amount when you are admitted to the hospital, and on some plans for each day you "
         "stay, regardless of what the hospital bills. The money goes to you, not the hospital."),
        ("Can I use the money for anything?",
         "Yes. Benefits are paid to you and can go toward your deductible, rent, groceries or lost income."),
        ("Do I need health questions to qualify?",
         "It depends on the plan. Some are guaranteed issue with lower benefits; others ask a few health questions. "
         "Most have waiting periods or pre-existing condition limits."),
        ("Is this the same as health insurance?",
         "No. It does not meet ACA requirements and does not replace a major medical plan. It is designed to sit "
         "alongside one."),
    ]
    body = f"""
<p class="iha-lead">A hospital stay can use up most of a high deductible in a few days. Hospital indemnity insurance
pays you a set cash amount when you are admitted, so you are not paying that deductible out of savings. It is one of
the most popular add-ons for people on Bronze and HSA plans in {s['state']}.</p>

<h2>How it works</h2>
<ul>
<li>You choose a benefit amount, for example a lump sum per admission, a daily amount per day in the hospital, or both</li>
<li>When a covered stay happens, you file a claim and the carrier pays you directly</li>
<li>The payment does not depend on what your health plan covers or what the hospital charges</li>
<li>Many plans offer riders for outpatient surgery, ER visits, or ICU days</li>
</ul>

<h2>Who it fits</h2>
<ul>
<li>People on a Bronze or HSA plan with a deductible of several thousand dollars</li>
<li>Families who lost their subsidy for {YEAR} and moved to a lower-premium plan</li>
<li>Anyone expecting a planned surgery or delivery (check the plan's waiting period and pregnancy rules first)</li>
<li>Self-employed people who would lose income during a hospital stay</li>
</ul>

<div class="iha-box iha-warn"><strong>Read the fine print with us.</strong> Pre-existing condition limits, waiting
periods, and what counts as an admission (versus observation status) vary by carrier. We will show you exactly what a
plan pays before you buy.</div>
{cta(s, "Compare hospital indemnity plans", "We quote several carriers side by side and pair the benefit with your deductible.")}
{faq_html(faqs)}
{SUPP_FINE}
{agency_fine(s)}
"""
    return dict(
        slug="hospital-indemnity-insurance", title=title, faqs=faqs, body=body,
        seo=f"{YEAR} Hospital Indemnity Insurance {s['abbr']} | Cash for Stays",
        meta=(f"Hospital indemnity insurance in {s['state']} pays you cash when you are admitted. Pair it with a "
              f"Bronze or HSA plan to cover your deductible. Free quotes."),
        parent="Under Individual / Supplemental (create Supplemental if none exists)",
        sites="all")


def page_ci(s):
    title = f"Critical Illness and Cancer Insurance in {s['state']}"
    faqs = [
        ("What is critical illness insurance?",
         "A policy that pays a lump sum when you are diagnosed with a covered condition, such as a heart attack, "
         "stroke, or cancer. You decide how to spend it."),
        ("How is cancer insurance different?",
         "Cancer-only policies focus on cancer and often pay benefits for treatments like chemotherapy and radiation "
         "in addition to, or instead of, a diagnosis lump sum."),
        ("Does it cover a condition I already have?",
         "Usually not right away. Most policies exclude or limit pre-existing conditions and have a waiting period "
         "after the policy starts."),
        ("Does my health plan already cover this?",
         "Your health plan pays medical bills. These policies pay cash for everything else: deductibles, travel for "
         "treatment, and lost income."),
    ]
    body = f"""
<p class="iha-lead">A serious diagnosis brings bills your health plan does not touch: time off work, travel to a
treatment center, childcare, and a deductible that resets every January. Critical illness and cancer insurance pay
cash directly to you, so you can focus on recovery.</p>

<h2>Two ways to protect yourself</h2>
<table>
<tr><th></th><th>Critical illness</th><th>Cancer insurance</th></tr>
<tr><td>Pays when</td><td>You are diagnosed with a covered condition (commonly heart attack, stroke, cancer, organ failure)</td><td>You are diagnosed with or treated for cancer</td></tr>
<tr><td>How it pays</td><td>Usually a lump sum</td><td>Lump sum, per-treatment benefits, or both</td></tr>
<tr><td>Good for</td><td>Broad protection at a modest premium</td><td>Family history of cancer, or longer treatment costs</td></tr>
</table>

<h2>What to compare</h2>
<ul>
<li><strong>Covered conditions and definitions.</strong> Two policies can both say "heart attack" and define it differently.</li>
<li><strong>Waiting periods</strong> before benefits start, and pre-existing condition limits</li>
<li><strong>Recurrence benefits</strong> if a condition comes back</li>
<li><strong>Issue rules.</strong> Some plans skip health questions in exchange for lower benefit amounts</li>
<li><strong>Riders</strong> such as wellness screening benefits</li>
</ul>
<p>These plans pair well with a high-deductible or HSA plan, and they are worth a look for anyone who lost a subsidy
for {YEAR} and moved to a lower-premium plan.</p>
{cta(s, "Compare critical illness and cancer plans", "We compare definitions and waiting periods across carriers, not just price.")}
{faq_html(faqs)}
{SUPP_FINE}
{agency_fine(s)}
"""
    return dict(
        slug="critical-illness-cancer-insurance", title=title, faqs=faqs, body=body,
        seo=f"{YEAR} Critical Illness and Cancer Insurance {s['abbr']}",
        meta=(f"Critical illness and cancer insurance in {s['state']} pays cash on diagnosis to cover deductibles, "
              f"travel and lost income. Compare plans with a licensed agent."),
        parent="Under Individual / Supplemental",
        sites="all")


def page_final_expense(s):
    title = f"Final Expense Insurance in {s['state']}"
    faqs = [
        ("What is final expense insurance?",
         "A small whole life policy meant to cover funeral, burial or cremation, and final bills, so your family "
         "is not left paying them."),
        ("Do I need a medical exam?",
         "Usually not. Most final expense policies use a short health questionnaire instead of an exam."),
        ("What if I have health problems?",
         "Graded or guaranteed issue policies are available. They typically pay a limited benefit (often a return "
         "of premium plus interest) if death from natural causes happens in the first two or three years."),
        ("Does the premium go up?",
         "Whole life final expense premiums are generally fixed for life, and coverage does not expire as long as "
         "premiums are paid."),
    ]
    body = f"""
<p class="iha-lead">Final expense insurance is a small whole life policy built for one job: making sure the cost of a
funeral and final bills does not fall on your family. Coverage is simple to qualify for, premiums stay level, and the
benefit is paid directly to your beneficiary.</p>

<h2>How it works</h2>
<ul>
<li>Smaller face amounts sized to funeral and end-of-life costs</li>
<li>No medical exam on most policies, just a few health questions</li>
<li>Premiums are typically locked in and the policy builds cash value</li>
<li>Your beneficiary can use the money however they need</li>
</ul>

<h2>Three types of policies</h2>
<table>
<tr><th>Type</th><th>Who it fits</th><th>Benefit from day one?</th></tr>
<tr><td>Level (immediate)</td><td>Reasonably good health</td><td>Yes, full benefit</td></tr>
<tr><td>Graded</td><td>Some health conditions</td><td>Partial in the early years, full after the graded period</td></tr>
<tr><td>Guaranteed issue</td><td>Serious health conditions; no health questions</td><td>Limited benefit for natural causes in the first two to three years</td></tr>
</table>

<div class="iha-box">Eligibility ages, benefit amounts and graded periods vary by carrier. We check which carriers
will offer you a level policy first, since that is usually the best value.</div>
{cta(s, "Get a final expense quote", "Most applications take one phone call and no exam.")}
{faq_html(faqs)}
<p class="iha-fine">Life insurance products are underwritten by the issuing carrier. Coverage, eligibility, and
benefits vary by carrier and state; the policy controls.</p>
{agency_fine(s)}
"""
    return dict(
        slug="final-expense-insurance", title=title, faqs=faqs, body=body,
        seo=f"Final Expense Insurance {s['state']} | Burial Coverage",
        meta=(f"Final expense insurance in {s['state']}: small whole life policies with level premiums and no "
              f"medical exam on most plans. Compare carriers with an agent."),
        parent="Top level or under Life Insurance (create if none exists)",
        sites="all")


def page_aep(s):
    title = f"Medicare Annual Enrollment for {YEAR} in {s['state']}"
    bday = ""
    if s["abbr"] == "CA":
        bday = ("<h3>California's Birthday Rule</h3><p>California gives Medigap policyholders a 60-day window "
                "starting on their birthday each year to switch to a plan with the same or fewer benefits without "
                'health questions. See our <a href="/medicare/#birthday-rule">Birthday Rule guide</a>.</p>')
    elif s["abbr"] == "IL":
        bday = ("<h3>Illinois' Birthday Rule</h3><p>Illinois gives Medigap policyholders age 65 to 75 a 45-day "
                "window each year, starting on their birthday, to switch to a plan with equal or lesser benefits "
                "from their current insurer or an affiliated company, without medical underwriting. "
                'See our <a href="/medicare-supplement-birthday-rule/">Illinois '
                "Birthday Rule guide</a>.</p>")
    faqs = [
        (f"When is Medicare open enrollment for {YEAR}?",
         f"The annual enrollment period runs October 15 through December 7, 2026. Changes take effect "
         f"January 1, {YEAR}."),
        (f"What is the Part D out-of-pocket cap in {YEAR}?",
         f"$2,400 for covered drugs, up from $2,100 in 2026. The maximum standard deductible rises to $700."),
        ("Can I switch Medicare Supplement plans during annual enrollment?",
         "You can apply any time, but annual enrollment does not give you a guaranteed right to a Medigap plan. "
         "Outside a guaranteed-issue situation, the carrier can ask health questions and decline you."),
        ("What if I miss December 7?",
         "If you are in a Medicare Advantage plan, you get one change between January 1 and March 31, either to "
         "another Advantage plan or back to Original Medicare."),
    ]
    body = f"""
<p class="iha-lead">Medicare annual enrollment runs <strong>October 15 through December 7, 2026</strong>, for coverage
starting January 1, {YEAR}. <!-- ANNUAL UPDATE --> Plans change every year, including premiums, drug lists, pharmacy
networks, and doctor networks. Here is what to check before December 7.</p>

<h2>{YEAR} Medicare dates</h2>
<table>
<tr><th>Window</th><th>What you can do</th></tr>
<tr><td>Oct 15 - Dec 7, 2026</td><td>Join, switch or drop a Medicare Advantage or Part D plan</td></tr>
<tr><td>Jan 1 - Mar 31, {YEAR}</td><td>If you are in Medicare Advantage: make one switch to another Advantage plan or return to Original Medicare</td></tr>
<tr><td>Any time</td><td>Apply for a Medicare Supplement (health questions may apply)</td></tr>
</table>

<h2>What changes in {YEAR}</h2>
<ul>
<li><strong>Part D out-of-pocket cap rises to $2,400</strong> (from $2,100 in 2026). <!-- ANNUAL UPDATE --></li>
<li><strong>Maximum Part D deductible rises to $700</strong> (from $615). <!-- ANNUAL UPDATE --></li>
<li><strong>Part B premium and deductibles for {YEAR}</strong> are usually announced by CMS in the fall. We will
update this page when they are published. <!-- ANNUAL UPDATE: add Part B premium, Part A and B deductibles --></li>
<li>Check your plan's Annual Notice of Change for network, drug list and copay changes.</li>
</ul>

<h2>Thinking about leaving Medicare Advantage for a Medigap plan?</h2>
<p>You can drop an Advantage plan during annual enrollment, but <strong>line up the Medigap plan first</strong>. Outside
guaranteed-issue situations, Medigap carriers can ask health questions and decline you. Federal rules guarantee your
right in some cases, such as when you joined Medicare Advantage for the first time within the last 12 months, or your
plan leaves your area. Apply for the supplement, wait for approval, and then switch.</p>
{bday}

<h2>Your annual enrollment checklist</h2>
<ul>
<li>Are all your prescriptions on next year's drug list, at the same tier?</li>
<li>Are your doctors and hospitals still in network?</li>
<li>Is your preferred pharmacy still preferred?</li>
<li>What is the plan's maximum out-of-pocket for {YEAR}?</li>
<li>Did dental, vision, or hearing extras change?</li>
</ul>
{cta(s, f"Review your {YEAR} Medicare options", "Compare plans in your ZIP code online, or have a licensed agent review your drugs and doctors.", quote_url=SUNFIRE, quote_label="Compare Plans Online", medicare=True)}
{faq_html(faqs)}
{medicare_fine(s)}
"""
    return dict(
        slug="medicare-annual-enrollment", title=title, faqs=faqs, body=body,
        seo=f"Medicare Open Enrollment {YEAR} {s['abbr']}: Oct 15 - Dec 7",
        meta=(f"Medicare annual enrollment for {YEAR} runs Oct 15 - Dec 7, 2026. What changes in {s['state']}, "
              f"the new $2,400 Part D cap, and a checklist. Free agent review."),
        parent="Under Medicare",
        sites="all")


def page_stm(s):
    title = f"Short-Term Health Insurance in {s['state']}"
    faqs = [
        ("Is short-term health insurance ACA coverage?",
         "No. Short-term plans do not have to cover pre-existing conditions or all essential health benefits, and "
         "they are not eligible for premium tax credits."),
        ("How long can I keep a short-term plan?",
         f"{s['stm_note']} A 2024 federal rule limits terms to three months (four with renewal). Federal agencies said "
         "in August 2025 they would not prioritize enforcing it and plan new rules, so available terms may change."),
        ("Can I buy short-term coverage any time?",
         "Yes. Short-term plans are not limited to open enrollment, and coverage can start within days."),
        ("Is there a penalty for having short-term coverage?",
         "There is no federal penalty for going without ACA coverage."),
    ]
    body = f"""
<p class="iha-lead">Short-term health insurance covers a gap: between jobs, waiting for employer coverage to start,
or after missing open enrollment. Coverage can start within days and premiums are often well below full-price ACA
plans. The trade-off is real, so here is the honest version.</p>

<h2>Rules in {s['state']}</h2>
<p>{s['stm_note']}</p>
<p>At the federal level, a 2024 rule limits short-term plans to three months, or four months with a renewal. In August
2025 the federal agencies said they would not prioritize enforcing that limit and would write new rules. As of October
2026 the 2024 rule is still on the books, so call us for the terms carriers are actually offering when you need to start.</p>

<h2>Short-term plan vs. ACA plan</h2>
<table>
<tr><th></th><th>Short-term plan</th><th>ACA plan</th></tr>
<tr><td>Pre-existing conditions</td><td>Usually excluded</td><td>Covered</td></tr>
<tr><td>Health questions</td><td>Yes, you can be declined</td><td>No</td></tr>
<tr><td>Enrollment</td><td>Any time</td><td>Open enrollment or a qualifying event</td></tr>
<tr><td>Subsidies</td><td>None</td><td>Available below 400% FPL</td></tr>
<tr><td>Benefit limits</td><td>Plan maximums apply</td><td>No lifetime or annual dollar limits on essential benefits</td></tr>
</table>

<h2>Who it fits</h2>
<ul>
<li>Healthy people between jobs or waiting on employer coverage</li>
<li>People who missed open enrollment and have no qualifying event</li>
<li>Early retirees bridging a few months to Medicare</li>
</ul>
<div class="iha-box iha-warn"><strong>Not a fit if</strong> you are pregnant, take ongoing prescriptions, or are treating
a condition. Those costs are typically excluded. An ACA plan during open enrollment ({s['oe']}) is the safer choice.</div>
{cta(s, "Compare short-term and ACA options", "We will tell you plainly which one fits your situation.")}
{faq_html(faqs)}
<p class="iha-fine">Short-term limited duration insurance is not comprehensive coverage and is not required to comply
with federal ACA requirements. It may not cover pre-existing conditions. Read the policy for exclusions and limits.</p>
{agency_fine(s)}
"""
    return dict(
        slug="short-term-health-insurance", title=title, faqs=faqs, body=body,
        seo=f"{YEAR} Short-Term Health Insurance {s['state']}",
        meta=(f"Short-term health insurance in {s['state']}: current rules, how it compares to an ACA plan, and who "
              f"it fits. Coverage can start in days. Free agent help."),
        parent="Under Individual / Health Insurance",
        sites="stm")


def page_ichra(s):
    title = f"ICHRA for {s['state']} Employers"
    faqs = [
        ("What is an ICHRA?",
         "An individual coverage health reimbursement arrangement lets an employer reimburse employees, tax-free, "
         "for individual health insurance premiums and, if the employer chooses, other medical expenses."),
        ("What size business can offer one?",
         "Any size. Employers can set different allowances for different classes of employees, such as full-time "
         "and part-time, or by location."),
        ("Do employees have to buy their own plan?",
         "Yes. Each employee must enroll in individual health coverage or Medicare to be reimbursed."),
        ("Can employees still get a marketplace subsidy?",
         "Only if they decline the ICHRA and the ICHRA is considered unaffordable for them. If it is affordable, "
         "they cannot get a premium tax credit."),
    ]
    body = f"""
<p class="iha-lead">Group renewals keep rising and small groups in {s['state']} have fewer carrier choices every year.
An ICHRA flips the model: you set a fixed monthly allowance, and each employee picks the individual plan that fits them,
with the reimbursement tax-free to both of you.</p>

<h2>How an ICHRA works</h2>
<ul>
<li>You choose an allowance for each class of employee (for example full-time, part-time, or by location)</li>
<li>Employees buy individual coverage on or off {s['exchange']}</li>
<li>They submit proof of coverage and premiums, and you reimburse up to the allowance</li>
<li>Reimbursements are excluded from income and payroll taxes</li>
</ul>

<h2>ICHRA vs. a traditional group plan</h2>
<table>
<tr><th></th><th>ICHRA</th><th>Group plan</th></tr>
<tr><td>Your cost</td><td>Fixed allowance you set</td><td>Set by renewal each year</td></tr>
<tr><td>Plan choice</td><td>Each employee picks their own</td><td>One or a few plans for everyone</td></tr>
<tr><td>Participation rules</td><td>None</td><td>Carrier minimums usually apply</td></tr>
<tr><td>Who handles claims and service</td><td>The employee's own carrier</td><td>The group carrier</td></tr>
</table>

<h2>Things to plan for</h2>
<ul>
<li><strong>Affordability.</strong> Employers with 50 or more full-time employees must meet ACA affordability tests to avoid penalties.</li>
<li><strong>Notice.</strong> Employees must get written notice, generally at least 90 days before the plan year starts.</li>
<li><strong>Local plan prices.</strong> Individual premiums vary by age and county, so we model the allowance against real {s['state']} rates.</li>
<li><strong>Under 50 employees?</strong> A QSEHRA is a simpler alternative with annual limits set by the IRS.</li>
</ul>
{cta(s, "See whether an ICHRA beats your renewal", "Send us your census and current renewal. We will model both side by side.")}
{faq_html(faqs)}
{agency_fine(s)}
"""
    return dict(
        slug="ichra", title=title, faqs=faqs, body=body,
        seo=f"ICHRA {s['state']} | {YEAR} Guide for Employers",
        meta=(f"An ICHRA lets {s['state']} employers reimburse individual health premiums tax-free at a fixed cost. "
              f"How it works, how it compares to group, and next steps."),
        parent="Under Group / Business insurance",
        sites=["tx", "il", "fl", "in"])


def page_il_birthday(s):
    title = "Illinois Medicare Supplement Birthday Rule"
    faqs = [
        ("What is the Illinois Medigap birthday rule?",
         "An annual 45-day window, starting on your birthday, when Illinois Medigap policyholders age 65 to 75 can "
         "move to a plan with equal or lesser benefits from their current insurer or an affiliated company, "
         "without medical underwriting."),
        ("Who qualifies?",
         "Illinois residents age 65 through 75 who already have a Medicare Supplement policy."),
        ("Can I switch to a different insurance company?",
         "Only to an insurer affiliated with your current one. Moving to an unrelated company usually means "
         "answering health questions, and the new insurer can decline you."),
        ("Can I upgrade to a plan with more benefits?",
         "Not under the birthday rule. Moving to richer benefits usually means answering health questions."),
        ("Does it apply to Medicare Advantage?",
         "No. The birthday rule is for Medicare Supplement (Medigap) policies only."),
    ]
    body = f"""
<p class="iha-lead">If you have a Medicare Supplement plan in Illinois and you are between 65 and 75, you get a
<strong>45-day window every year, starting on your birthday</strong>, to switch to a plan with equal or lesser benefits
from your current insurer or an affiliated company, without medical underwriting. Medigap premiums tend to rise as you
age, so this window is worth checking every year.</p>

<h2>How the Illinois birthday rule works</h2>
<ul>
<li>The window opens on your birthday and lasts 45 days</li>
<li>You must be age 65 through 75 and already have a Medigap policy</li>
<li>The new plan must have equal or lesser benefits (for example Plan G to Plan G, or Plan G to Plan N)</li>
<li>The new policy must come from your current insurer or one of its affiliated companies</li>
<li>No health questions, so a health condition cannot be used to decline you</li>
<li>Insurers must notify eligible policyholders about the window</li>
</ul>

<h2>Which plans you can move to</h2>
<p>The birthday rule lets you move within your insurer's family of companies, not to any insurer. Many Medigap
carriers sell through more than one affiliated company, sometimes at different premiums for the same plan letter. We
check what your insurer and its affiliates offer and handle the switch so your old policy ends the day the new one
starts, with no gap. Moving to an unrelated company is still possible, but outside a guaranteed-issue situation it
means answering health questions.</p>

<div class="iha-box"><strong>Example:</strong> You have Plan G and your premium went up at renewal. In the 45 days after
your birthday you can move to Plan N with the same insurer, or to a Plan G from an affiliated company at a lower premium,
without health questions. Benefits are standardized, so a Plan G covers the same things whichever company issues it.</div>

<h2>What to do before your birthday</h2>
<ul>
<li>Note your birthday on the calendar and call us about two weeks before</li>
<li>Have your current policy and premium handy</li>
<li>We compare your insurer's and its affiliates' Plan G and Plan N premiums for your ZIP code and age</li>
<li>Do not cancel your current policy until the new one is approved</li>
</ul>
{cta(s, "Check your birthday rule savings", "A two-minute comparison can show whether a switch lowers your premium.", quote_url=SUNFIRE, quote_label="Compare Plans Online", medicare=True)}
{faq_html(faqs)}
{medicare_fine(s)}
"""
    return dict(
        slug="medicare-supplement-birthday-rule", title=title, faqs=faqs, body=body,
        seo="Illinois Medigap Birthday Rule: 45-Day Switch Window",
        meta=("Illinois Medigap holders age 65-75 get 45 days after each birthday to switch to an equal or lesser "
              "plan with their insurer or an affiliate. No health questions."),
        parent="Under Medicare",
        sites=["il"])


def page_fl_ma_vs_medigap(s):
    title = "Medicare Advantage vs. Medicare Supplement in Florida"
    faqs = [
        ("Which is better in Florida, Medicare Advantage or a Medicare Supplement?",
         "It depends on how you use care. Medicare Advantage usually has lower premiums and a network with copays. "
         "A Medicare Supplement costs more each month but lets you see any provider that accepts Medicare, "
         "nationwide, with little or nothing out of pocket depending on the plan."),
        ("Can I switch from Medicare Advantage to a Medigap plan later?",
         "You can apply at any time, but outside a guaranteed-issue situation the insurer can ask health questions "
         "and decline you. Florida does not have an annual Medigap birthday rule."),
        ("I am under 65 and on Medicare because of a disability. Can I get a Medigap plan in Florida?",
         "Yes. Florida requires Medigap insurers to offer coverage to people under 65 who have Medicare because of "
         "a disability or end-stage renal disease, with a six-month open enrollment window after enrolling in "
         "Part B. Premiums for under-65 enrollees are often higher."),
        ("I split the year between Florida and another state. What should I pick?",
         "Snowbirds often prefer a Medicare Supplement because it works with any Medicare provider in any state. "
         "Most Medicare Advantage plans cover only emergency and urgent care outside the service area."),
    ]
    body = f"""
<!-- VERIFY: confirm the under-65 window wording against current s. 627.6741, Florida Statutes. -->
<p class="iha-lead">Florida has one of the most competitive Medicare Advantage markets in the country, with many
$0-premium plans in most counties. That makes the Advantage-or-Supplement decision bigger here than almost anywhere.
Here is how the two compare for Floridians, including snowbirds and people under 65.</p>

<h2>Side by side</h2>
<table>
<tr><th></th><th>Medicare Advantage (Part C)</th><th>Medicare Supplement (Medigap)</th></tr>
<tr><td>Monthly premium</td><td>Often $0 to low, plus your Part B premium</td><td>Higher, plus your Part B premium and a separate Part D plan</td></tr>
<tr><td>Doctors and hospitals</td><td>Plan network (HMO or PPO)</td><td>Any provider in the U.S. that accepts Medicare</td></tr>
<tr><td>Costs when you use care</td><td>Copays and coinsurance up to the plan's yearly maximum</td><td>Little to none, depending on the plan letter</td></tr>
<tr><td>Referrals</td><td>Often required on HMOs</td><td>Not required</td></tr>
<tr><td>Extras</td><td>Often dental, vision, hearing, and over-the-counter allowances</td><td>Not included; add a separate dental or vision policy</td></tr>
<tr><td>Travel outside Florida</td><td>Usually emergency and urgent care only</td><td>Works nationwide</td></tr>
<tr><td>Switching later</td><td>During annual enrollment each fall</td><td>Health questions may apply after your first open enrollment</td></tr>
</table>

<h2>Florida rules worth knowing</h2>
<ul>
<li><strong>Your first Medigap window matters most.</strong> In the six months after you are 65 and enrolled in Part B,
Medigap insurers must accept you without health questions. After that, they generally can ask them.</li>
<li><strong>Under 65 on Medicare?</strong> Florida requires Medigap insurers to offer coverage to people under 65 with
Medicare because of a disability or end-stage renal disease, with a six-month open enrollment after Part B starts.</li>
<li><strong>No annual birthday rule.</strong> Some states let you change Medigap plans each year without health
questions. Florida does not, so choose carefully the first time.</li>
<li><strong>Trial right.</strong> If you join Medicare Advantage when you first become eligible, or drop a Medigap plan to
try Advantage for the first time, federal rules generally let you go back to a Medigap plan within 12 months without
health questions.</li>
</ul>

<h2>Who usually picks which</h2>
<h3>Medicare Advantage tends to fit</h3>
<ul>
<li>Year-round Florida residents happy with a local network</li>
<li>People who want the lowest premium and value dental, vision, and hearing extras</li>
<li>People in good health who rarely see specialists</li>
</ul>
<h3>A Medicare Supplement tends to fit</h3>
<ul>
<li>Snowbirds and frequent travelers</li>
<li>People who want specific specialists or cancer centers without network limits</li>
<li>Anyone who wants predictable costs and can afford the higher premium</li>
</ul>
<p>Compare Supplement plans on our <a href="/insurance-applications/medicare-supplement-plans/">Florida Medicare
Supplement page</a>, or see what changes this fall in our <a href="/medicare-annual-enrollment/">annual enrollment
guide</a>.</p>
{cta(s, "Get a side-by-side for your ZIP code", "We compare Advantage plans and Supplement premiums from the carriers we offer in your county.", quote_url=SUNFIRE, quote_label="Compare Plans Online", medicare=True)}
{faq_html(faqs)}
{medicare_fine(s)}
"""
    return dict(
        slug="medicare-advantage-vs-medicare-supplement", title=title, faqs=faqs, body=body,
        seo=f"Medicare Advantage vs Medigap in Florida ({YEAR})",
        meta=("Medicare Advantage or a Medicare Supplement in Florida? Compare costs, networks and travel coverage, "
              "plus Florida rules for snowbirds and under-65 enrollees."),
        parent="Under Medicare (sibling of the Medicare Supplement page 11416)",
        sites=["fl"])


def page_fl_hurricane(s):
    title = "Hurricanes and Your Health Insurance in Florida"
    faqs = [
        ("Can I get my prescriptions refilled early before a hurricane?",
         "Yes. Florida law requires health insurers and HMOs to waive refill-too-soon limits and pay for at least a "
         "30-day supply when your county is under a hurricane warning, a state of emergency, or an activated "
         "emergency operations center. Ask your pharmacy as soon as the warning is issued."),
        ("A storm made me miss open enrollment. Can I still enroll?",
         "Possibly. If you live in a FEMA-declared disaster area and the storm kept you from enrolling, you can ask "
         "HealthCare.gov for a special enrollment period, generally available for 60 days after the FEMA incident "
         "period ends. Call 1-800-318-2596."),
        ("Does Medicare have a special enrollment period after a hurricane?",
         "Yes, in some cases. If a FEMA-declared emergency kept you from making a Medicare Advantage or Part D "
         "change you were eligible to make, you may qualify for a disaster special enrollment period."),
        ("What if I have to evacuate and see an out-of-network doctor?",
         "During a declared disaster, Medicare Advantage plans must let you get covered care at non-contracted "
         "providers at in-network cost sharing. Many other insurers relax network and referral rules too. Call the "
         "number on your ID card and keep receipts."),
    ]
    body = f"""
<!-- VERIFY each June before hurricane season: s. 252.358 F.S. wording, HealthCare.gov disaster SEP length,
and the CMS disaster SEP rules. Consider pinning this page to the homepage during active storms. -->
<p class="iha-lead">Every hurricane season raises the same questions from our Florida clients: can I refill my
medications early, what if I evacuate out of my network, and what if a storm made me miss a deadline? Here are the
answers, before you need them.</p>

<h2>Before the storm</h2>
<ul>
<li><strong>Refill prescriptions early.</strong> When your county is under a hurricane warning or a state of emergency,
Florida law requires insurers to cover at least a 30-day refill even if it is too soon. Request it within 30 days of
the declaration.</li>
<li><strong>Photograph your ID cards</strong> (medical, dental, Medicare, Part D) and save your carrier's phone number
and app login on your phone.</li>
<li><strong>Write down</strong> your medications, doses, and prescribing doctors.</li>
<li><strong>Keep a list of providers</strong> where you might evacuate. If you have a PPO or a Medicare Supplement, check
which ones accept your plan.</li>
</ul>

<h2>If you evacuate</h2>
<ul>
<li><strong>Medicare Advantage:</strong> during a declared disaster, plans must cover care from non-contracted providers
at in-network cost sharing and waive referral requirements while the emergency lasts.</li>
<li><strong>Medicare Supplement:</strong> works with any Medicare provider in the country, wherever you are.</li>
<li><strong>ACA and employer plans:</strong> emergency care is covered out of network. For non-emergency care, call your
carrier first, since many relax network rules after a declaration.</li>
<li>Keep every receipt. Out-of-network claims are easier with documentation.</li>
</ul>

<h2>If a storm made you miss a deadline</h2>
<table>
<tr><th>Coverage</th><th>What may be available</th><th>How to ask</th></tr>
<tr><td>Marketplace (ACA) plans</td><td>A special enrollment period if a FEMA-declared disaster kept you from enrolling, generally for 60 days after the incident period ends</td><td>HealthCare.gov, 1-800-318-2596, or call us</td></tr>
<tr><td>Medicare Advantage and Part D</td><td>A disaster special enrollment period if the emergency kept you from making a change you were eligible to make</td><td>1-800-MEDICARE, or call us</td></tr>
<tr><td>Losing job-based coverage after a storm</td><td>The usual 60-day loss-of-coverage special enrollment period</td><td>Call us right away</td></tr>
</table>
<div class="iha-box">You will usually be asked to confirm that you lived in an affected county. Check whether your
county is included at fema.gov/disaster.</div>

<h2>After the storm</h2>
<ul>
<li>Check whether your doctors and pharmacy are open; your carrier's app often shows temporary locations</li>
<li>Ask about telehealth, which most plans cover</li>
<li>If your income or address changed, update your marketplace application so your subsidy stays accurate</li>
</ul>
{cta(s, "Questions after a storm? Call us", "We help clients replace ID cards, file out-of-network claims, and use disaster enrollment periods.")}
{faq_html(faqs)}
{agency_fine(s)}
"""
    return dict(
        slug="hurricane-health-insurance-guide", title=title, faqs=faqs, body=body,
        seo="Hurricane Health Insurance Guide for Florida",
        meta=("Florida hurricane guide for health insurance: early prescription refills, evacuating out of network, "
              "and disaster enrollment periods for ACA and Medicare."),
        parent="Top level or under Resources / FAQ",
        sites=["fl"])


def page_in_hip(s):
    title = f"Losing HIP Coverage in {YEAR}? Your Options in Indiana"
    faqs = [
        ("When do the HIP work requirements start?",
         f"January 1, {YEAR}. They apply to Healthy Indiana Plan members age 19 to 64 who are not pregnant and not "
         "eligible for Medicare, unless an exemption applies."),
        ("What do I have to do to keep HIP?",
         "Show 80 hours a month of work, job training, volunteering, or school, or earn at least $580 a month, or "
         "qualify for an exemption. Indiana looks back three months, so October through December 2026 counts for "
         "January applications."),
        ("If I lose HIP, can I get a subsidized marketplace plan?",
         "It depends on why. Under federal law, people who lose Medicaid for not meeting work requirements cannot get "
         "a premium tax credit. If you lose HIP for another reason, such as higher income, you may qualify for a "
         "special enrollment period and a subsidy."),
        ("Is there still a year-round enrollment option for low-income people?",
         "No. The special enrollment period for people under 150% of the poverty level has ended, so timing matters. "
         "Losing coverage generally gives you 60 days to enroll in a marketplace plan."),
    ]
    body = f"""
<!-- Facts as of Oct 2026 (FSSA, Mirror Indy). Re-check FSSA guidance before publishing and each quarter. -->
<p class="iha-lead">Starting January 1, {YEAR}, most Healthy Indiana Plan (HIP) members must meet new work and activity
requirements, and eligibility will be checked every six months instead of once a year. The state estimates more than
58,000 Hoosiers could lose HIP coverage in {YEAR}. If you or someone in your family is on HIP, here is what to know now.</p>

<div class="iha-box iha-warn"><strong>The most important thing first:</strong> if you lose HIP <em>because you did not meet
or report the work requirement</em>, federal law bars you from a marketplace premium tax credit. Keeping HIP, or
claiming an exemption you qualify for, is almost always cheaper than any private plan. Report your hours through the
state before you think about anything else.</div>

<h2>The new HIP rules</h2>
<ul>
<li><strong>Who:</strong> HIP members age 19 to 64 who are not pregnant and not eligible for Medicare</li>
<li><strong>What:</strong> 80 hours a month of work, job training, volunteering, or school, or earnings of at least $580 a month</li>
<li><strong>Lookback:</strong> three months, so October through December 2026 counts for January {YEAR} applications</li>
<li><strong>Checks:</strong> eligibility every six months; hours checked more often</li>
<li><strong>Exemptions</strong> apply for some caregivers, people with certain health conditions, and others. See the
<a href="https://www.in.gov/fssa/hip/hip-work-requirements/info-for-hip-members" target="_blank" rel="noopener">FSSA HIP page</a>.</li>
</ul>

<h2>If you lose HIP anyway</h2>
<h3>Lost HIP because your income went up</h3>
<p>Losing Medicaid is a qualifying event. You generally have 60 days to enroll in a {s['exchange']} plan, and you may
qualify for a premium tax credit. We can tell you within minutes.</p>
<h3>Lost HIP for not meeting work requirements</h3>
<p>You can still buy a marketplace plan during open enrollment ({s['oe']}) or after a qualifying event, but without a
premium tax credit. Lower-cost options include Bronze plans, short-term coverage where it fits, and job-based coverage
if your employer offers it.</p>
<h3>Got a job with benefits?</h3>
<p>Compare the employer plan to what you would pay on your own. If the employer offers an ICHRA, see our
<a href="/ichra/">ICHRA guide</a>.</p>

<h2>Short-term coverage in Indiana</h2>
<p>{s['stm_note']} Short-term plans are not ACA coverage and usually exclude pre-existing conditions.
<a href="/short-term-health-insurance/">Learn more</a>.</p>
{cta(s, "Losing HIP? Talk to us first", "We will check whether you can keep HIP, qualify for a subsidy, or need a lower-cost private plan.")}
{faq_html(faqs)}
<p class="iha-fine">{s['name']} is not affiliated with the Indiana Family and Social Services Administration (FSSA) or the
Healthy Indiana Plan. For HIP eligibility decisions, contact FSSA. We help with private and marketplace coverage.</p>
{agency_fine(s)}
"""
    return dict(
        slug="losing-hip-coverage", title=title, faqs=faqs, body=body,
        seo=f"Losing HIP Coverage in {YEAR}? Indiana Options",
        meta=(f"HIP work requirements start Jan 1, {YEAR}. What Indiana members must do to keep coverage, and "
              f"options if you lose it: marketplace plans, subsidies and more."),
        parent="Under Individual / Health Insurance",
        sites=["in"])


PAGES = [page_open_enrollment, page_no_subsidy, page_aep, page_hospital, page_ci,
         page_final_expense, page_stm, page_ichra, page_il_birthday,
         page_fl_ma_vs_medigap, page_fl_hurricane, page_in_hip]


def wanted(page, key):
    scope = page["sites"]
    if scope == "all":
        return True
    if scope == "stm":
        return SITES[key]["stm"]
    return key in scope


BAD_DASH = re.compile("[\u2013\u2014]")


def build():
    root = os.path.join(os.path.dirname(__file__), "..", "drafts")
    index = []
    for key, s in SITES.items():
        os.makedirs(os.path.join(root, key), exist_ok=True)
        for fn in PAGES:
            p = fn(s)
            if not wanted(p, key):
                continue
            blocker = ("BLOCKER: phone number is a placeholder - fill in SITES before publishing\n"
                       if "VERIFY" in s["tel"] else "")
            header = (f"<!--\nDRAFT for {s['domain']} - not published\n{blocker}"
                      f"WP page title (renders as H1): {p['title']}\n"
                      f"Slug: /{p['slug']}/\nSuggested parent: {p['parent']}\n"
                      f"SEO title ({len(p['seo'])} chars): {p['seo']}\n"
                      f"Meta description ({len(p['meta'])} chars): {p['meta']}\n"
                      f"Page layout: et_no_sidebar\n-->\n")
            out = (header + CSS + '\n<div class="iha-gp">' + p["body"] + "</div>\n" +
                   jsonld(s, p["title"], p["slug"], p["faqs"]) + "\n")
            assert not BAD_DASH.search(out), f"em/en dash in {key}/{p['slug']}"
            assert "<h1" not in out
            assert len(p["meta"]) <= 160 and len(p["seo"]) <= 60, f"meta/seo too long: {key}/{p['slug']}"
            with open(os.path.join(root, key, p["slug"] + ".html"), "w") as f:
                f.write(out)
            index.append((s["domain"], p["slug"], p["title"], len(p["seo"]), len(p["meta"])))
    return index


if __name__ == "__main__":
    for row in build():
        print("%-28s %-38s seo=%d meta=%d  %s" % (row[0], row[1], row[3], row[4], row[2]))
