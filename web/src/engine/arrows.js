import * as THREE from 'three';
import { FLOORS } from './building.js';

// Katları ayır: an upright arrow on every room of every storey, carrying the
// room's name from the official plans (the label is an HTML pin at the tip).
// Arrows live in the storeys' floor groups, so they rise with their storey.
export const ARROW_HEIGHT = 10;

export class RoomArrows {
  constructor(building) {
    this.groups = {};
    for (const f of FLOORS) {
      const g = new THREE.Group();
      g.name = `arrows-${f}`;
      g.visible = false;
      building.floorGroups[f].add(g);
      this.groups[f] = g;
    }
  }

  init(rooms) {
    const material = new THREE.MeshBasicMaterial({ color: new THREE.Color(0x1d2421) });
    const shaft = new THREE.CylinderGeometry(0.16, 0.16, ARROW_HEIGHT - 1.4, 10).translate(0, (ARROW_HEIGHT - 1.4) / 2, 0);
    const head = new THREE.ConeGeometry(0.62, 1.6, 20).translate(0, ARROW_HEIGHT - 0.8, 0);
    const foot = new THREE.CircleGeometry(0.7, 28).rotateX(-Math.PI / 2).translate(0, 0.02, 0);
    for (const r of rooms) {
      const g = this.groups[r.floor];
      if (!g) continue;
      const arrow = new THREE.Group();
      arrow.position.set(r.anchor[0], r.y + 0.05, r.anchor[1]);
      for (const geo of [shaft, head, foot]) arrow.add(new THREE.Mesh(geo, material));
      g.add(arrow);
    }
  }

  // Pin position at the arrow's tip, before the storey's lift.
  tip(r) { return [r.anchor[0], r.y + ARROW_HEIGHT + 0.9, r.anchor[1]]; }

  setVisible(on) {
    for (const g of Object.values(this.groups)) g.visible = on;
  }
}
