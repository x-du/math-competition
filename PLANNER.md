# Competition planner

The planner is a static addition to the existing GitHub Pages site at `docs/planner.html`. The boxed Competition map link sits below Announcements on the home page. The planner uses the shared site theme, opens with a large map and circular campus markers, and places travel settings immediately beneath it. Marker popups show the name, date, registration deadline, city/state, official website, and results-database coverage. Clicking the same marker, the map background, or the website link closes the popup. Schedule controls remain in the list below. No framework, backend, or student-record rebuild is required. The public website has not been deployed by this change.

## Review without deploying

This feature is on `feature/competition-planner-review`. GitHub Pages serves `main` from `/docs`, so pushing this branch does not update mathintegrity.org. Do not merge into `main` until ready to publish.

Collaborators can preview locally:

```sh
git fetch origin
git switch --track origin/feature/competition-planner-review
python3 -m http.server 8765 --directory docs
```

Open `http://localhost:8765/index.html` for the silver map button and small first-visit announcement beside the map button, or `/planner.html` for the map. The announcement appears once per browser storage profile; clearing the `mathintegrity-planner-welcome-v3` localStorage entry shows it again. The committed Google API key is empty. No key is needed for the current rough estimates. PDF export downloads a file directly and includes the watchlist; ICS exports confirmed fixed dates for calendar imports.

## Free travel estimates

Google Maps JavaScript and Routes API are no longer loaded or called. No API key or paid routing service is needed. ZIP lookup is local; street addresses use the US Census geocoder. Starting locations remain in memory. External directions links only open Google Maps when clicked.

Driving estimates use geographic straight-line miles multiplied by 1.3, then divided by 50 mph with a 15-minute minimum. This is an explicit planning assumption, not calibrated road routing. Times display in roughly 15-minute increments. Traffic, road networks, terrain, islands, ferries, and stops are not modeled. Estimates are disabled outside the contiguous-US coordinate bounds; willing-to-fly mode still includes those destinations. Local-host events remain visible for any origin.

Validate with `node --test tests/*.test.cjs` and `python3 scripts/build_planner_data.py --check`. Serve with `python3 -m http.server 8765 --directory docs` and open `/planner.html`.

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

Initial additions beyond the results catalog include AMC 8, AMC 10/12 A and B, AIME, MATHCOUNTS chapter/state rounds, Purple Comet, the five MOEMS rounds, Berkeley's online and middle-school editions, mathleague.org middle/high school programs, and MathWorks Math Modeling Challenge. This is a curated directory, not an exhaustive feed of every local contest.

## Behavior and limitations

- Drive-only campus results require a successfully computed route within the selected one-way time limit. Failed routes are excluded, never replaced with straight-line driving estimates. No starting point means unfiltered browsing.
- Local/assigned venues and online events are listed separately in the interface and cannot be distance-filtered until an actual host is known. A national final listing is not a claim that it is held locally.
- Campus pins are approximate reference points, not room/building check-in locations. Multiple contests at the same coordinates share a marker with a list of events.
- Saved schedules show fixed-date overlaps and the HMMT November/February same-season restriction. They do not guarantee eligibility, admission, available seats, or feasible travel between consecutive events.
- `.ics` export includes only fixed dates as all-day events with an exclusive end date. Testing windows and unknown dates remain on the watchlist. Event times must be obtained from organizers.
- Only selected event IDs are kept in browser storage. User-entered locations and route responses remain in memory and are never sent to this site's server or stored in the URL. Google receives lookup/routing requests. No student records are loaded by the planner.

## US-only map display

`planner-map.js` uses locally bundled D3 7.9.0 and topojson-client 3.1.0 to render `docs/us-states.json` (us-atlas 3.0.1). The Albers USA projection shows 50 states plus DC and relocates Alaska and Hawaii into insets; Alaska uses a reduced scale. Library and dataset licenses are in `docs/vendor/`. No Google basemap is created. Test projection coverage with `node --test tests/planner-map.test.cjs`.

Scroll or pinch to zoom, drag to pan, or use the larger zoom buttons. With the map focused, +/− zoom, arrow keys pan, and Home or 0 reset. US overview also resets the view. Button zoom animates unless reduced motion is enabled. Competition coordinates come from the curated catalog. Girls-only dots are pink; mixed campuses use adjacent dots. Popups contain name, date, registration deadline, city/state, website, and a results-database badge when applicable and close on repeated clicks, background clicks, or Escape.

Google geocoding and route estimates are displayed as attributed text in the travel controls and competition list, not as Google geometry on the custom map. The starting point is obtained independently from US Census address lookup or the local GeoNames ZIP dataset, then plotted as an approximate turquoise marker. It is kept only in memory. Your existing Google key still supports these controls. Map and travel loading fail independently.

### Starting-location lookup and state labels

Small postal state abbreviations are drawn on every state. The turquoise origin dot remains visible even when competition filters produce no results, moves correctly during zoom/resize, and clears when the starting address is edited or filters reset.

ZIP and ZIP+4 searches use the first five digits against `docs/us-zip-locations.json`, derived from GeoNames' US postal extract (downloaded 2026-09-08; CC BY 4.0; attribution shown in the UI). These coordinates are approximate ZIP locations. Full street addresses are submitted to the US Census oneline geocoder using its supported JSONP endpoint, with timeout/error handling. Census positions are approximate interpolations, not guaranteed building entrances. If an address cannot be matched, try its ZIP code. Google receives starting coordinates for driving calculations, but is no longer used for geocoding. No additional key is required. Location disclosure and attribution are displayed beside the search form.

Tests: `node --test tests/*.test.cjs`. Geocoder tests use local data and simulated responses; they do not submit personal addresses or contact Google.


### Expanded in-person catalog and database coverage

The September 8 expansion adds 59 entries from the approved candidate list, including separate seasonal school contests and the in-person components of hybrid programs. No new online-only programs were imported. `candidateNumber` traces additions to `COMPETITION_CANDIDATES.md`. Dates and deadlines are sourced, never advanced from older editions. `registrationNote` explains school ordering deadlines or qualification requirements. A null deadline renders an explicit “Not announced” message. `dateTentative` dates are labeled and are not exported to calendars.

`recordSlugs` links planner programs to the historical results catalog in `database/contests/contests.csv`. Purple map dots, card borders and “Results in database” badges indicate coverage. Adding a planner event alone does not imply results coverage. Pink gender-restricted dots get a purple ring when covered. Saved events use a gold outer ring. Co-located programs with different gender/coverage categories get separate dots.

New host-area locations use GeoNames postal coordinates (`city` or `previous-city` precision); these are approximate, not building entrances. School-administered programs and events with no verified host remain in the list without map pins. Confirm venues before travel; routes to host areas are estimates.

## In-person catalog scope

The planner excludes all online-only editions, including BMT Online, Purple Comet, HMIC, and MathWorks Math Modeling Challenge. In-person editions and local/assigned testing hosts remain. Historical results are unchanged; `excludedOnlineRecordSlugs` records online-only result families intentionally omitted from the planner.
