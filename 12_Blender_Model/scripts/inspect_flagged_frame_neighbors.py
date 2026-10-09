"""Resolve sampled end-contact candidates against evaluated non-glass architecture."""
from pathlib import Path
import bpy,json,sys,re
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B/'scripts'))
from release_utils import verified_current_scene
r=verified_current_scene();revision='R'+re.search(r'_R(\d+)_',r['file'])[1];q=json.loads((B/'reports'/f'{revision}_side_frame_end_contacts.json').read_text());assert q['file']==r['file'];bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']));deps=bpy.context.evaluated_depsgraph_get();vs=[];fs=[];owners=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob.hide_render or not ob.visible_get() or ob.get('level_id')=='SITE':continue
 label=(ob.name+' '+ob.get('element_type','')).upper()
 if any(x in label for x in ['GLASS','TREE','LAMP','LIGHT','SHADING','SLAT']):continue
 eo=ob.evaluated_get(deps);me=eo.to_mesh();off=len(vs);vs.extend(eo.matrix_world@v.co for v in me.vertices)
 for f in me.polygons:fs.append(tuple(off+i for i in f.vertices));owners.append(ob.name)
 eo.to_mesh_clear()
t=BVHTree.FromPolygons(vs,fs);rows=[]
for finding in q['findings']:
 p=Vector(finding['center']);neighbors={}
 for loc,normal,index,distance in t.find_nearest_range(p,.8):
  name=owners[index]
  if name==finding['name']:continue
  record=dict(name=name,distance=distance,signed_distance=(p-loc).dot(normal),surface=list(loc))
  if name not in neighbors or distance<neighbors[name]['distance']:neighbors[name]=record
 rows.append(dict(finding=finding,nearest_non_glass=sorted(neighbors.values(),key=lambda x:x['distance'])[:8]))
(B/'reports'/f'{revision}_flagged_frame_neighbors.json').write_text(json.dumps(dict(file=r['file'],rows=rows,construction_acceptance=False),indent=2));print(json.dumps(rows,indent=2))
