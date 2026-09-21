# Competition Planner

The planner is a static page at `docs/planner.html`. Open it from the home page hamburger menu (**Competition Planner**), from articles, or at `/planner.html`. The page uses the shared site theme. Shared filters sit above **Map** and **Calendar** tabs; those filters apply to the map, the month calendar, and the list. Listings are for discovery, not endorsement. No framework, backend, or student-record rebuild is required.

## Review without deploying

This feature is on `feature/competition-planner-review`. GitHub Pages serves `main` from `/docs`, so pushing this branch does not update mathintegrity.org. Do not merge into `main` until ready to publish.

Collaborators can preview locally:

```sh
git fetch origin
git switch --track origin/feature/competition-planner-review
python3 -m http.server 8765 --directory docs
```

Open `http://localhost:8765/planner.html`, or `index.html` and use the menu link. `#map` and `#calendar` select the tab. PDF export downloads a file directly and includes the watchlist; ICS exports confirmed fixed dates for calendar imports.

Validate with `node --test tests/*.test.cjs` and `python3 scripts/build_planner_data.py --check`.

## Filters

All of these sit above the tabs and apply to every view:

- Starting point (`ZIP`, city + ZIP, or a full street address) and a mile radius (any distance, presets, or custom). Distance uses straight-line miles between the origin and a campus pin. No origin means unfiltered browsing.
- **Grade:** Middle School and lower, High School, or All.
- **Dates:** Upcoming (past end dates are hidden; unannounced dates stay) or All dates.
- **My Calendar** (saved events only) and **Show contests with no map pin** (local/assigned/unverified hosts).
- **Reset filters** restores the defaults, including Upcoming and All grades.

There is no search box. Calendar does not have a separate location form.

## Map

The Map tab is a US-only SVG map (`planner-map.js`) using locally bundled D3 7.9.0 and topojson-client 3.1.0 to render `docs/us-states.json` (us-atlas 3.0.1). The Albers USA projection shows 50 states plus DC and relocates Alaska and Hawaii into insets; Alaska uses a reduced scale. Library and dataset licenses are in `docs/vendor/`. No Google basemap is created.

Scroll or pinch to zoom, drag to pan, or use + / − and **Reset view**. With the map focused, +/− zoom, arrow keys pan, and Home or 0 reset. Button zoom animates unless reduced motion is enabled. Click a circle for name, date, registration deadline, city, and website; click it again, use close, or press Escape to dismiss. Map tips live in the **i** popover. Purple is a typical competition; blue means results are in this database. Pink is girls-only. A gold ring means the event is on your schedule. Teal is your starting point. Multiple contests at the same coordinates share a marker.

## Calendar and list

The Calendar tab has a month grid (default) and a paginated list (10 events per page, controls above and below). Saved events can be exported as PDF or `.ics`. `.ics` includes only fixed, non-tentative dates as all-day events with an exclusive end date. Testing windows and unknown dates remain on the watchlist. Event times must be obtained from organizers.

## Starting-location lookup

ZIP and ZIP+4 searches use the first five digits against `docs/us-zip-locations.json`, derived from GeoNames' US postal extract (downloaded 2026-09-08; CC BY 4.0; attribution shown in the UI). City + state + ZIP with no street also uses that ZIP table. Full street addresses are submitted to the US Census oneline geocoder using its supported JSONP endpoint, with timeout/error handling. Census positions are approximate interpolations, not guaranteed building entrances. If an address cannot be matched, try its ZIP code.

Google Maps JavaScript and Routes API are not loaded. No API key is needed. External Google Maps search and driving-directions links open only when clicked. Starting coordinates stay in this browser (`localStorage` key `math-competition-planner-v1`, with saved event IDs). They are never sent to this site's server or stored in the URL. Census receives street-address lookups. Geocoder tests use local data and simulated responses; they do not submit personal addresses or contact Google.

## Maintain the catalog

Edit `database/competition_events.json`, then run `scripts/build_planner_data.py` and commit the generated `docs/competition_events.json`. Do not add empty rankings to the historical student-results database. `recordSlugs` connects event families to the existing results; subject rounds are grouped into a single trip. The validator checks every existing result competition is represented.

Each event has:

- A stable `id` (saved schedules and calendar UIDs depend on it), title, official URL, eligibility summary, and notes.
- `startDate`/`endDate`: inclusive `YYYY-MM-DD` dates, or both `null`.
- `dateKind`: `fixed`, `window` (host chooses a session), or `unannounced`.
- `mode`: `campus`, `local` (local, variable, or assigned host), or `online`.
- A campus `location` with manually curated approximate coordinates, or `null` when the host is unverified, variable, or online. `precision: previous-campus` visibly warns that next-edition venue details need reconfirmation. No organizer headquarters are used as contest venues.
- `sources` and `checkedOn`: official source links and the review date. A null review date explicitly marks entries retained from the existing records database where the next edition needs verification.
- An optional `registrationDeadline`, only when specifically verified for this edition.

Never infer next year's date from last year's calendar. Keep published administration windows as windows, not multi-day attendance commitments. When a new edition is announced, create an edition-specific ID if the old event should remain available in saved schedules.

Initial additions beyond the results catalog include AMC 8, AMC 10/12 A and B, AIME, MATHCOUNTS chapter/state rounds, Purple Comet, the five MOEMS rounds, Berkeley's online and middle-school editions, mathleague.org middle/high school programs, and MathWorks Math Modeling Challenge. Online-only editions are excluded from the planner (see below). This is a curated directory, not an exhaustive feed of every local contest.

## Behavior and limitations

- Campus pins are approximate reference points, not room/building check-in locations. Confirm the exact venue with the organizer.
- Local/assigned venues and events with no verified host stay in the list without map pins and cannot be distance-filtered until an actual host is known. A national final listing is not a claim that it is held locally.
- Saved schedules show fixed-date overlaps and the HMMT November/February same-season restriction. They do not guarantee eligibility, admission, available seats, or feasible travel between consecutive events.
- Distance labels are straight-line miles. Traffic, road networks, terrain, islands, ferries, and stops are not modeled.
- No student records are loaded by the planner.

## Tests

Run all planner tests with `node --test tests/*.test.cjs`:

- `tests/planner.test.cjs` — `planner-core.js` filters (dates, miles, grade, saved/local), conflicts, and ICS export.
- `tests/planner-map.test.cjs` — US projection coverage for states and catalog campuses.
- `tests/planner-location.test.cjs` — ZIP and Census geocoder behavior with local/simulated responses.
- `tests/planner-catalog.test.cjs` — in-person catalog coverage and deadline labels.

There is no CI job for these tests; run them before merging planner changes.

## Expanded in-person catalog and database coverage

The September 8 expansion adds 59 entries from the approved candidate list, including separate seasonal school contests and the in-person components of hybrid programs. No new online-only programs were imported. `candidateNumber` traces additions to `COMPETITION_CANDIDATES.md`. Dates and deadlines are sourced, never advanced from older editions. `registrationNote` explains school ordering deadlines or qualification requirements. A null deadline renders an explicit “Not announced” message. `dateTentative` dates are labeled and are not exported to calendars.

`recordSlugs` links planner programs to the historical results catalog in `database/contests/contests.csv`. Adding a planner event alone does not imply results coverage. Co-located programs with different gender/coverage categories get separate dots.

New host-area locations use GeoNames postal coordinates (`city` or `previous-city` precision); these are approximate, not building entrances. School-administered programs and events with no verified host remain in the list without map pins.

## In-person catalog scope

The planner excludes all online-only editions, including BMT Online, Purple Comet, HMIC, and MathWorks Math Modeling Challenge. In-person editions and local/assigned testing hosts remain. Historical results are unchanged; `excludedOnlineRecordSlugs` records online-only result families intentionally omitted from the planner.
