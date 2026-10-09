from pathlib import Path
import sys,runpy,json,math,bpy
from mathutils import Vector
B=Path(__file__).resolve().parents[1];args=sys.argv[sys.argv.index('--')+1:];sys.argv=['audit','--',args[0]];g=runpy.run_path(str(B/'scripts/audit_interior_enclosure.py'));tree=g['tree'];rows=[];samples=0;rays=0;summary=[]
for rev in ['R04','R05','R10','R25']:
 r=json.loads((B/'reports'/f'{rev}_build_report.json').read_text());count=0;bad=0
 for step in r['steps']:
  ob=bpy.data.objects[step['name']];ps=[ob.matrix_world@v.co for v in ob.data.vertices];z=max(p.z for p in ps);top=[p for p in ps if abs(p.z-z)<1e-4];center=sum(top,Vector())/len(top);points=[center]+[center.lerp(top[min(len(top)-1,int(i*len(top)/4))],.65) for i in range(4)]
  for i,p in enumerate(points):
   samples+=1;count+=1;cover=tree.ray_cast(p+Vector((0,0,1.2)),Vector((0,0,1)),45);misses=[]
   for dz in [.15,1.2,2.1]:
    for angle in range(0,360,30):
     rays+=1;a=math.radians(angle);hit=tree.ray_cast(p+Vector((0,0,dz)),Vector((math.cos(a),math.sin(a),0)),200)
     if hit[0] is None:misses.append(dict(dz=dz,angle=angle))
   if cover[0] is None or misses:bad+=1;rows.append(dict(step=ob.name,sample=i,position=list(p),cover_missing=cover[0] is None,escapes=misses))
 summary.append(dict(revision=rev,samples=count,findings=bad))
q=dict(file=args[0],samples=samples,side_rays=rays,summary=summary,findings=rows,limits=['Geometric tread sample positions; source alignment and exact stair geometry remain separate.','Exterior escape rays require classification, not automatic filling of real circulation.']);(B/'reports/DIGER_MERDIVEN_KABUK_TARAMA.json').write_text(json.dumps(q,indent=2));print(summary)
