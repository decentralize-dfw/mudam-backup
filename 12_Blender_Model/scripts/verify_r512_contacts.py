import bpy,json,re,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];controls=json.loads((R/'reports/R512_TARGET_CONTROLS.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/'.local_source_cache/r316/museum_ring_reference.blend'));dg=bpy.context.evaluated_depsgraph_get();visible=[]
for x,y,z in controls:
 h,p,n,*_=bpy.context.scene.ray_cast(dg,Vector((x,y,35)),Vector((0,0,-1)),distance=80)
 if h and abs(p.z-z)<.25 and n.z>.65:visible.append([x,y,z,p.z])
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R512_KALE_DIS_TASAN_TOPRAK_KESIM_ADAY_v001.blend'));verts=[];faces=[];owners=[];names=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.hide_render:continue
 name=o.name.upper();rev=re.match(r'R(\d+)_',o.name);number=int(rev[1]) if rev else 0
 eligible=name.startswith(('R152_CLASS2_TERRAIN','R152_FORECOURT','R152_PATH')) or (317<=number<=512 and any(k in name for k in ['FLOOR','GROUND','COURT','LAWN','PATH','PASSAGE','PLAZA','TERRACE','EARTH_COVER']) and not any(k in name for k in ['WALL','GLAZ','BORDER','RAIL','FRAME','STAIR','COPING','DOOR','ROOF','GLASS']))
 if not eligible:continue
 me=o.data;me.calc_loop_triangles();start=len(verts);verts.extend(o.matrix_world@v.co for v in me.vertices)
 for t in me.loop_triangles:faces.append(tuple(start+i for i in t.vertices));owners.append(o.name)
 names.append(o.name)
bvh=BVHTree.FromPolygons(verts,faces,all_triangles=True);out=[]
for x,y,z,src in visible:
 p,n,i,d=bvh.ray_cast(Vector((x,y,35)),Vector((0,0,-1)),80)
 if p is not None:out.append(dict(x=x,y=y,ground=z,source=src,model=p.z,error=p.z-z,object=owners[i]))
 else:out.append(dict(x=x,y=y,ground=z,source=src,model=None,error=None,object=None))
(R/'reports/R512_TARGET_CONTACT_CHECK.json').write_text(json.dumps(dict(eligibleObjects=names,controls=len(controls),visibleControls=len(visible),rows=out,scope='New full marked-ring ground contact check after R485-R508 changes; source-visible stable class2 cells only, excludes source canopy and roofs. No overall acceptance inferred.'),indent=2));print('VISIBLE',len(visible),'ERROR>1m',sum(q['error'] is not None and abs(q['error'])>1 for q in out),'NO_HIT',sum(q['error'] is None for q in out))
