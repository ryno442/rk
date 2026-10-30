# Content Gap Analysis - State Health Agent Sites

Prepared 2026-10-30. Covers texashealthagents.com, ilhealthagents.com, floridahealthagents.com,
pahealthagents.com and californiahealthagents.com.

**Limits of this review:** this session's network policy blocks all five domains, so the live sites
were not crawled. The "what exists today" column comes from the page-builder skill notes (page IDs,
menus and hubs recorded through Aug 2026). Before publishing a draft, search the site
(`/wp-json/wp/v2/pages?search=<slug>&status=any`) to confirm the page doesn't already exist under
another slug. If it does, merge the new content into that page.

Draft pages are in `drafts/<site>/`, built by `tools/build_drafts.py`. Edit the generator, not the
HTML, and re-run `python3 tools/build_drafts.py`.

---

## 1. Time-sensitive: publish this week

| Opportunity | Why now | Draft |
|---|---|---|
| **2027 Open Enrollment guide** (all 5) | OE opens Nov 1, 2026. The enhanced subsidies expired 12/31/2025, the 400% FPL cliff is back, there is no repayment cap from 2026 coverage onward, and the 2027 max OOP is $12,000/$24,000. High search volume, and none of the skill notes list a dated OE page. | `open-enrollment-2027.html` |
| **No-subsidy options page** (all 5) | Households over 400% FPL lose all help for 2027. This is the biggest new audience this season, and it feeds HSA-Bronze, ICHRA, STM (where legal) and supplemental sales. | `no-subsidy-health-insurance-options.html` |
| **Medicare AEP 2027** (all 5) | AEP runs Oct 15 - Dec 7, 2026. The Part D cap goes to $2,400 and the deductible to $700. Also covers MA-to-Medigap switching, with a warning about underwriting. | `medicare-annual-enrollment.html` |

## 2. Products IHA is contracted for with no known page

The contracting reference shows appointments with Allstate Health Solutions / NHIC (fixed benefit,
TrioMED, CI, cancer, accident, dental, final expense), ManhattanLife (cancer, CI, DVH, Affordable
Choice), GTL, New Era, Pivot Health and UnitedHealthOne. None of the five skill notes list a
supplemental, indemnity or final-expense page on any site.

| Opportunity | Sites | Draft |
|---|---|---|
| Hospital indemnity | all 5 | `hospital-indemnity-insurance.html` |
| Critical illness and cancer | all 5 | `critical-illness-cancer-insurance.html` |
| Final expense life | all 5 | `final-expense-insurance.html` |
| Short-term medical | TX, FL, PA only. **Not IL** (banned 1/1/2025) or **CA** (SB 910). | `short-term-health-insurance.html` |
| Accident insurance | all 5 | not drafted yet: same template as CI |
| Dental/vision/hearing bundles (ManhattanLife DVH, NHIC) | check against the existing dental hubs first | not drafted |

Before publishing, check carrier availability in each state. Several schedules carve out FL and
other states.

## 3. Site-specific gaps

### Texas (texashealthagents.com)
- ICHRA page: PA and CA have one, TX doesn't appear to. Draft: `drafts/tx/ichra.html`.
- STM page: allowed in TX. Draft included.
- Medicare line: (972) 666-0578 ext. 2, linked as `tel:+19726660578,2` (the comma pause auto-dials the extension). Confirmed by Ryan 10/30/26. Also update the TX row in the ihealthagents skill.

### Illinois (ilhealthagents.com)
- **Illinois Medigap Birthday Rule** page. This is a state-specific ranking opportunity (CA already ranks on its own birthday rule content). Draft: `drafts/il/medicare-supplement-birthday-rule.html`.
  The switch must be to a policy from the current insurer or an affiliated company (confirmed by Ryan 10/30/26), so the page explains insurer-family moves and the health questions for moving to an unrelated company.
- Get Covered Illinois (Illinois's own marketplace since PY2026) explainer: the OE page covers dates. A standalone "Get Covered Illinois vs. HealthCare.gov" page is a further opportunity.
- ICHRA page. Draft included.

### Florida (floridahealthagents.com)
- Existing GSC problems (64 404s, 206 crawled-not-indexed, noindex fixed 8/20/26) mean new pages should go out alongside fixes for thin carrier pages. Strong pages on supplemental, AEP and OE topics give Google something worth indexing.
- STM page (FL law allows up to 36 months total). Draft included.
- ICHRA page. Draft included.
- **Medicare Advantage vs. Medigap in Florida** (drafted: `drafts/fl/medicare-advantage-vs-medicare-supplement.html`). Florida is the largest Medicare market of the five. The page covers snowbirds, the under-65 disability/ESRD Medigap right (s. 627.6741, has a VERIFY note), the fact that Florida has no birthday rule, and the federal trial right. It links to the existing Medigap page 11416.
- **Hurricane health insurance guide** (drafted: `drafts/fl/hurricane-health-insurance-guide.html`). This is unique to Florida and searched every season: early prescription refills under s. 252.358 F.S., out-of-network care when evacuating (MA disaster rules), and disaster SEPs for HealthCare.gov (60 days after the FEMA incident period) and Medicare. Re-verify every June, and pin it to the homepage during active storms.
- County Medicare pages (Miami-Dade, Broward, Palm Beach, Hillsborough, Orange): hold off until the 206 crawled-not-indexed pages are cleaned up. Thin county pages would make that problem worse.

### Pennsylvania (pahealthagents.com)
- Group carrier pages exist for Aetna, Cigna, Geisinger, UHC and Capital Blue Cross. **Missing: Highmark, Independence Blue Cross and UPMC Health Plan.** These are three of the largest group carriers in the state. Clone the Geisinger group page using the PA skill method.
- Individual/Pennie carrier pages: confirm which exist. Ambetter Health (PA Health & Wellness), Oscar, Highmark, IBX/AmeriHealth Caring and UPMC are the main 2027 Pennie carriers. Verify the 2027 list on pennie.com.
- Pennie Certified Broker logo: still waiting on the licensed files from Pennie External Affairs.
- PA pages use the baked-in header/footer template. The drafts here are content blocks, so drop them into a cloned page's content area.

### California (californiahealthagents.com)
- The site is already broad (group section, HSA, birthday rule, dental, travel, pet). Its gaps are supplemental and final expense, which are drafted.
- The OE draft uses Covered CA dates (Nov 1 - Jan 31; Dec 31 for Jan 1 start) and includes the CA mandate and HSA non-conformity.
- Do not add STM. The no-subsidy draft explains that it's banned.

### Indiana (indianahealthagents.com)
No skill notes and no site access, so these drafts are built from scratch. Phone: (312) 726-6565 (`tel:+13127266565`), the same number as Florida, confirmed by Ryan 10/30/26. Contact page: `/contact-us/`.
- **Losing HIP coverage** (drafted: `drafts/in/losing-hip-coverage.html`). This is the biggest Indiana-only opportunity. HIP work requirements start 1/1/2027 (80 hrs/month or $580/month, ages 19-64, 3-month lookback, 6-month redeterminations), and the state estimates 58,000+ could lose coverage. Key point: anyone who loses Medicaid for work-requirement non-compliance is barred from a premium tax credit (OBBBA s.71119), and the 150% FPL low-income SEP is gone.
- Shared set: OE 2027, no-subsidy, AEP, hospital indemnity, CI/cancer, final expense, ICHRA, and STM. Indiana allows initial terms up to 364 days and up to 36 months total, with a $2M minimum benefit (IC 27-8-5.9).
- Medicare counseling program in the disclaimer: Indiana SHIP, 1-800-452-4800.
- Indiana Medigap birthday rule (new in 2026: 60 days, same plan letter, any insurer) is covered in the AEP draft and links the existing help center article. Sources differ on when the window opens, so the page keeps the timing general.
- Not drafted: Indiana carrier pages (Anthem, CareSource, Ambetter/MHS, UHC, etc.). Confirm which exist first.

### Other sister sites (AZ, CO, OH, WI)
Not reviewed: there are no skill notes and no site access. The same set of drafts can be generated for
them by adding entries to `SITES` in the generator (phone, exchange, OE dates, STM legality, SHIP name and number).

---

## 4. Facts used, with sources (verify annual items each fall)

| Fact | Value | Source |
|---|---|---|
| Enhanced PTC status | Expired 12/31/2025, not restored as of Oct 2026 | Commonwealth Fund; Security Health |
| HealthCare.gov / Pennie / GCI OE | Nov 1, 2026 - Jan 15, 2027; Dec 15 for Jan 1 | obamacarefacts.com; Penn State PORH; IDOI 10/14/26 release |
| Covered California OE | Nov 1 - Jan 31 | CA skill notes |
| Repayment cap | Repealed for tax years after 2025 (OBBBA s.71305) | NATP; IRS FAQ summaries |
| 2027 ACA max OOP | $12,000 / $24,000 | CMS guidance 1/29/2026 via Baldwin, Hylant |
| 2027 HSA | $4,500 / $9,000; HDHP min deductible $1,750 / $3,500 | Rev. Proc. 2026-24 |
| 2027 Part D | OOP cap $2,400; deductible $700 | CMS CY2027 Rate Announcement (4/6/2026) |
| AEP / MA OEP | Oct 15 - Dec 7; Jan 1 - Mar 31 | CMS |
| STM federal | 2024 rule (3/4 months) on books; non-enforcement statement 8/7/2025 | DOL statement |
| IL STM | Banned from 1/1/2025 | healthinsurance.org; IL 2024 legislation |
| FL STM | <12 months initial, up to 36 months total by statute | healthinsurance.org |
| FL early refills | 30-day refill when a hurricane warning / state of emergency is in place (s. 252.358 F.S.) | FLOIR notices |
| Disaster SEPs | HealthCare.gov: 60 days after the FEMA incident period; Medicare: FEMA SEP for MA/Part D | CMS guidance |
| Indiana HIP work requirements | Start 1/1/2027; 80 hrs or $580/month; 3-month lookback | in.gov/fssa/hip; Mirror Indy |
| PTC bar after work-requirement loss | OBBBA s.71119 | NHeLP / analyses |
| IN STM | 364-day initial, 36 months total, $2M minimum benefit | healthinsurance.org; IDOI Bulletin 244 |
| IL Medigap birthday rule | 45 days from birthday, ages 65-75, equal or lesser benefits, current insurer or an affiliate | P.A. 102-0142; NAIC chart. Same insurer or an affiliate (confirmed by Ryan) |

**Not confirmed, and deliberately left out:** a reported 2026 rename of ICHRA to "CHOICE Arrangement"
(only one source), and 2027 Part B premium and deductibles (CMS usually announces these in mid-November).
The AEP draft has an `ANNUAL UPDATE` placeholder for them.

## 5. Publishing checklist (per page)

1. Confirm no existing page covers the topic (search `status=any`).
2. Create as **draft**, set the page title to the H1 shown in the file header, and set layout `et_no_sidebar`.
3. Paste the file body into a Code module (TX, IL, FL, CA) or into the cloned template's content area (PA).
4. Preview: one H1, the FAQ toggles open, the phone links dial, and the "Have an Agent Call Me" CTA opens the site's contact page: `/contact/` on PA (existing page 19), `/contact-us/` everywhere else.
5. Paste the SEO title and meta description into Yoast by hand. Yoast fields aren't REST-writable.
6. Publish, add to the correct menu parent (see the "Suggested parent" line in the header), and request indexing in GSC.
7. The drafts cross-link: OE links to no-subsidy, which links to AEP, hospital indemnity, CI and STM. Publish them as a set, or remove links to pages that aren't live yet.
