import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { lerp, ease } from './tween.js';

// The official Mudam plans put the entrance at the bottom of the sheet. In the
// model frame (x east, z south) that is a view from the north-east; this
// azimuth reproduces the sheet orientation in plan and frames the iso views.
export const PLAN_AZIMUTH = Math.atan2(0.7295, -0.6839);

const angleLerp = (a, b, t) => {
  let d = ((b - a + Math.PI) % (2 * Math.PI)) - Math.PI;
  if (d < -Math.PI) d += 2 * Math.PI;
  return a + d * t;
};

// Two cameras share one set of intents: an orthographic one for the
// maquette, section and plan views, and a perspective one for standing in a
// room in front of a work.
export class Rig {
  constructor(dom, tweens) {
    this.dom = dom;
    this.tweens = tweens;
    this.ortho = new THREE.OrthographicCamera(-1, 1, 1, -1, 1, 4000);
    this.persp = new THREE.PerspectiveCamera(52, 1, 0.05, 6000);
    this.orbit = new OrbitControls(this.ortho, dom);
    this.orbit.enableDamping = true;
    this.orbit.dampingFactor = 0.09;
    this.orbit.zoomToCursor = true;
    this.orbit.minZoom = 0.12;
    this.orbit.maxZoom = 40;
    this.orbit.maxPolarAngle = Math.PI * 0.47;
    this.orbit.screenSpacePanning = true;
    this.orbit.touches = { ONE: THREE.TOUCH.ROTATE, TWO: THREE.TOUCH.DOLLY_PAN };
    this.look = new OrbitControls(this.persp, dom);
    this.look.enableDamping = true;
    this.look.dampingFactor = 0.1;
    this.look.enablePan = false;
    this.look.rotateSpeed = -0.35; // drag the room, not the camera
    this.look.enableZoom = false;
    this.look.enabled = false;
    this.mode = 'ortho';
    this.viewSize = 120; // metres across the shorter screen side at zoom 1
    this.distance = 600;
    this.width = 1; this.height = 1;
    this.planLock = false;
    this.insets = { left: 0, right: 0, bottom: 0 };
  }

  get camera() { return this.mode === 'ortho' ? this.ortho : this.persp; }
  get controls() { return this.mode === 'ortho' ? this.orbit : this.look; }

  // Screen space taken by panels: the scene is framed in what is left.
  setInsets({ left = 0, right = 0, bottom = 0 }, ms = 450) {
    const from = { ...this.insets };
    const to = { left, right, bottom };
    if (from.left === left && from.right === right && from.bottom === bottom) return;
    this.tweens.run('insets', ms, (t) => {
      this.insets = { left: lerp(from.left, to.left, t), right: lerp(from.right, to.right, t), bottom: lerp(from.bottom, to.bottom, t) };
      this.resize(this.width, this.height);
    });
  }

  resize(w, h) {
    this.width = w; this.height = h;
    const dx = this.insets.left - this.insets.right, b = this.insets.bottom;
    const fw = w + Math.abs(dx), fh = h + b;
    const k = this.viewSize / Math.min(w, h); // metres per pixel at zoom 1
    this.ortho.left = -k * fw / 2; this.ortho.right = k * fw / 2;
    this.ortho.top = k * fh / 2; this.ortho.bottom = -k * fh / 2;
    const offX = dx < 0 ? -dx : 0;
    for (const cam of [this.ortho, this.persp]) {
      if (Math.abs(dx) < 0.5 && b < 0.5) cam.clearViewOffset();
      else cam.setViewOffset(fw, fh, offX, b, w, h);
    }
    this.ortho.updateProjectionMatrix();
    this.persp.aspect = fw / fh;
    this.persp.fov = w / h < 0.8 ? 68 : 52;
    this.persp.updateProjectionMatrix();
    this.onResize?.();
  }

  // Current orbit pose of the orthographic camera.
  pose() {
    const t = this.orbit.target;
    const off = this.ortho.position.clone().sub(t);
    const s = new THREE.Spherical().setFromVector3(off);
    return { target: t.clone(), azimuth: s.theta, polar: s.phi, zoom: this.ortho.zoom };
  }

  setPose({ target, azimuth, polar, zoom }) {
    const s = new THREE.Spherical(this.distance, Math.max(1e-4, polar), azimuth);
    this.orbit.target.copy(target);
    this.ortho.position.copy(target).add(new THREE.Vector3().setFromSpherical(s));
    this.ortho.zoom = zoom;
    this.ortho.up.set(0, 1, 0);
    this.ortho.lookAt(target);
    this.ortho.updateProjectionMatrix();
  }

  // Fly the orthographic camera; a perspective view hands over first.
  async flyTo(pose, ms = 1300) {
    if (this.mode !== 'ortho') this.useOrtho();
    const a = this.pose();
    const b = { target: pose.target.clone(), azimuth: pose.azimuth ?? a.azimuth, polar: pose.polar ?? a.polar, zoom: pose.zoom ?? a.zoom };
    this.orbit.enabled = false;
    const done = await this.tweens.run('camera', ms, (t) => {
      this.setPose({
        target: a.target.clone().lerp(b.target, t),
        azimuth: angleLerp(a.azimuth, b.azimuth, t),
        polar: lerp(a.polar, b.polar, t),
        // zoom is a scale: interpolate it geometrically
        zoom: Math.exp(lerp(Math.log(a.zoom), Math.log(b.zoom), t)),
      });
    }, ease.inOut);
    this.orbit.enabled = true;
    this.orbit.update();
    return done;
  }

  setPlan(on) {
    this.planLock = on;
    this.orbit.enableRotate = !on;
    this.orbit.minPolarAngle = on ? 0 : 0;
    this.orbit.maxPolarAngle = on ? 1e-3 : Math.PI * 0.47;
  }

  useOrtho() {
    this.mode = 'ortho';
    this.look.enabled = false;
    this.orbit.enabled = true;
  }

  // Stand at eye level in front of a work and look at it.
  async visit(eye, at, ms = 1200) {
    const from = this.mode === 'persp'
      ? { eye: this.persp.position.clone(), at: this.look.target.clone() }
      : null;
    this.mode = 'persp';
    this.orbit.enabled = false;
    this.look.enabled = false;
    if (!from) {
      // arrive from slightly above and behind the standing point
      const back = eye.clone().sub(at).setY(0).normalize();
      this.persp.position.copy(eye).addScaledVector(back, 3.2).add(new THREE.Vector3(0, 2.4, 0));
      this.persp.lookAt(at);
    }
    const p0 = this.persp.position.clone();
    const dir0 = new THREE.Vector3(); this.persp.getWorldDirection(dir0);
    const t0 = p0.clone().add(dir0.multiplyScalar(eye.distanceTo(at)));
    const done = await this.tweens.run('camera', ms, (t) => {
      this.persp.position.copy(p0).lerp(eye, t);
      const target = t0.clone().lerp(at, t);
      this.persp.lookAt(target);
    }, ease.inOut);
    // hand control to the look-around orbit: pivot is the eye itself
    const dir = at.clone().sub(eye).normalize();
    this.look.target.copy(eye).addScaledVector(dir, 0.01);
    this.persp.position.copy(eye);
    this.persp.lookAt(at);
    this.look.enabled = true;
    this.look.update();
    return done;
  }

  update() {
    if (this.mode === 'ortho') { if (this.orbit.enabled) this.orbit.update(); }
    else if (this.look.enabled) this.look.update();
  }
}
