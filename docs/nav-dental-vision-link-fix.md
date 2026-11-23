# Fix: Dental / Vision nav links on floridahealthagents.com

Audited 2026-11-23. Not applied: the site could not be edited from this session.

## Problem
"Dental Insurance" and "Vision Insurance" both link to
`https://ihealthagents.com/?banner=dental-vision`, a generic landing page on a different site.
It appears on all 86 pages in the sitemap, in two places:

| Where | How to edit |
|---|---|
| Mega menu, items 12072 (Dental Insurance) and 12073 (Vision Insurance) | wp-admin > Appearance > Menus > main menu (id 116), or `/wp/v2/menu-items/12072` and `/12073` |
| Footer "Insurance" list (two links) | Divi Theme Builder, footer layout 11953, the Code module with baked-in HTML |

## New targets (all verified HTTP 200 on 2026-11-23)
| Label | Old URL | New URL |
|---|---|---|
| Dental Insurance | `https://ihealthagents.com/?banner=dental-vision` | `/insurance-types/dental-insurance/` |
| Vision Insurance | `https://ihealthagents.com/?banner=dental-vision` | `/vsp-vision/` |

The all-ages page is used for Dental Insurance because the menu already has a separate "Senior Dental Plans (65+)" item pointing to `/senior-dental-plans/`.

## Steps
1. Menu: change the two custom links' URLs. Use site-relative paths or full `https://floridahealthagents.com/...` URLs.
2. Footer: in Theme Builder open layout 11953, edit the Code module HTML, replace the two hrefs, then Save in the builder, Exit, and press Save Changes on the Theme Builder page.
3. Purge cache (Breeze "Purge All Cache" in the admin bar).
4. Verify with a cache-busted fetch that no page contains `banner=dental-vision`:
   `curl -s "https://floridahealthagents.com/mutual-of-omaha/?x=$RANDOM" | grep -c banner=dental-vision` should print 0.

Related: the Mutual of Omaha page drafts (`drafts/fl/mutual-of-omaha*.html`) do not include the dental application URL.
