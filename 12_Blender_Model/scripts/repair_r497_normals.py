from pathlib import Path
R=Path('12_Blender_Model');p=R/'scripts/build_r497_surfaces.py';s=p.read_text();a=s.index("for name in ['R152");b=s.index("mat=bpy.data.materials",a);new='''for name in ['R152_CLASS2_TERRAIN','R485_NW_LAWN']:
 o=bpy.data.objects[name];me=o.data;groups={};keys={}
 for p in me.polygons:
  group=0 if name=='R152_CLASS2_TERRAIN' else (1 if p.normal.z>.3 else -1 if p.normal.z<-.3 else 2)
  for li in p.loop_indices:
   v=me.vertices[me.loops[li].vertex_index].co;key=(group,round(v.x,6),round(v.y,6),round(v.z,6));keys[li]=key
   if key not in groups:groups[key]=Vector((0,0,0))
   groups[key]+=p.normal*p.area
  p.use_smooth=True
 normals=[groups[keys[i]].normalized() for i in range(len(me.loops))];me.normals_split_custom_set(normals);records.append(dict(name=name,vertices=len(me.vertices),faces=len(me.polygons),change='area-weighted shared-position custom normals only; vertex coordinates, topology and UVs unchanged; lawn top/bottom/side normal groups separated'))
''';p.write_text(s[:a]+new+s[b:])
