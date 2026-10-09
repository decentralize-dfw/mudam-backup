"""R24 closed curved gallery shells and transmissive north clerestories."""
from pathlib import Path
import bpy,bmesh,json,sys,math
from collections import Counter
from mathutils import Vector
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';P=json.loads((B/'config/upper_gallery_roof.json').read_text());V=json.loads((B/'config/vector_reference.json').read_text());Z={p['id']:p['draft_value'] for p in json.loads((B/'config/vertical_study.json').read_text())['parameters']};UP=Z['Z_LP1_FINISH'];base=UP+P['roof_base_above_upper_floor'];high=P['roof_high_z'];version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v001';out=B/'scenes'/f'MUDAM_R24_GALERI_ISIKLIK_{version}.blend';assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(B/'scenes'/P['base_scene']));root=bpy.data.collections.new('P11_UPPER_GALLERY_SHELL_GLASS_CONDITIONAL');bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root);made=[];changed=[];panels=[];shells=[];up=Vector((0,0,1));white=bpy.data.materials['R17_PAVILION_WHITE_FINISH_CANDIDATE'];glass=bpy.data.materials['P10_GLASS_PREVIEW'];metal=bpy.data.materials['R16_EXTERIOR_DARK_COATING_CANDIDATE']
for ob in bpy.data.objects:
 if ob.name.startswith(('P05_SHED_','P05_CLERESTORY_')):ob.hide_render=True;ob.hide_set(True);changed.append(ob.name)
def mesh(name,vs,fs,mat,kind):
 me=bpy.data.meshes.new(name);me.from_pydata([tuple(v) for v in vs],[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);root.objects.link(ob);me.materials.append(mat)
 for k,v in dict(element_id=name,element_type=kind,zone_id='UPPER_GALLERIES',level_id='LP1_ROOF',source_ids=','.join(P['source_ids']),confidence_xy='C source perimeter; D bay count',confidence_z='D section candidate',confidence_detail='D photograph family and unmeasured profile',status='conditional_gallery_shell_glazing',assumption_note='East six and west four bays are stated candidates; shell profile, thickness and glazing modules unmeasured.').items():ob[k]=v
 made.append(name);return ob
def box(name,x0,x1,y0,y1,z0,z1,mat,kind):
 return mesh(name,[(x,y,z) for z in [z0,z1] for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat,kind)
def clip(poly,y,above):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ia=a[1]>=y-1e-9 if above else a[1]<=y+1e-9;ib=b[1]>=y-1e-9 if above else b[1]<=y+1e-9
  if ia:out.append(a)
  if ia!=ib:
   t=(y-a[1])/(b[1]-a[1]);out.append((a[0]+t*(b[0]-a[0]),y))
 clean=[]
 for p in out:
  if not clean or math.dist(p,clean[-1])>1e-7:clean.append(p)
 if len(clean)>1 and math.dist(clean[0],clean[-1])<1e-7:clean.pop()
 return clean
def cross(poly,y):
 xs=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if abs(a[1]-b[1])>1e-9 and min(a[1],b[1])-1e-8<=y<=max(a[1],b[1])+1e-8:
   t=(y-a[1])/(b[1]-a[1]);xs.append(a[0]+t*(b[0]-a[0]))
 return min(xs),max(xs)
for side in ['E','W']:
 poly=[tuple(p) for p in V['gallery_LP1_'+side]['loops_xy'][0]];ymin=min(p[1] for p in poly);ymax=max(p[1] for p in poly);count=P['bay_counts'][side];pitch=(ymax-ymin)/count
 for bay in range(count):
  ya=ymin+bay*pitch;yb=ya+pitch;ys=sorted(set([ya+j*pitch/P['profile_samples_per_bay'] for j in range(P['profile_samples_per_bay']+1)]+[p[1] for p in poly if ya<p[1]<yb]));coords=[];indices={};faces=[]
  def vertex(p):
   key=tuple(round(x,8) for x in p)
   if key not in indices:indices[key]=len(coords);coords.append(p)
   return indices[key]
  for y0,y1 in zip(ys,ys[1:]):
   region=clip(clip(poly,y0,True),y1,False)
   if len(region)>=3:
    face=tuple(vertex(p) for p in region)
    if len(set(face))>=3:faces.append(face)
  N=len(coords);vs=[]
  for dz in [0,P['shell_vertical_thickness_m']]:
   for x,y in coords:
    t=max(0,min(1,(y-ya)/pitch));z=base+(high-base)*math.sqrt(max(0,1-(1-t)**2));vs.append((x,y,z+dz))
  fs=list(faces)+[tuple(i+N for i in reversed(f)) for f in faces];counts=Counter();direct={}
  for f in faces:
   for a,b in zip(f,f[1:]+f[:1]):key=tuple(sorted((a,b)));counts[key]+=1;direct[key]=(a,b)
  for key,n in counts.items():
   if n==1:a,b=direct[key];fs.append((a,b,b+N,a+N))
  ob=mesh(f'R24_SHELL_{side}_{bay:02d}',vs,fs,white,'closed_curved_concrete_shell_candidate');shells.append(dict(name=ob.name,bay=bay,side=side,y_range=[ya,yb],pitch=pitch,low=base,high=high))
  if bay==count-1:continue
  x0,x1=cross(poly,yb);modules=max(1,math.ceil((x1-x0)/P['glass_max_candidate_module_m']));fw=P['frame_width_m'];depth=P['frame_depth_m'];gt=P['glass_thickness_m']
  for j in range(modules):
   xa=x0+(x1-x0)*j/modules;xb=x0+(x1-x0)*(j+1)/modules;name=f'R24_GLASS_{side}_{bay:02d}_{j:02d}';box(name,xa+fw/2,xb-fw/2,yb-gt/2,yb+gt/2,base+fw/2,high-fw/2,glass,'north_clerestory_glass_candidate');panels.append(dict(name=name,center=[(xa+xb)/2,yb,(base+high)/2],thickness=gt))
  for j in range(modules+1):
   x=x0+(x1-x0)*j/modules;box(f'R24_MULLION_{side}_{bay}_{j}',x-fw/2,x+fw/2,yb-depth/2,yb+depth/2,base,high,metal,'clerestory_frame_candidate')
  for label,z in [('LOW',base),('HIGH',high)]:box(f'R24_RAIL_{side}_{bay}_{label}',x0,x1,yb-depth/2,yb+depth/2,z-fw/2,z+fw/2,metal,'clerestory_frame_candidate')
  box(f'R24_VALLEY_BEAM_{side}_{bay}',x0,x1,yb-.065,yb+.065,base-.22,base,metal,'visible_dark_beam_envelope_candidate')
bpy.context.scene['stage']='R24 transmissive upper clerestories and closed shell candidates';bpy.context.scene['current_file']=out.name;bpy.data.texts.new('R24_SOURCE_AND_LIMITS').write(json.dumps(P,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);report=dict(file=out.relative_to(R).as_posix(),base_scene=P['base_scene'],closed_objects=made,changed_inherited_objects=changed,panels=panels,shells=shells,construction_acceptance=False);(B/'reports/R24_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
