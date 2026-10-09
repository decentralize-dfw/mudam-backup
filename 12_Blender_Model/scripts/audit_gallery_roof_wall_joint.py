"""Read-only local rays through the upper gallery roof perimeter below its skin."""
from pathlib import Path
import bpy,json,sys,math,re
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B/'scripts'))
from release_utils import verified_current_scene
r=verified_current_scene();bpy.ops.wm.open_mainfile(filepath=str(B.parent/r['file']))
P=json.loads((B/'config/upper_gallery_roof.json').read_text());V=json.loads((B/'config/vector_reference.json').read_text())
UP=next(p['draft_value'] for p in json.loads((B/'config/vertical_study.json').read_text())['parameters'] if p['id']=='Z_LP1_FINISH')
base=UP+P['roof_base_above_upper_floor'];high=P['roof_high_z'];verts=[];faces=[];owners=[];names=[];deps=bpy.context.evaluated_depsgraph_get()
for ob in bpy.context.scene.objects:
    if ob.type!='MESH' or ob.hide_render or not ob.visible_get() or ob.get('level_id')=='SITE':continue
    if re.search('TREE|MOAT|HISTORIC|LAMP|LENS|SPOT|FIXTURE|RAIL|SEAT|CHAIR|SHADING',ob.name,re.I):continue
    eo=ob.evaluated_get(deps);me=eo.to_mesh();start=len(verts);verts.extend(eo.matrix_world@v.co for v in me.vertices);names.append(ob.name)
    for f in me.polygons:faces.append(tuple(start+i for i in f.vertices));owners.append(len(names)-1)
    eo.to_mesh_clear()
tree=BVHTree.FromPolygons(verts,faces);rows=[];count=0;hist={}
for side in ['E','W']:
    poly=V['gallery_LP1_'+side]['loops_xy'][0];ymin=min(p[1] for p in poly);ymax=max(p[1] for p in poly);pitch=(ymax-ymin)/P['bay_counts'][side]
    for ei,(pa,pb) in enumerate(zip(poly,poly[1:]+poly[:1])):
        a=Vector((*pa,0));b=Vector((*pb,0));edge=b-a;n=Vector((-edge.y,edge.x,0)).normalized();steps=math.ceil(edge.length/.05)
        for i in range(steps):
            p=a+edge*((i+.5)/steps);t=((p.y-ymin)/pitch)%1
            if p.y>=ymax-1e-5:t=1
            z=base+(high-base)*math.sqrt(max(0,1-(1-t)**2))
            for drop in [.1,.3,.6]:
                q=Vector((p.x,p.y,z-drop));count+=1;hit=tree.ray_cast(q+n*.6,-n,1.2)
                if hit[0] is None:rows.append(dict(side=side,edge=ei,fraction=(i+.5)/steps,position=list(q),roof_z=z,drop=drop))
                else:
                    name=names[owners[hit[2]]];hist[name]=hist.get(name,0)+1
rev=re.search(r'_R(\d+)_',r['file']).group(1)
out=dict(file=r['file'],samples=count,missing=rows,missing_count=len(rows),hit_objects=hist,construction_acceptance=False,
         limits=['Only registered R24 outer roof perimeters, not internal glass rows.', 'Local 1.2m cross-boundary band; misses need source classification before changing geometry.'])
(B/'reports'/f'R{rev}_gallery_roof_wall_joint.json').write_text(json.dumps(out,indent=2));print('GALLERY ROOF WALL',count,len(rows))
