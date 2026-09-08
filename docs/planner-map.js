/* US-only SVG map. Coordinates are from the curated catalog, not Google results. */
(function () {
  const initials = {1:'AL',2:'AK',4:'AZ',5:'AR',6:'CA',8:'CO',9:'CT',10:'DE',11:'DC',12:'FL',13:'GA',15:'HI',16:'ID',17:'IL',18:'IN',19:'IA',20:'KS',21:'KY',22:'LA',23:'ME',24:'MD',25:'MA',26:'MI',27:'MN',28:'MS',29:'MO',30:'MT',31:'NE',32:'NV',33:'NH',34:'NJ',35:'NM',36:'NY',37:'NC',38:'ND',39:'OH',40:'OK',41:'OR',42:'PA',44:'RI',45:'SC',46:'SD',47:'TN',48:'TX',49:'UT',50:'VT',51:'VA',53:'WA',54:'WV',55:'WI',56:'WY'};
  class CompetitionUSMap {
    constructor(container, features, onSelect, onClose) {
      this.container = container;
      this.onSelect = onSelect;
      this.onClose = onClose;
      this.entries = [];
      this.transform = d3.zoomIdentity;
      this.projection = d3.geoAlbersUsa().fitExtent([[30, 25], [970, 600]], features);
      this.svg = d3.select(container).append('svg').attr('viewBox', '0 0 1000 640').attr('aria-label', 'United States with Alaska and Hawaii insets');
      this.layer = this.svg.append('g');
      const path = d3.geoPath(this.projection);
      this.layer.selectAll('path').data(features.features).join('path')
        .attr('d', path).attr('class', 'us-state')
        .attr('fill', f => `hsl(${Number(f.id) * 137.508 % 360}, 48%, 73%)`)
        .append('title').text(f => f.properties.name);
      const labelPoints = features.features.map(feature => ({ feature, point: path.centroid(feature) }));
      this.layer.append('g').attr('class', 'state-initials').selectAll('text').data(labelPoints).join('text')
        .attr('x', d => d.point[0]).attr('y', d => d.point[1])
        .attr('text-anchor', 'middle').attr('dominant-baseline', 'central')
        .text(d => initials[Number(d.feature.id)] || '');
      // Label the inset states explicitly; the composite projection relocates both.
      for (const [text, coords] of [['Alaska', [-152, 60]], ['Hawaii', [-157, 20]]]) {
        const point = this.projection(coords);
        if (point) this.layer.append('text').attr('x', point[0]).attr('y', point[1] + 45).attr('class', 'inset-label').text(text);
      }
      this.markerLayer = document.createElement('div');
      this.markerLayer.className = 'us-marker-layer'; container.append(this.markerLayer);
      this.zoom = d3.zoom().scaleExtent([1, 10]).extent([[0, 0], [1000, 640]])
        .translateExtent([[0, 0], [1000, 640]])
        .filter(event => !event.target.closest?.('button') && (!event.ctrlKey || event.type === 'wheel') && !event.button)
        .on('zoom', event => { this.transform = event.transform; this.layer.attr('transform', event.transform); this.positionMarkers(); this.onClose(); });
      this.svg.call(this.zoom).attr('tabindex', 0)
        .attr('aria-label', 'US competition map. Scroll or pinch to zoom, drag to pan. Use plus/minus or arrow keys when focused.')
        .on('keydown.navigation', event => {
          if (event.key === '+' || event.key === '=') { event.preventDefault(); this.zoomBy(1.35); }
          else if (event.key === '-') { event.preventDefault(); this.zoomBy(1 / 1.35); }
          else if (event.key === 'Home' || event.key === '0') { event.preventDefault(); this.reset(); }
          else if (['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'].includes(event.key)) {
            event.preventDefault();
            const dx = event.key === 'ArrowLeft' ? 65 : event.key === 'ArrowRight' ? -65 : 0;
            const dy = event.key === 'ArrowUp' ? 65 : event.key === 'ArrowDown' ? -65 : 0;
            this.svg.call(this.zoom.translateBy, dx / this.transform.k, dy / this.transform.k);
          }
        });
      this.svg.on('click.close', () => this.onClose());
      this.observer = new ResizeObserver(() => this.positionMarkers()); this.observer.observe(container);
    }
    setEvents(events, saved, origin = null) {
      this.markerLayer.replaceChildren(); this.entries = [];
      const groups = new Map();
      for (const event of events.filter(e => e.location)) {
        const girls = /girls|female/i.test(event.name + ' ' + event.grades);
        const campus = `${event.location.lat},${event.location.lng}`;
        const inDatabase = Boolean(event.inDatabase || event.recordSlugs?.length);
        const key = campus + (girls ? ':girls' : ':open') + (inDatabase ? ':records' : ':new');
        if (!groups.has(key)) groups.set(key, { events: [], girls, campus, inDatabase });
        groups.get(key).events.push(event);
      }
      for (const group of groups.values()) {
        const first = group.events[0];
        const point = this.projection([first.location.lng, first.location.lat]);
        if (!point) continue;
        const marker = document.createElement('button'); marker.type = 'button';
        marker.className = ['map-pin', group.girls ? 'girls' : '', group.inDatabase ? 'in-database' : '', group.events.some(e => saved.has(e.id)) ? 'saved' : ''].filter(Boolean).join(' ');
        marker.title = group.events.map(e => e.name).join(', ') + (group.inDatabase ? ' · Results in database' : '') + (group.girls ? ' · Girls / gender eligibility applies' : ''); marker.setAttribute('aria-label', marker.title);
        marker.setAttribute('aria-expanded', 'false'); marker.setAttribute('aria-controls', 'us-map-popup');
        if (group.events.length > 1) marker.textContent = group.events.length;
        marker.addEventListener('click', event => { event.stopPropagation(); this.onSelect(marker, group.events); });
        this.markerLayer.append(marker);
        const neighbors = [...groups.values()].filter(g => g.campus === group.campus);
        const offset = (neighbors.indexOf(group) - (neighbors.length - 1) / 2) * 40;
        this.entries.push({ marker, events: group.events, point, offset });
      }
      if (origin) {
        const point = this.projection([origin.lng, origin.lat]);
        if (point) {
          const marker = document.createElement('div');
          marker.className = 'map-pin home origin-pin'; marker.setAttribute('role', 'img');
          marker.title = 'Your starting location (approximate)';
          marker.setAttribute('aria-label', marker.title);
          this.markerLayer.append(marker);
          this.entries.push({ marker, events: [], point, offset: 0 });
        }
      }
      this.positionMarkers();
    }
    positionMarkers() {
      const { width, height } = this.container.getBoundingClientRect();
      const scale = Math.min(width / 1000, height / 640);
      const dx = (width - 1000 * scale) / 2, dy = (height - 640 * scale) / 2;
      for (const entry of this.entries) {
        const p = this.transform.apply(entry.point);
        entry.marker.style.left = `${dx + p[0] * scale + entry.offset}px`;
        entry.marker.style.top = `${dy + p[1] * scale}px`;
      }
    }
    reset() { this.svg.call(this.zoom.transform, d3.zoomIdentity); }
    zoomBy(factor) { this.svg.transition().duration(window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ? 0 : 180).call(this.zoom.scaleBy, factor); }
    focus(id) {
      const entry = this.entries.find(e => e.events.some(event => event.id === id));
      if (!entry) return;
      this.svg.call(this.zoom.transform, d3.zoomIdentity.translate(500, 320).scale(3).translate(-entry.point[0], -entry.point[1]));
      this.onSelect(entry.marker, entry.events); entry.marker.focus({ preventScroll: true });
    }
  }
  window.CompetitionUSMap = CompetitionUSMap;
})();
