import * as THREE from 'three';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

// Scene -> multisampled HDR target -> ambient occlusion -> tone-mapped screen.
//
// The AO pass is handed the scene target's own depth instead of re-rendering
// the scene with an override material. An override material ignores each
// mesh's clipping planes, so a cut floor would be darkened by the storeys the
// cut has removed. Normals are reconstructed from that depth.
export class Pipeline {
  constructor(renderer, scene, quality) {
    this.renderer = renderer;
    this.scene = scene;
    this.quality = quality;
    const size = renderer.getDrawingBufferSize(new THREE.Vector2());
    const depthTexture = new THREE.DepthTexture(size.x, size.y);
    depthTexture.type = THREE.UnsignedIntType;
    this.sceneTarget = new THREE.WebGLRenderTarget(size.x, size.y, {
      type: THREE.HalfFloatType,
      samples: quality.msaa,
      depthTexture,
    });
    this.aoTarget = new THREE.WebGLRenderTarget(size.x, size.y, { type: THREE.HalfFloatType });
    this.camera = null;
    this.ao = null;
    // > 1: the scene is drawn that much larger and scaled down on output (the
    // line drawing: one-pixel lines become half a pixel)
    this.scale = 1;
    this.targetSize = new THREE.Vector2(size.x, size.y);
    this.aoEnabled = quality.ao;
    this.output = new OutputPass();
    this.output.renderToScreen = true;
  }

  setCamera(camera) {
    if (this.camera === camera) return;
    this.camera = camera;
    if (!this.aoEnabled) return;
    const size = this.renderer.getDrawingBufferSize(new THREE.Vector2());
    if (!this.ao) {
      // (r180 dereferences its internal G-buffer when given a depth texture in
      // the constructor, so the external depth is attached afterwards)
      this.ao = new GTAOPass(this.scene, camera, size.x, size.y);
      this.ao.setGBuffer(this.sceneTarget.depthTexture);
      this.ao.output = GTAOPass.OUTPUT.Default;
      this.ao.blendIntensity = 0.9;
      this.ao.updateGtaoMaterial({ radius: 0.55, distanceExponent: 1.4, thickness: 1.6, scale: 1.0, samples: this.quality.aoSamples, distanceFallOff: 1, screenSpaceRadius: false });
      this.ao.updatePdMaterial({ lumaPhi: 10, depthPhi: 2, normalPhi: 3, radius: 6, radiusExponent: 1, rings: 2, samples: 16 });
    } else {
      this.ao.camera = camera;
      const perspective = camera.isPerspectiveCamera ? 1 : 0;
      for (const material of [this.ao.gtaoMaterial, this.ao.pdMaterial]) {
        if (material.defines.PERSPECTIVE_CAMERA !== perspective) {
          material.defines.PERSPECTIVE_CAMERA = perspective;
          material.needsUpdate = true;
        }
      }
    }
  }

  setSize() {
    const size = this.renderer.getDrawingBufferSize(new THREE.Vector2());
    const max = Math.min(this.renderer.capabilities.maxTextureSize, 6144);
    const k = Math.min(this.scale, max / Math.max(size.x, size.y));
    size.multiplyScalar(Math.max(1, k)).round();
    this.targetSize.copy(size);
    this.sceneTarget.setSize(size.x, size.y);
    this.aoTarget.setSize(size.x, size.y);
    this.ao?.setSize(size.x, size.y);
    this.output.setSize(size.x, size.y);
  }

  setScale(k) {
    if (k === this.scale) return;
    this.scale = k;
    this.setSize();
  }

  render() {
    const { renderer, scene, camera } = this;
    renderer.setRenderTarget(this.sceneTarget);
    renderer.clear();
    renderer.render(scene, camera);
    let source = this.sceneTarget;
    // (off in the line drawing: it would grey the white edges at corners)
    if (this.ao && this.aoEnabled && !this.aoOff) {
      this.ao.render(renderer, this.aoTarget, this.sceneTarget);
      source = this.aoTarget;
    }
    this.output.render(renderer, null, source);
  }
}
