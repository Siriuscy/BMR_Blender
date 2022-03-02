import bpy
import os
import yaml
import tqdm
from mathutils import Euler,Vector
from bpy_extras.image_utils import load_image
'''
1.将所有的动画非保护物体的origin设置为（0，0，0），为动画做准备
2.删除所有动画
3.删除所有空材质
'''
def initial():
    conf=yaml.load(open('../conf.yml','r'),Loader=yaml.FullLoader)
    
    mat_prefix_set=set([_.split("_")[0] for _ in bpy.data.materials.keys()])
    material_name_ls=sorted(bpy.data.materials.keys())
    material_dict={}
    for _ in mat_prefix_set:
        container_ls=[]
        for mat in material_name_ls:
            if mat.split("_")[0]==_:
                container_ls.append(mat)
        material_dict[_]=container_ls

    static_collection_ls=conf['static_collection']

    print("start init blender model...")
    for obj in tqdm.tqdm((bpy.data.objects.values())):
        if obj.type in ['ARMATURE','LIGHT','EMPTY']:
            continue
    # 0.删除所有旋转动画和材质   
        obj.animation_data_clear()
        print(obj.name)
        for mat in obj.data.materials.values():
            if mat==None:
                obj.data.materials.remove(mat)
        bpy.context.scene.cursor.location=Vector((0.0, 0.0, 0.0))
    # 1.设置旋转中心            
        collections=set([_.name for _ in obj.users_collection])
        if obj.parent==None and set(collections).intersection(set(static_collection_ls))==set():
            if obj.type not in ["MESH" , "CURVE"]:
                raise Exception("{} is not mesh/curve type".format(_.name))
            elif obj.type=="CURVE":
                obj.data.dimensions="3D"
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
    # 2.重置所有的贴图文件
    # for _ in bpy.data.images.values():
    #     bpy.data.images.remove(_)
    
    texture_path=conf['texture_path']
    texture_ls=os.listdir(texture_path)
    try:
        texture_ls.remove(".DS_Store")
    except:
        pass
    for image_name in texture_ls:
        if image_name not in bpy.data.images.keys():
            load_image(os.path.join(texture_path,image_name)) 
            
    for _ in bpy.data.images.values():
        if _.name not in texture_ls:
            bpy.data.images.remove(_)
    
    print("init blender model done")
    

if __name__ == '__main__':
    initial()