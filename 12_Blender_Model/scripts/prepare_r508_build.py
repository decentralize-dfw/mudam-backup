from pathlib import Path
R=Path(__file__).resolve().parents[1];s=(R/'scripts/build_r504_south_roof.py').read_text();s=s.replace('MUDAM_R501_BATI_SUR_AGAC_KOTU_DUZELTME_ADAY_v001.blend','MUDAM_R507_GUNEY_KULE_ZEMIN_TEMASI_ADAY_v001.blend').replace('R504_SOUTH_ROOF_PARAMETERS','R508_WEST_TOWER_PARAMETERS').replace("cx,cy,r=d['edge']['fit']","cx,cy=d['center'];r=d['radius']").replace('SOUTH','WEST').replace('(-57.4,-63.1)','(-71.5,-47.6)').replace('4.9410600662231445','5.125725746154785').replace('1.4464751482','1.4489598274').replace('1.06647515','1.06895983').replace(",'R424_WEST_RECESSED_DOOR'",'').replace('cx+57.4','cx+71.5').replace('cy+63.1','cy+47.6').replace('5.94629430770874','6.031954765319824').replace('MUDAM_R504_GUNEY_KULE_CATISI_OTURUM_ADAY_v001.blend','MUDAM_R508_BATI_KULE_EKSEN_ZEMIN_ADAY_v001.blend').replace('R504_BUILD','R508_BUILD').replace('R504_tower_roofs','R508_tower_roofs')
contact='''
c=json.loads((R/'reports/R399_FRONT_COURT_PLANES.json').read_text())['tower_forecourt']['plane']
for partIndex,part in enumerate(d['contact']):
 points=[];lookup={};faces=[]
 def index(x,y,z):
  key=(round(x,7),round(y,7),round(z,7))
  if key not in lookup:lookup[key]=len(points);points.append(key)
  return lookup[key]
 def level(x,y):return c[0]*x+c[1]*y+c[2]-.012
 for tri in part['triangles']:
  faces.append(tuple(index(x,y,level(x,y)) for x,y in tri));faces.append(tuple(index(x,y,level(x,y)-.12) for x,y in reversed(tri)))
 ring=part['outline']
 for i,(x,y) in enumerate(ring):
  xx,yy=ring[(i+1)%len(ring)];faces.append((index(x,y,level(x,y)),index(xx,yy,level(xx,yy)),index(xx,yy,level(xx,yy)-.12),index(x,y,level(x,y)-.12)))
 name='R508_WEST_COURT_CONTACT_'+str(partIndex);me=bpy.data.meshes.new(name);me.from_pydata(points,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(o);me.materials.append(bpy.data.materials['R402_LOW_COURT_GRASS']);o['level_id']='SITE';o['source']='Measured court plane fills old tower-foot domain uncovered by registered axis correction; original surrounding ground preserved.';changed.append(name)
'''
s=s.replace('checks=[]',contact+'\nchecks=[]');(R/'scripts/build_r508_west_tower.py').write_text(s)
