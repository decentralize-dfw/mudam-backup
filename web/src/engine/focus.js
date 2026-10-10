import * as THREE from 'three';

// A room picked on a floor: its interior lights come on and everything else
// (the rest of the building, the works, the surroundings) darkens by 70 %.
// The room is a soft mask drawn from its plan polygon into a texture over the
// building's extents; every material reads it by world position (x, z) and
// height, so the room stays lit whatever its shape. uFocus fades it in and out.
const DIM = 0.7;
const SIZE = 1024;
// shared with the section poché (hatch.js), a material of its own
export const FOCUS = {
  uFocus: { value: 0 },
  uFocusTex: { value: null },
  uFocusRect: { value: new THREE.Vector4(0, 0, 1, 1) },
  uFocusY: { value: new THREE.Vector2(-1e4, 1e4) },
  uFocusDim: { value: DIM },
};

export class RoomFocus {
  constructor(stage, extents) {
    this.stage = stage;
    this.canvas = document.createElement('canvas');
    this.canvas.width = this.canvas.height = SIZE;
    this.texture = new THREE.CanvasTexture(this.canvas);
    this.texture.flipY = false;
    this.texture.colorSpace = THREE.NoColorSpace;
    const pad = 4;
    this.rect = FOCUS.uFocusRect.value.set(extents.min.x - pad, extents.min.z - pad, extents.max.x + pad, extents.max.z + pad);
    FOCUS.uFocusTex.value = this.texture;
    this.uniforms = FOCUS;
    this.patched = new WeakSet();
    this.room = null;
    // one warm light in the room; made now so the number of lights never
    // changes (a new light would recompile every material)
    this.light = new THREE.PointLight(0xffd9b0, 0, 20, 1.4);
    stage.scene.add(this.light);
    stage.building.addHook((shader, material, kind) => { if (kind === 'band' || kind === 'line') this.inject(shader); });
  }

  // Shader edits shared by every patched material.
  inject(shader) {
    Object.assign(shader.uniforms, this.uniforms);
    shader.vertexShader = shader.vertexShader
      .replace('#include <common>', '#include <common>\nvarying vec3 vFocusPos;')
      .replace('#include <project_vertex>', `#include <project_vertex>
      {
        vec4 focusPos = vec4( transformed, 1.0 );
        #ifdef USE_BATCHING
          focusPos = batchingMatrix * focusPos;
        #endif
        #ifdef USE_INSTANCING
          focusPos = instanceMatrix * focusPos;
        #endif
        vFocusPos = ( modelMatrix * focusPos ).xyz;
      }`);
    shader.fragmentShader = shader.fragmentShader
      .replace('#include <common>', `#include <common>
      varying vec3 vFocusPos;
      uniform float uFocus;
      uniform float uFocusDim;
      uniform sampler2D uFocusTex;
      uniform vec4 uFocusRect;
      uniform vec2 uFocusY;`)
      .replace('#include <dithering_fragment>', `#include <dithering_fragment>
      if ( uFocus > 0.0 ) {
        vec2 focusUv = ( vFocusPos.xz - uFocusRect.xy ) / ( uFocusRect.zw - uFocusRect.xy );
        float inRoom = texture2D( uFocusTex, focusUv ).r * step( uFocusY.x, vFocusPos.y ) * step( vFocusPos.y, uFocusY.y );
        gl_FragColor.rgb *= 1.0 - uFocusDim * uFocus * ( 1.0 - inRoom );
      }`);
  }

  // Any other material (surroundings, works, room tints, arrows) takes part.
  patch(material) {
    if (!material || this.patched.has(material) || material.isShaderMaterial || material.isRawShaderMaterial) return;
    this.patched.add(material);
    const prev = material.onBeforeCompile;
    // the key of the material as it was (by default the source of its own
    // onBeforeCompile), taken now: two materials with different edits must
    // not share a program
    const base = material.customProgramCacheKey();
    material.onBeforeCompile = (shader, renderer) => {
      prev?.call(material, shader, renderer);
      this.inject(shader);
    };
    material.customProgramCacheKey = () => `focus|${base}`;
    material.needsUpdate = true;
  }

  patchRoots(roots) {
    for (const root of roots) {
      root?.traverse((o) => {
        if (!o.material) return;
        for (const m of Array.isArray(o.material) ? o.material : [o.material]) this.patch(m);
      });
    }
  }

  // Light `room` (null: none), fading over `ms`.
  set(room, ms = 600) {
    const same = room?.id === this.room?.id;
    this.room = room;
    if (room && !same) this.draw(room);
    const from = this.uniforms.uFocus.value, to = room ? 1 : 0;
    if (from === to && same) return;
    const level = this.light.intensity;
    this.stage.tweens.run('room-focus', ms, (t) => {
      this.uniforms.uFocus.value = from + (to - from) * t;
      this.light.intensity = room ? level + (this.lightLevel - level) * t : level * (1 - t);
      this.onChange?.();
      this.stage.renderer.shadowMap.needsUpdate = true;
      this.stage.dirty = true;
    });
  }

  draw(room) {
    const ctx = this.canvas.getContext('2d');
    const [x0, z0, x1, z1] = this.rect.toArray();
    const px = (x) => ((x - x0) / (x1 - x0)) * SIZE, pz = (z) => ((z - z0) / (z1 - z0)) * SIZE;
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, SIZE, SIZE);
    ctx.filter = 'blur(3px)';
    ctx.fillStyle = '#fff';
    ctx.beginPath();
    room.polygon.forEach(([x, z], i) => (i ? ctx.lineTo(px(x), pz(z)) : ctx.moveTo(px(x), pz(z))));
    ctx.closePath();
    ctx.fill();
    ctx.filter = 'none';
    this.texture.needsUpdate = true;
    // the room's own storey, floor to ceiling
    this.uniforms.uFocusY.value.set(room.y - 0.6, room.y + 4.7);
    // the light: over the middle of the room, as strong as the room is large
    let a = 0, cx = 0, cz = 0;
    const p = room.polygon;
    for (let i = 0; i < p.length; i++) {
      const [xa, za] = p[i], [xb, zb] = p[(i + 1) % p.length], c = xa * zb - xb * za;
      a += c; cx += (xa + xb) * c; cz += (za + zb) * c;
    }
    const area = Math.abs(a / 2);
    if (Math.abs(a) > 1e-6) { cx /= 3 * a; cz /= 3 * a; } else { [cx, cz] = room.anchor; }
    this.light.position.set(cx, room.y + 2.8, cz);
    this.light.distance = Math.sqrt(area) * 1.7 + 6;
    this.lightLevel = 30 + Math.min(70, area * 0.25);
  }

  // Background, darkened with the rest.
  shade(color) {
    return color.multiplyScalar(1 - DIM * this.uniforms.uFocus.value);
  }
}
