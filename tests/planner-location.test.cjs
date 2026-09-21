const test = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const d3 = require('../docs/vendor/d3.min.js');
const zipData = require('../docs/us-zip-locations.json');
function element() { return { style: {}, attributes: {}, setAttribute(k,v) { this.attributes[k]=v; }, remove() {}, append(e) { this.children.push(e); }, children: [], replaceChildren() {this.children=[];} }; }
function geocoder() {
 const window = {};
 const context = { window, URLSearchParams, fetch: async () => ({ok:true,json:async()=>zipData}), setTimeout: (...args) => {const t=setTimeout(...args);t.unref();return t;}, clearTimeout,
 document: { createElement: element, head: { append(script) {
  const callback = new URL(script.src).searchParams.get('callback');
  window[callback]({result:{addressMatches:[{matchedAddress:'PUBLIC TEST ADDRESS',coordinates:{x:-76.9,y:38.8}},{coordinates:{x:null,y:null}}]}});
 } } } };
 vm.runInNewContext(fs.readFileSync('docs/planner-geocoder.js','utf8'),context);
 return window.PlannerGeocoder;
}
test('ZIP lookup preserves leading zero and handles ZIP+4 without sending an address',async()=>{
 const g=geocoder(); const result=await g.lookup('02139-1234');
 assert.equal(result.length,1);assert.match(result[0].label,/02139/);assert.equal(result[0].approximate,true);
 assert.equal((await g.lookup('00000')).length,0);
});
test('Census response normalizes coordinates and discards invalid matches',async()=>{
 const result=await geocoder().lookup('PUBLIC TEST ADDRESS');
 assert.equal(result.length,1);assert.equal(result[0].position.lat,38.8);assert.equal(result[0].position.lng,-76.9);
});
test('origin dot survives empty event results, tracks zoom, and clears with the origin',()=>{
 const window={};vm.runInNewContext(fs.readFileSync('docs/planner-map.js','utf8'),{window,document:{createElement:element}});
 const map=Object.create(window.CompetitionUSMap.prototype);
 map.projection=d3.geoAlbersUsa().scale(1000).translate([500,320]);
 map.container={getBoundingClientRect:()=>({width:1000,height:640})};map.markerLayer=element();map.transform=d3.zoomIdentity;
 map.setEvents([],new Set(),{lat:42.36,lng:-71.06});
 assert.equal(map.entries.length,1); assert.match(map.entries[0].marker.className,/origin-pin/);
 const oldLeft=map.entries[0].marker.style.left;
 map.transform=d3.zoomIdentity.scale(2);map.positionMarkers();assert.notEqual(map.entries[0].marker.style.left,oldLeft);
 map.setEvents([],new Set(),null);assert.equal(map.entries.length,0);
});
