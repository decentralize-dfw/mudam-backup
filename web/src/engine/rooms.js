import * as THREE from 'three';

// Tinted floor overlays for the rooms (from the model's own floor slabs, see
// scripts/prepare_data.py). They make rooms clickable in the section and in
// plan, and carry the exhibition colour.
export class Rooms {
  constructor(building) {
    this.building = building;
    this.list = [];
    this.byId = new Map();
    this.meshes = [];
    this.selected = null;
    this.hovered = null;
    this.visible = false;
  }

  init(data, colourOf) {
    this.list = data.rooms;
    for (const r of this.list) {
      this.byId.set(r.id, r);
      const shape = new THREE.Shape(r.polygon.map(([x, z]) => new THREE.Vector2(x, -z)));
      const geo = new THREE.ShapeGeometry(shape).rotateX(-Math.PI / 2);
      const colour = new THREE.Color(colourOf(r) ?? 0x8b8f8c);
      const mat = new THREE.MeshBasicMaterial({ color: colour, transparent: true, opacity: 0, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -4, polygonOffsetUnits: -4 });
      const mesh = new THREE.Mesh(geo, mat);
      mesh.position.y = r.y + 0.03;
      mesh.renderOrder = 4;
      mesh.userData.room = r;
      r.mesh = mesh;
      r.colour = colour;
      // outline
      const pts = r.polygon.map(([x, z]) => new THREE.Vector3(x, 0, z));
      pts.push(pts[0].clone());
      const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), new THREE.LineBasicMaterial({ color: colour, transparent: true, opacity: 0, depthTest: false }));
      line.position.y = r.y + 0.06;
      line.renderOrder = 5;
      r.line = line;
      const group = this.building.floorGroups[r.floor];
      group.add(mesh, line);
      this.meshes.push(mesh);
    }
  }

  // Opacity of every overlay from the current mode, selection and hover.
  refresh({ show, exhibitionRooms = null }) {
    this.visible = show;
    for (const r of this.list) {
      const inShow = !exhibitionRooms || exhibitionRooms.has(r.id);
      const active = r.id === this.selected;
      const hover = r.id === this.hovered;
      let o = 0, lo = 0;
      if (show) {
        o = inShow ? (active ? 0.24 : hover ? 0.2 : 0.11) : (hover ? 0.1 : 0.03);
        lo = active ? 1 : inShow ? 0.55 : 0.12;
      }
      r.mesh.material.opacity = o;
      r.line.material.opacity = lo;
      r.mesh.visible = r.line.visible = show;
    }
  }

  pick(raycaster) {
    if (!this.visible) return null;
    const hits = raycaster.intersectObjects(this.meshes.filter((m) => m.parent?.visible), false);
    return hits[0]?.object.userData.room ?? null;
  }

  // World-space centre of a room for framing.
  centre(r) {
    const box = new THREE.Box3();
    for (const [x, z] of r.polygon) box.expandByPoint(new THREE.Vector3(x, r.y, z));
    const c = box.getCenter(new THREE.Vector3());
    c.y = r.y + 1.2 + this.building.lift(r.floor);
    return { centre: c, size: box.getSize(new THREE.Vector3()) };
  }
}
