const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const C = require('../docs/planner-core.js');
const {events} = require('../docs/competition_events.json');

test('approved in-person candidates are covered without adding online-only entries', () => {
  const added = events.filter(e => e.candidateNumber);
  const expected = Array.from({length:50}, (_,i) => i+1).filter(n => ![39,43,45,46].includes(n));
  assert.deepEqual([...new Set(added.map(e => e.candidateNumber))].sort((a,b)=>a-b), expected);
  assert.ok(added.every(e => e.mode !== 'online'));
  assert.ok(added.every(e => !e.recordSlugs.length));
  assert.ok(events.find(e => e.id === 'hmmt-nov').recordSlugs.length);
  const final = added.find(e => e.id === 'mathcon-finals');
  assert.equal(final.startDate, '2027-05-29');
  assert.equal(final.registrationDeadline, '2027-04-16');
  assert.match(final.notes, /qualify/);
});

test('deadline labels distinguish unknown dates from school or invitation deadlines', () => {
  assert.match(C.deadlineLabel({registrationDeadline:null}), /Not announced/);
  assert.match(C.deadlineLabel({registrationDeadline:'2027-04-16', registrationNote:'Invited finalists only'}), /Apr 16, 2027.*Invited finalists only/);
  const e = events.find(e => e.id === 'rose-hulman');
  assert.equal(e.startDate, null);
  assert.equal(e.registrationDeadline, null);
  assert.match(C.dateLabel(e), /Next date not announced/);
  const tentative = events.find(e => e.id === 'obryan');
  assert.match(C.dateLabel(tentative), /tentative/);
  assert.ok(!C.calendar([tentative]).includes('BEGIN:VEVENT'));
});

test('co-located map pins retain independent database, girls and saved indicators', () => {
  const element = () => ({style:{}, children:[], attributes:{}, append(e){this.children.push(e);}, replaceChildren(){this.children=[];}, setAttribute(k,v){this.attributes[k]=v;}, addEventListener(){}});
  const window = {};
  vm.runInNewContext(fs.readFileSync('docs/planner-map.js','utf8'), {window, document:{createElement:element}});
  const map=Object.create(window.CompetitionUSMap.prototype);
  map.projection=()=>[500,320]; map.transform={apply:p=>p};
  map.container={getBoundingClientRect:()=>({width:1000,height:640})}; map.markerLayer=element();
  const entries=[
    {id:'covered', name:'Open contest', grades:'High school', recordSlugs:['existing']},
    {id:'new', name:'New contest', grades:'High school', recordSlugs:[]},
    {id:'girls', name:'Girls contest', grades:'High school', recordSlugs:['existing']}
  ].map(e=>({...e, location:{lat:42,lng:-71}}));
  map.setEvents(entries,new Set(['covered']));
  assert.equal(map.entries.length,3);
  const covered=map.entries.find(e=>e.events[0].id==='covered');
  assert.match(covered.marker.className,/in-database/);
  assert.match(covered.marker.className,/saved/);
  assert.match(covered.marker.attributes['aria-label'],/Results in database/);
  assert.ok(!map.entries.find(e=>e.events[0].id==='new').marker.className.includes('in-database'));
  assert.match(map.entries.find(e=>e.events[0].id==='girls').marker.className,/girls in-database/);
  assert.equal(new Set(map.entries.map(e=>e.offset)).size,3);
});
