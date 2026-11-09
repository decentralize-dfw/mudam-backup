from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_MIMARI_ACIKLIKLAR_v076.blend'))
# Hand-traced rooflight outlines in registered 1400x1400 source top image.
traces=[[(541,664),(566,657),(573,676),(547,683)],[(626,645),(650,638),(657,656),(632,664)],[(727,705),(756,697),(763,716),(734,724)],[(831,733),(849,729),(854,746),(835,751)],[(1068,601),(1085,597),(1090,611),(1072,617)]]
roofs=[o for o in bpy.context.scene.objects if o.name.startswith('ARCH_MAIN_ROOF')];records=[]
for roof in roofs:
 bpy.context.view_layer.objects.active=roof
 for mod in list(roof.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
for k,trace in enumerate(traces):
 xy=[Vector((-80+(x-700)/25,-301+(700-y)/25,0)) for x,y in trace];mid=sum(xy,Vector())/4;hits=[]
 for roof in roofs:
  ok,p,n,idx=roof.ray_cast(Vector((mid.x,mid.y,10)),Vector((0,0,-1)))
  if ok:hits.append((p.z,roof,p,n))
 if not hits:continue
 z,roof,p,n=max(hits,key=lambda x:x[0]);n=n.normalized()
 if n.z<0:n=-n
 points=[Vector((v.x,v.y,p.z-(n.x*(v.x-p.x)+n.y*(v.y-p.y))/n.z)) for v in xy]
 def obj(name,verts,faces,mat=None):
  me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o)
  if mat:o.data.materials.append(mat)
  return o
 # Oriented closed cutter crosses roof thickness, removed after applied boolean.
 cutter=obj('temporary_aperture', [v+n*d for d in [-.5,.3] for v in points],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
 bpy.context.view_layer.objects.active=roof;mod=roof.modifiers.new('Real rooflight opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
 obj(f'ARCH_ROOFLIGHT_GLASS_{k}',[v+n*.025 for v in points],[(0,1,2,3)],bpy.data.materials['Glazing subdued blue grey'])
 for j in range(4):
  a=points[j];b=points[(j+1)%4];along=b-a;across=n.cross(along.normalized())*.035
  obj(f'ARCH_ROOFLIGHT_FRAME_{k}_{j}',[a-across+n*.06,b-across+n*.06,b+across+n*.06,a+across+n*.06],[(0,1,2,3)],bpy.data.materials['Painted light window frames'])
 records.append(dict(trace=trace,parent_roof=roof.name,center=list(p)))
s=bpy.context.scene;s['acceptance']='Architectural reconstruction WIP; not accepted. Measured rooflight outlines added, frame thickness provisional.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R169_MIMARI_CATI_PENCERELERI_v077.blend'));s.render.filepath=str(R/'renders/qa/R169_architectural_rooflights_v077.png');bpy.ops.render.render(write_still=True)
(R/'reports/R169_ARCHITECTURAL_ROOFLIGHTS_v077.json').write_text(json.dumps(dict(accepted=False,source='R169_full_row_source_wide.png',rooflights=records,source_mesh_objects_imported=0,source_textures_imported=0),indent=2));print('ROOFLIGHTS_SAVED',len(records))
