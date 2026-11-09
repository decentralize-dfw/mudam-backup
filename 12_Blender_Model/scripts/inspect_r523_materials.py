import bpy,json
bpy.ops.wm.open_mainfile(filepath='C:/Users/yigit/Desktop/WORK/MUDAM/12_Blender_Model/scenes/MUDAM_R522_BATI_SUR_TERAS_HENDEK_ADAY_v001.blend')
for name in ['R152_CLASS2_TERRAIN','R485_NW_LAWN','R430_FRONT_APPROACH_PAVING','R457_LOADING_COURT_MINERAL']:
 o=bpy.data.objects[name];print('MATERIAL_INFO',name,[(m.name,[(n.type,getattr(n,'uv_map',''),getattr(getattr(n,'image',None),'name',''))for n in m.node_tree.nodes]) for m in o.data.materials if m.use_nodes],flush=True)
