import math
import numpy as np
import bpy
import os
import bmesh
import json
import random
from math import pi
from importlib import reload
import time

def hsva2rgb(h,s,v,a):
    h = float(h)
    s = float(s)
    v = float(v)
    h60 = h / 60.0
    h60f = math.floor(h60)
    hi = int(h60f) % 6
    f = h60 - h60f
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    r, g, b = 0, 0, 0
    if hi == 0: r, g, b = v, t, p
    elif hi == 1: r, g, b = q, v, p
    elif hi == 2: r, g, b = p, v, t
    elif hi == 3: r, g, b = p, q, v
    elif hi == 4: r, g, b = t, p, v
    elif hi == 5: r, g, b = v, p, q
    # r, g, b = int(r * 255), int(g * 255), int(b * 255)
    return r, g, b, a 

def senta2H(senta):
    '''[情感值越高，颜色越偏暖色调]

    Parameters
    ----------
    senta : [float]
        [情感值]

    Returns
    -------
    [type]
        [HSV的H值]
    '''
    # y=np.abs(-2*x+1)
    return (np.arcsin(-2*senta+1)+math.pi)/2/math.pi

def record_data():
    pass

def find_multi_mat_obj(multi_mat_obj_filePath):
    '''[summary]
    找到所有的单个mesh多材质的物体，并保存在json文件中。

    Parameters
    ----------
    multi_mat_obj_filePath : [type]
        json文件地址

    Returns
    -------
    [type] dict
        [如果是单mesh多材质则返回]
    '''
    obj_ls=bpy.data.objects.values()
    container={}
    for obj in obj_ls:
        print("{} is judging if has multiple material...".format(obj.name))
        if obj.type=='MESH':
            # get mesh data
            if not obj.visible_get():
                obj.hide_set(False) 
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')
                mesh = bmesh.from_edit_mesh(obj.data)
                obj.hide_set(True)
                # bpy.ops.object.mode_set(mode='OBJECT')   
            else:
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')
                mesh = bmesh.from_edit_mesh(obj.data)
                # bpy.ops.object.mode_set(mode='OBJECT')   
                
            # if multi mat
            mat_ls=[]
            for face in mesh.faces:
                mat_ls.append(face.material_index)
                
            if len(set(mat_ls))>=2:
                print("{} is multi mat".format(obj.name))
                
                mat_keys=obj.data.materials.keys()
                indexes = [[face.index, face.material_index] for face in mesh.faces]
                container_dic={}
                for face_index,mat_index in indexes:
                    mat=mat_keys[mat_index] 
                    if mat in container_dic.keys():
                        container_dic[mat].append(face_index)
                    else:
                        container_dic[mat]=[face_index]
                container[obj.name]=(container_dic)
            else:
                print("{} is single mat".format(obj.name))
            bpy.ops.object.mode_set(mode='OBJECT')   
        else:
            print("{} is not a mesh".format(obj.name))    
    open(multi_mat_obj_filePath,'w').close()                        
    json.dump(container,open(multi_mat_obj_filePath,'w'),indent=4)
    
    return container

def find_all_children_objects(obj):
    ls=[]
    def iter(obj):
        ls.extend(list(obj.children))
        for c_obj in list(obj.children):
            if c_obj.children!=():
                iter(c_obj)
    iter(obj)
    return ls+[obj]
    
def choose_element(conf):
    '''[summary]'''
    container_dict={}
    expection_collection_ls=conf['exception_collection']
    must_selected_at_lesat_one=conf['must_selected_at_lesat_one']
    all_must_selected=conf['all_must_selected']
    # STEP 1: 记录所有不在 exception_collection 的无父集对象
    col_ls=bpy.data.collections.keys()        
    for col in col_ls:
        if col not in expection_collection_ls and bpy.data.collections[col].children.values()==[]:
            con=[]
            obj_ls=bpy.data.collections[col].all_objects.values()
            for _ in obj_ls:
                if not _.parent:
                    con.append(_.name)
                _.hide_render=True
                _.hide_set(True)
            container_dict[col]=con 
    
    one_code=""
    one_result_ls=[]
    keys_ls=sorted(container_dict.keys())
    for col_name in keys_ls:
        if col_name in must_selected_at_lesat_one:
            num=np.random.randint(0,len(container_dict[col_name]))
            one_result_ls.append(container_dict[col_name][num])
        elif col_name in all_must_selected:
            for num in list(range(0,len(container_dict[col_name]))):
                one_result_ls.append(container_dict[col_name][num])
        else:
            num=np.random.randint(0,len(container_dict[col_name])+1)
            if num == len(container_dict[col_name]):
                num='#'
                continue
            one_result_ls.append(container_dict[col_name][num])    
        one_code+=str(num)
    print("choose element done...\n{}".format(one_result_ls))
    
    try:
        data=json.load(open(conf['done_codes_path'],'r'))
        if one_code in data:
            print('code has been done...REPEATED')
            return 'REPEATED','REPEATED'
        else:
            data.append(one_code)
    except json.decoder.JSONDecodeError:
        data=[one_code]
    json.dump(data,open(conf['done_codes_path'],'w'))
    
    return one_code,one_result_ls

def dero_record_metadata(dic):
    def dero(func):
        def wrapper(obj):   
            dic[obj.name] = func(obj)
            return func(obj)
        return wrapper
    return dero
 
def assign_material(one_result_ls,multi_obj_name_ls,multi_obj_ls,one_code):    
    metadata={'code':one_code,
              'time':time.asctime(time.localtime(time.time())),
              'chosen objects':one_result_ls,}
    for obj_name in one_result_ls:
        one_obj=bpy.data.objects[obj_name]
        all_obj = find_all_children_objects(one_obj)
        
        for child_obj in all_obj:
            metadata[child_obj.name]={}
            
        @dero_record_metadata(metadata)
        def record_mat_and_assign(obj):
            import copy_material
            from importlib import reload
            reload(copy_material)
            # 1.记录需要的材质
            needed_mat_ls=[]
            for material in obj.data.materials.values():
                if material is not None and  '.' not in material.name:
                    needed_mat_ls.append(material)
            # 2.删除所有材质
            obj.data.materials.clear()
            # 3.随机材质
            random_mat=needed_mat_ls[np.random.randint(0,len(needed_mat_ls))]
            try:
                mat_data=eval('copy_material.'+random_mat.name.split('.')[0]+'()')
                obj.data.materials.append(mat_data[0])
                return_value={'material_name':mat_data[0].name.split('.')[0],'material_metadata':mat_data[1]}
            except AttributeError:
                return_value={'material_name':needed_mat_ls[0].name,'material_metadata':None} 
            # 4.把剩下的材质装回去,装回去的时候把材质的名字改成不带.001的
            for mat in needed_mat_ls:
                # mat=bpy.data.materials[mat.name.split('.')[0]]
                obj.data.materials.append(mat)    
            return return_value
        
        @dero_record_metadata(metadata)
        def multi_mat_assign(obj):
            import copy_material
            from importlib import reload
            reload(copy_material)
            # 1.记录需要的材质
            needed_mat_ls=[]
            for material in obj.data.materials.values():
                if material is not None and  '.' not in material.name:
                    needed_mat_ls.append(material)
            # 2.删除所有材质
            obj.data.materials.clear()
            face_index_ls=list(multi_obj_ls[obj.name].values())
            # 3.选择n个材质
            mat_choosed=random.sample(needed_mat_ls,len(face_index_ls))
            # 4.新加n个新材质
            container=[]
            for old_mat in mat_choosed:
                try:
                    mat_data=eval('copy_material.'+old_mat.name.split('.')[0]+'()')
                    obj.data.materials.append(mat_data[0])
                    return_value={'material_name':mat_data[0].name.split('.')[0],'material_metadata':mat_data[1]}
                except AttributeError:
                    return_value={'material_name':needed_mat_ls[0].name,'material_metadata':None} 
                container.append(return_value)
            # 5.把剩下的材质装回去
            for mat in needed_mat_ls:
                # mat=bpy.data.materials[mat.name.split('.')[0]]
                obj.data.materials.append(mat)
            # 6.根据面添加材质
            bpy.context.view_layer.objects.active = bpy.data.objects[obj.name]
            bpy.ops.object.mode_set(mode='EDIT')
            bm= bmesh.from_edit_mesh(bpy.data.objects[obj.name].data)
            for count,one_mat_ls in enumerate(face_index_ls):
                for face in one_mat_ls:
                    if hasattr(bm.faces, "ensure_lookup_table"): 
                        bm.faces.ensure_lookup_table()
                    bm.faces[face].material_index=count
            bpy.ops.object.mode_set(mode='OBJECT')
            return container

        # 选择一个obj 对其子集赋予材质
        for obj in all_obj:
            if obj.type in ['ARMATURE','LIGHT','EMPTY']:
                continue
            materials=obj.data.materials.keys()
            if len(materials)==0:
                print("{} has no material".format(obj.name))
                obj.data.materials.append(bpy.data.materials['colorfulHue'])
                # raise Exception("{} has no material".format(obj.name))
                continue
            if obj.name in multi_obj_name_ls:
                multi_mat_assign(obj)
            else:
                record_mat_and_assign(obj)
    return metadata

def assign_cartoon_material(one_result_ls,multi_obj_name_ls,multi_obj_ls,mat_mode): 
    metadata={}
    import utils
    reload(utils)
    import copy_material
    reload(copy_material)
            
    all_H=[num for num in list(range(0,361,30))]
    random_num=np.random.randint(0,len(all_H))
    adjacent_colour_ls=[all_H[random_num],all_H[(random_num+1)%12],all_H[(random_num+2)%12],all_H[(random_num+3)%12],all_H[(random_num+4)%12]]
    contrast_color_ls=[all_H[random_num],all_H[(random_num+4)%12],all_H[(random_num+8)%12]]
    
    print('adjacent_colour_ls:',adjacent_colour_ls)
    
    for obj_name in one_result_ls:
        if obj_name.split('_')[0] in ['eyes','mouse']:
            print('{} pass'.format(obj_name))
            continue
        one_obj=bpy.data.objects[obj_name]
        all_obj = find_all_children_objects(one_obj)
        
        for child_obj in all_obj:
            metadata[child_obj.name]={}
            
        # @dero_record_metadata(metadata)
        def record_mat_and_assign(obj,value):
            
            # 1.记录需要的材质
            
            # 2.删除所有材质
            obj.data.materials.clear()
            # 3.随机材质
            mat_data=copy_material.v10_flat_mat(value)
            obj.data.materials.append(mat_data[0])
            return_value={}
            return return_value
        
        # @dero_record_metadata(metadata)
        def multi_mat_assign(obj,value):
            import copy_material
            from importlib import reload
            reload(copy_material)
            obj.data.materials.clear()
            face_index_ls=list(multi_obj_ls[obj.name].values())
            # 4.新加n个新材质
            container=[]
            for _ in range(len(face_index_ls)):

                mat_data=copy_material.v10_flat_mat(value)
                obj.data.materials.append(mat_data[0])
                return_value={'material_name':mat_data[0].name.split('.')[0],'material_metadata':mat_data[1]}
                container.append(return_value)
            # 6.根据面添加材质
            bpy.context.view_layer.objects.active = bpy.data.objects[obj.name]
            bpy.ops.object.mode_set(mode='EDIT')
            bm= bmesh.from_edit_mesh(bpy.data.objects[obj.name].data)
            for count,one_mat_ls in enumerate(face_index_ls):
                for face in one_mat_ls:
                    if hasattr(bm.faces, "ensure_lookup_table"): 
                        bm.faces.ensure_lookup_table()
                    bm.faces[face].material_index=count
            bpy.ops.object.mode_set(mode='OBJECT')
            return container

        # 选择一个obj 对其子集赋予材质
        for obj in all_obj:
            if mat_mode=="random":
                value=utils.hsva2rgb(all_H[np.random.randint(len(all_H))],0.8,1,1)
            elif mat_mode=="adjacent_color":
                value=utils.hsva2rgb(adjacent_colour_ls[np.random.randint(len(adjacent_colour_ls))],0.8,1,1)
            elif mat_mode=='contrast_color':
                value=utils.hsva2rgb(contrast_color_ls[np.random.randint(len(contrast_color_ls))],0.8,1,1)
                
            print('value:',value)
            if obj.name in multi_obj_name_ls:
                multi_mat_assign(obj,value)
            else:
                record_mat_and_assign(obj,value)
    print('bg_h:{}'.format((adjacent_colour_ls[1]+120)%360))
    bpy.data.objects['background'].material_slots[0].material=copy_material.v10_paint_mat(value=utils.hsva2rgb((adjacent_colour_ls[2]+120)%360,0.8,0.8,1))[0]
    return metadata

def show_models(one_result_ls):
    def set_render_true(parent_obj):
        parent_obj.hide_render=False
        parent_obj.hide_set(False)
        for child_obj in parent_obj.children:
            child_obj.hide_render=False
            child_obj.hide_set(False)
            if child_obj.children !=():
                set_render_true(child_obj)
    for obj_name in one_result_ls:
        parent_obj=bpy.data.objects[obj_name]
        set_render_true(parent_obj)
        
def render(conf,code):
    pic_save_path=conf['pic_save_path']
    mode=conf['output_mode']
    if mode == "PICTURE":
        bpy.context.scene.render.image_settings.file_format="PNG"
        bpy.context.scene.render.filepath=os.path.join(pic_save_path,code+'.png')
        bpy.context.scene.frame_set(40)
        bpy.ops.render.render(animation=False,write_still=True)
    elif mode == "VIDEO":
        video_setting=conf['video_setting']
        format=video_setting['format']
        if format in ['AVI_JPEG','AVI_RAW',"FFMPEG"]:
            print("Rendering VIDEO...")
            bpy.context.scene.render.image_settings.file_format=format
            if format=="FFMPEG":
                bpy.context.scene.render.ffmpeg.format='MPEG4'
                bpy.context.scene.render.ffmpeg.codec="H264"
                bpy.context.scene.render.ffmpeg.constant_rate_factor = 'HIGH'
                bpy.context.scene.render.use_stamp_note = True
                bpy.context.scene.render.stamp_note_text = "BMR-LAB CHINA TONGJI UNIVERSITY."

            bpy.context.scene.render.filepath=os.path.join(pic_save_path,code)
            bpy.ops.render.render(animation=True,write_still=True)
        else:
            print("Rendering ARRAY IMAGES...")
            bpy.context.scene.render.image_settings.file_format=format
            new_path=os.path.join(pic_save_path,code)
            if os.path.exists(new_path):
                print("{} have been existed.".format(new_path))
            else:
                os.mkdir(new_path)
            bpy.context.scene.render.filepath=os.path.join(new_path,'frames')
            bpy.ops.render.render(animation=True)    

def set_annimation(conf,chosed_element):
    video_setting=conf['video_setting']
    static_collection_ls=conf['static_collection']
    time_scale=video_setting['time_scale']
    rotation=video_setting['rotation']
    
    bpy.context.scene.frame_set(0)
    fps=bpy.context.scene.render.fps=24
    bpy.context.scene.frame_end = fps*time_scale

    for obj_name in chosed_element:
        # like {'brain_01': {'brain_01': 'glass_01', 'bull': 'metal_01'}}
        parent_obj=bpy.data.objects[obj_name]                      
        parent_col_ls=set([_.name for _ in parent_obj.users_collection])
        if parent_obj.parent==None and set(parent_col_ls).intersection(set(static_collection_ls))==set():
            parent_obj.animation_data_clear()
            print("{} is setting a animation.".format(parent_obj.name))
            parent_obj.keyframe_insert("rotation_euler", frame=1) 
            parent_obj.rotation_euler[2]+=pi * rotation / 180
            parent_obj.keyframe_insert("rotation_euler", frame=fps*time_scale)
    print("Animation has set.")
    

def cleanup():
    for material in bpy.data.materials.values():
        if '.' in material.name:
            bpy.data.materials.remove(material)
    for meta in bpy.data.metaballs.values():
        bpy.data.metaballs.remove(meta)
        
def save_metadata(conf,metadata):
    code=metadata['code']
    filePath=os.path.join(conf['metadata_path'],code+'.json')
    with open(filePath,'w') as f:
        json.dump(metadata,f,ensure_ascii=False,indent=2),

    
if __name__ == '__main__':
    cleanup()