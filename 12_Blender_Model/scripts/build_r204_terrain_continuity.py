from pathlib import Path
import bpy,bmesh,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R202_ALT_MAHALLE_NEHIR_v001.blend'))
report=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or not(o.name in ['R154_FAR_GROUND','R154_FAR_ROADS','R161_ROAD_CONNECTIONS'] or o.name.startswith(('R182_EXTENSION_','R192_GRADE_'))):continue
 me=o.data;before=len(me.vertices);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.001);bmesh.ops.dissolve_degenerate(bm,edges=bm.edges[:],dist=.00001);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();me.update()
 for p in me.polygons:p.use_smooth=True
 report.append(dict(name=o.name,vertices_before=before,vertices_after=len(me.vertices)))
raw=json.loads((R/'.local_source_cache/r154/terrain.json').read_text());vs=[];fs=[]
for m in raw['meshes']:
 k=len(vs);vs.extend(m['vertices']);fs.extend([k+j for j in f] for f in m['faces'])
g=BVHTree.FromPolygons(vs,fs,all_triangles=True);rows=json.loads((R/'config/r202_river_domains.json').read_text())['domains'];bank_records=[]
for i,row in enumerate(rows):
 vs=[];fs=[];c=row['plane'];ox,oy=row['origin'];gaps=[]
 for ring in [row['outer']]+row['holes']:
  for aa,bb in zip(ring,ring[1:]+ring[:1]):
   a,b=Vector(aa),Vector(bb);count=max(1,math.ceil((b-a).length/.75))
   for j in range(count):
    p,q=a.lerp(b,j/count),a.lerp(b,(j+1)/count);zs=[]
    for v in [p,q]:
     z=c[0]*(v.x-ox)+c[1]*(v.y-oy)+c[2];h=g.ray_cast(Vector((v.x,v.y,100)),Vector((0,0,-1)),300)[0];top=max(z,h.z if h else z)+.025;zs.append((top,z-.15));gaps.append(top-z)
    k=len(vs);vs.extend([(p.x,p.y,zs[0][0]),(q.x,q.y,zs[1][0]),(q.x,q.y,zs[1][1]),(p.x,p.y,zs[0][1])]);fs.extend([(k,k+1,k+2),(k,k+2,k+3)])
 me=bpy.data.meshes.new('R204_RIVER_BANK_%02d'%i);me.from_pydata(vs,[],fs);me.update();me.materials.append(bpy.data.materials['R154_FORT_STONE_PBR']);uv=me.uv_layers.new()
 for l in me.loops:v=me.vertices[l.vertex_index].co;uv.data[l.index].uv=((v.x+v.y)/4,v.z/4)
 o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o);bank_records.append(dict(name=o.name,triangles=len(fs),max_join_height=max(gaps)))
(R/'reports/R204_TERRAIN_CONTINUITY.json').write_text(json.dumps(dict(accepted=False,terrain=report,banks=bank_records,method='Merge coincident authored terrain vertices after clipping, preserving UV loops; restore smooth shared normals. Join mapped river banks to measured original DEM.',limits=['River stone material approximate; source-only partial water-plane fit remains','Unrelated full11-region source fidelity not accepted']),indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R204_ARAZI_SUREKLILIGI_v001.blend'),compress=True);bpy.context.scene.render.filepath=str(R/'renders/qa/R204_terrain_continuity_v001.png');bpy.ops.render.render(write_still=True)
