"""Locate enclosure escape seams using near-parallel diagnostic rays."""
from pathlib import Path
import runpy,json,sys,math
from mathutils import Vector
B=Path(__file__).resolve().parents[1];sys.argv=['audit','--','12_Blender_Model/scenes/MUDAM_R82_BATI_MERDIVEN_GIRIS_KABUK_v001.blend'];g=runpy.run_path(str(B/'scripts/audit_interior_enclosure.py'));tree=g['tree'];point=g['point'];names=g['names'];owners=g['owners'];out=[]
for xy,z in [([565,591],1.2),([565,591],6.0590748),([674,474],1.2),([724,277],1.2)]:
 rays=[]
 for angle in [134,135,136,178,179,179.8,179.95,180,180.05,180.2,181,182]:
  d=Vector((math.cos(math.radians(angle)),math.sin(math.radians(angle)),0));hit=tree.ray_cast(point(xy,z),d,200);rays.append(dict(angle=angle,name=None if hit[0] is None else names[owners[hit[2]]],world=None if hit[0] is None else list(hit[0]),distance=hit[3]))
 out.append(dict(canonical=xy,z=z,rays=rays))
(B/'reports/ENCLOSURE_SEAM_DIAGNOSTIC.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
