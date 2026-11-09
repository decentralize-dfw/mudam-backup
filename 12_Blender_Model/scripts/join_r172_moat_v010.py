from pathlib import Path
import bpy,json,bmesh
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R172_ON_KALE_HENDEK_ADAY_v009.blend'))
r=next(r for r in json.loads((R/'reports/R172_TERRACES_v003.json').read_text())['terraces'] if r['name']=='MOAT_EAST');xy=r['xy'];c=r['plane'];origin=r['origin'];ground=bpy.data.objects['R154_FAR_GROUND'];points=[ground.matrix_world@v.co for v in ground.data.vertices];verts=[];faces=[];counts=[]
def floor(x,y):return c[0]*(x-origin[0])+c[1]*(y-origin[1])+c[2]
for a,b in zip(xy,xy[1:]+xy[:1]):
 ax,ay=a;dx=b[0]-ax;dy=b[1]-ay;length2=dx*dx+dy*dy;on={}
 for p in points:
  t=((p.x-ax)*dx+(p.y-ay)*dy)/length2
  if -.00001<=t<=1.00001 and abs((p.x-ax)*dy-(p.y-ay)*dx)<.0003:
   on[round(t,6)]=(ax+dx*t,ay+dy*t,p.z)
 ordered=sorted(on.items());counts.append(len(ordered))
 for (_,p),(_,q) in zip(ordered,ordered[1:]):
  if Vector(p).xy==Vector(q).xy:continue
  k=len(verts);verts.extend([p,q,(q[0],q[1],floor(q[0],q[1])),(p[0],p[1],floor(p[0],p[1]))]);faces.extend([(k,k+1,k+2),(k,k+2,k+3)])
me=bpy.data.meshes.new('R172_MOAT_TERRAIN_JOIN');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(me.name,me);bpy.context.collection.objects.link(o);me.materials.append(bpy.data.materials['R172_MOAT_EARTH']);o['status']='Terrain cut closure; masonry identity and full fort comparison remain pending'
bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.0001);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R172_ON_KALE_HENDEK_ADAY_v010.blend'),compress=True)
(R/'reports/R172_MOAT_v010.json').write_text(json.dumps({'accepted':False,'join_triangles':len(me.polygons),'boundary_sample_counts':counts,'method':'Exact existing terrain cut-edge breakpoints joined to independent measured floor plane','remaining':['Entire fort terraces and moat extent','Source-faithful retaining material and dimensions','All other user regions']},indent=2))
s=bpy.context.scene;s.render.filepath=str(R/'renders/qa/R172_fort_moat_v010.png');bpy.ops.render.render(write_still=True);print('R172_V010_DONE')
