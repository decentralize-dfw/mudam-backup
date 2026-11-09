from pathlib import Path
import bpy,json
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_MIMARI_ARKA_CIKMA_v079.blend'))
center=Vector((-81.746925354,-294.516082764,-69));right=Vector((-.97769629955,-.2100233883,0));n=Vector((-.2100236565,.97769629955,0));scale=36/2048
rects=[(110,108,180,170,2),(325,105,415,177,2),(795,108,892,180,3),(1050,110,1135,182,2),(1295,97,1380,180,2),(1555,110,1640,180,2),(1710,110,1775,180,2),(345,258,425,345,2),(563,280,676,348,3),(790,280,914,350,3),(1060,273,1130,365,2),(1575,256,1655,347,2),(1720,260,1760,345,1),(795,465,911,530,3)]
wallnames=['ARCH_WALL_MASS_0','ARCH_REAR_PROJECTION_WALL_0'];assign={k:[] for k in wallnames};pending=[]
for rect in rects:
 x0,y0,x1,y1,panes=rect;p0=center+right*((x0-1024)*scale);p1=center+right*((x1-1024)*scale);lo=-69+(395.636-y1)*scale;hi=-69+(395.636-y0)*scale;choices=[]
 for name in wallnames:
  o=bpy.data.objects[name];v=[v.co.copy() for v in o.data.vertices];a,b=v[:2];t=(b-a).normalized();den=t.dot(right)
  if abs(den)<.1:continue
  us=[(p-a).dot(right)/den for p in [p0,p1]];l,r=sorted(us);length=(b-a).length
  if l<.02 or r>length-.02:continue
  top=min(v[3].z+(v[2].z-v[3].z)*u/length for u in [l,r]);depth=((a+b)/2-center).dot(n);choices.append((depth,name,l,r,lo,hi,top,panes))
 if choices:
  item=max(choices)
  if hi<item[6]-.03:assign[item[1]].append(item)
  else:pending.append(dict(rect=rect,reason='Above actual current wall boundary; requires dormer/roof detail, do not force hole.'))
 else:pending.append(dict(rect=rect,reason='Outside modeled wall bounds'))
frame=bpy.data.materials['Painted light window frames'];glass=bpy.data.materials['Glazing subdued blue grey'];count=0
for name,items in assign.items():
 if not items:continue
 o=bpy.data.objects[name];v=[v.co.copy() for v in o.data.vertices];a,b=v[:2];length=(b-a).length;t=(b-a).normalized();mat=o.data.materials[0];xs=sorted(set([0,length]+[u for it in items for u in it[2:4]]));zs=sorted(set([-75,max(v[2].z,v[3].z)]+[z for it in items for z in it[4:6]]));vv=[];ff=[]
 def point(u,z,dep=0):return a+t*u+Vector((0,0,z-a.z))-n*dep
 def quad(p):
  k=len(vv);vv.extend(p);ff.append(tuple(range(k,len(vv))))
 for l,r in zip(xs,xs[1:]):
  for lo,hi in zip(zs,zs[1:]):
   if any(it[2]<(l+r)/2<it[3] and it[4]<(lo+hi)/2<it[5] for it in items):continue
   tl=v[3].z+(v[2].z-v[3].z)*l/length;tr=v[3].z+(v[2].z-v[3].z)*r/length
   if lo>=max(tl,tr):continue
   poly=[(l,lo),(r,lo),(r,hi),(l,hi)];clipped=[]
   def residual(p):return p[1]-(v[3].z+(v[2].z-v[3].z)*p[0]/length)
   for pa,pb in zip(poly,poly[1:]+poly[:1]):
    fa=residual(pa);fb=residual(pb)
    if fa<=0:clipped.append(pa)
    if (fa<0)!=(fb<0):
     f=fa/(fa-fb);clipped.append((pa[0]+(pb[0]-pa[0])*f,pa[1]+(pb[1]-pa[1])*f))
   if len(clipped)>=3:quad([point(*p) for p in clipped])
 for it in items:
  _,_,l,r,lo,hi,top,panes=it
  for s,e in [((l,lo),(r,lo)),((r,lo),(r,hi)),((r,hi),(l,hi)),((l,hi),(l,lo))]:quad([point(*s),point(*e),point(*e,.16),point(*s,.16)])
  def panel(label,ul,ur,zl,zr,dep,material):
   me=bpy.data.meshes.new(label);me.from_pydata([point(ul,zl,dep),point(ur,zl,dep),point(ur,zr,dep),point(ul,zr,dep)],[],[(0,1,2,3)]);obj=bpy.data.objects.new(label,me);bpy.context.collection.objects.link(obj);me.materials.append(material)
  panel(f'ARCH_REAR_GLAZING_{count}',l,r,lo,hi,.17,glass)
  for j in range(panes+1):
   u=l+(r-l)*j/panes;panel(f'ARCH_REAR_FRAME_{count}_{j}',u-.035,u+.035,lo,hi,.10,frame)
  for z in [lo,hi]:panel(f'ARCH_REAR_FRAME_H_{count}_{z}',l,r,z-.035,z+.035,.10,frame)
  count+=1
 me=bpy.data.meshes.new(name+'_openings');me.from_pydata(vv,[],ff);me.update();o.data=me;me.materials.append(mat)
s=bpy.context.scene;s['acceptance']='Unaccepted architectural WIP, rear visible wall openings added; upper openings beyond wall boundary queued as roof features.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R169_MIMARI_DUVAR_UST_KESIM_v088.blend'));target=Vector((-80,-301,-66));s.camera.location=target+Vector((-20,31,30));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(R/'renders/qa/R169_architectural_rear_v080.png');pass
(R/'reports/R169_ARCHITECTURAL_REAR_OPENINGS_v088.json').write_text(json.dumps(dict(accepted=False,source='R169_arch_rear_reference_v079.png',window_groups=count,assigned=assign,pending=pending),indent=2));print('REAR_OPENINGS',count,'PENDING',len(pending))
