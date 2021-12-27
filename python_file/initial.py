import bpy
import os
import yaml
import tqdm
from mathutils import Euler,Vector

'''
1.初始化blender模型，将所有需要多材质的模型列表加载所有目标材质，再使用material_slot 选取相应材质。
2.将所有的动画非保护物体的origin设置为（0，0，0），为动画做准备
'''

print(os.getcwd())
mat_prefix_set=set([_.split("_")[0] for _ in bpy.data.materials.keys()])
material_name_ls=sorted(bpy.data.materials.keys())
material_dict={}
for _ in mat_prefix_set:
    container_ls=[]
    for mat in material_name_ls:
        if mat.split("_")[0]==_:
            container_ls.append(mat)
    material_dict[_]=container_ls

static_collection_ls=yaml.load(open('../conf.yml','r'),Loader=yaml.FullLoader)['static_collection']



print("start init blender model...")
for obj in tqdm.tqdm((bpy.data.objects.values())):
    bpy.context.scene.cursor.location=Vector((0.0, 0.0, 0.0))
               
    collections=set([_.name for _ in obj.users_collection])
    if obj.parent==None and set(collections).intersection(set(static_collection_ls))==set():
        if obj.type not in ["MESH" , "CURVE"]:
            raise Exception("{} is not mesh/curve type".format(_.name))
        if not obj.visible_get():
            obj.hide_set(False) 
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            obj.hide_set(True)
            # bpy.ops.object.mode_set(mode='OBJECT')   
        else:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

    if obj.type=='MESH':
        material_ls=obj.data.materials.values()
        prefix_ls=[material.name.split('_')[0] for material in material_ls if material is not None]
        for prefix in prefix_ls:
            for mat in material_dict[prefix]:
                if mat not in obj.data.materials.keys():
                    obj.data.materials.append(bpy.data.materials[mat])

            
print("init blender model done")

# conf_path='./version_material/conf.yml'


# container_dict={}
# col_ls=bpy.data.collections.keys()
# exception_col_ls=yaml.load(open(conf_path,'r'),Loader=yaml.FullLoader)['exception_collection']
# for col in col_ls:
#     if col in exception_col_ls:
#         print('{} is in exception list'.format(col))
#     else:
#         con=[]
#         obj_ls=bpy.data.collections[col].all_objects.values()
#         for _ in obj_ls:
#             if not _.parent:
#                 con.append(_.name)
#         container_dict[col]=con  
        
# print(container_dict)
# muti_obj_collection_name_dict=yaml.load(open(conf_path,'r'),Loader=yaml.FullLoader)['muti_material']
# keys_ls=sorted(container_dict.keys())
# for _ in keys_ls:
#     if _ in muti_obj_collection_name_dict.keys():
#         print('{} is in muti_material'.format(_))
#         material_ls=[mat for mat in bpy.data.materials if mat.name.split('_')[0] == muti_obj_collection_name_dict[_]]
#         for obj_name in container_dict[_]:
#             bpy.data.objects[obj_name].data.materials.clear()
#             for _ in material_ls:
#                 bpy.data.objects[obj_name].data.materials.append(_)
    
