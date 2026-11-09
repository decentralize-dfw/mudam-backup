from pathlib import Path
import bpy,bmesh,json,numpy as np
R=Path(__file__).resolve().parents[1];D=R/'.local_source_cache/r169';d=json.loads((D/'facade_planes_v057.json').read_text());q=np.array(d['q']);ns=np.array([s['normal'] for s in d['sides']]);offsets=[s['offset'] or 0 for s in d['sides']];lines=[float(np.dot(ns[k],q[k])+offsets[k]) for k in range(4)];corners=[]
for k in range(4):corners.append(np.linalg.solve(np.array([ns[(k-1)%4],ns[k]]),[lines[(k-1)%4],lines[k]]).tolist())
bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R169_BUTUN_CATI_DOKULU_ADAY_v054.blend'))
for ob in list(bpy.context.scene.objects):
 if ob.type=='MESH' and ob.name!='R169_WHOLE_SOURCE_ROOF':bpy.data.objects.remove(ob,do_unlink=True)
base=-74.62;top=-66.10;v=[(*p,z) for z in [base,top] for p in corners];f=[(k,(k+1)%4,(k+1)%4+4,k+4) for k in range(4)]+[(4,5,6,7),(3,2,1,0)]
me=bpy.data.meshes.new('Measured_facade_planes');me.from_pydata(v,[],f);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new('Measured_facade_planes',me);bpy.context.collection.objects.link(ob)
bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);roof=bpy.data.objects['R169_WHOLE_SOURCE_ROOF'];roof.select_set(True);bpy.context.view_layer.objects.active=roof;bpy.ops.object.join()
roof['source_scope']='Three visible facade planes fitted from ACT horizontal rays. Side 3 is concealed party boundary. Base extends below existing ground; ground check pending.'
bpy.ops.wm.save_as_mainfile(filepath=str(R/'scenes/MUDAM_R169_TEK_BINA_ADAY_v057.blend'),compress=True)
(D/'facade_corners_v057.json').write_text(json.dumps(dict(corners=corners,offsets=offsets)))
