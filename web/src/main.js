import './style.css';
import * as THREE from 'three';
import { Stage, PLAN_AZIMUTH } from './engine/scene.js';
import { FLOOR_Y, CUTS, FLOORS, EXPLODE } from './engine/building.js';
import { clock } from './engine/daylight.js';
import { BUILDING_HOTSPOTS } from './content/building.js';
import { SURROUNDING_HOTSPOTS } from './content/surroundings.js';
import { EXHIBITIONS, OTHER_ROOMS } from './content/exhibitions.js';
import './content/translations.js';
import { i18n, t, pick } from './i18n.js';
import { MaterialExplode, LAYERS, LAYER_COLOURS } from './engine/explode.js';
import { WireMode } from './engine/wire.js';
import { WalkSurface, Walker } from './engine/walk.js';

const BASE = './demo/';
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const rad = (d) => (d * Math.PI) / 180;
const azimuth = (bearing) => Math.atan2(Math.sin(rad(bearing)), -Math.cos(rad(bearing)));
const polar = (tilt) => rad(90 - tilt);
// storey of a height: the nearest floor top (the −1 pavilion counts as −1)
const storeyOf = (y) => FLOORS.reduce((a, b) => (Math.abs(FLOOR_Y[b] - y) < Math.abs(FLOOR_Y[a] - y) ? b : a));
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const el = (html) => { const d = document.createElement('div'); d.innerHTML = html.trim(); return d.firstElementChild; };

// Bearing: compass direction the camera stands at, seen from the target.
// The official plans put the entrance at the bottom: that is bearing 47°.
const PLAN_BEARING = 47;
// `fit`: the view is zoomed to the extents of that part of the building in
// the free part of the screen (target and zoom are then only a fallback).
const HOME = {
  building: { target: [2, 5, 4], bearing: 204, tilt: 31, zoom: 1.0, fit: 'all' },
  surroundings: { target: [-20, 0, 10], bearing: 222, tilt: 40, zoom: 0.24 },
  explode: { target: [3, 56, -6], bearing: 22, tilt: 18, zoom: 0.48, fit: 'explode' },
  exhibitionsOverview: { target: [3, 40, -6], bearing: 22, tilt: 22, zoom: 0.54, fit: 'explode' },
};
// Malzemelere ayır: framing for the two exploded readings
const MAT_VIEW = {
  vertical: { target: [-1, 124, 2], bearing: 210, tilt: 15, zoom: 0.37, span: 150 },
  radial: { target: [-1, 74, 2], bearing: 210, tilt: 20, zoom: 0.44, span: 440 },
};
const MAT_SLUG = { vertical: 'malzeme-dikey', radial: 'malzeme-kure' };
const FLOOR_VIEW = {
  LM1: { target: [-2, FLOOR_Y.LM1, -6], bearing: 18, tilt: 52, zoom: 1.2, fit: 'LM1' },
  L00: { target: [0, FLOOR_Y.L00, 0], bearing: 18, tilt: 52, zoom: 1.0, fit: 'L00' },
  LP1: { target: [2, FLOOR_Y.LP1, -10], bearing: 18, tilt: 52, zoom: 1.15, fit: 'LP1' },
};

class App {
  constructor() {
    this.app = $('#app');
    this.stage = new Stage($('#viewport'), BASE);
    this.s = { mode: 'building', floor: 'all', explode: false, plan: false, hotspot: null, exhibition: null, room: null, artwork: null, visit: false, walk: false, mat: 'off', wire: false, cevre: 1, hour: 13.5, day: 283, lights: false, lightsAuto: true };
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
    // the building's extents, for zoom to extents
    const g = this.stage.building.sources[1][0].group;
    g.updateMatrixWorld(true);
    this.buildingBox = new THREE.Box3().setFromObject(g);
    this.exhibitionOfRoom = new Map();
    for (const ex of EXHIBITIONS) for (const r of ex.rooms) this.exhibitionOfRoom.set(r.id, ex);
    this.stage.rooms.init(this.data.rooms, (r) => this.exhibitionOfRoom.get(r.id)?.colour ?? 0x8f948f);
    this.stage.arrows.init(this.data.rooms.rooms);
    await this.stage.artworks.init(this.data.artworks, this.roomsById);
    this.orderArtworks();
    this.walkReady = this.initWalk();
    // material layers: patch the visible building band, then the trails
    this.mx = new MaterialExplode(this.stage.scene);
    this.stage.building.addHook(this.mx.hook);
    this.wire = new WireMode(this.stage);
    this.mx.wire = this.wire.uWire;
    this.stage.onDaylight = () => { if (this.wire.amount > 0) this.wire.apply(); };
    for (const b of this.stage.building.sources[1]) this.mx.attach(b.group);
    // while layers are away (or flying back), caps, works, pins and arrows
    // wait: the material offset counts as motion
    this.stage.building.held = () => (this.mx?.amount ?? 0) > 1e-3;
    this.mx.onChange = () => {
      this.stage.dirty = true;
      this.stage.renderer.shadowMap.needsUpdate = true;
      const held = this.stage.building.held();
      if (held !== this.mxHeld) { this.mxHeld = held; this.applyVisibility(); }
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
    addEventListener('resize', () => { this.updateInsets(); this.panelRects(); });
    this.panelRects();
    this.stage.frameHooks.add((now) => this.frame(now));
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
      this.applyVisibility();
      // the site and tree materials are new: re-apply the current fade to them
      this.stage.setContextFade(this.stage.contextFadeTarget ?? 1, 300, true);
      this.app.dataset.siteReady = 'true';
      this.initCevre2();
      // every storey's works, once the rest is in: the walk crosses storeys
      // and a first upload of a work atlas mid-walk would make it hitch
      setTimeout(() => FLOORS.forEach((f) => this.stage.artworks.load(f)), 4000);
    });
  }

  // ------------------------------------------------------- line drawing
  // White edges on black, hidden lines removed, for the exploded views.
  async setWire(on) {
    if (on && !(this.s.explode || this.s.mat !== 'off')) return;
    if (this.s.wire === on) return;
    this.s.wire = on;
    this.syncControls();
    if (on) this.buildWire();
    this.applyVisibility();
    await this.wire.set(on);
  }

  // Lines for whatever is loaded; the edges arrive from a worker, so the
  // drawing fills in over the first moments.
  buildWire() {
    const st = this.stage, w = this.wire;
    for (const bands of Object.values(st.building.sources)) w.buildBuilding(bands);
    for (const root of [st.site, st.trees, st.cevre2?.site, st.cevre2?.trees, st.cevre2?.near, st.cevre2?.far]) w.buildRoot(root);
    const c = st.context;
    if (c.massing && !w.done.has(c.massing)) { w.done.add(c.massing); w.patchFill(c.massing.material); w.addExisting(c.edges, 0.2); }
    if (c.ground) w.buildRoot(c.ground, { lines: false });
    for (const g of Object.values(st.building.floorGroups)) w.buildRoot(g, { cos: Math.cos(Math.PI / 6), material: w.full ??= w.makeFull() });
    for (const cap of Object.values(st.building.caps)) {
      const lines = cap.group.children.find((o) => o.isLineSegments && !o.userData.wire);
      if (lines && !w.done.has(lines)) { w.done.add(lines); w.addExisting(lines, 1); }
    }
    w.tint(st.arrows.material);
    if (this.mx.arcLines) for (const line of [...Object.values(this.mx.arcLines), this.mx.baseLine]) w.tint(line.material);
  }

  // ------------------------------------------------------- walk inside
  // Drop the figure on a floor (or click it) and walk through the building
  // at eye height: demo/data/walk.json says where one can stand.
  async initWalk() {
    try {
      const data = await fetch(`${BASE}data/walk.json`).then((r) => r.json());
      this.surface = new WalkSurface(data);
      // nobody walks through a plinth or a sculpture
      for (const a of this.stage.artworks.items) {
        if (a.kind === 'wall') continue;
        const r = a.kind === 'plinth' || a.kind === 'vitrine' ? Math.min(1.2, a.w * 0.6) / 2 : THREE.MathUtils.clamp(a.h * 0.42, 0.6, 1.1);
        this.surface.block(a.pos[0], a.pos[2], a.floorY, r + 0.25);
      }
      this.walker = new Walker(this.stage, this.surface);
      this.walker.bindPad($$('[data-walk-direction]'));
      // the clearance field takes a few hundred ms: off the first step's back
      setTimeout(() => this.surface.clearance(), 1500);
    } catch (e) {
      console.warn('walk.json', e);
      $('#walk-pegman').hidden = true;
    }
  }

  bindPegman() {
    const button = $('#walk-pegman');
    let ghost = null, start = null;
    const move = (e) => {
      if (!ghost) {
        if (Math.hypot(e.clientX - start.x, e.clientY - start.y) < 6) return;
        ghost = el(`<div class="pegman-ghost">${button.querySelector('svg').outerHTML}</div>`);
        document.body.append(ghost);
        document.body.classList.add('pegman-dragging');
      }
      ghost.style.transform = `translate(${e.clientX}px, ${e.clientY}px)`;
      ghost.dataset.ok = String(Boolean(this.dropPoint(e.clientX, e.clientY)));
    };
    const end = (e) => {
      removeEventListener('pointermove', move);
      removeEventListener('pointerup', end);
      removeEventListener('pointercancel', end);
      document.body.classList.remove('pegman-dragging');
      const dragged = Boolean(ghost);
      ghost?.remove(); ghost = null;
      if (e.type !== 'pointerup') return;
      // a click starts in the Grand Hall (or the largest room of the floor in view)
      if (!dragged) { this.enterWalk(); return; }
      const at = this.dropPoint(e.clientX, e.clientY);
      if (at) this.enterWalk(at);
      else if (e.target === this.stage.renderer.domElement) this.notify(t('walkDropInside'));
    };
    button.addEventListener('pointerdown', (e) => {
      if (e.button !== 0) return;
      e.preventDefault();
      start = { x: e.clientX, y: e.clientY };
      addEventListener('pointermove', move);
      addEventListener('pointerup', end);
      addEventListener('pointercancel', end);
    });
    // keyboard (Enter, Space): no pointer events, only the click
    button.addEventListener('click', (e) => { if (e.detail === 0) this.enterWalk(); });
  }

  // Where the figure would land under the pointer: [x, floor height, z] on
  // a walkable floor in view (below the cut), or null.
  dropPoint(clientX, clientY) {
    if (!this.surface || this.s.walk || this.s.visit || this.s.explode || this.s.mat !== 'off' || this.s.mode === 'surroundings') return null;
    const b = this.stage.building;
    if (b.moving || b.state === 'explode') return null;
    const r = this.stage.renderer.domElement.getBoundingClientRect();
    if (clientX < r.left || clientX > r.right || clientY < r.top || clientY > r.bottom) return null;
    const { ray } = this.stage.pointer({ clientX, clientY });
    const cut = b.state === 'all' ? null : b.state;
    const top = cut ? CUTS[cut] : 30, bottom = cut ? FLOOR_Y[cut] - 0.8 : -7;
    if (ray.direction.y > -0.05) return null;
    // march down the ray; land where it first passes a standing height
    const p = ray.origin.clone().addScaledVector(ray.direction, (top - ray.origin.y) / ray.direction.y);
    const step = ray.direction.clone().multiplyScalar(0.08);
    let prevY = p.y;
    while (p.y > bottom) {
      p.add(step);
      const h = this.surface.below(p.x, p.z, Math.min(top, prevY));
      if (h !== null && h >= p.y && h >= bottom) return [p.x, h, p.z];
      prevY = p.y;
    }
    if (!cut) return null;
    // over a cut wall: the floor beside it
    const hit = ray.origin.clone().addScaledVector(ray.direction, (FLOOR_Y[cut] - ray.origin.y) / ray.direction.y);
    return this.surface.nearest(hit.x, hit.z, FLOOR_Y[cut], 1.2);
  }

  // The way to face on arrival: the way the view was looking, turned toward
  // the most open direction (not into the nearest wall).
  openYaw([x, h, z]) {
    const dir = this.stage.rig.camera.getWorldDirection(new THREE.Vector3());
    const preferred = Math.atan2(-dir.x, -dir.z);
    const depth = (yaw) => {
      for (let d = 0.25; d <= 14; d += 0.25) if (this.surface.sample(x - Math.sin(yaw) * d, z - Math.cos(yaw) * d, h, 0.45) === null) return d - 0.25;
      return 14;
    };
    let best = preferred, score = -Infinity;
    for (let i = 0; i < 48; i++) {
      const a = (i / 48) * Math.PI * 2, yaw = preferred + a;
      const v = depth(yaw) * 0.5 + depth(yaw - 0.3) * 0.25 + depth(yaw + 0.3) * 0.25 + 2.5 * Math.cos(a);
      if (v > score) { score = v; best = yaw; }
    }
    return best;
  }

  async enterWalk(at = null) {
    await this.walkReady;
    if (!this.walker || this.s.walk) return;
    if (!at) {
      const floor = FLOORS.includes(this.s.floor) && !this.s.explode && this.s.mat === 'off' ? this.s.floor : 'L00';
      const room = floor === 'L00' ? this.roomsById.get('grand-hall')
        : this.data.rooms.rooms.filter((r) => r.floor === floor && r.kind !== 'link').sort((a, b) => area(b) - area(a))[0];
      at = room && this.surface.nearest(room.anchor[0], room.anchor[1], room.y, 4);
      if (!at) return;
    }
    const yaw = this.openYaw(at);
    if (!(await this.leaveMaterials())) return;
    if (this.s.visit) await this.leaveVisit(false);
    if (this.s.wire) this.setWire(false);
    this.s.walk = true;
    this.s.explode = false; this.s.floor = 'all';
    this.s.plan = false; this.stage.rig.setPlan(false);
    this.s.hotspot = null; this.s.room = null; this.s.artwork = null;
    this.closeCard(true);
    FLOORS.forEach((f) => this.stage.artworks.load(f));
    await this.fade(async () => {
      $('#walk-ui').hidden = false;
      this.stage.building.walking = true;
      this.syncControls();
      this.applyVisibility();
      this.renderMarkers();
      this.updateInsets();
      this.updateHint();
      this.stage.building.setState('all', this.stage.tweens, 0);
      const rig = this.stage.rig;
      rig.mode = 'persp';
      rig.orbit.enabled = false;
      rig.look.enabled = false;
      rig.fovFor = (w, h) => this.walker.fov(w, h);
      rig.resize(rig.width, rig.height);
      this.walkFloor = null; this.walkWhere = null;
      this.walker.arrive(at, yaw, this.stage.tweens).then((done) => { if (done && this.s.walk) this.walkMoved(true); });
      this.walkMoved(true);
    });
  }

  async leaveWalk(refly = true) {
    if (!this.s.walk) return;
    const w = this.walker;
    const p = w.camera.position.clone(), floor = storeyOf(w.foot), yaw = w.yaw;
    w.stop();
    this.stage.tweens.run('camera', 0, () => {});
    await this.fade(async () => {
      this.s.walk = false;
      this.stage.building.walking = false;
      $('#walk-ui').hidden = true;
      const rig = this.stage.rig;
      rig.fovFor = null;
      rig.useOrtho();
      rig.resize(rig.width, rig.height);
      if (refly) { this.s.floor = floor; this.s.explode = false; }
      this.syncControls();
      this.applyVisibility();
      this.renderMarkers();
      this.updateInsets();
      this.updateHint();
      this.placeRoomLights(this.s.floor);
      if (!refly) return;
      // back out over the spot, on the storey that was walked
      this.stage.artworks.load(floor);
      const target = new THREE.Vector3(p.x, FLOOR_Y[floor], p.z);
      rig.setPose({ target, azimuth: yaw, polar: polar(40), zoom: 6 });
      this.focusShadows(target, 1.6);
      this.stage.building.setState(floor, this.stage.tweens, 900);
      rig.flyTo({ target, azimuth: yaw, polar: polar(52), zoom: 1.6 }, 1100);
    });
    this.writeHash();
  }

  // Fade the view out, change it, fade it back in.
  fade(change) {
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) return change();
    this.app.dataset.fade = 'out';
    return new Promise((resolve) => setTimeout(async () => {
      try { await change(); } finally {
        this.stage.dirty = true;
        requestAnimationFrame(() => { this.app.dataset.fade = 'in'; resolve(); });
      }
    }, 240));
  }

  // While walking: which room, which storey, lights and shadows nearby.
  walkMoved(force = false) {
    const w = this.walker, p = w.camera.position, foot = w.foot;
    const floor = storeyOf(foot);
    if (force || floor !== this.walkFloor) { this.walkFloor = floor; this.placeRoomLights(floor); }
    // one shadow map over the whole building, drawn once: refitting it while
    // walking redraws every shadow and the walk would hitch
    if (force) {
      const g = this.surface.grid;
      this.focusShadows(new THREE.Vector3(g.x + (g.width * g.step) / 2, 0, g.z + (g.height * g.step) / 2), 1);
    }
    let room = null;
    for (const r of this.data.rooms.rooms) {
      if (Math.abs(r.y - foot) > 1.8 || !inside(r.polygon, p.x, p.z)) continue;
      if (!room || Math.abs(r.y - foot) < Math.abs(room.y - foot)) room = r;
    }
    const key = `${room?.id}|${floor}|${i18n.lang}`;
    if (!force && key === this.walkWhere) return;
    this.walkWhere = key;
    $('#walk-where').innerHTML = room
      ? `<span lang="fr">${esc(room.label)}</span><small>${esc(t('floorName' + room.floor))}</small>`
      : `<span>${esc(t('floorName' + floor))}</span>`;
  }

  // ------------------------------------------------ Çevre 1 / Çevre 2
  // Çevre 1 is the model built from current.glb.gz (R149) with the model
  // site, trees and OSM massing; Çevre 2 the delivered R151 web set
  // (building, near and far context). demo/data/cevre2.json lists its files.
  async initCevre2() {
    this.cevre2 = await fetch(`${BASE}data/cevre2.json`).then((r) => (r.ok ? r.json() : null)).catch(() => null);
    this.app.dataset.cevre2 = this.cevre2 ? 'available' : 'missing';
    if (new URLSearchParams(location.search).get('cevre') === '2') await this.setCevre(2);
  }

  async setCevre(n) {
    if (n === this.s.cevre && !(n === 2 && !this.stage.cevre2)) return;
    if (n === 2 && !this.stage.cevre2) {
      if (!this.cevre2) return this.notify(t('cevre2Missing'));
      const button = $('[data-cevre="2"]');
      if (!this.cevre2Loading) {
        this.app.dataset.cevre2 = 'loading';
        button.setAttribute('aria-busy', 'true');
        this.cevre2Loading = this.stage.loadCevre2(this.cevre2, (p) => button.style.setProperty('--p', `${Math.round(p * 100)}%`), () => { this.applyVisibility(); if (this.s.wire) this.buildWire(); })
          .then(async () => {
            const bands = this.stage.building.sources[2];
            if (bands && this.mx) for (const b of bands) this.mx.attach(b.group);
            // interior lights already on reach the new building too
            this.stage.building.setLamps(this.stage.building.lampLevel);
            this.tuneSite(this.stage.cevre2.site, this.stage.cevre2.trees);
            if (this.s.wire) this.buildWire();
            const pieces = await fetch(`${BASE}${this.cevre2.pieces}`).then((r) => (r.ok ? r.json() : null)).catch(() => null);
            if (pieces && this.mx) this.mx.build(pieces, 2);
            this.app.dataset.cevre2 = 'ready';
          })
          .catch((e) => { console.error('Çevre 2', e); this.app.dataset.cevre2 = 'error'; this.cevre2Loading = null; throw e; })
          .finally(() => { button.removeAttribute('aria-busy'); button.style.removeProperty('--p'); });
      }
      try { await this.cevre2Loading; } catch { return this.notify(t('cevre2Error')); }
    }
    this.s.cevre = n;
    // a set without its own building keeps Çevre 1's
    this.stage.building.useSource(this.stage.building.sources[n] ? n : 1);
    this.mx?.use(this.mx.sets?.[n] ? n : 1);
    this.syncControls();
    this.applyVisibility();
    this.renderMarkers();
    const url = new URL(location.href);
    if (n === 2) url.searchParams.set('cevre', '2'); else url.searchParams.delete('cevre');
    history.replaceState(null, '', url);
  }

  notify(text) {
    const n = $('#notice');
    n.textContent = text;
    n.hidden = false;
    clearTimeout(this.noticeTimer);
    this.noticeTimer = setTimeout(() => { n.hidden = true; }, 5200);
  }

  // ------------------------------------------------------------ helpers
  poseOf(v) {
    return { target: new THREE.Vector3(...v.target), azimuth: azimuth(v.bearing), polar: polar(v.tilt), zoom: v.zoom };
  }

  fly(v, ms) {
    let pose = this.poseOf(v);
    if (this.s.plan) { pose.polar = 1e-4; pose.azimuth = azimuth(PLAN_BEARING); }
    const box = v.fit && this.extents(v.fit);
    if (box) pose = this.stage.rig.fit(box, pose.azimuth, pose.polar, this.framePad());
    this.focusShadows(pose.target, pose.zoom);
    return this.stage.rig.flyTo(pose, ms);
  }

  // Screen edges the bars cover (the panels are insets of the rig).
  framePad() {
    return innerWidth <= 760 ? { top: 104, bottom: 8, side: 12 } : { top: 92, bottom: 88, side: 28 };
  }

  // World box of a part of the building as it stands in that view: 'all',
  // 'explode' (storeys lifted, the roof left out over the exhibitions) or a
  // storey (its rooms, from its floor to its cut).
  extents(kind) {
    const b = this.buildingBox;
    if (!b) return null;
    if (kind === 'all') return b.clone();
    if (kind === 'explode') {
      const top = this.s.mode === 'exhibitions' ? EXPLODE[2].hi + EXPLODE[2].dy : b.max.y + EXPLODE[3].dy;
      return new THREE.Box3(b.min.clone(), new THREE.Vector3(b.max.x, top, b.max.z));
    }
    const box = new THREE.Box3();
    for (const r of this.data.rooms.rooms) if (r.floor === kind) for (const [x, z] of r.polygon) box.expandByPoint(new THREE.Vector3(x, FLOOR_Y[kind], z));
    if (box.isEmpty()) return null;
    box.expandByVector(new THREE.Vector3(3, 0, 3));
    box.max.y = CUTS[kind];
    return box;
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
    $$('#layer-panel [data-mat]').forEach((b) => b.addEventListener('click', () => this.setMaterials(b.dataset.mat)));
    $$('[data-cevre]').forEach((b) => b.addEventListener('click', () => this.setCevre(Number(b.dataset.cevre))));
    $('#toggle-wire').addEventListener('click', () => this.setWire(!this.s.wire));
    this.bindPegman();
    $('#toggle-light-panel').addEventListener('click', () => {
      const open = this.app.dataset.light !== 'open';
      this.app.dataset.light = open ? 'open' : 'closed';
      $('#toggle-light-panel').setAttribute('aria-expanded', String(open));
    });
    $('#walk-exit').addEventListener('click', () => this.leaveWalk());
    $('#zoom-in').addEventListener('click', () => this.zoomBy(1.35));
    $('#zoom-out').addEventListener('click', () => this.zoomBy(1 / 1.35));
    $('#recentre').addEventListener('click', () => this.recentre());
    $('#card-close').addEventListener('click', () => this.closeCard());
    $('#hour').addEventListener('input', (e) => this.setHour(+e.target.value));
    $('#day').addEventListener('change', (e) => { this.s.day = +e.target.value; this.stage.daylight.set(this.s.hour, this.s.day); });
    $('#toggle-lights').addEventListener('click', () => { this.s.lightsAuto = false; this.setLights(!this.s.lights); });
    $$('.lang-flag').forEach((b) => b.addEventListener('click', () => {
      i18n.set(b.dataset.lang);
      // a ?lang= in the address follows the choice (it would win on reload)
      const url = new URL(location.href);
      if (url.searchParams.has('lang')) { url.searchParams.set('lang', i18n.lang); history.replaceState(null, '', url); }
      this.applyLanguage();
      // on the welcome screen nothing else is drawn yet
      if (this.app.dataset.ready === 'true') this.rerender();
    }));
    $('#open-about').addEventListener('click', () => { $('#about').hidden = !$('#about').hidden; });
    $$('[data-close="about"]').forEach((b) => b.addEventListener('click', () => { $('#about').hidden = true; }));
    $('#lightbox-close').addEventListener('click', () => { $('#lightbox').hidden = true; });
    $('#lightbox').addEventListener('click', (e) => { if (e.target.id === 'lightbox') $('#lightbox').hidden = true; });
    $$('[data-start]').forEach((b) => b.addEventListener('click', () => { this.app.dataset.booting = 'false'; this.setMode(b.dataset.start); }));
    $('#retry').addEventListener('click', () => location.reload());
    addEventListener('keydown', (e) => {
      if (e.target.closest?.('input,select,textarea') && !(this.s.walk && e.key === 'Escape')) return;
      if (e.key === 'Escape') this.back();
      // while walking the arrows walk
      if (this.s.walk) return;
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
    document.title = t('docTitle');
  }

  sourcesHtml() {
    return `<h3 class="kicker">${esc(t('sources'))}</h3><ul>
      <li>mudam.com — ${esc(t('srcMudam'))} (Kaihō, Christine Sun Kim: FOR EVER, Video Killed the Radio Star)</li>
      <li>WikiArquitectura, ArchEyes (MUDAM, I. M. Pei / Pei Cobb Freed &amp; Partners)</li>
      <li>Great Gardens of the World — Michel Desvigne, Dräi Eechelen Park</li>
      <li>${esc(t('srcOsm'))} (ODbL)</li></ul>`;
  }

  rerender() {
    this.renderMarkers();
    this.renderLayerList();
    if (this.s.mode === 'exhibitions') this.renderSheet();
    if (this.s.walk) this.walkMoved(true);
    if (this.s.artwork) this.renderArtworkCard();
    else if (this.s.room) this.renderRoomCard();
    else if (this.s.hotspot) this.renderHotspotCard();
    this.updateHint();
  }

  // --------------------------------------------------------------- modes
  async setMode(mode, { fly = true } = {}) {
    const prev = this.s.mode;
    if (this.s.walk) await this.leaveWalk(false);
    if (!(await this.leaveMaterials())) return;
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
    if (this.s.walk) await this.leaveWalk(false);
    // the layers return while the storeys move: one motion, no wait
    if (this.s.mat !== 'off' && !this.s.visit) this.setMaterials('off', { fly: false });
    if (this.s.visit) await this.leaveVisit(false);
    if (this.s.hotspot) { this.s.hotspot = null; this.closeCard(true); }
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
    if (this.s.walk) await this.leaveWalk(false);
    // the layers return while the storeys move: one motion, no wait
    if (this.s.mat !== 'off' && !this.s.visit) this.setMaterials('off', { fly: false });
    if (this.s.visit) await this.leaveVisit(false);
    // a hotspot's card belongs to its own view
    if (this.s.hotspot) { this.s.hotspot = null; this.closeCard(true); }
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
    if (this.s.walk) await this.leaveWalk(false);
    // the layers return while the storeys move: one motion, no wait
    if (this.s.mat !== 'off' && !this.s.visit) this.setMaterials('off', { fly: false });
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
    if (this.s.walk && mode !== 'off') await this.leaveWalk(false);
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
    if (mode !== 'off') { this.s.explode = false; this.s.floor = 'all'; this.s.plan = false; this.s.room = null; this.s.artwork = null; this.stage.rig.setPlan(false); }
    else this.mx.resetLayers();
    this.syncControls();
    this.applyVisibility();
    this.renderMarkers();
    this.renderLayerList();
    const flight = fly ? this.fly(mode === 'off' ? HOME.building : this.fitWidth(MAT_VIEW[mode]), 1800) : null;
    // storeys apart or cut close up while the layers come apart: one motion
    const settle = mode !== 'off' && this.stage.building.state !== 'all' ? this.stage.building.setState('all', this.stage.tweens, 1300) : null;
    await Promise.all([this.mx.set(mode, this.stage.tweens, prev !== 'off' && mode !== 'off' ? 1500 : 1800), flight, settle]);
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

  // Bring the parts back before another view. Resolves false when a newer
  // click turned the materials on again meanwhile: the caller then stops.
  async leaveMaterials() {
    if (this.s.mat === 'off') return true;
    await this.setMaterials('off', { fly: false });
    return this.s.mat === 'off';
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
    $$('#layer-panel [data-mat]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.mat === this.s.mat)));
    this.app.dataset.materials = this.s.mat === 'off' ? 'off' : 'on';
    $('#toggle-explode').setAttribute('aria-pressed', String(this.s.explode));
    $('#toggle-wire').setAttribute('aria-pressed', String(this.s.wire));
    this.app.dataset.exploded = this.s.explode || this.s.mat !== 'off' ? 'on' : 'off';
    this.app.dataset.wire = this.s.wire ? 'on' : 'off';
    $$('[data-cevre]').forEach((b) => b.setAttribute('aria-pressed', String(Number(b.dataset.cevre) === this.s.cevre)));
    $('#toggle-plan').setAttribute('aria-pressed', String(this.s.plan));
    this.app.dataset.visit = String(this.s.visit);
    this.app.dataset.walk = String(this.s.walk);
    if (innerWidth <= 760) this.updateInsets();
  }

  // What is drawn in each state: context, trees, room tints, plan dots.
  applyVisibility() {
    const st = this.stage;
    const cut = this.s.explode || this.s.floor !== 'all';
    // while the building is taken apart (floors or materials) the whole
    // surroundings model stays in place at 20 % opacity
    const exploded = this.s.explode || this.s.mat !== 'off';
    // the line drawing belongs to the exploded views
    if (!exploded && this.s.wire) { this.s.wire = false; this.wire.set(false); this.syncControls(); }
    // line drawing: the surroundings are solid black, their lines at 20 %
    st.setContextFade(exploded ? (this.s.wire ? 1 : 0.2) : 1);
    const c2 = this.s.cevre === 2 && Boolean(st.cevre2);
    const treesOn = exploded || (!cut && !this.s.visit);
    // Çevre 1: model site, trees, OSM massing and ground drawing
    if (st.site) st.site.visible = !c2;
    if (st.trees) st.trees.visible = !c2 && treesOn;
    st.context.group.visible = !c2;
    // Çevre 2: the delivered near and far surroundings
    if (st.cevre2) {
      const { site, trees, near, far } = st.cevre2;
      if (site) site.visible = c2;
      if (trees) trees.visible = c2 && treesOn;
      if (near) near.visible = c2;
      if (far) far.visible = c2 && !this.s.visit;
    }
    // neighbours stay out of the way of close building views
    st.context.setMassing(this.s.mode === 'surroundings' || exploded ? 1 : cut || this.s.hotspot ? 0.0 : 0.85);
    if (st.context.ground) st.context.ground.visible = true;
    const showRooms = !this.s.visit && (this.s.mode === 'exhibitions' || this.s.plan) && cut && !this.stage.building.held?.();
    const ex = EXHIBITIONS.find((e) => e.id === this.s.exhibition);
    st.rooms.selected = this.s.room;
    st.rooms.refresh({ show: showRooms, exhibitionRooms: ex ? new Set(ex.rooms.map((r) => r.id)) : (this.s.mode === 'exhibitions' ? new Set(this.exhibitionOfRoom.keys()) : null) });
    st.artworks.setPlanMarkers(this.s.plan && !this.s.visit);
    this.showArrows();
    st.building.visitFloor = this.s.visit ? this.roomsById.get(this.s.room)?.floor : null;
    st.building.roofVisible = this.s.mode !== 'exhibitions';
    st.building.apply();
    st.scene.background = this.s.visit ? null : st.daylight.backgroundColor(new THREE.Color());
    if (this.s.visit) { st.scene.background = new THREE.Color(0xdfe3e1); }
    // rooms under glass are bright at midday: expose for the walls, not the sky
    st.renderer.toneMappingExposure = this.s.visit ? 0.8 : this.s.walk ? 0.9 : 1.0;
    if (this.wire?.amount > 0) this.wire.apply();
    st.dirty = true;
  }

  showArrows() {
    this.stage.arrows.setVisible(this.s.explode && !this.s.visit && !this.s.walk && this.s.mode !== 'surroundings' && !this.stage.building.held?.());
  }

  // ------------------------------------------------------------- markers
  renderMarkers() {
    // new pins need a frame even when nothing else moves
    this.stage.dirty = true;
    const m = this.stage.markers;
    m.clear();
    if (this.s.visit || this.s.walk) return;
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
    if (this.s.explode && (this.s.mode === 'building' || this.s.mode === 'exhibitions')) {
      // storeys apart: an upright arrow from the middle of every room, its
      // name from the plans written on top (in the exhibitions, in the colour
      // of the exhibition shown there)
      const ex = EXHIBITIONS.find((e) => e.id === this.s.exhibition);
      for (const r of this.data.rooms.rooms) {
        const exOf = this.exhibitionOfRoom.get(r.id);
        const item = m.add({
          id: `room:${r.id}`, kind: 'roomtag', position: this.stage.arrows.tip(r), label: r.label, lang: 'fr',
          lift: () => this.stage.building.lift(r.floor),
          visible: () => this.s.explode && this.s.mat === 'off' && this.stage.building.state === 'explode' && !this.stage.building.moving && !this.stage.building.held(),
          onClick: () => this.openRoom(r.id),
        });
        if (this.s.mode === 'exhibitions') {
          item.el.style.setProperty('--room', exOf?.css ?? '#8f948f');
          item.el.classList.add('coloured');
          if (ex ? exOf !== ex : !exOf) item.el.classList.add('dim');
        }
      }
      m.setActive(this.s.room ? `room:${this.s.room}` : null);
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
    return this.s.floor === r.floor && !this.stage.building.moving && !this.stage.building.held();
  }

  hotspotVisible(h) {
    // pins wait until the parts are back in place
    if (this.s.mat !== 'off' || (this.mx?.amount ?? 0) > 1e-3 || this.stage.building.moving) return false;
    const st = this.stage.building.state;
    if (st === 'explode') return false;
    if (st === 'all') return (h.view.state ?? 'all') === 'all' || h.at[1] < 16;
    return h.at[1] < CUTS[st] + 0.5 && h.at[1] > FLOOR_Y[st] - 0.5;
  }

  // ------------------------------------------------------------ hotspots
  hotspots() { return this.s.mode === 'surroundings' ? SURROUNDING_HOTSPOTS : BUILDING_HOTSPOTS; }

  async openHotspot(id) {
    if (this.s.walk) await this.leaveWalk(false);
    if (!(await this.leaveMaterials())) return;
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
    // On a phone the sheet is a strip above the dock: the heading and texts
    // give way and the cards (or the rooms) scroll sideways (.sheet-row).
    if (!ex) {
      sheet.innerHTML = `
        <div class="sheet-head"><h2>${esc(t('exhibitionsHeading'))}</h2>
        <p class="lead">${esc(t('exhibitionsLead'))}</p></div>
        <div class="sheet-row">${EXHIBITIONS.map((e) => `
          <button class="ex-card" data-ex="${e.id}" style="--c:${e.css}">
            <span class="ex-title">${esc(e.title)}</span>
            <span class="ex-sub">${esc(pick(e.subtitle))}</span>
            <span class="ex-meta">${esc(pick(e.place))} · ${esc(pick(e.dates))}</span>
          </button>`).join('')}</div>
        <p class="small-note">${esc(t('placeholderNote'))}</p>`;
      $$('[data-ex]', sheet).forEach((b) => b.addEventListener('click', () => this.openExhibition(b.dataset.ex)));
      return;
    }
    const works = this.byExhibition.get(ex.id) ?? [];
    sheet.innerHTML = `
      <div class="sheet-head">
        <button class="back" data-back="list" aria-label="${esc(t('backToList'))}">← <span>${esc(t('backToList'))}</span></button>
        <p class="kicker" style="color:${ex.css}">${esc(pick(ex.place))}</p>
        <h2 style="--c:${ex.css}">${esc(ex.title)}</h2>
        <p class="lead dates" style="margin-bottom:4px"><strong>${esc(pick(ex.subtitle))}</strong><br/>${esc(pick(ex.dates))}</p>
      </div>
      <div class="sheet-intro">
        ${pick(ex.intro).map((p) => `<p class="lead">${esc(p)}</p>`).join('')}
        <p class="small-note">${esc(pick(ex.credits))}</p>
        ${ex.next ? `<p class="small-note">${esc(pick(ex.next))}</p>` : ''}
      </div>
      <div class="sheet-row">
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
            <span class="meta">${r.closed ? '—' : `${n} ${esc(t(n === 1 ? 'workOne' : 'works'))}`}</span></button>`;
        }).join('')}
      </div>
      </div>
      <p class="small-note">${esc(t('readingNote'))}</p>`;
    $('[data-back]', sheet).addEventListener('click', () => this.listExhibitions());
    $$('[data-room]', sheet).forEach((b) => b.addEventListener('click', () => this.openRoom(b.dataset.room)));
    $('[data-walk="works"]', sheet).addEventListener('click', () => { const first = works[0]; if (first) this.openArtwork(first.id); });
    $('[data-walk="rooms"]', sheet).addEventListener('click', () => this.openRoom(ex.rooms[0].id));
  }

  async listExhibitions() {
    if (this.s.walk) await this.leaveWalk(false);
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
    if (this.s.walk) await this.leaveWalk(false);
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
    if (this.s.walk) await this.leaveWalk(false);
    if (!(await this.leaveMaterials())) return;
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
    if (this.s.walk) await this.leaveWalk(false);
    if (!(await this.leaveMaterials())) return;
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
    if (this.s.walk) return this.leaveWalk();
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

  // Screen rectangles that labels on the scene keep clear of.
  panelRects() {
    const r = $('.light-panel').getBoundingClientRect();
    this.stage.markers.avoid = r.width ? [{ left: r.left - 6, right: r.right, top: r.top - 6, bottom: r.bottom }] : [];
  }

  // Panels cover part of the canvas; the camera frames what remains.
  updateInsets() {
    const mobile = innerWidth <= 760;
    const sheet = $('#sheet'), card = $('#card');
    const ins = { left: 0, right: 0, bottom: 0 };
    if (this.s.walk) { /* walking: the whole screen is the view */ } else if (mobile) {
      // on a phone the model sits above the bottom stack: the dock and the
      // strip over it (exhibitions, a card or the material layers)
      const tops = [sheet, card, $('#layer-panel'), $('.dock')]
        .filter((n) => !n.hidden && getComputedStyle(n).display !== 'none')
        .map((n) => n.getBoundingClientRect().top);
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
    if (this.s.walk) return;
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
    const near = this.s.visit || this.s.walk;
    const on = this.s.lights || near;
    const level = near ? (this.s.lights ? 0.7 : 0.3) : (this.s.lights ? 1 : 0);
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
    if (this.s.visit || this.s.walk) return;
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
    const touch = matchMedia('(pointer: coarse)').matches;
    h.textContent = this.s.walk ? t(touch ? 'walkHintTouch' : 'walkHint') : this.s.visit ? t('visitHint') : this.s.mat !== 'off' ? t('matHint') : this.s.plan ? t('planHint') : (this.s.mode === 'exhibitions' && (this.s.explode || this.s.floor !== 'all')) ? t('sectionHint') : t('orbitHint');
  }

  tuneSite(site = this.stage.site, trees = this.stage.trees) {
    const st = this.stage;
    // the source exports some ground faces with their normals pointing down
    site?.traverse((o) => {
      if (!o.isMesh || !/FLOOR_REFERENCE|MOAT_GROUND|TURF|PAVING|GROUND/i.test(o.material.name)) return;
      const n = o.geometry.attributes.normal;
      if (!n) return;
      for (let i = 0; i < n.count; i++) if (n.getY(i) < -0.5) n.setXYZ(i, -n.getX(i), -n.getY(i), -n.getZ(i));
      n.needsUpdate = true;
    });
    trees?.traverse((o) => {
      if (o.isMesh && /BARK|TRUNK/.test(o.material.name)) o.material.color.setHex(0x4a3b2c).convertSRGBToLinear();
    });
    st.renderer.shadowMap.needsUpdate = true;
    st.dirty = true;
  }

  frame(now) {
    if (this.walker?.update(now)) this.walkMoved();
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

function inside(polygon, x, z) {
  let c = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const [xi, zi] = polygon[i], [xj, zj] = polygon[j];
    if ((zi > z) !== (zj > z) && x < ((xj - xi) * (z - zi)) / (zj - zi) + xi) c = !c;
  }
  return c;
}

function area(r) {
  let s = 0;
  const p = r.polygon;
  for (let i = 0; i < p.length; i++) { const [x0, z0] = p[i], [x1, z1] = p[(i + 1) % p.length]; s += x0 * z1 - x1 * z0; }
  return Math.abs(s / 2);
}

const app = new App();
app.boot();
