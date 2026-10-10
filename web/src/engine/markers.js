import * as THREE from 'three';

// HTML pins anchored to 3D points. A pin with an outward normal fades when
// its face turns away from the camera, so pins on the far side of the
// building do not float over the near side.
export class Markers {
  constructor(host) {
    this.host = host;
    this.layer = document.createElement('div');
    this.layer.className = 'marker-layer';
    host.append(this.layer);
    this.items = [];
    this.v = new THREE.Vector3();
  }

  clear() {
    this.layer.replaceChildren();
    this.items = [];
  }

  // spec: { id, position:[x,y,z], normal?:[x,y,z], label, index?, kind, onClick, lift?:()=>number }
  add(spec) {
    const el = document.createElement('button');
    el.type = 'button';
    el.className = `marker marker-${spec.kind ?? 'info'}`;
    el.dataset.id = spec.id;
    if (spec.index != null) {
      const n = document.createElement('i');
      n.textContent = spec.index;
      el.append(n);
    } else {
      el.append(document.createElement('i'));
    }
    const label = document.createElement('span');
    label.textContent = spec.label;
    if (spec.kind === 'room') label.lang = 'fr';
    el.append(label);
    el.setAttribute('aria-label', spec.label);
    el.addEventListener('click', (e) => { e.stopPropagation(); spec.onClick?.(spec); });
    this.layer.append(el);
    const item = { ...spec, el, p: new THREE.Vector3(...spec.position), n: spec.normal ? new THREE.Vector3(...spec.normal).normalize() : null };
    this.items.push(item);
    return item;
  }

  setActive(id) {
    for (const it of this.items) it.el.classList.toggle('active', it.id === id);
  }

  update(camera, width, height) {
    const dir = new THREE.Vector3();
    camera.getWorldDirection(dir);
    for (const it of this.items) {
      this.v.copy(it.p);
      if (it.lift) this.v.y += it.lift();
      let facing = 1;
      if (it.n) {
        const toCam = camera.isOrthographicCamera ? dir.clone().negate() : camera.position.clone().sub(this.v).normalize();
        facing = THREE.MathUtils.smoothstep(it.n.dot(toCam), -0.25, 0.15);
      }
      this.v.project(camera);
      const off = this.v.z < -1 || this.v.z > 1 || Math.abs(this.v.x) > 1.05 || Math.abs(this.v.y) > 1.05;
      if (off || (it.visible && !it.visible())) { it.el.style.display = 'none'; continue; }
      it.el.style.display = '';
      const x = (this.v.x + 1) * width / 2, y = (1 - this.v.y) * height / 2;
      it.el.style.transform = `translate3d(${x.toFixed(1)}px, ${y.toFixed(1)}px, 0)`;
      it.el.style.opacity = it.el.classList.contains('active') ? 1 : (0.25 + 0.75 * facing).toFixed(2);
      it.el.classList.toggle('behind', facing < 0.5);
    }
  }
}
