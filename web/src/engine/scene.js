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
    this.raycaster = new THREE.Raycaster();
    this.frameHooks = new Set();
    this.dirty = true;
    this.daylight.onChange = (d) => {
      setHatchLight(d.level);
      if (this.rig.mode === 'ortho') this.scene.background = d.backgroundColor(new THREE.Color());
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
      draco.dispose();
    });
    return this.data;
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

  pointer(event) {
    const r = this.renderer.domElement.getBoundingClientRect();
    const p = new THREE.Vector2(((event.clientX - r.left) / r.width) * 2 - 1, -((event.clientY - r.top) / r.height) * 2 + 1);
    this.raycaster.setFromCamera(p, this.rig.camera);
    return this.raycaster;
  }
}

export { PLAN_AZIMUTH };
