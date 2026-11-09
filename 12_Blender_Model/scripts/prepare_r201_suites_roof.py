from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.local_source_cache/gis_runtime'))
from shapely.geometry import Polygon
from shapely import constrained_delaunay_triangles
r=json.loads((R/'config/r183_suites_architecture.json').read_text());outer=Polygon(r['outer']);inner=outer.buffer(-.24,join_style=2);block=Polygon(r['raised_roof_domain']);roof=inner.difference(block)
def tris(p):return [list(t.exterior.coords)[:-1] for t in constrained_delaunay_triangles(p).geoms]
out=dict(outer=r['outer'],inner=list(inner.exterior.coords)[:-1],roof_triangles=tris(roof),coping_triangles=tris(outer.difference(inner)),raised_roof_domain=r['raised_roof_domain'],raised_top=r['raised_top'],triangles=r['triangles'])
(R/'config/r201_suites_closed_roof.json').write_text(json.dumps(out,indent=2))
s=(R/'scripts/build_r183_suites.py').read_text();s=s.replace('MUDAM_R182_GENIS_ARAZI_MAHALLE_v003.blend','MUDAM_R200_BUTUN_VIYADUK_v001.blend').replace("r183_suites_architecture.json","r201_suites_closed_roof.json")
s=s.replace("r=json.loads", "\nfor old in list(bpy.data.objects):\n if old.name.startswith('R183_NOVOTEL_SUITES'):bpy.data.objects.remove(old,do_unlink=True)\nr=json.loads",1)
a=s.index("for tri in r['triangles']:");b=s.index("me=bpy.data.meshes.new",a)
s=s[:a]+'''# A continuous roof shell: inner parapet, solid coping, stepped technical roof.
for tri in r['triangles']:face([(x,y,base) for x,y in reversed(tri)],0)
for tri in r['roof_triangles']:face([(x,y,top) for x,y in tri],3)
for tri in r['coping_triangles']:face([(x,y,32.1) for x,y in tri],0)
for a,b in zip(r['inner'],r['inner'][1:]+r['inner'][:1]):face([(a[0],a[1],top),(b[0],b[1],top),(b[0],b[1],32.1),(a[0],a[1],32.1)],0)
block=r['raised_roof_domain'];zt=r['raised_top']
for a,b in zip(block,block[1:]+block[:1]):face([(a[0],a[1],top),(b[0],b[1],top),(b[0],b[1],zt),(a[0],a[1],zt)],0)
for tri in tessellate_polygon([[Vector((x,y,zt)) for x,y in block]]):face([(block[i][0],block[i][1],zt) for i in tri],3)
'''+s[b:]
a=s.index('# Correct the visible Mama');b=s.index('bpy.ops.wm.save_as_mainfile',a)
s=s[:a]+'''(R/'reports/R201_SUITES_ROOF.json').write_text(json.dumps(dict(accepted=False,change='Rebuilt whole roof as continuous stepped architectural shell; inner parapet faces and coping, technical volume joined through roof opening',dimensions=dict(mainRoof=31.35,parapet=32.1,copingWidth=.24),limits=['Coping width0.24m architectural assumption','Facade module/source agreement and ground interface remain pending']),indent=2))
'''+s[b:]
s=s.replace('R183_NOVOTEL_SUITES','R201_NOVOTEL_SUITES').replace('MUDAM_R183_KUZEY_MIMARI_v001','MUDAM_R201_KUZEY_KAPALI_CATILAR_v001').replace('R183_north_architecture_v001.png','R201_suites_closed_roof_v001.png').replace('dist=.00001','dist=.001')
(R/'scripts/build_r201_suites_roof.py').write_text(s)
