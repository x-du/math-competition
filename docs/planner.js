/* Planner UI. Schedule IDs and the last starting location are stored in this browser only. */
(async function () {
  'use strict';
  const C = window.PlannerCore;
  const $ = id => document.getElementById(id);
  const storageKey = 'math-competition-planner-v1';
  const themeToggle = $('planner-theme-toggle');
  const sunIcon = '<svg class="theme-toggle-svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32l1.41 1.41M2 12h2m16 0h2M4.93 19.07l1.41-1.41m11.32-11.32l1.41-1.41"/></svg>';
  const moonIcon = '<svg class="theme-toggle-svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
  function updateThemeButton() {
    const light = document.documentElement.dataset.theme === 'light';
    const icon = themeToggle.querySelector('.theme-toggle-icon');
    if (icon) icon.innerHTML = light ? moonIcon : sunIcon;
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
  const state = { events: [], saved: new Set(), origin: null, savedOrigin: null, markers: [], home: null, map: null, mapsReady: false, generation: 0, busy: false, tab: location.hash === '#calendar' ? 'calendar' : 'map', view: 'calendar', listPage: 1, filterKey: '', calYear: null, calMonth: null, calOpenId: null, visible: [] };
  const listPageSize = 10;

  const node = (tag, className, text) => { const e = document.createElement(tag); if (className) e.className = className; if (text != null) e.textContent = text; return e; };
  function link(text, url) { const a = node('a', '', text); a.href = url; a.target = '_blank'; a.rel = 'noopener noreferrer'; return a; }
  function button(text, action, cls = 'text-button') { const b = node('button', cls, text); b.type = 'button'; b.addEventListener('click', action); return b; }
  function options() {
    return { today: C.todayISO(), query: '', date: $('date-filter').value, grade: $('grade-filter').value, includeLocal: $('include-local').checked, savedOnly: $('saved-only').checked, saved: state.saved, origin: state.origin, limit: milesLimit() };
  }
  function milesLimit() {
    const preset = $('miles-preset').value;
    if (preset === 'custom') {
      const n = Number($('miles-limit').value);
      return Number.isFinite(n) && n > 0 ? n : Infinity;
    }
    return preset ? Number(preset) : Infinity;
  }
  function milesPhrase() {
    const n = milesLimit();
    return Number.isFinite(n) ? `${Math.round(n)} miles` : 'any distance';
  }
  function showCustomMiles(on) {
    $('miles-custom').hidden = !on;
    if (on) $('miles-limit').focus();
  }
  function applyMilesPreset() {
    const preset = $('miles-preset').value;
    showCustomMiles(preset === 'custom');
    if (preset !== 'custom') $('miles-limit').value = preset;
  }
  function onMilesChange() {
    if (state.origin) $('travel-status').textContent = 'Showing competitions within ' + milesPhrase() + ' of ' + $('origin').value + '.';
    else if ($('origin').value.trim()) lookupOrigin();
    render();
  }
  function travel(event) { const o = options(); return C.travelInfo(event, state.origin, o.limit); }
  function persist() {
    try {
      localStorage.setItem(storageKey, JSON.stringify({ saved: [...state.saved], origin: state.savedOrigin }));
    }
    catch { $('calendar-note').textContent = 'Browser storage is unavailable. This schedule lasts for this visit; export fixed dates to keep them.'; }
  }
  function readStore() {
    try {
      const raw = JSON.parse(localStorage.getItem(storageKey) || 'null');
      if (Array.isArray(raw)) return { saved: raw, origin: null };
      if (raw && typeof raw === 'object') return { saved: Array.isArray(raw.saved) ? raw.saved : [], origin: raw.origin && typeof raw.origin === 'object' ? raw.origin : null };
    } catch { /* A corrupt store must not prevent browsing. */ }
    return { saved: [], origin: null };
  }
  function originFromStore(value) {
    if (!value) return null;
    const lat = Number(value.lat), lng = Number(value.lng);
    const label = typeof value.label === 'string' ? value.label.trim().slice(0, 250) : '';
    if (!label || !Number.isFinite(lat) || !Number.isFinite(lng) || lat < -90 || lat > 90 || lng < -180 || lng > 180) return null;
    return { label, lat, lng };
  }
  function applyOrigin(origin, persistIt) {
    state.origin = origin ? { lat: origin.lat, lng: origin.lng } : null;
    state.savedOrigin = origin;
    $('origin').value = origin ? origin.label : $('origin').value;
    if (origin) $('travel-status').textContent = 'Showing competitions within ' + milesPhrase() + ' of ' + origin.label + '.';
    if (persistIt) persist();
  }
  function toggle(event) {
    if (state.saved.has(event.id)) state.saved.delete(event.id); else state.saved.add(event.id);
    persist();
    const reopenPin = state.activePinEvents;
    const reopenCal = state.calOpenId === event.id;
    render();
    if (reopenPin) {
      const entry = state.customMap?.entries?.find(e => e.events.some(ev => ev.id === event.id));
      if (entry) openPin(entry.marker, entry.events);
      return;
    }
    if (reopenCal) {
      const chip = document.querySelector(`[data-cal-id="${event.id}"]`);
      if (chip) openEventPopover(event, chip, true);
      return;
    }
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
    const heading = node('div', 'contest-heading'); heading.append(node('h3', '', event.name), node('p', 'place', event.location ? event.location.city + ' · ' + event.location.venue : event.mode === 'online' ? 'Online' : 'No map pin · confirm testing site'));
    const save = button(saved ? '✓' : '+', () => toggle(event), 'save-button'); save.dataset.saveId = event.id; save.setAttribute('aria-pressed', String(saved)); save.setAttribute('aria-label', `${saved ? 'Remove' : 'Add'} ${event.name} ${saved ? 'from' : 'to'} my schedule`);
    top.append(tile, heading, save); card.append(top);
    const badges = node('div', 'badges'); badges.append(node('span', 'badge', event.grades));
    if (info.kind !== 'browse') badges.append(node('span', 'badge travel', info.label));
    if (event.inDatabase || event.recordSlugs.length) { card.classList.add('has-records'); badges.append(node('span', 'badge database-badge', 'Results in database')); }
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
      if (state.origin) links.append(link('Driving directions ↗', directionsURL(event)));
    }
    card.append(links);
    if (saved) {
      const selected = state.events.filter(e => state.saved.has(e.id));
      for (const message of C.conflicts(event, selected)) card.append(node('p', 'conflict', message));
    }
    const source = node('p', 'source-note', event.checkedOn ? `Source checked ${event.checkedOn}` : 'From the records database · next edition needs verification');
    if (event.inDatabase || event.recordSlugs.length) source.append(document.createTextNode(' · Results in database'));
    // Date-specific sources (e.g. HMMT deadlines) remain directly reviewable.
    const official = (event.url || '').replace(/\/$/, '');
    for (const url of event.sources) {
      if (/geonames\.org/i.test(url)) continue;
      if (url.replace(/\/$/, '') === official) continue;
      source.append(document.createTextNode(' · '), link('Source', url));
    }
    card.append(source); return card;
  }
  function updateExports() {
    const selected = state.events.filter(e => state.saved.has(e.id));
    const savedOnly = $('saved-only').checked;
    $('export-pdf').hidden = !savedOnly;
    $('export-calendar').hidden = !savedOnly;
    $('export-pdf').disabled = !selected.length;
    $('export-calendar').disabled = !selected.some(e => e.dateKind === 'fixed' && !e.dateTentative);
  }
  function renderList(visible) {
    const list = $('competition-list'); list.replaceChildren();
    if (!visible.length) {
      list.append(node('p', 'empty', $('saved-only').checked ? 'Nothing on your schedule yet. Add competitions from the map, calendar, or list.' : 'No competitions match these filters. Try a larger distance, include contests with no map pin, or reset filters.'));
      return;
    }
    const pages = Math.max(1, Math.ceil(visible.length / listPageSize));
    state.listPage = Math.min(Math.max(1, state.listPage), pages);
    const start = (state.listPage - 1) * listPageSize;
    const page = visible.slice(start, start + listPageSize);
    let group = '';
    for (const event of page) {
      const key = event.startDate ? new Date(event.startDate + 'T12:00:00Z').toLocaleDateString('en-US', { month: 'long', year: 'numeric', timeZone: 'UTC' }) : 'Dates to come';
      if (key !== group) { list.append(node('h3', 'group-heading', key)); group = key; }
      list.append(renderCard(event));
    }
    if (pages === 1) return;
    list.prepend(listPager(visible.length, pages, start, page.length));
    list.append(listPager(visible.length, pages, start, page.length));
  }
  function listPager(total, pages, start, count) {
    const nav = node('nav', 'list-pager');
    nav.setAttribute('aria-label', 'List pages');
    const prev = button('Previous', () => setListPage(state.listPage - 1));
    prev.disabled = state.listPage <= 1;
    const next = button('Next', () => setListPage(state.listPage + 1));
    next.disabled = state.listPage >= pages;
    const status = node('p', 'list-pager-status', `${start + 1}–${start + count} of ${total}`);
    status.setAttribute('aria-live', 'polite');
    nav.append(prev, status, next);
    return nav;
  }
  function setListPage(page) {
    state.listPage = page;
    render();
    $('competition-list').scrollIntoView({ block: 'start' });
  }
  function isoDay(date) { return date.toISOString().slice(0, 10); }
  function eventsOnDay(events, iso) {
    return events.filter(e => e.startDate && e.startDate <= iso && (e.endDate || e.startDate) >= iso);
  }
  function shiftMonth(delta) {
    const next = new Date(Date.UTC(state.calYear, state.calMonth + delta, 1));
    state.calYear = next.getUTCFullYear();
    state.calMonth = next.getUTCMonth();
  }
  function ensureCalendarMonth(dated) {
    if (state.calYear != null) return;
    const today = C.todayISO();
    const focus = dated.find(e => (e.endDate || e.startDate) >= today) || dated[0];
    const iso = focus?.startDate || today;
    state.calYear = Number(iso.slice(0, 4));
    state.calMonth = Number(iso.slice(5, 7)) - 1;
  }
  function renderCalendar(visible) {
    const wrap = $('competition-calendar');
    const dated = visible.filter(e => e.startDate);
    ensureCalendarMonth(dated);
    wrap.replaceChildren();
    if (!visible.length) {
      wrap.append(node('p', 'empty', $('saved-only').checked ? 'Nothing on your schedule yet. Add competitions from the map, calendar, or list.' : 'No competitions match these filters. Try a larger distance, include contests with no map pin, or reset filters.'));
      return;
    }
    const toolbar = node('div', 'cal-toolbar');
    const prev = button('‹', () => { shiftMonth(-1); closePopover(); render(); }, 'cal-nav');
    prev.setAttribute('aria-label', 'Previous month');
    const next = button('›', () => { shiftMonth(1); closePopover(); render(); }, 'cal-nav');
    next.setAttribute('aria-label', 'Next month');
    const todayBtn = button('Today', () => {
      const today = C.todayISO();
      state.calYear = Number(today.slice(0, 4));
      state.calMonth = Number(today.slice(5, 7)) - 1;
      closePopover(); render();
    }, 'text-button');
    const heading = node('h3', 'cal-month-label', new Date(Date.UTC(state.calYear, state.calMonth, 1)).toLocaleDateString('en-US', { month: 'long', year: 'numeric', timeZone: 'UTC' }));
    heading.id = 'cal-month-label';
    toolbar.append(prev, heading, next, todayBtn);
    wrap.append(toolbar);
    const grid = node('div', 'cal-grid');
    grid.setAttribute('role', 'grid');
    grid.setAttribute('aria-labelledby', 'cal-month-label');
    for (const day of ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']) {
      const cell = node('div', 'cal-dow', day);
      cell.setAttribute('role', 'columnheader');
      grid.append(cell);
    }
    const first = new Date(Date.UTC(state.calYear, state.calMonth, 1));
    const cursor = new Date(first);
    cursor.setUTCDate(1 - first.getUTCDay());
    const today = C.todayISO();
    const maxChips = window.matchMedia('(max-width: 700px)').matches ? 2 : 3;
    for (let i = 0; i < 42; i += 1) {
      const iso = isoDay(cursor);
      const outside = cursor.getUTCMonth() !== state.calMonth;
      const day = node('div', 'cal-day' + (outside ? ' is-outside' : '') + (iso === today ? ' is-today' : ''));
      day.setAttribute('role', 'gridcell');
      day.setAttribute('data-date', iso);
      const num = node('span', 'cal-date', String(cursor.getUTCDate()));
      day.append(num);
      day.setAttribute('aria-label', cursor.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', timeZone: 'UTC' }));
      const onDay = eventsOnDay(dated, iso);
      if (onDay.length) {
        const shown = onDay.slice(0, maxChips);
        for (const event of shown) {
          const chip = button(event.name, () => {}, 'cal-event' + (state.saved.has(event.id) ? ' is-saved' : '') + (event.dateKind === 'window' ? ' is-window' : '') + (event.dateTentative ? ' is-tentative' : '') + (event.inDatabase || event.recordSlugs.length ? ' in-database' : ''));
          chip.dataset.calId = event.id;
          chip.title = event.name + ' · ' + C.dateLabel(event);
          chip.setAttribute('aria-haspopup', 'dialog');
          chip.setAttribute('aria-expanded', 'false');
          chip.addEventListener('click', ev => { ev.stopPropagation(); openEventPopover(event, chip); });
          day.append(chip);
        }
        if (onDay.length > maxChips) {
          const more = button(`+${onDay.length - maxChips} more`, () => {}, 'cal-more');
          more.dataset.calDay = iso;
          more.setAttribute('aria-haspopup', 'dialog');
          more.addEventListener('click', ev => { ev.stopPropagation(); openDayPopover(iso, onDay, more); });
          day.append(more);
        }
      }
      grid.append(day);
      cursor.setUTCDate(cursor.getUTCDate() + 1);
    }
    wrap.append(grid);
    const inMonth = dated.filter(e => {
      const start = e.startDate;
      const end = e.endDate || e.startDate;
      const from = `${state.calYear}-${String(state.calMonth + 1).padStart(2, '0')}-01`;
      const to = isoDay(new Date(Date.UTC(state.calYear, state.calMonth + 1, 0)));
      return start <= to && end >= from;
    }).length;
    if (dated.length && !inMonth) wrap.append(node('p', 'micro cal-empty-month', 'No dated competitions in this month. Use the arrows to find the next events.'));
  }
  function fillPopover(events) {
    const pop = $('event-popover'); pop.replaceChildren();
    const close = button('×', closePopover, 'popup-close');
    close.setAttribute('aria-label', 'Close details');
    pop.append(close);
    for (const event of events) {
      const card = renderCard(event);
      if (events.length === 1) {
        const title = card.querySelector('h3');
        if (title) title.id = 'event-popover-title';
      }
      pop.append(card);
    }
    if (events.length > 1) {
      const title = node('h3', 'sr-only', `${events.length} competitions`);
      title.id = 'event-popover-title';
      pop.prepend(title);
    }
  }
  function openEventPopover(event, anchor, keep) {
    if (!keep && state.calOpenId === event.id && !$('event-popover').hidden) { closePopover(); return; }
    closePopover();
    fillPopover([event]);
    state.calOpenId = event.id;
    showPopover(anchor);
  }
  function openDayPopover(iso, events, anchor) {
    closePopover();
    fillPopover(events);
    state.calOpenId = 'day:' + iso;
    showPopover(anchor);
  }
  function showPopover(anchor) {
    const pop = $('event-popover');
    const backdrop = $('event-popover-backdrop');
    pop.hidden = false; backdrop.hidden = false;
    if (anchor?.dataset.calId) anchor.setAttribute('aria-expanded', 'true');
    requestAnimationFrame(() => positionPopover(anchor));
  }
  function positionPopover(anchor) {
    const pop = $('event-popover');
    if (pop.hidden) return;
    if (window.innerWidth < 701 || !anchor) {
      pop.style.left = '0.75rem'; pop.style.right = '0.75rem'; pop.style.top = 'auto'; pop.style.bottom = '0.75rem'; pop.style.width = 'auto';
      return;
    }
    const pad = 10, r = anchor.getBoundingClientRect();
    pop.style.width = ''; pop.style.right = 'auto'; pop.style.bottom = 'auto';
    const pw = Math.min(360, pop.offsetWidth || 360), ph = pop.offsetHeight;
    let left = r.left, top = r.bottom + pad;
    if (left + pw > window.innerWidth - 12) left = window.innerWidth - pw - 12;
    if (left < 12) left = 12;
    if (top + ph > window.innerHeight - 12) top = Math.max(12, r.top - ph - pad);
    pop.style.left = `${left}px`; pop.style.top = `${top}px`;
  }
  function closePopover() {
    document.querySelectorAll('[aria-expanded="true"][data-cal-id]').forEach(el => el.setAttribute('aria-expanded', 'false'));
    state.calOpenId = null;
    const pop = $('event-popover'); const backdrop = $('event-popover-backdrop');
    if (pop) pop.hidden = true;
    if (backdrop) backdrop.hidden = true;
  }
  function render() {
    const opts = options();
    const visible = C.filterEvents(state.events, opts);
    state.visible = visible;
    const key = [opts.query, opts.date, opts.grade, opts.includeLocal, opts.savedOnly, opts.limit, state.origin?.lat, state.origin?.lng].join('|');
    if (key !== state.filterKey) { state.filterKey = key; state.listPage = 1; }
    if (state.calOpenId && !state.calOpenId.startsWith?.('day:') && !visible.some(e => e.id === state.calOpenId)) closePopover();
    $('result-count').textContent = visible.length;
    $('competition-calendar').hidden = state.view !== 'calendar';
    $('competition-list').hidden = state.view !== 'list';
    if (state.view === 'list') renderList(visible); else renderCalendar(visible);
    updateExports(); renderMarkers(visible);
  }
  function closePin() {
    state.activeMarker?.setAttribute('aria-expanded', 'false');
    state.activeMarker = null;
    state.activePinEvents = null;
    if ($('us-map-popup')) $('us-map-popup').hidden = true;
  }
  function mapTipsOpen() { return !$('map-tips-popover').hidden; }
  function closeMapTips() {
    $('map-tips-popover').hidden = true;
    $('map-tips-button').setAttribute('aria-expanded', 'false');
  }
  function openMapTips() {
    closePin();
    $('map-tips-popover').hidden = false;
    $('map-tips-button').setAttribute('aria-expanded', 'true');
  }
  function renderMarkers(visible) {
    if (!state.customMap) return;
    closePin(); state.customMap.setEvents(visible, state.saved, state.origin);
  }
  function openPin(marker, events) {
    if (state.activeMarker === marker) { closePin(); return; }
    closeMapTips();
    closePin();
    const content = $('us-map-popup'); content.replaceChildren();
    const close = button('×', closePin, 'popup-close');
    close.setAttribute('aria-label', 'Close details');
    content.append(close);
    for (const event of events) {
      const detail = node('section', 'pin-event');
      const website = link('Official website ↗', event.url);
      website.addEventListener('click', closePin);
      detail.append(node('h3', '', event.name));
      if (event.inDatabase || event.recordSlugs.length) detail.append(node('span', 'badge database-badge', 'Results in database'));
      detail.append(node('p', 'pin-date', 'Date: ' + C.dateLabel(event)), node('p', 'pin-deadline', C.deadlineLabel(event) + (event.registrationDeadline && event.registrationDeadline < C.todayISO() ? ' · Passed' : '')), node('p', 'pin-location', event.location.city + (event.location.precision?.startsWith('previous-') ? ' · Previous host' : '')), website);
      const saved = state.saved.has(event.id);
      const save = button(saved ? 'Remove from my schedule' : 'Add to my schedule', () => toggle(event), saved ? 'text-button pin-save' : 'primary pin-save');
      save.dataset.saveId = event.id;
      save.setAttribute('aria-pressed', String(saved));
      detail.append(save);
      content.append(detail);
    }
    state.activeMarker = marker; state.activePinEvents = events; marker.setAttribute('aria-expanded', 'true'); content.hidden = false;
    requestAnimationFrame(() => positionPinPopup(marker));
  }
  function positionPinPopup(marker) {
    const popup = $('us-map-popup');
    const map = $('map');
    if (!popup || popup.hidden || !marker || !map) return;
    const mapBox = map.getBoundingClientRect();
    const pinBox = marker.getBoundingClientRect();
    const pad = 8, gap = 10;
    popup.style.right = 'auto';
    popup.style.bottom = 'auto';
    const pw = popup.offsetWidth, ph = popup.offsetHeight;
    const pinX = pinBox.left + pinBox.width / 2 - mapBox.left;
    const pinY = pinBox.top + pinBox.height / 2 - mapBox.top;
    const pinR = pinBox.width / 2;
    let left = pinX + pinR + gap;
    let top = pinY - 28;
    let place = 'right';
    if (left + pw > mapBox.width - pad) {
      left = pinX - pinR - gap - pw;
      place = 'left';
    }
    if (left < pad) {
      left = Math.max(pad, Math.min(pinX - pw / 2, mapBox.width - pw - pad));
      top = pinY + pinR + gap;
      place = 'below';
      if (top + ph > mapBox.height - pad) {
        top = pinY - pinR - gap - ph;
        place = 'above';
      }
    }
    top = Math.max(pad, Math.min(top, mapBox.height - ph - pad));
    left = Math.max(pad, Math.min(left, mapBox.width - pw - pad));
    popup.style.left = `${left}px`;
    popup.style.top = `${top}px`;
    popup.dataset.place = place;
  }
  function setTab(tab) {
    const next = tab === 'calendar' ? 'calendar' : 'map';
    const changed = state.tab !== next;
    state.tab = next;
    document.body.classList.toggle('is-map-tab', next === 'map');
    document.body.classList.toggle('is-calendar-tab', next === 'calendar');
    $('map-tab-panel').hidden = next !== 'map';
    $('calendar-tab-panel').hidden = next !== 'calendar';
    $('tab-map').setAttribute('aria-selected', String(next === 'map'));
    $('tab-calendar').setAttribute('aria-selected', String(next === 'calendar'));
    $('tab-map').tabIndex = next === 'map' ? 0 : -1;
    $('tab-calendar').tabIndex = next === 'calendar' ? 0 : -1;
    const hash = next === 'calendar' ? '#calendar' : '#map';
    if (location.hash !== hash) history.replaceState(null, '', hash);
    if (next !== 'map') { closePin(); closeMapTips(); }
    if (next !== 'calendar') closePopover();
    if (next === 'map' && changed) {
      requestAnimationFrame(() => requestAnimationFrame(() => {
        state.customMap?.positionMarkers();
        if (state.activeMarker) positionPinPopup(state.activeMarker);
      }));
    }
  }
  function showUS() { closePin(); state.customMap?.reset(); }
  function focusPin(event) {
    closePopover();
    setTab('map');
    requestAnimationFrame(() => requestAnimationFrame(() => {
      state.customMap?.focus(event.id);
      $('map').scrollIntoView({ block: 'nearest' });
    }));
  }
  function fitMap() { showUS(); }
  async function loadCustomMap() {
    try {
      const response = await timeout(fetch('us-states.json'));
      if (!response.ok) throw new Error('boundaries');
      const topology = await response.json();
      const features = topojson.feature(topology, topology.objects.states);
      features.features = features.features.filter(f => Number(f.id) <= 56);
      $('map').hidden = false; $('map-message').hidden = true;
      state.customMap = new CompetitionUSMap($('map'), features, openPin, closePin, () => positionPinPopup(state.activeMarker));
      const popup = node('div', 'info-window us-map-popup'); popup.id = 'us-map-popup'; popup.hidden = true;
      popup.setAttribute('role', 'region'); popup.setAttribute('aria-label', 'Competition details');
      $('map').append(popup);
      popup.addEventListener('click', event => event.stopPropagation());
      popup.addEventListener('pointerdown', event => event.stopPropagation());
      $('map').addEventListener('keydown', event => { if (event.key === 'Escape') { const marker = state.activeMarker; closePin(); marker?.focus(); } });
      $('us-view').addEventListener('click', event => { event.preventDefault(); event.stopPropagation(); showUS(); });
      $('zoom-in').addEventListener('click', event => { event.preventDefault(); event.stopPropagation(); state.customMap.zoomBy(1.6); });
      $('zoom-out').addEventListener('click', event => { event.preventDefault(); event.stopPropagation(); state.customMap.zoomBy(1 / 1.6); });
      for (const id of ['us-view', 'zoom-in', 'zoom-out']) $(id).disabled = false;
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
  function setBusy(busy) {
    state.busy = busy;
    $('origin').setAttribute('aria-busy', String(busy));
  }
  async function chooseOrigin(result, generation) {
    if (generation !== state.generation) return;
    $('location-choices').hidden = true;
    state.origin = result.position;
    state.savedOrigin = { label: result.label, lat: result.position.lat, lng: result.position.lng };
    $('origin').value = result.label;
    $('travel-status').textContent = 'Showing competitions within ' + milesPhrase() + ' of ' + result.label + '.';
    persist();
    setBusy(false); render(); fitMap();
  }
  async function lookupOrigin() {
    const address = $('origin').value.trim();
    if (!address) {
      $('location-choices').hidden = true;
      if (state.origin || state.savedOrigin) {
        state.origin = null;
        state.savedOrigin = null;
        persist();
        render();
      }
      $('travel-status').textContent = 'Browse all competitions, or enter a starting point to filter by miles.';
      return;
    }
    if (state.origin && state.savedOrigin?.label === address) return;
    const generation = ++state.generation;
    setBusy(true);
    $('location-choices').hidden = true;
    $('travel-status').textContent = 'Finding your starting point…';
    try {
      const results = await timeout(PlannerGeocoder.lookup(address));
      if (generation !== state.generation) return;
      if (!results.length) throw new Error('no-results');
      if (results.length > 1) {
        const choices = $('location-choices'); choices.replaceChildren(); choices.hidden = false;
        for (const result of results.slice(0, 5)) choices.append(button(result.label, () => { setBusy(true); chooseOrigin(result, generation); }, 'choice-chip'));
        $('travel-status').textContent = 'Confirm the matching location below, or enter a more specific address.'; setBusy(false);
      } else await chooseOrigin(results[0], generation);
    } catch {
      if (generation !== state.generation) return;
      $('travel-status').textContent = 'Could not locate that address. Try a ZIP code or a full street address, city, and state. Check your connection if the problem continues.';
      setBusy(false);
    }
  }
  let originTimer;
  $('travel-form').addEventListener('submit', event => {
    event.preventDefault();
    clearTimeout(originTimer);
    lookupOrigin();
  });
  $('origin').addEventListener('input', () => {
    clearTimeout(originTimer);
    state.generation++;
    setBusy(false);
    $('location-choices').hidden = true;
    const address = $('origin').value.trim();
    if (!address) {
      state.origin = null;
      if (state.savedOrigin) { state.savedOrigin = null; persist(); }
      $('travel-status').textContent = 'Browse all competitions, or enter a starting point to filter by miles.';
      render();
      return;
    }
    if (state.origin) { state.origin = null; render(); }
    $('travel-status').textContent = 'Finding your starting point…';
    originTimer = setTimeout(lookupOrigin, 550);
  });
  for (const id of ['date-filter', 'grade-filter', 'include-local', 'saved-only']) $(id).addEventListener('change', render);
  $('miles-preset').addEventListener('change', () => { applyMilesPreset(); onMilesChange(); });
  $('miles-limit').addEventListener('input', onMilesChange);
  document.querySelectorAll('[name=explore-view]').forEach(input => input.addEventListener('change', () => {
    state.view = document.querySelector('[name=explore-view]:checked').value;
    closePopover(); render();
  }));
  $('tab-map').addEventListener('click', () => setTab('map'));
  $('tab-calendar').addEventListener('click', () => setTab('calendar'));
  document.querySelector('.planner-tabs').addEventListener('keydown', event => {
    if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight' && event.key !== 'Home' && event.key !== 'End') return;
    event.preventDefault();
    const next = event.key === 'ArrowLeft' || event.key === 'Home' ? 'map' : event.key === 'ArrowRight' || event.key === 'End' ? 'calendar' : state.tab;
    setTab(next);
    $(next === 'map' ? 'tab-map' : 'tab-calendar').focus();
  });
  window.addEventListener('hashchange', () => setTab(location.hash === '#calendar' ? 'calendar' : 'map'));
  setTab(state.tab);
  $('event-popover-backdrop').addEventListener('click', closePopover);
  $('map-tips-button').addEventListener('click', event => {
    event.stopPropagation();
    if (mapTipsOpen()) closeMapTips(); else openMapTips();
  });
  $('map-tips-close').addEventListener('click', closeMapTips);
  document.addEventListener('pointerdown', event => {
    if (!mapTipsOpen()) return;
    if ($('map-tips-button').contains(event.target) || $('map-tips-popover').contains(event.target)) return;
    closeMapTips();
  });
  document.addEventListener('keydown', event => {
    if (event.key !== 'Escape') return;
    if (!$('event-popover').hidden) {
      const id = state.calOpenId;
      closePopover();
      if (id && !String(id).startsWith('day:')) document.querySelector(`[data-cal-id="${id}"]`)?.focus();
      return;
    }
    if (mapTipsOpen()) {
      closeMapTips();
      $('map-tips-button').focus();
    }
  });
  window.addEventListener('resize', () => {
    if ($('event-popover').hidden) return;
    const anchor = document.querySelector('[data-cal-id][aria-expanded="true"]') || document.querySelector('[data-cal-day]');
    positionPopover(anchor);
  });
  $('reset-filters').addEventListener('click', () => {
    state.generation++; state.origin = null; state.savedOrigin = null; $('origin').value = ''; $('date-filter').value = 'upcoming'; $('grade-filter').value = 'all'; $('include-local').checked = true; $('saved-only').checked = false; $('miles-preset').value = ''; $('miles-limit').value = ''; showCustomMiles(false); $('location-choices').hidden = true; setBusy(false);
    persist();
    $('travel-status').textContent = 'Showing all locations. Enter a starting point to filter by miles.'; render(); fitMap();
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
  try {
    const response = await timeout(fetch('competition_events.json'));
    if (!response.ok) throw new Error('catalog');
    const catalog = await response.json();
    if (!Array.isArray(catalog.events)) throw new Error('catalog');
    state.events = catalog.events;
    try {
      const stored = readStore();
      state.saved = new Set(stored.saved.filter(id => state.events.some(e => e.id === id)));
      const origin = originFromStore(stored.origin);
      if (origin) applyOrigin(origin, false);
    } catch { /* A corrupt or blocked store must not prevent browsing. */ }
    render(); await loadCustomMap();
  } catch {
    $('competition-list').replaceChildren(node('p', 'empty', 'The competition catalog could not load. Please refresh to try again.'));
    $('competition-calendar').replaceChildren(node('p', 'empty', 'The competition catalog could not load. Please refresh to try again.'));
    $('map-message').querySelector('p').textContent = 'The competition catalog is unavailable. Refresh to try again.';
  }
})();
