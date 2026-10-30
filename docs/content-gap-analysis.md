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
- Medicare phone line is still "confirm with Ryan" in the skill. The drafts use the main number until that's confirmed.

### Illinois (ilhealthagents.com)
- **Illinois Medigap Birthday Rule** page. This is a state-specific ranking opportunity (CA already ranks on its own birthday rule content). Draft: `drafts/il/medicare-supplement-birthday-rule.html`.
  **Has a VERIFY block.** Sources disagree on whether the switch must stay with the current insurer. Check 215 ILCS 5/363 and fix the marked paragraph before publishing.
- Get Covered Illinois (Illinois's own marketplace since PY2026) explainer: the OE page covers dates. A standalone "Get Covered Illinois vs. HealthCare.gov" page is a further opportunity.
- ICHRA page. Draft included.

### Florida (floridahealthagents.com)
- Existing GSC problems (64 404s, 206 crawled-not-indexed, noindex fixed 8/20/26) mean new pages should go out alongside fixes for thin carrier pages. Strong pages on supplemental, AEP and OE topics give Google something worth indexing.
- STM page (FL law allows up to 36 months total). Draft included.
- ICHRA page. Draft included.
- Florida is the largest Medicare market of the five. Next opportunities: a "Medicare Advantage vs Medigap in Florida" page and county pages (Miami-Dade, Broward, Palm Beach, Hillsborough, Orange). Not drafted.

### Pennsylvania (pahealthagents.com)
- Group carrier pages exist for Aetna, Cigna, Geisinger, UHC and Capital Blue Cross. **Missing: Highmark, Independence Blue Cross and UPMC Health Plan.** These are three of the largest group carriers in the state. Clone the Geisinger group page using the PA skill method.
- Individual/Pennie carrier pages: confirm which exist. Ambetter Health (PA Health & Wellness), Oscar, Highmark, IBX/AmeriHealth Caring and UPMC are the main 2027 Pennie carriers. Verify the 2027 list on pennie.com.
- Pennie Certified Broker logo: still waiting on the licensed files from Pennie External Affairs.
- PA pages use the baked-in header/footer template. The drafts here are content blocks, so drop them into a cloned page's content area.

### California (californiahealthagents.com)
- The site is already broad (group section, HSA, birthday rule, dental, travel, pet). Its gaps are supplemental and final expense, which are drafted.
- The OE draft uses Covered CA dates (Nov 1 - Jan 31; Dec 31 for Jan 1 start) and includes the CA mandate and HSA non-conformity.
- Do not add STM. The no-subsidy draft explains that it's banned.

### Sister sites (AZ, CO, IN, OH, WI)
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
| IL Medigap birthday rule | 45 days from birthday, ages 65-75, equal or lesser benefits | P.A. 102-0142; NAIC chart (**same vs any insurer unresolved**) |

**Not confirmed, and deliberately left out:** a reported 2026 rename of ICHRA to "CHOICE Arrangement"
(only one source), and 2027 Part B premium and deductibles (CMS usually announces these in mid-November).
The AEP draft has an `ANNUAL UPDATE` placeholder for them.

## 5. Publishing checklist (per page)

1. Confirm no existing page covers the topic (search `status=any`).
2. Create as **draft**, set the page title to the H1 shown in the file header, and set layout `et_no_sidebar`.
3. Paste the file body into a Code module (TX, IL, FL, CA) or into the cloned template's content area (PA).
4. Preview: one H1, the FAQ toggles open, the phone links dial, and the CTAs point at the right contact slug (marked `VERIFY` in the generator for FL, PA and CA).
5. Paste the SEO title and meta description into Yoast by hand. Yoast fields aren't REST-writable.
6. Publish, add to the correct menu parent (see the "Suggested parent" line in the header), and request indexing in GSC.
7. The drafts cross-link: OE links to no-subsidy, which links to AEP, hospital indemnity, CI and STM. Publish them as a set, or remove links to pages that aren't live yet.
