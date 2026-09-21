const test = require('node:test');
const assert = require('node:assert/strict');
const C = require('../docs/planner-core.js');
const { events } = require('../docs/competition_events.json');
const event = id => events.find(e => e.id === id);
const base = () => ({ today: '2026-09-08', query: '', date: 'upcoming', includeLocal: true, savedOnly: false, saved: new Set(), origin: null, limit: Infinity });

test('browse includes unknown dates, and groups subject rounds into one trip', () => {
  const result = C.filterEvents(events, base());
  assert.equal(result.length, events.length);
  assert.equal(result.filter(e => e.id === 'pumac').length, 1);
  assert.ok(event('pumac').recordSlugs.includes('pumac-b-algebra'));
  assert.equal(result.at(-1).startDate, null);
});
test('distance filter keeps campus events within the mile limit', () => {
  const origin = { lat: 42.36, lng: -71.06 };
  const near = event('hmmt-nov'), far = event('pumac');
  const cutoff = (C.milesBetween(origin, near.location) + C.milesBetween(origin, far.location)) / 2;
  const result = C.filterEvents(events, { ...base(), origin, limit: cutoff });
  assert.ok(result.includes(near));
  assert.ok(!result.includes(far));
  assert.ok(!result.includes(event('dmm')));
});
test('any-distance origin still shows far campus events', () => {
  const options = { ...base(), origin: { lat: 21.3, lng: -157.8 }, limit: Infinity };
  assert.ok(C.filterEvents(events, options).includes(event('bmt')));
  const info = C.travelInfo(event('bmt'), options.origin, Infinity);
  assert.equal(info.kind, 'near');
  assert.match(info.label, /mi/);
});
test('local programs remain visible without fabricated proximity', () => {
  const o = { ...base(), origin: { lat: 0, lng: 0 }, includeLocal: true, limit: 1 };
  const result = C.filterEvents(events, o);
  assert.ok(result.includes(event('amc8'))); assert.ok(result.includes(event('amc8')));
  o.includeLocal = false; assert.equal(C.filterEvents(events, o).length, 0);
});
test('date filter respects inclusive multi-day end and never rolls last year forward', () => {
  const e = event('amc8');
  assert.ok(C.filterEvents([e], { ...base(), today: '2027-01-27' }).length);
  assert.equal(C.filterEvents([e], { ...base(), today: '2027-01-28' }).length, 0);
  assert.ok(C.filterEvents(events, { ...base(), date: 'upcoming' }).some(e => !e.startDate));
  assert.ok(C.filterEvents([e], { ...base(), today: '2028-01-01', date: 'all' }).length);
});
test('search and saved-only filters compose', () => {
  const o = { ...base(), query: '  princeton ', savedOnly: true, saved: new Set(['pumac']) };
  assert.deepEqual(C.filterEvents(events, o).map(e => e.id), ['pumac']);
  o.saved.clear(); assert.equal(C.filterEvents(events, o).length, 0);
});
test('real HMMT/Duke collision is flagged; broad testing windows are not fixed conflicts', () => {
  assert.match(C.conflicts(event('hmmt-nov'), [event('hmmt-nov'), event('dmm')])[0], /Date overlap/);
  assert.deepEqual(C.conflicts(event('hmmt-feb'), [event('mathcounts-chapter')]), []);
});
test('HMMT season restriction is flagged even on nonoverlapping dates', () => {
  assert.match(C.conflicts(event('hmmt-nov'), [event('hmmt-feb')])[0], /Season rule/);
});
test('calendar excludes testing windows and unannounced dates', () => {
  const result = C.calendar([event('amc8'), event('cmimc'), event('pumac')]);
  assert.equal((result.match(/BEGIN:VEVENT/g) || []).length, 1);
  assert.match(result, /DTSTART;VALUE=DATE:20261121/);
  assert.match(result, /DTEND;VALUE=DATE:20261122/);
});
test('calendar preserves multi-day dates, crosses year boundary and escapes content', () => {
  const e = { ...event('usamo'), id: 'test', name: 'A, B; C\\D\nE', startDate: '2026-12-31', endDate: '2027-01-01' };
  const result = C.calendar([e], new Date('2026-09-08T00:00:00Z'));
  assert.match(result, /DTEND;VALUE=DATE:20270102/);
  assert.ok(result.includes('SUMMARY:A\\, B\\; C\\\\D\\nE'));
  assert.match(result, /DTSTAMP:20260908T000000Z/);
});
test('calendar folds at 75 UTF-8 octets without breaking Unicode', () => {
  const e = { ...event('pumac'), name: '数学∑'.repeat(60) };
  const result = C.calendar([e]);
  for (const line of result.split('\r\n')) assert.ok(Buffer.byteLength(line, 'utf8') <= 75);
  assert.ok(result.replaceAll('\r\n ', '').includes(e.name));
});
test('distance is stable for identical locations and antipodes', () => {
  assert.equal(C.milesBetween({ lat: 40, lng: 0 }, { lat: 40, lng: 0 }), 0);
  assert.ok(Number.isFinite(C.milesBetween({ lat: 0, lng: 0 }, { lat: 0, lng: 180 })));
});

test('AMM Local remains nationwide and distinct from the Denver AMM festival', () => {
  const local = event('amm-local-2027'), festival = event('amm');
  assert.equal(local.startDate, '2027-01-17');
  assert.equal(local.inDatabase, true);
  assert.equal(local.location, null);
  assert.equal(local.mode, 'local');
  assert.equal(festival.startDate, '2027-05-28');
  assert.equal(festival.endDate, '2027-05-31');
  for (const origin of [{lat: 40.71, lng: -74}, {lat: 21.3, lng: -157.8}, {lat: 61.2, lng: -149.9}]) {
    assert.ok(C.filterEvents(events, {...base(), origin, limit: 0}).includes(local));
  }
});

test('planner excludes online editions while retaining in-person BMT', () => {
  assert.ok(events.every(e => e.mode !== 'online'));
  assert.equal(event('bmt').mode, 'campus');
  for (const id of ['bmt-online', 'purple-comet', 'hmic', 'm3']) assert.equal(event(id), undefined);
});

test('distance labels use straight-line miles', () => {
  const origin = {lat: 40, lng: -75}, destination = {lat: 41, lng: -75};
  const e = {...event('bmt'), location: destination};
  const miles = Math.round(C.milesBetween(origin, destination));
  const info = C.travelInfo(e, origin, 500);
  assert.equal(info.reachable, true);
  assert.equal(info.label, `${miles} mi`);
  assert.equal(C.travelInfo(e, origin, miles - 1).reachable, false);
});
test('straight-line miles apply to Alaska and Hawaii', () => {
  const destination = event('bmt').location;
  for (const origin of [{lat:21.3,lng:-157.8},{lat:61.2,lng:-149.9}]) {
    assert.equal(C.travelInfo(event('bmt'), origin, 100).reachable, false);
    assert.equal(C.travelInfo(event('bmt'), origin, Infinity).reachable, true);
    assert.ok(C.milesBetween(origin, destination) > 100);
  }
});
test('grade filter separates middle school, high school, and overlapping contests', () => {
  assert.equal(C.classifyGrades('Middle school').middle, true);
  assert.equal(C.classifyGrades('Middle school').high, false);
  assert.equal(C.classifyGrades('High school').middle, false);
  assert.equal(C.classifyGrades('High school').high, true);
  assert.equal(C.classifyGrades('Middle school & high school').middle, true);
  assert.equal(C.classifyGrades('Middle school & high school').high, true);
  assert.equal(C.classifyGrades('Grade 8 and below; age limit applies').middle, true);
  assert.equal(C.classifyGrades('Grade 8 and below; age limit applies').high, false);
  assert.equal(C.classifyGrades('Grades 10 / 12 and below; age limits apply').middle, true);
  assert.equal(C.classifyGrades('Grades 10 / 12 and below; age limits apply').high, true);
  const middle = C.filterEvents(events, { ...base(), date: 'all', grade: 'middle' });
  const high = C.filterEvents(events, { ...base(), date: 'all', grade: 'high' });
  assert.ok(middle.includes(event('amc8')));
  assert.ok(!high.includes(event('amc8')));
  assert.ok(high.includes(event('hmmt-nov')));
  assert.ok(!middle.includes(event('hmmt-nov')));
  assert.ok(middle.length && high.length && middle.length < events.length && high.length < events.length);
});
