import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { Pipeline } from './pipeline.js';
import { Daylight } from './daylight.js';
import { Building } from './building.js';
import { Rig, PLAN_AZIMUTH } from './rig.js';
import { Tweens } from './tween.js';
import { Context } from './context.js';
import { Rooms } from './rooms.js';
import { Artworks } from './artworks.js';
import { Markers } from './markers.js';
import { RoomArrows } from './arrows.js';
import { setHatchLight } from './hatch.js';

export function qualityProfile() {
  const coarse = matchMedia('(pointer: coarse)').matches;
  const small = Math.min(screen.width, screen.height) < 820;
  const mobile = coarse && small;
  const q = new URLSearchParams(location.search).get('q');
  const low = q === 'low' || (q !== 'high' && mobile);
  return {
    mobile,
    maxDpr: low ? 1.5 : 2,
    msaa: low ? 2 : 4,
    ao: q !== 'noao' && !low,
    aoSamples: 12,
    shadowMap: low ? 2048 : 4096,
  };
}

// Everything that draws: renderer, lights, model, overlays and the loop.
export class Stage {
  constructor(host, base) {
    this.host = host;
    this.base = base;
    this.quality = qualityProfile();
    const renderer = new THREE.WebGLRenderer({ antialias: false, powerPreference: 'high-performance', alpha: false });
    renderer.setPixelRatio(Math.min(devicePixelRatio, this.quality.maxDpr));
    renderer.toneMapping = THREE.NeutralToneMapping;
    renderer.toneMappingExposure = 1.0;
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.localClippingEnabled = true;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.shadowMap.autoUpdate = false;
    host.append(renderer.domElement);
    this.renderer = renderer;
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0xe7ebe8);
    this.tweens = new Tweens();
    this.rig = new Rig(renderer.domElement, this.tweens);
    this.pipeline = new Pipeline(renderer, this.scene, this.quality);
    this.daylight = new Daylight(renderer, this.scene, this.quality);
    this.building = new Building(this.scene, renderer);
    this.building.onChange = () => { this.dirty = true; };
    this.context = new Context(this.scene);
    this.rooms = new Rooms(this.building);
    this.artworks = new Artworks(this.building, this.rooms, base);
    this.markers = new Markers(host);
    this.arrows = new RoomArrows(this.building);
    this.raycaster = new THREE.Raycaster();
    this.frameHooks = new Set();
    this.dirty = true;
    // the ACT surroundings are photo meshes without lighting of their own:
    // they take the daylight as a colour (dark blue night, warm low sun)
    this.dayTint = { value: new THREE.Color(1, 1, 1) };
    this.daylight.onChange = (d) => {
      setHatchLight(d.level);
      if (this.rig.mode === 'ortho') this.scene.background = d.backgroundColor(new THREE.Color());
      const warm = new THREE.Color(1, 1, 1).lerp(d.sun.color, 0.45 * Math.sin(Math.PI * Math.min(1, d.level)));
      this.dayTint.value.setRGB(0.07, 0.085, 0.14).lerp(new THREE.Color(1, 1, 1), d.level).multiply(warm);
      this.onDaylight?.(d);
      this.dirty = true;
    };
    this.resize();
    addEventListener('resize', () => this.resize());
    this.rig.onResize = () => { this.dirty = true; };
    this.rig.orbit.addEventListener('change', () => { this.dirty = true; });
    this.rig.look.addEventListener('change', () => { this.dirty = true; });
  }

  resize() {
    const w = this.host.clientWidth, h = this.host.clientHeight;
    this.renderer.setSize(w, h);
    this.rig.resize(w, h);
    this.pipeline.setSize(w, h);
    this.dirty = true;
  }

  async load(onProgress) {
    const draco = new DRACOLoader().setDecoderPath(`${this.base}draco/`);
    const loader = new GLTFLoader().setDRACOLoader(draco);
    this.loader = loader;
    const progress = { building: 0, site: 0, trees: 0, data: 0 };
    const weight = { building: 0.55, site: 0.15, trees: 0.2, data: 0.1 };
    const report = () => onProgress?.(Object.entries(progress).reduce((s, [k, v]) => s + v * weight[k], 0));
    const gltf = (name) => loader.loadAsync(`${this.base}model/${name}.glb`, (e) => { if (e.total) { progress[name] = e.loaded / e.total; report(); } })
      .then((g) => { progress[name] = 1; report(); return g; });
    const json = (name) => fetch(`${this.base}data/${name}.json`).then((r) => r.json());
    const [building, sections, rooms, artworks, context, ground] = await Promise.all([
      gltf('building'), json('sections'), json('rooms'), json('artworks'), json('context'), json('ground'),
    ]);
    progress.data = 1; report();
    this.data = { sections, rooms, artworks, context, ground };
    this.building.attach(building.scene);
    this.building.attachSections(sections);
    // site and trees follow the building in; they are not needed for the first frame
    this.siteReady = Promise.all([gltf('site'), gltf('trees'), this.context.init(this.base, context, ground)]).then(([site, trees]) => {
      site.scene.traverse((o) => { if (o.isMesh) { o.receiveShadow = true; o.castShadow = true; o.material.side = THREE.DoubleSide; } });
      trees.scene.traverse((o) => { if (o.isMesh) { o.receiveShadow = true; o.castShadow = true; o.material.side = THREE.DoubleSide; } });
      this.site = site.scene; this.trees = trees.scene;
      if (this.data.context.trees?.length) trees.scene.add(this.context.addCanopies(this.data.context.trees));
      this.scene.add(site.scene, trees.scene);
      this.dirty = true;
    });
    return this.data;
  }

  // Çevre 2: the delivered building with its near and far surroundings
  // (12_Blender_Model/exports/r151_web_v002, prepared by build-model.mjs
  // --cevre2). Loaded on first use; the building gets its own bands so cuts,
  // floors and layers work the same way.
  async loadCevre2(manifest, onProgress, onLate, sourceId = 2) {
    // the far context is the largest file and only seen from a distance:
    // it follows once the rest is on screen
    const files = Object.entries(manifest.files).filter(([k]) => sourceId === 3 || k !== 'far');
    const done = {};
    const total = files.reduce((s, [, f]) => s + (f.bytes || 1), 0);
    const report = () => onProgress?.(files.reduce((s, [k, f]) => s + (done[k] ?? 0) * (f.bytes || 1), 0) / total);
    const fetchOne = (key, f, track) => this.loader.loadAsync(`${this.base}${f.file}`, (e) => {
      if (!track) return;
      done[key] = e.total ? e.loaded / e.total : (f.bytes ? e.loaded / f.bytes : 0); report();
    }).then((g) => { if (track) { done[key] = 1; report(); } return g.scene; });
    const loaded = Object.fromEntries(await Promise.all(files.map(([key, f]) => fetchOne(key, f, true).then((r) => [key, r]))));
    const set = { building: loaded.building };
    const add = (key, root) => {
      root.name = `cevre${sourceId}-${key}`;
      root.traverse((o) => {
        if (!o.isMesh) return;
        o.receiveShadow = true;
        // the far context is too large to cast into the sun's shadow map
        o.castShadow = key !== 'far';
        o.material.side = THREE.DoubleSide;
        if (sourceId === 3 && o.material.map) {
          o.material.map.anisotropy = Math.min(16, this.renderer.capabilities.getMaxAnisotropy());
          o.material.map.needsUpdate = true;
        }
        if (sourceId === 2 && o.material.isMeshBasicMaterial) this.daylit(o.material);
      });
      root.visible = false;
      this.scene.add(root);
      set[key] = root;
    };
    for (const key of ['site', 'trees', 'near', 'far', 'melia', 'schuman', 'vegetation', 'district']) if (loaded[key]) add(key, loaded[key]);
    // the delivered trees come without foliage meshes, like Çevre 1's
    if (set.trees && this.data.context.trees?.length) set.trees.add(this.context.addCanopies(this.data.context.trees));
    if (set.building) this.building.attach(set.building, sourceId);
    this[`cevre${sourceId}`] = set;
    // a fade in progress (building taken apart) covers the new surroundings too
    this.setContextFade(this.contextFadeTarget ?? 1, 300, true);
    this.renderer.shadowMap.needsUpdate = true;
    this.dirty = true;
    if (sourceId === 2 && manifest.files.far) {
      this.cevre2Far = fetchOne('far', manifest.files.far, false).then((root) => {
        add('far', root);
        this.setContextFade(this.contextFadeTarget ?? 1, 300, true);
        onLate?.('far');
        this.dirty = true;
      }).catch((e) => console.warn('Çevre 2 far context', e));
    }
    return set;
  }

  // An unlit (photo) material follows the daylight.
  daylit(material) {
    if (material.userData.daylit) return;
    material.userData.daylit = true;
    material.onBeforeCompile = (shader) => {
      shader.uniforms.uDayTint = this.dayTint;
      shader.fragmentShader = shader.fragmentShader
        .replace('#include <common>', '#include <common>\nuniform vec3 uDayTint;')
        .replace('#include <opaque_fragment>', 'outgoingLight *= uDayTint;\n#include <opaque_fragment>');
    };
    material.customProgramCacheKey = () => 'act-daylit';
    material.needsUpdate = true;
  }

  // Everything around the building, both model sets, loaded or not yet.
  contextRoots() {
    return [this.site, this.trees, this.context.group, this.cevre2?.site, this.cevre2?.trees, this.cevre2?.near, this.cevre2?.far, ...Object.values(this.cevre3 ?? {})].filter(Boolean);
  }

  start() {
    this.renderer.compile(this.scene, this.rig.camera);
    const loop = (now) => {
      requestAnimationFrame(loop);
      this.tweens.update(now);
      this.rig.update();
      this.daylight.update(now);
      for (const fn of this.frameHooks) fn(now);
      const moving = this.tweens.active || this.dirty || this.building.moving;
      if (!moving && !this.alwaysRender) return;
      this.dirty = false;
      const cam = this.rig.camera;
      this.pipeline.setCamera(cam);
      this.markers.update(cam, this.host.clientWidth, this.host.clientHeight);
      this.pipeline.render();
    };
    requestAnimationFrame(loop);
  }

  // Everything that is not the building (site, trees, neighbours, ground
  // drawing) fades together, e.g. to 20 % while the building is taken apart.
  setContextFade(alpha, ms = 700, force = false) {
    // compare with where the fade is heading, not where it is: a reversal
    // that arrives before the fade has moved must still be honoured
    if (!force && Math.abs((this.contextFadeTarget ?? 1) - alpha) < 1e-3) return;
    this.contextFadeTarget = alpha;
    const from = this.contextFade ?? 1;
    const mats = new Set();
    for (const root of this.contextRoots()) {
      root?.traverse((o) => {
        if (!o.material || o === this.context.massing || o === this.context.edges) return;
        for (const m of Array.isArray(o.material) ? o.material : [o.material]) mats.add(m);
      });
    }
    for (const m of mats) {
      m.userData.fadeBase ??= { opacity: m.opacity, transparent: m.transparent, depthWrite: m.depthWrite };
    }
    const setCast = (on) => {
      for (const root of [this.site, this.trees, this.cevre2?.site, this.cevre2?.trees, this.cevre2?.near, this.cevre3?.near]) root?.traverse((o) => { if (o.isMesh) o.castShadow = on; });
      if (this.context.massing) this.context.massing.castShadow = on;
    };
    if (alpha < 1) setCast(false);
    this.tweens.run('context-fade', ms, (t) => {
      const a = from + (alpha - from) * t;
      this.contextFade = a;
      for (const m of mats) {
        const b = m.userData.fadeBase;
        const faded = a < 0.999;
        m.opacity = b.opacity * a;
        if (m.transparent !== (faded || b.transparent)) { m.transparent = faded || b.transparent; m.needsUpdate = true; }
        m.depthWrite = faded ? false : b.depthWrite;
      }
      this.context.massingFade = a;
      this.context.applyMassing?.();
      this.renderer.shadowMap.needsUpdate = true;
      this.dirty = true;
    }).then((done) => { if (done && alpha >= 1) { setCast(true); this.renderer.shadowMap.needsUpdate = true; } });
  }

  pointer(event) {
    const r = this.renderer.domElement.getBoundingClientRect();
    const p = new THREE.Vector2(((event.clientX - r.left) / r.width) * 2 - 1, -((event.clientY - r.top) / r.height) * 2 + 1);
    this.raycaster.setFromCamera(p, this.rig.camera);
    return this.raycaster;
  }
}

export { PLAN_AZIMUTH };
