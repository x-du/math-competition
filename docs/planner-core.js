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
  function travelInfo(event, origin, limit) {
    if (!event.location) return { kind: event.mode === 'online' ? 'online' : 'local', label: event.mode === 'online' ? 'Online · no travel' : 'Venue / host to confirm', reachable: true };
    if (!origin) return { kind: 'browse', label: '', reachable: true };
    const miles = milesBetween(origin, event.location);
    const reachable = miles <= limit;
    return { kind: reachable ? 'near' : 'far', label: `${Math.round(miles).toLocaleString()} mi`, reachable };
  }
  function classifyGrades(grades) {
    const t = String(grades || '').toLowerCase().replace(/[–—]/g, '-');
    const values = [];
    const num = token => token === 'k' ? 0 : Number(token);
    const take = n => { if (Number.isFinite(n) && n >= 0 && n <= 12) values.push(n); };
    for (const m of t.matchAll(/\b(k|\d{1,2})\s*-\s*(k|\d{1,2})\b/g)) { take(num(m[1])); take(num(m[2])); }
    for (const m of t.matchAll(/\b(k|\d{1,2})\s*\/\s*(\d{1,2})\b/g)) { take(num(m[1])); take(num(m[2])); }
    for (const m of t.matchAll(/\b(?:grade|grades)\s+(k|\d{1,2})\b/g)) take(num(m[1]));
    const minG = values.length ? Math.min(...values) : null;
    const maxG = values.length ? Math.max(...values) : null;
    const below = /\band below\b/.test(t);
    let middle = /\belementary\b|\bmiddle\b|\bjunior high\b/.test(t);
    let high = /\bhigh school\b|\bsenior high\b/.test(t);
    if (minG != null) {
      if (below || minG <= 8) middle = true;
      if (maxG >= 9) high = true;
    }
    if (!middle && !high) high = true;
    return { middle, high };
  }
  function matchesGradeFilter(grades, filter) {
    if (!filter || filter === 'all') return true;
    const bands = classifyGrades(grades);
    return filter === 'middle' ? bands.middle : filter === 'high' ? bands.high : true;
  }
  function filterEvents(events, options) {
    return events.filter(event => {
      if (options.date !== 'all' && event.endDate && event.endDate < options.today) return false;
      if (!options.includeLocal && !event.location) return false;
      if (options.savedOnly && !options.saved.has(event.id)) return false;
      if (!matchesGradeFilter(event.grades, options.grade)) return false;
      const text = [event.name, event.grades, event.location?.city, event.location?.venue].join(' ').toLowerCase();
      if (options.query && !text.includes(options.query.trim().toLowerCase())) return false;
      return travelInfo(event, options.origin, options.limit).reachable;
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
  const api = { todayISO, dateLabel, deadlineLabel, compareEvents, milesBetween, travelInfo, classifyGrades, matchesGradeFilter, filterEvents, conflicts, calendar };
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.PlannerCore = api;
})(globalThis);
