"""R115: visible glass retention on the six existing pavilion door panes.

Source 067 supports the stepped frame/glass perimeter, not measured profiles.
Existing openings, leaf positions and clear glass area remain unchanged.
"""
from pathlib import Path
import bpy, bmesh, json
from mathutils import Vector
B=Path(__file__).resolve().parents[1]
R=B.parent
base=json.loads((B/'reports/R114_build_report.json').read_text())
out=B/'scenes/MUDAM_R115_PAVYON_KAPI_CAM_TUTUCULARI_v001.blend'
assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(R/base['file']))
root=bpy.data.collections.new('R115_PAVILION_DOOR_GLAZING_RETENTION')
bpy.data.collections['90_UNCERTAIN_OR_PROXY'].children.link(root)
metal=bpy.data.materials['P10_FRAME_PREVIEW']
rubber=bpy.data.materials.new('R115_GLAZING_SEAL_CANDIDATE')
rubber.use_nodes=True
bs=rubber.node_tree.nodes.get('Principled BSDF')
bs.inputs['Base Color'].default_value=(.025,.027,.026,1)
bs.inputs['Roughness'].default_value=.65
names=json.loads((B/'reports/R18_build_report.json').read_text())['panels']
made=[]; rows=[]
faces=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
for name in names:
    glass=bpy.data.objects[name]
    vs=[glass.matrix_world@v.co for v in glass.data.vertices]
    origin=(vs[0]+vs[3])/2
    x=(vs[1]-vs[0]).normalized(); y=(vs[3]-vs[0]).normalized(); z=Vector((0,0,1))
    w=(vs[1]-vs[0]).length; h=vs[4].z-vs[0].z; depth=(vs[3]-vs[0]).length/2
    def box(tag,bounds,mat,kind):
        u0,u1,d0,d1,v0,v1=bounds
        key=name.replace('R18_','R115_')+'_'+tag
        me=bpy.data.meshes.new(key)
        me.from_pydata([origin+x*u+y*d+z*v for v in [v0,v1] for u,d in [(u0,d0),(u1,d0),(u1,d1),(u0,d1)]],[],faces)
        me.update(); bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
        ob=bpy.data.objects.new(key,me);root.objects.link(ob);me.materials.append(mat)
        for k,val in dict(element_id=key,element_type=kind,zone_id='PAV_LINK',level_id='L00',source_ids='067',status='representative_visible_perimeter_detail',confidence_detail='D unmeasured profile and seal',assumption_note='067 shows a stepped glass/frame perimeter. 18mm frame engagement, 8mm glass overlap, 3mm seal and 10mm bead depth are editable representative sizes. No concealed fasteners or proprietary system claimed.',host_glass=name).items():ob[k]=val
        made.append(key)
        rows.append(dict(name=key,host=name,bounds=bounds,origin=list(origin),x=list(x),y=list(y)))
    for side in [-1,1]:
        for kind,mat,lo,hi,engage,overlap in [('SEAL',rubber,depth,depth+.003,.006,.008),('BEAD',metal,depth+.003,depth+.013,.018,.008)]:
            d0,d1=sorted([side*lo,side*hi])
            # Four strips join at corners without covering the central glass.
            for edge,u0,u1,v0,v1 in [('BOTTOM',-engage,w+engage,-engage,overlap),('TOP',-engage,w+engage,h-overlap,h+engage),('LEFT',-engage,overlap,overlap,h-overlap),('RIGHT',w-overlap,w+engage,overlap,h-overlap)]:
                box(f'{kind}_{side}_{edge}',[u0,u1,d0,d1,v0,v1],mat,'glazing_'+kind.lower()+'_candidate')
report=dict(file=out.relative_to(R).as_posix(),base_scene=Path(base['file']).name,closed_objects=made,changed_inherited_objects=[],panes=names,parts=rows,construction_acceptance=False,limits=['Visible perimeter family from067; all profile dimensions representative.','Existing door leaf pose and clear opening inherited, no door hardware or fire/structural certification.'])
bpy.context.scene['stage']='R115 pavilion door glass beads and perimeter seals'
bpy.context.scene['current_file']=out.name
bpy.data.texts.new('R115_SOURCE_LIMITS').write(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(B/'reports/R115_build_report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('R115',len(names),'panes',len(made),'new solid parts')
