import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'scenes/MUDAM_R365_PAVYON_SUR_TABAN_BIRLESIM_ADAY_v001.blend'))
for n in ['R35_WALL_51946353_00_0','R29_E_BOUNDARY_03','R348_MOAT_INNER_ARM_RUIN_FLOOR']:
 o=bpy.data.objects[n];print(n,'hideRender',o.hide_render,'viewport',o.hide_viewport,'hideGet',o.hide_get(),'visible',o.visible_get(),'collections',[(c.name,c.hide_render,c.hide_viewport) for c in o.users_collection])
def walk(c,path):
 if c.exclude or c.hide_viewport or c.collection.hide_render:print('HIDDEN',path,c.exclude,c.hide_viewport,c.collection.hide_render)
 for a in c.children:walk(a,path+'/'+a.name)
walk(bpy.context.view_layer.layer_collection,'scene')
