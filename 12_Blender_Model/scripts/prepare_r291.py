from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
d=json.loads((R/'config/r290_south_roof.json').read_text());a,b,c=d['plane'];ox,oy=d['origin']
d['cornerRoofs']=[a*(x-ox)+b*(y-oy)+c for x,y in d['polygon']];d['unresolvedCropEdges']=[]
(R/'config/r291_south_roof.json').write_text(json.dumps([d],indent=2))
s=(R/'scripts/build_r289_roofs.py').read_text()
s=s.replace('MUDAM_R286_DOGU_BUTUN_CATI_KESIT_ADAY_v001.blend','MUDAM_R289_DOGU_IKI_BUYUK_CATI_ADAY_v001.blend')
s=s.replace('r289_roof_boundaries.json','r291_south_roof.json').replace('R289','R291').replace('r289','r291')
# Restore input after global label replacement.
s=s.replace('MUDAM_R291_DOGU_IKI_BUYUK_CATI_ADAY_v001.blend\'))','MUDAM_R289_DOGU_IKI_BUYUK_CATI_ADAY_v001.blend\'))',1)
s=s.replace("assert d['samples']>500 and d['support']>.98 and d['p90']<.15","assert d['samples']>2000 # Equipment/openings contaminate whole-roof residual; not source acceptance")
s=s.replace("((.12,.14,.14,1) if i==0 else (.62,.60,.55,1))","(.31,.30,.26,1)")
s=s.replace("prism(f'R291_ROOF_SLAB_{i}',p,[h-.25 for h in z],z,ma);regions.append(p)","slab=prism(f'R291_ROOF_SLAB_{i}',p,[h-.25 for h in z],z,ma);regions.append(p)")
insert='''
# Independently traced visible rooflights; opening and reveal dimensions remain image-derived candidates.
lights=[(379,1360,24,13,[-.85,.53]),(424,1332,23,13,[-.85,.53]),(456,1310,22,13,[-.85,.53]),(488,1288,22,13,[-.85,.53]),
(366,1269,13,22,[.53,-.85]),(377,1245,13,22,[.53,-.85]),(390,1220,13,22,[.53,-.85]),(402,1197,13,22,[.53,-.85]),
(428,1131,14,22,[.53,-.85]),(447,1103,14,22,[.53,-.85]),(468,1082,14,22,[.53,-.85]),(492,1045,14,22,[.53,-.85]),(505,1027,14,22,[.53,-.85]),
(529,998,14,22,[.53,-.85]),(543,974,14,22,[.53,-.85]),(554,954,14,22,[.53,-.85]),(566,932,14,22,[.53,-.85]),(580,914,14,22,[.53,-.85]),
(578,938,14,22,[.53,-.85]),(600,952,14,22,[.53,-.85]),(564,964,14,22,[.53,-.85]),(588,976,14,22,[.53,-.85]),(558,1004,14,22,[.53,-.85]),
(632,985,14,22,[.53,-.85]),(641,971,14,22,[.53,-.85]),(674,974,14,22,[.53,-.85]),(682,961,14,22,[.53,-.85]),
(708,1008,14,22,[.53,-.85]),(718,1028,14,22,[.53,-.85]),(728,1052,14,22,[.53,-.85]),(747,1054,14,22,[.53,-.85]),
(729,1076,14,22,[.53,-.85]),(753,1074,14,22,[.53,-.85]),(771,1086,14,22,[.53,-.85]),(745,1102,14,22,[.53,-.85]),(730,1110,14,22,[.53,-.85]),(706,1130,14,22,[.53,-.85])]
lightRecords=[]
def xy(px,py):return Vector((150+px*.1875,300-py*.1875))
for k,(px,py,w,l,axis) in enumerate(lights):
 center=xy(px,py);u=Vector((axis[0],-axis[1])).normalized();v=Vector((-u.y,u.x));u*=l*.1875/2;v*=w*.1875/2
 pp=[tuple(center-u-v),tuple(center+u-v),tuple(center+u+v),tuple(center-u+v)]
 zz=[ds[0]['plane'][0]*(x-ds[0]['origin'][0])+ds[0]['plane'][1]*(y-ds[0]['origin'][1])+ds[0]['plane'][2] for x,y in pp]
 cutter=prism('TEMP_APERTURE',pp,[h-1 for h in zz],[h+1 for h in zz],ma);boolean(slab,cutter)
 prism(f'R291_ROOFLIGHT_GLASS_{k:02}',pp,[h-.06 for h in zz],[h-.02 for h in zz],glass)
 for j in range(4):
  aa=Vector(pp[j]);bb=Vector(pp[(j+1)%4]);normal=(center-(aa+bb)/2).normalized()*.12
  edge=[tuple(aa),tuple(bb),tuple(bb+normal),tuple(aa+normal)];h=(zz[j]+zz[(j+1)%4])/2
  prism(f'R291_ROOFLIGHT_REVEAL_{k:02}_{j}',edge,h-.25,h+.18,bpy.data.materials['R262_PALE_COPING'])
 lightRecords.append(dict(sourcePixel=[px,py],polygon=pp))
'''
s=s.replace('def clip(points,a,b,sign,inside):',insert+'\ndef clip(points,a,b,sign,inside):')
s=s.replace('s.camera.location=(380,215,180)','s.camera.location=(250,77,180)').replace('s.camera.data.ortho_scale=110','s.camera.data.ortho_scale=150')
s=s.replace("sourceFits=ds,clipping=records,checks=checks","sourceFits=ds,rooflights=lightRecords,clipping=records,checks=checks")
s=s.replace("'Boundary corrected from matched R288 source view; white roof source crop unresolved and no coping added there'","'South roof traced from R277; 37 rectangular rooflights modeled; round lights and remaining perimeter openings unresolved; whole roof source p90 1.028m so not accepted'")
(R/'scripts/build_r291_south_roof.py').write_text(s)
