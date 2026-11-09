import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R422_KALE_ESKI_ORTU_ARTIKLARI_KALDIRILDI_ADAY_v001.blend'));raw=json.loads((R/'.local_source_cache/r154/fort.json').read_text());fits=json.loads((R/'reports/R418_TOWER_CAP_PLANES.json').read_text());c=json.loads((R/'reports/R399_FRONT_COURT_PLANES.json').read_text())['tower_forecourt']['plane'];names=[];records=[];stone=bpy.data.materials['R154_FORT_STONE_PBR'];dressed=bpy.data.materials['R406_FORT_DRESSED_SANDSTONE'];doorMat=bpy.data.materials['R419_DARK_DOOR']
code=(R/'scripts/r424_architectural_primitives.py').read_text().replace('R419_TEMP_CUT','R424_TEMP_CUT');exec(compile(code,'<architectural primitives>','exec'))
for o in bpy.context.scene.objects:
 if o.name.startswith(('R419_SOUTH_','R407_CENTRAL_TOWER_','R408_')) or o.name in ['R154_TOWER_WEST','R154_TOWER_CENTRE','R154_TOWER_SOUTH','R154_TOWER_LOWER_COPING_WEST','R154_TOWER_LOWER_COPING_CENTRE','R154_TOWER_LOWER_COPING_SOUTH']:
  o.hide_render=True;o.hide_viewport=True;o.hide_set(True)
front=math.atan2(-raw['direction'][1],-raw['direction'][0]);centre=Vector((-61.6,-53.15))
for q in raw['towers']:
 label=q['name'];cx,cy=q['center'];r=q['radius']-.18;fit=fits[label]['coef'];roof=fit[0]+fit[1]*(q['radius']+.2);base=c[0]*cx+c[1]*cy+c[2]-.06;N=192;count={'WEST':18,'SOUTH':16,'CENTRE':9}[label]
 profile=[(r,base),(r,roof-.30),(q['radius']+.08,roof-.20),(q['radius']+.17,roof-.12),(q['radius']+.17,roof)];vs=[(cx+rr*math.cos(math.tau*i/N),cy+rr*math.sin(math.tau*i/N),z) for rr,z in profile for i in range(N)];fs=[list(range(N-1,-1,-1)),list(range((len(profile)-1)*N,len(profile)*N))]
 for k in range(len(profile)-1):fs.extend([(k*N+i,k*N+(i+1)%N,(k+1)*N+(i+1)%N,(k+1)*N+i) for i in range(N)])
 tower=mesh('R424_'+label+'_TOWER_BODY',vs,fs,stone);court=(centre-Vector((cx,cy))).normalized() if label!='CENTRE' else Vector(raw['direction']).normalized();angles=[front+i*math.tau/count for i in range(count)];openings=[]
 doorIndex=min(range(count),key=lambda i:abs(math.atan2(math.sin(angles[i]-math.radians(120)),math.cos(angles[i]-math.radians(120))))) if label=='SOUTH' else -1
 for i,a in enumerate(angles):
  isCourt=Vector((math.cos(a),math.sin(a))).dot(court)>.15;isDoor=i==doorIndex;lo=base+.04 if isDoor else base+(.55 if isCourt else 1.25);hi=base+2.16 if isDoor else base+(1.62 if isCourt else 2.15);width=1.0 if isDoor else .48;cut_window(a,width,lo,hi);openings.append(dict(angleDegrees=math.degrees(a)%360,courtSide=isCourt,door=isDoor,bottom=lo,top=hi,width=width))
 vs=[];fs=[];outer=math.pi*r/count;inner=outer-.20;spring=roof-.38-outer
 for phi in angles:
  for j in range(16):
   a=math.pi*j/16+.002;b=math.pi*(j+1)/16-.002;stonepiece([(inner*math.cos(a),spring+inner*math.sin(a)),(inner*math.cos(b),spring+inner*math.sin(b)),(outer*math.cos(b),spring+outer*math.sin(b)),(outer*math.cos(a),spring+outer*math.sin(a))],phi)
  for sign in [-1,1]:
   stonepiece([(sign*inner,base),(sign*outer,base),(sign*outer,spring),(sign*inner,spring)],phi)
   stonepiece([(sign*(inner-.09),spring-.17),(sign*(outer+.08),spring-.17),(sign*(outer+.08),spring),(sign*(inner-.09),spring)],phi)
 mesh('R424_'+label+'_BLIND_ARCADES',vs,fs,dressed)
 # Exterior coping is restricted to the front semicircle. Court face stays flush.
 vs=[];fs=[]
 for j in range(96):
  a=front-math.pi/2+j*math.pi/96;b=front-math.pi/2+(j+1)*math.pi/96;k=len(vs)
  for rr,z in [(r-.03,base-.12),(r+.32,base-.12),(r+.32,base+.02),(r-.03,base+.02)]:
   vs.extend([(cx+rr*math.cos(a),cy+rr*math.sin(a),z),(cx+rr*math.cos(b),cy+rr*math.sin(b),z)])
  fs.extend([tuple(k+t for t in f) for f in [(0,2,3,1),(2,4,5,3),(4,6,7,5),(6,0,1,7),(0,6,4,2),(1,3,5,7)]])
 mesh('R424_'+label+'_EXTERIOR_BASE_COPING',vs,fs,dressed)
 if doorIndex>=0:
  phi=angles[doorIndex];n=Vector((math.cos(phi),math.sin(phi),0));t=Vector((-n.y,n.x,0));org=Vector((cx,cy,0))+n*(r-.46);dv=[tuple(org+t*x+n*d+Vector((0,0,z))) for d in [0,.06] for x,z in [(-.47,base+.06),(.47,base+.06),(.47,base+2.13),(-.47,base+2.13)]];mesh('R424_SOUTH_RECESSED_DOOR',dv,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],doorMat)
 records.append(dict(tower=label,bays=count,base=base,eave=roof,openings=openings))
out=R/'scenes/MUDAM_R424_UC_KULE_FOTOGRAF_CEPHELERI_ADAY_v001.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);bpy.ops.wm.open_mainfile(filepath=str(out));checks=[]
for name in names:
 bm=bmesh.new();bm.from_mesh(bpy.data.objects[name].data);checks.append(dict(name=name,nonManifold=sum(not e.is_manifold for e in bm.edges),zeroArea=sum(f.calc_area()<1e-10 for f in bm.faces)));bm.free()
assert not any(x['nonManifold'] or x['zeroArea'] for x in checks),checks
(R/'reports/R424_TOWER_FACADES.json').write_text(json.dumps(dict(scene=out.name,accepted=False,published=False,records=records,checks=checks,sources=['reports/R423_TOWER_BAY_COUNT.json','references/fort_inpa/R423_68151068_full.jpg','references/fort_inpa/R423_68151083_full.jpg','references/fort_inpa/R423_68151076_full.jpg','references/fort_inpa/rooftop_view_1_Zinneke_CC_BY_SA_3.jpg'],limits=['Count evidence: west18 and south16 EXIF perspective fits; centre9 lower-confidence fit. World phase inherited front direction, not fully registered.','Opening heights, widths, recess depth and coping profile are photo-proportioned; not a measured facade survey.','Stone materials, acorn finials and concealed tower junctions remain unaccepted. No complete ring acceptance.']),indent=2))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=850;s.render.resolution_percentage=100
for label,eye,target,lens in [('court',(-46,-37,5.4),(-61.6,-53.15,3.1),35),('front',(-107,-92,6),(-63,-54,1.7),50)]:
 bpy.ops.object.camera_add(location=eye);s.camera=bpy.context.object;s.camera.rotation_euler=(Vector(target)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=lens;s.render.filepath=str(R/f'renders/qa/R424_{label}_candidate.png');bpy.ops.render.render(write_still=True)
print('R424_READY')
