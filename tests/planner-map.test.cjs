const test = require('node:test');
const assert = require('node:assert/strict');
const d3 = require('../docs/vendor/d3.min.js');
const topojson = require('../docs/vendor/topojson-client.min.js');
const topology = require('../docs/us-states.json');
const features = topojson.feature(topology, topology.objects.states);
features.features = features.features.filter(f => Number(f.id) <= 56);
const projection = d3.geoAlbersUsa().fitExtent([[30, 25], [970, 600]], features);
test('US map contains 50 states and DC, with valid paths', () => {
  assert.equal(features.features.length, 51);
  for (const feature of features.features) {
    const path = d3.geoPath(projection)(feature);
    assert.ok(path && !path.includes('NaN'), feature.properties.name);
  }
});
test('Alaska, Hawaii and every catalog campus fit the inset projection', () => {
  const points = [[-149.9, 61.2], [-157.85, 21.3], ...require('../docs/competition_events.json').events.filter(e => e.location).map(e => [e.location.lng, e.location.lat])];
  for (const coords of points) {
    const p = projection(coords);
    assert.ok(p && p[0] >= 0 && p[0] <= 1000 && p[1] >= 0 && p[1] <= 640, coords.join(','));
  }
  assert.equal(projection([2.35, 48.86]), null);
});
