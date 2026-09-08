/* Shared, dependency-free planner rules; also loaded by Node's test runner. */
(function (root) {
  'use strict';
  function todayISO(now = new Date()) {
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
  }
  function dateLabel(event) {
    if (!event.startDate) return 'Next date not announced';
    const format = date => new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC' }).format(new Date(date + 'T12:00:00Z'));
    return format(event.startDate) + (event.endDate !== event.startDate ? ' – ' + format(event.endDate) : '') + (event.dateTentative ? ' (tentative)' : '');
  }
  function deadlineLabel(event) {
    const value = event.registrationDeadline ? dateLabel({ startDate: event.registrationDeadline, endDate: event.registrationDeadline }) : 'Not announced — check website';
    return 'Registration deadline: ' + value + (event.registrationNote ? ' · ' + event.registrationNote : '');
  }
  function compareEvents(a, b) {
    return (a.startDate || '9999').localeCompare(b.startDate || '9999') || a.name.localeCompare(b.name);
  }
  function milesBetween(a, b) {
    const rad = x => x * Math.PI / 180;
    const h = Math.sin(rad(b.lat - a.lat) / 2) ** 2 + Math.cos(rad(a.lat)) * Math.cos(rad(b.lat)) * Math.sin(rad(b.lng - a.lng) / 2) ** 2;
    return 3958.7613 * 2 * Math.atan2(Math.sqrt(Math.min(1, h)), Math.sqrt(Math.max(0, 1 - h)));
  }
  function routeKey(location) { return `${location.lat},${location.lng}`; }
  // Planning heuristic, not a road route: 30% distance allowance at 50 mph.
  function estimateRoute(origin, destination) {
    const lower48 = p => p.lat >= 24 && p.lat <= 50 && p.lng >= -125 && p.lng <= -66;
    if (!lower48(origin) || !lower48(destination)) return { status: 'unsupported', estimated: true };
    const miles = milesBetween(origin, destination) * 1.3;
    return { status: 'ok', estimated: true, miles, hours: Math.max(0.25, miles / 50) };
  }
  function travelInfo(event, origin, routes, mode, limit) {
    if (!event.location) return { kind: event.mode === 'online' ? 'online' : 'local', label: event.mode === 'online' ? 'Online · no travel' : 'Venue / host to confirm', reachable: true };
    if (!origin) return { kind: 'browse', label: 'Enter your start to check travel', reachable: true };
    const route = routes.get(routeKey(event.location));
    const time = route?.estimated ? formatHours(Math.max(0.25, Math.round(route.hours * 4) / 4)) : route ? formatHours(route.hours) : '';
    const prefix = route?.estimated ? 'Rough estimate: ' : '';
    if (route?.status === 'ok' && route.hours <= limit) return { kind: 'drive', label: `${prefix}${time} drive · ${route.estimated ? Math.round(route.miles / 5) * 5 : Math.round(route.miles)} mi`, reachable: true };
    if (mode === 'fly') return { kind: 'fly', label: `Consider flying · ${Math.round(milesBetween(origin, event.location)).toLocaleString()} mi direct`, reachable: true };
    if (route?.status === 'ok') return { kind: 'far', label: `${prefix}${time} drive · over your limit`, reachable: false };
    return { kind: 'unknown', label: route?.status === 'unsupported' ? 'Driving estimate unavailable outside the contiguous US' : route?.status === 'no-route' ? 'No driving route found' : 'Driving route not verified', reachable: false };
  }
  function formatHours(hours) {
    const minutes = Math.round(hours * 60);
    return minutes < 60 ? `${minutes} min` : `${Math.floor(minutes / 60)} hr${minutes % 60 ? ' ' + minutes % 60 + ' min' : ''}`;
  }
  function filterEvents(events, options) {
    return events.filter(event => {
      if (options.date !== 'all' && event.endDate && event.endDate < options.today) return false;
      if (options.date === 'confirmed' && !event.startDate) return false;
      if (!options.includeLocal && !event.location) return false;
      if (options.savedOnly && !options.saved.has(event.id)) return false;
      const text = [event.name, event.grades, event.location?.city, event.location?.venue].join(' ').toLowerCase();
      if (options.query && !text.includes(options.query.trim().toLowerCase())) return false;
      return travelInfo(event, options.origin, options.routes, options.mode, options.limit).reachable;
    }).sort(compareEvents);
  }
  function conflicts(event, selected) {
    const messages = [];
    for (const other of selected) {
      if (other.id === event.id) continue;
      if ([event.id, other.id].includes('hmmt-nov') && [event.id, other.id].includes('hmmt-feb')) messages.push(`Season rule: choose either HMMT November or HMMT February.`);
      if (event.dateKind === 'fixed' && other.dateKind === 'fixed' && event.startDate <= other.endDate && other.startDate <= event.endDate) messages.push(`Date overlap with ${other.name}.`);
    }
    return [...new Set(messages)];
  }
  function nextDate(date) {
    const d = new Date(date + 'T12:00:00Z'); d.setUTCDate(d.getUTCDate() + 1);
    return d.toISOString().slice(0, 10).replaceAll('-', '');
  }
  function escapeICS(text) { return String(text).replaceAll('\\', '\\\\').replace(/\r?\n/g, '\\n').replaceAll(';', '\\;').replaceAll(',', '\\,'); }
  function foldLine(line) {
    const encoder = new TextEncoder(); let folded = '', bytes = 0;
    for (const char of line) {
      const size = encoder.encode(char).length;
      if (bytes + size > 75) { folded += '\r\n '; bytes = 1; }
      folded += char; bytes += size;
    }
    return folded;
  }
  function calendar(events, stamp = new Date()) {
    const lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Math Competition Records//Planner//EN', 'CALSCALE:GREGORIAN', 'METHOD:PUBLISH'];
    for (const event of events.filter(e => e.startDate && e.dateKind === 'fixed' && !e.dateTentative).sort(compareEvents)) {
      lines.push('BEGIN:VEVENT', `UID:${event.id}-${event.startDate}@mathintegrity.org`, `DTSTAMP:${stamp.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}/, '')}`, `DTSTART;VALUE=DATE:${event.startDate.replaceAll('-', '')}`, `DTEND;VALUE=DATE:${nextDate(event.endDate)}`, `SUMMARY:${escapeICS(event.name)}`, `LOCATION:${escapeICS(event.location ? event.location.venue + ', ' + event.location.city : event.mode === 'online' ? 'Online' : 'Confirm with organizer')}`, `DESCRIPTION:${escapeICS(event.notes + '\nRegistration and eligibility must be confirmed with the organizer.\n' + event.url)}`, `URL:${event.url}`, 'END:VEVENT');
    }
    lines.push('END:VCALENDAR');
    return lines.map(foldLine).join('\r\n') + '\r\n';
  }
  const api = { todayISO, dateLabel, deadlineLabel, compareEvents, milesBetween, estimateRoute, routeKey, travelInfo, formatHours, filterEvents, conflicts, calendar };
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.PlannerCore = api;
})(globalThis);
