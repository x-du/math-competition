/* Static Google Maps planner: no student records or addresses are persisted. */
(async function () {
  'use strict';
  const C = window.PlannerCore;
  const $ = id => document.getElementById(id);
  const storageKey = 'math-competition-planner-v1';
  const themeToggle = $('planner-theme-toggle');
  function updateThemeButton() {
    const light = document.documentElement.dataset.theme === 'light';
    themeToggle.textContent = light ? '☾' : '☼';
    themeToggle.setAttribute('aria-label', light ? 'Switch to dark mode' : 'Switch to light mode');
    themeToggle.title = light ? 'Dark mode' : 'Light mode';
  }
  themeToggle.addEventListener('click', () => {
    const next = document.documentElement.dataset.theme === 'light' ? 'dark' : 'light';
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem('theme', next); } catch (_) {}
    updateThemeButton();
  });
  updateThemeButton();
  const state = { events: [], saved: new Set(), origin: null, routes: new Map(), markers: [], home: null, map: null, mapsReady: false, generation: 0, busy: false };

  const node = (tag, className, text) => { const e = document.createElement(tag); if (className) e.className = className; if (text != null) e.textContent = text; return e; };
  function link(text, url) { const a = node('a', '', text); a.href = url; a.target = '_blank'; a.rel = 'noopener noreferrer'; return a; }
  function button(text, action, cls = 'text-button') { const b = node('button', cls, text); b.type = 'button'; b.addEventListener('click', action); return b; }
  function options() {
    return { today: C.todayISO(), query: $('search').value, date: $('date-filter').value, includeLocal: $('include-local').checked, savedOnly: $('saved-only').checked, saved: state.saved, origin: state.origin, routes: state.routes, mode: document.querySelector('[name=travel]:checked').value, limit: Number($('drive-limit').value) };
  }
  function travel(event) { const o = options(); return C.travelInfo(event, state.origin, state.routes, o.mode, o.limit); }
  function persist() {
    try { localStorage.setItem(storageKey, JSON.stringify([...state.saved])); }
    catch { $('calendar-note').textContent = 'Browser storage is unavailable. This schedule lasts for this visit; export fixed dates to keep them.'; }
  }
  function toggle(event) {
    if (state.saved.has(event.id)) state.saved.delete(event.id); else state.saved.add(event.id);
    persist(); render();
    // Restore focus after rebuilding the card list for keyboard users.
    const target = document.querySelector(`[data-save-id="${event.id}"]`);
    if (target) target.focus({ preventScroll: true });
  }
  function mapsURL(event) {
    const params = new URLSearchParams({ api: '1', query: event.location.venue + ', ' + event.location.city });
    return 'https://www.google.com/maps/search/?' + params;
  }
  function directionsURL(event) {
    const params = new URLSearchParams({ api: '1', destination: event.location.venue + ', ' + event.location.city, travelmode: 'driving' });
    if (state.origin) params.set('origin', `${state.origin.lat},${state.origin.lng}`);
    return 'https://www.google.com/maps/dir/?' + params;
  }
  function renderCard(event) {
    const saved = state.saved.has(event.id), info = travel(event);
    const card = node('article', 'contest' + (saved ? ' is-saved' : '')); card.id = 'event-' + event.id; card.tabIndex = -1;
    const top = node('div', 'contest-top');
    const tile = node('div', 'date-tile'); tile.setAttribute('aria-hidden', 'true');
    tile.append(node('span', '', event.startDate ? new Date(event.startDate + 'T12:00:00Z').toLocaleDateString('en-US', { month: 'short', timeZone: 'UTC' }) : 'NEXT'), node('strong', '', event.startDate ? String(Number(event.startDate.slice(-2))) : '—'));
    const heading = node('div', 'contest-heading'); heading.append(node('h3', '', event.name), node('p', 'place', event.location ? event.location.city + ' · ' + event.location.venue : event.mode === 'online' ? 'Online' : 'Local / assigned host'));
    const save = button(saved ? '✓' : '+', () => toggle(event), 'save-button'); save.dataset.saveId = event.id; save.setAttribute('aria-pressed', String(saved)); save.setAttribute('aria-label', `${saved ? 'Remove' : 'Add'} ${event.name} ${saved ? 'from' : 'to'} my schedule`);
    top.append(tile, heading, save); card.append(top);
    const badges = node('div', 'badges'); badges.append(node('span', 'badge', event.grades), node('span', 'badge travel', info.label));
    if (event.recordSlugs.length) { card.classList.add('has-records'); badges.append(node('span', 'badge database-badge', 'Results in database')); }
    if (!event.startDate) badges.append(node('span', 'badge warning', 'Date unannounced'));
    if (event.dateTentative) badges.append(node('span', 'badge warning', 'Tentative date'));
    if (event.dateKind === 'window') badges.append(node('span', 'badge warning', 'Testing window'));
    if (event.location?.precision === 'previous-campus') badges.append(node('span', 'badge warning', 'Previous campus · reconfirm'));
    if (event.location?.precision?.includes('city')) badges.append(node('span', 'badge warning', event.location.precision === 'previous-city' ? 'Previous host area · reconfirm' : 'Approximate host area'));
    card.append(badges, node('p', 'contest-notes', C.dateLabel(event)), node('p', 'contest-notes', event.notes));
    card.append(node('p', 'contest-notes', C.deadlineLabel(event) + (event.registrationDeadline && event.registrationDeadline < C.todayISO() ? ' · Passed' : '')));
    const links = node('div', 'contest-links'); links.append(link('Official details ↗', event.url));
    if (event.location) {
      links.append(link('Google Maps ↗', mapsURL(event)));
      if (state.customMap) links.append(button('Show pin', () => focusPin(event)));
      if (info.kind === 'drive') links.append(link('Driving directions ↗', directionsURL(event)));
    }
    card.append(links);
    const source = node('p', 'source-note', event.checkedOn ? `Source checked ${event.checkedOn}` : 'From the records database · next edition needs verification');
    if (event.recordSlugs.length) source.append(document.createTextNode(' · Results in database'));
    // Date-specific sources (e.g. HMMT deadlines) remain directly reviewable.
    for (const url of event.sources.filter(url => url !== event.url)) source.append(document.createTextNode(' · '), link('Source', url));
    card.append(source); return card;
  }
  function renderSchedule() {
    const selected = state.events.filter(e => state.saved.has(e.id)).sort(C.compareEvents);
    $('saved-count').textContent = selected.length;
    $('export-pdf').disabled = !selected.length;
    $('export-calendar').disabled = !selected.some(e => e.dateKind === 'fixed' && !e.dateTentative);
    const list = $('schedule-list'); list.replaceChildren();
    if (!selected.length) list.append(node('p', 'empty', 'Add competitions to see your season take shape.'));
    for (const event of selected) {
      const row = node('article', 'schedule-item');
      const remove = button('Remove', () => { toggle(event); $('schedule-title').tabIndex = -1; $('schedule-title').focus({ preventScroll: true }); }); remove.setAttribute('aria-label', `Remove ${event.name} from schedule`);
      row.append(remove, node('p', 'schedule-date', C.dateLabel(event)), node('h3', '', event.name), node('p', '', event.location?.city || (event.mode === 'online' ? 'Online' : 'Confirm testing host')));
      row.append(node('p', '', C.deadlineLabel(event) + (event.registrationDeadline && event.registrationDeadline < C.todayISO() ? ' · Passed' : '')));
      const website = node('p', 'schedule-website'); website.append(link('Official website ↗', event.url)); row.append(website);
      if (event.endDate && event.endDate < C.todayISO()) row.append(node('p', 'conflict', 'This event has passed.'));
      const info = travel(event);
      if (state.origin && event.location) row.append(node('p', info.reachable ? '' : 'conflict', info.label));
      if (event.dateTentative) row.append(node('p', '', 'Watchlist · waiting for date confirmation'));
      if (event.dateKind !== 'fixed') row.append(node('p', '', 'Watchlist · ' + (event.dateKind === 'window' ? 'choose a session with your host' : 'waiting for a date')));
      for (const message of C.conflicts(event, selected)) row.append(node('p', 'conflict', message));
      list.append(row);
    }
  }
  function render() {
    const visible = C.filterEvents(state.events, options());
    $('result-count').textContent = visible.length;
    const list = $('competition-list'); list.replaceChildren();
    let group = '';
    for (const event of visible) {
      const key = event.startDate ? new Date(event.startDate + 'T12:00:00Z').toLocaleDateString('en-US', { month: 'long', year: 'numeric', timeZone: 'UTC' }) : 'Dates to come';
      if (key !== group) { list.append(node('h3', 'group-heading', key)); group = key; }
      list.append(renderCard(event));
    }
    if (!visible.length) list.append(node('p', 'empty', 'No competitions match these filters. Try a longer drive, include local and online events, or reset filters.'));
    const o = options();
    const excluded = state.origin && o.mode === 'drive' ? state.events.filter(e => e.location && !travel(e).reachable).length : 0;
    $('results-note').textContent = (excluded ? `${excluded} campus events are outside your driving limit or have no verified route. ` : '') + 'Campus pins are approximate; confirm the venue before booking. Local hosts are not distance-filtered.';
    renderSchedule(); renderMarkers(visible);
  }
  function closePin() {
    state.activeMarker?.setAttribute('aria-expanded', 'false');
    state.activeMarker = null;
    if ($('us-map-popup')) $('us-map-popup').hidden = true;
  }
  function renderMarkers(visible) {
    if (!state.customMap) return;
    closePin(); state.customMap.setEvents(visible, state.saved, state.origin);
  }
  function openPin(marker, events) {
    if (state.activeMarker === marker) { closePin(); return; }
    closePin();
    const content = $('us-map-popup'); content.replaceChildren();
    for (const event of events) {
      const detail = node('section', 'pin-event');
      const website = link('Official website ↗', event.url);
      website.addEventListener('click', closePin);
      detail.append(node('h3', '', event.name));
      if (event.recordSlugs.length) detail.append(node('span', 'badge database-badge', 'Results in database'));
      detail.append(node('p', 'pin-date', 'Date: ' + C.dateLabel(event)), node('p', 'pin-deadline', C.deadlineLabel(event) + (event.registrationDeadline && event.registrationDeadline < C.todayISO() ? ' · Passed' : '')), node('p', 'pin-location', event.location.city + (event.location.precision?.startsWith('previous-') ? ' · Previous host' : '')), website);
      content.append(detail);
    }
    state.activeMarker = marker; marker.setAttribute('aria-expanded', 'true'); content.hidden = false;
  }
  function showUS() { closePin(); state.customMap?.reset(); }
  function focusPin(event) { state.customMap?.focus(event.id); $('map').scrollIntoView({ block: 'center' }); }
  function fitMap() { showUS(); }
  async function loadCustomMap() {
    try {
      const response = await timeout(fetch('us-states.json'));
      if (!response.ok) throw new Error('boundaries');
      const topology = await response.json();
      const features = topojson.feature(topology, topology.objects.states);
      features.features = features.features.filter(f => Number(f.id) <= 56);
      $('map').hidden = false; $('map-message').hidden = true;
      state.customMap = new CompetitionUSMap($('map'), features, openPin, closePin);
      const popup = node('div', 'info-window us-map-popup'); popup.id = 'us-map-popup'; popup.hidden = true;
      popup.setAttribute('role', 'region'); popup.setAttribute('aria-label', 'Competition details');
      $('map').append(popup);
      $('map').addEventListener('keydown', event => { if (event.key === 'Escape') { const marker = state.activeMarker; closePin(); marker?.focus(); } });
      $('us-view').addEventListener('click', showUS);
      $('zoom-in').addEventListener('click', () => state.customMap.zoomBy(1.6));
      $('zoom-out').addEventListener('click', () => state.customMap.zoomBy(1 / 1.6));
      for (const id of ['us-view', 'fit-map', 'zoom-in', 'zoom-out']) $(id).disabled = false;
      render();
    } catch {
      $('map').hidden = true; $('map-message').hidden = false;
      $('map-message').querySelector('p').textContent = 'The US map could not load. Refresh to try again; the competition list is still available.';
    }
  }
  function timeout(promise, ms = 20000) {
    let timer;
    return Promise.race([promise, new Promise((_, reject) => { timer = setTimeout(() => reject(new Error('timeout')), ms); })]).finally(() => clearTimeout(timer));
  }
  function setBusy(busy) { state.busy = busy; $('find-button').disabled = busy; $('find-button').textContent = busy ? 'Finding your route…' : 'Find competitions ↗'; }
  async function chooseOrigin(result, generation) {
    if (generation !== state.generation) return;
    $('location-choices').hidden = true;
    state.origin = result.position; state.routes.clear();
    $('origin').value = result.label;
    $('travel-status').textContent = 'Starting from ' + result.label + '. Checking driving routes…';
    render(); fitMap();
    try {
      if (!state.mapsReady) {
        $('travel-status').textContent = 'Starting from ' + result.label + ' (approximate). Google driving estimates are unavailable; choose “Willing to fly” to browse destinations.';
        return;
      }
      const { RouteMatrix } = await timeout(google.maps.importLibrary('routes'));
      const destinations = [...new Map(state.events.filter(e => e.location).map(e => [C.routeKey(e.location), e.location])).values()];
      // Stay under the API's destination limits as the catalog grows.
      for (let offset = 0; offset < destinations.length; offset += 25) {
        if (generation !== state.generation) return;
        const batch = destinations.slice(offset, offset + 25);
        const { matrix } = await timeout(RouteMatrix.computeRouteMatrix({ origins: [state.origin], destinations: batch.map(l => ({ lat: l.lat, lng: l.lng })), travelMode: 'DRIVING', routingPreference: 'TRAFFIC_UNAWARE', fields: ['condition', 'durationMillis', 'distanceMeters'] }));
        if (generation !== state.generation) return;
        batch.forEach((destination, i) => {
          const item = matrix.rows[0]?.items[i];
          state.routes.set(C.routeKey(destination), item && !item.error && item.condition === 'ROUTE_EXISTS' && Number.isFinite(item.durationMillis) && Number.isFinite(item.distanceMeters) ? { status: 'ok', hours: item.durationMillis / 3600000, miles: item.distanceMeters / 1609.344 } : { status: item?.condition === 'ROUTE_NOT_FOUND' ? 'no-route' : 'error' });
        });
      }
      const errors = [...state.routes.values()].filter(r => r.status === 'error').length;
      $('travel-status').textContent = `Starting from ${result.label} (approximate). Driving times exclude traffic and stops; some destinations are approximate host areas.` + (errors ? ` ${errors} routes could not be verified.` : '') + ' Flying shows destinations to consider, not available flights.';
    } catch {
      if (generation !== state.generation) return;
      $('travel-status').textContent = 'Your starting point was found, but some driving routes could not be checked. Drive-only results exclude unverified routes. Retry the search, or browse destinations with “Willing to fly”.';
    } finally {
      if (generation === state.generation) { setBusy(false); render(); fitMap(); }
    }
  }
  $('travel-form').addEventListener('submit', async event => {
    event.preventDefault();
    const address = $('origin').value.trim(); if (!address) return;
    const generation = ++state.generation; setBusy(true); $('location-choices').hidden = true;
    $('travel-status').textContent = 'Finding your starting point…';
    try {
      const results = await timeout(PlannerGeocoder.lookup(address));
      if (generation !== state.generation) return;
      if (!results.length) throw new Error('no-results');
      if (results.length > 1) {
        const choices = $('location-choices'); choices.replaceChildren(); choices.hidden = false;
        for (const result of results.slice(0, 5)) choices.append(button(result.label, () => { setBusy(true); chooseOrigin(result, generation); }));
        $('travel-status').textContent = 'Confirm the matching location below, or enter a more specific address.'; setBusy(false);
      } else await chooseOrigin(results[0], generation);
    } catch {
      if (generation !== state.generation) return;
      $('travel-status').textContent = 'Could not locate that address. Try a ZIP code or a full street address, city, and state. Check your connection if the problem continues.';
      setBusy(false);
    }
  });
  // Editing an address cancels in-flight work and removes stale reachability claims.
  $('origin').addEventListener('input', () => {
    state.generation++; state.origin = null; state.routes.clear(); $('location-choices').hidden = true; setBusy(false);
    $('travel-status').textContent = 'Submit your starting point to check travel. Currently showing all locations.'; render();
  });
  for (const id of ['search', 'date-filter', 'include-local', 'saved-only', 'drive-limit']) $(id).addEventListener(id === 'search' ? 'input' : 'change', render);
  document.querySelectorAll('[name=travel]').forEach(input => input.addEventListener('change', render));
  $('fit-map').addEventListener('click', fitMap);
  $('reset-filters').addEventListener('click', () => {
    state.generation++; state.origin = null; state.routes.clear(); $('origin').value = ''; $('search').value = ''; $('date-filter').value = 'upcoming'; $('include-local').checked = true; $('saved-only').checked = false; $('drive-limit').value = '4'; document.querySelector('[name=travel][value=drive]').checked = true; $('location-choices').hidden = true; setBusy(false);
    $('travel-status').textContent = 'Showing all locations. Enter your starting point to check driving times.'; render(); fitMap();
  });
  $('export-pdf').addEventListener('click', () => {
    const events = state.events.filter(e => state.saved.has(e.id));
    if (!events.length) return;
    try {
      const pdf = PlannerPDF.create(events, C, window.jspdf.jsPDF);
      const url = URL.createObjectURL(pdf.output('blob'));
      const a = node('a'); a.href = url; a.download = 'math-competition-schedule.pdf';
      document.body.append(a); a.click(); a.remove();
      setTimeout(() => URL.revokeObjectURL(url), 60000);
      $('pdf-help').textContent = 'Your PDF is ready. Check your browser downloads for math-competition-schedule.pdf.';
    } catch {
      $('pdf-help').textContent = 'PDF export could not load. Refresh the page and try again.';
    }
  });
  $('export-calendar').addEventListener('click', () => {
    const events = state.events.filter(e => state.saved.has(e.id));
    const url = URL.createObjectURL(new Blob([C.calendar(events)], { type: 'text/calendar;charset=utf-8' }));
    const a = node('a'); a.href = url; a.download = 'math-competition-schedule.ics'; document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
  function mapUnavailable(message) {
    state.mapsReady = false;
    $('travel-status').textContent = message + ' The US map and schedule remain available.';
    render();
  }
  async function loadMap() {
    const config = window.COMPETITION_PLANNER_CONFIG || {};
    if (!config.googleMapsApiKey) {
      mapUnavailable('Connect Google Maps to enable driving estimates.'); return;
    }
    try {
      await timeout(new Promise((resolve, reject) => {
        window.initCompetitionMap = resolve;
        window.gm_authFailure = () => { reject(new Error('auth')); mapUnavailable('Google Maps could not authorize this site. The maintainer should check the API key, billing, and allowed website domains.'); };
        const script = document.createElement('script');
        script.src = 'https://maps.googleapis.com/maps/api/js?' + new URLSearchParams({ key: config.googleMapsApiKey, v: 'weekly', loading: 'async', callback: 'initCompetitionMap' });
        script.async = true; script.onerror = () => reject(new Error('network')); document.head.append(script);
      }));
      state.mapsReady = true;
    } catch { mapUnavailable('Google Maps could not load. Check your connection, or try again later. Competition details and your schedule are still available.'); }
  }
  try {
    const response = await timeout(fetch('competition_events.json'));
    if (!response.ok) throw new Error('catalog');
    const catalog = await response.json();
    if (!Array.isArray(catalog.events)) throw new Error('catalog');
    state.events = catalog.events;
    try {
      const saved = JSON.parse(localStorage.getItem(storageKey) || '[]');
      if (Array.isArray(saved)) state.saved = new Set(saved.filter(id => state.events.some(e => e.id === id)));
    } catch { /* A corrupt or blocked store must not prevent browsing. */ }
    $('catalog-note').textContent = `Catalog updated ${catalog.updatedOn}. Dates link to organizer sources; unannounced editions are not projected from last year. Flight availability, registration, and exact arrival times are not checked.`;
    render(); await Promise.allSettled([loadCustomMap(), loadMap()]);
  } catch {
    $('competition-list').replaceChildren(node('p', 'empty', 'The competition catalog could not load. Please refresh to try again, or use the original calendar linked below.'));
    $('map-message').querySelector('p').textContent = 'The competition catalog is unavailable. Refresh to try again.';
  }
})();
