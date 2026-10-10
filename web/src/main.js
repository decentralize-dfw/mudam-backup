import './style.css';
import * as THREE from 'three';
import { Stage, PLAN_AZIMUTH } from './engine/scene.js';
import { FLOOR_Y, CUTS, FLOORS } from './engine/building.js';
import { clock } from './engine/daylight.js';
import { BUILDING_HOTSPOTS } from './content/building.js';
import { SURROUNDING_HOTSPOTS } from './content/surroundings.js';
import { EXHIBITIONS, OTHER_ROOMS } from './content/exhibitions.js';
import { i18n, t, pick } from './i18n.js';
import { MaterialExplode, LAYERS, LAYER_COLOURS } from './engine/explode.js';

const BASE = './demo/';
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const rad = (d) => (d * Math.PI) / 180;
const azimuth = (bearing) => Math.atan2(Math.sin(rad(bearing)), -Math.cos(rad(bearing)));
const polar = (tilt) => rad(90 - tilt);
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const el = (html) => { const d = document.createElement('div'); d.innerHTML = html.trim(); return d.firstElementChild; };

// Bearing: compass direction the camera stands at, seen from the target.
// The official plans put the entrance at the bottom: that is bearing 47°.
const PLAN_BEARING = 47;
const HOME = {
  building: { target: [2, 5, 4], bearing: 204, tilt: 31, zoom: 1.0 },
  surroundings: { target: [-20, 0, 10], bearing: 222, tilt: 40, zoom: 0.24 },
  explode: { target: [3, 20, -6], bearing: 22, tilt: 30, zoom: 0.62 },
  exhibitionsOverview: { target: [3, 12, -6], bearing: 22, tilt: 36, zoom: 0.78 },
};
// Malzemelere ayır: framing for the two exploded readings
const MAT_VIEW = {
  vertical: { target: [-1, 74, 2], bearing: 210, tilt: 22, zoom: 0.45, span: 150 },
  radial: { target: [-1, 52, 2], bearing: 210, tilt: 20, zoom: 0.55, span: 320 },
};
const MAT_SLUG = { vertical: 'malzeme-dikey', radial: 'malzeme-kure' };
const FLOOR_VIEW = {
  LM1: { target: [-2, FLOOR_Y.LM1, -6], bearing: 18, tilt: 52, zoom: 1.2 },
  L00: { target: [0, FLOOR_Y.L00, 0], bearing: 18, tilt: 52, zoom: 1.0 },
  LP1: { target: [2, FLOOR_Y.LP1, -10], bearing: 18, tilt: 52, zoom: 1.15 },
};

class App {
  constructor() {
    this.app = $('#app');
    this.stage = new Stage($('#viewport'), BASE);
    this.s = { mode: 'building', floor: 'all', explode: false, plan: false, hotspot: null, exhibition: null, room: null, artwork: null, visit: false, mat: 'off', hour: 13.5, day: 283, lights: false, lightsAuto: true };
    this.pointer = { x: 0, y: 0, down: null };
    window.__mudam = this; // QA hook
    window.THREE = THREE;
  }

  async boot() {
    this.applyLanguage();
    this.bindUI();
    try {
      const data = await this.stage.load((p) => { $('#boot-fill').style.width = `${Math.round(p * 100)}%`; });
      this.data = data;
    } catch (e) {
      console.error(e);
      $('#boot-status').textContent = t('no3d');
      $('#retry').hidden = false;
      this.app.dataset.siteReady = 'error';
      return;
    }
    $('#boot-status').textContent = t('loadingData');
    this.roomsById = new Map(this.data.rooms.rooms.map((r) => [r.id, r]));
    this.exhibitionOfRoom = new Map();
    for (const ex of EXHIBITIONS) for (const r of ex.rooms) this.exhibitionOfRoom.set(r.id, ex);
    this.stage.rooms.init(this.data.rooms, (r) => this.exhibitionOfRoom.get(r.id)?.colour ?? 0x8f948f);
    await this.stage.artworks.init(this.data.artworks, this.roomsById);
    this.orderArtworks();
    // material layers: patch the visible building band, then the trails
    this.mx = new MaterialExplode(this.stage.scene);
    this.mx.attach(this.stage.building.bands[0].group);
    this.mx.onChange = () => {
      const b = this.stage.building, open = this.mx.amount > 1e-4;
      if (open !== Boolean(b.unclipped)) { b.unclipped = open; b.apply(); }
      this.stage.dirty = true;
      this.stage.renderer.shadowMap.needsUpdate = true;
    };
    try {
      const pieces = await fetch(`${BASE}data/pieces.json`).then((r) => r.json());
      this.mx.build(pieces);
    } catch (e) { console.warn('pieces.json', e); }
    this.renderLayerList();
    this.setupLights();
    this.stage.daylight.set(this.s.hour, this.s.day);
    this.stage.rig.setPose(this.poseOf(HOME.building));
    this.stage.start();
    addEventListener('resize', () => this.updateInsets());
    this.stage.frameHooks.add(() => this.frame());
    this.app.dataset.ready = 'true';
    document.title = t('docTitle');
    const deep = this.readHash();
    if (deep) {
      this.app.dataset.booting = 'false';
      await this.go(deep);
    } else {
      $('#boot-actions').hidden = false;
      this.setMode('building', { fly: false });
    }
    this.stage.siteReady.then(() => {
      this.stage.context.setMassing(this.s.mode === 'surroundings' ? 1 : 0.85);
      this.tuneSite();
      this.stage.contextFade = 1; // new materials: let the current fade re-apply to them
      this.applyVisibility();
      this.app.dataset.siteReady = 'true';
    });
  }

  // ------------------------------------------------------------ helpers
  poseOf(v) {
    return { target: new THREE.Vector3(...v.target), azimuth: azimuth(v.bearing), polar: polar(v.tilt), zoom: v.zoom };
  }

  fly(v, ms) {
    const pose = this.poseOf(v);
    if (this.s.plan) { pose.polar = 1e-4; pose.azimuth = azimuth(PLAN_BEARING); }
    this.focusShadows(pose.target, v.zoom);
    return this.stage.rig.flyTo(pose, ms);
  }

  focusShadows(target, zoom) {
    const r = THREE.MathUtils.clamp(70 / Math.max(zoom, 0.05), 85, 520);
    this.stage.daylight.setShadowFocus(new THREE.Vector3(target.x, 0, target.z), r);
  }

  buildingState() { return this.s.explode ? 'explode' : this.s.floor; }

  // ----------------------------------------------------------- UI wiring
  bindUI() {
    $$('.mode-picker button').forEach((b) => b.addEventListener('click', () => this.setMode(b.dataset.mode)));
    $$('.floor-row button').forEach((b) => b.addEventListener('click', () => this.setFloor(b.dataset.floor)));
    $('#toggle-explode').addEventListener('click', () => this.setExplode(!this.s.explode));
    $('#toggle-plan').addEventListener('click', () => this.setPlan(!this.s.plan));
    $('#toggle-materials').addEventListener('click', () => this.setMaterials(this.s.mat === 'off' ? 'vertical' : 'off'));
    $$('[data-mat]').forEach((b) => b.addEventListener('click', () => this.setMaterials(b.dataset.mat)));
    $('#zoom-in').addEventListener('click', () => this.zoomBy(1.35));
    $('#zoom-out').addEventListener('click', () => this.zoomBy(1 / 1.35));
    $('#recentre').addEventListener('click', () => this.recentre());
    $('#card-close').addEventListener('click', () => this.closeCard());
    $('#hour').addEventListener('input', (e) => this.setHour(+e.target.value));
    $('#day').addEventListener('change', (e) => { this.s.day = +e.target.value; this.stage.daylight.set(this.s.hour, this.s.day); });
    $('#toggle-lights').addEventListener('click', () => { this.s.lightsAuto = false; this.setLights(!this.s.lights); });
    $$('.lang-flag').forEach((b) => b.addEventListener('click', () => { i18n.set(b.dataset.lang); this.applyLanguage(); this.rerender(); }));
    $('#open-about').addEventListener('click', () => { $('#about').hidden = !$('#about').hidden; });
    $$('[data-close="about"]').forEach((b) => b.addEventListener('click', () => { $('#about').hidden = true; }));
    $('#lightbox-close').addEventListener('click', () => { $('#lightbox').hidden = true; });
    $('#lightbox').addEventListener('click', (e) => { if (e.target.id === 'lightbox') $('#lightbox').hidden = true; });
    $$('[data-start]').forEach((b) => b.addEventListener('click', () => { this.app.dataset.booting = 'false'; this.setMode(b.dataset.start); }));
    $('#retry').addEventListener('click', () => location.reload());
    addEventListener('keydown', (e) => {
      if (e.target.closest?.('input,select,textarea')) return;
      if (e.key === 'Escape') this.back();
      if (e.key === 'ArrowRight') this.step(1);
      if (e.key === 'ArrowLeft') this.step(-1);
    });
    addEventListener('hashchange', () => { if (this.ignoreHash) return; const d = this.readHash(); if (d) this.go(d); });
    const canvas = this.stage.renderer.domElement;
    canvas.addEventListener('pointerdown', (e) => { this.pointer.down = { x: e.clientX, y: e.clientY, t: performance.now() }; });
    canvas.addEventListener('pointerup', (e) => {
      const d = this.pointer.down; this.pointer.down = null;
      if (!d || Math.hypot(e.clientX - d.x, e.clientY - d.y) > 6 || performance.now() - d.t > 600) return;
      this.click(e);
    });
    canvas.addEventListener('pointermove', (e) => { if (e.pointerType === 'mouse' && !this.pointer.down) this.hover(e); });
  }

  applyLanguage() {
    document.documentElement.lang = i18n.lang;
    $$('[data-i18n]').forEach((n) => { n.textContent = t(n.dataset.i18n); });
    $$('[data-i18n-label]').forEach((n) => n.setAttribute('aria-label', t(n.dataset.i18nLabel)));
    $$('[data-i18n-title]').forEach((n) => n.setAttribute('title', t(n.dataset.i18nTitle)));
    $$('.lang-flag').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.lang === i18n.lang)));
    $('#about-body').innerHTML = t('aboutBody').map((p) => `<p>${esc(p)}</p>`).join('') + this.sourcesHtml();
    if (this.data) document.title = t('docTitle');
  }

  sourcesHtml() {
    return `<h3 class="kicker">${esc(t('sources'))}</h3><ul>
      <li>mudam.com — architecture, visit, exhibitions (Kaihō, Christine Sun Kim: FOR EVER, Video Killed the Radio Star)</li>
      <li>WikiArquitectura, ArchEyes (MUDAM, I. M. Pei / Pei Cobb Freed &amp; Partners)</li>
      <li>Great Gardens of the World — Michel Desvigne, Dräi Eechelen Park</li>
      <li>OpenStreetMap contributors (ODbL)</li></ul>`;
  }

  rerender() {
    this.renderMarkers();
    if (this.s.mode === 'exhibitions') this.renderSheet();
    if (this.s.artwork) this.renderArtworkCard();
    else if (this.s.room) this.renderRoomCard();
    else if (this.s.hotspot) this.renderHotspotCard();
    this.updateHint();
  }

  // --------------------------------------------------------------- modes
  async setMode(mode, { fly = true } = {}) {
    const prev = this.s.mode;
    await this.leaveMaterials();
    this.s.mode = mode;
    this.app.dataset.mode = mode;
    $$('.mode-picker button').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.mode === mode)));
    this.s.hotspot = null;
    if (this.s.visit) await this.leaveVisit(false);
    this.s.room = null; this.s.artwork = null;
    this.closeCard(true);
    $('#sheet').hidden = mode !== 'exhibitions';
    this.updateInsets();
    if (mode === 'exhibitions') {
      this.s.exhibition = null;
      this.s.plan = false; this.stage.rig.setPlan(false);
      this.s.explode = true; this.s.floor = 'all';
      this.renderSheet();
      this.syncControls();
      this.applyVisibility();
      this.renderMarkers();
      const p = this.stage.building.setState('explode', this.stage.tweens);
      if (fly) await Promise.all([p, this.fly(HOME.exhibitionsOverview)]);
    } else {
      this.s.exhibition = null;
      this.s.explode = false; this.s.floor = 'all';
      this.s.plan = false; this.stage.rig.setPlan(false);
      this.syncControls();
      this.applyVisibility();
      this.renderMarkers();
      const p = this.stage.building.setState('all', this.stage.tweens);
      if (fly) await Promise.all([p, this.fly(mode === 'surroundings' ? HOME.surroundings : HOME.building, prev === mode ? 900 : 1500)]);
    }
    this.writeHash();
    this.updateHint();
  }

  async setFloor(floor) {
    if (this.s.mode === 'surroundings') return;
    await this.leaveMaterials();
    if (this.s.visit) await this.leaveVisit(false);
    this.s.floor = floor;
    this.s.explode = false;
    if (floor === 'all' && this.s.plan) { this.s.plan = false; this.stage.rig.setPlan(false); }
    this.syncControls();
    this.applyVisibility();
    this.renderMarkers();
    const p = this.stage.building.setState(this.buildingState(), this.stage.tweens);
    const view = floor === 'all' ? HOME.building : FLOOR_VIEW[floor];
    if (floor !== 'all') this.stage.artworks.load(floor);
    await Promise.all([p, this.fly(view)]);
    if (this.s.mode === 'exhibitions' && !this.s.room) this.renderSheet();
    this.writeHash();
    this.updateHint();
  }

  async setExplode(on) {
    await this.leaveMaterials();
    if (this.s.visit) await this.leaveVisit(false);
    this.s.explode = on;
    if (on) { this.s.plan = false; this.stage.rig.setPlan(false); this.s.floor = 'all'; }
    this.syncControls();
    this.applyVisibility();
    this.renderMarkers();
    if (on) FLOORS.forEach((f) => this.stage.artworks.load(f));
    const p = this.stage.building.setState(this.buildingState(), this.stage.tweens);
    const overview = this.s.mode === 'exhibitions' ? HOME.exhibitionsOverview : HOME.explode;
    await Promise.all([p, this.fly(on ? overview : HOME.building)]);
    this.writeHash();
    this.updateHint();
  }

  async setPlan(on) {
    if (this.s.mode === 'surroundings') return;
    await this.leaveMaterials();
    if (this.s.visit) await this.leaveVisit(false);
    if (on && (this.s.floor === 'all' || this.s.explode)) {
      const ex = EXHIBITIONS.find((e) => e.id === this.s.exhibition);
      const room = this.s.room && this.roomsById.get(this.s.room);
      this.s.floor = room?.floor ?? ex?.start ?? 'L00';
      this.s.explode = false;
      this.stage.building.setState(this.buildingState(), this.stage.tweens);
      this.stage.artworks.load(this.s.floor);
    }
    this.s.plan = on;
    this.stage.rig.setPlan(on);
    this.syncControls();
    this.applyVisibility();
    this.renderMarkers();
    const room = this.s.room && this.roomsById.get(this.s.room);
    if (room && room.floor === this.s.floor) await this.frameRoom(room);
    else await this.fly(FLOOR_VIEW[this.s.floor]);
    this.writeHash();
    this.updateHint();
  }

  // ------------------------------------------------- material layers
  async setMaterials(mode, { fly = true } = {}) {
    if (!this.mx) return;
    if (mode !== 'off' && this.s.mode !== 'building') {
      this.s.mode = 'building'; this.app.dataset.mode = 'building';
      $$('.mode-picker button').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.mode === 'building')));
      $('#sheet').hidden = true; this.s.exhibition = null; this.s.room = null;
    }
    if (this.s.visit) await this.leaveVisit(false);
    const prev = this.s.mat;
    if (prev === mode) return;
    this.s.mat = mode;
    this.s.hotspot = null;
    this.closeCard(true);
    if (mode !== 'off') { this.s.explode = false; this.s.floor = 'all'; this.s.plan = false; this.stage.rig.setPlan(false); }
    else this.mx.resetLayers();
    this.syncControls();
    this.applyVisibility();
    this.renderMarkers();
    this.renderLayerList();
    const steps = [];
    if (mode !== 'off' && this.stage.building.state !== 'all') steps.push(this.stage.building.setState('all', this.stage.tweens));
    steps.push(this.mx.set(mode, this.stage.tweens, prev !== 'off' && mode !== 'off' ? 1500 : 1800));
    if (fly) steps.push(this.fly(mode === 'off' ? HOME.building : this.fitWidth(MAT_VIEW[mode]), 1800));
    await Promise.all(steps);
    this.renderMarkers();
    this.writeHash();
    this.updateHint();
  }

  // On a narrow screen, zoom out until `span` metres fit across the width.
  fitWidth(view) {
    const host = this.stage.host, w = host.clientWidth, h = host.clientHeight;
    const across = (this.stage.rig.viewSize * w) / Math.min(w, h);
    return view.span ? { ...view, zoom: Math.min(view.zoom, across / view.span) } : view;
  }

  leaveMaterials() {
    return this.s.mat === 'off' ? Promise.resolve() : this.setMaterials('off', { fly: false });
  }

  renderLayerList() {
    const list = $('#layer-list');
    if (!list) return;
    list.innerHTML = LAYERS.map((l) => `<button class="layer-chip" data-layer="${l}" style="--c:${LAYER_COLOURS[l]}" aria-pressed="${!this.mx?.hidden.has(l)}"><i></i>${esc(t('layer_' + l))}</button>`).join('');
    $$('[data-layer]', list).forEach((b) => b.addEventListener('click', () => this.toggleLayer(b.dataset.layer)));
  }

  toggleLayer(layer) {
    const on = this.mx.hidden.has(layer);
    this.mx.setLayerVisible(layer, on);
    this.renderLayerList();
  }

  syncControls() {
    $$('.floor-row button').forEach((b) => b.setAttribute('aria-pressed', String(!this.s.explode && this.s.mat === 'off' && b.dataset.floor === this.s.floor)));
    $('#toggle-materials').setAttribute('aria-pressed', String(this.s.mat !== 'off'));
    $('#layer-panel').hidden = this.s.mat === 'off';
    $$('[data-mat]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.mat === this.s.mat)));
    this.app.dataset.mat = this.s.mat === 'off' ? 'off' : 'on';
    $('#toggle-explode').setAttribute('aria-pressed', String(this.s.explode));
    $('#toggle-plan').setAttribute('aria-pressed', String(this.s.plan));
    this.app.dataset.visit = String(this.s.visit);
  }

  // What is drawn in each state: context, trees, room tints, plan dots.
  applyVisibility() {
    const st = this.stage;
    const cut = this.s.explode || this.s.floor !== 'all';
    // while the building is taken apart (floors or materials) the whole
    // surroundings model stays in place at 20 % opacity
    const exploded = this.s.explode || this.s.mat !== 'off';
    st.setContextFade(exploded ? 0.2 : 1);
    if (st.trees) st.trees.visible = exploded || (!cut && !this.s.visit);
    // neighbours stay out of the way of close building views
    st.context.setMassing(this.s.mode === 'surroundings' || exploded ? 1 : cut || this.s.hotspot ? 0.0 : 0.85);
    if (st.context.ground) st.context.ground.visible = true;
    const showRooms = !this.s.visit && (this.s.mode === 'exhibitions' || this.s.plan) && cut;
    const ex = EXHIBITIONS.find((e) => e.id === this.s.exhibition);
    st.rooms.selected = this.s.room;
    st.rooms.refresh({ show: showRooms, exhibitionRooms: ex ? new Set(ex.rooms.map((r) => r.id)) : (this.s.mode === 'exhibitions' ? new Set(this.exhibitionOfRoom.keys()) : null) });
    st.artworks.setPlanMarkers(this.s.plan && !this.s.visit);
    st.building.visitFloor = this.s.visit ? this.roomsById.get(this.s.room)?.floor : null;
    st.building.roofVisible = this.s.mode !== 'exhibitions';
    st.building.apply();
    st.scene.background = this.s.visit ? null : st.daylight.backgroundColor(new THREE.Color());
    if (this.s.visit) { st.scene.background = new THREE.Color(0xdfe3e1); }
    // rooms under glass are bright at midday: expose for the walls, not the sky
    st.renderer.toneMappingExposure = this.s.visit ? 0.8 : 1.0;
    st.dirty = true;
  }

  // ------------------------------------------------------------- markers
  renderMarkers() {
    const m = this.stage.markers;
    m.clear();
    if (this.s.visit) return;
    if (this.s.mat !== 'off' && this.mx?.anchors) {
      LAYERS.forEach((l, i) => {
        const it = m.add({
          id: `layer:${l}`, kind: 'layername', position: [0, 0, 0], label: t('layer_' + l),
          pos: () => this.mx.labelPosition(i),
          visible: () => this.mx.amount > 0.55 && !this.mx.hidden.has(l),
          onClick: () => this.toggleLayer(l),
        });
        it.el.style.setProperty('--c', LAYER_COLOURS[l]);
      });
      return;
    }
    if (this.s.mode === 'surroundings') {
      SURROUNDING_HOTSPOTS.forEach((h, i) => m.add({ id: h.id, position: h.at, label: pick(h).title, index: i + 1, onClick: () => this.openHotspot(h.id) }).el.classList.add('labelled'));
    } else if (this.s.mode === 'building' && !this.s.plan) {
      BUILDING_HOTSPOTS.forEach((h, i) => m.add({
        id: h.id, position: h.at, normal: h.n, label: pick(h).title, index: i + 1, kind: h.kind,
        visible: () => this.hotspotVisible(h),
        onClick: () => this.openHotspot(h.id),
      }));
    }
    if (this.s.mode === 'exhibitions' && !this.s.exhibition && this.s.explode) {
      // overview: one pin per exhibition, on its first room
      const pinRoom = { kaiho: 'galerie-est-1', vktrs: 'galerie-ouest-m1', forever: 'pavillon' };
      for (const ex of EXHIBITIONS) {
        const r = this.roomsById.get(pinRoom[ex.id] ?? ex.rooms[0].id);
        const item = m.add({
          id: `ex:${ex.id}`, kind: 'exhibition', position: [r.anchor[0], r.y + 3.4, r.anchor[1]],
          label: `${ex.title} · ${pick(ex.subtitle)}`,
          lift: () => this.stage.building.lift(r.floor),
          onClick: () => this.openExhibition(ex.id),
        });
        item.el.style.setProperty('--room', ex.css);
      }
      return;
    }
    if (this.s.mode === 'exhibitions' || this.s.plan) {
      const ex = EXHIBITIONS.find((e) => e.id === this.s.exhibition);
      for (const r of this.data.rooms.rooms) {
        const exOf = this.exhibitionOfRoom.get(r.id);
        const inShow = ex ? exOf === ex : Boolean(exOf);
        if (this.s.mode === 'exhibitions' && !inShow && !OTHER_ROOMS[r.id]) continue;
        if (r.kind === 'link' && r.id !== 'passage' && r.id !== 'pont') continue;
        const item = m.add({
          id: `room:${r.id}`, kind: 'room', position: [r.anchor[0], r.y + 0.4, r.anchor[1]],
          label: this.roomLabel(r),
          lift: () => this.stage.building.lift(r.floor),
          visible: () => this.roomMarkerVisible(r),
          onClick: () => this.openRoom(r.id),
        });
        item.el.style.setProperty('--room', exOf?.css ?? '#8f948f');
        if (!inShow) item.el.classList.add('dim');
      }
    }
    m.setActive(this.s.hotspot ?? (this.s.room ? `room:${this.s.room}` : null));
  }

  roomLabel(r) {
    const base = r.label;
    return base;
  }

  roomMarkerVisible(r) {
    if (this.s.visit) return false;
    if (this.s.explode) return this.s.mode === 'exhibitions';
    return this.s.floor === r.floor && !this.stage.building.moving;
  }

  hotspotVisible(h) {
    if (this.s.mat !== 'off') return false;
    const st = this.stage.building.state;
    if (st === 'explode') return false;
    if (st === 'all') return (h.view.state ?? 'all') === 'all' || h.at[1] < 16;
    return h.at[1] < CUTS[st] + 0.5 && h.at[1] > FLOOR_Y[st] - 0.5;
  }

  // ------------------------------------------------------------ hotspots
  hotspots() { return this.s.mode === 'surroundings' ? SURROUNDING_HOTSPOTS : BUILDING_HOTSPOTS; }

  async openHotspot(id) {
    await this.leaveMaterials();
    const list = this.hotspots();
    const h = list.find((x) => x.id === id);
    if (!h) return;
    this.s.hotspot = id;
    this.stage.markers.setActive(id);
    this.renderHotspotCard();
    this.applyVisibility();
    const v = h.view;
    if (v.hour != null) this.setHour(v.hour);
    const want = v.state ?? (this.s.mode === 'surroundings' ? 'all' : this.s.floor);
    let p = Promise.resolve();
    if (this.s.mode === 'building' && (want !== this.buildingState())) {
      this.s.explode = false;
      this.s.floor = want;
      this.syncControls();
      this.applyVisibility();
      p = this.stage.building.setState(want, this.stage.tweens);
    }
    this.writeHash();
    await Promise.all([p, this.fly(v)]);
  }

  renderHotspotCard() {
    const list = this.hotspots();
    const i = list.findIndex((x) => x.id === this.s.hotspot);
    if (i < 0) return;
    const h = list[i], c = pick(h);
    this.showCard(`
      <p class="kicker">${esc(c.kicker)}</p>
      <h2>${esc(c.title)}</h2>
      ${c.body.map((p) => `<p>${esc(p)}</p>`).join('')}
      <div class="card-nav">
        <button data-step="-1">← ${esc(t('prev'))}</button>
        <span class="count">${i + 1} ${t('of')} ${list.length}</span>
        <button data-step="1">${esc(t('next'))} →</button>
      </div>`);
  }

  // ----------------------------------------------------------- exhibitions
  orderArtworks() {
    // visiting order: exhibition, then its rooms in curatorial order, then wall order
    const order = [];
    for (const ex of EXHIBITIONS) {
      for (const r of ex.rooms) {
        const list = this.stage.artworks.items.filter((a) => a.room === r.id);
        order.push(...list);
      }
    }
    this.byExhibition = new Map(EXHIBITIONS.map((ex) => [ex.id, order.filter((a) => a.exhibition === ex.id)]));
    for (const list of this.byExhibition.values()) list.forEach((a, i) => { a.n = i + 1; });
  }

  renderSheet() {
    const sheet = $('#sheet-body');
    const ex = EXHIBITIONS.find((e) => e.id === this.s.exhibition);
    if (!ex) {
      sheet.innerHTML = `
        <h2>${esc(t('exhibitionsHeading'))}</h2>
        <p class="lead">${esc(t('exhibitionsLead'))}</p>
        ${EXHIBITIONS.map((e) => `
          <button class="ex-card" data-ex="${e.id}" style="--c:${e.css}">
            <span class="ex-title">${esc(e.title)}</span>
            <span class="ex-sub">${esc(pick(e.subtitle))}</span>
            <span class="ex-meta">${esc(pick(e.place))} · ${esc(pick(e.dates))}</span>
          </button>`).join('')}
        <p class="small-note">${esc(t('placeholderNote'))}</p>`;
      $$('[data-ex]', sheet).forEach((b) => b.addEventListener('click', () => this.openExhibition(b.dataset.ex)));
      return;
    }
    const works = this.byExhibition.get(ex.id) ?? [];
    sheet.innerHTML = `
      <button class="back" data-back="list">← ${esc(t('backToList'))}</button>
      <p class="kicker" style="color:${ex.css}">${esc(pick(ex.place))}</p>
      <h2>${esc(ex.title)}</h2>
      <p class="lead" style="margin-bottom:4px"><strong>${esc(pick(ex.subtitle))}</strong><br/>${esc(pick(ex.dates))}</p>
      ${pick(ex.intro).map((p) => `<p class="lead">${esc(p)}</p>`).join('')}
      <p class="small-note">${esc(pick(ex.credits))}</p>
      ${ex.next ? `<p class="small-note">${esc(pick(ex.next))}</p>` : ''}
      <div class="actions">
        <button data-walk="works" ${works.length ? '' : 'disabled'}>${esc(t('walkWorks'))}</button>
        <button data-walk="rooms" class="secondary">${esc(t('walkRooms'))}</button>
      </div>
      <h3>${esc(t('rooms'))}</h3>
      <div class="room-list">
        ${ex.rooms.map((r) => {
          const room = this.roomsById.get(r.id);
          const n = works.filter((a) => a.room === r.id).length;
          return `<button class="room-item ${r.closed ? 'closed' : ''}" data-room="${r.id}" style="--c:${ex.css}" aria-current="${this.s.room === r.id}">
            <span class="floor">${esc(t('floor' + room.floor))}</span><span class="dot"></span>
            <span>${esc(pick(r).title)}<br/><small style="opacity:.7" lang="fr">${esc(room.label)}</small></span>
            <span class="meta">${r.closed ? '—' : `${n} ${esc(t('works'))}`}</span></button>`;
        }).join('')}
      </div>
      <p class="small-note">${esc(t('readingNote'))}</p>`;
    $('[data-back]', sheet).addEventListener('click', () => this.listExhibitions());
    $$('[data-room]', sheet).forEach((b) => b.addEventListener('click', () => this.openRoom(b.dataset.room)));
    $('[data-walk="works"]', sheet).addEventListener('click', () => { const first = works[0]; if (first) this.openArtwork(first.id); });
    $('[data-walk="rooms"]', sheet).addEventListener('click', () => this.openRoom(ex.rooms[0].id));
  }

  async listExhibitions() {
    if (this.s.visit) await this.leaveVisit(false);
    this.s.exhibition = null; this.s.room = null; this.s.artwork = null;
    this.closeCard(true);
    this.s.explode = true; this.s.floor = 'all'; this.s.plan = false; this.stage.rig.setPlan(false);
    this.renderSheet(); this.syncControls(); this.applyVisibility(); this.renderMarkers();
    await Promise.all([this.stage.building.setState('explode', this.stage.tweens), this.fly(HOME.exhibitionsOverview)]);
    this.writeHash();
  }

  async openExhibition(id, { fly = true } = {}) {
    const ex = EXHIBITIONS.find((e) => e.id === id);
    if (!ex) return;
    if (this.s.mode !== 'exhibitions') { this.s.mode = 'exhibitions'; this.app.dataset.mode = 'exhibitions'; $$('.mode-picker button').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.mode === 'exhibitions'))); $('#sheet').hidden = false; this.updateInsets(); }
    if (this.s.visit) await this.leaveVisit(false);
    this.s.exhibition = id; this.s.room = null; this.s.artwork = null;
    this.closeCard(true);
    this.renderSheet();
    this.s.explode = false; this.s.floor = ex.start;
    this.syncControls(); this.applyVisibility(); this.renderMarkers();
    this.stage.artworks.load(ex.start);
    const p = this.stage.building.setState(ex.start, this.stage.tweens);
    if (fly) {
      const rooms = ex.rooms.map((r) => this.roomsById.get(r.id)).filter((r) => r.floor === ex.start && !ex.rooms.find((x) => x.id === r.id).closed);
      await Promise.all([p, this.frameRooms(rooms)]);
    }
    this.writeHash();
    this.updateHint();
  }

  frameRooms(rooms, ms) {
    const box = new THREE.Box3();
    for (const r of rooms) for (const [x, z] of r.polygon) box.expandByPoint(new THREE.Vector3(x, r.y, z));
    const c = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());
    const span = Math.max(size.x, size.z) * 1.15 + 14;
    const zoom = THREE.MathUtils.clamp(this.stage.rig.viewSize / span * this.fitAspect(), 0.5, 8);
    return this.fly({ target: [c.x, rooms[0]?.y ?? 0, c.z], bearing: this.s.plan ? PLAN_BEARING : 18, tilt: this.s.plan ? 90 : 52, zoom }, ms);
  }

  fitAspect() {
    // the room should clear the side sheet and card on wide screens
    const w = innerWidth, h = innerHeight;
    return w > 900 ? Math.min(1, (w - 760) / h) * 1.05 : 0.9;
  }

  frameRoom(room, ms) { return this.frameRooms([room], ms); }

  async openRoom(id) {
    const room = this.roomsById.get(id);
    if (!room) return;
    await this.leaveMaterials();
    const ex = this.exhibitionOfRoom.get(id);
    if (this.s.visit) await this.leaveVisit(false);
    if (ex && this.s.mode !== 'exhibitions') {
      this.s.mode = 'exhibitions'; this.app.dataset.mode = 'exhibitions';
      $$('.mode-picker button').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.mode === 'exhibitions')));
      $('#sheet').hidden = false;
      this.updateInsets();
    }
    if (ex) this.s.exhibition = ex.id;
    this.s.room = id; this.s.artwork = null; this.s.hotspot = null;
    const floorChange = this.s.explode || this.s.floor !== room.floor;
    this.s.explode = false; this.s.floor = room.floor;
    this.syncControls(); this.applyVisibility(); this.renderMarkers();
    if (this.s.mode === 'exhibitions') this.renderSheet();
    this.renderRoomCard();
    this.stage.artworks.load(room.floor);
    const p = floorChange ? this.stage.building.setState(room.floor, this.stage.tweens) : Promise.resolve();
    this.stage.artworks.focusRoom(id).then(() => { this.stage.dirty = true; });
    this.placeRoomLights(room.floor);
    this.writeHash();
    await Promise.all([p, this.frameRoom(room)]);
    this.updateHint();
  }

  renderRoomCard() {
    const room = this.roomsById.get(this.s.room);
    if (!room) return;
    const ex = this.exhibitionOfRoom.get(room.id);
    if (!ex) {
      const o = OTHER_ROOMS[room.id];
      this.showCard(`<p class="kicker">${esc(t('floorName' + room.floor))} · ${esc(t('notExhibition'))}</p>
        <h2>${esc(o ? pick(o).title : room.label)}</h2>${o ? `<p>${esc(pick(o).text)}</p>` : ''}`);
      return;
    }
    const r = ex.rooms.find((x) => x.id === room.id);
    const i = ex.rooms.indexOf(r);
    const works = (this.byExhibition.get(ex.id) ?? []).filter((a) => a.room === room.id);
    this.showCard(`
      <span class="tag" style="--c:${ex.css}"><i></i>${esc(ex.title)}</span>
      <p class="kicker"><span lang="fr">${esc(room.label)}</span> · ${esc(t('floorName' + room.floor))}</p>
      <h2>${esc(pick(r).title)}</h2>
      <p>${esc(pick(r).text)}</p>
      ${r.closed ? `<p class="note">${esc(t('closedRoom'))}</p>` : `
        <h3 class="kicker" style="margin-top:14px">${esc(t('worksTitle'))} · ${works.length}</h3>
        <div class="thumbs">${works.map((a) => `<button data-art="${a.id}" title="${esc(t('work'))} ${a.n}">${a.kind === 'wall' ? `<img loading="lazy" src="${BASE}art/${a.id}-s.webp" alt="${esc(t('placeholder'))} ${a.n}"/>` : `<img loading="lazy" src="${BASE}art/${a.id}-s.webp" alt=""/>`}</button>`).join('')}</div>`}
      <div class="card-nav">
        <button data-step="-1">← ${esc(t('prev'))}</button>
        <span class="count">${esc(t('room'))} ${i + 1} ${t('of')} ${ex.rooms.length}</span>
        <button data-step="1">${esc(t('next'))} →</button>
      </div>`);
    $$('[data-art]', $('#card-body')).forEach((b) => b.addEventListener('click', () => this.openArtwork(b.dataset.art)));
  }

  // --------------------------------------------------------------- works
  async openArtwork(id) {
    const a = this.stage.artworks.byId.get(id);
    if (!a) return;
    await this.leaveMaterials();
    const room = this.roomsById.get(a.room);
    const ex = this.exhibitionOfRoom.get(a.room);
    this.s.exhibition = ex.id;
    if (this.s.mode !== 'exhibitions') { this.s.mode = 'exhibitions'; this.app.dataset.mode = 'exhibitions'; $$('.mode-picker button').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.mode === 'exhibitions'))); $('#sheet').hidden = false; this.updateInsets(); }
    const roomChanged = this.s.room !== a.room;
    this.s.room = a.room; this.s.artwork = id; this.s.hotspot = null;
    if (this.s.plan) { this.s.plan = false; this.stage.rig.setPlan(false); }
    this.renderSheet();
    this.renderArtworkCard();
    this.stage.artworks.load(room.floor);
    await this.stage.artworks.focusRoom(a.room);
    // arrive inside: keep the cut while flying, then close the roof over the room
    this.s.explode = false; this.s.floor = room.floor;
    if (!this.s.visit) {
      this.syncControls();
      if (this.stage.building.state !== room.floor) await this.stage.building.setState(room.floor, this.stage.tweens, 500);
    }
    this.s.visit = true;
    this.syncControls();
    this.renderMarkers();
    this.applyVisibility();
    this.placeRoomLights(room.floor, a);
    const vp = this.stage.artworks.viewpoint(a);
    this.focusShadows(vp.at, 3);
    if (roomChanged || this.stage.building.state !== 'all') {
      // full building once inside, so the room has its ceiling and light
      this.stage.building.setState('all', this.stage.tweens, 0);
    }
    this.stage.scene.background = new THREE.Color(0xdfe3e1);
    await this.stage.rig.visit(vp.eye, vp.at);
    this.writeHash();
    this.updateHint();
  }

  renderArtworkCard() {
    const a = this.stage.artworks.byId.get(this.s.artwork);
    if (!a) return;
    const ex = this.exhibitionOfRoom.get(a.room);
    const room = this.roomsById.get(a.room);
    const r = ex.rooms.find((x) => x.id === a.room);
    const list = this.byExhibition.get(ex.id);
    this.showCard(`
      <span class="tag" style="--c:${ex.css}"><i></i>${esc(ex.title)}</span>
      <img class="art-image" src="${BASE}art/${a.id}.webp" alt="${esc(t('placeholder'))}" data-enlarge />
      <span class="placeholder-badge">${esc(t('placeholder'))}</span>
      <h2>${esc(t('work'))} ${String(a.n).padStart(3, '0')}</h2>
      <p class="kicker">${esc(pick(r).title)} · <span lang="fr">${esc(room.label)}</span> · ${esc(t('floorName' + room.floor))}</p>
      <p class="note">${esc(t('placeholderNote'))}</p>
      <div class="actions"><button class="secondary" data-back-room>${esc(t('backToRoom'))}</button><button class="secondary" data-enlarge>${esc(t('enlarge'))}</button></div>
      <div class="card-nav">
        <button data-step="-1">← ${esc(t('prev'))}</button>
        <span class="count">${a.n} ${t('of')} ${list.length}</span>
        <button data-step="1">${esc(t('next'))} →</button>
      </div>`);
    $$('[data-enlarge]', $('#card-body')).forEach((b) => b.addEventListener('click', () => { $('#lightbox-img').src = `${BASE}art/${a.id}.webp`; $('#lightbox').hidden = false; }));
    $('[data-back-room]', $('#card-body')).addEventListener('click', () => this.openRoom(a.room));
  }

  async leaveVisit(refly = true) {
    if (!this.s.visit) return;
    this.s.visit = false;
    this.s.artwork = null;
    this.stage.rig.useOrtho();
    this.syncControls();
    await this.stage.building.setState(this.buildingState(), this.stage.tweens, 0);
    this.applyVisibility();
    this.renderMarkers();
    this.placeRoomLights(this.s.floor);
    if (refly && this.s.room) await this.frameRoom(this.roomsById.get(this.s.room), 900);
  }

  // ----------------------------------------------------- stepping / back
  step(dir) {
    if (this.s.artwork) {
      const a = this.stage.artworks.byId.get(this.s.artwork);
      const list = this.byExhibition.get(a.exhibition);
      const next = list[(list.indexOf(a) + dir + list.length) % list.length];
      return this.openArtwork(next.id);
    }
    if (this.s.room) {
      const ex = this.exhibitionOfRoom.get(this.s.room);
      if (!ex) return;
      const i = ex.rooms.findIndex((r) => r.id === this.s.room);
      return this.openRoom(ex.rooms[(i + dir + ex.rooms.length) % ex.rooms.length].id);
    }
    if (this.s.hotspot) {
      const list = this.hotspots();
      const i = list.findIndex((h) => h.id === this.s.hotspot);
      return this.openHotspot(list[(i + dir + list.length) % list.length].id);
    }
  }

  back() {
    if (!$('#lightbox').hidden) { $('#lightbox').hidden = true; return; }
    if (!$('#about').hidden) { $('#about').hidden = true; return; }
    if (this.s.artwork) return this.openRoom(this.s.room);
    if (this.s.room) { this.closeCard(); return; }
    if (this.s.hotspot) { this.closeCard(); return; }
    if (this.s.exhibition) return this.listExhibitions();
  }

  showCard(html) {
    $('#card-body').innerHTML = html;
    $('#card').hidden = false;
    this.app.dataset.card = 'true';
    $$('[data-step]', $('#card-body')).forEach((b) => b.addEventListener('click', () => this.step(+b.dataset.step)));
    this.updateInsets();
  }

  // Panels cover part of the canvas; the camera frames what remains.
  updateInsets() {
    const mobile = innerWidth <= 760;
    const sheet = $('#sheet'), card = $('#card');
    const ins = { left: 0, right: 0, bottom: 0 };
    if (mobile) {
      // on a phone the card replaces the sheet while it is open
      const tops = [sheet, card].filter((n) => !n.hidden && n.offsetParent).map((n) => n.getBoundingClientRect().top);
      if (tops.length) ins.bottom = Math.max(0, innerHeight - Math.min(...tops)) * 0.85;
    } else {
      if (!sheet.hidden) ins.left = sheet.getBoundingClientRect().right;
      if (!card.hidden) ins.right = innerWidth - card.getBoundingClientRect().left;
    }
    this.stage.rig.setInsets(ins);
  }

  async closeCard(silent = false) {
    $('#card').hidden = true;
    this.app.dataset.card = 'false';
    this.updateInsets();
    if (silent) return;
    if (this.s.visit) { await this.leaveVisit(true); }
    this.s.hotspot = null; this.s.room = null; this.s.artwork = null;
    this.stage.markers.setActive(null);
    this.applyVisibility();
    if (this.s.mode === 'exhibitions') this.renderSheet();
    this.writeHash();
  }

  // -------------------------------------------------------------- picking
  click(e) {
    const ray = this.stage.pointer(e);
    if (this.s.visit) {
      const a = this.stage.artworks.pick(ray, FLOORS);
      if (a) this.openArtwork(a.id);
      return;
    }
    const cut = this.s.explode || this.s.floor !== 'all';
    if (!cut) return;
    const floors = this.s.explode ? FLOORS : [this.s.floor];
    const art = this.stage.artworks.pick(ray, floors);
    const room = this.stage.rooms.pick(ray);
    if (art && (!room || this.s.room === art.room || this.s.plan)) return this.openArtwork(art.id);
    if (room) return this.openRoom(room.id);
    if (art) return this.openArtwork(art.id);
  }

  hover(e) {
    if (this.hoverPending) return;
    this.hoverPending = true;
    requestAnimationFrame(() => {
      this.hoverPending = false;
      const cut = this.s.explode || this.s.floor !== 'all';
      if (!cut || this.s.visit || !this.stage.rooms.visible) { this.app.dataset.picking = 'false'; return; }
      const ray = this.stage.pointer(e);
      const room = this.stage.rooms.pick(ray);
      const art = this.stage.artworks.pick(ray, this.s.explode ? FLOORS : [this.s.floor]);
      const id = room?.id ?? null;
      this.app.dataset.picking = String(Boolean(room || art));
      if (id !== this.stage.rooms.hovered) {
        this.stage.rooms.hovered = id;
        this.applyVisibility();
      }
    });
  }

  // ---------------------------------------------------------------- light
  setHour(hour) {
    this.s.hour = hour;
    $('#hour').value = hour;
    $('#hour-out').textContent = clock(hour);
    this.stage.daylight.set(hour, this.s.day);
    const night = this.stage.daylight.level < 0.25;
    this.app.dataset.night = String(night);
    if (this.s.lightsAuto) this.setLights(night, true);
    if (!this.s.visit) this.stage.scene.background = this.stage.daylight.backgroundColor(new THREE.Color());
  }

  setupLights() {
    const n = this.stage.quality.mobile ? 3 : 6;
    this.roomLights = [];
    for (let i = 0; i < n; i++) {
      const l = new THREE.PointLight(0xffe2c0, 0, 26, 1.6);
      this.stage.scene.add(l);
      this.roomLights.push(l);
    }
    this.spot = new THREE.SpotLight(0xfff0dc, 0, 14, rad(30), 0.55, 1.4);
    this.stage.scene.add(this.spot, this.spot.target);
    $('#hour-out').textContent = clock(this.s.hour);
  }

  setLights(on, auto = false) {
    this.s.lights = on;
    if (!auto) this.s.lightsAuto = false;
    $('#toggle-lights').setAttribute('aria-pressed', String(on));
    this.stage.building.setLamps(on ? 1 : 0);
    this.placeRoomLights(this.s.floor);
    this.stage.dirty = true;
  }

  // A few warm lights over the largest rooms of the floor in view, and a
  // spot on the work being looked at. Fixed count: no shader recompiles.
  placeRoomLights(floor, artwork = null) {
    const lights = this.roomLights;
    if (!lights) return;
    const f = FLOORS.includes(floor) ? floor : 'L00';
    const rooms = this.data.rooms.rooms.filter((r) => r.floor === f && r.kind !== 'link')
      .sort((a, b) => (artwork && b.id === artwork.room) - (artwork && a.id === artwork.room) || area(b) - area(a));
    const on = this.s.lights || this.s.visit;
    const level = this.s.visit ? (this.s.lights ? 0.7 : 0.3) : (this.s.lights ? 1 : 0);
    lights.forEach((l, i) => {
      const r = rooms[i];
      if (!r || !on) { l.intensity = 0; return; }
      const lift = this.stage.building.lift(r.floor);
      l.position.set(r.anchor[0], r.y + 3.4 + lift, r.anchor[1]);
      l.intensity = level * 60;
      l.distance = Math.sqrt(area(r)) * 1.6 + 6;
    });
    if (artwork && this.s.visit) {
      const at = artwork.anchor.clone();
      const n = artwork.normalV ?? new THREE.Vector3(0, 0, 1);
      this.spot.position.copy(at).addScaledVector(n, 2.2).add(new THREE.Vector3(0, 2.0, 0));
      this.spot.target.position.copy(at);
      this.spot.intensity = 12;
      this.spot.angle = rad(artwork.kind === 'wall' ? 24 + Math.min(14, artwork.w * 4) : 30);
    } else this.spot.intensity = 0;
    this.stage.dirty = true;
  }

  // -------------------------------------------------------------- camera
  zoomBy(k) {
    if (this.s.visit) return;
    const p = this.stage.rig.pose();
    this.stage.rig.flyTo({ ...p, zoom: THREE.MathUtils.clamp(p.zoom * k, 0.12, 40) }, 350);
  }

  recentre() {
    if (this.s.visit) return this.openArtwork(this.s.artwork);
    if (this.s.room) return this.frameRoom(this.roomsById.get(this.s.room));
    if (this.s.mode === 'surroundings') return this.fly(HOME.surroundings);
    if (this.s.mat !== 'off') return this.fly(this.fitWidth(MAT_VIEW[this.s.mat]));
    if (this.s.explode) return this.fly(this.s.mode === 'exhibitions' ? HOME.exhibitionsOverview : HOME.explode);
    if (this.s.floor !== 'all') return this.fly(FLOOR_VIEW[this.s.floor]);
    return this.fly(HOME.building);
  }

  updateHint() {
    const h = $('#hint');
    h.textContent = this.s.visit ? t('visitHint') : this.s.mat !== 'off' ? t('matHint') : this.s.plan ? t('planHint') : (this.s.mode === 'exhibitions' && (this.s.explode || this.s.floor !== 'all')) ? t('sectionHint') : t('orbitHint');
  }

  tuneSite() {
    const st = this.stage;
    // the source exports some ground faces with their normals pointing down
    st.site?.traverse((o) => {
      if (!o.isMesh || !/FLOOR_REFERENCE|MOAT_GROUND|TURF|PAVING|GROUND/i.test(o.material.name)) return;
      const n = o.geometry.attributes.normal;
      if (!n) return;
      for (let i = 0; i < n.count; i++) if (n.getY(i) < -0.5) n.setXYZ(i, -n.getX(i), -n.getY(i), -n.getZ(i));
      n.needsUpdate = true;
    });
    st.trees?.traverse((o) => {
      if (o.isMesh && /BARK|TRUNK/.test(o.material.name)) o.material.color.setHex(0x4a3b2c).convertSRGBToLinear();
    });
    st.renderer.shadowMap.needsUpdate = true;
    st.dirty = true;
  }

  frame() {
    this.mx?.update(this.stage.rig.camera);
    // shadows follow the building while it moves
    if (this.stage.building.moving || this.stage.tweens.active) this.stage.renderer.shadowMap.needsUpdate = true;
  }

  // ----------------------------------------------------------- deep links
  // #bina | #cevre | #sergi | #sergi/<ex> | #sergi/<ex>/<room> | #eser/<id> | #bina/<hotspot> | #cevre/<hotspot>
  // #bina/katlar (floors apart) | #bina/malzeme-dikey | #bina/malzeme-kure (materials apart)
  readHash() {
    const h = decodeURIComponent(location.hash.replace(/^#/, ''));
    if (!h) return null;
    const [a, b, c] = h.split('/');
    const mode = { bina: 'building', building: 'building', cevre: 'surroundings', surroundings: 'surroundings', sergi: 'exhibitions', exhibitions: 'exhibitions', eser: 'work', work: 'work' }[a];
    if (!mode) return null;
    return { mode, b, c };
  }

  async go({ mode, b, c }) {
    if (mode === 'work') { await this.setMode('exhibitions', { fly: false }); return this.openArtwork(b); }
    if (mode === 'exhibitions' && b) {
      if (this.s.mode !== 'exhibitions') await this.setMode('exhibitions', { fly: false });
      if (c) return this.openRoom(c);
      return this.openExhibition(b);
    }
    const mat = Object.keys(MAT_SLUG).find((k) => MAT_SLUG[k] === b);
    const floors = mode === 'building' && b === 'katlar';
    await this.setMode(mode, { fly: !mat && !floors });
    if (mat) return this.setMaterials(mat);
    if (floors) return this.setExplode(true);
    if (b) await this.openHotspot(b);
  }

  writeHash() {
    let h = { building: 'bina', surroundings: 'cevre', exhibitions: 'sergi' }[this.s.mode];
    if (this.s.artwork) h = `eser/${this.s.artwork}`;
    else if (this.s.mode === 'exhibitions' && this.s.exhibition) h += `/${this.s.exhibition}${this.s.room ? `/${this.s.room}` : ''}`;
    else if (this.s.hotspot) h += `/${this.s.hotspot}`;
    else if (this.s.mat !== 'off') h += `/${MAT_SLUG[this.s.mat]}`;
    else if (this.s.mode === 'building' && this.s.explode) h += '/katlar';
    if (location.hash.slice(1) === h) return;
    this.ignoreHash = true;
    history.replaceState(null, '', `#${h}`);
    setTimeout(() => { this.ignoreHash = false; }, 0);
  }
}

function area(r) {
  let s = 0;
  const p = r.polygon;
  for (let i = 0; i < p.length; i++) { const [x0, z0] = p[i], [x1, z1] = p[(i + 1) % p.length]; s += x0 * z1 - x1 * z0; }
  return Math.abs(s / 2);
}

const app = new App();
app.boot();
