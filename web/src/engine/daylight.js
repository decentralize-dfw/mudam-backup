import * as THREE from 'three';
import { Sky } from 'three/addons/objects/Sky.js';

// Mudam, Kirchberg, Luxembourg City.
export const SITE = { latitude: 49.6177, longitude: 6.1408 };

// Central European time with the EU summer-time rule (last Sunday of March to
// last Sunday of October). `day` is the day of year.
export function utcOffset(day, year = 2026) {
  const lastSunday = (month) => {
    const d = new Date(Date.UTC(year, month + 1, 0));
    return d.getUTCDate() - d.getUTCDay();
  };
  const doy = (month, date) => Math.round((Date.UTC(year, month, date) - Date.UTC(year, 0, 0)) / 864e5);
  const start = doy(2, lastSunday(2)), end = doy(9, lastSunday(9));
  return day >= start && day < end ? 2 : 1;
}

// NOAA fractional-year solar position (after angora/viewer/src/daylight.js).
// Model frame: +x east, -z north, +y up. Returns a unit vector toward the sun.
export function solarDirection(hour, day) {
  const rad = Math.PI / 180;
  const tz = utcOffset(day);
  const g = 2 * Math.PI / 365 * (day - 1 + (hour - tz - 12) / 24);
  const eq = 229.18 * (0.000075 + 0.001868 * Math.cos(g) - 0.032077 * Math.sin(g) - 0.014615 * Math.cos(2 * g) - 0.040849 * Math.sin(2 * g));
  const dec = 0.006918 - 0.399912 * Math.cos(g) + 0.070257 * Math.sin(g) - 0.006758 * Math.cos(2 * g) + 0.000907 * Math.sin(2 * g) - 0.002697 * Math.cos(3 * g) + 0.00148 * Math.sin(3 * g);
  const ha = (hour * 60 + eq + 4 * SITE.longitude - 60 * tz) / 4 * rad - Math.PI;
  const lat = SITE.latitude * rad;
  const east = -Math.cos(dec) * Math.sin(ha);
  const north = Math.cos(lat) * Math.sin(dec) - Math.sin(lat) * Math.cos(dec) * Math.cos(ha);
  const up = Math.sin(lat) * Math.sin(dec) + Math.cos(lat) * Math.cos(dec) * Math.cos(ha);
  return new THREE.Vector3(east, up, -north).normalize();
}

export function clock(hour) {
  const m = Math.round(hour * 60);
  return `${String(Math.floor(m / 60) % 24).padStart(2, '0')}:${String(m % 60).padStart(2, '0')}`;
}

const smooth = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };

// Sun, sky and the image-based light derived from that sky. The sky is a
// physical (Preetham) model, so dusk, overcast-free noon and the winter sun
// all come from the same sun vector; the environment map is re-baked from it
// whenever the hour changes.
export class Daylight {
  constructor(renderer, scene, quality) {
    this.renderer = renderer;
    this.scene = scene;
    this.quality = quality;
    this.hour = 13.5;
    this.day = 283; // 10 October
    this.level = 1;
    this.sun = new THREE.DirectionalLight(0xfff1dc, 5);
    this.sun.castShadow = true;
    this.sun.shadow.mapSize.setScalar(quality.shadowMap);
    this.sun.shadow.bias = -0.00018;
    this.sun.shadow.normalBias = 0.035;
    this.sun.shadow.radius = 2.5;
    this.sun.shadow.blurSamples = 12;
    scene.add(this.sun, this.sun.target);
    this.hemi = new THREE.HemisphereLight(0xf4f1ea, 0x8d877b, 0.12);
    scene.add(this.hemi);
    this.sky = new Sky();
    this.sky.scale.setScalar(9000);
    const u = this.sky.material.uniforms;
    u.turbidity.value = 4.2; u.rayleigh.value = 1.4; u.mieCoefficient.value = 0.004; u.mieDirectionalG.value = 0.82;
    this.pmrem = new THREE.PMREMGenerator(renderer);
    this.probe = new THREE.Scene();
    this.probeSky = new Sky();
    this.probeSky.scale.setScalar(9000);
    Object.assign(this.probeSky.material.uniforms.turbidity, { value: 4.2 });
    this.probeSky.material.uniforms.rayleigh.value = 1.4;
    this.probeSky.material.uniforms.mieCoefficient.value = 0.004;
    this.probe.add(this.probeSky);
    // A ground under the probe, so soffits and reveals are lit from below by
    // the park the way they are on site, not by a black lower hemisphere.
    this.ground = new THREE.Mesh(new THREE.CircleGeometry(4000, 24).rotateX(-Math.PI / 2), new THREE.MeshBasicMaterial({ color: 0x7c8268 }));
    this.ground.position.y = -2;
    this.probe.add(this.ground);
    this.envTarget = null;
    this.envDirty = true;
    this.lastEnv = 0;
    this.direction = new THREE.Vector3();
    this.center = new THREE.Vector3(0, 0, 0);
    this.shadowRadius = 90;
    this.onChange = () => {};
  }

  set(hour = this.hour, day = this.day) {
    this.hour = hour; this.day = day;
    const d = solarDirection(hour, day);
    this.direction.copy(d);
    const altitude = Math.asin(d.y) * 180 / Math.PI;
    // daylight level: 0 at night, 1 from ~12° altitude
    this.level = smooth(-6, 14, altitude);
    const warm = smooth(2, 30, altitude);
    const sunColor = new THREE.Color().setRGB(1, 0.62 + 0.34 * warm, 0.38 + 0.52 * warm);
    this.sun.color.copy(sunColor);
    this.sun.intensity = 5.2 * smooth(-1.5, 10, altitude);
    this.sun.castShadow = altitude > -1.5;
    this.hemi.intensity = 0.09 + 0.08 * this.level;
    const sunPos = d.clone();
    if (sunPos.y < -0.12) sunPos.y = -0.12;
    for (const s of [this.sky, this.probeSky]) s.material.uniforms.sunPosition.value.copy(sunPos);
    this.ground.material.color.setRGB(0.16 + 0.32 * this.level, 0.17 + 0.33 * this.level, 0.13 + 0.25 * this.level);
    this.placeSun();
    this.envDirty = true;
    this.onChange(this);
  }

  // Fit the shadow frustum to what is on screen: the building closely, the
  // park when the view widens. Texel density stays roughly constant.
  setShadowFocus(center, radius) {
    this.center.copy(center);
    this.shadowRadius = radius;
    this.placeSun();
  }

  placeSun() {
    const d = this.direction.y > 0.03 ? this.direction : new THREE.Vector3(this.direction.x, 0.03, this.direction.z).normalize();
    const r = this.shadowRadius;
    this.sun.position.copy(this.center).addScaledVector(d, r * 3);
    this.sun.target.position.copy(this.center);
    const cam = this.sun.shadow.camera;
    cam.left = -r; cam.right = r; cam.top = r; cam.bottom = -r;
    cam.near = r * 0.5; cam.far = r * 6;
    cam.updateProjectionMatrix();
    this.sun.shadow.needsUpdate = true;
    this.renderer.shadowMap.needsUpdate = true;
  }

  // Background for the maquette views: the sky's horizon tone, kept pale.
  backgroundColor(target = new THREE.Color()) {
    const day = new THREE.Color(0xe7ebe8), dusk = new THREE.Color(0xd9c6b6), night = new THREE.Color(0x1c2228);
    const altitude = Math.asin(this.direction.y) * 180 / Math.PI;
    const t = smooth(-2, 18, altitude);
    target.copy(night).lerp(dusk, smooth(-8, 2, altitude)).lerp(day, t);
    return target;
  }

  update(now) {
    if (!this.envDirty || now - this.lastEnv < 220) return;
    this.envDirty = false;
    this.lastEnv = now;
    const old = this.envTarget;
    this.envTarget = this.pmrem.fromScene(this.probe, 0.02, 1, 12000);
    this.scene.environment = this.envTarget.texture;
    this.scene.environmentIntensity = 0.16 + 0.2 * this.level;
    old?.dispose();
  }
}
