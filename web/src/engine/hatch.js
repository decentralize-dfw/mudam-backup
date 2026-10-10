import * as THREE from 'three';

// Section poché, after angora/viewer/src/section.js: what the plane cuts goes
// dark, and a 45° ruling rides on top of it. The ruling is filtered over the
// pixel footprint (the integral of the square wave), so it greys out with
// distance instead of turning into a coarse barcode.
export const SECTION_POCHE = { pitch: 0.16, duty: 0.07, ground: [0.055, 0.052, 0.05], ink: [0.42, 0.40, 0.37], strength: 0.6 };

const HATCHES = new Set();
export function setHatchLight(level) {
  for (const m of HATCHES) m.uniforms.uLight.value = 0.55 + 0.45 * level;
}

export function createHatchMaterial({ pitch, duty, ground, ink, strength }) {
  const f = (v) => v.map((x) => x.toFixed(3)).join(', ');
  const material = new THREE.ShaderMaterial({
    side: THREE.DoubleSide,
    polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2,
    uniforms: { uLight: { value: 1 } },
    vertexShader: /* glsl */`varying vec3 vWorld;
      void main() {
        vec4 world = modelMatrix * vec4(position, 1.0);
        vWorld = world.xyz;
        gl_Position = projectionMatrix * viewMatrix * world;
      }`,
    fragmentShader: /* glsl */`varying vec3 vWorld;
      uniform float uLight;
      const float INK = ${(2 * duty).toFixed(5)};
      float ruled(float x) { return floor(x) * INK + min(fract(x), INK); }
      void main() {
        float v = (vWorld.x + vWorld.z) / ${pitch.toFixed(4)};
        float w = max(fwidth(v), 1e-5);
        float hatch = clamp((ruled(v + 0.5 * w) - ruled(v - 0.5 * w)) / w, 0.0, 1.0);
        vec3 c = mix(vec3(${f(ground)}), vec3(${f(ink)}), hatch * ${strength.toFixed(2)});
        gl_FragColor = vec4(c * uLight, 1.0);
      }`,
  });
  HATCHES.add(material);
  return material;
}

// Flat caps from demo/data/sections.json (x,z pairs + triangle indices).
export function capGeometry(cut) {
  const n = cut.p.length / 2;
  const pos = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) { pos[i * 3] = cut.p[i * 2]; pos[i * 3 + 2] = cut.p[i * 2 + 1]; }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  g.setIndex(cut.i);
  g.computeBoundingSphere();
  return g;
}

export function capLines(cut) {
  const seg = [];
  for (const line of cut.lines) {
    for (let i = 0; i + 3 < line.length; i += 2) seg.push(line[i], 0, line[i + 1], line[i + 2], 0, line[i + 3]);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(seg, 3));
  return g;
}
