from pathlib import Path
import json,bpy,bmesh
R=Path(__file__).resolve().parents[2];B=R/'12_Blender_Model';r=json.loads((B/'reports/P09_build_report.json').read_text());p=json.loads((B/'config/stair_podium.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/r['file']))
checks=[]
for i,name in enumerate(r['podium_meshes']):
 ob=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(ob.data);bad=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);bm.free();zs=[v.co.z for v in ob.data.vertices];assert bad==0 and vol>0,(name,bad,vol)
 assert abs(min(zs)-i*p['draft_riser_m'])<1e-6 and abs(max(zs)-(i+1)*p['draft_riser_m'])<1e-6
 assert not [f for f in ob.data.polygons if f.area<1e-10]
 checks.append(dict(id=name,nonmanifold_edges=bad,volume_m3=vol,z_min=min(zs),z_max=max(zs),pdf_path_index=ob['source_path_index']))
old=bpy.data.objects['P05_PATH_GH_UP'];assert old.hide_render
new=bpy.data.objects['P09_GH_UP_CORRECTED_PATH'];pts=new.data.splines[0].points;assert abs(pts[0].co.z)<1e-6 and abs(pts[1].co.z-.48)<1e-6 and pts[-1].co.z>4
down=bpy.data.objects['P05_PATH_GH_DOWN'].data.splines[0].points;assert abs(down[0].co.z)<1e-6 and down[-1].co.z<0
for ident in ['008','011','013','022','023']:assert bpy.data.objects['REF_P09_'+ident].data.packed_file
assert len([o for o in bpy.data.objects if o.name in ['ENT-01-L00','ENT-01-LP1','ENT-02-L00','ENT-02-LP1','ENT-03-L00','ENT-03-LP1']])==6
result=dict(file=r['file'],podium_checks=checks,gh_up_corrected=True,gh_down_still_descends=True,podium_source_images_packed=True,entry_openings_preserved=6,full_flight_modeled=False,construction_acceptance=False)
(B/'reports/P09_verification.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2))
